# Portfolio backtest — bt_fallen50_forestC_top10_cap2_rankfloor

- run `2b648306785a`, git `77dec7f4241df13aadb73fde82e1f1fb95bd7e2e`, backtest config `3bbf0d1552a571ad`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 660,060.78  | 480,060.78 | 11.89%         | 10.25%   | -57.54%      | 1,973.60   |
| benchmark | 180,000.00 | 664,684.90  | 484,684.90 | 11.96%         | 9.72%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006              | 16.28%       | 13.50%        | 2.78%   | 12,000.00 | 111    | 0.4370          |
| 2007              | -7.75%       | 4.41%         | -12.16% | 12,000.00 | 117    | 0.5696          |
| 2008 (GFC)        | -32.07%      | -34.28%       | 2.21%   | 12,000.00 | 120    | 0.6468          |
| 2009 (GFC)        | 41.54%       | 24.77%        | 16.77%  | 12,000.00 | 114    | 0.6968          |
| 2010              | 22.88%       | 14.30%        | 8.58%   | 12,000.00 | 117    | 0.6456          |
| 2011              | 5.94%        | 2.46%         | 3.48%   | 12,000.00 | 112    | 0.5825          |
| 2012              | 18.86%       | 17.09%        | 1.77%   | 12,000.00 | 115    | 0.5410          |
| 2013              | 36.94%       | 27.75%        | 9.19%   | 12,000.00 | 118    | 0.4943          |
| 2014              | 11.81%       | 14.50%        | -2.68%  | 12,000.00 | 119    | 0.4287          |
| 2015              | -8.93%       | -0.10%        | -8.83%  | 12,000.00 | 120    | 0.4563          |
| 2016              | 19.56%       | 14.45%        | 5.10%   | 12,000.00 | 116    | 0.5295          |
| 2017              | 20.97%       | 21.63%        | -0.66%  | 12,000.00 | 118    | 0.5033          |
| 2018              | -7.23%       | -5.13%        | -2.10%  | 12,000.00 | 120    | 0.4956          |
| 2019              | 27.04%       | 32.30%        | -5.27%  | 12,000.00 | 113    | 0.5413          |
| 2020 (COVID)      | 17.54%       | 15.68%        | 1.86%   | 12,000.00 | 119    | 0.5861          |
| 2021              | 21.98%       | 31.26%        | -9.28%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -12.24%      | -18.98%       | 6.73%   | 0.00      | 0      | —               |
| 2023              | 21.27%       | 26.71%        | -5.44%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_5y_high <= -0.5`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Technology             | 285  | 16.30% |
| Consumer Cyclical      | 260  | 14.87% |
| Industrials            | 236  | 13.49% |
| Healthcare             | 189  | 10.81% |
| Communication Services | 186  | 10.63% |
| Consumer Defensive     | 172  | 9.83%  |
| Energy                 | 160  | 9.15%  |
| Basic Materials        | 123  | 7.03%  |
| Real Estate            | 60   | 3.43%  |
| Utilities              | 42   | 2.40%  |
| Financial Services     | 36   | 2.06%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2006 | 111  | 27     | 7      | Technology             | 21.62%        |
| 2007 | 117  | 29     | 8      | Communication Services | 20.51%        |
| 2008 | 120  | 31     | 10     | Technology             | 20.00%        |
| 2009 | 114  | 31     | 9      | Industrials            | 21.05%        |
| 2010 | 117  | 26     | 8      | Industrials            | 20.51%        |
| 2011 | 112  | 31     | 10     | Technology             | 21.43%        |
| 2012 | 115  | 26     | 11     | Technology             | 20.87%        |
| 2013 | 118  | 31     | 11     | Energy                 | 17.80%        |
| 2014 | 119  | 26     | 8      | Technology             | 20.17%        |
| 2015 | 120  | 29     | 8      | Technology             | 20.00%        |
| 2016 | 116  | 30     | 9      | Technology             | 20.69%        |
| 2017 | 118  | 25     | 8      | Technology             | 20.34%        |
| 2018 | 120  | 26     | 9      | Energy                 | 17.50%        |
| 2019 | 113  | 28     | 10     | Energy                 | 18.58%        |
| 2020 | 119  | 35     | 9      | Industrials            | 20.17%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 111  | 111  | 3.43%          | 5.16%            | 55.86%  | 26.13%  | 8.11%         | 111  | 1.58%          | 2.49%            | 57.66%  | 73.87%  | 16.22%        |
| 2007     | 117  | 117  | -10.77%        | -6.40%           | 41.88%  | 79.49%  | 1.71%         | 117  | -2.67%         | -0.44%           | 47.86%  | 62.39%  | 23.08%        |
| 2008     | 120  | 120  | 0.63%          | 2.81%            | 56.67%  | 71.67%  | 2.50%         | 120  | 7.04%          | 4.39%            | 70.83%  | 24.17%  | 5.00%         |
| 2009     | 114  | 114  | 10.46%         | 10.20%           | 70.18%  | 14.91%  | 2.63%         | 114  | 3.69%          | 5.88%            | 68.42%  | 8.77%   | 15.79%        |
| 2010     | 117  | 117  | 9.86%          | 8.54%            | 61.54%  | 12.82%  | 1.71%         | 117  | 1.15%          | 8.21%            | 62.39%  | 17.95%  | 12.82%        |
| 2011     | 112  | 112  | 1.36%          | -4.61%           | 45.54%  | 41.07%  | 8.04%         | 112  | -3.61%         | -2.34%           | 46.43%  | 21.43%  | 10.71%        |
| 2012     | 115  | 115  | 8.29%          | 4.63%            | 59.13%  | 15.65%  | 0.00%         | 115  | 2.15%          | 0.92%            | 51.30%  | 8.70%   | 17.39%        |
| 2013     | 118  | 118  | -3.80%         | -2.76%           | 44.07%  | 25.42%  | 5.08%         | 118  | -5.92%         | -3.34%           | 40.68%  | 27.12%  | 12.71%        |
| 2014     | 119  | 119  | -28.07%        | -27.51%          | 21.01%  | 69.75%  | 7.56%         | 119  | -20.46%        | -16.11%          | 13.45%  | 66.39%  | 26.05%        |
| 2015     | 120  | 120  | -18.06%        | -21.95%          | 22.50%  | 71.67%  | 5.83%         | 120  | -7.92%         | -4.85%           | 31.67%  | 33.33%  | 35.83%        |
| 2016     | 116  | 116  | -0.55%         | -4.46%           | 49.14%  | 33.62%  | 8.62%         | 116  | -10.51%        | -5.73%           | 39.66%  | 37.93%  | 29.31%        |
| 2017     | 118  | 118  | 10.09%         | 6.92%            | 58.47%  | 22.88%  | 17.80%        | 118  | -5.59%         | -10.30%          | 33.90%  | 47.46%  | 31.36%        |
| 2018     | 120  | 120  | -7.29%         | -8.70%           | 43.33%  | 52.50%  | 5.00%         | 120  | -11.52%        | -10.08%          | 25.00%  | 30.00%  | 12.50%        |
| 2019     | 113  | 113  | -24.71%        | -25.47%          | 18.58%  | 67.26%  | 5.31%         | 113  | -8.20%         | -7.56%           | 34.51%  | 29.20%  | 16.81%        |
| 2020     | 119  | 119  | 17.76%         | 7.45%            | 58.82%  | 10.08%  | 1.68%         | 119  | -3.40%         | 0.47%            | 50.42%  | 31.09%  | 7.56%         |
| all buys | 1749 | 1749 | -2.14%         | -2.80%           | 47.06%  | 41.17%  | 5.43%         | 1749 | -4.33%         | -2.15%           | 44.83%  | 34.65%  | 18.24%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 111  | 1.58%       | -15.81%           | 17.40%        | -7.70%       | 9.28%    | 73.87%    | 81.80%          | 80.62%     |
| 2007     | 117  | -2.67%      | -16.05%           | 13.38%        | -12.57%      | 9.90%    | 62.39%    | 76.07%          | 76.02%     |
| 2008     | 120  | 7.04%       | -4.77%            | 11.82%        | 0.50%        | 6.55%    | 24.17%    | 48.34%          | 40.57%     |
| 2009     | 114  | 3.69%       | 1.65%             | 2.04%         | 1.87%        | 1.82%    | 8.77%     | 24.74%          | 17.35%     |
| 2010     | 117  | 1.15%       | -8.50%            | 9.66%         | -4.52%       | 5.68%    | 17.95%    | 34.40%          | 25.23%     |
| 2011     | 112  | -3.61%      | -11.46%           | 7.85%         | -5.68%       | 2.07%    | 21.43%    | 37.70%          | 25.37%     |
| 2012     | 115  | 2.15%       | -10.19%           | 12.34%        | -7.37%       | 9.52%    | 8.70%     | 37.22%          | 29.97%     |
| 2013     | 118  | -5.92%      | -21.88%           | 15.97%        | -17.87%      | 11.95%   | 27.12%    | 56.81%          | 52.84%     |
| 2014     | 119  | -20.46%     | -30.22%           | 9.76%         | -22.95%      | 2.49%    | 66.39%    | 66.11%          | 57.34%     |
| 2015     | 120  | -7.92%      | -24.69%           | 16.77%        | -16.09%      | 8.17%    | 33.33%    | 58.28%          | 49.62%     |
| 2016     | 116  | -10.51%     | -19.23%           | 8.72%         | -12.30%      | 1.79%    | 37.93%    | 52.74%          | 43.52%     |
| 2017     | 118  | -5.59%      | -30.64%           | 25.05%        | -27.02%      | 21.43%   | 47.46%    | 69.41%          | 71.21%     |
| 2018     | 120  | -11.52%     | -24.35%           | 12.83%        | -22.96%      | 11.44%   | 30.00%    | 55.51%          | 49.44%     |
| 2019     | 113  | -8.20%      | -18.29%           | 10.09%        | -10.47%      | 2.27%    | 29.20%    | 52.84%          | 40.57%     |
| 2020     | 119  | -3.40%      | -10.25%           | 6.85%         | 1.78%        | -5.18%   | 31.09%    | 46.54%          | 30.81%     |
| all buys | 1749 | -4.33%      | -13.49%           | 9.16%         | -10.97%      | 6.64%    | 34.65%    | 49.28%          | 46.07%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 111  | 3.43%       | 0.49%             | 2.95%         | -2.37%       | 5.80%    | 26.13%    | 48.73%          | 38.05%     |
| 2007     | 117  | -10.77%     | -19.11%           | 8.34%         | -17.60%      | 6.83%    | 79.49%    | 80.53%          | 81.34%     |
| 2008     | 120  | 0.63%       | 9.54%             | -8.90%        | 9.00%        | -8.36%   | 71.67%    | 69.73%          | 70.16%     |
| 2009     | 114  | 10.46%      | 41.43%            | -30.97%       | 20.33%       | -9.87%   | 14.91%    | 21.98%          | 16.56%     |
| 2010     | 117  | 9.86%       | 3.52%             | 6.34%         | 5.22%        | 4.63%    | 12.82%    | 40.56%          | 30.21%     |
| 2011     | 112  | 1.36%       | -12.37%           | 13.73%        | -13.87%      | 15.23%   | 41.07%    | 58.29%          | 57.33%     |
| 2012     | 115  | 8.29%       | 8.23%             | 0.05%         | 6.83%        | 1.45%    | 15.65%    | 35.49%          | 27.36%     |
| 2013     | 118  | -3.80%      | 6.69%             | -10.50%       | 2.80%        | -6.60%   | 25.42%    | 37.13%          | 29.96%     |
| 2014     | 119  | -28.07%     | -26.51%           | -1.56%        | -25.75%      | -2.33%   | 69.75%    | 70.05%          | 64.16%     |
| 2015     | 120  | -18.06%     | -22.63%           | 4.56%         | -16.54%      | -1.52%   | 71.67%    | 69.36%          | 64.62%     |
| 2016     | 116  | -0.55%      | 1.77%             | -2.32%        | 9.19%        | -9.74%   | 33.62%    | 44.05%          | 36.08%     |
| 2017     | 118  | 10.09%      | -4.15%            | 14.25%        | -2.40%       | 12.49%   | 22.88%    | 51.64%          | 42.91%     |
| 2018     | 120  | -7.29%      | -25.64%           | 18.35%        | -24.97%      | 17.68%   | 52.50%    | 72.13%          | 69.55%     |
| 2019     | 113  | -24.71%     | -12.05%           | -12.66%       | -19.71%      | -5.01%   | 67.26%    | 64.84%          | 61.29%     |
| 2020     | 119  | 17.76%      | 69.14%            | -51.37%       | 37.84%       | -20.07%  | 10.08%    | 25.76%          | 18.60%     |
| all buys | 1749 | -2.14%      | 6.58%             | -8.71%        | -2.14%       | 0.00%    | 41.17%    | 48.83%          | 47.35%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 50
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 756.2 (min 348)
- mean with a tradable quote: 740.1 (min 344)
- forced delisting liquidations: 138 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 16 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fallen50_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `ebda639d8b5535cb`, train run `b98ceed78486`, folds 2006–2020 (from `experiments/models/forest_fallen50_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0_b98ceed78486`)

### Artifacts

- equity_curve: `reports/backtest/bt_fallen50_forestC_top10_cap2_rankfloor_3bbf0d1552a571ad_equity.csv`
- trades: `reports/backtest/bt_fallen50_forestC_top10_cap2_rankfloor_3bbf0d1552a571ad_trades.csv`
- rebalances: `reports/backtest/bt_fallen50_forestC_top10_cap2_rankfloor_3bbf0d1552a571ad_rebalances.csv`
- equity_plot: `reports/backtest/bt_fallen50_forestC_top10_cap2_rankfloor_3bbf0d1552a571ad_equity.png`
