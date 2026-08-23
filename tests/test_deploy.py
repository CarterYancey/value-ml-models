"""Deployment training + inference against the miniature dataset.

The deployment path (data/manual.md §4 rule 7) refits on *all* labeled
rows — every role, every snapshot kind — reads no split tags, and scores
an `inference_{date}` dataset that carries features but no labels.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.deploy import (
    DEPLOYMENT_SCHEME,
    INFERENCE_SCHEME,
    TREND_COLUMNS,
    _main_predict,
    _main_train,
    predict_with_bundle,
    predict_with_bundles,
    train_deployment_model,
)
from harness.errors import DatasetValidationError
from harness.model_store import DeploymentBundle, ModelBundle, ModelBundleError
from harness.results import ResultsStore

LABEL = "label_3y_beat_spy"
WEIGHT = "sample_weight_3y"


def _config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "deploy_tree_3y_beat_spy",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": LABEL,
        "model": {"name": "decision_tree", "max_depth": 3},
        "feature_groups": ["features", "ranks"],
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


@pytest.fixture()
def trained(data_root, dataset_dir, tmp_path):
    """One deployment training run: (summary, config, paths)."""
    results = tmp_path / "results.csv"
    summary = train_deployment_model(
        _config(),
        data_root=data_root,
        results_path=results,
        models_dir=tmp_path / "models",
    )
    return summary, results


@pytest.fixture()
def inference_dir(dataset_dir, tmp_path) -> Path:
    """An `inference_{date}` directory built from the fixture's latest
    median snapshots: feature columns only, no labels or weights."""
    data = pd.read_parquet(dataset_dir / "dataset.parquet")
    manifest = json.loads((dataset_dir / "manifest.json").read_text())
    cols = manifest["columns"]
    latest = (
        data[data["snapshot_kind"] == "median"]
        .sort_values("snapshot_date")
        .groupby("permaticker", as_index=False)
        .tail(1)
    )
    keep = ["permaticker", "ticker", "snapshot_date"]
    keep += cols["features"] + cols["ranks"] + cols["sector_ranks"]
    out = tmp_path / "inference_2026-07-22"
    out.mkdir()
    latest[keep].to_parquet(out / "dataset.parquet")
    return out


def test_trains_on_all_labeled_rows(trained, dataset_dir):
    summary, results = trained
    data = pd.read_parquet(dataset_dir / "dataset.parquet")
    labeled = data[data[LABEL].notna()]
    # every labeled row, all snapshot kinds — not just role='train'
    assert summary["n_train_rows"] == len(labeled)
    assert set(labeled["snapshot_kind"].unique()) == {"low", "median", "high"}
    assert summary["effective_train_size"] == pytest.approx(
        labeled[WEIGHT].sum()
    )
    # delistings stay in the fit
    assert (labeled["delisted_in_window_3y"] != "false").any()


def test_training_run_is_logged_under_deployment_scheme(trained):
    summary, results = trained
    df = ResultsStore(results).load()
    row = df[df["run_id"] == summary["run_id"]].iloc[0]
    assert row["status"] == "completed"
    assert row["scheme"] == DEPLOYMENT_SCHEME
    assert row["fold"] == "all_labeled"
    assert row["git_sha"]
    assert row["config_hash"]


def test_bundle_roundtrip_and_kind_guards(trained, tmp_path):
    summary, _ = trained
    bundle = DeploymentBundle.load(summary["bundle_path"])
    assert bundle.run_id == summary["run_id"]
    assert bundle.n_train_rows == summary["n_train_rows"]
    assert bundle.probabilistic
    assert bundle.feature_columns == (
        "book_to_market",
        "earnings_yield",
        "book_to_market_rank",
        "earnings_yield_rank",
    )
    # a deployment bundle is not a per-fold bundle, and vice versa
    with pytest.raises(ModelBundleError, match="deployment"):
        ModelBundle.load(summary["bundle_path"])


def test_fold_bundle_refused_by_deployment_loader(
    data_root, tmp_path
):
    from harness.runner import run_experiment

    summary = run_experiment(
        _config(name="wf_tree", folds=(2016,)),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    with pytest.raises(ModelBundleError, match="fold_models"):
        DeploymentBundle.load(summary["model_bundle"])


def test_predict_writes_ranked_csv_and_top(trained, inference_dir, tmp_path):
    summary, results = trained
    out_csv = tmp_path / "preds" / "ranking.csv"
    pred = predict_with_bundle(
        summary["bundle_path"],
        inference_dir,
        output_path=out_csv,
        results_path=results,
        top_n=3,
    )
    ranking = pd.read_csv(out_csv)
    n_stocks = len(pd.read_parquet(inference_dir / "dataset.parquet"))
    assert len(ranking) == n_stocks == pred["n_rows_scored"]
    assert list(ranking["rank"]) == list(range(1, n_stocks + 1))
    assert (ranking["score"].diff().dropna() <= 0).all()  # descending
    assert {"permaticker", "ticker", "snapshot_date", "score"} <= set(
        ranking.columns
    )
    assert len(pred["top"]) == 3
    assert list(pred["top"]["rank"]) == [1, 2, 3]

    meta = json.loads(Path(pred["meta_path"]).read_text())
    assert meta["bundle_run_id"] == summary["run_id"]
    assert meta["n_rows_scored"] == n_stocks

    df = ResultsStore(results).load()
    row = df[df["run_id"] == pred["run_id"]].iloc[0]
    assert row["status"] == "completed"
    assert row["scheme"] == INFERENCE_SCHEME
    assert row["fold"] == "inference_2026-07-22"


def test_default_output_path_uses_source_and_bundle_names(
    trained, inference_dir, tmp_path
):
    summary, results = trained
    pred = predict_with_bundle(
        summary["bundle_path"],
        inference_dir,
        results_path=results,
        predictions_dir=tmp_path / "predictions",
    )
    assert pred["output_path"].name == (
        f"inference_2026-07-22__{Path(summary['bundle_path']).name}.csv"
    )
    assert pred["output_path"].exists()


def test_predict_refuses_missing_feature_columns(
    trained, inference_dir, tmp_path
):
    summary, results = trained
    frame = pd.read_parquet(inference_dir / "dataset.parquet")
    broken = tmp_path / "inference_broken"
    broken.mkdir()
    frame.drop(columns=["earnings_yield"]).to_parquet(
        broken / "dataset.parquet"
    )
    with pytest.raises(DatasetValidationError, match="earnings_yield"):
        predict_with_bundle(
            summary["bundle_path"], broken, results_path=results
        )
    # the failure is logged like any other run
    df = ResultsStore(results).load()
    assert (df["status"] == "failed").any()


def test_predict_refuses_frame_without_permaticker(
    trained, inference_dir, tmp_path
):
    summary, results = trained
    frame = pd.read_parquet(inference_dir / "dataset.parquet")
    broken = tmp_path / "inference_no_key"
    broken.mkdir()
    frame.drop(columns=["permaticker"]).to_parquet(broken / "dataset.parquet")
    with pytest.raises(DatasetValidationError, match="permaticker"):
        predict_with_bundle(
            summary["bundle_path"], broken, results_path=results
        )


@pytest.fixture()
def trained_pair(data_root, dataset_dir, tmp_path):
    """Two deployment bundles with distinct config names: (summaries,
    results_path)."""
    results = tmp_path / "results.csv"
    summaries = [
        train_deployment_model(
            _config(name=name, model={"name": "decision_tree", "max_depth": d}),
            data_root=data_root,
            results_path=results,
            models_dir=tmp_path / "models",
        )
        for name, d in [("deploy_depth2", 2), ("deploy_depth3", 3)]
    ]
    return summaries, results


def test_multi_bundle_combined_csv(trained_pair, inference_dir, tmp_path):
    summaries, results = trained_pair
    bundle_dirs = [s["bundle_path"] for s in summaries]
    out_csv = tmp_path / "preds" / "combined.csv"
    pred = predict_with_bundles(
        bundle_dirs,
        inference_dir,
        output_path=out_csv,
        results_path=results,
        top_n=3,
    )
    combined = pd.read_csv(out_csv)
    n_stocks = len(pd.read_parquet(inference_dir / "dataset.parquet"))
    assert len(combined) == n_stocks == pred["n_rows_scored"]
    assert list(combined.columns) == [
        "permaticker", "ticker", "snapshot_date", "mean_rank",
        "rank_deploy_depth2", "score_deploy_depth2",
        "rank_deploy_depth3", "score_deploy_depth3",
    ]
    # ordered by mean rank, which is the mean of the per-model ranks
    assert (combined["mean_rank"].diff().dropna() >= 0).all()
    assert combined["mean_rank"].equals(
        combined[["rank_deploy_depth2", "rank_deploy_depth3"]].mean(axis=1)
    )
    assert len(pred["top"]) == 3

    # each model's column matches what a single-bundle run produces
    for s, name in zip(summaries, ["deploy_depth2", "deploy_depth3"]):
        single = predict_with_bundle(
            s["bundle_path"],
            inference_dir,
            output_path=tmp_path / f"single_{name}.csv",
            results_path=results,
        )["top"].set_index("permaticker")
        merged = combined.set_index("permaticker")
        assert merged.loc[single.index, f"score_{name}"].tolist() == (
            pytest.approx(single["score"].tolist())
        )

    # one inference run logged per model
    df = ResultsStore(results).load()
    logged = df[df["run_id"].isin(pred["run_ids"])]
    assert len(logged) == 2
    assert (logged["scheme"] == INFERENCE_SCHEME).all()
    assert (logged["status"] == "completed").all()

    meta = json.loads(Path(pred["meta_path"]).read_text())
    assert [m["column_suffix"] for m in meta["models"]] == [
        "deploy_depth2", "deploy_depth3"
    ]
    assert [m["run_id"] for m in meta["models"]] == pred["run_ids"]


def test_multi_bundle_default_output_and_name_dedup(
    trained, inference_dir, tmp_path
):
    # the same bundle twice: config names collide, so column suffixes
    # fall back to name + bundle run_id, and both stay in the CSV
    summary, results = trained
    pred = predict_with_bundles(
        [summary["bundle_path"], summary["bundle_path"]],
        inference_dir,
        results_path=results,
        predictions_dir=tmp_path / "predictions",
    )
    suffix = f"deploy_tree_3y_beat_spy_{summary['run_id']}"
    combined = pd.read_csv(pred["output_path"])
    assert f"score_{suffix}" in combined.columns
    assert pred["output_path"].name.startswith(
        "inference_2026-07-22__multi__"
    )


def test_multi_bundle_missing_feature_logs_failure(
    trained_pair, inference_dir, tmp_path
):
    summaries, results = trained_pair
    frame = pd.read_parquet(inference_dir / "dataset.parquet")
    broken = tmp_path / "inference_broken"
    broken.mkdir()
    frame.drop(columns=["earnings_yield"]).to_parquet(
        broken / "dataset.parquet"
    )
    with pytest.raises(DatasetValidationError, match="earnings_yield"):
        predict_with_bundles(
            [s["bundle_path"] for s in summaries], broken, results_path=results
        )
    df = ResultsStore(results).load()
    assert (df["status"] == "failed").any()


def test_cli_end_to_end(data_root, inference_dir, tmp_path, capsys):
    config = tmp_path / "deploy.toml"
    config.write_text(
        "\n".join(
            [
                'name = "cli_deploy_tree"',
                'dataset_version = "dataset_v0.0-test"',
                'scheme = "walkforward"',
                "horizon_years = 3",
                f'label = "{LABEL}"',
                'feature_groups = ["features", "ranks"]',
                "[model]",
                'name = "decision_tree"',
                "max_depth = 3",
            ]
        )
    )
    results = tmp_path / "results.csv"
    models = tmp_path / "models"
    assert (
        _main_train(
            [
                str(config),
                "--data-root", str(data_root),
                "--results", str(results),
                "--models-dir", str(models),
            ]
        )
        == 0
    )
    bundle_dir = next(models.iterdir())
    out_csv = tmp_path / "ranking.csv"
    assert (
        _main_predict(
            [
                str(bundle_dir),
                str(inference_dir),
                "--output", str(out_csv),
                "--results", str(results),
            ]
        )
        == 0
    )
    assert out_csv.exists()
    printed = capsys.readouterr().out
    assert "top" in printed and "score" in printed


def test_cli_multi_bundle(trained_pair, inference_dir, tmp_path, capsys):
    summaries, results = trained_pair
    out_csv = tmp_path / "combined.csv"
    assert (
        _main_predict(
            [
                str(summaries[0]["bundle_path"]),
                str(summaries[1]["bundle_path"]),
                str(inference_dir),
                "--output", str(out_csv),
                "--results", str(results),
                "--top", "3",
            ]
        )
        == 0
    )
    combined = pd.read_csv(out_csv)
    assert {"score_deploy_depth2", "score_deploy_depth3"} <= set(
        combined.columns
    )
    printed = capsys.readouterr().out
    assert "mean rank" in printed


# --- --trends: carry trend context columns into the output ---------------


@pytest.fixture()
def inference_dir_trends(inference_dir, tmp_path) -> Path:
    """The inference fixture plus the TREND_COLUMNS an upstream inference
    dataset would carry (synthetic values keyed off the row index)."""
    frame = pd.read_parquet(inference_dir / "dataset.parquet")
    for i, col in enumerate(TREND_COLUMNS):
        frame[col] = [float(100 * i + j) for j in range(len(frame))]
    out = tmp_path / "inference_trends"
    out.mkdir()
    frame.to_parquet(out / "dataset.parquet")
    return out


def test_predict_carries_trend_columns(trained, inference_dir_trends, tmp_path):
    summary, results = trained
    out_csv = tmp_path / "ranking_trends.csv"
    predict_with_bundle(
        summary["bundle_path"],
        inference_dir_trends,
        output_path=out_csv,
        results_path=results,
        extra_columns=TREND_COLUMNS,
    )
    ranked = pd.read_csv(out_csv)
    # trend columns sit after the score, values carried verbatim per row
    assert list(ranked.columns)[-len(TREND_COLUMNS) - 1] == "score"
    assert list(ranked.columns)[-len(TREND_COLUMNS):] == list(TREND_COLUMNS)
    source = pd.read_parquet(inference_dir_trends / "dataset.parquet")
    merged = ranked.merge(
        source[["permaticker", *TREND_COLUMNS]],
        on="permaticker",
        suffixes=("", "_src"),
    )
    for col in TREND_COLUMNS:
        assert (merged[col] == merged[f"{col}_src"]).all()
    meta = json.loads(
        (out_csv.parent / f"{out_csv.name}.meta.json").read_text()
    )
    assert meta["extra_columns"] == list(TREND_COLUMNS)


def test_predict_without_flag_keeps_csv_unchanged(
    trained, inference_dir_trends, tmp_path
):
    summary, results = trained
    out_csv = tmp_path / "ranking_plain.csv"
    predict_with_bundle(
        summary["bundle_path"],
        inference_dir_trends,
        output_path=out_csv,
        results_path=results,
    )
    ranked = pd.read_csv(out_csv)
    assert not set(TREND_COLUMNS) & set(ranked.columns)


def test_predict_trends_missing_from_inference_is_an_error(
    trained, inference_dir, tmp_path
):
    summary, results = trained
    with pytest.raises(DatasetValidationError, match="lacks columns"):
        predict_with_bundle(
            summary["bundle_path"],
            inference_dir,
            output_path=tmp_path / "nope.csv",
            results_path=results,
            extra_columns=TREND_COLUMNS,
        )


def test_multi_bundle_carries_trend_columns(
    trained_pair, inference_dir_trends, tmp_path
):
    summaries, results = trained_pair
    out_csv = tmp_path / "combined_trends.csv"
    predict_with_bundles(
        [s["bundle_path"] for s in summaries],
        inference_dir_trends,
        output_path=out_csv,
        results_path=results,
        extra_columns=TREND_COLUMNS,
    )
    combined = pd.read_csv(out_csv)
    assert list(combined.columns)[-len(TREND_COLUMNS):] == list(TREND_COLUMNS)
    meta = json.loads(
        (out_csv.parent / f"{out_csv.name}.meta.json").read_text()
    )
    assert meta["extra_columns"] == list(TREND_COLUMNS)


def test_cli_trends_flag(trained, inference_dir_trends, tmp_path, capsys):
    summary, results = trained
    out_csv = tmp_path / "cli_trends.csv"
    assert (
        _main_predict(
            [
                str(summary["bundle_path"]),
                str(inference_dir_trends),
                "--output", str(out_csv),
                "--results", str(results),
                "--trends",
            ]
        )
        == 0
    )
    ranked = pd.read_csv(out_csv)
    assert set(TREND_COLUMNS) <= set(ranked.columns)
    capsys.readouterr()
