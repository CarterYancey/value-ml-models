# Portfolio backtest — bt_fresh40_forestC_top10_cap2_rankfloor_to2020

- run `93d9abfa4ffc`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `53bc43ab9920a493`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2020-12-31; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 470,922.70  | 290,922.70 | 11.88%         | 10.10%   | -61.27%      | 1,351.93   |
| benchmark | 180,000.00 | 500,058.34  | 320,058.34 | 12.58%         | 9.67%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year         | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ------------ | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006         | 26.56%       | 13.50%        | 13.06%  | 12,000.00 | 108    | 0.3891          |
| 2007         | -11.55%      | 4.41%         | -15.96% | 12,000.00 | 112    | 0.4801          |
| 2008 (GFC)   | -32.16%      | -34.28%       | 2.11%   | 12,000.00 | 113    | 0.6238          |
| 2009 (GFC)   | 44.29%       | 24.77%        | 19.52%  | 12,000.00 | 118    | 0.6609          |
| 2010         | 26.80%       | 14.30%        | 12.50%  | 12,000.00 | 114    | 0.4584          |
| 2011         | -4.00%       | 2.46%         | -6.46%  | 12,000.00 | 118    | 0.4247          |
| 2012         | 18.43%       | 17.09%        | 1.34%   | 12,000.00 | 114    | 0.3957          |
| 2013         | 37.91%       | 27.75%        | 10.15%  | 12,000.00 | 114    | 0.3613          |
| 2014         | 9.09%        | 14.50%        | -5.40%  | 12,000.00 | 120    | 0.3549          |
| 2015         | -8.27%       | -0.10%        | -8.17%  | 12,000.00 | 118    | 0.4158          |
| 2016         | 29.82%       | 14.45%        | 15.36%  | 12,000.00 | 114    | 0.4936          |
| 2017         | 18.70%       | 21.63%        | -2.93%  | 12,000.00 | 117    | 0.3988          |
| 2018         | -13.47%      | -5.13%        | -8.34%  | 12,000.00 | 113    | 0.4049          |
| 2019         | 26.46%       | 32.30%        | -5.85%  | 12,000.00 | 120    | 0.5016          |
| 2020 (COVID) | 15.10%       | 17.28%        | -2.17%  | 12,000.00 | 114    | 0.5376          |

**Defensive hypothesis:** Benchmark down-years in window: 3; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_52w_high <= -0.4`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Cyclical      | 291  | 16.85% |
| Industrials            | 283  | 16.39% |
| Technology             | 272  | 15.75% |
| Consumer Defensive     | 203  | 11.75% |
| Communication Services | 165  | 9.55%  |
| Healthcare             | 153  | 8.86%  |
| Energy                 | 143  | 8.28%  |
| Basic Materials        | 138  | 7.99%  |
| Real Estate            | 40   | 2.32%  |
| Financial Services     | 24   | 1.39%  |
| Utilities              | 15   | 0.87%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2006 | 108  | 31     | 7      | Consumer Defensive | 19.44%        |
| 2007 | 112  | 32     | 9      | Industrials        | 18.75%        |
| 2008 | 113  | 35     | 10     | Consumer Cyclical  | 16.81%        |
| 2009 | 118  | 34     | 10     | Industrials        | 20.34%        |
| 2010 | 114  | 32     | 8      | Consumer Cyclical  | 21.05%        |
| 2011 | 118  | 36     | 9      | Consumer Cyclical  | 20.34%        |
| 2012 | 114  | 32     | 8      | Technology         | 21.05%        |
| 2013 | 114  | 33     | 9      | Technology         | 20.18%        |
| 2014 | 120  | 30     | 9      | Consumer Cyclical  | 17.50%        |
| 2015 | 118  | 33     | 8      | Technology         | 20.34%        |
| 2016 | 114  | 35     | 9      | Technology         | 21.05%        |
| 2017 | 117  | 34     | 9      | Consumer Cyclical  | 20.51%        |
| 2018 | 113  | 36     | 10     | Technology         | 19.47%        |
| 2019 | 120  | 31     | 8      | Industrials        | 20.00%        |
| 2020 | 114  | 35     | 10     | Consumer Cyclical  | 18.42%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 108  | 108  | 5.58%          | 2.72%            | 50.93%  | 40.74%  | 12.04%        | 108  | -9.09%         | -2.35%           | 49.07%  | 73.15%  | 25.00%        |
| 2007     | 112  | 112  | -8.94%         | -10.04%          | 37.50%  | 78.57%  | 0.00%         | 112  | -1.25%         | -0.10%           | 50.00%  | 58.93%  | 13.39%        |
| 2008     | 113  | 113  | 11.82%         | 5.90%            | 58.41%  | 63.72%  | 0.00%         | 113  | 4.57%          | 4.78%            | 69.91%  | 26.55%  | 2.65%         |
| 2009     | 118  | 118  | 14.15%         | 12.12%           | 73.73%  | 9.32%   | 0.00%         | 118  | 5.61%          | 6.40%            | 72.88%  | 8.47%   | 0.00%         |
| 2010     | 114  | 114  | -2.40%         | -14.13%          | 39.47%  | 49.12%  | 2.63%         | 114  | -2.45%         | -5.72%           | 44.74%  | 31.58%  | 12.28%        |
| 2011     | 118  | 118  | -20.63%        | -25.13%          | 27.97%  | 61.02%  | 9.32%         | 118  | -10.15%        | -6.22%           | 38.14%  | 33.05%  | 22.88%        |
| 2012     | 114  | 114  | -3.25%         | -6.37%           | 42.11%  | 33.33%  | 2.63%         | 114  | -13.56%        | -9.35%           | 28.07%  | 41.23%  | 2.63%         |
| 2013     | 114  | 114  | 2.15%          | 6.31%            | 57.02%  | 28.95%  | 2.63%         | 114  | -13.73%        | -12.47%          | 27.19%  | 55.26%  | 13.16%        |
| 2014     | 120  | 120  | -1.80%         | -0.35%           | 50.00%  | 41.67%  | 5.00%         | 120  | -4.87%         | -2.25%           | 42.50%  | 33.33%  | 28.33%        |
| 2015     | 118  | 118  | -5.35%         | -6.60%           | 38.14%  | 56.78%  | 0.00%         | 118  | -6.71%         | -2.16%           | 42.37%  | 27.97%  | 7.63%         |
| 2016     | 114  | 114  | 7.64%          | 5.94%            | 59.65%  | 21.93%  | 5.26%         | 114  | -1.97%         | 0.09%            | 50.00%  | 21.93%  | 15.79%        |
| 2017     | 117  | 117  | -5.74%         | -8.00%           | 42.74%  | 42.74%  | 0.00%         | 117  | -23.44%        | -23.68%          | 17.95%  | 69.23%  | 7.69%         |
| 2018     | 113  | 113  | -3.69%         | -5.48%           | 43.36%  | 47.79%  | 8.85%         | 0    | —              | —                | —       | —       | —             |
| 2019     | 120  | 120  | -11.66%        | -13.55%          | 31.67%  | 51.67%  | 7.50%         | 0    | —              | —                | —       | —       | —             |
| 2020     | 114  | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 1727 | 1613 | -1.67%         | -3.53%           | 46.56%  | 44.76%  | 3.97%         | 1380 | -6.43%         | -2.82%           | 44.35%  | 39.78%  | 12.61%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 108  | -9.09%      | -22.58%           | 13.49%        | -15.88%      | 6.79%    | 73.15%    | 84.71%          | 80.56%     |
| 2007     | 112  | -1.25%      | -21.08%           | 19.83%        | -13.30%      | 12.05%   | 58.93%    | 78.82%          | 74.81%     |
| 2008     | 113  | 4.57%       | -5.40%            | 9.97%         | 0.52%        | 4.05%    | 26.55%    | 49.80%          | 41.69%     |
| 2009     | 118  | 5.61%       | 2.92%             | 2.69%         | 1.17%        | 4.44%    | 8.47%     | 24.14%          | 19.17%     |
| 2010     | 114  | -2.45%      | -21.81%           | 19.36%        | -16.46%      | 14.01%   | 31.58%    | 54.87%          | 45.03%     |
| 2011     | 118  | -10.15%     | -22.28%           | 12.13%        | -18.16%      | 8.01%    | 33.05%    | 51.75%          | 47.68%     |
| 2012     | 114  | -13.56%     | -18.73%           | 5.18%         | -15.90%      | 2.34%    | 41.23%    | 49.05%          | 45.15%     |
| 2013     | 114  | -13.73%     | -27.95%           | 14.22%        | -23.00%      | 9.27%    | 55.26%    | 65.05%          | 61.59%     |
| 2014     | 120  | -4.87%      | -32.79%           | 27.92%        | -18.28%      | 13.41%   | 33.33%    | 69.06%          | 51.71%     |
| 2015     | 118  | -6.71%      | -27.33%           | 20.63%        | -18.99%      | 12.29%   | 27.97%    | 61.07%          | 51.13%     |
| 2016     | 114  | -1.97%      | -19.38%           | 17.41%        | -11.26%      | 9.29%    | 21.93%    | 52.47%          | 39.17%     |
| 2017     | 117  | -23.44%     | -31.27%           | 7.83%         | -26.77%      | 3.33%    | 69.23%    | 68.63%          | 67.05%     |
| all buys | 1380 | -6.43%      | -15.22%           | 8.79%         | -14.72%      | 8.29%    | 39.78%    | 52.21%          | 51.83%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 108  | 5.58%       | -0.45%            | 6.04%         | 0.87%        | 4.71%    | 40.74%    | 55.90%          | 43.90%     |
| 2007     | 112  | -8.94%      | -21.27%           | 12.33%        | -16.74%      | 7.80%    | 78.57%    | 81.23%          | 79.03%     |
| 2008     | 113  | 11.82%      | 8.80%             | 3.01%         | 7.14%        | 4.68%    | 63.72%    | 70.73%          | 69.63%     |
| 2009     | 118  | 14.15%      | 47.45%            | -33.31%       | 21.17%       | -7.02%   | 9.32%     | 20.11%          | 17.05%     |
| 2010     | 114  | -2.40%      | -11.99%           | 9.59%         | -13.44%      | 11.05%   | 49.12%    | 59.67%          | 56.05%     |
| 2011     | 118  | -20.63%     | -21.49%           | 0.87%         | -20.00%      | -0.62%   | 61.02%    | 63.74%          | 65.01%     |
| 2012     | 114  | -3.25%      | -1.80%            | -1.45%        | 0.17%        | -3.43%   | 33.33%    | 46.91%          | 40.48%     |
| 2013     | 114  | 2.15%       | 4.72%             | -2.57%        | -3.85%       | 6.00%    | 28.95%    | 46.31%          | 44.23%     |
| 2014     | 120  | -1.80%      | -25.25%           | 23.45%        | -12.27%      | 10.46%   | 41.67%    | 70.81%          | 54.73%     |
| 2015     | 118  | -5.35%      | -24.27%           | 18.92%        | -19.52%      | 14.16%   | 56.78%    | 70.73%          | 64.37%     |
| 2016     | 114  | 7.64%       | 3.59%             | 4.05%         | 2.34%        | 5.29%    | 21.93%    | 44.77%          | 35.91%     |
| 2017     | 117  | -5.74%      | -0.40%            | -5.33%        | -0.86%       | -4.88%   | 42.74%    | 55.48%          | 49.77%     |
| 2018     | 113  | -3.69%      | -27.95%           | 24.26%        | -15.28%      | 11.59%   | 47.79%    | 74.12%          | 60.08%     |
| 2019     | 120  | -11.66%     | -8.57%            | -3.09%        | -10.43%      | -1.23%   | 51.67%    | 63.65%          | 57.86%     |
| all buys | 1613 | -1.67%      | 3.25%             | -4.91%        | -5.81%       | 4.14%    | 44.76%    | 53.74%          | 52.70%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 57
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 613.7 (min 185)
- mean with a tradable quote: 605.0 (min 184)
- forced delisting liquidations: 125 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 24 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fresh40_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `dbdbe116c40b7e98`, train run `86f2d1626a6e`, folds 2006–2020 (from `experiments/models/forest_fresh40_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_86f2d1626a6e`)

### Artifacts

- equity_curve: `reports/backtest/bt_fresh40_forestC_top10_cap2_rankfloor_to2020_53bc43ab9920a493_equity.csv`
- trades: `reports/backtest/bt_fresh40_forestC_top10_cap2_rankfloor_to2020_53bc43ab9920a493_trades.csv`
- rebalances: `reports/backtest/bt_fresh40_forestC_top10_cap2_rankfloor_to2020_53bc43ab9920a493_rebalances.csv`
- equity_plot: `reports/backtest/bt_fresh40_forestC_top10_cap2_rankfloor_to2020_53bc43ab9920a493_equity.png`
