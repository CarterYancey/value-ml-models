# Backtesting: simulate the strategy without the deployed models

A deployment bundle is refit on all labeled history, so backtesting it
would score the past with a model that has seen it. `vml-backtest`
instead consumes the **walk-forward fold bundles** `vml-run` saves: a
trade in year Y is scored by the fold-Y models — trained, purged, and
embargoed on years before Y — which is exactly "update the models at the
end of each calendar year". One TOML in `experiments/portfolios/`
declares the whole strategy (see
`experiments/portfolios/allprob_top25_5models.toml` for the live
five-model AllProb screen):

- the model bundles and how their scores combine (`product` = AllProb,
  `mean`, `min`, `mean_rank`) plus an optional per-model `min_score`;
- declared column filters (e.g. `revenue_trend_20q > 0`) — validated
  against the manifest's feature/rank groups, so a screen can never
  reference a label;
- a **mandatory investability statement**: `[[investability]]` filters or
  the explicit `investability = "none"` (reported with a warning). A
  bundle trained inside a `[[universe]]` (docs/experiments.md) is
  refused unless the same filters are among the backtest's
  `[[investability]]` or `[[filters]]`: a model only scores stocks of
  the universe it learned from, and its year-end refits stay inside it;
- per-model floors via `[signal.min_scores]` (bundle name → floor,
  overriding the scalar `min_score`);
- the strategy and **mandatory `cost_bps`**: `buy_and_hold` (monthly
  deposit, buy top-K by combined score, score-, equal- or
  market-capitalization-weighted (`weighting = "marketcap"`, from the
  snapshot's `log_marketcap`), whole
  shares — the budget remainder stays in cash — never sell) or
  `sell_below_criteria` (same buying, plus: any held position failing
  the *sell criteria* at a rebalance is sold entirely, proceeds funding
  that month's buys — falling out of the top-K alone is never a sell,
  and a holding whose snapshot aged out of the cross-section fails).
  The sell criteria default to the buy criteria; an optional `[sell]`
  section (own `min_score`/`min_scores`/`filters`) states a hysteresis
  band explicitly (buy > 0.7, sell < 0.5). `[sell] max_rank_pct = 0.3`
  adds a criterion relative to the month's cross-section: a holding is
  sold once it is no longer among the top 30% of the month's buy
  candidates by combined score (after every buy screen), or is not a
  candidate at all. A score floor means different things in different
  years (fold models score hotter before a crash than after one) and a
  `mean_rank` combination has no score to floor; the rank criterion
  works for both, with the band between the top K that is bought and
  the top share that is kept as the hysteresis. New portfolio-management
  ideas plug in as new `Strategy` classes without touching the engine;
- an optional **group cap**, `[portfolio] max_per_group = 2`: at each
  rebalance the candidates are walked in score order and a stock is
  skipped once that many of the month's buys already share its group
  (`group_column`, default `sector`; a NULL group counts as one group).
  It caps a month's buys, not the book: what is already held is not
  counted. A selection rule like the investability filter, stated in
  the report and part of the config hash when set. Every report, capped
  or not, carries "What was bought": the share of buys per group and
  the largest group of each year, because a portfolio whose buys sit
  in one sector is one bet however many stocks it holds;
- the `model_update` policy for trade years past a bundle's last fold
  (the fold calendar stops where test labels stop being observable, but
  a live portfolio keeps trading): `"refit"` (default) simulates the
  real year-end procedure — the bundle's config refit on every row
  whose label window was observable by Jan 1 of the trade year
  (manual.md §4 rule 7 applied point-in-time; no split tags read, no
  test set) — while `"frozen"` keeps the last fold's model. Refits are
  cached on disk (`experiments/models/refits/`, git-ignored) keyed by
  (train config hash, dataset version, trade year, label lag), so
  re-running with different strategy parameters reuses the identical
  models — the report's refit appendix marks each row `fit` or `cache`
  (`--refit-cache DIR` moves the cache, `--no-refit-cache` bypasses
  it). Reports flag that these years overlap the sealed holdout era:
  context, never a selection signal;
- the simulation window (defaults: buys start at the latest first-fold
  year across the bundles and continue, deposits included, to the price
  panel's end; `[window] start` trims the early thin years).

Monthly point-in-time cross-sections come from `dataset.parquet` itself
(latest completed-quarter median-kind snapshot per stock, staleness-
capped) — **not** from historical inference directories, which are
survivor-only by construction. The benchmark leg (SPY) runs through the
same engine with identical deposits and accounting.

Every report carries **"What the buys went on to do"**: each buy read
on its own over the 1 and 3 years after its trade date, from the price
panel, against the benchmark over the same dates, by buy year and
pooled (mean and median excess return a year, share beating the
benchmark, share losing money, share that stopped printing early). A
stock that stops printing exits at its final print and the proceeds
ride the benchmark to the horizon. The pooled row is logged
(`buy_mean_excess_3y`, `buy_beat_3y`, ...). Read it beside the
headline: time-weighted return gives the small early portfolio the
weight of the large late one, money-weighted return the reverse, and
two strategies can swap places between them; one buy, one vote says
whether the selection was good in the early years and in the late
ones. It excludes costs and sizing, so it is a reading of the
selection, not of the portfolio.

Reports land in
`reports/backtest/<name>_<config-hash>.*` (report, equity/trades/
rebalances CSVs — trades carry tickers, per-model scores, and realized
profit on sells — and the equity plot), lead with money- and
time-weighted results, the per-year era slice with crash years tagged,
and the defensive-hypothesis check; runs are logged to
`experiments/results.csv` under scheme `backtest`.

```sh
# 1. train walk-forward bundles for the models the strategy uses
uv run vml-run experiments/<model-config>.toml
# 2. point the portfolio config's `bundles` at those directories, then
uv run vml-backtest experiments/portfolios/allprob_top25_5models.toml
```

Backtests additionally require a versioned **price panel**
`data/datasets/prices_vX.Y/` (`prices.parquet` — daily total-return
adjusted closes per permaticker, survivorship-free through each stock's
final print; `benchmark.parquet` — SPY, whose dates define the trading
calendar; `manifest.json`). Build it from the upstream repo's raw
Sharadar tables — the same `SEP.closeadj` / `SFP` source the labels are
computed from — with the raw directory symlinked like the datasets:

```sh
ln -s ~/radarash-dataset/data/raw data/raw
uv run python scripts/build_price_panel.py data/raw dataset_v1.1 --out-version prices_v1.0
```

This is the one sanctioned read of raw Sharadar tables in this repo:
the panel carries `(permaticker, date, closeadj)` outcome paths only —
never features — and the consumer contract in `src/portfolio/prices.py`
validates it on load.
