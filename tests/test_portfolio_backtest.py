"""Signal guardrails and the end-to-end backtest on the miniature
dataset + price panel: deployment bundles refused, dataset-version pins
enforced, buys confined to fold years, both legs under identical
deposits, everything logged."""

import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.dataset import Dataset
from harness.deploy import train_deployment_model
from harness.errors import ConfigError
from harness.model_store import ModelBundleError
from harness.results import ResultsStore
from portfolio.backtest import BACKTEST_SCHEME, run_backtest
from portfolio.config import BacktestConfig, FilterSpec
from portfolio.signals import (
    ModelSet,
    apply_filters,
    apply_min_score,
    combine_scores,
    validate_filter_columns,
)

DATASET = "dataset_v0.0-test"
PRICES = "prices_v0.0-test"


def _bt_config(bundle_dir, **overrides) -> BacktestConfig:
    raw = {
        "name": "bt_e2e",
        "dataset_version": DATASET,
        "prices_version": PRICES,
        "bundles": [str(bundle_dir)],
        "signal": {"combine": "product"},
        "filters": [{"column": "book_to_market", "op": ">", "value": 0.0}],
        "investability": "none",
        "portfolio": {
            "strategy": "buy_and_hold",
            "top_k": 2,
            "weighting": "score",
            "monthly_cash": 1000.0,
        },
        "execution": {"cost_bps": 10.0, "max_quote_age_days": 3},
    }
    raw.update(overrides)
    return BacktestConfig.from_dict(raw)


# ------------------------------------------------------------ signal guards


def test_deployment_bundles_are_refused(data_root, tmp_path):
    summary = train_deployment_model(
        ExperimentConfig.from_dict(
            {
                "name": "bt_dep_tree",
                "dataset_version": DATASET,
                "scheme": "walkforward",
                "label": "label_3y_beat_spy",
                "feature_groups": ["features", "ranks"],
                "model": {"name": "decision_tree", "max_depth": 2},
            }
        ),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        models_dir=tmp_path / "models",
    )
    with pytest.raises(ModelBundleError, match="deployment"):
        ModelSet([summary["bundle_path"]])


def test_dataset_version_pin_is_enforced(data_root, wf_bundle_dir):
    dataset = Dataset(data_root / DATASET)
    model_set = ModelSet([wf_bundle_dir])
    config = _bt_config(wf_bundle_dir, dataset_version="dataset_v9.9")
    with pytest.raises(ConfigError, match="dataset"):
        model_set.validate_against(config, dataset)


def test_filters_cannot_reference_labels(data_root):
    dataset = Dataset(data_root / DATASET)
    bad = (FilterSpec("label_3y_beat_spy", ">", 0.0),)
    with pytest.raises(ConfigError, match="label"):
        validate_filter_columns(bad, dataset, "[[filters]]")
    with pytest.raises(ConfigError, match="not in"):
        validate_filter_columns(
            (FilterSpec("no_such_column", ">", 0.0),), dataset, "[[filters]]"
        )


def test_filter_and_floor_semantics():
    frame = pd.DataFrame(
        {
            "x": [1.0, None, -1.0],
            "score_a": [0.9, 0.9, 0.9],
            "score_b": [0.6, 0.4, 0.6],
        }
    )
    passed = apply_filters(frame, (FilterSpec("x", ">", 0.0),))
    assert list(passed.index) == [0]  # NULL fails, negative fails
    floored = apply_min_score(frame, ["score_a", "score_b"], 0.5)
    assert list(floored.index) == [0, 2]


def test_combine_modes():
    frame = pd.DataFrame({"score_a": [0.5, 0.9], "score_b": [0.8, 0.1]})
    cols = ["score_a", "score_b"]
    assert combine_scores(frame, cols, "product").tolist() == pytest.approx(
        [0.4, 0.09]
    )
    assert combine_scores(frame, cols, "mean").tolist() == pytest.approx(
        [0.65, 0.5]
    )
    assert combine_scores(frame, cols, "min").tolist() == pytest.approx(
        [0.5, 0.1]
    )
    mean_rank = combine_scores(frame, cols, "mean_rank")
    assert mean_rank.tolist() == pytest.approx([-1.5, -1.5])


# ------------------------------------------------------------- end to end


def test_backtest_end_to_end(data_root, prices_dir, wf_bundle_dir, tmp_path):
    results = tmp_path / "results.csv"
    reports = tmp_path / "reports"
    summary = run_backtest(
        _bt_config(wf_bundle_dir),
        data_root=data_root,
        results_path=results,
        reports_dir=reports,
    )
    assert summary["status"] == "completed"
    # buys are confined to the bundle's walk-forward fold years
    assert summary["buy_years"] == [2016, 2017]
    strategy = summary["strategy_result"]
    benchmark = summary["benchmark_result"]

    buys = strategy.trades[strategy.trades["side"] == "buy"]
    assert not buys.empty
    assert set(buys["date"].dt.year) <= {2016, 2017}
    # 24 monthly deposits into both legs, identically
    assert strategy.total_deposits == pytest.approx(24_000.0)
    assert benchmark.total_deposits == pytest.approx(24_000.0)
    assert list(strategy.monthly["date"]) == list(benchmark.monthly["date"])
    # valuation runs to the panel's final trading day
    assert strategy.monthly["date"].iloc[-1] == pd.Timestamp("2021-06-30")
    assert strategy.final_value > 0
    assert benchmark.final_value > 0
    # costs were actually charged
    assert strategy.total_costs > 0

    report = (reports / "bt_e2e.md").read_text()
    assert "split_folds.parquet" in report
    assert "explicitly opted out" in report  # investability = "none"
    assert "configurations tried" in report
    for artifact in ("bt_e2e_equity.csv", "bt_e2e_trades.csv",
                     "bt_e2e_equity.png"):
        assert (reports / artifact).exists()

    store = ResultsStore(results).load()
    row = store[store["scheme"] == BACKTEST_SCHEME].iloc[-1]
    assert row["status"] == "completed"
    assert row["experiment"] == "bt_e2e"
    assert row["fold"] == "2016-2017"


def test_backtest_failure_is_logged(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    results = tmp_path / "results.csv"
    config = _bt_config(
        wf_bundle_dir,
        name="bt_bad_filter",
        filters=[{"column": "label_3y_beat_spy", "op": ">", "value": 0.0}],
    )
    with pytest.raises(ConfigError):
        run_backtest(
            config,
            data_root=data_root,
            results_path=results,
            reports_dir=tmp_path / "reports",
        )
    store = ResultsStore(results).load()
    assert store.iloc[-1]["status"] == "failed"
    assert store.iloc[-1]["scheme"] == BACKTEST_SCHEME


def test_window_outside_fold_years_is_refused(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    from datetime import date

    config = _bt_config(
        wf_bundle_dir,
        name="bt_holdout_grab",
        window={"start": date(2018, 1, 1), "end": date(2019, 12, 31)},
    )
    with pytest.raises(ConfigError, match="fold years"):
        run_backtest(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
