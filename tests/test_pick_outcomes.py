"""Pick outcomes (eval.picks): report-only outcomes of the top-K picks,
the common yardstick for comparing labels in front of vml-backtest.
They must describe exactly precision@K's picks, never enter a fit, and
leave the identity of configs that do not use them untouched."""

import math

import numpy as np
import pandas as pd
import pytest

from eval.era import collect_predictions
from eval.metrics import precision_at_k
from eval.picks import (
    outcome_column,
    pick_outcome_metrics,
    pick_outcome_table,
)
from harness.config import EvalConfig, ExperimentConfig
from harness.errors import ConfigError, DatasetValidationError
from harness.evaluate import evaluate_bundle
from harness.results import ResultsStore
from harness.runner import run_experiment
from harness.sweep import SweepConfig, run_sweep

VERSION = "dataset_v0.0-test"
OUTCOMES = ["label_3y_cagr_ge_8", "fwd_3y_cagr", "fwd_1y_cagr >= 0.0"]


def _config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "tree_with_picks",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


def _frame():
    """Two years, four rows each; scores rank rows 0..3 within a year."""
    return pd.concat(
        [
            collect_predictions(
                2016, np.full(4, 2016), [1, 0, 1, 0], [0.9, 0.8, 0.2, 0.1],
                np.ones(4),
                stocks=[10, 10, 11, 12],
                pick_outcomes={
                    outcome_column("beat", True): [1.0, 0.0, 1.0, np.nan],
                    outcome_column("ret", False): [0.30, -0.10, 0.05, 0.01],
                },
            ),
            collect_predictions(
                2017, np.full(4, 2017), [0, 1, 0, 0], [0.7, 0.6, 0.5, 0.4],
                np.ones(4),
                stocks=[20, 21, 22, 23],
                pick_outcomes={
                    outcome_column("beat", True): [np.nan, 1.0, 0.0, 0.0],
                    outcome_column("ret", False): [0.50, 0.10, -0.20, 0.00],
                },
            ),
        ],
        ignore_index=True,
    )


# --- the metrics -----------------------------------------------------------


def test_pooled_metrics_pick_per_year():
    m = pick_outcome_metrics(_frame(), top_k=(2,))
    # picks: 2016 rows 0,1 and 2017 rows 0,1
    assert m["pick_mean_ret_at_2"] == pytest.approx((0.30 - 0.10 + 0.50 + 0.10) / 4)
    assert m["pick_median_ret_at_2"] == pytest.approx(0.20)
    # the NULL outcome of the 2017 top pick is left out, not a miss
    assert m["pick_mean_beat_at_2"] == pytest.approx(2 / 3)
    assert "pick_median_beat_at_2" not in m
    # reference over every test row, unweighted
    assert m["all_mean_ret"] == pytest.approx(0.0825)
    assert m["all_mean_beat"] == pytest.approx(3 / 6)
    # 2016's two picks are one stock, 2017's are two
    assert m["n_stocks_at_2"] == pytest.approx(1.5)


def test_single_fold_metrics_pick_over_the_fold():
    m = pick_outcome_metrics(_frame(), top_k=(2,), per_year=False)
    # one ranking over all eight rows: the two highest scores
    assert m["pick_mean_ret_at_2"] == pytest.approx((0.30 - 0.10) / 2)
    assert m["n_stocks_at_2"] == 1


def test_picks_are_precision_at_k_picks():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 200).astype(float)
    scores = np.round(rng.uniform(size=200), 1)  # many ties
    frame = collect_predictions(
        2016, np.full(200, 2016), y, scores, np.ones(200),
        stocks=np.arange(200),
        pick_outcomes={outcome_column("same", True): y},
    )
    m = pick_outcome_metrics(frame, top_k=(20,))
    assert m["pick_mean_same_at_20"] == precision_at_k(y, scores, 20)


def test_frame_without_outcomes_yields_nothing():
    frame = collect_predictions(
        2016, np.full(3, 2016), [1, 0, 1], [0.3, 0.2, 0.1], np.ones(3)
    )
    assert pick_outcome_metrics(frame) == {}
    assert "permaticker" not in frame.columns


def test_table_has_a_row_per_year_and_a_pooled_row():
    table = pick_outcome_table(_frame(), 2)
    assert list(table["era"]) == ["2016", "2017", "pooled"]
    assert list(table["picks"]) == [2, 2, 4]
    assert table.loc[0, "stocks"] == 1
    assert table.loc[0, "ret mean"] == pytest.approx(0.10)
    assert table.loc[0, "ret all rows mean"] == pytest.approx(0.065)
    assert table.loc[1, "beat hit rate"] == pytest.approx(1.0)


# --- the config ------------------------------------------------------------


def test_config_without_outcomes_keeps_its_identity():
    plain = _config()
    assert plain.pick_outcomes == ()
    assert "pick_outcomes" not in plain.canonical_json()
    assert "pick_outcomes" not in plain.to_raw_dict()
    with_outcomes = _config(pick_outcomes=OUTCOMES)
    assert with_outcomes.config_hash != plain.config_hash
    # round-trips; expressions are normalized like a label's
    assert ExperimentConfig.from_dict(with_outcomes.to_raw_dict()) == with_outcomes
    spaced = _config(pick_outcomes=["fwd_1y_cagr>=0.0"])
    assert spaced.pick_outcomes == ("fwd_1y_cagr >= 0.0",)


@pytest.mark.parametrize(
    "outcomes, match",
    [
        ("label_3y_cagr_ge_8", "must be a list"),
        (["fwd_3y_cagr", "fwd_3y_cagr"], "repeats"),
        (["fwd_5y_cagr"], "outlives"),
        (["book_to_market_rank"], "horizon"),
    ],
)
def test_config_refuses_bad_outcomes(outcomes, match):
    with pytest.raises(ConfigError, match=match):
        _config(pick_outcomes=outcomes)


def test_outcome_must_be_a_label_column(data_root, tmp_path):
    # carries a horizon token, but is not in the manifest's labels group
    config = _config(pick_outcomes=["sample_weight_3y"])
    with pytest.raises(DatasetValidationError):
        run_experiment(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )


# --- the run ---------------------------------------------------------------


@pytest.fixture(scope="module")
def run(data_root, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("pick_outcomes")
    paths = {
        "data_root": data_root,
        "results": tmp / "results.csv",
        "reports": tmp / "reports",
        "models": tmp / "models",
    }
    summary = run_experiment(
        _config(pick_outcomes=OUTCOMES),
        data_root=data_root,
        results_path=paths["results"],
        reports_dir=paths["reports"],
        models_dir=paths["models"],
    )
    return summary, paths


def test_run_reports_pick_outcomes(run):
    summary, _ = run
    pooled = summary["pooled_metrics"]
    expression = "label_1y_cagr_ge_0p0"
    for key in (
        "pick_mean_label_3y_cagr_ge_8_at_5",
        "all_mean_label_3y_cagr_ge_8",
        "pick_mean_fwd_3y_cagr_at_5",
        "pick_median_fwd_3y_cagr_at_5",
        "all_mean_fwd_3y_cagr",
        "all_median_fwd_3y_cagr",
        f"pick_mean_{expression}_at_5",
        "n_stocks_at_5",
    ):
        assert key in pooled, key
        assert math.isfinite(pooled[key])
    assert 0.0 <= pooled["pick_mean_label_3y_cagr_ge_8_at_5"] <= 1.0
    assert 1 <= pooled["n_stocks_at_5"] <= 5
    # binary outcomes have no median
    assert "pick_median_label_3y_cagr_ge_8_at_5" not in pooled
    # the per-fold ledger metrics carry the block too
    fold = summary["fold_results"][0]["metrics"]
    assert "pick_mean_fwd_3y_cagr_at_5" in fold
    report = summary["report_path"].read_text()
    assert "## Pick outcomes" in report
    assert "### Top 5 per test year: `fwd_3y_cagr`" in report
    assert "### Top 5 per test year: `label_3y_cagr_ge_8`" in report
    assert "picks median" in report and "picks hit rate" in report


def test_outcomes_do_not_change_the_model_or_its_cell(run, data_root, tmp_path):
    summary, paths = run
    plain = run_experiment(
        _config(name="tree_plain"),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    for key, value in plain["pooled_metrics"].items():
        assert summary["pooled_metrics"][key] == pytest.approx(value, nan_ok=True)
    assert "## Pick outcomes" not in plain["report_path"].read_text()
    rows = ResultsStore(paths["results"]).load()
    assert set(rows["label"]) == {"label_3y_beat_spy"}


def test_training_label_as_outcome_equals_precision(data_root, tmp_path):
    summary = run_experiment(
        _config(name="tree_self", pick_outcomes=["label_3y_beat_spy"]),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    pooled = summary["pooled_metrics"]
    assert pooled["pick_mean_label_3y_beat_spy_at_5"] == pytest.approx(
        pooled["precision_at_5"]
    )
    for fr in summary["fold_results"]:
        m = fr["metrics"]
        assert m["pick_mean_label_3y_beat_spy_at_5"] == pytest.approx(
            m["precision_at_5"]
        )


def test_eval_config_adds_outcomes_to_a_saved_bundle(run):
    summary, paths = run
    inherited = evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict({"name": "k3", "top_k": [3]}),
        data_root=paths["data_root"],
        results_path=paths["results"],
        reports_dir=paths["reports"],
    )
    assert "pick_mean_fwd_3y_cagr_at_3" in inherited["fold_results"][0]["metrics"]
    replaced = evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict(
            {"name": "k3b", "top_k": [3], "pick_outcomes": ["fwd_1y_cagr"]}
        ),
        data_root=paths["data_root"],
        results_path=paths["results"],
        reports_dir=paths["reports"],
    )
    metrics = replaced["fold_results"][0]["metrics"]
    assert "pick_mean_fwd_1y_cagr_at_3" in metrics
    assert "pick_mean_fwd_3y_cagr_at_3" not in metrics
    with pytest.raises(ConfigError, match="outlives"):
        evaluate_bundle(
            summary["model_bundle"],
            EvalConfig.from_dict(
                {"name": "k3c", "pick_outcomes": ["fwd_5y_cagr"]}
            ),
            data_root=paths["data_root"],
            results_path=paths["results"],
            reports_dir=paths["reports"],
        )


# --- the sweep -------------------------------------------------------------


def _sweep_dict(**overrides):
    raw = {
        "name": "mini_pick_sweep",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "folds": "all",
        "feature_groups": ["ranks"],
        "seeds": [3],
        "top_k": [5],
        "cells": [{"horizon_years": 3, "label": "label_3y_beat_spy"}],
        "model": {"name": "decision_tree", "min_weight_fraction_leaf": 0.02},
        "grid": {"max_depth": [2, 3]},
    }
    raw.update(overrides)
    return raw


def test_sweep_identity_unchanged_without_outcomes():
    plain = SweepConfig.from_dict(_sweep_dict())
    with_outcomes = SweepConfig.from_dict(_sweep_dict(pick_outcomes=OUTCOMES))
    assert plain.identity_hash != with_outcomes.identity_hash
    assert all(r.config.pick_outcomes == () for r in plain.expand())
    assert all(
        r.config.pick_outcomes == with_outcomes.pick_outcomes
        for r in with_outcomes.expand()
    )
    with pytest.raises(ConfigError, match="outlives"):
        SweepConfig.from_dict(_sweep_dict(pick_outcomes=["fwd_5y_cagr"]))


def test_sweep_summary_carries_pick_outcomes(data_root, tmp_path):
    out = run_sweep(
        SweepConfig.from_dict(_sweep_dict(pick_outcomes=OUTCOMES)),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert out["n_failed"] == 0
    summary = pd.read_csv(out["summary_csv"])
    assert "pick_mean_fwd_3y_cagr_at_5" in summary.columns
    assert "n_stocks_at_5" in summary.columns
    # ranked by the metric of record, not by an outcome
    assert summary["precision_at_5"].is_monotonic_decreasing
    text = out["summary_md"].read_text()
    assert "pick_mean_fwd_3y_cagr_at_5" in text
