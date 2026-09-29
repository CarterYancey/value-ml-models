# Portfolio backtest — bt_cagr10_dd20_top10_cap2

- run `88eaafcc45da`, git `499884bdad9045e076ea5f4cef753aa1cbb4473f`, backtest config `dfc6f0cfdade59a6`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 605,181.78  | 413,181.78 | 10.01%         | 8.73%    | -49.01%      | 1,460.91   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 3.62%        | 6.51%         | -2.90%  | 12,000.00 | 111    | 0.4593          |
| 2006              | 12.12%       | 12.67%        | -0.55%  | 12,000.00 | 111    | 0.4962          |
| 2007              | -7.10%       | 7.28%         | -14.39% | 12,000.00 | 112    | 0.5732          |
| 2008 (GFC)        | -31.61%      | -43.21%       | 11.60%  | 12,000.00 | 118    | 0.5764          |
| 2009 (GFC)        | 30.38%       | 39.07%        | -8.69%  | 12,000.00 | 120    | 0.5112          |
| 2010              | 28.65%       | 10.86%        | 17.79%  | 12,000.00 | 120    | 0.4525          |
| 2011              | 12.22%       | 5.33%         | 6.89%   | 12,000.00 | 120    | 0.3924          |
| 2012              | 17.89%       | 15.60%        | 2.29%   | 12,000.00 | 119    | 0.3552          |
| 2013              | 20.38%       | 30.42%        | -10.04% | 12,000.00 | 120    | 0.3875          |
| 2014              | 21.03%       | 16.18%        | 4.84%   | 12,000.00 | 114    | 0.4105          |
| 2015              | 1.53%        | 4.46%         | -2.93%  | 12,000.00 | 116    | 0.4251          |
| 2016              | 10.68%       | 6.48%         | 4.20%   | 12,000.00 | 117    | 0.4488          |
| 2017              | 16.18%       | 22.88%        | -6.70%  | 12,000.00 | 110    | 0.4614          |
| 2018              | 8.48%        | 7.53%         | 0.94%   | 12,000.00 | 112    | 0.4599          |
| 2019              | 15.39%       | 13.81%        | 1.58%   | 12,000.00 | 109    | 0.4527          |
| 2020 (COVID)      | 3.30%        | 19.77%        | -16.46% | 12,000.00 | 102    | 0.4640          |
| 2021              | 15.52%       | 24.81%        | -9.29%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 3.94%        | -8.20%        | 12.13%  | 0.00      | 0      | —               |
| 2023              | 1.23%        | 19.00%        | -17.77% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
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
| Utilities              | 363  | 19.83% |
| Real Estate            | 305  | 16.66% |
| Energy                 | 219  | 11.96% |
| Industrials            | 214  | 11.69% |
| Consumer Defensive     | 189  | 10.32% |
| Consumer Cyclical      | 148  | 8.08%  |
| Healthcare             | 109  | 5.95%  |
| Technology             | 92   | 5.02%  |
| Communication Services | 87   | 4.75%  |
| Basic Materials        | 63   | 3.44%  |
| Financial Services     | 42   | 2.29%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2005 | 111  | 19     | 9      | Real Estate   | 21.62%        |
| 2006 | 111  | 20     | 8      | Real Estate   | 21.62%        |
| 2007 | 112  | 14     | 8      | Real Estate   | 21.43%        |
| 2008 | 118  | 22     | 6      | Real Estate   | 20.34%        |
| 2009 | 120  | 30     | 9      | Energy        | 20.00%        |
| 2010 | 120  | 25     | 9      | Real Estate   | 20.00%        |
| 2011 | 120  | 30     | 10     | Real Estate   | 20.00%        |
| 2012 | 119  | 25     | 9      | Real Estate   | 20.17%        |
| 2013 | 120  | 31     | 9      | Utilities     | 20.00%        |
| 2014 | 114  | 28     | 9      | Utilities     | 21.05%        |
| 2015 | 116  | 30     | 10     | Utilities     | 20.69%        |
| 2016 | 117  | 27     | 9      | Utilities     | 20.51%        |
| 2017 | 110  | 30     | 8      | Utilities     | 21.82%        |
| 2018 | 112  | 30     | 8      | Utilities     | 21.43%        |
| 2019 | 109  | 29     | 8      | Utilities     | 22.02%        |
| 2020 | 102  | 34     | 8      | Utilities     | 23.53%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 69
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 49 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 5 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_cagr10_dd20_3y` — label `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` (3y), model `random_forest`, config `8b3d0dc22175d8e7`, train run `df10b2ee396f`, folds 2005–2020 (from `experiments/models/forest_cagr10_dd20_3y_df10b2ee396f`)

### Artifacts

- equity_curve: `reports/backtest/bt_cagr10_dd20_top10_cap2_dfc6f0cfdade59a6_equity.csv`
- trades: `reports/backtest/bt_cagr10_dd20_top10_cap2_dfc6f0cfdade59a6_trades.csv`
- rebalances: `reports/backtest/bt_cagr10_dd20_top10_cap2_dfc6f0cfdade59a6_rebalances.csv`
- equity_plot: `reports/backtest/bt_cagr10_dd20_top10_cap2_dfc6f0cfdade59a6_equity.png`
