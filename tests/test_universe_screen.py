"""Universe filters, the portfolio screen, selection by score, and
boolean feature columns.

A universe is a row filter on feature columns declared in the config:
it changes which rows are fitted and evaluated, never which role a row
has, and it puts the run in its own ledger cell. The screen and the
threshold outcomes are report-only readings of a run's picks."""

import json
import math
import shutil

import numpy as np
import pandas as pd
import pytest

from eval.era import collect_predictions
from eval.picks import (
    outcome_column,
    screen_group_table,
    screen_metrics,
    screen_picks,
    screen_table,
    threshold_outcome_metrics,
    threshold_outcome_table,
)
from harness.config import (
    EvalConfig,
    ExperimentConfig,
    PickScreen,
    split_cell_label,
)
from harness.dataset import Dataset, feature_matrix
from harness.deploy import train_deployment_model
from harness.errors import ConfigError, DatasetValidationError
from harness.evaluate import evaluate_bundle
from harness.filters import FilterSpec
from harness.results import ResultsStore
from harness.runner import run_experiment
from harness.sweep import SweepConfig, run_sweep
from portfolio.config import BacktestConfig
from portfolio.signals import ModelSet

VERSION = "dataset_v0.1-universe"
SECTORS = ["Utilities", "Technology", "Energy"]
FLOOR = {"column": "dollar_volume_3m", "op": ">=", "value": 100.0}


@pytest.fixture(scope="module")
def universe_root(dataset_dir, tmp_path_factory):
    """The mini dataset plus three feature columns: a liquidity column
    (NULL for one stock), a sector, and a boolean flag with NULLs."""
    root = tmp_path_factory.mktemp("universe_data")
    out = root / VERSION
    shutil.copytree(dataset_dir, out)
    data = pd.read_parquet(out / "dataset.parquet")
    rng = np.random.default_rng(3)
    data["dollar_volume_3m"] = rng.uniform(0, 300, len(data))
    data.loc[data["permaticker"] == 100010, "dollar_volume_3m"] = np.nan
    data["sector"] = [SECTORS[p % 3] for p in data["permaticker"]]
    flag = rng.uniform(size=len(data))
    data["negative_equity"] = pd.array(
        np.where(flag < 0.2, None, flag < 0.6), dtype="boolean"
    ).astype(object)
    data.to_parquet(out / "dataset.parquet")
    manifest = json.loads((out / "manifest.json").read_text())
    manifest["columns"]["features"] += [
        "dollar_volume_3m", "sector", "negative_equity",
    ]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return root


def _config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "tree_universe",
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


def _run(config, root, tmp_path, **kwargs):
    return run_experiment(
        config,
        data_root=root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        **kwargs,
    )


# --- config ----------------------------------------------------------------


def test_config_without_universe_keeps_its_hash_and_cell():
    plain = _config()
    assert plain.universe == () and plain.pick_screen is None
    assert plain.cell_label == "label_3y_beat_spy"
    payload = json.loads(plain.canonical_json())
    assert "universe" not in payload and "pick_screen" not in payload


def test_universe_qualifies_the_cell_and_the_hash():
    plain = _config()
    floored = _config(universe=[FLOOR])
    assert floored.config_hash != plain.config_hash
    assert floored.cell_label == (
        "label_3y_beat_spy [universe: dollar_volume_3m >= 100]"
    )
    assert split_cell_label(floored.cell_label) == (
        "label_3y_beat_spy", "dollar_volume_3m >= 100"
    )
    assert split_cell_label("label_3y_beat_spy") == ("label_3y_beat_spy", "")
    # one universe, one hash: integer or float spelling, any order
    other = {"column": "book_to_market_rank", "op": "<", "value": 0.9}
    a = _config(universe=[FLOOR, other])
    b = _config(universe=[other, {**FLOOR, "value": 100}])
    assert a.config_hash == b.config_hash and a.cell_label == b.cell_label
    # and scope "test" is another config in the same cell
    test_scope = _config(universe=[FLOOR], universe_scope="test")
    assert test_scope.config_hash != floored.config_hash
    assert test_scope.cell_label == floored.cell_label


def test_config_round_trips_through_the_bundle_mapping():
    config = _config(
        universe=[FLOOR],
        universe_scope="test",
        pick_screen={"top_k": 2, "max_per_group": 1},
    )
    again = ExperimentConfig.from_dict(config.to_raw_dict())
    assert again == config and again.config_hash == config.config_hash


def test_bad_universe_and_screen_configs_are_refused():
    with pytest.raises(ConfigError, match="universe_scope"):
        _config(universe=[FLOOR], universe_scope="train")
    with pytest.raises(ConfigError, match="no \\[\\[universe\\]\\]"):
        _config(universe_scope="test")
    with pytest.raises(ConfigError, match="repeats"):
        _config(universe=[FLOOR, {**FLOOR, "value": 100}])
    with pytest.raises(ConfigError, match="per must be"):
        _config(pick_screen={"per": "month"})
    with pytest.raises(ConfigError, match="positive integer"):
        _config(pick_screen={"top_k": 0})
    with pytest.raises(ConfigError, match="group_column is set"):
        _config(pick_screen={"group_column": "sector"})


# --- the universe in a run -------------------------------------------------


def test_universe_filters_train_and_test_rows(universe_root, tmp_path):
    plain = _run(_config(), universe_root, tmp_path)
    floored = _run(_config(name="floored", universe=[FLOOR]),
                   universe_root, tmp_path)
    dataset = Dataset(universe_root / VERSION)
    for before, after in zip(plain["fold_results"], floored["fold_results"]):
        fold = after["fold"]
        split = dataset.apply_split(
            "walkforward", fold, 3,
            columns=["dollar_volume_3m", "label_3y_beat_spy"],
        )
        inside_test = int((split.test["dollar_volume_3m"] >= 100).sum())
        labeled = split.train[split.train["label_3y_beat_spy"].notna()]
        inside_train = int((labeled["dollar_volume_3m"] >= 100).sum())
        assert after["n_test_rows"] == inside_test < before["n_test_rows"]
        assert after["n_train_rows"] == inside_train < before["n_train_rows"]
        assert after["n_test_rows_all"] == before["n_test_rows"]
    report = floored["report_path"].read_text()
    assert "universe: `dollar_volume_3m >= 100`" in report
    assert "test_rows_before_universe" in report


def test_scope_test_trains_on_every_row(universe_root, tmp_path):
    plain = _run(_config(), universe_root, tmp_path)
    scoped = _run(
        _config(name="scoped", universe=[FLOOR], universe_scope="test"),
        universe_root, tmp_path,
    )
    for before, after in zip(plain["fold_results"], scoped["fold_results"]):
        assert after["n_train_rows"] == before["n_train_rows"]
        assert after["n_test_rows"] < before["n_test_rows"]
    assert "evaluated inside the universe only" in (
        scoped["report_path"].read_text()
    )


def test_null_fails_the_universe(universe_root):
    dataset = Dataset(universe_root / VERSION)
    frame = dataset.frame(["dollar_volume_3m"])
    kept = dataset.apply_universe(
        frame, (FilterSpec("dollar_volume_3m", ">=", 0.0),)
    )
    assert frame["dollar_volume_3m"].isna().any()
    assert kept["dollar_volume_3m"].notna().all()
    assert 100010 not in set(kept["permaticker"])


def test_universe_may_not_read_a_label(universe_root, tmp_path):
    config = _config(
        universe=[{"column": "fwd_3y_cagr", "op": ">", "value": 0.0}]
    )
    with pytest.raises(ConfigError, match="can never be screened on"):
        _run(config, universe_root, tmp_path)


def test_universe_runs_are_counted_in_their_own_cell(universe_root, tmp_path):
    _run(_config(), universe_root, tmp_path)
    summary = _run(_config(name="floored", universe=[FLOOR]),
                   universe_root, tmp_path)
    store = ResultsStore(tmp_path / "results.csv")
    cell = "label_3y_beat_spy [universe: dollar_volume_3m >= 100]"
    assert set(store.load()["label"]) == {"label_3y_beat_spy", cell}
    assert store.configurations_tried(VERSION, "walkforward", 3, cell) == 1
    assert store.configurations_tried(
        VERSION, "walkforward", 3, "label_3y_beat_spy"
    ) == 1
    assert store.configurations_tried_any_universe(
        VERSION, "walkforward", 3, "label_3y_beat_spy"
    ) == 2
    assert summary["configurations_tried"] == 1
    assert "**2 against this label in any universe**" in (
        summary["report_path"].read_text()
    )


def test_eval_config_universe_is_scope_test(universe_root, tmp_path):
    trained = _run(_config(), universe_root, tmp_path,
                   models_dir=tmp_path / "models")
    summary = evaluate_bundle(
        trained["model_bundle"],
        EvalConfig.from_dict({"name": "floor", "top_k": [5],
                              "universe": [FLOOR]}),
        data_root=universe_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    for before, after in zip(trained["fold_results"], summary["fold_results"]):
        assert after["n_train_rows"] == before["n_train_rows"]
        assert after["n_test_rows"] < before["n_test_rows"]
    rows = ResultsStore(tmp_path / "results.csv").load()
    assert rows.iloc[-1]["label"].endswith("[universe: dollar_volume_3m >= 100]")

    floored = _run(_config(name="floored", universe=[FLOOR]), universe_root,
                   tmp_path, models_dir=tmp_path / "models")
    with pytest.raises(ConfigError, match="pinned"):
        evaluate_bundle(
            floored["model_bundle"],
            EvalConfig.from_dict({"name": "again", "universe": [FLOOR]}),
            data_root=universe_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
    # re-scoring a floored bundle keeps its universe
    again = evaluate_bundle(
        floored["model_bundle"],
        EvalConfig.from_dict({"name": "again", "top_k": [3]}),
        data_root=universe_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert [f["n_test_rows"] for f in again["fold_results"]] == [
        f["n_test_rows"] for f in floored["fold_results"]
    ]


def test_deployment_refit_stays_inside_the_universe(universe_root, tmp_path):
    kwargs = dict(
        data_root=universe_root,
        results_path=tmp_path / "results.csv",
        models_dir=tmp_path / "models",
    )
    plain = train_deployment_model(_config(), **kwargs)
    floored = train_deployment_model(
        _config(name="floored", universe=[FLOOR]), **kwargs
    )
    scoped = train_deployment_model(
        _config(name="scoped", universe=[FLOOR], universe_scope="test"),
        **kwargs,
    )
    assert floored["n_train_rows"] < plain["n_train_rows"]
    assert scoped["n_train_rows"] == plain["n_train_rows"]


def test_backtest_must_screen_on_the_bundles_universe(universe_root, tmp_path):
    floored = _run(_config(name="floored", universe=[FLOOR]), universe_root,
                   tmp_path, models_dir=tmp_path / "models")
    model_set = ModelSet([floored["model_bundle"]])
    dataset = Dataset(universe_root / VERSION)

    def backtest(investability):
        return BacktestConfig.from_dict(
            {
                "name": "bt",
                "dataset_version": VERSION,
                "prices_version": "prices_v0.0-test",
                "bundles": [str(floored["model_bundle"])],
                "signal": {"combine": "mean_rank"},
                "investability": investability,
                "portfolio": {"weighting": "equal"},
                "execution": {"cost_bps": 10.0},
            }
        )

    with pytest.raises(ConfigError, match="trained inside the universe"):
        model_set.validate_against(backtest("none"), dataset)
    with pytest.raises(ConfigError, match="trained inside the universe"):
        model_set.validate_against(
            backtest([{**FLOOR, "value": 50.0}]), dataset
        )
    model_set.validate_against(backtest([{**FLOOR, "value": 100}]), dataset)


def test_sweep_carries_universe_and_screen(universe_root, tmp_path):
    sweep = SweepConfig.from_dict(
        {
            "name": "sweep_universe",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "cells": [{"label": "label_3y_beat_spy"}],
            "feature_groups": ["ranks"],
            "top_k": [5],
            "pick_outcomes": ["fwd_3y_cagr"],
            "universe": [FLOOR],
            "pick_screen": {"top_k": 2, "max_per_group": 1},
            "model": {"name": "decision_tree"},
            "grid": {"max_depth": [1, 2]},
        }
    )
    plain = SweepConfig.from_dict(
        {
            "name": "sweep_universe",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "cells": [{"label": "label_3y_beat_spy"}],
            "feature_groups": ["ranks"],
            "top_k": [5],
            "pick_outcomes": ["fwd_3y_cagr"],
            "model": {"name": "decision_tree"},
            "grid": {"max_depth": [1, 2]},
        }
    )
    assert sweep.identity_hash != plain.identity_hash
    runs = sweep.expand()
    assert all(r.config.universe == sweep.universe for r in runs)
    assert all(r.config.pick_screen == sweep.pick_screen for r in runs)
    result = run_sweep(
        sweep,
        data_root=universe_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert result["n_failed"] == 0
    pooled = result["runs"][0]["pooled_metrics"]
    assert pooled["screen_n"] > 0 and "screen_mean_fwd_3y_cagr" in pooled
    summary = result["summary_md"].read_text()
    assert "universe: `dollar_volume_3m >= 100`" in summary
    assert "label_3y_beat_spy [universe: dollar_volume_3m >= 100]" in summary
    assert "screen_mean_fwd_3y_cagr" in summary


# --- boolean feature columns ------------------------------------------------


def test_boolean_features_become_floats_and_keep_null():
    frame = pd.DataFrame(
        {
            "flag": pd.Series([True, False, None], dtype=object),
            "strict": [True, False, True],
            "x": [0.1, 0.2, 0.3],
        }
    )
    X = feature_matrix(frame, ["flag", "strict", "x"])
    assert X["flag"].dtype == float and X["strict"].dtype == float
    assert X["flag"].tolist()[:2] == [1.0, 0.0] and math.isnan(X["flag"][2])
    assert X["strict"].tolist() == [1.0, 0.0, 1.0]
    # no boolean column selected: the frame's own columns, untouched
    assert feature_matrix(frame, ["x"])["x"].tolist() == [0.1, 0.2, 0.3]
    assert frame["flag"].dtype == object  # the source is not modified


def test_a_run_can_use_a_nullable_flag(universe_root, tmp_path):
    config = ExperimentConfig.from_dict(
        {
            "name": "tree_flag",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "label": "label_3y_beat_spy",
            "features": {
                "groups": ["ranks"], "columns": ["negative_equity"],
            },
            "model": {"name": "decision_tree", "max_depth": 2},
            "top_k": [5],
        }
    )
    summary = _run(config, universe_root, tmp_path,
                   models_dir=tmp_path / "models")
    assert summary["status"] == "completed"
    record = json.loads(
        (tmp_path / "reports" / "tree_flag_config.json").read_text()
    )
    assert "negative_equity" in record["feature_columns"]


# --- the portfolio screen ---------------------------------------------------


def _screen_frame():
    """One year, two quarters, four rows each; scores rank rows 0..3."""
    quarters = ["2016Q1"] * 4 + ["2016Q2"] * 4
    return collect_predictions(
        2016, np.full(8, 2016),
        [1, 1, 0, 0, 0, 1, 1, 0],
        [0.9, 0.8, 0.7, 0.1, 0.9, 0.8, 0.7, 0.6],
        np.ones(8),
        stocks=[1, 2, 3, 4, 1, 2, 3, 4],
        pick_outcomes={
            outcome_column("ret", False): [
                0.4, 0.2, -0.3, 0.0, -0.1, 0.1, 0.3, 0.5,
            ],
            outcome_column("loser", True): [0, 0, 1, 0, 1, 0, 0, 0],
        },
        quarters=quarters,
        groups=["U", "U", "T", "T", "U", "U", "T", None],
    )


def test_screen_picks_per_quarter_under_the_cap():
    frame = _screen_frame()
    uncapped = screen_picks(frame, PickScreen(top_k=2))
    assert uncapped["permaticker"].tolist() == [1, 2, 1, 2]
    capped = screen_picks(frame, PickScreen(top_k=2, max_per_group=1))
    # the second U row of each quarter is skipped for the best T row
    assert capped["permaticker"].tolist() == [1, 3, 1, 3]
    yearly = screen_picks(frame, PickScreen(per="year", top_k=3))
    assert len(yearly) == 3


def test_screen_metrics_and_tables():
    frame = _screen_frame()
    screen = PickScreen(top_k=2, max_per_group=1)
    m = screen_metrics(frame, screen)
    assert m["screen_n"] == 4 and m["screen_n_stocks"] == 2
    assert m["screen_precision"] == pytest.approx(0.5)
    assert m["screen_mean_ret"] == pytest.approx((0.4 - 0.3 - 0.1 + 0.3) / 4)
    assert m["screen_median_ret"] == pytest.approx(0.1)
    assert m["screen_mean_loser"] == pytest.approx(0.5)
    assert m["screen_top_group_share"] == pytest.approx(0.5)
    table = screen_table(frame, screen)
    assert table["era"].tolist() == ["2016", "pooled"]
    assert table["picks"].tolist() == [4, 4]
    groups = screen_group_table(frame, screen)
    assert set(groups["group"]) == {"U", "T", "unknown"}
    assert groups.set_index("group").loc["unknown", "share of picks"] == 0.0
    # a frame without the screen's columns reports nothing
    assert screen_metrics(frame.drop(columns=["quarter"]), screen) == {}
    assert screen_metrics(frame, None) == {}


def test_screen_in_a_run_report(universe_root, tmp_path):
    config = _config(
        pick_outcomes=["fwd_3y_cagr"],
        pick_screen={"top_k": 2, "max_per_group": 1},
        score_thresholds=[0.5],
    )
    summary = _run(config, universe_root, tmp_path)
    pooled = summary["pooled_metrics"]
    # 2 folds x 4 quarters x 2 picks
    assert pooled["screen_n"] == 16
    assert 0.0 <= pooled["screen_top_group_share"] <= 0.5
    assert "thr_mean_fwd_3y_cagr_at_0.5" in pooled
    report = summary["report_path"].read_text()
    assert "## Portfolio screen" in report
    assert "top 2 per test quarter, at most 1 per `sector`" in report
    assert "## Selection by score" in report
    with pytest.raises(ConfigError, match="group_column"):
        _run(
            _config(pick_screen={"top_k": 2, "max_per_group": 1,
                                 "group_column": "fwd_3y_cagr"}),
            universe_root, tmp_path,
        )


# --- selection by score -----------------------------------------------------


def test_threshold_outcomes_count_years_in_cash():
    frame = pd.concat(
        [
            _screen_frame(),
            collect_predictions(
                2017, np.full(2, 2017), [1, 0], [0.3, 0.2], np.ones(2),
                stocks=[5, 6],
                pick_outcomes={
                    outcome_column("ret", False): [0.1, 0.2],
                    outcome_column("loser", True): [0, 0],
                },
                quarters=["2017Q1"] * 2, groups=["U", "T"],
            ),
        ],
        ignore_index=True,
    )
    m = threshold_outcome_metrics(frame, [0.8])
    # 2016: rows scored 0.9, 0.8, 0.9, 0.8; 2017: none
    assert m["thr_years_at_0.8"] == 1 and m["thr_n_stocks_at_0.8"] == 2
    assert m["thr_mean_ret_at_0.8"] == pytest.approx((0.4 + 0.2 - 0.1 + 0.1) / 4)
    assert m["thr_median_ret_at_0.8"] == pytest.approx(0.15)
    table = threshold_outcome_table(frame, 0.8)
    assert table["era"].tolist() == ["2016", "2017", "pooled"]
    assert table["picks"].tolist() == [4, 0, 4]
    assert math.isnan(table.loc[1, "precision"])
    assert threshold_outcome_metrics(frame.drop(
        columns=[c for c in frame.columns if c.startswith("out")]
    ), [0.8]) == {}


# --- the screen's same-size peers --------------------------------------------


def test_peer_bands_cut_a_rank_into_equal_bands():
    from eval.picks import peer_bands

    bands = peer_bands(np.array([0.0, 0.049, 0.05, 0.5, 0.999, 1.0, np.nan]), 20)
    assert bands.tolist() == [0, 0, 1, 10, 19, 19, -1]
    assert peer_bands(np.array([0.3, 0.7]), 2).tolist() == [0, 1]


def test_screen_reads_the_picks_against_their_peers():
    """With a peer column the screen says what the test rows of the
    pick's own quarter and band did: a pick that is merely in the
    better band leads all rows and not its peers."""
    from eval.picks import PEER_COLUMN

    quarters = ["2016Q1"] * 6
    frame = collect_predictions(
        2016, np.full(6, 2016),
        [1, 1, 1, 0, 0, 0],
        [0.9, 0.8, 0.2, 0.7, 0.6, 0.1],
        np.ones(6),
        stocks=[1, 2, 3, 4, 5, 6],
        pick_outcomes={
            # band 1 (rows 0-2) earns 0.10 on average, band 0 minus 0.20
            outcome_column("ret", False): [0.12, 0.08, 0.10, -0.10, -0.30, np.nan],
        },
        quarters=quarters,
        peers=[1, 1, 1, 0, 0, 0],
    )
    assert frame[PEER_COLUMN].tolist() == [1, 1, 1, 0, 0, 0]
    screen = PickScreen(top_k=2, peer_column="log_marketcap_rank", peer_bins=2)
    m = screen_metrics(frame, screen)
    # the two picks are rows 0 and 1, both in band 1
    assert m["screen_mean_ret"] == pytest.approx(0.10)
    assert m["screen_peer_mean_ret"] == pytest.approx(0.10)
    assert m["screen_peer_precision"] == pytest.approx(1.0)
    assert m["screen_precision"] == pytest.approx(1.0)
    # against all rows the same picks look 0.12 better than they are
    assert np.nanmean(frame[outcome_column("ret", False)]) == pytest.approx(-0.02)
    table = screen_table(frame, screen)
    pooled = table.iloc[-1]
    assert pooled["ret peers"] == pytest.approx(0.10)
    assert pooled["precision peers"] == pytest.approx(1.0)
    assert list(table.columns).index("ret peers") == (
        list(table.columns).index("ret mean") + 1
    )
    # a pick without the outcome does not count its peers either
    three = PickScreen(top_k=6, peer_column="log_marketcap_rank", peer_bins=2)
    m3 = screen_metrics(frame, three)
    assert m3["screen_mean_ret"] == pytest.approx(-0.02)
    assert m3["screen_peer_mean_ret"] == pytest.approx(
        (3 * 0.10 + 2 * -0.20) / 5
    )
    # without a peer column nothing is added and nothing changes
    plain = screen_metrics(frame, PickScreen(top_k=2))
    assert "screen_peer_mean_ret" not in plain
    assert plain["screen_mean_ret"] == m["screen_mean_ret"]


def test_peer_settings_are_validated_and_keep_old_hashes():
    with pytest.raises(ConfigError, match="peer_bins is set without"):
        _config(pick_screen={"peer_bins": 10})
    with pytest.raises(ConfigError, match="2 or more"):
        _config(pick_screen={"peer_column": "book_to_market_rank",
                             "peer_bins": 1})
    plain = _config(pick_screen={"top_k": 2})
    peered = _config(pick_screen={"top_k": 2,
                                  "peer_column": "book_to_market_rank"})
    assert plain.pick_screen.to_table() == {"per": "quarter", "top_k": 2}
    assert peered.config_hash != plain.config_hash
    assert peered.pick_screen.to_table()["peer_bins"] == 20
    assert "bands of `book_to_market_rank`" in peered.pick_screen.describe()


def test_peer_screen_in_a_run_and_an_evaluation(universe_root, tmp_path):
    """The peer column is read from the test rows (it need not be a
    model input), must be a rank column, and an eval config may add it
    to a saved bundle."""
    config = _config(
        pick_outcomes=["fwd_3y_cagr"],
        pick_screen={"top_k": 2, "peer_column": "book_to_market_rank",
                     "peer_bins": 2},
    )
    summary = _run(config, universe_root, tmp_path,
                   models_dir=tmp_path / "models")
    pooled = summary["pooled_metrics"]
    assert "screen_peer_mean_fwd_3y_cagr" in pooled
    assert "screen_peer_precision" in pooled
    report = summary["report_path"].read_text()
    assert "fwd_3y_cagr peers" in report
    assert "Read a selection against its peers" in report
    with pytest.raises(ConfigError, match="not a rank column"):
        _run(
            _config(pick_screen={"top_k": 2, "peer_column": "book_to_market"}),
            universe_root, tmp_path,
        )
