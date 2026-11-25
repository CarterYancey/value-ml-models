# Portfolio backtest — bt_fresh30_forestC_top10_cap2_rankfloor_to2020

- run `cd3ae931debe`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `b3fc317e0f4a766d`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2020-12-31; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 499,881.29  | 319,881.29 | 12.58%         | 9.90%    | -57.34%      | 1,182.56   |
| benchmark | 180,000.00 | 500,058.34  | 320,058.34 | 12.58%         | 9.67%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year         | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ------------ | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006         | 11.31%       | 13.50%        | -2.19%  | 12,000.00 | 111    | 0.4907          |
| 2007         | -9.91%       | 4.41%         | -14.32% | 12,000.00 | 115    | 0.5666          |
| 2008 (GFC)   | -26.63%      | -34.28%       | 7.65%   | 12,000.00 | 120    | 0.7094          |
| 2009 (GFC)   | 34.22%       | 24.77%        | 9.46%   | 12,000.00 | 120    | 0.7323          |
| 2010         | 22.53%       | 14.30%        | 8.23%   | 12,000.00 | 120    | 0.5312          |
| 2011         | 3.69%        | 2.46%         | 1.24%   | 12,000.00 | 120    | 0.4767          |
| 2012         | 16.73%       | 17.09%        | -0.36%  | 12,000.00 | 120    | 0.4429          |
| 2013         | 38.58%       | 27.75%        | 10.82%  | 12,000.00 | 120    | 0.4046          |
| 2014         | 3.19%        | 14.50%        | -11.31% | 12,000.00 | 119    | 0.4046          |
| 2015         | -2.44%       | -0.10%        | -2.33%  | 12,000.00 | 117    | 0.4738          |
| 2016         | 22.75%       | 14.45%        | 8.30%   | 12,000.00 | 113    | 0.5450          |
| 2017         | 21.59%       | 21.63%        | -0.04%  | 12,000.00 | 115    | 0.4630          |
| 2018         | -9.25%       | -5.13%        | -4.12%  | 12,000.00 | 116    | 0.4786          |
| 2019         | 28.83%       | 32.30%        | -3.47%  | 12,000.00 | 115    | 0.5558          |
| 2020 (COVID) | 15.54%       | 17.28%        | -1.74%  | 12,000.00 | 111    | 0.5881          |

**Defensive hypothesis:** Benchmark down-years in window: 3; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_52w_high <= -0.3`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Cyclical      | 322  | 18.38% |
| Industrials            | 297  | 16.95% |
| Technology             | 280  | 15.98% |
| Healthcare             | 183  | 10.45% |
| Consumer Defensive     | 181  | 10.33% |
| Basic Materials        | 163  | 9.30%  |
| Communication Services | 114  | 6.51%  |
| Energy                 | 108  | 6.16%  |
| Real Estate            | 53   | 3.03%  |
| Financial Services     | 45   | 2.57%  |
| Utilities              | 6    | 0.34%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2006 | 111  | 28     | 7      | Consumer Cyclical  | 21.62%        |
| 2007 | 115  | 28     | 10     | Industrials        | 18.26%        |
| 2008 | 120  | 34     | 10     | Consumer Cyclical  | 20.00%        |
| 2009 | 120  | 29     | 9      | Industrials        | 20.00%        |
| 2010 | 120  | 35     | 10     | Technology         | 20.00%        |
| 2011 | 120  | 35     | 8      | Consumer Cyclical  | 20.00%        |
| 2012 | 120  | 37     | 9      | Technology         | 20.00%        |
| 2013 | 120  | 35     | 9      | Technology         | 18.33%        |
| 2014 | 119  | 30     | 9      | Basic Materials    | 19.33%        |
| 2015 | 117  | 34     | 9      | Energy             | 20.51%        |
| 2016 | 113  | 34     | 9      | Consumer Cyclical  | 21.24%        |
| 2017 | 115  | 34     | 8      | Consumer Cyclical  | 20.87%        |
| 2018 | 116  | 33     | 7      | Consumer Defensive | 20.69%        |
| 2019 | 115  | 33     | 9      | Industrials        | 20.87%        |
| 2020 | 111  | 35     | 10     | Industrials        | 18.92%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 111  | 111  | 2.63%          | 2.96%            | 52.25%  | 31.53%  | 5.41%         | 111  | -3.33%         | -0.98%           | 48.65%  | 76.58%  | 13.51%        |
| 2007     | 115  | 115  | -9.75%         | -12.12%          | 31.30%  | 79.13%  | 11.30%        | 115  | -1.71%         | -0.55%           | 47.83%  | 71.30%  | 15.65%        |
| 2008     | 120  | 120  | 10.22%         | 7.31%            | 62.50%  | 69.17%  | 0.00%         | 120  | 6.25%          | 6.33%            | 75.83%  | 20.83%  | 10.00%        |
| 2009     | 120  | 120  | 16.67%         | 15.49%           | 73.33%  | 7.50%   | 0.00%         | 120  | 6.59%          | 6.59%            | 79.17%  | 4.17%   | 2.50%         |
| 2010     | 120  | 120  | -1.01%         | -8.31%           | 39.17%  | 40.83%  | 7.50%         | 120  | -1.85%         | -2.19%           | 42.50%  | 15.00%  | 12.50%        |
| 2011     | 120  | 120  | -11.33%        | -9.78%           | 31.67%  | 51.67%  | 5.00%         | 120  | -9.69%         | -6.17%           | 38.33%  | 30.83%  | 13.33%        |
| 2012     | 120  | 120  | 0.83%          | 1.57%            | 52.50%  | 25.83%  | 7.50%         | 120  | -6.51%         | -3.64%           | 39.17%  | 26.67%  | 13.33%        |
| 2013     | 120  | 120  | -9.15%         | -13.45%          | 31.67%  | 40.83%  | 0.83%         | 120  | -15.85%        | -10.92%          | 31.67%  | 49.17%  | 5.83%         |
| 2014     | 119  | 119  | -2.35%         | -6.78%           | 39.50%  | 43.70%  | 1.68%         | 119  | -7.12%         | -4.01%           | 41.18%  | 36.13%  | 5.88%         |
| 2015     | 117  | 117  | -4.87%         | -6.40%           | 38.46%  | 52.14%  | 0.00%         | 117  | -10.34%        | -9.06%           | 28.21%  | 41.03%  | 5.13%         |
| 2016     | 113  | 113  | -1.28%         | -3.50%           | 46.90%  | 27.43%  | 0.00%         | 113  | -3.82%         | -4.23%           | 40.71%  | 29.20%  | 7.96%         |
| 2017     | 115  | 115  | -14.56%        | -11.70%          | 26.96%  | 44.35%  | 13.04%        | 115  | -18.16%        | -11.76%          | 23.48%  | 50.43%  | 15.65%        |
| 2018     | 116  | 116  | -1.92%         | -4.29%           | 44.83%  | 44.83%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2019     | 115  | 115  | -13.80%        | -16.01%          | 23.48%  | 52.17%  | 6.96%         | 0    | —              | —                | —       | —       | —             |
| 2020     | 111  | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 1752 | 1641 | -2.78%         | -5.00%           | 42.54%  | 43.63%  | 4.20%         | 1410 | -5.44%         | -2.41%           | 44.82%  | 37.23%  | 10.07%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 111  | -3.33%      | -18.55%           | 15.22%        | -10.14%      | 6.81%    | 76.58%    | 81.82%          | 75.96%     |
| 2007     | 115  | -1.71%      | -17.34%           | 15.63%        | -8.17%       | 6.46%    | 71.30%    | 76.89%          | 74.77%     |
| 2008     | 120  | 6.25%       | -3.42%            | 9.67%         | 3.04%        | 3.21%    | 20.83%    | 46.98%          | 36.07%     |
| 2009     | 120  | 6.59%       | 2.34%             | 4.25%         | 1.19%        | 5.40%    | 4.17%     | 23.09%          | 16.37%     |
| 2010     | 120  | -1.85%      | -18.02%           | 16.17%        | -9.84%       | 8.00%    | 15.00%    | 49.10%          | 36.74%     |
| 2011     | 120  | -9.69%      | -17.52%           | 7.83%         | -12.18%      | 2.49%    | 30.83%    | 45.55%          | 39.37%     |
| 2012     | 120  | -6.51%      | -14.75%           | 8.24%         | -14.07%      | 7.56%    | 26.67%    | 43.33%          | 41.98%     |
| 2013     | 120  | -15.85%     | -25.17%           | 9.32%         | -21.07%      | 5.22%    | 49.17%    | 62.25%          | 56.75%     |
| 2014     | 119  | -7.12%      | -28.11%           | 20.98%        | -16.24%      | 9.12%    | 36.13%    | 64.07%          | 48.24%     |
| 2015     | 117  | -10.34%     | -22.82%           | 12.48%        | -16.11%      | 5.77%    | 41.03%    | 56.10%          | 48.11%     |
| 2016     | 113  | -3.82%      | -16.38%           | 12.56%        | -9.94%       | 6.13%    | 29.20%    | 48.37%          | 38.89%     |
| 2017     | 115  | -18.16%     | -29.04%           | 10.88%        | -23.58%      | 5.42%    | 50.43%    | 67.06%          | 63.30%     |
| all buys | 1410 | -5.44%      | -13.58%           | 8.14%         | -11.40%      | 5.96%    | 37.23%    | 50.55%          | 47.76%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 111  | 2.63%       | -1.53%            | 4.16%         | -1.64%       | 4.28%    | 31.53%    | 51.94%          | 42.28%     |
| 2007     | 115  | -9.75%      | -18.37%           | 8.62%         | -12.57%      | 2.82%    | 79.13%    | 80.32%          | 76.71%     |
| 2008     | 120  | 10.22%      | 7.25%             | 2.97%         | 5.29%        | 4.93%    | 69.17%    | 71.01%          | 71.13%     |
| 2009     | 120  | 16.67%      | 39.61%            | -22.94%       | 15.74%       | 0.93%    | 7.50%     | 20.08%          | 16.04%     |
| 2010     | 120  | -1.01%      | -8.31%            | 7.29%         | 0.74%        | -1.75%   | 40.83%    | 56.36%          | 42.84%     |
| 2011     | 120  | -11.33%     | -17.54%           | 6.21%         | -16.05%      | 4.72%    | 51.67%    | 60.15%          | 61.11%     |
| 2012     | 120  | 0.83%       | 0.36%             | 0.46%         | 1.68%        | -0.85%   | 25.83%    | 42.07%          | 35.96%     |
| 2013     | 120  | -9.15%      | 2.53%             | -11.69%       | -5.14%       | -4.01%   | 40.83%    | 43.74%          | 43.87%     |
| 2014     | 119  | -2.35%      | -19.38%           | 17.03%        | -13.14%      | 10.79%   | 43.70%    | 66.53%          | 56.16%     |
| 2015     | 117  | -4.87%      | -20.97%           | 16.11%        | -17.89%      | 13.02%   | 52.14%    | 68.34%          | 67.98%     |
| 2016     | 113  | -1.28%      | 3.37%             | -4.65%        | 1.46%        | -2.74%   | 27.43%    | 40.90%          | 34.67%     |
| 2017     | 115  | -14.56%     | -1.47%            | -13.09%       | -3.24%       | -11.32%  | 44.35%    | 53.51%          | 48.00%     |
| 2018     | 116  | -1.92%      | -23.99%           | 22.07%        | -12.05%      | 10.14%   | 44.83%    | 70.32%          | 57.80%     |
| 2019     | 115  | -13.80%     | -10.36%           | -3.44%        | -13.83%      | 0.03%    | 52.17%    | 62.43%          | 57.02%     |
| all buys | 1641 | -2.78%      | 0.70%             | -3.48%        | -5.00%       | 2.22%    | 43.63%    | 53.06%          | 50.80%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 40
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 908.7 (min 348)
- mean with a tradable quote: 897.6 (min 344)
- forced delisting liquidations: 103 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 22 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fresh30_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `5344934b5b14329c`, train run `b0edc2b3f4b1`, folds 2006–2020 (from `experiments/models/forest_fresh30_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_b0edc2b3f4b1`)

### Artifacts

- equity_curve: `reports/backtest/bt_fresh30_forestC_top10_cap2_rankfloor_to2020_b3fc317e0f4a766d_equity.csv`
- trades: `reports/backtest/bt_fresh30_forestC_top10_cap2_rankfloor_to2020_b3fc317e0f4a766d_trades.csv`
- rebalances: `reports/backtest/bt_fresh30_forestC_top10_cap2_rankfloor_to2020_b3fc317e0f4a766d_rebalances.csv`
- equity_plot: `reports/backtest/bt_fresh30_forestC_top10_cap2_rankfloor_to2020_b3fc317e0f4a766d_equity.png`
