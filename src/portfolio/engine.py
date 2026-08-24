"""The portfolio simulation loop: dates, cash flows, execution, valuation.

Deliberately strategy- and signal-agnostic: the engine is handed a
trading calendar, a deposit schedule, a price source, a strategy, and a
`candidates_fn` that produces the scored candidate list for a rebalance
date. The benchmark leg runs through this same engine with a one-asset
candidate list, so strategy and benchmark are measured by *identical*
accounting — same deposit dates, same valuation dates, same cost
mechanics.

Accounting conventions (all disclosed in reports):

- Execution at the trade date's adjusted close; fractional shares; no
  market impact beyond the flat per-side `cost_bps`.
- `closeadj` is total-return adjusted, so a fixed share count implicitly
  reinvests dividends (the upstream label convention).
- A held position whose last print is older than `delist_after_days` at
  a valuation date is liquidated at its final print (the upstream
  delisting convention: the final price is what you got), cost applied;
  proceeds sit in cash until the next rebalance.
- Time-weighted returns chain V_pre(t+1) / (V_pre(t) + deposit(t)), so
  deposits are external flows while transaction costs and delistings
  stay inside performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from portfolio.prices import SeriesPriceSource
from portfolio.strategy import Order


@dataclass
class SimulationResult:
    #: one row per valuation date: deposit, cash, holdings, total_value,
    #: capital (post-deposit denominator), twr_return, twr_index, n_held
    monthly: pd.DataFrame
    #: one row per executed order (buys and forced liquidations)
    trades: pd.DataFrame
    #: per-rebalance-date diagnostics from candidates_fn
    rebalance_log: pd.DataFrame
    total_deposits: float
    total_costs: float
    final_value: float
    #: (date, amount) external flows plus the terminal value — XIRR input
    cashflows: list[tuple[pd.Timestamp, float]] = field(default_factory=list)


def run_simulation(
    *,
    dates: list[pd.Timestamp],
    buy_dates: set[pd.Timestamp],
    deposit: float,
    price_source: SeriesPriceSource,
    strategy,
    candidates_fn,
    cost_bps: float,
    delist_after_days: int,
) -> SimulationResult:
    """Run one portfolio leg over `dates` (ascending valuation dates;
    those in `buy_dates` also receive the deposit and a rebalance).
    `candidates_fn(date) -> (candidates, diagnostics)` supplies the
    scored, filtered, priced candidate frame (columns at least `asset`,
    `combined_score`, `price`)."""
    cost_rate = float(cost_bps) / 10_000.0
    cash = 0.0
    positions: dict[object, float] = {}

    monthly_rows: list[dict] = []
    trade_rows: list[dict] = []
    rebalance_rows: list[dict] = []
    cashflows: list[tuple[pd.Timestamp, float]] = []
    total_deposits = total_costs = 0.0
    prev_capital: float | None = None
    twr_index = 1.0

    for when in dates:
        # 1. forced liquidation of positions whose series has gone stale
        for asset in [a for a, s in positions.items() if s > 0]:
            if price_source.asof(asset, when, delist_after_days) is not None:
                continue
            final = price_source.final_print(asset)
            if final is None:  # never printed: worthless, remove
                price, print_date, proceeds, cost = 0.0, pd.NaT, 0.0, 0.0
            else:
                price, print_date = final
                gross = positions[asset] * price
                cost = gross * cost_rate
                proceeds = gross - cost
            trade_rows.append(
                {
                    "date": when,
                    "asset": asset,
                    "side": "sell",
                    "reason": "delisted",
                    "shares": positions[asset],
                    "price": price,
                    "price_date": print_date,
                    "gross": positions[asset] * price,
                    "cost": cost,
                }
            )
            cash += proceeds
            total_costs += cost
            del positions[asset]

        # 2. mark to market (every surviving position has a quote)
        holdings_value = 0.0
        for asset, shares in positions.items():
            quote = price_source.asof(asset, when, delist_after_days)
            holdings_value += shares * quote[0]
        v_pre = cash + holdings_value

        # 3. time-weighted return over the elapsed period
        twr_return = None
        if prev_capital is not None and prev_capital > 0:
            twr_return = v_pre / prev_capital - 1.0
            twr_index *= 1.0 + twr_return

        # 4. deposit + rebalance
        flow = 0.0
        if when in buy_dates:
            flow = float(deposit)
            cash += flow
            total_deposits += flow
            cashflows.append((when, -flow))

            candidates, diagnostics = candidates_fn(when)
            orders = strategy.orders(when, candidates, cash, positions)
            scores = (
                candidates.set_index("asset")["combined_score"]
                if not candidates.empty
                else pd.Series(dtype=float)
            )
            prices = (
                candidates.set_index("asset")["price"]
                if not candidates.empty
                else pd.Series(dtype=float)
            )
            n_bought = 0
            for order in orders:
                before = len(trade_rows)
                cash, holdings_value = _execute(
                    order, when, cost_rate, cash, holdings_value,
                    positions, prices, scores, price_source,
                    delist_after_days, trade_rows,
                )
                if len(trade_rows) > before:  # the order actually filled
                    total_costs += trade_rows[-1]["cost"]
                    if trade_rows[-1]["side"] == "buy":
                        n_bought += 1
            rebalance_rows.append(
                {
                    "date": when,
                    "n_orders": len(orders),
                    "n_bought": n_bought,
                    "cash_after": cash,
                    **diagnostics,
                }
            )

        v_post = cash + holdings_value
        capital = v_pre + flow  # denominator for the next period's TWR
        monthly_rows.append(
            {
                "date": when,
                "deposit": flow,
                "cash": cash,
                "holdings_value": holdings_value,
                "total_value": v_post,
                "capital": capital,
                "twr_return": twr_return,
                "twr_index": twr_index,
                "n_held": len(positions),
            }
        )
        prev_capital = capital

    final_value = monthly_rows[-1]["total_value"] if monthly_rows else 0.0
    if monthly_rows:
        cashflows.append((monthly_rows[-1]["date"], final_value))
    return SimulationResult(
        monthly=pd.DataFrame(monthly_rows),
        trades=pd.DataFrame(trade_rows),
        rebalance_log=pd.DataFrame(rebalance_rows),
        total_deposits=total_deposits,
        total_costs=total_costs,
        final_value=final_value,
        cashflows=cashflows,
    )


def _execute(
    order: Order,
    when: pd.Timestamp,
    cost_rate: float,
    cash: float,
    holdings_value: float,
    positions: dict,
    prices: pd.Series,
    scores: pd.Series,
    price_source: SeriesPriceSource,
    delist_after_days: int,
    trade_rows: list[dict],
) -> tuple[float, float]:
    """Execute one order against the books; returns (cash, holdings_value).
    Buys spend `cash_amount` (cost inside); sells liquidate shares at the
    date's quote."""
    if order.side == "buy":
        amount = min(float(order.cash_amount), cash)
        if amount <= 0:
            return cash, holdings_value
        price = float(prices[order.asset])
        cost = amount * cost_rate
        shares = (amount - cost) / price
        positions[order.asset] = positions.get(order.asset, 0.0) + shares
        cash -= amount
        holdings_value += shares * price
        trade_rows.append(
            {
                "date": when,
                "asset": order.asset,
                "side": "buy",
                "reason": "rebalance",
                "shares": shares,
                "price": price,
                "price_date": when,
                "gross": amount,
                "cost": cost,
                "combined_score": float(scores.get(order.asset, float("nan"))),
            }
        )
        return cash, holdings_value

    if order.side == "sell":
        held = positions.get(order.asset, 0.0)
        shares = min(float(order.shares), held)
        if shares <= 0:
            return cash, holdings_value
        quote = price_source.asof(order.asset, when, delist_after_days)
        if quote is None:
            return cash, holdings_value  # the delisting pass handles it
        price = quote[0]
        gross = shares * price
        cost = gross * cost_rate
        positions[order.asset] = held - shares
        if positions[order.asset] <= 0:
            del positions[order.asset]
        cash += gross - cost
        holdings_value -= gross
        trade_rows.append(
            {
                "date": when,
                "asset": order.asset,
                "side": "sell",
                "reason": "rebalance",
                "shares": shares,
                "price": price,
                "price_date": when,
                "gross": gross,
                "cost": cost,
            }
        )
        return cash, holdings_value

    raise ValueError(f"unknown order side {order.side!r}")
