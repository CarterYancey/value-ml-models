# Portfolio backtest — bt_fresh50_forestC_top10_cap2_rankfloor

- run `82c8a571806b`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `8d1e090f6229681b`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 558,796.50  | 378,796.50 | 10.41%         | 8.69%    | -60.18%      | 1,889.55   |
| benchmark | 180,000.00 | 664,684.90  | 484,684.90 | 11.96%         | 9.72%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006              | 19.87%       | 13.50%        | 6.37%   | 12,000.00 | 107    | 0.3189          |
| 2007              | -21.97%      | 4.41%         | -26.39% | 12,000.00 | 114    | 0.4087          |
| 2008 (GFC)        | -30.38%      | -34.28%       | 3.89%   | 12,000.00 | 120    | 0.5320          |
| 2009 (GFC)        | 59.31%       | 24.77%        | 34.55%  | 12,000.00 | 117    | 0.5651          |
| 2010              | 28.25%       | 14.30%        | 13.95%  | 12,000.00 | 120    | 0.3889          |
| 2011              | -7.21%       | 2.46%         | -9.67%  | 12,000.00 | 117    | 0.3539          |
| 2012              | 15.31%       | 17.09%        | -1.78%  | 12,000.00 | 117    | 0.3501          |
| 2013              | 38.92%       | 27.75%        | 11.17%  | 12,000.00 | 113    | 0.3362          |
| 2014              | 3.29%        | 14.50%        | -11.20% | 12,000.00 | 120    | 0.3225          |
| 2015              | -7.99%       | -0.10%        | -7.88%  | 12,000.00 | 119    | 0.3807          |
| 2016              | 27.51%       | 14.45%        | 13.05%  | 12,000.00 | 120    | 0.4300          |
| 2017              | 20.01%       | 21.63%        | -1.62%  | 12,000.00 | 107    | 0.3600          |
| 2018              | -13.17%      | -5.13%        | -8.04%  | 12,000.00 | 117    | 0.3572          |
| 2019              | 17.36%       | 32.30%        | -14.94% | 12,000.00 | 117    | 0.4267          |
| 2020 (COVID)      | 19.85%       | 15.68%        | 4.17%   | 12,000.00 | 114    | 0.4831          |
| 2021              | 24.19%       | 31.26%        | -7.07%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -17.60%      | -18.98%       | 1.37%   | 0.00      | 0      | —               |
| 2023              | 24.62%       | 26.71%        | -2.08%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_52w_high <= -0.5`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Cyclical      | 289  | 16.62% |
| Technology             | 287  | 16.50% |
| Industrials            | 255  | 14.66% |
| Healthcare             | 202  | 11.62% |
| Consumer Defensive     | 187  | 10.75% |
| Energy                 | 182  | 10.47% |
| Communication Services | 152  | 8.74%  |
| Basic Materials        | 120  | 6.90%  |
| Real Estate            | 32   | 1.84%  |
| Financial Services     | 27   | 1.55%  |
| Utilities              | 6    | 0.35%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2006 | 107  | 33     | 8      | Consumer Cyclical  | 21.50%        |
| 2007 | 114  | 29     | 9      | Technology         | 21.05%        |
| 2008 | 120  | 38     | 9      | Technology         | 20.00%        |
| 2009 | 117  | 31     | 9      | Industrials        | 20.51%        |
| 2010 | 120  | 30     | 8      | Healthcare         | 20.00%        |
| 2011 | 117  | 32     | 9      | Consumer Cyclical  | 20.51%        |
| 2012 | 117  | 32     | 8      | Technology         | 20.51%        |
| 2013 | 113  | 31     | 8      | Technology         | 20.35%        |
| 2014 | 120  | 31     | 9      | Basic Materials    | 17.50%        |
| 2015 | 119  | 34     | 8      | Energy             | 19.33%        |
| 2016 | 120  | 32     | 8      | Energy             | 20.00%        |
| 2017 | 107  | 31     | 9      | Consumer Cyclical  | 19.63%        |
| 2018 | 117  | 33     | 10     | Consumer Defensive | 20.51%        |
| 2019 | 117  | 31     | 9      | Consumer Cyclical  | 20.51%        |
| 2020 | 114  | 38     | 10     | Consumer Cyclical  | 15.79%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 107  | 107  | -11.87%        | -12.74%          | 34.58%  | 47.66%  | 2.80%         | 107  | -11.45%        | -12.45%          | 28.04%  | 84.11%  | 14.02%        |
| 2007     | 114  | 114  | -11.56%        | -23.55%          | 36.84%  | 67.54%  | 1.75%         | 114  | -3.98%         | -4.35%           | 49.12%  | 56.14%  | 28.95%        |
| 2008     | 120  | 120  | 13.94%         | 11.31%           | 63.33%  | 60.00%  | 2.50%         | 120  | 3.65%          | 1.85%            | 58.33%  | 37.50%  | 5.00%         |
| 2009     | 117  | 117  | 19.39%         | 12.58%           | 70.94%  | 12.82%  | 7.69%         | 117  | 4.65%          | 4.38%            | 66.67%  | 13.68%  | 17.95%        |
| 2010     | 120  | 120  | -2.75%         | -10.84%          | 39.17%  | 48.33%  | 0.00%         | 120  | -11.35%        | -8.10%           | 36.67%  | 44.17%  | 15.00%        |
| 2011     | 117  | 117  | -16.02%        | -30.88%          | 31.62%  | 60.68%  | 11.97%        | 117  | -15.80%        | -5.08%           | 39.32%  | 45.30%  | 23.08%        |
| 2012     | 117  | 117  | -1.78%         | -4.16%           | 45.30%  | 32.48%  | 0.00%         | 117  | -12.97%        | -10.55%          | 25.64%  | 31.62%  | 7.69%         |
| 2013     | 113  | 113  | -3.77%         | -4.09%           | 43.36%  | 36.28%  | 5.31%         | 113  | -20.63%        | -13.75%          | 22.12%  | 59.29%  | 19.47%        |
| 2014     | 120  | 120  | -17.74%        | -23.86%          | 35.83%  | 56.67%  | 5.83%         | 120  | -13.65%        | -8.17%           | 34.17%  | 43.33%  | 37.50%        |
| 2015     | 119  | 119  | -3.23%         | -4.25%           | 47.90%  | 51.26%  | 0.00%         | 119  | -4.54%         | -6.54%           | 37.82%  | 36.97%  | 5.04%         |
| 2016     | 120  | 120  | 17.13%         | 17.00%           | 63.33%  | 30.00%  | 7.50%         | 120  | -5.16%         | 0.62%            | 52.50%  | 32.50%  | 15.00%        |
| 2017     | 107  | 107  | 5.10%          | 5.22%            | 54.21%  | 40.19%  | 0.00%         | 107  | -29.88%        | -21.51%          | 17.76%  | 71.03%  | 9.35%         |
| 2018     | 117  | 117  | -19.08%        | -26.76%          | 28.21%  | 67.52%  | 2.56%         | 117  | -14.43%        | -13.97%          | 25.64%  | 40.17%  | 17.95%        |
| 2019     | 117  | 117  | -8.02%         | -8.55%           | 41.03%  | 52.14%  | 2.56%         | 117  | -6.30%         | -5.46%           | 35.90%  | 33.33%  | 17.95%        |
| 2020     | 114  | 114  | 26.51%         | 21.84%           | 65.79%  | 10.53%  | 2.63%         | 114  | 7.88%          | 6.93%            | 65.79%  | 24.56%  | 9.65%         |
| all buys | 1739 | 1739 | -0.89%         | -3.95%           | 46.81%  | 45.03%  | 3.57%         | 1739 | -8.79%         | -6.44%           | 39.91%  | 43.13%  | 16.27%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 107  | -11.45%     | -25.70%           | 14.24%        | -23.56%      | 12.11%   | 84.11%    | 86.43%          | 85.18%     |
| 2007     | 114  | -3.98%      | -24.12%           | 20.14%        | -19.11%      | 15.13%   | 56.14%    | 81.74%          | 75.92%     |
| 2008     | 120  | 3.65%       | -7.80%            | 11.45%        | -0.97%       | 4.61%    | 37.50%    | 52.37%          | 44.65%     |
| 2009     | 117  | 4.65%       | 3.82%             | 0.83%         | 3.46%        | 1.19%    | 13.68%    | 25.30%          | 21.72%     |
| 2010     | 120  | -11.35%     | -26.24%           | 14.89%        | -19.78%      | 8.43%    | 44.17%    | 59.01%          | 51.00%     |
| 2011     | 117  | -15.80%     | -28.40%           | 12.60%        | -25.31%      | 9.51%    | 45.30%    | 60.18%          | 58.05%     |
| 2012     | 117  | -12.97%     | -22.83%           | 9.86%         | -20.51%      | 7.54%    | 31.62%    | 53.77%          | 50.56%     |
| 2013     | 113  | -20.63%     | -30.41%           | 9.78%         | -29.29%      | 8.66%    | 59.29%    | 67.28%          | 64.18%     |
| 2014     | 120  | -13.65%     | -36.85%           | 23.19%        | -27.59%      | 13.94%   | 43.33%    | 72.46%          | 59.30%     |
| 2015     | 119  | -4.54%      | -31.98%           | 27.45%        | -22.58%      | 18.05%   | 36.97%    | 65.69%          | 55.12%     |
| 2016     | 120  | -5.16%      | -22.61%           | 17.45%        | -11.00%      | 5.84%    | 32.50%    | 56.40%          | 43.15%     |
| 2017     | 107  | -29.88%     | -33.73%           | 3.85%         | -25.43%      | -4.45%   | 71.03%    | 70.25%          | 61.12%     |
| 2018     | 117  | -14.43%     | -32.76%           | 18.33%        | -22.98%      | 8.54%    | 40.17%    | 63.43%          | 46.24%     |
| 2019     | 117  | -6.30%      | -26.58%           | 20.29%        | -16.10%      | 9.81%    | 33.33%    | 61.96%          | 46.06%     |
| 2020     | 114  | 7.88%       | -13.67%           | 21.55%        | -1.92%       | 9.80%    | 24.56%    | 51.37%          | 39.71%     |
| all buys | 1739 | -8.79%      | -17.85%           | 9.06%         | -17.42%      | 8.63%    | 43.13%    | 54.40%          | 53.17%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 107  | -11.87%     | 6.12%             | -17.98%       | -12.62%      | 0.75%    | 47.66%    | 58.46%          | 58.74%     |
| 2007     | 114  | -11.56%     | -23.22%           | 11.67%        | -21.53%      | 9.97%    | 67.54%    | 80.70%          | 79.21%     |
| 2008     | 120  | 13.94%      | 11.21%            | 2.73%         | 9.30%        | 4.64%    | 60.00%    | 69.50%          | 69.32%     |
| 2009     | 117  | 19.39%      | 58.66%            | -39.27%       | 35.09%       | -15.70%  | 12.82%    | 19.94%          | 18.55%     |
| 2010     | 120  | -2.75%      | -12.95%           | 10.20%        | -9.58%       | 6.83%    | 48.33%    | 62.57%          | 53.44%     |
| 2011     | 117  | -16.02%     | -27.13%           | 11.11%        | -26.30%      | 10.27%   | 60.68%    | 68.18%          | 68.72%     |
| 2012     | 117  | -1.78%      | -5.20%            | 3.42%         | 7.75%        | -9.53%   | 32.48%    | 52.19%          | 45.15%     |
| 2013     | 113  | -3.77%      | 6.94%             | -10.70%       | -1.10%       | -2.67%   | 36.28%    | 49.03%          | 46.01%     |
| 2014     | 120  | -17.74%     | -30.24%           | 12.50%        | -26.91%      | 9.17%    | 56.67%    | 73.62%          | 67.62%     |
| 2015     | 119  | -3.23%      | -28.38%           | 25.14%        | -21.71%      | 18.47%   | 51.26%    | 73.50%          | 67.39%     |
| 2016     | 120  | 17.13%      | 2.90%             | 14.23%        | 14.26%       | 2.87%    | 30.00%    | 48.87%          | 38.07%     |
| 2017     | 107  | 5.10%       | 1.75%             | 3.35%         | 4.61%        | 0.49%    | 40.19%    | 56.35%          | 47.31%     |
| 2018     | 117  | -19.08%     | -30.90%           | 11.82%        | -22.12%      | 3.05%    | 67.52%    | 76.47%          | 68.20%     |
| 2019     | 117  | -8.02%      | -5.84%            | -2.18%        | -17.72%      | 9.70%    | 52.14%    | 64.95%          | 61.78%     |
| 2020     | 114  | 26.51%      | 88.03%            | -61.52%       | 80.51%       | -54.00%  | 10.53%    | 26.52%          | 17.48%     |
| all buys | 1739 | -0.89%      | 15.29%            | -16.18%       | -0.64%       | -0.25%   | 45.03%    | 51.17%          | 53.88%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 53
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 396.4 (min 105)
- mean with a tradable quote: 389.2 (min 104)
- forced delisting liquidations: 197 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 25 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fresh50_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `3b5deaae9886851c`, train run `12137a7f9c2a`, folds 2006–2020 (from `experiments/models/forest_fresh50_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_12137a7f9c2a`)

### Artifacts

- equity_curve: `reports/backtest/bt_fresh50_forestC_top10_cap2_rankfloor_8d1e090f6229681b_equity.csv`
- trades: `reports/backtest/bt_fresh50_forestC_top10_cap2_rankfloor_8d1e090f6229681b_trades.csv`
- rebalances: `reports/backtest/bt_fresh50_forestC_top10_cap2_rankfloor_8d1e090f6229681b_rebalances.csv`
- equity_plot: `reports/backtest/bt_fresh50_forestC_top10_cap2_rankfloor_8d1e090f6229681b_equity.png`
