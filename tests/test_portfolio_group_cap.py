"""The group cap at selection: at most N of one rebalance's buys per
group, walked in score order (portfolio.strategy.capped_top_k), and the
report's account of what was bought."""

import pandas as pd
import pytest

from harness.errors import ConfigError
from portfolio.report import group_tables
from portfolio.strategy import BuyAndHoldTopK, build_strategy, capped_top_k


def _candidates(groups, scores=None) -> pd.DataFrame:
    n = len(groups)
    scores = scores or [1.0 - 0.01 * i for i in range(n)]
    return pd.DataFrame(
        {
            "asset": list(range(100, 100 + n)),
            "combined_score": scores,
            "price": [10.0] * n,
            "group": groups,
        }
    )


def test_no_cap_is_the_plain_top_k():
    frame = _candidates(["a", "a", "a", "b"])
    assert list(capped_top_k(frame, 3, None)["asset"]) == [100, 101, 102]


def test_cap_skips_a_full_group_and_keeps_score_order():
    frame = _candidates(["a", "a", "a", "b", "a", "c"])
    picks = capped_top_k(frame, 4, 2)
    assert list(picks["asset"]) == [100, 101, 103, 105]
    assert picks["group"].value_counts().max() == 2


def test_cap_returns_fewer_picks_when_the_groups_run_out():
    frame = _candidates(["a", "a", "a", "b"])
    assert list(capped_top_k(frame, 4, 1)["asset"]) == [100, 103]


def test_null_groups_are_one_group():
    frame = _candidates([None, float("nan"), "a", None])
    assert list(capped_top_k(frame, 4, 1)["asset"]) == [100, 102]


def test_cap_without_a_group_column_is_refused():
    frame = _candidates(["a", "b"]).drop(columns=["group"])
    with pytest.raises(ConfigError, match="group"):
        capped_top_k(frame, 2, 1)
    # and is not needed when there is no cap
    assert len(capped_top_k(frame, 2, None)) == 2


def test_strategy_spreads_cash_over_the_capped_picks():
    strategy = build_strategy("buy_and_hold", 3, "equal", max_per_group=1)
    orders = strategy.orders(
        None, _candidates(["a", "a", "b", "c"]), 900.0, {}
    )
    assert [o.asset for o in orders] == [100, 102, 103]
    assert [o.cash_amount for o in orders] == pytest.approx([300.0] * 3)


def test_strategy_default_is_uncapped():
    strategy = BuyAndHoldTopK(top_k=2, weighting="equal")
    orders = strategy.orders(None, _candidates(["a", "a", "b"]), 100.0, {})
    assert [o.asset for o in orders] == [100, 101]


def test_group_tables_count_buys_by_group_and_year():
    trades = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2005-01-03", "2005-02-01", "2005-02-01", "2006-01-03",
                 "2006-01-03"]
            ),
            "asset": [1, 1, 2, 3, 1],
            "side": ["buy", "buy", "buy", "buy", "sell"],
            "group": ["a", "a", "b", None, "a"],
        }
    )
    overall, by_year = group_tables(trades)
    assert dict(zip(overall["group"], overall["buys"])) == {
        "a": 2, "b": 1, "unknown": 1,
    }
    assert overall["share"].sum() == pytest.approx(1.0)
    first = by_year.iloc[0]
    assert (first["year"], first["buys"], first["stocks"]) == (2005, 3, 2)
    assert first["largest_group"] == "a"
    assert first["largest_share"] == pytest.approx(2 / 3)
    assert by_year.iloc[1]["largest_group"] == "unknown"


def test_group_tables_need_a_group_column():
    trades = pd.DataFrame({"date": [], "asset": [], "side": []})
    assert group_tables(trades) is None
