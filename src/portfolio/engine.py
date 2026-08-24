"""The portfolio simulation loop: dates, cash flows, execution, valuation.

Deliberately strategy- and signal-agnostic: the engine is handed a
trading calendar, a deposit schedule, a price source, a strategy, and a
`candidates_fn` that produces the scored candidate list for a rebalance
date. The benchmark leg runs through this same engine with a one-asset
candidate list, so strategy and benchmark are measured by *identical*
accounting — same deposit dates, same valuation dates, same cost and
share mechanics.

Accounting conventions (all disclosed in reports):

- Execution at the trade date's adjusted close; **whole shares** by
  default (a buy order is a cash budget; the engine buys
  ⌊budget / (price · (1 + cost))⌋ shares and the remainder stays in
  cash for next month) — `fractional_shares=True` restores exact
  budget spending; no market impact beyond the flat per-side `cost_bps`
  charged on gross.
- `closeadj` is total-return adjusted, so a fixed share count implicitly
  reinvests dividends (the upstream label convention).
- A held position whose last print is older than `delist_after_days` at
  a valuation date is liquidated at its final print (the upstream
  delisting convention: the final price is what you got), cost applied;
  proceeds sit in cash until the next rebalance.
- Positions carry their cash cost basis (buy gross + buy costs), so
  every sell reports realized profit net of both sides' costs.
- Time-weighted returns chain V_pre(t+1) / (V_pre(t) + deposit(t)), so
  deposits are external flows while transaction costs and delistings
  stay inside performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import math

import pandas as pd

from portfolio.prices import SeriesPriceSource
from portfolio.strategy import Order


@dataclass
class Position:
    shares: float = 0.0
    #: cash spent acquiring the current shares: gross + buy costs
    cost_basis: float = 0.0
    ticker: str = ""


@dataclass
class SimulationResult:
    #: one row per valuation date: deposit, cash, holdings_value,
    #: total_value (after trades/costs), value_after_deposit (the TWR
    #: denominator: pre-trade value + this date's deposit — total_value
    #: differs from it by this date's buy costs), costs (paid this
    #: date), twr_return, twr_index, n_held
    monthly: pd.DataFrame
    #: one row per executed order (buys and sells, forced liquidations
    #: included): ticker, shares, price, gross, cost; buys carry the
    #: combined and per-model scores; sells carry cost basis and
    #: realized profit (net of both sides' costs)
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
    fractional_shares: bool = False,
) -> SimulationResult:
    """Run one portfolio leg over `dates` (ascending valuation dates;
    those in `buy_dates` also receive the deposit and a rebalance).
    `candidates_fn(date) -> (candidates, diagnostics)` supplies the
    scored, filtered, priced candidate frame (columns at least `asset`,
    `combined_score`, `price`; `ticker` and `score_*` columns are
    carried into the trade log when present)."""
    cost_rate = float(cost_bps) / 10_000.0
    cash = 0.0
    positions: dict[object, Position] = {}

    monthly_rows: list[dict] = []
    trade_rows: list[dict] = []
    rebalance_rows: list[dict] = []
    cashflows: list[tuple[pd.Timestamp, float]] = []
    total_deposits = total_costs = 0.0
    prev_denominator: float | None = None
    twr_index = 1.0

    for when in dates:
        costs_today = 0.0

        # 1. forced liquidation of positions whose series has gone stale
        for asset in [a for a, p in positions.items() if p.shares > 0]:
            if price_source.asof(asset, when, delist_after_days) is not None:
                continue
            position = positions[asset]
            final = price_source.final_print(asset)
            if final is None:  # never printed: worthless, remove
                price, print_date = 0.0, pd.NaT
            else:
                price, print_date = final
            gross = position.shares * price
            cost = gross * cost_rate
            proceeds = gross - cost
            trade_rows.append(
                {
                    "date": when,
                    "asset": asset,
                    "ticker": position.ticker,
                    "side": "sell",
                    "reason": "delisted",
                    "shares": position.shares,
                    "price": price,
                    "price_date": print_date,
                    "gross": gross,
                    "cost": cost,
                    "cost_basis": position.cost_basis,
                    "profit": proceeds - position.cost_basis,
                }
            )
            cash += proceeds
            total_costs += cost
            costs_today += cost
            del positions[asset]

        # 2. mark to market (every surviving position has a quote)
        holdings_value = 0.0
        for asset, position in positions.items():
            quote = price_source.asof(asset, when, delist_after_days)
            holdings_value += position.shares * quote[0]
        v_pre = cash + holdings_value

        # 3. time-weighted return over the elapsed period
        twr_return = None
        if prev_denominator is not None and prev_denominator > 0:
            twr_return = v_pre / prev_denominator - 1.0
            twr_index *= 1.0 + twr_return

        # 4. deposit + rebalance
        flow = 0.0
        if when in buy_dates:
            flow = float(deposit)
            cash += flow
            total_deposits += flow
            cashflows.append((when, -flow))

            candidates, diagnostics = candidates_fn(when)
            orders = strategy.orders(
                when, candidates, cash,
                {a: p.shares for a, p in positions.items()},
            )
            cand_info = (
                candidates.set_index("asset")
                if not candidates.empty
                else pd.DataFrame()
            )
            n_bought = 0
            for order in orders:
                before = len(trade_rows)
                cash, holdings_value = _execute(
                    order, when, cost_rate, cash, holdings_value,
                    positions, cand_info, price_source,
                    delist_after_days, fractional_shares, trade_rows,
                )
                if len(trade_rows) > before:  # the order actually filled
                    total_costs += trade_rows[-1]["cost"]
                    costs_today += trade_rows[-1]["cost"]
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
        denominator = v_pre + flow  # next period's TWR denominator
        monthly_rows.append(
            {
                "date": when,
                "deposit": flow,
                "cash": cash,
                "holdings_value": holdings_value,
                "total_value": v_post,
                "value_after_deposit": denominator,
                "costs": costs_today,
                "twr_return": twr_return,
                "twr_index": twr_index,
                "n_held": len(positions),
            }
        )
        prev_denominator = denominator

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
    positions: dict[object, Position],
    cand_info: pd.DataFrame,
    price_source: SeriesPriceSource,
    delist_after_days: int,
    fractional_shares: bool,
    trade_rows: list[dict],
) -> tuple[float, float]:
    """Execute one order against the books; returns (cash, holdings_value).
    Buys treat `cash_amount` as a budget (whole shares by default, the
    remainder stays in cash); sells liquidate shares at the date's
    quote."""
    if order.side == "buy":
        budget = min(float(order.cash_amount), cash)
        if budget <= 0 or order.asset not in cand_info.index:
            return cash, holdings_value
        row = cand_info.loc[order.asset]
        price = float(row["price"])
        shares = budget / (price * (1.0 + cost_rate))
        if not fractional_shares:
            # tolerance far below a cent, so float noise in the budget
            # split (e.g. 749.9999999999999) can't drop a whole share
            shares = math.floor(shares + 1e-9)
        if shares <= 0:
            return cash, holdings_value
        gross = shares * price
        cost = gross * cost_rate
        spend = gross + cost
        position = positions.setdefault(
            order.asset, Position(ticker=str(row.get("ticker", order.asset)))
        )
        position.shares += shares
        position.cost_basis += spend
        cash -= spend
        holdings_value += gross
        trade_rows.append(
            {
                "date": when,
                "asset": order.asset,
                "ticker": position.ticker,
                "side": "buy",
                "reason": "rebalance",
                "shares": shares,
                "price": price,
                "price_date": when,
                "gross": gross,
                "cost": cost,
                "combined_score": float(
                    row.get("combined_score", float("nan"))
                ),
                # per-model scores, for line-by-line sanity checks
                **{
                    c: float(row[c])
                    for c in cand_info.columns
                    if c.startswith("score_")
                },
            }
        )
        return cash, holdings_value

    if order.side == "sell":
        position = positions.get(order.asset)
        held = position.shares if position else 0.0
        shares = min(float(order.shares), held)
        if not fractional_shares:
            shares = math.floor(shares)
        if shares <= 0:
            return cash, holdings_value
        quote = price_source.asof(order.asset, when, delist_after_days)
        if quote is None:
            return cash, holdings_value  # the delisting pass handles it
        price = quote[0]
        gross = shares * price
        cost = gross * cost_rate
        basis = position.cost_basis * (shares / position.shares)
        position.shares -= shares
        position.cost_basis -= basis
        if position.shares <= 0:
            del positions[order.asset]
        cash += gross - cost
        holdings_value -= gross
        trade_rows.append(
            {
                "date": when,
                "asset": order.asset,
                "ticker": position.ticker,
                "side": "sell",
                "reason": "rebalance",
                "shares": shares,
                "price": price,
                "price_date": when,
                "gross": gross,
                "cost": cost,
                "cost_basis": basis,
                "profit": (gross - cost) - basis,
            }
        )
        return cash, holdings_value

    raise ValueError(f"unknown order side {order.side!r}")
