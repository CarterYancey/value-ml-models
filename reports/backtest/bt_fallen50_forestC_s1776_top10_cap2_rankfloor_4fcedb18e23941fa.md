# Portfolio backtest — bt_fallen50_forestC_s1776_top10_cap2_rankfloor

- run `fa43e4eaecaa`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`, backtest config `4fcedb18e23941fa`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2006–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 180,000.00 | 697,902.75  | 517,902.75 | 12.39%         | 10.29%   | -58.14%      | 1,964.58   |
| benchmark | 180,000.00 | 664,684.90  | 484,684.90 | 11.96%         | 9.72%    | -52.84%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2006              | 10.80%       | 13.50%        | -2.70%  | 12,000.00 | 113    | 0.4439          |
| 2007              | -7.50%       | 4.41%         | -11.91% | 12,000.00 | 117    | 0.5676          |
| 2008 (GFC)        | -33.41%      | -34.28%       | 0.86%   | 12,000.00 | 120    | 0.6468          |
| 2009 (GFC)        | 43.55%       | 24.77%        | 18.78%  | 12,000.00 | 117    | 0.6992          |
| 2010              | 23.03%       | 14.30%        | 8.73%   | 12,000.00 | 117    | 0.6471          |
| 2011              | 5.84%        | 2.46%         | 3.38%   | 12,000.00 | 115    | 0.5838          |
| 2012              | 18.52%       | 17.09%        | 1.43%   | 12,000.00 | 114    | 0.5349          |
| 2013              | 37.24%       | 27.75%        | 9.48%   | 12,000.00 | 118    | 0.4940          |
| 2014              | 11.08%       | 14.50%        | -3.42%  | 12,000.00 | 120    | 0.4277          |
| 2015              | -8.84%       | -0.10%        | -8.73%  | 12,000.00 | 120    | 0.4559          |
| 2016              | 19.64%       | 14.45%        | 5.18%   | 12,000.00 | 116    | 0.5267          |
| 2017              | 20.94%       | 21.63%        | -0.69%  | 12,000.00 | 119    | 0.5016          |
| 2018              | -5.15%       | -5.13%        | -0.02%  | 12,000.00 | 120    | 0.4945          |
| 2019              | 27.38%       | 32.30%        | -4.92%  | 12,000.00 | 113    | 0.5427          |
| 2020 (COVID)      | 17.60%       | 15.68%        | 1.92%   | 12,000.00 | 119    | 0.5837          |
| 2021              | 24.57%       | 31.26%        | -6.69%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -11.11%      | -18.98%       | 7.87%   | 0.00      | 0      | —               |
| 2023              | 21.64%       | 26.71%        | -5.07%  | 0.00      | 0      | —               |

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
| Consumer Cyclical      | 277  | 15.76% |
| Technology             | 276  | 15.70% |
| Industrials            | 229  | 13.03% |
| Communication Services | 190  | 10.81% |
| Healthcare             | 183  | 10.41% |
| Energy                 | 164  | 9.33%  |
| Consumer Defensive     | 163  | 9.27%  |
| Basic Materials        | 132  | 7.51%  |
| Real Estate            | 66   | 3.75%  |
| Utilities              | 42   | 2.39%  |
| Financial Services     | 36   | 2.05%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2006 | 113  | 25     | 7      | Technology             | 21.24%        |
| 2007 | 117  | 32     | 8      | Communication Services | 20.51%        |
| 2008 | 120  | 31     | 7      | Technology             | 20.00%        |
| 2009 | 117  | 32     | 9      | Industrials            | 20.51%        |
| 2010 | 117  | 26     | 8      | Industrials            | 17.95%        |
| 2011 | 115  | 30     | 10     | Communication Services | 18.26%        |
| 2012 | 114  | 26     | 11     | Technology             | 21.05%        |
| 2013 | 118  | 32     | 11     | Real Estate            | 17.80%        |
| 2014 | 120  | 27     | 8      | Technology             | 20.00%        |
| 2015 | 120  | 30     | 8      | Technology             | 20.00%        |
| 2016 | 116  | 31     | 9      | Technology             | 20.69%        |
| 2017 | 119  | 24     | 9      | Technology             | 20.17%        |
| 2018 | 120  | 28     | 9      | Consumer Cyclical      | 20.00%        |
| 2019 | 113  | 25     | 10     | Energy                 | 21.24%        |
| 2020 | 119  | 35     | 9      | Industrials            | 17.65%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2006     | 113  | 113  | 1.12%          | -3.06%           | 47.79%  | 24.78%  | 8.85%         | 113  | -0.24%         | 2.97%            | 57.52%  | 74.34%  | 21.24%        |
| 2007     | 117  | 117  | -7.56%         | -4.62%           | 42.74%  | 76.07%  | 1.71%         | 117  | -4.18%         | -0.71%           | 47.01%  | 66.67%  | 20.51%        |
| 2008     | 120  | 120  | 2.50%          | 5.89%            | 60.00%  | 68.33%  | 2.50%         | 120  | 6.60%          | 4.50%            | 69.17%  | 25.00%  | 5.00%         |
| 2009     | 117  | 117  | 13.72%         | 11.63%           | 69.23%  | 8.55%   | 0.00%         | 117  | 4.97%          | 4.71%            | 68.38%  | 5.98%   | 6.84%         |
| 2010     | 117  | 117  | 11.27%         | 7.98%            | 62.39%  | 12.82%  | 1.71%         | 117  | 1.18%          | 8.56%            | 62.39%  | 20.51%  | 15.38%        |
| 2011     | 115  | 115  | -0.57%         | -5.41%           | 40.87%  | 43.48%  | 5.22%         | 115  | -1.56%         | -0.28%           | 48.70%  | 18.26%  | 10.43%        |
| 2012     | 114  | 114  | 7.53%          | 4.39%            | 59.65%  | 14.91%  | 0.00%         | 114  | 1.23%          | -0.56%           | 50.00%  | 8.77%   | 14.91%        |
| 2013     | 118  | 118  | -0.34%         | -1.48%           | 48.31%  | 22.03%  | 5.08%         | 118  | -2.93%         | -1.39%           | 45.76%  | 22.03%  | 10.17%        |
| 2014     | 120  | 120  | -25.55%        | -20.75%          | 21.67%  | 64.17%  | 11.67%        | 120  | -20.42%        | -16.71%          | 14.17%  | 61.67%  | 39.17%        |
| 2015     | 120  | 120  | -20.84%        | -24.47%          | 22.50%  | 72.50%  | 5.83%         | 120  | -9.27%         | -5.29%           | 31.67%  | 35.00%  | 35.83%        |
| 2016     | 116  | 116  | -5.94%         | -11.61%          | 37.93%  | 35.34%  | 11.21%        | 116  | -12.39%        | -8.50%           | 32.76%  | 41.38%  | 26.72%        |
| 2017     | 119  | 119  | 10.03%         | 9.51%            | 62.18%  | 21.85%  | 20.17%        | 119  | -4.88%         | -3.32%           | 36.97%  | 43.70%  | 33.61%        |
| 2018     | 120  | 120  | -6.20%         | -8.78%           | 44.17%  | 53.33%  | 7.50%         | 120  | -13.13%        | -10.73%          | 26.67%  | 35.83%  | 12.50%        |
| 2019     | 113  | 113  | -24.54%        | -26.95%          | 21.24%  | 67.26%  | 5.31%         | 113  | -10.12%        | -8.18%           | 33.63%  | 34.51%  | 16.81%        |
| 2020     | 119  | 119  | 18.32%         | 7.45%            | 58.82%  | 8.40%   | 1.68%         | 119  | -1.31%         | 2.74%            | 55.46%  | 25.21%  | 9.24%         |
| all buys | 1758 | 1758 | -1.81%         | -2.93%           | 46.64%  | 39.70%  | 5.92%         | 1758 | -4.46%         | -2.14%           | 45.28%  | 34.58%  | 18.60%        |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 113  | -0.24%      | -15.81%           | 15.57%        | -7.06%       | 6.81%    | 74.34%    | 81.80%          | 80.96%     |
| 2007     | 117  | -4.18%      | -16.05%           | 11.87%        | -12.96%      | 8.78%    | 66.67%    | 76.07%          | 76.59%     |
| 2008     | 120  | 6.60%       | -4.77%            | 11.38%        | 0.44%        | 6.16%    | 25.00%    | 48.34%          | 40.54%     |
| 2009     | 117  | 4.97%       | 1.65%             | 3.32%         | 1.74%        | 3.23%    | 5.98%     | 24.74%          | 17.52%     |
| 2010     | 117  | 1.18%       | -8.50%            | 9.68%         | -4.30%       | 5.48%    | 20.51%    | 34.40%          | 25.04%     |
| 2011     | 115  | -1.56%      | -11.46%           | 9.90%         | -5.77%       | 4.21%    | 18.26%    | 37.70%          | 25.81%     |
| 2012     | 114  | 1.23%       | -10.19%           | 11.42%        | -6.89%       | 8.12%    | 8.77%     | 37.22%          | 29.58%     |
| 2013     | 118  | -2.93%      | -21.88%           | 18.96%        | -17.55%      | 14.62%   | 22.03%    | 56.81%          | 52.17%     |
| 2014     | 120  | -20.42%     | -30.22%           | 9.80%         | -22.85%      | 2.43%    | 61.67%    | 66.11%          | 57.50%     |
| 2015     | 120  | -9.27%      | -24.69%           | 15.41%        | -15.37%      | 6.10%    | 35.00%    | 58.28%          | 48.48%     |
| 2016     | 116  | -12.39%     | -19.23%           | 6.84%         | -13.10%      | 0.71%    | 41.38%    | 52.74%          | 46.21%     |
| 2017     | 119  | -4.88%      | -30.64%           | 25.76%        | -25.77%      | 20.89%   | 43.70%    | 69.41%          | 70.09%     |
| 2018     | 120  | -13.13%     | -24.35%           | 11.22%        | -22.52%      | 9.39%    | 35.83%    | 55.51%          | 48.29%     |
| 2019     | 113  | -10.12%     | -18.29%           | 8.17%         | -10.68%      | 0.56%    | 34.51%    | 52.84%          | 40.69%     |
| 2020     | 119  | -1.31%      | -10.25%           | 8.94%         | 1.57%        | -2.88%   | 25.21%    | 46.54%          | 30.85%     |
| all buys | 1758 | -4.46%      | -13.49%           | 9.02%         | -10.79%      | 6.33%    | 34.58%    | 49.28%          | 46.04%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2006     | 113  | 1.12%       | 0.49%             | 0.64%         | -2.40%       | 3.52%    | 24.78%    | 48.73%          | 37.63%     |
| 2007     | 117  | -7.56%      | -19.11%           | 11.55%        | -18.32%      | 10.76%   | 76.07%    | 80.53%          | 81.28%     |
| 2008     | 120  | 2.50%       | 9.54%             | -7.04%        | 9.97%        | -7.47%   | 68.33%    | 69.73%          | 69.34%     |
| 2009     | 117  | 13.72%      | 41.43%            | -27.71%       | 20.69%       | -6.97%   | 8.55%     | 21.98%          | 17.05%     |
| 2010     | 117  | 11.27%      | 3.52%             | 7.76%         | 5.77%        | 5.51%    | 12.82%    | 40.56%          | 29.69%     |
| 2011     | 115  | -0.57%      | -12.37%           | 11.80%        | -14.50%      | 13.93%   | 43.48%    | 58.29%          | 57.26%     |
| 2012     | 114  | 7.53%       | 8.23%             | -0.70%        | 8.49%        | -0.95%   | 14.91%    | 35.49%          | 27.31%     |
| 2013     | 118  | -0.34%      | 6.69%             | -7.03%        | 3.14%        | -3.48%   | 22.03%    | 37.13%          | 30.16%     |
| 2014     | 120  | -25.55%     | -26.51%           | 0.96%         | -25.83%      | 0.28%    | 64.17%    | 70.05%          | 65.53%     |
| 2015     | 120  | -20.84%     | -22.63%           | 1.78%         | -15.00%      | -5.85%   | 72.50%    | 69.36%          | 62.84%     |
| 2016     | 116  | -5.94%      | 1.77%             | -7.71%        | 8.24%        | -14.18%  | 35.34%    | 44.05%          | 38.15%     |
| 2017     | 119  | 10.03%      | -4.15%            | 14.19%        | -2.06%       | 12.09%   | 21.85%    | 51.64%          | 43.16%     |
| 2018     | 120  | -6.20%      | -25.64%           | 19.44%        | -23.47%      | 17.27%   | 53.33%    | 72.13%          | 69.33%     |
| 2019     | 113  | -24.54%     | -12.05%           | -12.49%       | -20.33%      | -4.21%   | 67.26%    | 64.84%          | 61.70%     |
| 2020     | 119  | 18.32%      | 69.14%            | -50.82%       | 35.78%       | -17.46%  | 8.40%     | 25.76%          | 18.07%     |
| all buys | 1758 | -1.81%      | 6.58%             | -8.38%        | -1.99%       | 0.18%    | 39.70%    | 48.83%          | 47.34%     |

## Coverage & diagnostics

- rebalance months: 180; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 41
- mean stocks in the point-in-time cross-section: 3986.6 (min 3639)
- mean after the per-model min_score floor: 3986.6 (min 3639)
- mean after the column filters: 3986.6 (min 3639)
- mean after the investability filter: 756.2 (min 348)
- mean with a tradable quote: 740.1 (min 344)
- forced delisting liquidations: 135 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 32 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `ec8994acec106928`, train run `28a4e3464744`, folds 2006–2020 (from `experiments/models/forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s1776_28a4e3464744`)

### Artifacts

- equity_curve: `reports/backtest/bt_fallen50_forestC_s1776_top10_cap2_rankfloor_4fcedb18e23941fa_equity.csv`
- trades: `reports/backtest/bt_fallen50_forestC_s1776_top10_cap2_rankfloor_4fcedb18e23941fa_trades.csv`
- rebalances: `reports/backtest/bt_fallen50_forestC_s1776_top10_cap2_rankfloor_4fcedb18e23941fa_rebalances.csv`
- equity_plot: `reports/backtest/bt_fallen50_forestC_s1776_top10_cap2_rankfloor_4fcedb18e23941fa_equity.png`
