# Portfolio backtest — bt_fresh70_forestC_top10_cap2_rankfloor_to2020

- run `44e73828c4c7`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `6240023813fd9ee1`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2020-12-31; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 312,884.36  | 132,884.36 | 7.00%          | 16.99%   | -92.86%      | 1,786.26   |
| benchmark | 180,000.00 | 500,058.34  | 320,058.34 | 12.58%         | 9.67%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year         | strategy_twr | benchmark_twr | excess   | deposits  | n_buys | mean_pick_score |
| ------------ | ------------ | ------------- | -------- | --------- | ------ | --------------- |
| 2006         | 1910.67%     | 13.50%        | 1897.16% | 12,000.00 | 120    | 0.2592          |
| 2007         | -70.15%      | 4.41%         | -74.56%  | 12,000.00 | 117    | 0.2831          |
| 2008 (GFC)   | -58.76%      | -34.28%       | -24.49%  | 12,000.00 | 120    | 0.3526          |
| 2009 (GFC)   | 99.36%       | 24.77%        | 74.60%   | 12,000.00 | 109    | 0.3804          |
| 2010         | 42.64%       | 14.30%        | 28.34%   | 12,000.00 | 115    | 0.2745          |
| 2011         | -25.34%      | 2.46%         | -27.80%  | 12,000.00 | 118    | 0.2668          |
| 2012         | 12.42%       | 17.09%        | -4.67%   | 12,000.00 | 112    | 0.2968          |
| 2013         | 40.44%       | 27.75%        | 12.69%   | 12,000.00 | 108    | 0.2833          |
| 2014         | -6.90%       | 14.50%        | -21.40%  | 12,000.00 | 108    | 0.2431          |
| 2015         | -21.22%      | -0.10%        | -21.12%  | 12,000.00 | 105    | 0.3287          |
| 2016         | 28.91%       | 14.45%        | 14.45%   | 12,000.00 | 116    | 0.3713          |
| 2017         | 14.20%       | 21.63%        | -7.43%   | 12,000.00 | 117    | 0.3029          |
| 2018         | -18.70%      | -5.13%        | -13.57%  | 12,000.00 | 114    | 0.2958          |
| 2019         | 8.92%        | 32.30%        | -23.39%  | 12,000.00 | 118    | 0.3361          |
| 2020 (COVID) | 32.59%       | 17.28%        | 15.32%   | 12,000.00 | 120    | 0.3848          |

**Defensive hypothesis:** Benchmark down-years in window: 3; strategy lost less (positive excess) in 0 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_52w_high <= -0.7`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Cyclical      | 274  | 15.96% |
| Industrials            | 241  | 14.04% |
| Technology             | 225  | 13.10% |
| Energy                 | 223  | 12.99% |
| Communication Services | 206  | 12.00% |
| Healthcare             | 183  | 10.66% |
| Basic Materials        | 141  | 8.21%  |
| Consumer Defensive     | 133  | 7.75%  |
| Real Estate            | 34   | 1.98%  |
| Financial Services     | 32   | 1.86%  |
| Utilities              | 25   | 1.46%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2006 | 120  | 31     | 9      | Industrials            | 17.50%        |
| 2007 | 117  | 31     | 10     | Consumer Cyclical      | 20.51%        |
| 2008 | 120  | 30     | 8      | Consumer Cyclical      | 20.00%        |
| 2009 | 109  | 33     | 8      | Industrials            | 22.02%        |
| 2010 | 115  | 28     | 10     | Industrials            | 18.26%        |
| 2011 | 118  | 31     | 9      | Industrials            | 17.80%        |
| 2012 | 112  | 30     | 8      | Technology             | 21.43%        |
| 2013 | 108  | 25     | 9      | Energy                 | 19.44%        |
| 2014 | 108  | 27     | 9      | Consumer Cyclical      | 19.44%        |
| 2015 | 105  | 26     | 8      | Industrials            | 22.86%        |
| 2016 | 116  | 28     | 9      | Consumer Cyclical      | 18.10%        |
| 2017 | 117  | 33     | 10     | Energy                 | 17.95%        |
| 2018 | 114  | 29     | 11     | Communication Services | 21.05%        |
| 2019 | 118  | 34     | 11     | Energy                 | 20.34%        |
| 2020 | 120  | 37     | 11     | Consumer Cyclical      | 20.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 120  | 120  | 407.98%        | -39.15%          | 28.33%  | 62.50%  | 19.17%        | 120  | -25.77%        | -32.00%          | 23.33%  | 83.33%  | 59.17%        |
| 2007     | 117  | 117  | -38.23%        | -56.33%          | 19.66%  | 85.47%  | 21.37%        | 117  | -25.81%        | -28.68%          | 26.50%  | 78.63%  | 51.28%        |
| 2008     | 120  | 120  | 31.08%         | -15.94%          | 41.67%  | 64.17%  | 10.83%        | 120  | -4.60%         | -3.71%           | 45.83%  | 51.67%  | 25.00%        |
| 2009     | 109  | 109  | 51.30%         | 18.66%           | 64.22%  | 14.68%  | 4.59%         | 109  | 8.64%          | 9.12%            | 62.39%  | 20.18%  | 12.84%        |
| 2010     | 115  | 115  | -9.19%         | -29.61%          | 35.65%  | 59.13%  | 46.09%        | 115  | -18.57%        | -10.54%          | 40.00%  | 45.22%  | 66.09%        |
| 2011     | 118  | 118  | -36.41%        | -60.03%          | 15.25%  | 79.66%  | 28.81%        | 118  | -32.12%        | -38.39%          | 20.34%  | 67.80%  | 55.08%        |
| 2012     | 112  | 112  | -19.18%        | -21.63%          | 27.68%  | 53.57%  | 0.89%         | 112  | -30.27%        | -20.95%          | 24.11%  | 56.25%  | 32.14%        |
| 2013     | 108  | 108  | -8.09%         | -28.82%          | 33.33%  | 53.70%  | 12.96%        | 108  | -36.15%        | -35.19%          | 21.30%  | 68.52%  | 41.67%        |
| 2014     | 108  | 108  | -56.16%        | -85.20%          | 13.89%  | 79.63%  | 32.41%        | 108  | -59.66%        | -61.16%          | 3.70%   | 91.67%  | 70.37%        |
| 2015     | 105  | 105  | -23.94%        | -36.49%          | 31.43%  | 66.67%  | 13.33%        | 105  | -16.96%        | -10.47%          | 31.43%  | 46.67%  | 34.29%        |
| 2016     | 116  | 116  | 9.83%          | -12.64%          | 43.10%  | 44.83%  | 4.31%         | 116  | -19.91%        | -16.84%          | 36.21%  | 52.59%  | 27.59%        |
| 2017     | 117  | 117  | -23.95%        | -39.08%          | 31.62%  | 64.10%  | 11.97%        | 117  | -46.54%        | -50.27%          | 10.26%  | 80.34%  | 23.08%        |
| 2018     | 114  | 114  | -45.85%        | -61.44%          | 14.91%  | 84.21%  | 14.91%        | 0    | —              | —                | —       | —       | —             |
| 2019     | 118  | 118  | -16.97%        | -42.24%          | 26.27%  | 70.34%  | 2.54%         | 0    | —              | —                | —       | —       | —             |
| 2020     | 120  | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 1717 | 1597 | 17.51%         | -33.55%          | 30.43%  | 63.24%  | 16.03%        | 1365 | -25.58%        | -23.61%          | 28.79%  | 62.12%  | 41.61%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 120  | -25.77%     | -29.47%           | 3.70%         | -28.42%      | 2.66%    | 83.33%    | 88.22%          | 87.53%     |
| 2007     | 117  | -25.81%     | -31.88%           | 6.07%         | -34.54%      | 8.73%    | 78.63%    | 84.28%          | 84.84%     |
| 2008     | 120  | -4.60%      | -16.74%           | 12.14%        | -14.63%      | 10.03%   | 51.67%    | 61.16%          | 59.25%     |
| 2009     | 109  | 8.64%       | 6.49%             | 2.15%         | 3.00%        | 5.65%    | 20.18%    | 28.02%          | 30.80%     |
| 2010     | 115  | -18.57%     | -34.55%           | 15.98%        | -35.57%      | 17.00%   | 45.22%    | 68.26%          | 63.78%     |
| 2011     | 118  | -32.12%     | -41.59%           | 9.48%         | -38.38%      | 6.26%    | 67.80%    | 73.93%          | 74.97%     |
| 2012     | 112  | -30.27%     | -28.73%           | -1.55%        | -23.90%      | -6.37%   | 56.25%    | 59.30%          | 54.68%     |
| 2013     | 108  | -36.15%     | -33.01%           | -3.14%        | -40.16%      | 4.01%    | 68.52%    | 71.89%          | 76.77%     |
| 2014     | 108  | -59.66%     | -50.90%           | -8.76%        | -54.47%      | -5.18%   | 91.67%    | 82.21%          | 86.54%     |
| 2015     | 105  | -16.96%     | -42.69%           | 25.72%        | -38.07%      | 21.11%   | 46.67%    | 76.70%          | 72.48%     |
| 2016     | 116  | -19.91%     | -32.26%           | 12.35%        | -19.42%      | -0.50%   | 52.59%    | 67.03%          | 55.12%     |
| 2017     | 117  | -46.54%     | -42.22%           | -4.32%        | -39.52%      | -7.02%   | 80.34%    | 77.19%          | 74.57%     |
| all buys | 1365 | -25.58%     | -19.61%           | -5.97%        | -30.23%      | 4.65%    | 62.12%    | 56.66%          | 68.55%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 120  | 407.98%     | 72.98%            | 335.00%       | 66.88%       | 341.10%  | 62.50%    | 62.19%          | 62.67%     |
| 2007     | 117  | -38.23%     | -30.61%           | -7.62%        | -39.45%      | 1.22%    | 85.47%    | 84.28%          | 89.89%     |
| 2008     | 120  | 31.08%      | 19.70%            | 11.37%        | 16.38%       | 14.69%   | 64.17%    | 69.11%          | 67.10%     |
| 2009     | 109  | 51.30%      | 102.19%           | -50.89%       | 78.81%       | -27.51%  | 14.68%    | 20.41%          | 23.85%     |
| 2010     | 115  | -9.19%      | -23.52%           | 14.33%        | -23.85%      | 14.66%   | 59.13%    | 71.10%          | 68.64%     |
| 2011     | 118  | -36.41%     | -38.03%           | 1.62%         | -43.69%      | 7.27%    | 79.66%    | 76.72%          | 81.05%     |
| 2012     | 112  | -19.18%     | -8.04%            | -11.14%       | 6.55%        | -25.73%  | 53.57%    | 58.45%          | 51.41%     |
| 2013     | 108  | -8.09%      | 12.16%            | -20.25%       | -9.85%       | 1.76%    | 53.70%    | 55.90%          | 57.85%     |
| 2014     | 108  | -56.16%     | -44.83%           | -11.33%       | -44.69%      | -11.47%  | 79.63%    | 82.21%          | 80.99%     |
| 2015     | 105  | -23.94%     | -41.61%           | 17.67%        | -40.07%      | 16.13%   | 66.67%    | 80.95%          | 80.84%     |
| 2016     | 116  | 9.83%       | -4.62%            | 14.45%        | 23.86%       | -14.02%  | 44.83%    | 59.13%          | 45.71%     |
| 2017     | 117  | -23.95%     | -0.47%            | -23.49%       | -4.48%       | -19.47%  | 64.10%    | 64.61%          | 61.83%     |
| 2018     | 114  | -45.85%     | -36.82%           | -9.04%        | -32.81%      | -13.04%  | 84.21%    | 81.90%          | 78.83%     |
| 2019     | 118  | -16.97%     | 5.97%             | -22.94%       | -9.18%       | -7.79%   | 70.34%    | 69.82%          | 68.73%     |
| all buys | 1597 | 17.51%      | 24.82%            | -7.31%        | -3.68%       | 21.19%   | 63.24%    | 55.36%          | 65.76%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 72
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 136.3 (min 26)
- mean with a tradable quote: 131.7 (min 25)
- forced delisting liquidations: 217 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 28 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fresh70_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `dd4ddbd0a7ea4ffa`, train run `b4761e624f82`, folds 2006–2020 (from `experiments/models/forest_fresh70_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_b4761e624f82`)

### Artifacts

- equity_curve: `reports/backtest/bt_fresh70_forestC_top10_cap2_rankfloor_to2020_6240023813fd9ee1_equity.csv`
- trades: `reports/backtest/bt_fresh70_forestC_top10_cap2_rankfloor_to2020_6240023813fd9ee1_trades.csv`
- rebalances: `reports/backtest/bt_fresh70_forestC_top10_cap2_rankfloor_to2020_6240023813fd9ee1_rebalances.csv`
- equity_plot: `reports/backtest/bt_fresh70_forestC_top10_cap2_rankfloor_to2020_6240023813fd9ee1_equity.png`
