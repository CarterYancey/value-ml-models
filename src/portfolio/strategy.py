"""Portfolio strategies: candidates + state → orders.

The engine owns time, cash flows, prices, and execution; a strategy only
decides what to do with the investable cash at a rebalance date, given
the scored, filtered, priced candidate list. That split is what makes the
harness reusable: a new portfolio-management idea (rebalancing, sell
rules, position caps) is a new `Strategy`, not a new engine.

Strategies see candidates as a DataFrame sorted by `combined_score`
descending with at least: `asset` (permaticker or benchmark symbol),
`combined_score`, `price`. They never see labels, and they never see the
future — the engine hands them one date at a time.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from harness.errors import ConfigError


@dataclass(frozen=True)
class Order:
    """One instruction to the engine. Buys are cash-sized (the engine
    converts to shares at the execution price, net of costs); sells are
    share-sized. `reason` lands verbatim in the trade log."""

    asset: object
    side: str  # "buy" | "sell"
    cash_amount: float = 0.0
    shares: float = 0.0
    reason: str = "rebalance"


class BuyAndHoldTopK:
    """Deposit-driven accumulation: at every rebalance date, invest all
    available cash across the top-K candidates, weighted by combined
    score (or equally); never sell. Delisting proceeds land back in cash
    and are reinvested at the next date. Months with no qualifying
    candidates hold cash — that drag is real strategy behavior and is
    reported, not hidden."""

    def __init__(self, top_k: int, weighting: str):
        self.top_k = int(top_k)
        self.weighting = weighting

    def orders(
        self, date, candidates: pd.DataFrame, cash: float, positions: dict
    ) -> list[Order]:
        if cash <= 0 or candidates.empty:
            return []
        picks = candidates.head(self.top_k)
        if self.weighting == "score":
            raw = picks["combined_score"].to_numpy(dtype=float)
            if (raw < 0).any():
                raise ConfigError(
                    "weighting = 'score' needs non-negative combined "
                    "scores; use weighting = 'equal' for this combine mode"
                )
            if raw.sum() <= 0:
                # zero conviction across the board: hold cash this month
                return []
            weights = raw / raw.sum()
        else:
            weights = [1.0 / len(picks)] * len(picks)
        return [
            Order(asset=asset, side="buy", cash_amount=cash * w)
            for asset, w in zip(picks["asset"], weights)
            if w > 0
        ]


class SellBelowCriteria(BuyAndHoldTopK):
    """Buy-and-hold with a sell discipline: at every rebalance, any held
    position that fails the *sell criteria* is sold entirely (proceeds
    join that month's investable cash); buying is exactly
    `BuyAndHoldTopK`.

    The distinction that defines this strategy: falling out of the
    top-K is never a sell. A held stock that still clears the criteria
    simply stops receiving new shares. The engine hands `sell_orders` a
    review of the held book evaluated on the full scored cross-section
    (portfolio.signals.review_held), so the verdict is independent of
    what the buy screen and ranking selected this month. The sell
    criteria default to the buy criteria; a separate `[sell]` section
    (looser floors, different filters) makes the band explicit —
    including a stricter-than-buy band, which can sell and immediately
    rebuy: state your criteria with intent.
    """

    def sell_orders(
        self, date, held_review: pd.DataFrame, positions: dict
    ) -> list[Order]:
        orders = []
        if held_review is None or held_review.empty:
            return orders
        for asset, row in held_review.iterrows():
            shares = positions.get(asset, 0.0)
            if shares > 0 and not row["passes_sell"]:
                orders.append(
                    Order(
                        asset=asset,
                        side="sell",
                        shares=shares,
                        reason=f"criteria:{row['sell_reason']}",
                    )
                )
        return orders


STRATEGIES = {
    "buy_and_hold": BuyAndHoldTopK,
    "sell_below_criteria": SellBelowCriteria,
}


def build_strategy(name: str, top_k: int, weighting: str):
    if name not in STRATEGIES:
        raise ConfigError(
            f"unknown strategy {name!r}; available: {sorted(STRATEGIES)}"
        )
    return STRATEGIES[name](top_k=top_k, weighting=weighting)
