# Portfolio backtest — bt_fallen30_forestC_top10_cap2_rankfloor

- run `f2b564bcd706`, git `77dec7f4241df13aadb73fde82e1f1fb95bd7e2e`, backtest config `3bf38d97bca05b0b`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 634,783.70  | 454,783.70 | 11.55%         | 10.31%   | -48.12%      | 1,186.48   |
| benchmark | 180,000.00 | 664,684.90  | 484,684.90 | 11.96%         | 9.72%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2006              | 15.79%       | 13.50%        | 2.29%  | 12,000.00 | 120    | 0.5196          |
| 2007              | -1.69%       | 4.41%         | -6.10% | 12,000.00 | 117    | 0.6713          |
| 2008 (GFC)        | -23.88%      | -34.28%       | 10.40% | 12,000.00 | 117    | 0.7429          |
| 2009 (GFC)        | 28.26%       | 24.77%        | 3.50%  | 12,000.00 | 120    | 0.7628          |
| 2010              | 19.10%       | 14.30%        | 4.80%  | 12,000.00 | 118    | 0.7180          |
| 2011              | 5.12%        | 2.46%         | 2.66%  | 12,000.00 | 119    | 0.6548          |
| 2012              | 18.42%       | 17.09%        | 1.33%  | 12,000.00 | 120    | 0.5706          |
| 2013              | 35.17%       | 27.75%        | 7.42%  | 12,000.00 | 120    | 0.5386          |
| 2014              | 12.07%       | 14.50%        | -2.43% | 12,000.00 | 120    | 0.4791          |
| 2015              | -5.30%       | -0.10%        | -5.19% | 12,000.00 | 120    | 0.5115          |
| 2016              | 19.38%       | 14.45%        | 4.93%  | 12,000.00 | 120    | 0.6094          |
| 2017              | 20.79%       | 21.63%        | -0.84% | 12,000.00 | 114    | 0.5655          |
| 2018              | -9.04%       | -5.13%        | -3.91% | 12,000.00 | 118    | 0.5570          |
| 2019              | 28.21%       | 32.30%        | -4.10% | 12,000.00 | 116    | 0.6213          |
| 2020 (COVID)      | 11.96%       | 15.68%        | -3.73% | 12,000.00 | 111    | 0.6530          |
| 2021              | 26.05%       | 31.26%        | -5.21% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -13.81%      | -18.98%       | 5.17%  | 0.00      | 0      | —               |
| 2023              | 20.81%       | 26.71%        | -5.90% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `dist_5y_high <= -0.3`
- `dollar_volume_3m >= 100000`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Industrials            | 297  | 16.78% |
| Technology             | 237  | 13.39% |
| Consumer Cyclical      | 210  | 11.86% |
| Consumer Defensive     | 180  | 10.17% |
| Real Estate            | 160  | 9.04%  |
| Healthcare             | 158  | 8.93%  |
| Communication Services | 144  | 8.14%  |
| Energy                 | 138  | 7.80%  |
| Utilities              | 120  | 6.78%  |
| Basic Materials        | 96   | 5.42%  |
| Financial Services     | 30   | 1.69%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2006 | 120  | 31     | 9      | Healthcare         | 20.00%        |
| 2007 | 117  | 31     | 9      | Healthcare         | 20.51%        |
| 2008 | 117  | 32     | 11     | Consumer Cyclical  | 17.95%        |
| 2009 | 120  | 27     | 9      | Industrials        | 20.00%        |
| 2010 | 118  | 22     | 8      | Utilities          | 17.80%        |
| 2011 | 119  | 32     | 10     | Healthcare         | 17.65%        |
| 2012 | 120  | 25     | 10     | Utilities          | 20.00%        |
| 2013 | 120  | 36     | 10     | Industrials        | 20.00%        |
| 2014 | 120  | 28     | 9      | Industrials        | 20.00%        |
| 2015 | 120  | 33     | 10     | Real Estate        | 15.00%        |
| 2016 | 120  | 34     | 10     | Industrials        | 20.00%        |
| 2017 | 114  | 31     | 10     | Technology         | 21.05%        |
| 2018 | 118  | 31     | 9      | Consumer Defensive | 17.80%        |
| 2019 | 116  | 31     | 9      | Real Estate        | 20.69%        |
| 2020 | 111  | 30     | 10     | Industrials        | 21.62%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 120  | 120  | 1.52%          | 5.29%            | 59.17%  | 25.00%  | 1.67%         | 120  | 4.25%          | 6.30%            | 72.50%  | 59.17%  | 2.50%         |
| 2007     | 117  | 117  | -4.05%         | -2.01%           | 45.30%  | 73.50%  | 5.13%         | 117  | 0.46%          | 1.05%            | 53.85%  | 65.81%  | 12.82%        |
| 2008     | 117  | 117  | 8.96%          | 9.17%            | 71.79%  | 73.50%  | 0.00%         | 117  | 5.12%          | 5.85%            | 70.94%  | 24.79%  | 7.69%         |
| 2009     | 120  | 120  | -0.29%         | -1.56%           | 46.67%  | 15.83%  | 2.50%         | 120  | -2.99%         | 0.43%            | 50.83%  | 15.83%  | 7.50%         |
| 2010     | 118  | 118  | 1.32%          | -2.18%           | 44.92%  | 25.42%  | 2.54%         | 118  | 0.04%          | -1.11%           | 47.46%  | 8.47%   | 12.71%        |
| 2011     | 119  | 119  | -3.05%         | -2.21%           | 40.34%  | 33.61%  | 5.04%         | 119  | 1.59%          | 2.11%            | 61.34%  | 14.29%  | 5.04%         |
| 2012     | 120  | 120  | 3.17%          | 2.22%            | 52.50%  | 14.17%  | 0.00%         | 120  | 1.98%          | 3.37%            | 58.33%  | 8.33%   | 0.00%         |
| 2013     | 120  | 120  | -3.36%         | -4.45%           | 40.00%  | 19.17%  | 0.00%         | 120  | -5.19%         | -2.96%           | 42.50%  | 32.50%  | 2.50%         |
| 2014     | 120  | 120  | -19.86%        | -18.02%          | 28.33%  | 61.67%  | 0.00%         | 120  | -10.98%        | -11.66%          | 26.67%  | 51.67%  | 10.00%        |
| 2015     | 120  | 120  | -4.23%         | -6.26%           | 39.17%  | 54.17%  | 0.00%         | 120  | -3.73%         | -2.27%           | 48.33%  | 27.50%  | 17.50%        |
| 2016     | 120  | 120  | -0.90%         | -3.13%           | 42.50%  | 22.50%  | 5.00%         | 120  | -7.28%         | -8.25%           | 21.67%  | 31.67%  | 12.50%        |
| 2017     | 114  | 114  | -9.69%         | -9.84%           | 26.32%  | 35.09%  | 6.14%         | 114  | -18.18%        | -17.53%          | 8.77%   | 64.04%  | 19.30%        |
| 2018     | 118  | 118  | -11.24%        | -15.99%          | 31.36%  | 60.17%  | 1.69%         | 118  | -11.48%        | -13.87%          | 23.73%  | 39.83%  | 10.17%        |
| 2019     | 116  | 116  | -20.27%        | -20.16%          | 13.79%  | 59.48%  | 2.59%         | 116  | -9.07%         | -9.40%           | 22.41%  | 31.90%  | 11.21%        |
| 2020     | 111  | 111  | -0.87%         | -7.76%           | 39.64%  | 17.12%  | 0.00%         | 111  | -2.14%         | -1.61%           | 44.14%  | 20.72%  | 2.70%         |
| all buys | 1770 | 1770 | -4.17%         | -4.39%           | 41.53%  | 39.32%  | 2.15%         | 1770 | -3.81%         | -2.42%           | 43.67%  | 33.05%  | 8.93%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 120  | 4.25%       | -13.64%           | 17.90%        | -4.38%       | 8.63%    | 59.17%    | 80.49%          | 74.82%     |
| 2007     | 117  | 0.46%       | -12.07%           | 12.53%        | -5.03%       | 5.49%    | 65.81%    | 74.16%          | 72.37%     |
| 2008     | 117  | 5.12%       | -2.07%            | 7.19%         | 2.16%        | 2.96%    | 24.79%    | 44.50%          | 35.93%     |
| 2009     | 120  | -2.99%      | 1.29%             | -4.28%        | -0.54%       | -2.46%   | 15.83%    | 22.33%          | 14.37%     |
| 2010     | 118  | 0.04%       | -5.77%            | 5.82%         | -2.44%       | 2.48%    | 8.47%     | 28.72%          | 18.64%     |
| 2011     | 119  | 1.59%       | -8.85%            | 10.44%        | -4.89%       | 6.49%    | 14.29%    | 32.48%          | 23.54%     |
| 2012     | 120  | 1.98%       | -8.05%            | 10.03%        | -5.67%       | 7.65%    | 8.33%     | 32.20%          | 24.85%     |
| 2013     | 120  | -5.19%      | -17.35%           | 12.16%        | -12.38%      | 7.19%    | 32.50%    | 51.22%          | 46.24%     |
| 2014     | 120  | -10.98%     | -23.18%           | 12.20%        | -16.59%      | 5.61%    | 51.67%    | 58.68%          | 56.13%     |
| 2015     | 120  | -3.73%      | -18.62%           | 14.89%        | -13.57%      | 9.83%    | 27.50%    | 50.37%          | 45.24%     |
| 2016     | 120  | -7.28%      | -14.65%           | 7.37%         | -10.28%      | 3.00%    | 31.67%    | 45.44%          | 37.80%     |
| 2017     | 114  | -18.18%     | -25.08%           | 6.90%         | -20.60%      | 2.41%    | 64.04%    | 64.65%          | 62.63%     |
| 2018     | 118  | -11.48%     | -19.83%           | 8.35%         | -16.81%      | 5.33%    | 39.83%    | 50.08%          | 44.42%     |
| 2019     | 116  | -9.07%      | -14.35%           | 5.28%         | -6.05%       | -3.03%   | 31.90%    | 46.24%          | 31.33%     |
| 2020     | 111  | -2.14%      | -7.50%            | 5.35%         | 2.33%        | -4.47%   | 20.72%    | 40.56%          | 23.54%     |
| all buys | 1770 | -3.81%      | -10.75%           | 6.94%         | -7.68%       | 3.87%    | 33.05%    | 45.38%          | 40.81%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 120  | 1.52%       | -1.14%            | 2.65%         | 0.63%        | 0.89%    | 25.00%    | 46.05%          | 32.43%     |
| 2007     | 117  | -4.05%      | -14.56%           | 10.52%        | -9.78%       | 5.74%    | 73.50%    | 78.81%          | 79.78%     |
| 2008     | 117  | 8.96%       | 6.54%             | 2.43%         | 4.13%        | 4.84%    | 73.50%    | 70.97%          | 71.02%     |
| 2009     | 120  | -0.29%      | 31.70%            | -31.99%       | 6.62%        | -6.91%   | 15.83%    | 20.96%          | 16.00%     |
| 2010     | 118  | 1.32%       | 4.56%             | -3.24%        | 4.90%        | -3.58%   | 25.42%    | 35.92%          | 26.63%     |
| 2011     | 119  | -3.05%      | -9.41%            | 6.36%         | -10.64%      | 7.59%    | 33.61%    | 54.23%          | 51.17%     |
| 2012     | 120  | 3.17%       | 6.54%             | -3.38%        | 2.70%        | 0.46%    | 14.17%    | 31.74%          | 23.77%     |
| 2013     | 120  | -3.36%      | 3.76%             | -7.12%        | 0.80%        | -4.15%   | 19.17%    | 35.05%          | 27.01%     |
| 2014     | 120  | -19.86%     | -20.17%           | 0.31%         | -20.87%      | 1.00%    | 61.67%    | 63.91%          | 62.54%     |
| 2015     | 120  | -4.23%      | -17.43%           | 13.20%        | -16.11%      | 11.88%   | 54.17%    | 64.75%          | 64.07%     |
| 2016     | 120  | -0.90%      | 2.06%             | -2.96%        | 0.71%        | -1.62%   | 22.50%    | 37.64%          | 31.15%     |
| 2017     | 114  | -9.69%      | -4.09%            | -5.60%        | -0.82%       | -8.87%   | 35.09%    | 48.17%          | 40.88%     |
| 2018     | 118  | -11.24%     | -20.93%           | 9.70%         | -17.15%      | 5.91%    | 60.17%    | 67.27%          | 62.94%     |
| 2019     | 116  | -20.27%     | -13.00%           | -7.27%        | -14.12%      | -6.15%   | 59.48%    | 62.00%          | 56.59%     |
| 2020     | 111  | -0.87%      | 51.74%            | -52.61%       | 23.89%       | -24.77%  | 17.12%    | 22.37%          | 15.84%     |
| all buys | 1770 | -4.17%      | 3.64%             | -7.81%        | -3.12%       | -1.06%   | 39.32%    | 46.82%          | 44.14%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 25
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 1211.1 (min 619)
- mean with a tradable quote: 1187.2 (min 613)
- forced delisting liquidations: 87 (final-print convention, sell cost applied)

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
- `forest_fallen30_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `1617845e74ae77b1`, train run `9d3bb4134ab9`, folds 2006–2020 (from `experiments/models/forest_fallen30_cells_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3_9d3bb4134ab9`)

### Artifacts

- equity_curve: `reports/backtest/bt_fallen30_forestC_top10_cap2_rankfloor_3bf38d97bca05b0b_equity.csv`
- trades: `reports/backtest/bt_fallen30_forestC_top10_cap2_rankfloor_3bf38d97bca05b0b_trades.csv`
- rebalances: `reports/backtest/bt_fallen30_forestC_top10_cap2_rankfloor_3bf38d97bca05b0b_rebalances.csv`
- equity_plot: `reports/backtest/bt_fallen30_forestC_top10_cap2_rankfloor_3bf38d97bca05b0b_equity.png`
