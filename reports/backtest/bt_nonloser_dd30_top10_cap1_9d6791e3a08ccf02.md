# Portfolio backtest — bt_nonloser_dd30_top10_cap1

- run `d91c8739af90`, git `499884bdad9045e076ea5f4cef753aa1cbb4473f`, backtest config `9d6791e3a08ccf02`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 650,979.56  | 458,979.56 | 10.63%         | 9.69%    | -42.75%      | 1,264.47   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 5.93%        | 6.51%         | -0.58%  | 12,000.00 | 117    | 0.6981          |
| 2006              | 12.50%       | 12.67%        | -0.17%  | 12,000.00 | 120    | 0.7225          |
| 2007              | 1.04%        | 7.28%         | -6.24%  | 12,000.00 | 117    | 0.7976          |
| 2008 (GFC)        | -28.92%      | -43.21%       | 14.29%  | 12,000.00 | 119    | 0.8192          |
| 2009 (GFC)        | 29.52%       | 39.07%        | -9.55%  | 12,000.00 | 120    | 0.7938          |
| 2010              | 24.17%       | 10.86%        | 13.31%  | 12,000.00 | 120    | 0.7370          |
| 2011              | 10.49%       | 5.33%         | 5.17%   | 12,000.00 | 117    | 0.6715          |
| 2012              | 16.93%       | 15.60%        | 1.33%   | 12,000.00 | 120    | 0.6300          |
| 2013              | 19.57%       | 30.42%        | -10.85% | 12,000.00 | 120    | 0.6520          |
| 2014              | 19.98%       | 16.18%        | 3.80%   | 12,000.00 | 112    | 0.6780          |
| 2015              | 8.51%        | 4.46%         | 4.05%   | 12,000.00 | 111    | 0.6897          |
| 2016              | 7.85%        | 6.48%         | 1.38%   | 12,000.00 | 115    | 0.7144          |
| 2017              | 19.99%       | 22.88%        | -2.88%  | 12,000.00 | 116    | 0.7224          |
| 2018              | 8.73%        | 7.53%         | 1.20%   | 12,000.00 | 115    | 0.7161          |
| 2019              | 18.44%       | 13.81%        | 4.63%   | 12,000.00 | 108    | 0.7254          |
| 2020 (COVID)      | 7.06%        | 19.77%        | -12.70% | 12,000.00 | 102    | 0.7290          |
| 2021              | 13.76%       | 24.81%        | -11.05% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 0.04%        | -8.20%        | 8.23%   | 0.00      | 0      | —               |
| 2023              | 2.89%        | 19.00%        | -16.11% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 1 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Utilities              | 192  | 10.38% |
| Consumer Defensive     | 189  | 10.22% |
| Communication Services | 186  | 10.06% |
| Industrials            | 183  | 9.90%  |
| Healthcare             | 183  | 9.90%  |
| Real Estate            | 181  | 9.79%  |
| Consumer Cyclical      | 178  | 9.63%  |
| Technology             | 174  | 9.41%  |
| Basic Materials        | 161  | 8.71%  |
| Energy                 | 144  | 7.79%  |
| Financial Services     | 78   | 4.22%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 117  | 26     | 11     | Real Estate        | 10.26%        |
| 2006 | 120  | 23     | 11     | Real Estate        | 10.00%        |
| 2007 | 117  | 23     | 11     | Real Estate        | 10.26%        |
| 2008 | 119  | 21     | 10     | Real Estate        | 10.08%        |
| 2009 | 120  | 25     | 10     | Energy             | 10.00%        |
| 2010 | 120  | 23     | 10     | Utilities          | 10.00%        |
| 2011 | 117  | 23     | 10     | Real Estate        | 10.26%        |
| 2012 | 120  | 30     | 10     | Real Estate        | 10.00%        |
| 2013 | 120  | 30     | 11     | Utilities          | 10.00%        |
| 2014 | 112  | 26     | 11     | Utilities          | 10.71%        |
| 2015 | 111  | 32     | 11     | Utilities          | 10.81%        |
| 2016 | 115  | 25     | 10     | Consumer Defensive | 10.43%        |
| 2017 | 116  | 22     | 10     | Consumer Defensive | 10.34%        |
| 2018 | 115  | 29     | 11     | Utilities          | 10.43%        |
| 2019 | 108  | 19     | 10     | Utilities          | 11.11%        |
| 2020 | 102  | 24     | 11     | Utilities          | 11.76%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 55
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 55 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 6 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_cap1_9d6791e3a08ccf02_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_cap1_9d6791e3a08ccf02_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_cap1_9d6791e3a08ccf02_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_cap1_9d6791e3a08ccf02_equity.png`
