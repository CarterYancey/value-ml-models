"""Historical analogues: the labeled rows most similar to a pick as the
models see it. Explanation, not evaluation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from explain.analogues import (
    _main,
    find_analogues,
    leaf_ids,
    leaf_similarity,
    path_features,
    rank_similarity,
    run_analogues,
)
from harness.config import ExperimentConfig
from harness.dataset import Dataset
from harness.deploy import train_deployment_model
from harness.errors import ConfigError
from harness.model_store import DeploymentBundle

LABEL = "label_3y_beat_spy"


def _config(name: str, model: dict) -> ExperimentConfig:
    return ExperimentConfig.from_dict(
        {
            "name": name,
            "dataset_version": "dataset_v0.0-test",
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": LABEL,
            "model": model,
            "feature_groups": ["features", "ranks"],
        }
    )


@pytest.fixture()
def bundles(data_root, tmp_path):
    """A forest and a rank factor refit for deployment: the two kinds of
    similarity."""
    out = {}
    for name, model in [
        ("forest", {"name": "random_forest", "n_estimators": 12, "max_depth": 3}),
        ("factor", {"name": "rank_factor", "rank_column": "book_to_market_rank"}),
        ("tree", {"name": "decision_tree", "max_depth": 2}),
    ]:
        summary = train_deployment_model(
            _config(name, model), data_root=data_root,
            results_path=tmp_path / "results.csv",
            models_dir=tmp_path / "models",
        )
        out[name] = summary["bundle_path"]
    return out


@pytest.fixture()
def inference(dataset_dir, tmp_path) -> Path:
    data = pd.read_parquet(dataset_dir / "dataset.parquet")
    manifest = json.loads((dataset_dir / "manifest.json").read_text())
    cols = manifest["columns"]
    latest = (
        data[data["snapshot_kind"] == "median"]
        .sort_values("snapshot_date")
        .groupby("permaticker", as_index=False)
        .tail(1)
    )
    keep = ["permaticker", "ticker", "snapshot_date"] + cols["features"] + cols["ranks"]
    out = tmp_path / "inference_2026-07-22"
    out.mkdir()
    latest[keep].to_parquet(out / "dataset.parquet")
    return out


def test_rank_similarity_is_closeness_and_null_matches_null():
    sim = rank_similarity(
        np.array([0.9, np.nan]), np.array([0.9, 0.4, np.nan]), 1.0
    )
    assert sim.shape == (2, 3)
    assert sim[0].tolist() == pytest.approx([1.0, 0.5, 0.0])
    assert sim[1].tolist() == pytest.approx([0.0, 0.0, 1.0])
    # a wider column is scaled by its range and floored at zero
    assert rank_similarity(np.array([0.0]), np.array([5.0, 20.0]), 10.0)[
        0
    ].tolist() == pytest.approx([0.5, 0.0])


def test_leaf_similarity_is_the_share_of_shared_leaves(bundles, dataset_dir):
    forest = DeploymentBundle.load(bundles["forest"])
    data = pd.read_parquet(dataset_dir / "dataset.parquet")
    X = data[list(forest.feature_columns)].head(60)
    leaves = leaf_ids(forest.model, X)
    assert leaves.shape == (60, 12)
    sim = leaf_similarity(forest.model, X.head(3), X, chunk_rows=25)
    assert sim.shape == (3, 60)
    # a row shares every leaf with itself, and the chunking is exact
    assert sim[0, 0] == 1.0 and sim[2, 2] == 1.0
    expected = (leaves == leaves[1]).mean(axis=1)
    assert sim[1].tolist() == pytest.approx(expected.tolist())
    # a rank factor has no leaves
    factor = DeploymentBundle.load(bundles["factor"])
    assert leaf_ids(factor.model, X) is None
    # the features on a row's paths, most used first, shares in (0, 1]
    paths = path_features(forest.model, X.head(2))
    assert len(paths) == 2 and paths[0]
    assert all(0 < share <= 1 for _, share in paths[0])
    assert paths[0][0][1] >= paths[0][-1][1]


def test_analogues_of_named_tickers(bundles, inference, data_root, tmp_path):
    """The blend's analogues: one row per stock, never the pick itself,
    ordered by the mean of the models' similarities, with outcomes."""
    frame = pd.read_parquet(inference / "dataset.parquet")
    ticker = str(frame["ticker"].iloc[0])
    out = run_analogues(
        [bundles["forest"], bundles["factor"]], inference,
        tickers=[ticker], top=5, data_root=data_root,
        results_path=tmp_path / "results.csv",
        predictions_dir=tmp_path / "predictions",
    )
    rows = out["analogues"]
    assert 0 < len(rows) <= 5
    assert rows["analogue"].tolist() == list(range(1, len(rows) + 1))
    own = frame.loc[frame["ticker"] == ticker, "permaticker"].iloc[0]
    assert own not in set(rows["permaticker"])
    assert rows["permaticker"].is_unique
    sims = rows["similarity"].tolist()
    assert sims == sorted(sims, reverse=True)
    assert all(0.0 <= s <= 1.0 for s in sims)
    assert {"sim_forest", "sim_factor"} <= set(rows.columns)
    assert rows["similarity"].tolist() == pytest.approx(
        ((rows["sim_forest"] + rows["sim_factor"]) / 2).tolist()
    )
    assert "fwd_3y_cagr" in rows.columns and "label_forest" in rows.columns
    summary = out["summary"].iloc[0]
    assert summary["pick"] == ticker and summary["analogues"] == len(rows)
    assert 0.0 <= summary["lost_money"] <= 1.0
    assert out["pool_summary"]["rows"] > 0
    report = out["report_path"].read_text()
    assert "explanation, not an evaluation" in report
    assert f"## {ticker}" in report and "*whole pool*" in report
    meta = json.loads(out["meta_path"].read_text())
    assert meta["method"]["forest"].startswith("shared leaves")
    assert meta["method"]["factor"] == "rank column book_to_market_rank"
    assert pd.read_csv(out["csv_path"]).shape[0] == len(rows)

    # the pick's own history can be asked for, and then comes first
    with_self = run_analogues(
        [bundles["tree"]], inference, tickers=[ticker], top=3,
        include_self=True, data_root=data_root,
        results_path=tmp_path / "results.csv",
        predictions_dir=tmp_path / "predictions",
    )
    assert with_self["analogues"]["similarity"].iloc[0] == 1.0


def test_analogues_of_the_picks_and_argument_checks(
    bundles, inference, data_root, tmp_path, capsys
):
    kwargs = dict(
        data_root=data_root, results_path=tmp_path / "results.csv",
        predictions_dir=tmp_path / "predictions",
    )
    out = run_analogues(
        [bundles["forest"], bundles["factor"]], inference, pick=2, top=3,
        **kwargs,
    )
    assert len(out["summary"]) == 2
    assert out["analogues"].groupby("pick_permaticker").size().max() <= 3
    ranking = pd.read_csv(out["ranking_path"])
    picked = ranking[ranking["pick"].notna()]["permaticker"].tolist()
    assert out["summary"]["pick_permaticker"].tolist() == picked
    with pytest.raises(ConfigError, match="name the stocks"):
        run_analogues([bundles["forest"]], inference, **kwargs)
    with pytest.raises(ConfigError, match="not in the ranking"):
        run_analogues(
            [bundles["forest"]], inference, tickers=["NOSUCH"], **kwargs
        )
    assert (
        _main(
            [
                str(bundles["forest"]), str(bundles["factor"]), str(inference),
                "--pick", "2", "--top", "2",
                "--data-root", str(data_root),
                "--results", str(tmp_path / "results.csv"),
                "--predictions-dir", str(tmp_path / "predictions"),
            ]
        )
        == 0
    )
    assert "Explanation, not evaluation" in capsys.readouterr().out
