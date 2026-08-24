"""Phase 4 — portfolio construction & backtest (PLAN §4).

Turns saved walk-forward model bundles into a simulated portfolio and
measures it against a benchmark under identical cash flows. The design
constraints that shape everything here:

- **Deployed models are never backtested.** A deployment bundle is refit
  on all labeled history, so its scores have seen the backtest period.
  The backtest scores each trade date with the walk-forward *fold* model
  of that date's year (`ModelBundle.fold_models[year]`) — trained on an
  expanding window that ends, purged and embargoed, before the year
  begins. "Update the models at the end of each calendar year" is
  exactly the upstream fold calendar.
- **Historical inference datasets are not the mechanism.** The upstream
  inference directory is survivor-only by construction (data/manual.md
  §9) and must never be evaluated on. Point-in-time monthly
  cross-sections are built instead from `dataset.parquet`, which keeps
  every stock that later delisted: the latest *completed-quarter*
  median-kind snapshot per stock as of the trade date.
- **Buy decisions stay inside the walk-forward fold years.** A trade
  date needs its year's fold model, so the sealed-holdout years (which
  have no walkforward fold) can never host a buy decision. Valuation of
  already-held positions may run past the last fold year and says so in
  the report.
- **Prices are a separate versioned artifact** (`portfolio.prices`):
  the model dataset carries no price paths, and rebuilding them here
  from raw Sharadar tables is exactly the kind of easy join the
  contract bans. The `prices_vX.Y` panel is built upstream with the
  same survivorship discipline as the labels.
"""
