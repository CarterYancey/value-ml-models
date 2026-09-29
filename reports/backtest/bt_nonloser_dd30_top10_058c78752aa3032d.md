# Portfolio backtest — bt_nonloser_dd30_top10

- run `f9c5ed7f2cf9`, git `499884bdad9045e076ea5f4cef753aa1cbb4473f`, backtest config `058c78752aa3032d`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 518,612.33  | 326,612.33 | 8.70%          | 7.90%    | -63.43%      | 1,441.59   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 11.00%       | 6.51%         | 4.49%   | 12,000.00 | 120    | 0.7742          |
| 2006              | 34.02%       | 12.67%        | 21.35%  | 12,000.00 | 120    | 0.8098          |
| 2007              | -20.71%      | 7.28%         | -27.99% | 12,000.00 | 118    | 0.8447          |
| 2008 (GFC)        | -44.65%      | -43.21%       | -1.45%  | 12,000.00 | 118    | 0.8381          |
| 2009 (GFC)        | 45.44%       | 39.07%        | 6.37%   | 12,000.00 | 120    | 0.8092          |
| 2010              | 27.05%       | 10.86%        | 16.19%  | 12,000.00 | 120    | 0.7477          |
| 2011              | 14.25%       | 5.33%         | 8.93%   | 12,000.00 | 120    | 0.6849          |
| 2012              | 16.32%       | 15.60%        | 0.72%   | 12,000.00 | 120    | 0.6463          |
| 2013              | 12.21%       | 30.42%        | -18.21% | 12,000.00 | 120    | 0.6683          |
| 2014              | 23.63%       | 16.18%        | 7.44%   | 12,000.00 | 120    | 0.6875          |
| 2015              | 3.60%        | 4.46%         | -0.87%  | 12,000.00 | 118    | 0.6993          |
| 2016              | 9.99%        | 6.48%         | 3.51%   | 12,000.00 | 118    | 0.7269          |
| 2017              | 17.06%       | 22.88%        | -5.81%  | 12,000.00 | 112    | 0.7313          |
| 2018              | 5.04%        | 7.53%         | -2.49%  | 12,000.00 | 119    | 0.7314          |
| 2019              | 15.43%       | 13.81%        | 1.62%   | 12,000.00 | 115    | 0.7386          |
| 2020 (COVID)      | -0.37%       | 19.77%        | -20.13% | 12,000.00 | 114    | 0.7377          |
| 2021              | 14.48%       | 24.81%        | -10.33% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.79%        | -8.20%        | 12.99%  | 0.00      | 0      | —               |
| 2023              | -1.54%       | 19.00%        | -20.54% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Utilities              | 924  | 48.84% |
| Real Estate            | 515  | 27.22% |
| Consumer Defensive     | 138  | 7.29%  |
| Energy                 | 116  | 6.13%  |
| Industrials            | 111  | 5.87%  |
| Healthcare             | 47   | 2.48%  |
| Consumer Cyclical      | 21   | 1.11%  |
| Technology             | 9    | 0.48%  |
| Communication Services | 6    | 0.32%  |
| Financial Services     | 3    | 0.16%  |
| Basic Materials        | 2    | 0.11%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 120  | 23     | 1      | Real Estate        | 100.00%       |
| 2006 | 120  | 28     | 1      | Real Estate        | 100.00%       |
| 2007 | 118  | 29     | 4      | Real Estate        | 92.37%        |
| 2008 | 118  | 21     | 4      | Real Estate        | 45.76%        |
| 2009 | 120  | 25     | 3      | Utilities          | 77.50%        |
| 2010 | 120  | 20     | 4      | Utilities          | 80.00%        |
| 2011 | 120  | 24     | 4      | Utilities          | 65.00%        |
| 2012 | 120  | 27     | 4      | Utilities          | 57.50%        |
| 2013 | 120  | 29     | 8      | Utilities          | 55.00%        |
| 2014 | 120  | 24     | 5      | Utilities          | 65.00%        |
| 2015 | 118  | 30     | 7      | Consumer Defensive | 27.97%        |
| 2016 | 118  | 28     | 6      | Utilities          | 61.02%        |
| 2017 | 112  | 20     | 6      | Utilities          | 45.54%        |
| 2018 | 119  | 26     | 6      | Utilities          | 73.11%        |
| 2019 | 115  | 23     | 3      | Utilities          | 83.48%        |
| 2020 | 114  | 25     | 5      | Utilities          | 61.40%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 25
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 52 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 3 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_058c78752aa3032d_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_058c78752aa3032d_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_058c78752aa3032d_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_058c78752aa3032d_equity.png`
