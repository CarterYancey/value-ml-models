# Portfolio backtest — bt_nonloser_dd30_top10_cap2

- run `cff9198cadc1`, git `0f08aa1d44a6075fc2d6f5462389b7dbd5aef515`, backtest config `f84cc5238ba25a0c`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 643,694.32  | 451,694.32 | 10.53%         | 10.01%   | -46.57%      | 1,522.21   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 11.72%       | 7.09%         | 4.63%   | 12,000.00 | 120    | 0.7344          |
| 2006              | 19.56%       | 13.61%        | 5.94%   | 12,000.00 | 111    | 0.7644          |
| 2007              | -7.60%       | 4.40%         | -12.00% | 12,000.00 | 113    | 0.8205          |
| 2008 (GFC)        | -20.24%      | -34.30%       | 14.06%  | 12,000.00 | 118    | 0.8339          |
| 2009 (GFC)        | 24.67%       | 24.74%        | -0.07%  | 12,000.00 | 120    | 0.8024          |
| 2010              | 25.33%       | 14.30%        | 11.03%  | 12,000.00 | 120    | 0.7431          |
| 2011              | 15.90%       | 2.46%         | 13.44%  | 12,000.00 | 117    | 0.6799          |
| 2012              | 14.54%       | 17.09%        | -2.55%  | 12,000.00 | 120    | 0.6407          |
| 2013              | 13.61%       | 27.75%        | -14.14% | 12,000.00 | 120    | 0.6623          |
| 2014              | 24.57%       | 14.49%        | 10.07%  | 12,000.00 | 115    | 0.6838          |
| 2015              | 1.22%        | -0.11%        | 1.32%   | 12,000.00 | 118    | 0.6972          |
| 2016              | 17.29%       | 14.45%        | 2.84%   | 12,000.00 | 115    | 0.7236          |
| 2017              | 11.90%       | 21.63%        | -9.73%  | 12,000.00 | 116    | 0.7286          |
| 2018              | -1.88%       | -5.13%        | 3.25%   | 12,000.00 | 114    | 0.7252          |
| 2019              | 28.30%       | 32.30%        | -4.01%  | 12,000.00 | 107    | 0.7335          |
| 2020 (COVID)      | 1.08%        | 15.69%        | -14.61% | 12,000.00 | 110    | 0.7338          |
| 2021              | 26.17%       | 31.26%        | -5.08%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -6.23%       | -18.98%       | 12.75%  | 0.00      | 0      | —               |
| 2023              | 5.92%        | 26.71%        | -20.78% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

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
| Utilities              | 354  | 19.09% |
| Real Estate            | 269  | 14.51% |
| Consumer Defensive     | 256  | 13.81% |
| Industrials            | 239  | 12.89% |
| Energy                 | 207  | 11.17% |
| Healthcare             | 137  | 7.39%  |
| Financial Services     | 127  | 6.85%  |
| Consumer Cyclical      | 127  | 6.85%  |
| Communication Services | 60   | 3.24%  |
| Technology             | 59   | 3.18%  |
| Basic Materials        | 19   | 1.02%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2005 | 120  | 26     | 9      | Real Estate   | 20.00%        |
| 2006 | 111  | 21     | 8      | Real Estate   | 21.62%        |
| 2007 | 113  | 24     | 8      | Real Estate   | 21.24%        |
| 2008 | 118  | 20     | 8      | Real Estate   | 20.34%        |
| 2009 | 120  | 23     | 7      | Energy        | 20.00%        |
| 2010 | 120  | 19     | 9      | Utilities     | 20.00%        |
| 2011 | 117  | 23     | 8      | Utilities     | 20.51%        |
| 2012 | 120  | 27     | 8      | Energy        | 20.00%        |
| 2013 | 120  | 27     | 9      | Utilities     | 20.00%        |
| 2014 | 115  | 27     | 9      | Utilities     | 20.87%        |
| 2015 | 118  | 31     | 8      | Utilities     | 20.34%        |
| 2016 | 115  | 27     | 8      | Utilities     | 20.87%        |
| 2017 | 116  | 24     | 8      | Utilities     | 20.69%        |
| 2018 | 114  | 26     | 9      | Utilities     | 21.05%        |
| 2019 | 107  | 19     | 8      | Utilities     | 22.43%        |
| 2020 | 110  | 24     | 9      | Industrials   | 21.82%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | 4.15%          | 2.92%            | 55.83%  | 24.17%  | 3.33%         | 120  | -0.18%         | 0.28%            | 53.33%  | 35.00%  | 22.50%        |
| 2006     | 111  | 111  | -1.08%         | -0.53%           | 48.65%  | 18.92%  | 18.92%        | 111  | -2.12%         | -1.36%           | 41.44%  | 81.08%  | 23.42%        |
| 2007     | 113  | 113  | 4.27%          | 4.58%            | 59.29%  | 69.03%  | 8.85%         | 113  | 3.79%          | 2.74%            | 58.41%  | 54.87%  | 8.85%         |
| 2008     | 118  | 118  | 11.27%         | 11.10%           | 69.49%  | 71.19%  | 7.63%         | 118  | 6.74%          | 7.36%            | 75.42%  | 16.10%  | 8.47%         |
| 2009     | 120  | 120  | 3.59%          | 3.10%            | 60.83%  | 2.50%   | 0.00%         | 120  | 5.28%          | 4.73%            | 70.00%  | 0.00%   | 0.00%         |
| 2010     | 120  | 120  | 5.18%          | 3.93%            | 65.83%  | 9.17%   | 0.00%         | 120  | 1.78%          | 2.20%            | 59.17%  | 4.17%   | 4.17%         |
| 2011     | 117  | 117  | 10.19%         | 9.65%            | 72.65%  | 11.97%  | 2.56%         | 117  | -0.80%         | -0.20%           | 47.01%  | 3.42%   | 2.56%         |
| 2012     | 120  | 120  | 4.68%          | 4.94%            | 59.17%  | 8.33%   | 0.00%         | 120  | -1.37%         | -1.17%           | 45.00%  | 2.50%   | 2.50%         |
| 2013     | 120  | 120  | -8.89%         | -9.55%           | 29.17%  | 18.33%  | 0.00%         | 120  | 2.23%          | 1.51%            | 57.50%  | 2.50%   | 10.83%        |
| 2014     | 115  | 115  | 2.83%          | 7.19%            | 58.26%  | 28.70%  | 0.00%         | 115  | 2.66%          | 1.87%            | 57.39%  | 9.57%   | 6.09%         |
| 2015     | 118  | 118  | 10.82%         | 10.40%           | 75.42%  | 14.41%  | 5.93%         | 118  | -0.35%         | 0.57%            | 52.54%  | 10.17%  | 8.47%         |
| 2016     | 115  | 115  | -3.41%         | -4.49%           | 40.87%  | 8.70%   | 2.61%         | 115  | 0.17%          | 1.63%            | 55.65%  | 12.17%  | 2.61%         |
| 2017     | 116  | 116  | -5.25%         | -6.98%           | 34.48%  | 24.14%  | 0.00%         | 116  | -0.76%         | 0.28%            | 52.59%  | 10.34%  | 5.17%         |
| 2018     | 114  | 114  | 15.59%         | 13.93%           | 87.72%  | 5.26%   | 7.89%         | 114  | -2.81%         | -1.45%           | 36.84%  | 4.39%   | 7.89%         |
| 2019     | 107  | 107  | -12.02%        | -11.71%          | 18.69%  | 45.79%  | 1.87%         | 107  | -5.78%         | -4.46%           | 26.17%  | 21.50%  | 1.87%         |
| 2020     | 110  | 110  | -11.85%        | -18.35%          | 20.00%  | 24.55%  | 0.91%         | 110  | -2.51%         | -0.26%           | 47.27%  | 15.45%  | 6.36%         |
| all buys | 1854 | 1854 | 2.01%          | 2.05%            | 53.83%  | 23.84%  | 3.72%         | 1854 | 0.43%          | 0.43%            | 52.48%  | 17.37%  | 7.61%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -0.18%      | -7.05%            | 6.87%         | -1.90%       | 1.71%    | 35.00%    | 51.15%          | 43.21%     |
| 2006     | 111  | -2.12%      | -8.77%            | 6.65%         | -2.68%       | 0.56%    | 81.08%    | 77.11%          | 72.52%     |
| 2007     | 113  | 3.79%       | -6.21%            | 10.00%        | -0.87%       | 4.66%    | 54.87%    | 69.16%          | 64.46%     |
| 2008     | 118  | 6.74%       | -0.71%            | 7.45%         | 2.07%        | 4.68%    | 16.10%    | 41.68%          | 35.05%     |
| 2009     | 120  | 5.28%       | 1.15%             | 4.13%         | 1.07%        | 4.21%    | 0.00%     | 22.58%          | 15.52%     |
| 2010     | 120  | 1.78%       | -5.26%            | 7.04%         | -1.95%       | 3.73%    | 4.17%     | 26.07%          | 16.28%     |
| 2011     | 117  | -0.80%      | -7.27%            | 6.47%         | -1.82%       | 1.01%    | 3.42%     | 26.82%          | 13.68%     |
| 2012     | 120  | -1.37%      | -6.36%            | 4.99%         | -2.26%       | 0.89%    | 2.50%     | 26.57%          | 16.14%     |
| 2013     | 120  | 2.23%       | -10.20%           | 12.43%        | -3.88%       | 6.12%    | 2.50%     | 39.13%          | 25.51%     |
| 2014     | 115  | 2.66%       | -11.89%           | 14.56%        | -3.85%       | 6.52%    | 9.57%     | 41.94%          | 25.70%     |
| 2015     | 118  | -0.35%      | -10.90%           | 10.54%        | -5.11%       | 4.76%    | 10.17%    | 38.50%          | 27.86%     |
| 2016     | 115  | 0.17%       | -9.39%            | 9.56%         | -2.92%       | 3.10%    | 12.17%    | 35.30%          | 21.83%     |
| 2017     | 116  | -0.76%      | -14.92%           | 14.17%        | -5.03%       | 4.27%    | 10.34%    | 51.24%          | 33.21%     |
| 2018     | 114  | -2.81%      | -12.32%           | 9.51%         | -4.99%       | 2.19%    | 4.39%     | 37.83%          | 22.18%     |
| 2019     | 107  | -5.78%      | -12.56%           | 6.78%         | -4.53%       | -1.26%   | 21.50%    | 40.86%          | 22.52%     |
| 2020     | 110  | -2.51%      | -9.60%            | 7.10%         | -2.97%       | 0.46%    | 15.45%    | 40.64%          | 26.06%     |
| all buys | 1854 | 0.43%       | -8.31%            | 8.74%         | -2.58%       | 3.01%    | 17.37%    | 42.44%          | 29.92%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | 4.15%       | 5.55%             | -1.40%        | 5.24%        | -1.09%   | 24.17%    | 37.87%          | 31.75%     |
| 2006     | 111  | -1.08%      | -0.04%            | -1.04%        | 2.04%        | -3.12%   | 18.92%    | 37.68%          | 27.70%     |
| 2007     | 113  | 4.27%       | -6.64%            | 10.90%        | -0.39%       | 4.66%    | 69.03%    | 73.25%          | 68.48%     |
| 2008     | 118  | 11.27%      | 4.12%             | 7.14%         | 3.87%        | 7.39%    | 71.19%    | 74.19%          | 74.36%     |
| 2009     | 120  | 3.59%       | 29.46%            | -25.87%       | 14.40%       | -10.81%  | 2.50%     | 21.24%          | 17.44%     |
| 2010     | 120  | 5.18%       | 4.76%             | 0.41%         | 4.93%        | 0.24%    | 9.17%     | 32.69%          | 23.81%     |
| 2011     | 117  | 10.19%      | -7.12%            | 17.31%        | -2.92%       | 13.11%   | 11.97%    | 47.77%          | 37.26%     |
| 2012     | 120  | 4.68%       | 4.38%             | 0.30%         | 1.96%        | 2.72%    | 8.33%     | 26.20%          | 18.38%     |
| 2013     | 120  | -8.89%      | 0.88%             | -9.77%        | 1.56%        | -10.45%  | 18.33%    | 28.61%          | 15.98%     |
| 2014     | 115  | 2.83%       | -7.37%            | 10.20%        | -0.72%       | 3.55%    | 28.70%    | 47.98%          | 33.24%     |
| 2015     | 118  | 10.82%      | -9.74%            | 20.56%        | -3.73%       | 14.55%   | 14.41%    | 56.60%          | 47.69%     |
| 2016     | 115  | -3.41%      | 1.86%             | -5.27%        | -1.14%       | -2.27%   | 8.70%     | 30.74%          | 22.64%     |
| 2017     | 116  | -5.25%      | -1.22%            | -4.02%        | -1.62%       | -3.63%   | 24.14%    | 41.15%          | 31.08%     |
| 2018     | 114  | 15.59%      | -11.00%           | 26.59%        | -1.74%       | 17.33%   | 5.26%     | 54.83%          | 41.63%     |
| 2019     | 107  | -12.02%     | -9.48%            | -2.55%        | -5.18%       | -6.84%   | 45.79%    | 56.24%          | 43.68%     |
| 2020     | 110  | -11.85%     | 35.07%            | -46.92%       | 7.38%        | -19.23%  | 24.55%    | 22.83%          | 15.28%     |
| all buys | 1854 | 2.01%       | 1.88%             | 0.13%         | 1.56%        | 0.45%    | 23.84%    | 43.65%          | 34.30%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 58
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3151.2 (min 2666)
- mean with a tradable quote: 3077.4 (min 2636)
- forced delisting liquidations: 57 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 37 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_equity.png`
