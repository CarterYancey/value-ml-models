# Backtesting: simulate the strategy without the deployed models

A deployment bundle is refit on all labeled history. Backtesting it
would score the past with a model that has seen it. `vml-backtest`
instead consumes the **walk-forward fold bundles** that `vml-run` saves.
The fold-Y models score a trade in year Y. Those models trained on
years before Y, purged and embargoed. That is exactly "update the
models at the end of each calendar year". One TOML in
`experiments/portfolios/` declares the whole strategy. See
`experiments/portfolios/allprob_top25_5models.toml` for the live
five-model AllProb screen. The TOML declares:

- the model bundles and how their scores combine, plus an optional
  per-model `min_score`. The combinations are `product` (AllProb),
  `mean`, `min`, `mean_rank` and `worst_rank`. `worst_rank` ranks a
  stock by its rank in the model that likes it least, with ties broken
  by the mean rank. It selects the stocks in every model's top N, for
  every N at once.
- declared column filters, such as `revenue_trend_20q > 0`. The
  harness validates them against the manifest's feature and rank
  groups, so a screen can never reference a label.
- a **mandatory investability statement**: `[[investability]]` filters
  or the explicit `investability = "none"`, which the report carries
  with a warning. `vml-backtest` refuses a bundle trained inside a `[[universe]]`
  (docs/experiments.md) unless the same filters are among the
  backtest's `[[investability]]` or `[[filters]]`. A model only
  scores stocks of the universe it learned from, and its year-end
  refits stay inside it.
- per-model floors via `[signal.min_scores]`. It maps a bundle name to
  a floor and overrides the scalar `min_score`.
- the strategy and the **mandatory `cost_bps`**. The strategy is
  `buy_and_hold` or `sell_below_criteria`. `buy_and_hold` makes a
  monthly deposit, buys the top K by combined score in whole shares,
  and never sells. The budget remainder stays in cash. Positions are
  score-weighted, equal-weighted or market-capitalization-weighted.
  `weighting = "marketcap"` weights by the snapshot's `log_marketcap`.
  `sell_below_criteria` buys the same way. In addition, it sells
  entirely any held position that fails the *sell criteria* at a
  rebalance, and the proceeds fund that month's buys. Falling out of the
  top K alone is never a sell. A holding whose snapshot aged out of the
  cross-section fails the criteria. The sell criteria default to the
  buy criteria. An optional `[sell]` section states a hysteresis band explicitly,
  with its own `min_score`, `min_scores` and `filters`. An example is
  a buy floor of 0.7 and a sell floor of 0.5.
  `[sell] max_rank_pct = 0.3` adds a criterion relative to the month's
  cross-section. The strategy sells a holding once it is no longer among the top
  30% of the month's buy candidates by combined score. The buy
  candidates are the stocks left after every buy screen. It also sells
  a holding that is not a candidate at all. A score floor means different
  things in different years, because fold models score hotter before a
  crash than after one. A `mean_rank` combination has no score to
  floor. The rank criterion works for both. The hysteresis is the gap
  between the top K that the strategy buys and the top share that it
  keeps. New
  portfolio-management ideas plug in as new `Strategy` classes without
  touching the engine.
- an optional **group cap**, `[portfolio] max_per_group = 2`. At each
  rebalance the engine walks the candidates in score order. It skips a
  stock once that many of the month's buys already share its group.
  The group is `group_column`, default `sector`, and a NULL group
  counts as one group. The cap applies to a month's buys, not to the
  book. The engine does not count the positions it already holds. It is a selection rule
  like the investability filter. The report states it, and it is part
  of the config hash when set. Every report, capped or not, carries
  "What was bought": the share of buys per group and the largest group
  of each year. A portfolio whose buys sit in one sector is one bet,
  however many stocks it holds.
- the `model_update` policy for trade years past a bundle's last fold.
  The fold calendar stops where test labels stop being observable, but
  a live portfolio keeps trading. `"refit"`, the default, simulates the
  real year-end procedure. It refits the bundle's config on every row
  whose label window was observable by Jan 1 of the trade year. That
  is manual.md §4 rule 7 applied point-in-time. The refit reads no
  split tags and keeps back no rows for evaluation. `"frozen"` keeps
  the last fold's model. The engine caches refits on disk in
  `experiments/models/refits/`, which is git-ignored. The cache key is
  the train config hash, the dataset version, the trade year and the
  label lag. Re-running with different strategy parameters therefore
  reuses the identical models. The report's refit appendix marks each
  row `fit` or `cache`. `--refit-cache DIR` moves the cache, and
  `--no-refit-cache` bypasses it. Reports flag that these years overlap
  the sealed holdout era. That flag is context and never a selection
  signal.
- the simulation window. By default buys start at the latest first-fold
  year across the bundles. They continue, deposits included, to the
  price panel's end. `[window] start` trims the early thin years.

Monthly point-in-time cross-sections come from `dataset.parquet`
itself: the latest completed-quarter median-kind snapshot per stock,
with a cap on staleness. They do **not** come from historical inference
directories, which are survivor-only by construction. The benchmark
leg (SPY) runs through the same engine with identical deposits and
accounting.

Every report carries **"What the buys went on to do"**. It reads each
buy on its own over the 1 and 3 years after its trade date. The
returns come from the price panel, against the benchmark over the same
dates. It reports by buy year and pooled. The statistics are the mean
and median excess return a year, the share beating the benchmark, and
the share losing money. It also gives the share that stopped printing
early. A stock that stops
printing exits at its final print, and the proceeds ride the benchmark
to the horizon. The ledger records the pooled row as `buy_mean_excess_3y`,
`buy_beat_3y` and so on. Read it beside the headline. Time-weighted
return gives the small early portfolio the weight of the large late
one. Money-weighted return does the reverse. Two strategies can swap
places between them. One buy, one vote says whether the selection was
good in the early years and in the late ones. It excludes costs and
sizing, so it is a reading of the selection, not of the portfolio.

Under it, **"Against the stocks they were chosen from"** gives the
same reading for every candidate of every rebalance. A candidate is
each stock that passed the screens and had a quote. The section
reports by buy year and pooled, and sets the buys beside two
references:

- *all candidates*, equal-weighted. Its columns are
  `candidates_excess` and `vs_candidates`.
- *same-size peers*: for each buy, the candidates of its own rebalance
  in its own 5% band of `log_marketcap_rank`. Its columns are
  `peers_excess` and `vs_peers`. This reference is absent when the
  dataset has no such column.

Read `vs_peers` for the selection. The average small stock lags a
capitalization-weighted benchmark by a wide margin in every period.
On `dataset_v1.4`, the smaller half of the investable stocks lagged
the benchmark by 12 to 33 points a year over three years. That
measurement covers 2005 to 2026.
A ranking that merely prefers large companies therefore beats "all
candidates" without choosing well among them. When `candidates_excess`
and `peers_excess` are themselves far below zero, the benchmark outran
equal-weighted stocks of every kind. That is a statement about the
benchmark and the period, which no equal-weighted selection from the
universe could have escaped. The ledger records the pooled rows as
`ref_vs_peers_3y`, `ref_vs_candidates_3y`, `ref_peers_excess_3y` and
so on.

A run writes its output to `reports/backtest/<name>_<config-hash>.*`.
The output is the report, the equity, trades and rebalances CSVs, and
the equity plot. Trades carry tickers, per-model scores, and realized
profit on sells. The report leads with money-weighted and
time-weighted results, then gives the per-year era slice with crash
years tagged, and the defensive-hypothesis check. A year runs from the
first trading day of January to the first of the next January. The
engine values the portfolio monthly, and it counts a month's return in
the year the month starts in. Reports written before 2026-10-01 counted it
in the year it ended in, so their "2022" is December 2021 to December
2022. The ledger `experiments/results.csv` records each run under scheme
`backtest`.

```sh
# 1. train walk-forward bundles for the models the strategy uses
uv run vml-run experiments/<model-config>.toml
# 2. point the portfolio config's `bundles` at those directories, then
uv run vml-backtest experiments/portfolios/allprob_top25_5models.toml
```

Backtests additionally require a versioned **price panel** at
`data/datasets/prices_vX.Y/`. It holds three files. `prices.parquet`
holds daily total-return adjusted closes per permaticker,
survivorship-free through each stock's final print.
`benchmark.parquet` holds SPY, whose dates define the trading calendar.
`manifest.json` describes the panel. Build it from the upstream repo's
raw Sharadar tables, the same `SEP.closeadj` / `SFP` source that the
labels come from. Create a symlink to the raw directory, as for the
datasets:

```sh
ln -s ~/radarash-dataset/data/raw data/raw
uv run python scripts/build_price_panel.py data/raw dataset_v1.1 --out-version prices_v1.0
```

This is the one sanctioned read of raw Sharadar tables in this repo.
The panel carries `(permaticker, date, closeadj)` outcome paths only,
and never features. The consumer contract in `src/portfolio/prices.py`
validates it on load.
