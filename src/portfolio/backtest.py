"""`vml-backtest`: run one portfolio strategy config end to end.

Wiring, in order: load the pinned dataset and price panel; load the
walk-forward model bundles and validate them against the config (same
dataset version, walkforward scheme, probabilistic where the combination
needs it); derive the buy window from the intersection of every bundle's
fold years; simulate the strategy and the benchmark through the same
engine under identical cash flows; write the report + artifacts; log the
run — completed or failed — to the results store under scheme
``backtest``, so strategy configurations count as trials like any other.
"""

from __future__ import annotations

import traceback
from datetime import date
from pathlib import Path

import pandas as pd

from harness.dataset import Dataset
from harness.errors import ConfigError, DatasetValidationError
from harness.results import ResultsStore, git_sha, new_run_id
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_REPORTS, DEFAULT_RESULTS
from portfolio.config import BacktestConfig
from portfolio.crosssection import CrossSectionBuilder
from portfolio.engine import run_simulation
from portfolio.prices import (
    PricePanel,
    benchmark_price_source,
    stock_price_source,
)
from portfolio.report import (
    headline_table,
    max_drawdown,
    render_equity_plot,
    twr_cagr,
    write_backtest_report,
    xirr,
)
from portfolio.signals import (
    ModelSet,
    apply_filters,
    apply_min_score,
    combine_scores,
    validate_filter_columns,
)
from portfolio.strategy import BuyAndHoldTopK, build_strategy

#: Scheme recorded in the results store for backtest runs — distinct from
#: every split scheme, so backtests can never be mistaken for (or counted
#: among) per-cell walk-forward trials, but still accumulate their own
#: trial count.
BACKTEST_SCHEME = "backtest"


class CandidateFeed:
    """Scored, filtered, priced candidates for one rebalance date, plus
    the funnel diagnostics the report aggregates."""

    def __init__(
        self,
        builder: CrossSectionBuilder,
        model_set: ModelSet,
        config: BacktestConfig,
        stock_source,
    ):
        self.builder = builder
        self.model_set = model_set
        self.config = config
        self.stock_source = stock_source

    def __call__(self, when: pd.Timestamp):
        config = self.config
        xs = self.builder.at(when)
        scored = self.model_set.score(xs, int(when.year))
        cols = self.model_set.score_columns

        after_floor = apply_min_score(scored, cols, config.min_score)
        after_filters = apply_filters(after_floor, config.filters)
        after_inv = apply_filters(after_filters, config.investability)

        rows = after_inv.copy()
        rows["combined_score"] = combine_scores(rows, cols, config.combine)

        prices, kept = [], []
        for idx, permaticker in rows["permaticker"].items():
            quote = self.stock_source.asof(
                int(permaticker), when, config.max_quote_age_days
            )
            if quote is not None:
                prices.append(quote[0])
                kept.append(idx)
        priced = rows.loc[kept].copy()
        priced["price"] = prices
        priced = priced.rename(columns={"permaticker": "asset"})
        keep = ["asset", "ticker", "combined_score", "price"] + cols
        priced = priced[[c for c in keep if c in priced.columns]]
        priced = priced.sort_values(
            ["combined_score", "asset"], ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)

        diagnostics = {
            "n_cross_section": len(xs),
            "n_after_min_score": len(after_floor),
            "n_after_filters": len(after_filters),
            "n_after_investability": len(after_inv),
            "n_priced": len(priced),
        }
        return priced, diagnostics


def _derive_window(
    config: BacktestConfig, model_set: ModelSet, panel: PricePanel
) -> tuple[list[int], date, date, date]:
    """(buy_years, start, buy_end, valuation_end): buys are confined to
    the contiguous fold years every bundle covers, clipped by the config
    window; valuation may run to the panel's end."""
    common = model_set.common_fold_years()
    if not common:
        raise ConfigError(
            "the bundles share no walk-forward fold years — nothing to "
            "backtest"
        )
    years = [
        y
        for y in common
        if (config.start is None or y >= config.start.year)
        and (config.end is None or y <= config.end.year)
    ]
    if not years:
        raise ConfigError(
            f"the window [{config.start}, {config.end}] leaves no common "
            f"fold years (bundles share {common})"
        )
    if years != list(range(years[0], years[-1] + 1)):
        raise ConfigError(
            f"common fold years {years} are not contiguous; a monthly "
            "deposit schedule cannot skip years — narrow the window"
        )
    start = max(config.start or date(years[0], 1, 1), date(years[0], 1, 1))
    buy_end = min(config.end or date(years[-1], 12, 31), date(years[-1], 12, 31))
    panel_end = panel.trading_days[-1].date()
    valuation_end = config.valuation_end or panel_end
    if valuation_end > panel_end:
        valuation_end = panel_end
    if valuation_end < buy_end:
        raise ConfigError(
            f"valuation_end {valuation_end} precedes the last buy date "
            f"{buy_end}"
        )
    return years, start, buy_end, valuation_end


def run_backtest(
    config: BacktestConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    config_path: str = "",
) -> dict:
    """Run one backtest config. Returns a summary dict; raises after
    logging on failure."""
    store = ResultsStore(results_path)
    run_id = new_run_id()
    sha = git_sha()
    base_row = {
        "run_id": run_id,
        "experiment": config.name,
        "config_hash": config.config_hash,
        "config_path": config_path,
        "dataset_version": config.dataset_version,
        "git_sha": sha,
        "scheme": BACKTEST_SCHEME,
        "label": config.combine,
        "model": config.strategy,
    }

    try:
        dataset = Dataset(Path(data_root) / config.dataset_version)
        panel = PricePanel(Path(data_root) / config.prices_version)
        model_set = ModelSet(list(config.bundles))
        model_set.validate_against(config, dataset)
        validate_filter_columns(config.filters, dataset, "[[filters]]")
        validate_filter_columns(
            config.investability, dataset, "[[investability]]"
        )

        buy_years, start, buy_end, valuation_end = _derive_window(
            config, model_set, panel
        )
        buy_dates = panel.month_first_trading_days(start, buy_end)
        if not buy_dates:
            raise DatasetValidationError(
                f"price panel {panel.version} has no trading days in the "
                f"buy window [{start}, {buy_end}]"
            )
        all_dates = panel.month_first_trading_days(start, valuation_end)
        final_days = panel.trading_days[
            panel.trading_days <= pd.Timestamp(valuation_end)
        ]
        dates = sorted(set(all_dates) | {final_days[-1]})

        # coverage sanity: a survivor-only or truncated panel would
        # quietly bias everything downstream of it
        dataset_pts = set(
            int(p) for p in dataset.data["permaticker"].unique()
        )
        covered = len(dataset_pts & panel.permatickers)
        coverage = covered / len(dataset_pts) if dataset_pts else 0.0
        if coverage < 0.5:
            raise DatasetValidationError(
                f"price panel {panel.version} covers only {covered}/"
                f"{len(dataset_pts)} dataset permatickers — refusing to "
                "backtest against a panel that lost half the universe "
                "(survivorship suspicion)"
            )

        stock_source = stock_price_source(panel)
        feed = CandidateFeed(
            CrossSectionBuilder(dataset, config.max_staleness_days),
            model_set,
            config,
            stock_source,
        )
        strategy = build_strategy(
            config.strategy, config.top_k, config.weighting
        )
        strategy_result = run_simulation(
            dates=dates,
            buy_dates=set(buy_dates),
            deposit=config.monthly_cash,
            price_source=stock_source,
            strategy=strategy,
            candidates_fn=feed,
            cost_bps=config.cost_bps,
            delist_after_days=config.delist_after_days,
        )

        bench_source = benchmark_price_source(panel)
        bench_asset = panel.benchmark_name

        def bench_candidates(when: pd.Timestamp):
            quote = bench_source.asof(bench_asset, when, 0)
            if quote is None:
                raise DatasetValidationError(
                    f"benchmark has no print on trading day {when.date()}"
                )
            frame = pd.DataFrame(
                {"asset": [bench_asset], "combined_score": [1.0],
                 "price": [quote[0]]}
            )
            return frame, {}

        benchmark_result = run_simulation(
            dates=dates,
            buy_dates=set(buy_dates),
            deposit=config.monthly_cash,
            price_source=bench_source,
            strategy=BuyAndHoldTopK(top_k=1, weighting="equal"),
            candidates_fn=bench_candidates,
            cost_bps=config.benchmark_cost_bps,
            delist_after_days=config.delist_after_days,
        )

        reports_dir = Path(reports_dir)
        artifacts = _write_artifacts(
            reports_dir, config.name, strategy_result, benchmark_result
        )
        artifacts["equity_plot"] = render_equity_plot(
            strategy_result,
            benchmark_result,
            reports_dir / f"{config.name}_equity.png",
            f"{config.name} — strategy vs {panel.benchmark_name}, "
            "identical monthly deposits",
        )
        configurations_tried = _backtest_configurations_tried(
            store, config.dataset_version, config.config_hash
        )
        report_path = write_backtest_report(
            path=reports_dir / f"{config.name}.md",
            config=config,
            run_id=run_id,
            git_sha=sha,
            dataset=dataset,
            panel=panel,
            model_set=model_set,
            strategy_result=strategy_result,
            benchmark_result=benchmark_result,
            buy_years=buy_years,
            buy_end=pd.Timestamp(buy_end),
            valuation_end=pd.Timestamp(valuation_end),
            configurations_tried=configurations_tried,
            artifacts=artifacts,
        )

        headline = headline_table(strategy_result, benchmark_result)
        metrics = {
            "deposits": strategy_result.total_deposits,
            "final_value": strategy_result.final_value,
            "mwr_annualized": xirr(strategy_result.cashflows),
            "twr_cagr": twr_cagr(strategy_result.monthly),
            "max_drawdown": max_drawdown(
                strategy_result.monthly["twr_index"]
            ),
            "costs_paid": strategy_result.total_costs,
            "benchmark_final_value": benchmark_result.final_value,
            "benchmark_twr_cagr": twr_cagr(benchmark_result.monthly),
            "prices_version": panel.version,
            "buy_years": f"{buy_years[0]}-{buy_years[-1]}",
        }
        store.append(
            {
                **base_row,
                "status": "completed",
                "fold": f"{buy_years[0]}-{buy_years[-1]}",
                "n_test_rows": len(strategy_result.monthly),
                "metrics_json": {
                    k: v for k, v in metrics.items() if v is not None
                },
            }
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "buy_years": buy_years,
            "headline": headline,
            "report_path": report_path,
            "artifacts": artifacts,
            "strategy_result": strategy_result,
            "benchmark_result": benchmark_result,
        }
    except Exception as exc:
        store.append(
            {
                **base_row,
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        raise


def _write_artifacts(
    reports_dir: Path, name: str, strategy_result, benchmark_result
) -> dict:
    reports_dir.mkdir(parents=True, exist_ok=True)
    equity = strategy_result.monthly.merge(
        benchmark_result.monthly[["date", "total_value", "twr_index"]],
        on="date",
        suffixes=("", "_benchmark"),
    )
    equity_path = reports_dir / f"{name}_equity.csv"
    equity.to_csv(equity_path, index=False)
    trades_path = reports_dir / f"{name}_trades.csv"
    strategy_result.trades.to_csv(trades_path, index=False)
    rebalance_path = reports_dir / f"{name}_rebalances.csv"
    strategy_result.rebalance_log.to_csv(rebalance_path, index=False)
    return {
        "equity_curve": equity_path,
        "trades": trades_path,
        "rebalances": rebalance_path,
    }


def _backtest_configurations_tried(
    store: ResultsStore, dataset_version: str, current_hash: str
) -> int:
    """Distinct backtest configs ever run against this dataset version,
    counting the current one (it is appended to the store after the
    report is written)."""
    df = store.load()
    if df.empty:
        return 1
    sel = df[
        (df["scheme"] == BACKTEST_SCHEME)
        & (df["dataset_version"] == dataset_version)
    ]
    hashes = set(sel["config_hash"]) | {current_hash}
    return len(hashes)


def run_backtest_file(path: str | Path, **kwargs) -> dict:
    config = BacktestConfig.from_file(path)
    return run_backtest(config, config_path=str(path), **kwargs)


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Backtest a portfolio strategy config "
        "(experiments/portfolios/*.toml) against walk-forward fold "
        "models and a versioned price panel; the benchmark leg gets "
        "identical deposits and accounting."
    )
    parser.add_argument(
        "config", help="path to an experiments/portfolios/*.toml config"
    )
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    args = parser.parse_args(argv)
    try:
        summary = run_backtest_file(
            args.config,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
        )
    except Exception:
        traceback.print_exc()
        print("backtest FAILED (logged to the results store)")
        return 1
    years = summary["buy_years"]
    print(
        f"backtest {summary['run_id']} completed: buys {years[0]}–{years[-1]}"
    )
    print(summary["headline"].to_string(index=False))
    print(f"report: {summary['report_path']}")
    return 0


def main() -> None:
    import sys

    sys.exit(_main())
