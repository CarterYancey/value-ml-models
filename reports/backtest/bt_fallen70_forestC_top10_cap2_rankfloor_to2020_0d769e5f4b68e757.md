# Portfolio backtest — bt_fallen70_forestC_top10_cap2_rankfloor_to2020

- run `2f71f638428c`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `0d769e5f4b68e757`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2020-12-31; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 476,626.63  | 296,626.63 | 12.02%         | 6.78%    | -75.54%      | 1,621.92   |
| benchmark | 180,000.00 | 500,058.34  | 320,058.34 | 12.58%         | 9.67%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year         | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ------------ | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006         | -11.25%      | 13.50%        | -24.75% | 12,000.00 | 114    | 0.2972          |
| 2007         | -31.40%      | 4.41%         | -35.81% | 12,000.00 | 114    | 0.4759          |
| 2008 (GFC)   | -32.04%      | -34.28%       | 2.23%   | 12,000.00 | 119    | 0.5117          |
| 2009 (GFC)   | 60.70%       | 24.77%        | 35.93%  | 12,000.00 | 120    | 0.5702          |
| 2010         | 31.28%       | 14.30%        | 16.98%  | 12,000.00 | 120    | 0.5241          |
| 2011         | -5.18%       | 2.46%         | -7.63%  | 12,000.00 | 115    | 0.5029          |
| 2012         | 16.39%       | 17.09%        | -0.70%  | 12,000.00 | 118    | 0.4699          |
| 2013         | 42.09%       | 27.75%        | 14.33%  | 12,000.00 | 116    | 0.4489          |
| 2014         | 4.12%        | 14.50%        | -10.38% | 12,000.00 | 115    | 0.3799          |
| 2015         | -3.76%       | -0.10%        | -3.65%  | 12,000.00 | 120    | 0.3970          |
| 2016         | 20.90%       | 14.45%        | 6.44%   | 12,000.00 | 120    | 0.4577          |
| 2017         | 21.21%       | 21.63%        | -0.42%  | 12,000.00 | 118    | 0.4313          |
| 2018         | -8.94%       | -5.13%        | -3.81%  | 12,000.00 | 116    | 0.4283          |
| 2019         | 16.63%       | 32.30%        | -15.68% | 12,000.00 | 115    | 0.4742          |
| 2020 (COVID) | 25.28%       | 17.28%        | 8.00%   | 12,000.00 | 120    | 0.5274          |

**Defensive hypothesis:** Benchmark down-years in window: 3; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_5y_high <= -0.7`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Technology             | 281  | 15.97% |
| Consumer Cyclical      | 276  | 15.68% |
| Industrials            | 258  | 14.66% |
| Communication Services | 222  | 12.61% |
| Energy                 | 188  | 10.68% |
| Healthcare             | 183  | 10.40% |
| Consumer Defensive     | 147  | 8.35%  |
| Basic Materials        | 114  | 6.48%  |
| Financial Services     | 36   | 2.05%  |
| Real Estate            | 30   | 1.70%  |
| Utilities              | 21   | 1.19%  |
| unknown                | 4    | 0.23%  |

| year | buys | stocks | groups | largest_group   | largest_share |
| ---- | ---- | ------ | ------ | --------------- | ------------- |
| 2006 | 114  | 18     | 7      | Healthcare      | 21.05%        |
| 2007 | 114  | 27     | 9      | Healthcare      | 18.42%        |
| 2008 | 119  | 26     | 9      | Healthcare      | 20.17%        |
| 2009 | 120  | 32     | 9      | Technology      | 20.00%        |
| 2010 | 120  | 27     | 7      | Technology      | 20.00%        |
| 2011 | 115  | 24     | 8      | Technology      | 20.87%        |
| 2012 | 118  | 31     | 9      | Technology      | 19.49%        |
| 2013 | 116  | 28     | 9      | Industrials     | 18.10%        |
| 2014 | 115  | 25     | 9      | Technology      | 18.26%        |
| 2015 | 120  | 30     | 9      | Basic Materials | 20.00%        |
| 2016 | 120  | 31     | 10     | Technology      | 17.50%        |
| 2017 | 118  | 22     | 10     | Industrials     | 20.34%        |
| 2018 | 116  | 28     | 11     | Energy          | 20.69%        |
| 2019 | 115  | 30     | 9      | Energy          | 20.87%        |
| 2020 | 120  | 28     | 9      | Healthcare      | 20.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 114  | 114  | -45.53%        | -50.78%          | 11.40%  | 79.82%  | 10.53%        | 114  | -43.72%        | -37.72%          | 0.88%   | 100.00% | 42.11%        |
| 2007     | 114  | 114  | -4.85%         | -17.60%          | 42.98%  | 65.79%  | 8.77%         | 114  | 2.29%          | 2.63%            | 53.51%  | 57.02%  | 32.46%        |
| 2008     | 119  | 119  | 10.53%         | 7.26%            | 53.78%  | 56.30%  | 0.00%         | 119  | 1.42%          | 1.84%            | 53.78%  | 42.02%  | 17.65%        |
| 2009     | 120  | 120  | 29.86%         | 20.75%           | 70.00%  | 18.33%  | 0.83%         | 120  | 2.83%          | -0.17%           | 49.17%  | 25.83%  | 10.00%        |
| 2010     | 120  | 120  | 7.59%          | 2.66%            | 54.17%  | 34.17%  | 8.33%         | 120  | -1.86%         | -0.44%           | 48.33%  | 24.17%  | 25.83%        |
| 2011     | 115  | 115  | -4.28%         | -5.93%           | 42.61%  | 46.09%  | 5.22%         | 115  | -2.25%         | 2.05%            | 53.04%  | 22.61%  | 21.74%        |
| 2012     | 118  | 118  | 15.41%         | 8.45%            | 61.86%  | 13.56%  | 5.93%         | 118  | 3.90%          | 3.99%            | 59.32%  | 16.10%  | 13.56%        |
| 2013     | 116  | 116  | 6.87%          | 6.18%            | 55.17%  | 23.28%  | 6.90%         | 116  | -12.60%        | -6.12%           | 34.48%  | 42.24%  | 23.28%        |
| 2014     | 115  | 115  | -13.37%        | -14.82%          | 26.96%  | 59.13%  | 8.70%         | 115  | -14.57%        | -12.15%          | 25.22%  | 52.17%  | 32.17%        |
| 2015     | 120  | 120  | -5.43%         | -19.56%          | 40.00%  | 59.17%  | 4.17%         | 120  | -7.10%         | -7.86%           | 37.50%  | 36.67%  | 30.83%        |
| 2016     | 120  | 120  | -0.72%         | 0.84%            | 50.00%  | 36.67%  | 15.83%        | 120  | -10.35%        | -5.87%           | 39.17%  | 40.00%  | 20.00%        |
| 2017     | 118  | 118  | 9.61%          | -0.22%           | 49.15%  | 37.29%  | 5.93%         | 118  | -13.47%        | -13.47%          | 27.97%  | 52.54%  | 20.34%        |
| 2018     | 116  | 116  | -26.89%        | -31.23%          | 24.14%  | 69.83%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2019     | 115  | 115  | -26.70%        | -34.64%          | 25.22%  | 66.96%  | 4.35%         | 0    | —              | —                | —       | —       | —             |
| 2020     | 120  | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 1760 | 1640 | -3.17%         | -7.13%           | 43.60%  | 47.38%  | 6.10%         | 1409 | -7.85%         | -4.96%           | 40.31%  | 42.37%  | 24.06%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 114  | -43.72%     | -18.33%           | -25.39%       | -22.01%      | -21.71%  | 100.00%   | 83.82%          | 83.67%     |
| 2007     | 114  | 2.29%       | -20.37%           | 22.65%        | -17.61%      | 19.90%   | 57.02%    | 77.70%          | 76.25%     |
| 2008     | 119  | 1.42%       | -11.65%           | 13.07%        | -13.01%      | 14.43%   | 42.02%    | 55.60%          | 57.72%     |
| 2009     | 120  | 2.83%       | 1.70%             | 1.13%         | 1.48%        | 1.35%    | 25.83%    | 28.84%          | 25.33%     |
| 2010     | 120  | -1.86%      | -13.22%           | 11.36%        | -6.12%       | 4.27%    | 24.17%    | 42.38%          | 30.93%     |
| 2011     | 115  | -2.25%      | -16.27%           | 14.02%        | -5.16%       | 2.91%    | 22.61%    | 45.57%          | 28.41%     |
| 2012     | 118  | 3.90%       | -14.45%           | 18.35%        | -10.50%      | 14.40%   | 16.10%    | 44.24%          | 38.92%     |
| 2013     | 116  | -12.60%     | -28.77%           | 16.17%        | -28.32%      | 15.72%   | 42.24%    | 63.89%          | 61.19%     |
| 2014     | 115  | -14.57%     | -38.15%           | 23.58%        | -38.02%      | 23.45%   | 52.17%    | 74.19%          | 72.03%     |
| 2015     | 120  | -7.10%      | -31.71%           | 24.61%        | -20.26%      | 13.17%   | 36.67%    | 65.32%          | 49.44%     |
| 2016     | 120  | -10.35%     | -25.74%           | 15.39%        | -20.68%      | 10.32%   | 40.00%    | 60.23%          | 57.61%     |
| 2017     | 118  | -13.47%     | -36.85%           | 23.38%        | -34.62%      | 21.16%   | 52.54%    | 73.51%          | 73.10%     |
| all buys | 1409 | -7.85%      | -17.22%           | 9.37%         | -17.82%      | 9.97%    | 42.37%    | 54.50%          | 54.34%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 114  | -45.53%     | 7.17%             | -52.70%       | -6.15%       | -39.39%  | 79.82%    | 51.15%          | 54.96%     |
| 2007     | 114  | -4.85%      | -22.93%           | 18.08%        | -19.94%      | 15.09%   | 65.79%    | 81.53%          | 79.26%     |
| 2008     | 119  | 10.53%      | 9.93%             | 0.60%         | 4.08%        | 6.45%    | 56.30%    | 71.19%          | 71.40%     |
| 2009     | 120  | 29.86%      | 63.66%            | -33.80%       | 40.62%       | -10.76%  | 18.33%    | 23.64%          | 22.39%     |
| 2010     | 120  | 7.59%       | 1.61%             | 5.98%         | 5.08%        | 2.51%    | 34.17%    | 46.48%          | 39.68%     |
| 2011     | 115  | -4.28%      | -16.33%           | 12.04%        | -8.32%       | 4.04%    | 46.09%    | 63.52%          | 55.89%     |
| 2012     | 118  | 15.41%      | 10.12%            | 5.28%         | 17.88%       | -2.47%   | 13.56%    | 41.42%          | 31.71%     |
| 2013     | 116  | 6.87%       | 10.21%            | -3.34%        | 12.68%       | -5.81%   | 23.28%    | 42.34%          | 33.66%     |
| 2014     | 115  | -13.37%     | -32.15%           | 18.78%        | -39.62%      | 26.25%   | 59.13%    | 75.24%          | 76.80%     |
| 2015     | 120  | -5.43%      | -27.99%           | 22.56%        | -11.61%      | 6.17%    | 59.17%    | 73.76%          | 64.08%     |
| 2016     | 120  | -0.72%      | -1.03%            | 0.31%         | 6.39%        | -7.11%   | 36.67%    | 51.54%          | 43.26%     |
| 2017     | 118  | 9.61%       | -3.81%            | 13.42%        | 2.60%        | 7.01%    | 37.29%    | 56.85%          | 51.22%     |
| 2018     | 116  | -26.89%     | -30.63%           | 3.74%         | -31.15%      | 4.25%    | 69.83%    | 76.59%          | 75.70%     |
| 2019     | 115  | -26.70%     | -6.38%            | -20.32%       | -21.94%      | -4.75%   | 66.96%    | 66.54%          | 64.73%     |
| all buys | 1640 | -3.17%      | 4.83%             | -8.00%        | -3.29%       | 0.11%    | 47.38%    | 54.22%          | 54.45%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 40
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 389.5 (min 180)
- mean with a tradable quote: 380.1 (min 180)
- forced delisting liquidations: 122 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 20 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fallen70_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `7ffa4401b798e324`, train run `440e6e4b7645`, folds 2006–2020 (from `experiments/models/forest_fallen70_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_440e6e4b7645`)

### Artifacts

- equity_curve: `reports/backtest/bt_fallen70_forestC_top10_cap2_rankfloor_to2020_0d769e5f4b68e757_equity.csv`
- trades: `reports/backtest/bt_fallen70_forestC_top10_cap2_rankfloor_to2020_0d769e5f4b68e757_trades.csv`
- rebalances: `reports/backtest/bt_fallen70_forestC_top10_cap2_rankfloor_to2020_0d769e5f4b68e757_rebalances.csv`
- equity_plot: `reports/backtest/bt_fallen70_forestC_top10_cap2_rankfloor_to2020_0d769e5f4b68e757_equity.png`
