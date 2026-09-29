# Portfolio backtest — bt_nonloser_ey_top10_cap2

- run `fb24007a1cfa`, git `52f2ccda31ca487d3a79a5e38c8ddb6dfcf6cf8f`, backtest config `caba6955165f0c3a`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 493,413.21  | 301,413.21 | 8.28%          | 7.76%    | -49.43%      | 1,590.72   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 11.57%       | 6.51%         | 5.06%   | 12,000.00 | 111    | -106.2072       |
| 2006              | 10.35%       | 12.67%        | -2.32%  | 12,000.00 | 114    | -109.7412       |
| 2007              | -3.92%       | 7.28%         | -11.20% | 12,000.00 | 114    | -146.3728       |
| 2008 (GFC)        | -35.24%      | -43.21%       | 7.97%   | 12,000.00 | 120    | -158.7333       |
| 2009 (GFC)        | 34.47%       | 39.07%        | -4.60%  | 12,000.00 | 120    | -178.1375       |
| 2010              | 26.98%       | 10.86%        | 16.13%  | 12,000.00 | 120    | -117.8292       |
| 2011              | 8.37%        | 5.33%         | 3.05%   | 12,000.00 | 120    | -156.9167       |
| 2012              | 15.41%       | 15.60%        | -0.19%  | 12,000.00 | 120    | -165.1583       |
| 2013              | 22.63%       | 30.42%        | -7.79%  | 12,000.00 | 114    | -156.5482       |
| 2014              | 20.04%       | 16.18%        | 3.86%   | 12,000.00 | 118    | -140.8729       |
| 2015              | -0.64%       | 4.46%         | -5.10%  | 12,000.00 | 109    | -163.6514       |
| 2016              | 11.14%       | 6.48%         | 4.66%   | 12,000.00 | 120    | -184.3458       |
| 2017              | 16.41%       | 22.88%        | -6.47%  | 12,000.00 | 113    | -172.0619       |
| 2018              | 2.32%        | 7.53%         | -5.22%  | 12,000.00 | 113    | -171.7699       |
| 2019              | 12.71%       | 13.81%        | -1.10%  | 12,000.00 | 107    | -197.6822       |
| 2020 (COVID)      | -7.43%       | 19.77%        | -27.19% | 12,000.00 | 117    | -193.5641       |
| 2021              | 16.14%       | 24.81%        | -8.67%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 6.02%        | -8.20%        | 14.22%  | 0.00      | 0      | —               |
| 2023              | 1.58%        | 19.00%        | -17.42% | 0.00      | 0      | —               |

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
| Real Estate            | 335  | 18.11% |
| Utilities              | 294  | 15.89% |
| Energy                 | 249  | 13.46% |
| Industrials            | 186  | 10.05% |
| Communication Services | 181  | 9.78%  |
| Technology             | 120  | 6.49%  |
| Healthcare             | 120  | 6.49%  |
| Consumer Defensive     | 101  | 5.46%  |
| Financial Services     | 95   | 5.14%  |
| Consumer Cyclical      | 87   | 4.70%  |
| Basic Materials        | 82   | 4.43%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 111  | 18     | 8      | Real Estate            | 21.62%        |
| 2006 | 114  | 21     | 8      | Real Estate            | 21.05%        |
| 2007 | 114  | 24     | 10     | Real Estate            | 21.05%        |
| 2008 | 120  | 26     | 8      | Utilities              | 20.00%        |
| 2009 | 120  | 24     | 10     | Energy                 | 20.00%        |
| 2010 | 120  | 21     | 7      | Communication Services | 20.00%        |
| 2011 | 120  | 21     | 9      | Communication Services | 20.00%        |
| 2012 | 120  | 26     | 9      | Utilities              | 20.00%        |
| 2013 | 114  | 20     | 8      | Energy                 | 21.05%        |
| 2014 | 118  | 24     | 11     | Energy                 | 20.34%        |
| 2015 | 109  | 22     | 9      | Real Estate            | 22.02%        |
| 2016 | 120  | 22     | 10     | Real Estate            | 20.00%        |
| 2017 | 113  | 23     | 9      | Real Estate            | 21.24%        |
| 2018 | 113  | 23     | 10     | Real Estate            | 21.24%        |
| 2019 | 107  | 23     | 8      | Real Estate            | 22.43%        |
| 2020 | 117  | 22     | 10     | Real Estate            | 17.95%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 69
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 68 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 7 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_earnings_yield_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `34c363bc3e0c70b5`, train run `6403ce008496`, folds 2005–2020 (from `experiments/models/factor_earnings_yield_3y_6403ce008496`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_ey_top10_cap2_caba6955165f0c3a_equity.csv`
- trades: `reports/backtest/bt_nonloser_ey_top10_cap2_caba6955165f0c3a_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_ey_top10_cap2_caba6955165f0c3a_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_ey_top10_cap2_caba6955165f0c3a_equity.png`
