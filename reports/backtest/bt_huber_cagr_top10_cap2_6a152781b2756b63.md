# Portfolio backtest — bt_huber_cagr_top10_cap2

- run `1f06df22adb3`, git `c2396a8acc1e9c5202ba78cd6d7d486c92fc13be`, backtest config `6a152781b2756b63`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 663,060.47  | 471,060.47 | 10.78%         | 9.39%    | -60.64%      | 2,209.02   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.58%        | 7.09%         | -4.51%  | 12,000.00 | 114    | -6.9386         |
| 2006              | 25.46%       | 13.61%        | 11.85%  | 12,000.00 | 119    | -12.3277        |
| 2007              | -5.18%       | 4.40%         | -9.58%  | 12,000.00 | 111    | -8.5676         |
| 2008 (GFC)        | -44.74%      | -34.30%       | -10.44% | 12,000.00 | 117    | -7.2564         |
| 2009 (GFC)        | 60.49%       | 24.74%        | 35.75%  | 12,000.00 | 120    | -7.5000         |
| 2010              | 33.29%       | 14.30%        | 19.00%  | 12,000.00 | 120    | -8.0667         |
| 2011              | -5.03%       | 2.46%         | -7.49%  | 12,000.00 | 118    | -6.0169         |
| 2012              | 22.08%       | 17.09%        | 4.99%   | 12,000.00 | 120    | -6.3000         |
| 2013              | 39.53%       | 27.75%        | 11.78%  | 12,000.00 | 119    | -6.2941         |
| 2014              | 3.95%        | 14.49%        | -10.55% | 12,000.00 | 120    | -5.9500         |
| 2015              | -5.92%       | -0.11%        | -5.81%  | 12,000.00 | 117    | -6.4615         |
| 2016              | 30.78%       | 14.45%        | 16.33%  | 12,000.00 | 120    | -6.3000         |
| 2017              | 14.08%       | 21.63%        | -7.55%  | 12,000.00 | 120    | -6.0750         |
| 2018              | -6.23%       | -5.13%        | -1.09%  | 12,000.00 | 120    | -6.2750         |
| 2019              | 21.98%       | 32.30%        | -10.32% | 12,000.00 | 120    | -6.1083         |
| 2020 (COVID)      | 8.44%        | 15.69%        | -7.25%  | 12,000.00 | 120    | -6.5000         |
| 2021              | 30.31%       | 31.26%        | -0.94%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -14.16%      | -18.98%       | 4.82%   | 0.00      | 0      | —               |
| 2023              | 16.22%       | 26.71%        | -10.49% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `mean_rank`

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
| Technology             | 342  | 18.05% |
| Industrials            | 300  | 15.83% |
| Consumer Cyclical      | 279  | 14.72% |
| Healthcare             | 221  | 11.66% |
| Energy                 | 159  | 8.39%  |
| Basic Materials        | 138  | 7.28%  |
| Consumer Defensive     | 114  | 6.02%  |
| Real Estate            | 111  | 5.86%  |
| Communication Services | 105  | 5.54%  |
| Financial Services     | 90   | 4.75%  |
| Utilities              | 30   | 1.58%  |
| unknown                | 6    | 0.32%  |

| year | buys | stocks | groups | largest_group     | largest_share |
| ---- | ---- | ------ | ------ | ----------------- | ------------- |
| 2005 | 114  | 30     | 8      | Consumer Cyclical | 21.05%        |
| 2006 | 119  | 31     | 10     | Industrials       | 20.17%        |
| 2007 | 111  | 27     | 7      | Technology        | 21.62%        |
| 2008 | 117  | 27     | 6      | Technology        | 20.51%        |
| 2009 | 120  | 34     | 12     | Technology        | 20.00%        |
| 2010 | 120  | 33     | 10     | Technology        | 20.00%        |
| 2011 | 118  | 36     | 10     | Industrials       | 17.80%        |
| 2012 | 120  | 32     | 10     | Technology        | 20.00%        |
| 2013 | 119  | 32     | 9      | Technology        | 20.17%        |
| 2014 | 120  | 33     | 11     | Technology        | 20.00%        |
| 2015 | 117  | 34     | 9      | Technology        | 20.51%        |
| 2016 | 120  | 37     | 10     | Technology        | 17.50%        |
| 2017 | 120  | 33     | 10     | Basic Materials   | 17.50%        |
| 2018 | 120  | 32     | 9      | Industrials       | 20.00%        |
| 2019 | 120  | 32     | 9      | Real Estate       | 20.00%        |
| 2020 | 120  | 36     | 9      | Industrials       | 20.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 114  | 114  | 8.66%          | 5.38%            | 59.65%  | 25.44%  | 10.53%        | 114  | -1.42%         | 2.57%            | 57.02%  | 34.21%  | 36.84%        |
| 2006     | 119  | 119  | 10.08%         | -6.11%           | 46.22%  | 37.82%  | 13.45%        | 119  | -2.45%         | 2.90%            | 56.30%  | 64.71%  | 27.73%        |
| 2007     | 111  | 111  | -9.96%         | -9.71%           | 31.53%  | 84.68%  | 2.70%         | 111  | -8.06%         | -9.43%           | 33.33%  | 78.38%  | 15.32%        |
| 2008     | 117  | 117  | 8.68%          | -8.20%           | 42.74%  | 74.36%  | 0.00%         | 117  | -8.34%         | -5.58%           | 33.33%  | 59.83%  | 28.21%        |
| 2009     | 120  | 120  | 37.19%         | 3.13%            | 52.50%  | 23.33%  | 3.33%         | 120  | 6.67%          | 6.93%            | 58.33%  | 30.00%  | 17.50%        |
| 2010     | 120  | 120  | 3.73%          | 4.31%            | 58.33%  | 25.83%  | 6.67%         | 120  | -3.44%         | 3.04%            | 53.33%  | 23.33%  | 14.17%        |
| 2011     | 118  | 118  | 0.05%          | -5.35%           | 40.68%  | 48.31%  | 2.54%         | 118  | -1.74%         | -1.01%           | 46.61%  | 22.03%  | 15.25%        |
| 2012     | 120  | 120  | 11.18%         | 2.65%            | 56.67%  | 16.67%  | 11.67%        | 120  | 0.44%          | -1.16%           | 47.50%  | 18.33%  | 14.17%        |
| 2013     | 119  | 119  | 5.18%          | -2.73%           | 43.70%  | 25.21%  | 7.56%         | 119  | -1.28%         | -0.24%           | 48.74%  | 26.05%  | 15.13%        |
| 2014     | 120  | 120  | -10.02%        | -12.06%          | 42.50%  | 50.00%  | 7.50%         | 120  | -3.84%         | -0.95%           | 48.33%  | 30.83%  | 15.00%        |
| 2015     | 117  | 117  | -1.86%         | -0.15%           | 48.72%  | 46.15%  | 2.56%         | 117  | -4.08%         | -4.95%           | 44.44%  | 35.04%  | 5.13%         |
| 2016     | 120  | 120  | 17.34%         | 9.43%            | 64.17%  | 14.17%  | 10.00%        | 120  | -0.01%         | 1.24%            | 54.17%  | 17.50%  | 15.00%        |
| 2017     | 120  | 120  | -11.78%        | -9.21%           | 33.33%  | 39.17%  | 2.50%         | 120  | -12.33%        | -11.77%          | 24.17%  | 52.50%  | 20.00%        |
| 2018     | 120  | 120  | -2.30%         | -5.07%           | 40.83%  | 46.67%  | 15.00%        | 120  | -11.34%        | -9.25%           | 28.33%  | 33.33%  | 27.50%        |
| 2019     | 120  | 120  | -14.90%        | -16.67%          | 20.00%  | 59.17%  | 15.00%        | 120  | -7.99%         | -8.04%           | 16.67%  | 30.00%  | 17.50%        |
| 2020     | 120  | 120  | 13.73%         | -6.60%           | 45.00%  | 12.50%  | 2.50%         | 120  | -5.99%         | -3.75%           | 39.17%  | 23.33%  | 7.50%         |
| all buys | 1895 | 1895 | 4.12%          | -3.19%           | 45.44%  | 39.10%  | 7.12%         | 1895 | -4.06%         | -2.88%           | 43.11%  | 35.99%  | 18.21%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -1.42%      | -7.05%            | 5.63%         | -12.69%      | 11.26%   | 34.21%    | 51.15%          | 60.70%     |
| 2006     | 119  | -2.45%      | -8.77%            | 6.32%         | -15.23%      | 12.78%   | 64.71%    | 77.11%          | 81.46%     |
| 2007     | 111  | -8.06%      | -6.21%            | -1.85%        | -13.59%      | 5.53%    | 78.38%    | 69.16%          | 74.79%     |
| 2008     | 117  | -8.34%      | -0.71%            | -7.63%        | -6.87%       | -1.47%   | 59.83%    | 41.68%          | 51.34%     |
| 2009     | 120  | 6.67%       | 1.15%             | 5.52%         | 0.65%        | 6.01%    | 30.00%    | 22.58%          | 29.12%     |
| 2010     | 120  | -3.44%      | -5.26%            | 1.82%         | -9.83%       | 6.39%    | 23.33%    | 26.07%          | 35.97%     |
| 2011     | 118  | -1.74%      | -7.27%            | 5.53%         | -9.53%       | 7.79%    | 22.03%    | 26.82%          | 31.96%     |
| 2012     | 120  | 0.44%       | -6.36%            | 6.80%         | -5.66%       | 6.10%    | 18.33%    | 26.57%          | 25.84%     |
| 2013     | 119  | -1.28%      | -10.20%           | 8.92%         | -14.01%      | 12.73%   | 26.05%    | 39.13%          | 47.63%     |
| 2014     | 120  | -3.84%      | -11.89%           | 8.05%         | -15.60%      | 11.77%   | 30.83%    | 41.94%          | 48.31%     |
| 2015     | 117  | -4.08%      | -10.90%           | 6.81%         | -9.46%       | 5.38%    | 35.04%    | 38.50%          | 37.70%     |
| 2016     | 120  | -0.01%      | -9.39%            | 9.39%         | -9.46%       | 9.45%    | 17.50%    | 35.30%          | 37.63%     |
| 2017     | 120  | -12.33%     | -14.92%           | 2.59%         | -16.43%      | 4.10%    | 52.50%    | 51.24%          | 54.31%     |
| 2018     | 120  | -11.34%     | -12.32%           | 0.98%         | -14.33%      | 2.99%    | 33.33%    | 37.83%          | 43.00%     |
| 2019     | 120  | -7.99%      | -12.56%           | 4.57%         | -12.02%      | 4.02%    | 30.00%    | 40.86%          | 41.64%     |
| 2020     | 120  | -5.99%      | -9.60%            | 3.62%         | -7.20%       | 1.22%    | 23.33%    | 40.64%          | 39.80%     |
| all buys | 1895 | -4.06%      | -8.31%            | 4.24%         | -10.69%      | 6.63%    | 35.99%    | 42.44%          | 46.15%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | 8.66%       | 5.55%             | 3.11%         | 44.52%       | -35.86%  | 25.44%    | 37.87%          | 44.68%     |
| 2006     | 119  | 10.08%      | -0.04%            | 10.12%        | -3.56%       | 13.64%   | 37.82%    | 37.68%          | 45.87%     |
| 2007     | 111  | -9.96%      | -6.64%            | -3.32%        | -14.51%      | 4.55%    | 84.68%    | 73.25%          | 77.97%     |
| 2008     | 117  | 8.68%       | 4.12%             | 4.56%         | 6.16%        | 2.52%    | 74.36%    | 74.19%          | 73.44%     |
| 2009     | 120  | 37.19%      | 29.46%            | 7.74%         | 52.38%       | -15.18%  | 23.33%    | 21.24%          | 25.92%     |
| 2010     | 120  | 3.73%       | 4.76%             | -1.04%        | 2.53%        | 1.19%    | 25.83%    | 32.69%          | 39.81%     |
| 2011     | 118  | 0.05%       | -7.12%            | 7.16%         | -8.73%       | 8.78%    | 48.31%    | 47.77%          | 51.01%     |
| 2012     | 120  | 11.18%      | 4.38%             | 6.80%         | 5.97%        | 5.21%    | 16.67%    | 26.20%          | 25.44%     |
| 2013     | 119  | 5.18%       | 0.88%             | 4.30%         | 1.97%        | 3.21%    | 25.21%    | 28.61%          | 35.46%     |
| 2014     | 120  | -10.02%     | -7.37%            | -2.65%        | -9.88%       | -0.14%   | 50.00%    | 47.98%          | 54.52%     |
| 2015     | 117  | -1.86%      | -9.74%            | 7.88%         | -8.68%       | 6.82%    | 46.15%    | 56.60%          | 56.76%     |
| 2016     | 120  | 17.34%      | 1.86%             | 15.48%        | 5.32%        | 12.01%   | 14.17%    | 30.74%          | 30.68%     |
| 2017     | 120  | -11.78%     | -1.22%            | -10.56%       | 0.44%        | -12.22%  | 39.17%    | 41.15%          | 41.95%     |
| 2018     | 120  | -2.30%      | -11.00%           | 8.70%         | -13.68%      | 11.38%   | 46.67%    | 54.83%          | 58.40%     |
| 2019     | 120  | -14.90%     | -9.48%            | -5.43%        | -11.93%      | -2.97%   | 59.17%    | 56.24%          | 57.77%     |
| 2020     | 120  | 13.73%      | 35.07%            | -21.34%       | 33.53%       | -19.79%  | 12.50%    | 22.83%          | 22.17%     |
| all buys | 1895 | 4.12%       | 1.88%             | 2.24%         | 5.13%        | -1.01%   | 39.10%    | 43.65%          | 46.16%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 22
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3151.2 (min 2666)
- mean with a tradable quote: 3077.4 (min 2636)
- forced delisting liquidations: 192 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 40 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `lgbm_regressor_growth_allrows_3y__fwd_3y_cagr__set0` — label `fwd_3y_cagr` (3y), model `lightgbm_regressor`, config `7c1507e3f386652f`, train run `233299a55d4c`, folds 2005–2020 (from `experiments/models/lgbm_regressor_growth_allrows_3y__fwd_3y_cagr__set0_233299a55d4c`)

### Artifacts

- equity_curve: `reports/backtest/bt_huber_cagr_top10_cap2_6a152781b2756b63_equity.csv`
- trades: `reports/backtest/bt_huber_cagr_top10_cap2_6a152781b2756b63_trades.csv`
- rebalances: `reports/backtest/bt_huber_cagr_top10_cap2_6a152781b2756b63_rebalances.csv`
- equity_plot: `reports/backtest/bt_huber_cagr_top10_cap2_6a152781b2756b63_equity.png`
