"""Decision 84: deposit schedules, the schedule table and the benchmark
expense ratio."""
import pandas as pd
import pytest

from portfolio.config import BacktestConfig, ConfigError
from portfolio.engine import deposit_schedule, run_simulation
from portfolio.prices import SeriesPriceSource
from portfolio.report import (
    DEPOSIT_SCHEDULES, deposit_schedule_table, schedule_final_value,
)
from portfolio.strategy import BuyAndHoldTopK

D = [pd.Timestamp(f"2016-{m:02d}-01") for m in range(1, 13)]
_NO_REVIEW = pd.DataFrame(columns=["passes_sell", "sell_reason"])


def _series(values):
    return pd.Series(list(values), index=pd.DatetimeIndex(D[: len(values)]))


def _one_asset(prices):
    series = _series(prices)

    def fn(when, held):
        return (
            pd.DataFrame({"asset": ["A"], "ticker": ["AAA"],
                          "combined_score": [1.0],
                          "price": [float(series.loc[when])]}),
            _NO_REVIEW, {},
        )

    return SeriesPriceSource({"A": series}), fn


def test_deposit_schedule_flat_is_a_float_and_growth_compounds():
    assert deposit_schedule(1000.0, 0.0, D[0]) == 1000.0
    fn = deposit_schedule(1000.0, 0.10, D[0])
    assert callable(fn)
    assert fn(D[0]) == pytest.approx(1000.0)
    one_year = D[0] + pd.Timedelta(days=365.25)
    assert fn(one_year) == pytest.approx(1100.0, rel=1e-6)


def test_simulation_takes_a_growing_deposit():
    source, cands = _one_asset([10.0] * 12)
    fn = deposit_schedule(1000.0, 0.12, D[0])
    result = run_simulation(
        dates=D, buy_dates=set(D), deposit=fn, price_source=source,
        strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
        candidates_fn=cands, cost_bps=0.0, delist_after_days=30,
        fractional_shares=True,
    )
    expected = sum(fn(d) for d in D)
    assert result.total_deposits == pytest.approx(expected)
    assert result.monthly["deposit"].iloc[-1] > result.monthly["deposit"].iloc[0]


def test_schedule_table_flat_row_reproduces_the_final_value():
    prices = [10, 11, 12, 11, 13, 14, 13, 15, 16, 15, 17, 18]
    source, cands = _one_asset([float(p) for p in prices])
    result = run_simulation(
        dates=D, buy_dates=set(D), deposit=1000.0, price_source=source,
        strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
        candidates_fn=cands, cost_bps=35.0, delist_after_days=30,
        fractional_shares=True,
    )
    table = deposit_schedule_table(result, result)
    assert list(table["key"]) == [k for k, _ in DEPOSIT_SCHEDULES]
    flat = table.set_index("key").loc["flat"]
    # fractional shares and proportional costs: the path scales with the
    # account, so the flat schedule's reconstruction is the headline
    # ... except for the last date's buy cost, which the index has not
    # absorbed yet: 1000 at 35 bps
    assert flat["strategy"] == pytest.approx(result.final_value, abs=3.6)
    assert flat["strategy"] > result.final_value
    assert flat["ratio"] == pytest.approx(1.0)
    # all the money on the first date grows by the whole path
    lump = schedule_final_value(result, "lump_sum")
    m = result.monthly
    assert lump == pytest.approx(
        result.total_deposits * m["twr_index"].iloc[-1] / m["twr_index"].iloc[0]
    )
    assert schedule_final_value(result, "growing_6pct") != pytest.approx(
        flat["strategy"]
    )


def test_config_fields_parse_and_hash_only_when_set(tmp_path):
    base = {
        "name": "x", "dataset_version": "dataset_v1.4.1",
        "prices_version": "prices_v1.0", "bundles": ["b"],
        "signal": {"combine": "mean_rank"},
        "investability": "none",
        "portfolio": {"strategy": "buy_and_hold", "top_k": 10, "weighting": "equal"},
        "execution": {"cost_bps": 35.0},
        "window": {},
    }
    plain = BacktestConfig.from_dict(dict(base), "t")
    assert plain.deposit_growth_per_year == 0.0
    assert plain.benchmark_expense_bps_per_year == 0.0
    explicit = dict(base, window={"deposit_growth_per_year": 0.0},
                    execution={"cost_bps": 35.0,
                               "benchmark_expense_bps_per_year": 0.0})
    assert BacktestConfig.from_dict(explicit, "t").config_hash == plain.config_hash
    grown = dict(base, window={"deposit_growth_per_year": 0.03})
    assert BacktestConfig.from_dict(grown, "t").config_hash != plain.config_hash
    fee = dict(base, execution={"cost_bps": 35.0,
                                "benchmark_expense_bps_per_year": 9.0})
    assert BacktestConfig.from_dict(fee, "t").config_hash != plain.config_hash
    with pytest.raises(ConfigError):
        BacktestConfig.from_dict(
            dict(base, execution={"cost_bps": 35.0,
                                  "benchmark_expense_bps_per_year": -1.0}), "t")
    with pytest.raises(ConfigError):
        BacktestConfig.from_dict(
            dict(base, window={"deposit_growth_per_year": -1.0}), "t")


def test_expensed_benchmark_drags_by_the_yearly_rate():
    from portfolio.prices import expensed_benchmark_source

    class Panel:
        benchmark_name = "SPY"
        benchmark = pd.Series(
            [100.0, 100.0],
            index=pd.DatetimeIndex([D[0], D[0] + pd.Timedelta(days=365.25)]),
        )

    source = expensed_benchmark_source(Panel(), 100.0)  # 1% a year
    later = D[0] + pd.Timedelta(days=366)
    price, _ = source.asof("SPY", later, 1)
    assert price == pytest.approx(99.0, rel=1e-4)
    bare = expensed_benchmark_source(Panel(), 0.0)
    assert bare.asof("SPY", D[0], 0)[0] == pytest.approx(100.0)
