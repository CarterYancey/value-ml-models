"""Engine accounting on hand-built prices: deposits, costs inside TWR,
delisting liquidation, and the money-weighted/drawdown metrics."""

import pandas as pd
import pytest

from portfolio.engine import run_simulation
from portfolio.prices import SeriesPriceSource
from portfolio.report import max_drawdown, twr_cagr, xirr
from portfolio.strategy import BuyAndHoldTopK, SellBelowCriteria

D1, D2, D3 = (
    pd.Timestamp("2016-01-04"),
    pd.Timestamp("2016-02-01"),
    pd.Timestamp("2016-03-01"),
)

_NO_REVIEW = pd.DataFrame(columns=["passes_sell", "sell_reason"])


def _series(values: dict) -> pd.Series:
    return pd.Series(
        list(values.values()), index=pd.DatetimeIndex(list(values.keys()))
    )


def _one_asset_candidates(price: float):
    def fn(when, held):
        return (
            pd.DataFrame(
                {"asset": ["A"], "ticker": ["AAA"],
                 "combined_score": [1.0], "price": [price]}
            ),
            _NO_REVIEW,
            {},
        )

    return fn


def test_hand_checked_accounting_whole_shares_with_costs():
    source = SeriesPriceSource({"A": _series({D1: 10.0, D2: 10.0, D3: 20.0})})
    result = run_simulation(
        dates=[D1, D2, D3],
        buy_dates={D1, D2},
        deposit=1000.0,
        price_source=source,
        strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
        candidates_fn=_one_asset_candidates(10.0),
        cost_bps=100.0,  # 1% per side
        delist_after_days=30,
    )
    m = result.monthly.set_index("date")
    # D1: budget 1000 at price 10 + 1% -> ⌊1000/10.10⌋ = 99 shares,
    # gross 990, cost 9.90, spend 999.90, cash 0.10
    assert m.loc[D1, "cash"] == pytest.approx(0.10)
    assert m.loc[D1, "total_value"] == pytest.approx(990.10)
    assert m.loc[D1, "value_after_deposit"] == pytest.approx(1000.0)
    assert m.loc[D1, "costs"] == pytest.approx(9.90)
    # D2: the cost drag shows up as the period's TWR return
    assert m.loc[D2, "twr_return"] == pytest.approx(990.10 / 1000.0 - 1.0)
    # 99 more shares bought from cash 1000.10 -> 198 sh × 10 + cash 0.20
    assert m.loc[D2, "total_value"] == pytest.approx(1980.20)
    # D3: price doubles, no flow
    assert m.loc[D3, "total_value"] == pytest.approx(3960.20)
    assert m.loc[D3, "twr_return"] == pytest.approx(
        3960.20 / 1990.10 - 1.0
    )
    assert result.total_deposits == pytest.approx(2000.0)
    assert result.total_costs == pytest.approx(19.80)
    assert result.final_value == pytest.approx(3960.20)
    assert m.loc[D3, "twr_index"] == pytest.approx(
        (990.10 / 1000.0) * (3960.20 / 1990.10)
    )
    # whole shares, ticker carried into the trade log
    trades = result.trades
    assert (trades["shares"] == 99).all()
    assert set(trades["ticker"]) == {"AAA"}
    # cashflows: two deposits + terminal value
    assert [(d, a) for d, a in result.cashflows] == [
        (D1, -1000.0),
        (D2, -1000.0),
        (D3, pytest.approx(3960.20)),
    ]


def test_fractional_shares_spend_the_full_budget():
    source = SeriesPriceSource({"A": _series({D1: 10.0})})
    result = run_simulation(
        dates=[D1],
        buy_dates={D1},
        deposit=1000.0,
        price_source=source,
        strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
        candidates_fn=_one_asset_candidates(10.0),
        cost_bps=100.0,
        delist_after_days=30,
        fractional_shares=True,
    )
    m = result.monthly.set_index("date")
    assert m.loc[D1, "cash"] == pytest.approx(0.0)
    # shares = 1000 / 10.10; value = shares × 10 = 1000 / 1.01
    assert m.loc[D1, "total_value"] == pytest.approx(1000.0 / 1.01)


def test_delisting_liquidates_at_final_print():
    dates = [
        pd.Timestamp(d)
        for d in ("2016-01-04", "2016-02-01", "2016-03-01",
                  "2016-04-01", "2016-05-02", "2016-06-01")
    ]
    series = _series(
        {
            dates[0]: 10.0,
            dates[1]: 10.0,
            dates[2]: 10.0,
            pd.Timestamp("2016-03-31"): 8.0,  # last print, then silence
        }
    )
    source = SeriesPriceSource({"A": series})
    result = run_simulation(
        dates=dates,
        buy_dates={dates[0]},
        deposit=1000.0,
        price_source=source,
        strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
        candidates_fn=_one_asset_candidates(10.0),
        cost_bps=0.0,
        delist_after_days=30,
    )
    m = result.monthly.set_index("date")
    # 2016-04-01: last print 1 day old -> still held, marked at 8
    assert m.loc[dates[3], "holdings_value"] == pytest.approx(800.0)
    assert m.loc[dates[3], "n_held"] == 1
    # 2016-05-02: 32 days of silence -> liquidated at the final print
    assert m.loc[dates[4], "n_held"] == 0
    assert m.loc[dates[4], "cash"] == pytest.approx(800.0)
    assert m.loc[dates[5], "total_value"] == pytest.approx(800.0)
    delisted = result.trades[result.trades["reason"] == "delisted"]
    assert len(delisted) == 1
    assert delisted.iloc[0]["price"] == pytest.approx(8.0)
    # realized loss vs the 1000 cost basis is reported on the sell
    assert delisted.iloc[0]["cost_basis"] == pytest.approx(1000.0)
    assert delisted.iloc[0]["profit"] == pytest.approx(-200.0)
    assert delisted.iloc[0]["ticker"] == "AAA"


def test_no_candidates_holds_cash():
    source = SeriesPriceSource({})

    def empty_candidates(when, held):
        return (
            pd.DataFrame(columns=["asset", "combined_score", "price"]),
            _NO_REVIEW,
            {},
        )

    result = run_simulation(
        dates=[D1, D2],
        buy_dates={D1, D2},
        deposit=1000.0,
        price_source=source,
        strategy=BuyAndHoldTopK(top_k=5, weighting="score"),
        candidates_fn=empty_candidates,
        cost_bps=10.0,
        delist_after_days=30,
    )
    assert result.final_value == pytest.approx(2000.0)
    assert result.trades.empty
    # cash earns nothing: flat TWR
    assert result.monthly["twr_index"].iloc[-1] == pytest.approx(1.0)


def test_score_weighting_splits_cash_proportionally():
    source = SeriesPriceSource(
        {"A": _series({D1: 10.0}), "B": _series({D1: 5.0})}
    )

    def candidates(when, held):
        return (
            pd.DataFrame(
                {
                    "asset": ["A", "B"],
                    "ticker": ["AAA", "BBB"],
                    "combined_score": [0.6, 0.2],
                    "score_m1": [0.6, 0.2],
                    "price": [10.0, 5.0],
                }
            ),
            _NO_REVIEW,
            {},
        )

    result = run_simulation(
        dates=[D1],
        buy_dates={D1},
        deposit=1000.0,
        price_source=source,
        strategy=BuyAndHoldTopK(top_k=2, weighting="score"),
        candidates_fn=candidates,
        cost_bps=0.0,
        delist_after_days=30,
    )
    buys = result.trades.set_index("asset")
    assert buys.loc["A", "gross"] == pytest.approx(750.0)  # 0.6 / 0.8
    assert buys.loc["B", "gross"] == pytest.approx(250.0)
    assert buys.loc["A", "shares"] == pytest.approx(75.0)
    assert buys.loc["B", "shares"] == pytest.approx(50.0)
    # per-model score columns are carried into the trade log
    assert buys.loc["A", "score_m1"] == pytest.approx(0.6)


def test_sell_below_criteria_sells_and_reinvests_same_month():
    """D1: buy A. D2: A fails the sell criteria -> sold; the proceeds
    plus the deposit buy B the same month."""
    source = SeriesPriceSource(
        {"A": _series({D1: 10.0, D2: 12.0}), "B": _series({D2: 5.0})}
    )

    def feed(when, held):
        if when == D1:
            frame = pd.DataFrame(
                {"asset": ["A"], "ticker": ["AAA"],
                 "combined_score": [1.0], "price": [10.0]}
            )
            review = _NO_REVIEW
        else:
            frame = pd.DataFrame(
                {"asset": ["B"], "ticker": ["BBB"],
                 "combined_score": [1.0], "price": [5.0]}
            )
            review = pd.DataFrame(
                {"passes_sell": [False],
                 "sell_reason": ["score_floor:m1"]},
                index=pd.Index(held, name="asset"),
            )
        return frame, review, {}

    result = run_simulation(
        dates=[D1, D2],
        buy_dates={D1, D2},
        deposit=1000.0,
        price_source=source,
        strategy=SellBelowCriteria(top_k=1, weighting="equal"),
        candidates_fn=feed,
        cost_bps=0.0,
        delist_after_days=30,
    )
    trades = result.trades
    sell = trades[trades["side"] == "sell"].iloc[0]
    assert sell["asset"] == "A"
    assert sell["reason"] == "criteria:score_floor:m1"
    assert sell["shares"] == 100  # the whole position
    assert sell["profit"] == pytest.approx(200.0)  # bought 1000, sold 1200
    # D2 buy of B spends deposit + proceeds: 2200 -> 440 shares at 5
    buy_b = trades[(trades["side"] == "buy") & (trades["asset"] == "B")]
    assert buy_b.iloc[0]["gross"] == pytest.approx(2200.0)
    assert buy_b.iloc[0]["shares"] == 440
    m = result.monthly.set_index("date")
    assert m.loc[D2, "n_held"] == 1
    assert result.rebalance_log.set_index("date").loc[D2, "n_sold"] == 1


def test_top_k_dropout_is_not_a_sell():
    """The defining distinction: A drops out of the candidate list (not
    top-K any more) but still passes the sell criteria -> held, no
    sell; the deposit buys the new top pick."""
    source = SeriesPriceSource(
        {"A": _series({D1: 10.0, D2: 10.0}), "B": _series({D2: 5.0})}
    )

    def feed(when, held):
        if when == D1:
            frame = pd.DataFrame(
                {"asset": ["A"], "ticker": ["AAA"],
                 "combined_score": [1.0], "price": [10.0]}
            )
            review = _NO_REVIEW
        else:
            frame = pd.DataFrame(  # A is no longer a candidate
                {"asset": ["B"], "ticker": ["BBB"],
                 "combined_score": [1.0], "price": [5.0]}
            )
            review = pd.DataFrame(
                {"passes_sell": [True], "sell_reason": [""]},
                index=pd.Index(held, name="asset"),
            )
        return frame, review, {}

    result = run_simulation(
        dates=[D1, D2],
        buy_dates={D1, D2},
        deposit=1000.0,
        price_source=source,
        strategy=SellBelowCriteria(top_k=1, weighting="equal"),
        candidates_fn=feed,
        cost_bps=0.0,
        delist_after_days=30,
    )
    assert (result.trades["side"] == "buy").all()  # no sells at all
    m = result.monthly.set_index("date")
    assert m.loc[D2, "n_held"] == 2  # A held, B added
    assert m.loc[D2, "total_value"] == pytest.approx(2000.0)


def test_xirr_matches_closed_form():
    t0, t1 = pd.Timestamp("2016-01-01"), pd.Timestamp("2017-01-01")
    rate = xirr([(t0, -1000.0), (t1, 1100.0)])
    expected = 1.1 ** (365.25 / (t1 - t0).days) - 1.0
    assert rate == pytest.approx(expected, abs=1e-6)


def test_xirr_undefined_without_sign_change():
    assert xirr([(D1, -1000.0)]) is None


def test_max_drawdown():
    index = pd.Series([1.0, 1.2, 0.9, 1.5])
    assert max_drawdown(index) == pytest.approx(0.9 / 1.2 - 1.0)


def test_twr_cagr_flat_is_zero():
    monthly = pd.DataFrame(
        {
            "date": [D1, D2, D3],
            "twr_return": [None, 0.0, 0.0],
            "twr_index": [1.0, 1.0, 1.0],
        }
    )
    assert twr_cagr(monthly) == pytest.approx(0.0)
