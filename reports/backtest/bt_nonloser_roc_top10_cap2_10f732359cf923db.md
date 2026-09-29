# Portfolio backtest — bt_nonloser_roc_top10_cap2

- run `3946b00fa313`, git `52f2ccda31ca487d3a79a5e38c8ddb6dfcf6cf8f`, backtest config `10f732359cf923db`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 694,944.59  | 502,944.59 | 11.18%         | 9.65%    | -41.16%      | 1,045.13   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.35%        | 6.51%         | -4.17%  | 12,000.00 | 105    | -82.2714        |
| 2006              | 11.46%       | 12.67%        | -1.21%  | 12,000.00 | 117    | -86.4444        |
| 2007              | 2.84%        | 7.28%         | -4.44%  | 12,000.00 | 120    | -100.9375       |
| 2008 (GFC)        | -31.63%      | -43.21%       | 11.58%  | 12,000.00 | 120    | -85.5875        |
| 2009 (GFC)        | 35.30%       | 39.07%        | -3.77%  | 12,000.00 | 117    | -73.5043        |
| 2010              | 14.92%       | 10.86%        | 4.06%   | 12,000.00 | 120    | -85.2417        |
| 2011              | 8.64%        | 5.33%         | 3.32%   | 12,000.00 | 114    | -76.9167        |
| 2012              | 10.83%       | 15.60%        | -4.76%  | 12,000.00 | 109    | -79.6147        |
| 2013              | 28.54%       | 30.42%        | -1.88%  | 12,000.00 | 113    | -62.7124        |
| 2014              | 19.35%       | 16.18%        | 3.17%   | 12,000.00 | 108    | -53.8657        |
| 2015              | 10.73%       | 4.46%         | 6.27%   | 12,000.00 | 105    | -51.1143        |
| 2016              | 8.84%        | 6.48%         | 2.37%   | 12,000.00 | 103    | -68.3883        |
| 2017              | 19.55%       | 22.88%        | -3.33%  | 12,000.00 | 109    | -54.9862        |
| 2018              | 6.23%        | 7.53%         | -1.30%  | 12,000.00 | 111    | -69.0135        |
| 2019              | 17.50%       | 13.81%        | 3.69%   | 12,000.00 | 110    | -81.1500        |
| 2020 (COVID)      | 10.87%       | 19.77%        | -8.90%  | 12,000.00 | 102    | -61.4755        |
| 2021              | 13.39%       | 24.81%        | -11.42% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 5.88%        | -8.20%        | 14.08%  | 0.00      | 0      | —               |
| 2023              | 4.18%        | 19.00%        | -14.82% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 2 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 384  | 21.54% |
| Industrials            | 329  | 18.45% |
| Technology             | 314  | 17.61% |
| Healthcare             | 293  | 16.43% |
| Consumer Cyclical      | 217  | 12.17% |
| Communication Services | 69   | 3.87%  |
| Energy                 | 57   | 3.20%  |
| Financial Services     | 57   | 3.20%  |
| Basic Materials        | 51   | 2.86%  |
| Real Estate            | 9    | 0.50%  |
| Utilities              | 3    | 0.17%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 105  | 15     | 9      | Consumer Defensive | 22.86%        |
| 2006 | 117  | 23     | 8      | Consumer Defensive | 20.51%        |
| 2007 | 120  | 21     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 117  | 17     | 6      | Healthcare         | 20.51%        |
| 2010 | 120  | 19     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 114  | 18     | 7      | Consumer Defensive | 21.05%        |
| 2012 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2013 | 113  | 18     | 7      | Consumer Defensive | 21.24%        |
| 2014 | 108  | 14     | 6      | Consumer Defensive | 22.22%        |
| 2015 | 105  | 15     | 6      | Consumer Defensive | 22.86%        |
| 2016 | 103  | 16     | 8      | Consumer Defensive | 23.30%        |
| 2017 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2018 | 111  | 22     | 8      | Consumer Defensive | 21.62%        |
| 2019 | 110  | 21     | 8      | Consumer Defensive | 21.82%        |
| 2020 | 102  | 21     | 7      | Consumer Defensive | 23.53%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 108
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 26 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 9 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_equity.png`
