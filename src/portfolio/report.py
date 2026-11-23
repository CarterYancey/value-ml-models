"""Backtest metrics and the markdown report.

Reporting rules carried over from the evaluation harness: era-sliced
(per-year) results always accompany pooled numbers, crash years are
tagged inline, the benchmark comparison is computed under identical cash
flows and accounting, and the provenance appendix cites the fold
definitions, every bundle's identity, and the number of backtest
configurations tried against this dataset+prices pair.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from eval.era import crash_label  # noqa: E402
from harness.report import _table  # noqa: E402
from portfolio.engine import SimulationResult  # noqa: E402
from portfolio.signals import (  # noqa: E402
    sell_filter_specs,
    sell_score_floors,
)
from portfolio.strategy import STRATEGIES  # noqa: E402

_DAYS_PER_YEAR = 365.25


# ------------------------------------------------------------------ metrics


def xirr(cashflows: list[tuple[pd.Timestamp, float]]) -> float | None:
    """Annualized money-weighted return of dated cashflows (deposits
    negative, terminal value positive), by bisection on the annual rate.
    None when undefined (no flows, no sign change)."""
    flows = [(pd.Timestamp(d), float(a)) for d, a in cashflows if a != 0.0]
    if len(flows) < 2:
        return None
    t0 = min(d for d, _ in flows)

    def npv(rate: float) -> float:
        return sum(
            a / (1.0 + rate) ** ((d - t0).days / _DAYS_PER_YEAR)
            for d, a in flows
        )

    lo, hi = -0.9999, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        f_mid = npv(mid)
        if abs(f_mid) < 1e-9:
            return mid
        if f_lo * f_mid <= 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0


def twr_cagr(monthly: pd.DataFrame) -> float | None:
    """Annualized growth of the time-weighted index over the simulation."""
    dated = monthly[monthly["twr_return"].notna()]
    if dated.empty:
        return None
    days = (monthly["date"].iloc[-1] - monthly["date"].iloc[0]).days
    if days <= 0:
        return None
    index = float(monthly["twr_index"].iloc[-1])
    if index <= 0:
        return -1.0
    return index ** (_DAYS_PER_YEAR / days) - 1.0


def max_drawdown(twr_index: pd.Series) -> float:
    """Most negative peak-to-trough drop of the TWR index (<= 0)."""
    if twr_index.empty:
        return 0.0
    running_max = twr_index.cummax()
    return float((twr_index / running_max - 1.0).min())


def yearly_table(
    strategy: SimulationResult, benchmark: SimulationResult
) -> pd.DataFrame:
    """Per-calendar-year TWR of both legs, with crash years tagged —
    the era slice of a backtest.

    A row of `monthly` carries the return from the previous valuation
    date to its own, so the return belongs to the year that period
    *starts* in: with valuations on the first trading day of each month
    the January row is December's return. Year Y therefore runs from
    the first valuation of January Y to the first of January Y+1 (the
    last year, to the final valuation). Grouping on the row's own date
    would label 1 December to 1 December as the year."""

    def per_year(result: SimulationResult) -> pd.Series:
        monthly = result.monthly
        period_start = monthly["date"].shift(1)
        m = monthly[monthly["twr_return"].notna() & period_start.notna()]
        if m.empty:
            return pd.Series(dtype=float)
        grouped = m.groupby(period_start[m.index].dt.year)["twr_return"]
        return grouped.apply(lambda r: float((1.0 + r).prod() - 1.0))

    strat, bench = per_year(strategy), per_year(benchmark)
    years = sorted(set(strat.index) | set(bench.index))
    deposits = strategy.monthly.groupby(
        strategy.monthly["date"].dt.year
    )["deposit"].sum()
    buys = pd.Series(dtype=float)
    scores = pd.Series(dtype=float)
    if not strategy.trades.empty:
        buy_rows = strategy.trades[strategy.trades["side"] == "buy"]
        if not buy_rows.empty:
            buys = buy_rows.groupby(buy_rows["date"].dt.year)["asset"].count()
            scores = buy_rows.groupby(buy_rows["date"].dt.year)[
                "combined_score"
            ].mean()

    rows = []
    for year in years:
        label = crash_label(int(year))
        rows.append(
            {
                "year": f"{year} ({label})" if label else str(year),
                "strategy_twr": strat.get(year),
                "benchmark_twr": bench.get(year),
                "excess": (
                    strat.get(year) - bench.get(year)
                    if year in strat.index and year in bench.index
                    else None
                ),
                "deposits": float(deposits.get(year, 0.0)),
                "n_buys": int(buys.get(year, 0)),
                "mean_pick_score": (
                    float(scores.get(year)) if year in scores.index else None
                ),
            }
        )
    return pd.DataFrame(rows)


def group_tables(
    trades: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """What was bought, by the candidates' `group` (the sector unless
    the config names another column): the share of buys per group over
    the whole window, and per year the largest group with its share.
    None when the trade log carries no group. Counts buys, not money:
    with equal weights the two agree, with score weights they need
    not."""
    if trades.empty or "group" not in trades.columns:
        return None
    buys = trades[trades["side"] == "buy"].copy()
    if buys.empty:
        return None
    buys["group"] = (
        buys["group"].astype(object).where(buys["group"].notna(), "unknown")
    )
    counts = buys["group"].value_counts()
    overall = pd.DataFrame(
        {
            "group": counts.index,
            "buys": counts.to_numpy(),
            "share": (counts / counts.sum()).to_numpy(),
        }
    )
    buys["year"] = pd.to_datetime(buys["date"]).dt.year
    rows = []
    for year, frame in buys.groupby("year"):
        per = frame["group"].value_counts()
        rows.append(
            {
                "year": int(year),
                "buys": int(len(frame)),
                "stocks": int(frame["asset"].nunique()),
                "groups": int(len(per)),
                "largest_group": per.index[0],
                "largest_share": float(per.iloc[0] / per.sum()),
            }
        )
    return overall, pd.DataFrame(rows)


#: Horizons, in years, the buy-outcome table reads each buy on.
BUY_OUTCOME_HORIZONS = (1, 3)

#: The cross-section column a buy's same-size peers are matched on, and
#: the number of equal-width bins it is cut into (a 5% band of the
#: market-capitalization rank). Size is matched because it decides more
#: of a stock's return against a capitalization-weighted benchmark than
#: anything a model adds: the smaller half of the investable stocks
#: trailed SPY by 12 to 33 points a year in every period of 2005-2026,
#: so a selection that merely prefers large companies "beats the
#: average stock" without any skill.
SIZE_COLUMN = "log_marketcap_rank"
SIZE_BINS = 20


def position_outcomes(
    frame: pd.DataFrame,
    panel,
    valuation_end,
    horizons: tuple[int, ...] = BUY_OUTCOME_HORIZONS,
    early_exit_days: int = 30,
) -> pd.DataFrame:
    """What a position opened at `price` on `date` went on to do, for
    every row of `frame` (`asset`, `date`, `price`): per horizon H its
    annualized return over the H years after the date, that return's
    excess over the benchmark's, and whether it exited early.

    A stock that stops printing before the horizon (a delisting, most
    often an acquisition) exits at its final print and the proceeds
    ride the benchmark to the horizon: a portfolio gets the cash back
    and reinvests it, it does not hold it at zero. (The dataset's label
    convention carries the final price flat to the horizon, which is
    why an acquired stock looks worse on `fwd_*_excess_cagr` than it
    was for a portfolio.) Costs are not included. A row whose horizon
    ends after `valuation_end`, or whose stock the panel has never
    seen, has no outcome at that horizon (NaN).

    Returns the three columns per horizon, indexed like `frame`.
    Vectorized per stock: the backtest reads every candidate of every
    rebalance through it, a million rows on the real dataset."""
    columns = [
        f"{key}_{h}y"
        for h in horizons
        for key in ("return", "excess", "early_exit")
    ]
    if frame.empty:
        return pd.DataFrame(np.nan, index=frame.index, columns=columns)
    bench = panel.benchmark
    bench_dates = bench.index.values
    bench_values = bench.to_numpy(dtype=float)
    end = np.datetime64(pd.Timestamp(valuation_end))

    def bench_asof(when: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(bench_dates, when, side="right") - 1
        return np.where(
            idx >= 0, bench_values[np.clip(idx, 0, None)], np.nan
        )

    dates = pd.to_datetime(frame["date"])
    price = frame["price"].to_numpy(dtype=float)
    start = bench_asof(dates.values)
    targets = {
        h: (dates + pd.DateOffset(years=h)).values for h in horizons
    }
    values = np.full((len(frame), len(columns)), np.nan)
    for asset, rows in frame.groupby("asset", sort=False).indices.items():
        series = panel.series(int(asset))
        if series is None or series.empty:
            continue
        print_dates = series.index.values
        prints = series.to_numpy(dtype=float)
        for n, h in enumerate(horizons):
            target = targets[h][rows]
            idx = np.searchsorted(print_dates, target, side="right") - 1
            ok = (target <= end) & (idx >= 0) & (price[rows] > 0)
            idx = np.clip(idx, 0, None)
            exit_date = print_dates[idx]
            at_exit, at_target = bench_asof(exit_date), bench_asof(target)
            with np.errstate(invalid="ignore", divide="ignore"):
                # the stock to its exit, then the benchmark to the horizon
                total = prints[idx] / price[rows] * at_target / at_exit
                bench_total = at_target / start[rows]
                annual = total ** (1.0 / h)
                excess = annual - bench_total ** (1.0 / h)
            ok &= ~np.isnan(excess)
            early = (
                (target - exit_date) / np.timedelta64(1, "D")
            ) > early_exit_days
            values[rows, 3 * n] = np.where(ok, annual - 1.0, np.nan)
            values[rows, 3 * n + 1] = np.where(ok, excess, np.nan)
            values[rows, 3 * n + 2] = np.where(ok, early.astype(float), np.nan)
    return pd.DataFrame(values, index=frame.index, columns=columns)


def buy_outcomes(
    trades: pd.DataFrame,
    panel,
    valuation_end,
    horizons: tuple[int, ...] = BUY_OUTCOME_HORIZONS,
    early_exit_days: int = 30,
) -> pd.DataFrame:
    """What each buy went on to do, from the price panel: one row per
    buy with, per horizon H, its annualized return over the H years
    after the trade date and that return's excess over the benchmark's
    (`position_outcomes`, which states the delisting convention).

    A portfolio figure weights a year by what the portfolio then held:
    time-weighted return gives the first years, when a deposit-driven
    portfolio is small and young, the weight of the last ones, and
    money-weighted return does the opposite. Neither says whether the
    *selection* was good year by year. This does: every buy counts
    once, read over a fixed horizon from its own trade date."""
    columns = ["asset", "date", "year", "gross"]
    for h in horizons:
        columns += [f"return_{h}y", f"excess_{h}y", f"early_exit_{h}y"]
    if trades.empty:
        return pd.DataFrame(columns=columns)
    buys = trades[trades["side"] == "buy"]
    if buys.empty:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(
        {
            "asset": buys["asset"].to_numpy(),
            "date": pd.to_datetime(buys["date"]).to_numpy(),
            "price": buys["price"].to_numpy(dtype=float),
            "gross": buys["gross"].to_numpy(dtype=float),
        }
    )
    frame["year"] = frame["date"].dt.year.astype(int)
    outcomes = position_outcomes(
        frame, panel, valuation_end, horizons, early_exit_days
    )
    return pd.concat([frame, outcomes], axis=1)[columns]


def candidate_outcomes(
    candidates: pd.DataFrame,
    panel,
    valuation_end,
    horizons: tuple[int, ...] = BUY_OUTCOME_HORIZONS,
) -> pd.DataFrame:
    """`position_outcomes` for every candidate of every rebalance (the
    feed's log: `asset`, `date`, `price`, and `size` when the
    cross-section has `SIZE_COLUMN`), with the candidate's size bin:
    the stocks the buys were chosen from, read as the buys are."""
    if candidates is None or candidates.empty:
        return pd.DataFrame()
    frame = candidates.reset_index(drop=True).copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["year"] = frame["date"].dt.year.astype(int)
    if "size" in frame.columns:
        size = frame["size"].to_numpy(dtype=float)
        bins = np.floor(np.clip(size, 0.0, 1.0) * SIZE_BINS)
        bins = np.minimum(bins, SIZE_BINS - 1)
        frame["size_bin"] = np.where(np.isnan(size), -1, bins).astype(int)
    outcomes = position_outcomes(frame, panel, valuation_end, horizons)
    return pd.concat([frame, outcomes], axis=1)


def reference_table(
    buys: pd.DataFrame,
    candidates: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    """The buys against the stocks they were chosen from, at one
    horizon, by buy year with a pooled row.

    Two references, both equal-weighted and read exactly as the buys
    are. *All candidates*: every stock that passed the screens and had
    a quote at a rebalance of the year. *Same-size peers*: for each
    buy, the candidates of its own rebalance in its own band of
    `SIZE_COLUMN` (`SIZE_BINS` bands); the row gives the mean of the
    buys' peer means and the mean difference. The second is the one
    that reads selection: against a capitalization-weighted benchmark
    the average small stock loses by a wide margin in every period, so
    a ranking that only prefers large companies beats "all candidates"
    without choosing well among them.

    Columns: `buys` (with an outcome), `buys_excess`, `candidates_excess`,
    `vs_candidates`, `peers_excess`, `vs_peers`, `buys_lost`,
    `candidates_lost`, `peers_lost` (shares with a negative return).
    The peer columns are absent when the cross-section has no size
    column."""
    exc, ret = f"excess_{horizon}y", f"return_{horizon}y"
    if buys.empty or candidates.empty or exc not in candidates.columns:
        return pd.DataFrame()
    cand = candidates[candidates[exc].notna()]
    seen = buys[buys[exc].notna()].copy()
    if cand.empty or seen.empty:
        return pd.DataFrame()
    sized = "size_bin" in cand.columns
    if sized:
        peers = (
            cand.assign(lost=(cand[ret] < 0).astype(float))
            .groupby(["date", "size_bin"])
            .agg(peer_excess=(exc, "mean"), peer_lost=("lost", "mean"))
            .reset_index()
        )
        own = cand[["date", "asset", "size_bin"]].drop_duplicates(
            ["date", "asset"]
        )
        seen = seen.merge(own, on=["date", "asset"], how="left").merge(
            peers, on=["date", "size_bin"], how="left"
        )

    def row(label, b: pd.DataFrame, c: pd.DataFrame) -> dict:
        r = {
            "year": label,
            "buys": int(len(b)),
            "buys_excess": float(b[exc].mean()),
            "candidates_excess": float(c[exc].mean()),
        }
        r["vs_candidates"] = r["buys_excess"] - r["candidates_excess"]
        if sized:
            matched = b[b["peer_excess"].notna()]
            r["peers_excess"] = float(matched["peer_excess"].mean())
            r["vs_peers"] = float(
                (matched[exc] - matched["peer_excess"]).mean()
            )
        r["buys_lost"] = float((b[ret] < 0).mean())
        r["candidates_lost"] = float((c[ret] < 0).mean())
        if sized:
            r["peers_lost"] = float(b["peer_lost"].mean())
        return r

    rows = [
        row(int(y), g, cand[cand["year"] == y])
        for y, g in seen.groupby("year", sort=True)
        if (cand["year"] == y).any()
    ]
    rows.append(row("all buys", seen, cand[cand["year"].isin(seen["year"])]))
    return pd.DataFrame(rows)


def buy_outcome_table(
    outcomes: pd.DataFrame,
    horizons: tuple[int, ...] = BUY_OUTCOME_HORIZONS,
) -> pd.DataFrame:
    """`buy_outcomes` by buy year, with a pooled row: per horizon the
    number of buys with an outcome, their mean and median excess return
    a year over the benchmark, the share that beat it, the share that
    lost money and the share that exited early (stopped printing)."""
    if outcomes.empty:
        return pd.DataFrame()

    def row(label, frame: pd.DataFrame) -> dict:
        r: dict = {"year": label, "buys": int(len(frame))}
        for h in horizons:
            seen = frame[frame[f"excess_{h}y"].notna()]
            r[f"n_{h}y"] = int(len(seen))
            if seen.empty:
                for key in ("mean_excess", "median_excess", "beat", "lost",
                            "early_exit"):
                    r[f"{key}_{h}y"] = float("nan")
                continue
            r[f"mean_excess_{h}y"] = float(seen[f"excess_{h}y"].mean())
            r[f"median_excess_{h}y"] = float(seen[f"excess_{h}y"].median())
            r[f"beat_{h}y"] = float((seen[f"excess_{h}y"] > 0).mean())
            r[f"lost_{h}y"] = float((seen[f"return_{h}y"] < 0).mean())
            r[f"early_exit_{h}y"] = float(seen[f"early_exit_{h}y"].mean())
        return r

    rows = [row(int(y), g) for y, g in outcomes.groupby("year", sort=True)]
    rows.append(row("all buys", outcomes))
    return pd.DataFrame(rows)


def _reference_lines(
    buys: pd.DataFrame, candidates: pd.DataFrame | None
) -> list[str]:
    """The report section that sets the buys beside their candidates
    (`reference_table`), longest horizon first; empty without a
    candidate log."""
    if candidates is None or candidates.empty:
        return []
    tables = []
    for h in sorted(BUY_OUTCOME_HORIZONS, reverse=True):
        table = reference_table(buys, candidates, h)
        if table.empty:
            continue
        view = table.copy()
        for col in view.columns:
            if col not in ("year", "buys"):
                view[col] = view[col].map(_pct)
        tables += [f"Over {h} year{'s' if h > 1 else ''}:", "", _table(view), ""]
    if not tables:
        return []
    sized = "size_bin" in candidates.columns
    lines = [
        "### Against the stocks they were chosen from",
        "",
        "The same reading for every candidate of every rebalance (each "
        "stock that passed the screens and had a quote), equal-weighted: "
        "`candidates_excess` is their mean annualized return minus the "
        "benchmark's, `vs_candidates` the buys' mean minus theirs, "
        "`*_lost` the shares with a negative return."
        + (
            " `peers_excess` is the mean, over the buys, of the candidates "
            f"of the same rebalance in the same band of `{SIZE_COLUMN}` "
            f"({SIZE_BINS} bands), and `vs_peers` the buys' mean lead over "
            "them. **Read `vs_peers` for the selection.** Against a "
            "capitalization-weighted benchmark the average small stock "
            "trails by a wide margin in every period, so a ranking that "
            "only prefers large companies beats `candidates` without "
            "choosing well among them; and when `candidates_excess` and "
            "`peers_excess` are far below zero, the benchmark outran "
            "equal-weighted stocks of every kind and no equal-weighted "
            "selection from this universe kept up with it."
            if sized
            else ""
        ),
        "",
    ]
    return lines + tables


def headline_table(
    strategy: SimulationResult, benchmark: SimulationResult
) -> pd.DataFrame:
    def row(name: str, result: SimulationResult) -> dict:
        return {
            "leg": name,
            "deposits": result.total_deposits,
            "final_value": result.final_value,
            "profit": result.final_value - result.total_deposits,
            "mwr_annualized": xirr(result.cashflows),
            "twr_cagr": twr_cagr(result.monthly),
            "max_drawdown": max_drawdown(result.monthly["twr_index"]),
            "costs_paid": result.total_costs,
        }

    return pd.DataFrame([row("strategy", strategy), row("benchmark", benchmark)])


# ------------------------------------------------------------------ figures


def render_equity_plot(
    strategy: SimulationResult,
    benchmark: SimulationResult,
    path: str | Path,
    title: str,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    s, b = strategy.monthly, benchmark.monthly
    fig, (ax_value, ax_dd) = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )
    ax_value.plot(s["date"], s["total_value"], label="strategy", lw=1.6)
    ax_value.plot(b["date"], b["total_value"], label="benchmark", lw=1.6)
    ax_value.plot(
        s["date"], s["deposit"].cumsum(), label="deposits (cumulative)",
        lw=1.0, ls="--", color="grey",
    )
    ax_value.set_ylabel("portfolio value")
    ax_value.set_title(title)
    ax_value.legend(loc="upper left", frameon=False)
    ax_value.grid(True, alpha=0.3)

    for frame, label in ((s, "strategy"), (b, "benchmark")):
        dd = frame["twr_index"] / frame["twr_index"].cummax() - 1.0
        ax_dd.plot(frame["date"], dd, label=label, lw=1.2)
    ax_dd.set_ylabel("drawdown (TWR)")
    ax_dd.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


# ------------------------------------------------------------------- report


def _pct(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{v * 100:.2f}%"


def _money(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{v:,.2f}"


def write_backtest_report(
    *,
    path: str | Path,
    config,
    run_id: str,
    git_sha: str,
    dataset,
    panel,
    model_set,
    strategy_result: SimulationResult,
    benchmark_result: SimulationResult,
    buy_years: list[int],
    buy_end,
    valuation_end,
    configurations_tried: int,
    artifacts: dict,
    buy_outcome_frame: pd.DataFrame | None = None,
    candidate_outcome_frame: pd.DataFrame | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    strategy_cls = STRATEGIES.get(config.strategy)
    strategy_sells = strategy_cls is not None and hasattr(
        strategy_cls, "sell_orders"
    )

    headline = headline_table(strategy_result, benchmark_result)
    headline_view = headline.copy()
    for col in ("mwr_annualized", "twr_cagr", "max_drawdown"):
        headline_view[col] = headline_view[col].map(_pct)
    for col in ("deposits", "final_value", "profit", "costs_paid"):
        headline_view[col] = headline_view[col].map(_money)

    yearly = yearly_table(strategy_result, benchmark_result)
    yearly_view = yearly.copy()
    for col in ("strategy_twr", "benchmark_twr", "excess"):
        yearly_view[col] = yearly_view[col].map(_pct)
    yearly_view["deposits"] = yearly_view["deposits"].map(_money)

    down = yearly[yearly["benchmark_twr"].notna() & (yearly["benchmark_twr"] < 0)]
    if down.empty:
        defensive = (
            "No benchmark down-years fall inside the backtest window, so "
            "the defensive hypothesis (PLAN §4) is **not testable** here."
        )
    else:
        won = int((down["excess"].fillna(-1) > 0).sum())
        defensive = (
            f"Benchmark down-years in window: {len(down)}; strategy lost "
            f"less (positive excess) in {won} of them. See the tagged rows "
            "above — few, correlated observations, wide uncertainty."
        )

    group_lines = []
    grouped = group_tables(strategy_result.trades)
    if grouped is not None:
        overall, by_year = grouped
        overall_view = overall.copy()
        overall_view["share"] = overall_view["share"].map(_pct)
        by_year_view = by_year.copy()
        by_year_view["largest_share"] = by_year_view["largest_share"].map(_pct)
        group_lines = [
            f"## What was bought, by `{config.group_column}`",
            "",
            "Shares of the number of buys. A portfolio whose buys sit in "
            "one group is one bet, however many stocks it holds.",
            "",
            _table(overall_view),
            "",
            _table(by_year_view),
            "",
        ]

    reb = strategy_result.rebalance_log
    n_months = len(reb)
    buy_lines = []
    if buy_outcome_frame is not None and not buy_outcome_frame.empty:
        view = buy_outcome_table(buy_outcome_frame)
        for col in view.columns:
            if col.startswith(("mean_", "median_", "beat_", "lost_",
                               "early_exit_")):
                view[col] = view[col].map(_pct)
        horizons = ", ".join(f"{h}" for h in BUY_OUTCOME_HORIZONS)
        buy_lines = [
            "## What the buys went on to do",
            "",
            f"Every buy read on its own, over the {horizons} years after "
            "its trade date, from the price panel: `mean_excess` and "
            "`median_excess` are the buys' annualized return minus the "
            f"benchmark's over the same dates, `beat` the share above it, "
            "`lost` the share with a negative return, `early_exit` the "
            "share that stopped printing before the horizon (they exit "
            "at the final print and the proceeds ride the benchmark to "
            "the horizon, as a portfolio reinvests what an acquisition "
            "pays out). `n` counts the buys whose horizon ends inside "
            "the valuation window. One buy, one vote, no costs: this "
            "reads the selection, where the headline reads the "
            "portfolio (time-weighted return gives the small early "
            "portfolio the weight of the large late one; money-weighted "
            "return the reverse).",
            "",
            _table(view),
            "",
        ]
        buy_lines += _reference_lines(
            buy_outcome_frame, candidate_outcome_frame
        )

    coverage_lines = []
    if n_months:
        zero = int((reb["n_bought"] == 0).sum())
        short = int(
            (reb["n_bought"].between(1, config.top_k - 1)).sum()
        )
        coverage_lines = [
            f"- rebalance months: {n_months}; months with **no** qualifying "
            f"picks (cash held): {zero}; months with fewer than "
            f"top_k={config.top_k} picks: {short}",
        ]
        for col, desc in (
            ("n_cross_section", "stocks in the point-in-time cross-section"),
            ("n_after_min_score", "after the per-model min_score floor"),
            ("n_after_filters", "after the column filters"),
            ("n_after_investability", "after the investability filter"),
            ("n_priced", "with a tradable quote"),
        ):
            if col in reb.columns:
                coverage_lines.append(
                    f"- mean {desc}: {reb[col].mean():.1f} "
                    f"(min {int(reb[col].min())})"
                )
    delisted = criteria_sells = 0
    if not strategy_result.trades.empty:
        reasons = strategy_result.trades["reason"].astype(str)
        delisted = int((reasons == "delisted").sum())
        criteria_sells = int(reasons.str.startswith("criteria:").sum())
    if strategy_sells:
        coverage_lines.append(
            f"- criteria sells: {criteria_sells} (per-cause breakdown in "
            "the trades CSV `reason` column)"
        )
    coverage_lines.append(
        f"- forced delisting liquidations: {delisted} (final-print "
        "convention, sell cost applied)"
    )

    floors = {}
    for name in model_set.names:
        floor = config.min_scores.get(name, config.min_score)
        if floor is not None:
            floors[name] = floor
    if not floors:
        floor_line = ""
    elif config.min_scores:
        floor_line = ", per-model floors: " + ", ".join(
            f"`{n}` > {f}" for n, f in floors.items()
        )
    else:
        floor_line = f", per-model floor score > {config.min_score}"

    sell_lines = []
    if strategy_sells:
        sell_lines.append(
            f"- sell discipline (`{config.strategy}`): a held position "
            "failing the sell criteria at a rebalance is sold entirely "
            "(proceeds fund that month's buys); falling out of the top "
            f"{config.top_k} alone is never a sell. A holding whose "
            "snapshot has aged out of the cross-section fails the "
            "criteria."
        )
        s_floors = sell_score_floors(config, model_set.names)
        s_filters = sell_filter_specs(config)
        own_floors = (
            config.sell_min_score is not None or config.sell_min_scores
        )
        floor_desc = (
            ", ".join(
                f"`{c.removeprefix('score_')}` > {v}"
                for c, v in s_floors.items()
            )
            or "(none)"
        )
        filter_desc = (
            "; ".join(f"`{f.describe()}`" for f in s_filters) or "(none)"
        )
        sell_lines.append(
            f"- sell floors{'' if own_floors else ' (inherited from buy)'}: "
            f"{floor_desc}"
        )
        sell_lines.append(
            "- sell filters"
            f"{'' if config.sell_filters is not None else ' (inherited from buy)'}: "
            f"{filter_desc}"
        )
        if config.sell_max_rank_pct is not None:
            sell_lines.append(
                "- sell rank: a held position is sold once it is no "
                f"longer among the top {config.sell_max_rank_pct:.0%} of "
                "the month's buy candidates by combined score (after "
                "every buy screen), or is not a candidate at all"
            )

    inv_lines = (
        [f"- `{f.describe()}`" for f in config.investability]
        if config.investability
        else [
            "- **NONE — explicitly opted out.** Microcaps dominate this "
            "universe and there is no upstream liquidity floor; treat "
            "these results as paper returns that may not be attainable "
            "at size."
        ]
    )

    provenance = getattr(model_set, "provenance", None) or [{}] * len(
        model_set.bundles
    )
    bundle_lines, refit_rows = [], []
    for d, b, name, info in zip(
        model_set.bundle_dirs, model_set.bundles, model_set.names, provenance
    ):
        fold_years = info.get("fold_years", b.folds)
        policy_years = info.get("policy_years", [])
        parts = []
        if fold_years:
            parts.append(f"folds {fold_years[0]}–{fold_years[-1]}")
        if policy_years:
            what = (
                "year-end refits"
                if info.get("policy") == "refit"
                else f"frozen fold-{max(b.folds)} model"
            )
            parts.append(
                f"{policy_years[0]}–{policy_years[-1]} served by {what}"
            )
        served = "; ".join(parts) or f"folds {b.folds}"
        bundle_lines.append(
            f"- `{name}` — label `{b.train_config.label}` "
            f"({b.train_config.horizon_years}y), model "
            f"`{b.train_config.model_name}`, config "
            f"`{b.train_config.config_hash}`, train run `{b.run_id}`, "
            f"{served} (from `{d}`)"
        )
        for year, stats in sorted(info.get("refit_stats", {}).items()):
            refit_rows.append(
                {
                    "bundle": name,
                    "trade_year": year,
                    "n_train_rows": stats["n_train_rows"],
                    "effective_train_size": round(
                        stats["effective_train_size"], 1
                    ),
                    "last_usable_snapshot": stats["last_usable_snapshot"],
                    "source": stats.get("source", "fit"),
                }
            )

    filters_lines = [f"- `{f.describe()}`" for f in config.filters] or [
        "- (none)"
    ]

    lines = [
        f"# Portfolio backtest — {config.name}",
        "",
        f"- run `{run_id}`, git `{git_sha}`, backtest config "
        f"`{config.config_hash}`",
        f"- dataset `{dataset.version}`, price panel `{panel.version}` "
        f"(benchmark `{panel.benchmark_name}`)",
        f"- buy window: {buy_years[0]}–{buy_years[-1]} (last buy "
        f"{buy_end.date()}), valuation through {valuation_end.date()}; "
        f"trade years past a bundle's walk-forward folds are served by "
        f"`model_update = \"{config.model_update}\"` (see the bundle "
        "list below)",
        f"- deposits: {_money(config.monthly_cash)} on the first trading "
        "day of each month, identically into both legs",
        "",
        "**These are simulated, cost-adjusted paper results under the "
        "assumptions below — not live performance.** Scores come from "
        "walk-forward fold models (each trade year scored by a model "
        "trained, purged and embargoed, on years before it); deployment "
        "bundles are never backtested.",
        "",
        "## Headline",
        "",
        _table(headline_view),
        "",
        "Money-weighted (MWR/XIRR) is what the deposits earned; "
        "time-weighted (TWR) is the strategy's per-period compounding "
        "with deposits treated as external flows. Both legs get identical "
        "deposit dates and accounting.",
        "",
        "## Per-year results (era slice)",
        "",
        _table(yearly_view),
        "",
        f"**Defensive hypothesis:** {defensive}",
        "",
        "## Strategy definition",
        "",
        f"- signal: {len(model_set.bundles)} walk-forward model(s), "
        f"combined by `{config.combine}`" + floor_line,
        "- the `product` combination is a conviction ranking, not a joint "
        "probability — the per-model scores are correlated"
        if config.combine == "product"
        else "",
        "- filters (NULL fails any screen):",
        *filters_lines,
        "- investability filter:",
        *inv_lines,
        f"- selection: top {config.top_k} by combined score, "
        f"`{config.weighting}`-weighted; strategy `{config.strategy}`"
        + (
            f"; at most {config.max_per_group} of a rebalance's buys per "
            f"`{config.group_column}`, walked in score order"
            if config.max_per_group is not None
            else ""
        ),
        *sell_lines,
        f"- costs: {config.cost_bps} bps per side (benchmark "
        f"{config.benchmark_cost_bps} bps)",
        "",
        *group_lines,
        *buy_lines,
        "## Coverage & diagnostics",
        "",
        *coverage_lines,
        "",
        "## Assumptions (all of them)",
        "",
        "- Execution at the trade date's total-return adjusted close "
        "(dividends implicitly reinvested), "
        + (
            "fractional shares"
            if config.fractional_shares
            else "whole shares only (a buy budget's remainder stays in "
            "cash for the next month)"
        )
        + ", no market impact beyond the flat per-side cost.",
        f"- Candidates need a print within {config.max_quote_age_days} "
        "day(s) of the trade date; positions silent for "
        f"{config.delist_after_days}+ days are liquidated at their final "
        "print (the upstream delisting convention).",
        f"- Signals use each stock's latest completed-quarter median-kind "
        f"snapshot, at most {config.max_staleness_days} days old — up to "
        "a quarter-plus staler than a live inference run, and ranked "
        "within the snapshot's own quarter rather than the trade date's "
        "cross-section.",
        "- Trade years inside a bundle's walk-forward folds use that "
        "year's fold model (trained purged/embargoed on years before "
        "it). Years past the last fold are served by "
        + (
            "**simulated year-end deployment refits**: the same config "
            "refit on every row whose label window was fully observable "
            f"by Jan 1 of the trade year (+{config.label_lag_days}d "
            "settlement lag) — data/manual.md §4 rule 7 applied "
            "point-in-time; no split tags are read and no test set "
            "exists (see the refit appendix)."
            if config.model_update == "refit"
            else "the **frozen** last-fold model, unchanged."
        ),
        "- Those later trade years — and all valuation past the last "
        "fold — overlap the sealed holdout era. That is what a live "
        "simulation requires, but it makes this segment selection-toxic: "
        "results there are context; feeding them back into model or "
        "strategy selection erodes the holdout.",
        "",
        "## Provenance",
        "",
        f"- backtest configurations tried against dataset "
        f"`{dataset.version}`: {configurations_tried} (this one included; "
        "every run is logged, failures too)",
        f"- fold definitions: `{dataset.root / 'split_folds.parquet'}` "
        "(frozen upstream; the buy window is the intersection of every "
        "bundle's fold years)",
        "- model bundles:",
        *bundle_lines,
        *(
            [
                "",
                "### Simulated year-end refits",
                "",
                "One refit per (bundle, trade year) past that bundle's "
                "folds — trained on rows whose labels were observable by "
                "Jan 1, all snapshot kinds, delistings included, no "
                "split tags read. `source = cache` rows were reused from "
                "the refit cache (identical by construction: the cache "
                "key pins train config, dataset version, year, and "
                "label lag):",
                "",
                _table(pd.DataFrame(refit_rows)),
            ]
            if refit_rows
            else []
        ),
        "",
        "### Artifacts",
        "",
        *[
            f"- {kind}: `{p}`"
            for kind, p in artifacts.items()
        ],
        "",
    ]
    path.write_text("\n".join(line for line in lines if line is not None))
    return path
