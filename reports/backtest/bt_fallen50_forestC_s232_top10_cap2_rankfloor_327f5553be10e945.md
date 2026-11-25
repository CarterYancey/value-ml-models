# Portfolio backtest — bt_fallen50_forestC_s232_top10_cap2_rankfloor

- run `7e8566ce2cb6`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `327f5553be10e945`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 649,287.21  | 469,287.21 | 11.75%         | 10.19%   | -57.97%      | 1,939.29   |
| benchmark | 180,000.00 | 664,684.90  | 484,684.90 | 11.96%         | 9.72%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006              | 17.03%       | 13.50%        | 3.52%   | 12,000.00 | 114    | 0.4519          |
| 2007              | -6.53%       | 4.41%         | -10.94% | 12,000.00 | 115    | 0.5775          |
| 2008 (GFC)        | -33.00%      | -34.28%       | 1.28%   | 12,000.00 | 120    | 0.6504          |
| 2009 (GFC)        | 43.55%       | 24.77%        | 18.79%  | 12,000.00 | 117    | 0.6983          |
| 2010              | 23.55%       | 14.30%        | 9.25%   | 12,000.00 | 117    | 0.6467          |
| 2011              | 5.89%        | 2.46%         | 3.44%   | 12,000.00 | 114    | 0.5869          |
| 2012              | 16.72%       | 17.09%        | -0.37%  | 12,000.00 | 114    | 0.5344          |
| 2013              | 35.50%       | 27.75%        | 7.75%   | 12,000.00 | 118    | 0.5013          |
| 2014              | 11.38%       | 14.50%        | -3.12%  | 12,000.00 | 116    | 0.4249          |
| 2015              | -10.81%      | -0.10%        | -10.70% | 12,000.00 | 120    | 0.4580          |
| 2016              | 19.88%       | 14.45%        | 5.42%   | 12,000.00 | 116    | 0.5302          |
| 2017              | 22.03%       | 21.63%        | 0.40%   | 12,000.00 | 118    | 0.5036          |
| 2018              | -4.83%       | -5.13%        | 0.30%   | 12,000.00 | 120    | 0.4952          |
| 2019              | 25.80%       | 32.30%        | -6.50%  | 12,000.00 | 115    | 0.5415          |
| 2020 (COVID)      | 17.87%       | 15.68%        | 2.19%   | 12,000.00 | 119    | 0.5814          |
| 2021              | 23.88%       | 31.26%        | -7.38%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -14.36%      | -18.98%       | 4.62%   | 0.00      | 0      | —               |
| 2023              | 20.87%       | 26.71%        | -5.84%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 3 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

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
| Technology             | 288  | 16.43% |
| Consumer Cyclical      | 263  | 15.00% |
| Industrials            | 210  | 11.98% |
| Communication Services | 202  | 11.52% |
| Healthcare             | 178  | 10.15% |
| Energy                 | 166  | 9.47%  |
| Consumer Defensive     | 164  | 9.36%  |
| Basic Materials        | 132  | 7.53%  |
| Real Estate            | 69   | 3.94%  |
| Utilities              | 42   | 2.40%  |
| Financial Services     | 39   | 2.22%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2006 | 114  | 26     | 7      | Technology    | 21.05%        |
| 2007 | 115  | 29     | 8      | Technology    | 20.87%        |
| 2008 | 120  | 33     | 10     | Technology    | 20.00%        |
| 2009 | 117  | 31     | 9      | Industrials   | 20.51%        |
| 2010 | 117  | 29     | 8      | Healthcare    | 17.95%        |
| 2011 | 114  | 31     | 10     | Technology    | 21.05%        |
| 2012 | 114  | 25     | 11     | Technology    | 21.05%        |
| 2013 | 118  | 31     | 11     | Energy        | 17.80%        |
| 2014 | 116  | 26     | 8      | Technology    | 20.69%        |
| 2015 | 120  | 28     | 8      | Technology    | 20.00%        |
| 2016 | 116  | 32     | 9      | Technology    | 20.69%        |
| 2017 | 118  | 23     | 7      | Technology    | 20.34%        |
| 2018 | 120  | 27     | 10     | Energy        | 20.00%        |
| 2019 | 115  | 27     | 9      | Energy        | 20.87%        |
| 2020 | 119  | 35     | 9      | Industrials   | 17.65%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 114  | 114  | 2.54%          | 1.71%            | 52.63%  | 28.07%  | 6.14%         | 114  | -1.10%         | 2.46%            | 57.02%  | 78.07%  | 18.42%        |
| 2007     | 115  | 115  | -7.90%         | -2.45%           | 46.96%  | 73.91%  | 0.00%         | 115  | -3.01%         | -0.39%           | 48.70%  | 63.48%  | 15.65%        |
| 2008     | 120  | 120  | 2.61%          | 2.81%            | 55.00%  | 70.00%  | 2.50%         | 120  | 8.26%          | 4.13%            | 65.83%  | 27.50%  | 7.50%         |
| 2009     | 117  | 117  | 17.02%         | 16.36%           | 72.65%  | 12.82%  | 5.13%         | 117  | 6.91%          | 6.53%            | 71.79%  | 6.84%   | 10.26%        |
| 2010     | 117  | 117  | 8.47%          | 4.55%            | 58.12%  | 16.24%  | 0.00%         | 117  | 2.54%          | 8.11%            | 60.68%  | 17.09%  | 12.82%        |
| 2011     | 114  | 114  | -1.11%         | -6.41%           | 41.23%  | 43.86%  | 5.26%         | 114  | -3.50%         | -3.30%           | 43.86%  | 19.30%  | 10.53%        |
| 2012     | 114  | 114  | 8.05%          | 4.81%            | 61.40%  | 14.04%  | 0.00%         | 114  | 1.04%          | -2.26%           | 49.12%  | 8.77%   | 14.91%        |
| 2013     | 118  | 118  | -0.77%         | -1.91%           | 46.61%  | 22.03%  | 5.08%         | 118  | -4.11%         | -1.39%           | 45.76%  | 22.03%  | 10.17%        |
| 2014     | 116  | 116  | -28.02%        | -27.82%          | 19.83%  | 68.97%  | 8.62%         | 116  | -19.86%        | -15.28%          | 16.38%  | 62.93%  | 33.62%        |
| 2015     | 120  | 120  | -20.15%        | -22.34%          | 20.83%  | 73.33%  | 5.83%         | 120  | -9.17%         | -5.29%           | 30.83%  | 35.00%  | 35.83%        |
| 2016     | 116  | 116  | -3.63%         | -8.63%           | 42.24%  | 33.62%  | 13.79%        | 116  | -9.83%         | -5.88%           | 38.79%  | 35.34%  | 34.48%        |
| 2017     | 118  | 118  | 7.95%          | 5.97%            | 59.32%  | 23.73%  | 17.80%        | 118  | -4.39%         | -3.42%           | 38.98%  | 46.61%  | 28.81%        |
| 2018     | 120  | 120  | -5.18%         | -8.78%           | 44.17%  | 53.33%  | 5.00%         | 120  | -13.52%        | -11.05%          | 25.83%  | 36.67%  | 7.50%         |
| 2019     | 115  | 115  | -26.96%        | -31.40%          | 18.26%  | 70.43%  | 3.48%         | 115  | -10.68%        | -10.17%          | 30.43%  | 37.39%  | 17.39%        |
| 2020     | 119  | 119  | 19.01%         | 4.99%            | 56.30%  | 9.24%   | 1.68%         | 119  | -2.58%         | 1.18%            | 52.10%  | 27.73%  | 5.04%         |
| all buys | 1753 | 1753 | -1.85%         | -3.36%           | 46.38%  | 40.96%  | 5.36%         | 1753 | -4.20%         | -2.20%           | 45.07%  | 34.91%  | 17.51%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 114  | -1.10%      | -15.81%           | 14.71%        | -7.38%       | 6.28%    | 78.07%    | 81.80%          | 79.90%     |
| 2007     | 115  | -3.01%      | -16.05%           | 13.04%        | -12.23%      | 9.22%    | 63.48%    | 76.07%          | 76.46%     |
| 2008     | 120  | 8.26%       | -4.77%            | 13.04%        | 1.02%        | 7.24%    | 27.50%    | 48.34%          | 39.60%     |
| 2009     | 117  | 6.91%       | 1.65%             | 5.26%         | 2.11%        | 4.80%    | 6.84%     | 24.74%          | 17.67%     |
| 2010     | 117  | 2.54%       | -8.50%            | 11.04%        | -4.66%       | 7.19%    | 17.09%    | 34.40%          | 25.33%     |
| 2011     | 114  | -3.50%      | -11.46%           | 7.96%         | -6.17%       | 2.67%    | 19.30%    | 37.70%          | 26.49%     |
| 2012     | 114  | 1.04%       | -10.19%           | 11.23%        | -6.88%       | 7.92%    | 8.77%     | 37.22%          | 29.71%     |
| 2013     | 118  | -4.11%      | -21.88%           | 17.78%        | -17.76%      | 13.65%   | 22.03%    | 56.81%          | 52.60%     |
| 2014     | 116  | -19.86%     | -30.22%           | 10.36%        | -23.82%      | 3.96%    | 62.93%    | 66.11%          | 58.66%     |
| 2015     | 120  | -9.17%      | -24.69%           | 15.52%        | -15.98%      | 6.81%    | 35.00%    | 58.28%          | 49.51%     |
| 2016     | 116  | -9.83%      | -19.23%           | 9.40%         | -13.37%      | 3.54%    | 35.34%    | 52.74%          | 45.08%     |
| 2017     | 118  | -4.39%      | -30.64%           | 26.25%        | -26.82%      | 22.43%   | 46.61%    | 69.41%          | 71.35%     |
| 2018     | 120  | -13.52%     | -24.35%           | 10.83%        | -22.85%      | 9.34%    | 36.67%    | 55.51%          | 49.72%     |
| 2019     | 115  | -10.68%     | -18.29%           | 7.61%         | -10.41%      | -0.27%   | 37.39%    | 52.84%          | 39.57%     |
| 2020     | 119  | -2.58%      | -10.25%           | 7.68%         | 1.35%        | -3.93%   | 27.73%    | 46.54%          | 31.10%     |
| all buys | 1753 | -4.20%      | -13.49%           | 9.29%         | -10.94%      | 6.74%    | 34.91%    | 49.28%          | 46.16%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 114  | 2.54%       | 0.49%             | 2.05%         | -1.72%       | 4.26%    | 28.07%    | 48.73%          | 36.40%     |
| 2007     | 115  | -7.90%      | -19.11%           | 11.21%        | -17.85%      | 9.95%    | 73.91%    | 80.53%          | 80.74%     |
| 2008     | 120  | 2.61%       | 9.54%             | -6.92%        | 10.19%       | -7.58%   | 70.00%    | 69.73%          | 69.42%     |
| 2009     | 117  | 17.02%      | 41.43%            | -24.41%       | 20.93%       | -3.91%   | 12.82%    | 21.98%          | 17.18%     |
| 2010     | 117  | 8.47%       | 3.52%             | 4.95%         | 5.49%        | 2.98%    | 16.24%    | 40.56%          | 29.37%     |
| 2011     | 114  | -1.11%      | -12.37%           | 11.26%        | -14.73%      | 13.62%   | 43.86%    | 58.29%          | 57.01%     |
| 2012     | 114  | 8.05%       | 8.23%             | -0.18%        | 7.75%        | 0.30%    | 14.04%    | 35.49%          | 27.80%     |
| 2013     | 118  | -0.77%      | 6.69%             | -7.47%        | 2.49%        | -3.26%   | 22.03%    | 37.13%          | 30.27%     |
| 2014     | 116  | -28.02%     | -26.51%           | -1.51%        | -26.87%      | -1.16%   | 68.97%    | 70.05%          | 65.53%     |
| 2015     | 120  | -20.15%     | -22.63%           | 2.48%         | -15.41%      | -4.74%   | 73.33%    | 69.36%          | 63.49%     |
| 2016     | 116  | -3.63%      | 1.77%             | -5.40%        | 7.19%        | -10.82%  | 33.62%    | 44.05%          | 37.93%     |
| 2017     | 118  | 7.95%       | -4.15%            | 12.11%        | -3.25%       | 11.20%   | 23.73%    | 51.64%          | 43.47%     |
| 2018     | 120  | -5.18%      | -25.64%           | 20.46%        | -24.20%      | 19.02%   | 53.33%    | 72.13%          | 69.92%     |
| 2019     | 115  | -26.96%     | -12.05%           | -14.91%       | -21.33%      | -5.63%   | 70.43%    | 64.84%          | 63.04%     |
| 2020     | 119  | 19.01%      | 69.14%            | -50.13%       | 41.58%       | -22.57%  | 9.24%     | 25.76%          | 18.35%     |
| all buys | 1753 | -1.85%      | 6.58%             | -8.42%        | -1.92%       | 0.07%    | 40.96%    | 48.83%          | 47.36%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 45
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 756.2 (min 348)
- mean with a tradable quote: 740.1 (min 344)
- forced delisting liquidations: 130 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 31 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `38ad64165da7bb89`, train run `0cb0ea8c1a5c`, folds 2006–2020 (from `experiments/models/forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s232_0cb0ea8c1a5c`)

### Artifacts

- equity_curve: `reports/backtest/bt_fallen50_forestC_s232_top10_cap2_rankfloor_327f5553be10e945_equity.csv`
- trades: `reports/backtest/bt_fallen50_forestC_s232_top10_cap2_rankfloor_327f5553be10e945_trades.csv`
- rebalances: `reports/backtest/bt_fallen50_forestC_s232_top10_cap2_rankfloor_327f5553be10e945_rebalances.csv`
- equity_plot: `reports/backtest/bt_fallen50_forestC_s232_top10_cap2_rankfloor_327f5553be10e945_equity.png`
