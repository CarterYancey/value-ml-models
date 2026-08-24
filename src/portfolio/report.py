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
import pandas as pd  # noqa: E402

from eval.era import crash_label  # noqa: E402
from harness.report import _table  # noqa: E402
from portfolio.engine import SimulationResult  # noqa: E402

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
    the era slice of a backtest."""

    def per_year(result: SimulationResult) -> pd.Series:
        m = result.monthly[result.monthly["twr_return"].notna()]
        if m.empty:
            return pd.Series(dtype=float)
        grouped = m.groupby(m["date"].dt.year)["twr_return"]
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
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

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

    reb = strategy_result.rebalance_log
    n_months = len(reb)
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
    delisted = 0
    if not strategy_result.trades.empty:
        delisted = int(
            (strategy_result.trades["reason"] == "delisted").sum()
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
        f"`{config.weighting}`-weighted; strategy `{config.strategy}`",
        f"- costs: {config.cost_bps} bps per side (benchmark "
        f"{config.benchmark_cost_bps} bps)",
        "",
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
