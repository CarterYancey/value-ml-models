"""Signal guardrails and the end-to-end backtest on the miniature
dataset + price panel: deployment bundles refused, dataset-version pins
enforced, refits cached and validated, both legs under identical
deposits, everything logged."""

import json

import numpy as np

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
    review_held,
    sell_filter_specs,
    sell_score_floors,
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
    floored = apply_min_score(frame, {"score_a": 0.5, "score_b": 0.5})
    assert list(floored.index) == [0, 2]
    # per-model floors: only the floored column is screened
    only_b = apply_min_score(frame, {"score_b": 0.5})
    assert list(only_b.index) == [0, 2]
    assert apply_min_score(frame, {}).equals(frame)


def test_per_model_floors_resolve_and_validate(data_root, wf_bundle_dir):
    from portfolio.signals import score_floors

    dataset = Dataset(data_root / DATASET)
    model_set = ModelSet([wf_bundle_dir])
    config = _bt_config(
        wf_bundle_dir,
        signal={"min_score": 0.5,
                "min_scores": {"wf_tree_3y_beat_spy": 0.9}},
    )
    model_set.validate_against(config, dataset)
    assert score_floors(config, model_set.names) == {
        "score_wf_tree_3y_beat_spy": 0.9
    }
    bad = _bt_config(
        wf_bundle_dir, signal={"min_scores": {"no_such_bundle": 0.9}}
    )
    with pytest.raises(ConfigError, match="no_such_bundle"):
        model_set.validate_against(bad, dataset)


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


def test_review_held_verdicts():
    scored = pd.DataFrame(
        {
            "permaticker": [1, 2, 3],
            "score_m": [0.9, 0.3, 0.9],
            "trend": [1.0, 1.0, -1.0],
        }
    )
    review = review_held(
        scored,
        held_assets=[1, 2, 3, 4],  # 4 is not in the cross-section
        floors={"score_m": 0.5},
        filters=(FilterSpec("trend", ">", 0.0),),
    )
    assert review.loc[1, "passes_sell"]
    assert not review.loc[2, "passes_sell"]
    assert review.loc[2, "sell_reason"] == "score_floor:m"
    assert not review.loc[3, "passes_sell"]
    assert review.loc[3, "sell_reason"] == "filter:trend"
    assert not review.loc[4, "passes_sell"]
    assert review.loc[4, "sell_reason"] == "not_in_cross_section"


def test_sell_criteria_inherit_and_override(wf_bundle_dir):
    name = "wf_tree_3y_beat_spy"
    inherit = _bt_config(wf_bundle_dir, signal={"min_score": 0.7})
    assert sell_score_floors(inherit, [name]) == {f"score_{name}": 0.7}
    assert sell_filter_specs(inherit) == inherit.filters

    # hysteresis: buy > 0.7, sell < 0.5; sell filters cleared explicitly
    band = _bt_config(
        wf_bundle_dir,
        signal={"min_score": 0.7},
        sell={"min_score": 0.5, "filters": []},
    )
    assert sell_score_floors(band, [name]) == {f"score_{name}": 0.5}
    assert sell_filter_specs(band) == ()
    assert band.config_hash != inherit.config_hash

    with pytest.raises(ConfigError, match="unknown \\[sell\\] keys"):
        BacktestConfig.from_dict(
            {
                "name": "x",
                "dataset_version": DATASET,
                "prices_version": PRICES,
                "bundles": ["b"],
                "investability": "none",
                "execution": {"cost_bps": 1.0},
                "sell": {"max_score": 1.0},
            }
        )


def test_sell_backtest_end_to_end(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    # a sell floor above every attainable tree score forces criteria
    # sells of everything bought the month before
    config = _bt_config(
        wf_bundle_dir,
        name="bt_sell",
        portfolio={"strategy": "sell_below_criteria", "top_k": 2,
                   "weighting": "equal", "monthly_cash": 1000.0},
        sell={"min_score": 1.5},
        window={"end": __import__("datetime").date(2017, 12, 31)},
    )
    summary = run_backtest(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        refit_cache_dir=tmp_path / "refits",
    )
    trades = summary["strategy_result"].trades
    criteria = trades[trades["reason"].astype(str).str.startswith("criteria:")]
    assert not criteria.empty
    assert (criteria["side"] == "sell").all()
    report = (
        tmp_path / "reports" / "backtest"
        / f"bt_sell_{config.config_hash}.md"
    ).read_text()
    assert "sell discipline" in report
    assert "criteria sells:" in report
    assert "sell floors: " in report


def test_sell_section_needs_a_selling_strategy(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    config = _bt_config(
        wf_bundle_dir, name="bt_sell_mismatch", sell={"min_score": 0.5}
    )
    with pytest.raises(ConfigError, match="never sells"):
        run_backtest(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
            refit_cache_dir=tmp_path / "refits",
        )


def test_refit_cache_roundtrip(data_root, wf_bundle_dir, tmp_path):
    from portfolio.crosssection import CrossSectionBuilder

    dataset = Dataset(data_root / DATASET)
    cache = tmp_path / "refits"
    years = [2016, 2017, 2018, 2019]

    first = ModelSet([wf_bundle_dir])
    first.prepare(years, dataset, "refit", 45, refit_cache_dir=cache)
    stats1 = first.provenance[0]["refit_stats"]
    assert {y: s["source"] for y, s in stats1.items()} == {
        2018: "fit", 2019: "fit"
    }

    second = ModelSet([wf_bundle_dir])
    second.prepare(years, dataset, "refit", 45, refit_cache_dir=cache)
    stats2 = second.provenance[0]["refit_stats"]
    assert {y: s["source"] for y, s in stats2.items()} == {
        2018: "cache", 2019: "cache"
    }
    for year in (2018, 2019):
        assert stats2[year]["n_train_rows"] == stats1[year]["n_train_rows"]
        assert stats2[year]["effective_train_size"] == pytest.approx(
            stats1[year]["effective_train_size"]
        )
    # a cached model scores identically to the one it replaced
    xs = CrossSectionBuilder(dataset, 200).at(pd.Timestamp("2018-02-01"))
    col = first.score_columns[0]
    assert second.score(xs, 2018)[col].tolist() == pytest.approx(
        first.score(xs, 2018)[col].tolist()
    )

    # a different label lag is a different fit, not a cache hit
    other_lag = ModelSet([wf_bundle_dir])
    other_lag.prepare(
        [2016, 2017, 2018], dataset, "refit", 30, refit_cache_dir=cache
    )
    assert other_lag.provenance[0]["refit_stats"][2018]["source"] == "fit"

    # a sidecar that doesn't vouch for the pickle is not trusted
    meta_path = next(cache.rglob("refit_y2019_lag45.json"))
    meta = json.loads(meta_path.read_text())
    meta["config_hash"] = "deadbeef"
    meta_path.write_text(json.dumps(meta))
    tampered = ModelSet([wf_bundle_dir])
    tampered.prepare(years, dataset, "refit", 45, refit_cache_dir=cache)
    stats4 = tampered.provenance[0]["refit_stats"]
    assert stats4[2018]["source"] == "cache"
    assert stats4[2019]["source"] == "fit"  # refit and re-cached
    restored = ModelSet([wf_bundle_dir])
    restored.prepare(years, dataset, "refit", 45, refit_cache_dir=cache)
    assert restored.provenance[0]["refit_stats"][2019]["source"] == "cache"


def test_backtest_end_to_end_with_refits(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    results = tmp_path / "results.csv"
    reports = tmp_path / "reports"
    config = _bt_config(wf_bundle_dir)
    summary = run_backtest(
        config,
        data_root=data_root,
        results_path=results,
        reports_dir=reports,
        refit_cache_dir=tmp_path / "refits",
    )
    assert summary["status"] == "completed"
    # buys start at the first fold year and keep rolling past the last
    # fold (2017) under model_update = "refit", to the panel's end
    assert summary["buy_years"] == [2016, 2017, 2018, 2019, 2020, 2021]
    strategy = summary["strategy_result"]
    benchmark = summary["benchmark_result"]

    buys = strategy.trades[strategy.trades["side"] == "buy"]
    assert not buys.empty
    assert set(buys["date"].dt.year) <= set(range(2016, 2022))
    assert buys["date"].dt.year.max() >= 2018  # refit years traded too
    # whole shares, tickers, and per-model scores in the trade log
    assert (buys["shares"] % 1 == 0).all()
    assert buys["ticker"].notna().all()
    assert "score_wf_tree_3y_beat_spy" in buys.columns
    # 66 monthly deposits (2016-01 .. 2021-06) into both legs
    assert strategy.total_deposits == pytest.approx(66_000.0)
    assert benchmark.total_deposits == pytest.approx(66_000.0)
    assert list(strategy.monthly["date"]) == list(benchmark.monthly["date"])
    assert strategy.monthly["date"].iloc[-1] == pd.Timestamp("2021-06-30")
    assert {"value_after_deposit", "costs"} <= set(strategy.monthly.columns)
    assert strategy.final_value > 0
    assert benchmark.final_value > 0
    assert strategy.total_costs > 0

    stem = f"bt_e2e_{config.config_hash}"
    report = (reports / "backtest" / f"{stem}.md").read_text()
    assert "split_folds.parquet" in report
    assert "explicitly opted out" in report  # investability = "none"
    assert "configurations tried" in report
    assert "Simulated year-end refits" in report
    assert "selection-toxic" in report
    for suffix in ("_equity.csv", "_trades.csv", "_equity.png",
                   "_rebalances.csv"):
        assert (reports / "backtest" / f"{stem}{suffix}").exists()

    store = ResultsStore(results).load()
    row = store[store["scheme"] == BACKTEST_SCHEME].iloc[-1]
    assert row["status"] == "completed"
    assert row["experiment"] == "bt_e2e"
    assert row["fold"] == "2016-2021"
    # the buys are set beside the stocks they were chosen from, in the
    # report and in the ledger (the fixture has no size column, so the
    # same-size peer columns are absent)
    assert "### Against the stocks they were chosen from" in report
    assert "vs_candidates" in report and "vs_peers" not in report
    metrics = json.loads(row["metrics_json"])
    assert "ref_vs_candidates_1y" in metrics
    assert "ref_candidates_excess_1y" in metrics


def test_frozen_policy_and_window_start(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    from datetime import date

    config = _bt_config(
        wf_bundle_dir,
        name="bt_frozen",
        signal={"combine": "product", "model_update": "frozen"},
        window={"start": date(2017, 1, 1), "end": date(2018, 12, 31)},
    )
    summary = run_backtest(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        refit_cache_dir=tmp_path / "refits",
    )
    # start is honored (2016 skipped), 2018 served by the frozen model
    assert summary["buy_years"] == [2017, 2018]
    assert summary["strategy_result"].total_deposits == pytest.approx(
        24_000.0
    )
    report = (
        tmp_path / "reports" / "backtest"
        / f"bt_frozen_{config.config_hash}.md"
    ).read_text()
    assert "frozen" in report
    assert "Simulated year-end refits" not in report


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


def test_window_before_first_fold_year_is_refused(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    from datetime import date

    config = _bt_config(
        wf_bundle_dir,
        name="bt_too_early",
        window={"end": date(2015, 12, 31)},
    )
    with pytest.raises(ConfigError, match="serveable"):
        run_backtest(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )


def test_rank_sell_criterion(wf_bundle_dir):
    from portfolio.signals import candidate_rank_pct

    candidates = pd.DataFrame(
        {"asset": [7, 1, 2, 3], "combined_score": [0.9, 0.8, 0.5, 0.1]}
    )
    pct = candidate_rank_pct(candidates)
    assert pct.loc[7] == 0.25 and pct.loc[3] == 1.0
    assert candidate_rank_pct(candidates.iloc[:0]).empty

    scored = pd.DataFrame({"permaticker": [1, 2, 3, 4], "score_m": 0.9})
    review = review_held(
        scored, held_assets=[1, 2, 3, 4], floors={}, filters=(),
        rank_pct=pct, max_rank_pct=0.5,
    )
    assert review.loc[1, "passes_sell"]  # second of four: top half
    assert not review.loc[2, "passes_sell"]
    assert review.loc[2, "sell_reason"] == "rank:below_top_share"
    # scored but screened out of the month's candidates
    assert review.loc[4, "sell_reason"] == "rank:not_a_candidate"
    # without the criterion nothing changes
    plain = review_held(scored, held_assets=[2, 4], floors={}, filters=())
    assert plain["passes_sell"].all()

    ranked = _bt_config(
        wf_bundle_dir, sell={"max_rank_pct": 0.3},
        portfolio={"strategy": "sell_below_criteria"},
    )
    band = _bt_config(
        wf_bundle_dir, sell={}, portfolio={"strategy": "sell_below_criteria"},
    )
    assert ranked.sell_max_rank_pct == 0.3 and band.sell_max_rank_pct is None
    assert ranked.config_hash != band.config_hash
    assert "max_rank_pct" not in band.canonical_json()
    for bad in (0, 1.5, True, "half"):
        with pytest.raises(ConfigError, match="max_rank_pct"):
            _bt_config(wf_bundle_dir, sell={"max_rank_pct": bad})


def test_rank_sell_backtest_end_to_end(
    data_root, prices_dir, wf_bundle_dir, tmp_path
):
    # six stocks, two bought a month: a holding outside the top third
    # of the month's candidates is sold
    config = _bt_config(
        wf_bundle_dir,
        name="bt_rank_sell",
        signal={"combine": "mean_rank"},
        portfolio={"strategy": "sell_below_criteria", "top_k": 2,
                   "weighting": "equal", "monthly_cash": 1000.0},
        sell={"max_rank_pct": 0.34},
        window={"end": __import__("datetime").date(2017, 12, 31)},
    )
    summary = run_backtest(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        refit_cache_dir=tmp_path / "refits",
    )
    trades = summary["strategy_result"].trades
    reasons = set(trades.loc[trades["side"] == "sell", "reason"].astype(str))
    assert any(r.startswith("criteria:rank:") for r in reasons)
    report = (
        tmp_path / "reports" / "backtest"
        / f"bt_rank_sell_{config.config_hash}.md"
    ).read_text()
    assert "sell rank: a held position is sold once it is no longer among the top 34%" in report

def test_buy_outcomes_read_each_buy_against_the_benchmark():
    from portfolio.report import buy_outcome_table, buy_outcomes

    days = pd.bdate_range("2010-01-04", "2014-12-31")
    n = np.arange(len(days), dtype=float)
    bench = pd.Series(100.0 * 1.10 ** (n / 261.0), index=days)
    grower = pd.Series(10.0 * 1.20 ** (n / 261.0), index=days)
    # stops printing after six months, 30% up: an acquisition
    acquired = pd.Series(
        np.linspace(10.0, 13.0, 130), index=days[:130]
    )

    class Panel:
        benchmark = bench

        def series(self, asset):
            return {1: grower, 2: acquired}.get(asset)

    trades = pd.DataFrame(
        {
            "asset": [1, 2, 1, 3],
            "date": [days[0], days[0], days[-100], days[0]],
            "side": ["buy", "buy", "buy", "sell"],
            "price": [10.0, 10.0, float(grower.iloc[-100]), 1.0],
            "gross": [100.0, 100.0, 100.0, 5.0],
        }
    )
    out = buy_outcomes(trades, Panel(), days[-1])
    assert len(out) == 3  # the sell is not a buy
    first, second, late = out.iloc[0], out.iloc[1], out.iloc[2]
    assert first["excess_1y"] == pytest.approx(0.10, abs=0.01)
    assert first["excess_3y"] == pytest.approx(0.10, abs=0.01)
    assert first["early_exit_3y"] == 0.0
    # +30% in six months, then the benchmark's 10% a year: about +37%
    # over the year against the benchmark's 10%, not +30% held flat
    assert second["early_exit_1y"] == 1.0
    assert second["return_1y"] == pytest.approx(1.30 * 1.10 ** 0.5 - 1, abs=0.02)
    assert second["excess_3y"] > 0
    # a buy whose horizon ends after the valuation date has no outcome
    assert np.isnan(late["excess_1y"]) and np.isnan(late["excess_3y"])

    table = buy_outcome_table(out)
    assert table["year"].tolist() == [2010, 2014, "all buys"]
    pooled = table.iloc[-1]
    assert pooled["buys"] == 3 and pooled["n_3y"] == 2
    assert pooled["beat_3y"] == 1.0 and pooled["lost_3y"] == 0.0
    assert pooled["early_exit_3y"] == 0.5
    assert buy_outcome_table(out.iloc[:0]).empty


def _reference_panel():
    """A benchmark growing 10% a year, six stocks with known growth
    rates, and one that is acquired after six months."""
    days = pd.bdate_range("2010-01-04", "2014-12-31")
    n = np.arange(len(days), dtype=float)
    bench = pd.Series(100.0 * 1.10 ** (n / 261.0), index=days)
    rates = {1: 0.20, 2: 0.00, 3: 0.30, 4: 0.10, 5: -0.10, 6: 0.15}
    series = {
        a: pd.Series(10.0 * (1.0 + r) ** (n / 261.0), index=days)
        for a, r in rates.items()
    }
    series[7] = pd.Series(np.linspace(10.0, 13.0, 130), index=days[:130])

    class Panel:
        benchmark = bench

        def series(self, asset):
            return series.get(asset)

    return Panel(), days, rates


def test_position_outcomes_match_the_delisting_convention():
    """The vectorized reading equals the hand calculation: a stock that
    stops printing exits at its final print and the proceeds ride the
    benchmark; an unknown stock, a non-positive price and a horizon
    past the valuation date have no outcome."""
    from portfolio.report import position_outcomes

    panel, days, _ = _reference_panel()
    frame = pd.DataFrame(
        {
            "asset": [1, 7, 1, 99, 2],
            "date": [days[0], days[0], days[-100], days[0], days[0]],
            "price": [10.0, 10.0, 12.0, 10.0, 0.0],
        },
        index=[10, 11, 12, 13, 14],
    )
    out = position_outcomes(frame, panel, days[-1])
    assert list(out.index) == [10, 11, 12, 13, 14]
    assert out.loc[10, "excess_3y"] == pytest.approx(0.10, abs=0.01)
    assert out.loc[10, "early_exit_3y"] == 0.0
    assert out.loc[11, "early_exit_1y"] == 1.0
    assert out.loc[11, "return_1y"] == pytest.approx(
        1.30 * 1.10 ** 0.5 - 1, abs=0.02
    )
    for idx in (12, 13, 14):
        assert out.loc[idx].isna().all()


def test_reference_table_sets_the_buys_beside_their_candidates():
    """Buys are read against every candidate and against the candidates
    of their own rebalance in their own size band: a buy that is the
    best of the large stocks leads its peers by less than it leads the
    whole list when the small stocks did worse."""
    from portfolio.report import (
        buy_outcomes,
        candidate_outcomes,
        reference_table,
    )

    panel, days, rates = _reference_panel()
    # stocks 1-3 are large (size 0.96-0.98), 4-6 small (0.11-0.13)
    sizes = {1: 0.96, 2: 0.97, 3: 0.98, 4: 0.11, 5: 0.12, 6: 0.13}
    candidates = pd.DataFrame(
        {
            "asset": list(sizes),
            "price": 10.0,
            "date": days[0],
            "size": [sizes[a] for a in sizes],
        }
    )
    cand = candidate_outcomes(candidates, panel, days[-1])
    assert set(cand["size_bin"]) == {19, 2}
    trades = pd.DataFrame(
        {
            "asset": [3, 4],
            "date": [days[0], days[0]],
            "side": ["buy", "buy"],
            "price": [10.0, 10.0],
            "gross": [100.0, 100.0],
        }
    )
    buys = buy_outcomes(trades, panel, days[-1])
    table = reference_table(buys, cand, 3)
    assert table["year"].tolist() == [2010, "all buys"]
    row = table.iloc[-1]
    bench = 0.10
    all_mean = np.mean([rates[a] for a in sizes]) - bench
    assert row["buys"] == 2
    assert row["buys_excess"] == pytest.approx((0.30 + 0.10) / 2 - bench, abs=0.01)
    assert row["candidates_excess"] == pytest.approx(all_mean, abs=0.01)
    assert row["vs_candidates"] == pytest.approx(
        (0.30 + 0.10) / 2 - np.mean(list(rates.values())), abs=0.01
    )
    # peers: stock 3 against the large three, stock 4 against the small
    large = np.mean([0.20, 0.00, 0.30])
    small = np.mean([0.10, -0.10, 0.15])
    assert row["peers_excess"] == pytest.approx(
        (large + small) / 2 - bench, abs=0.01
    )
    assert row["vs_peers"] == pytest.approx(
        ((0.30 - large) + (0.10 - small)) / 2, abs=0.01
    )
    assert row["buys_lost"] == 0.0
    assert row["candidates_lost"] == pytest.approx(1 / 6)
    assert row["peers_lost"] == pytest.approx((0.0 + 1 / 3) / 2)
    # without a size column the peer columns are absent, the rest stays
    plain = candidate_outcomes(
        candidates.drop(columns=["size"]), panel, days[-1]
    )
    slim = reference_table(buys, plain, 3)
    assert "vs_peers" not in slim.columns
    assert slim.iloc[-1]["vs_candidates"] == pytest.approx(
        row["vs_candidates"]
    )
    assert reference_table(buys.iloc[:0], cand, 3).empty
