# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_s1776_v141

- run `6b55630b1846`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `e1306d8eb51f7dec`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 959,231.53  | 767,231.53 | 13.88%         | 12.18%   | -41.14%      | 1,223.33   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 7.08%        | 7.09%         | -0.00% | 12,000.00 | 108    | -361.3364       |
| 2006              | 8.99%        | 13.61%        | -4.62% | 12,000.00 | 120    | -382.7083       |
| 2007              | -0.79%       | 4.40%         | -5.19% | 12,000.00 | 116    | -339.1580       |
| 2008 (GFC)        | -22.45%      | -34.30%       | 11.86% | 12,000.00 | 120    | -297.9833       |
| 2009 (GFC)        | 28.72%       | 24.74%        | 3.98%  | 12,000.00 | 114    | -210.6520       |
| 2010              | 30.05%       | 14.30%        | 15.76% | 12,000.00 | 120    | -384.6028       |
| 2011              | 7.15%        | 2.46%         | 4.69%  | 12,000.00 | 109    | -294.9664       |
| 2012              | 16.12%       | 17.09%        | -0.97% | 12,000.00 | 108    | -195.8796       |
| 2013              | 38.23%       | 27.75%        | 10.48% | 12,000.00 | 114    | -263.8918       |
| 2014              | 10.46%       | 14.49%        | -4.03% | 12,000.00 | 113    | -291.2743       |
| 2015              | 6.98%        | -0.11%        | 7.08%  | 12,000.00 | 108    | -202.8765       |
| 2016              | 13.69%       | 14.45%        | -0.76% | 12,000.00 | 108    | -186.8056       |
| 2017              | 22.63%       | 21.63%        | 1.00%  | 12,000.00 | 100    | -286.6367       |
| 2018              | -2.03%       | -5.13%        | 3.11%  | 12,000.00 | 97     | -254.3918       |
| 2019              | 39.58%       | 32.30%        | 7.27%  | 12,000.00 | 104    | -217.9135       |
| 2020 (COVID)      | 18.84%       | 15.69%        | 3.15%  | 12,000.00 | 83     | -197.1205       |
| 2021              | 22.88%       | 31.26%        | -8.38% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -16.42%      | -18.98%       | 2.56%  | 0.00      | 0      | —               |
| 2023              | 24.73%       | 26.71%        | -1.98% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 301  | 17.28% |
| Industrials            | 281  | 16.13% |
| Healthcare             | 272  | 15.61% |
| Technology             | 270  | 15.50% |
| Consumer Cyclical      | 263  | 15.10% |
| Communication Services | 114  | 6.54%  |
| Basic Materials        | 95   | 5.45%  |
| Energy                 | 63   | 3.62%  |
| Financial Services     | 61   | 3.50%  |
| Real Estate            | 13   | 0.75%  |
| Utilities              | 9    | 0.52%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 26     | 10     | Industrials            | 22.22%        |
| 2006 | 120  | 31     | 9      | Healthcare             | 20.00%        |
| 2007 | 116  | 31     | 9      | Consumer Cyclical      | 19.83%        |
| 2008 | 120  | 30     | 8      | Healthcare             | 20.00%        |
| 2009 | 114  | 33     | 10     | Healthcare             | 21.05%        |
| 2010 | 120  | 28     | 7      | Consumer Cyclical      | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive     | 19.27%        |
| 2012 | 108  | 29     | 8      | Consumer Defensive     | 22.22%        |
| 2013 | 114  | 32     | 8      | Communication Services | 21.05%        |
| 2014 | 113  | 26     | 7      | Technology             | 21.24%        |
| 2015 | 108  | 24     | 8      | Consumer Defensive     | 22.22%        |
| 2016 | 108  | 27     | 7      | Consumer Defensive     | 22.22%        |
| 2017 | 100  | 26     | 9      | Industrials            | 21.00%        |
| 2018 | 97   | 24     | 8      | Consumer Cyclical      | 24.74%        |
| 2019 | 104  | 27     | 6      | Consumer Defensive     | 23.08%        |
| 2020 | 83   | 25     | 8      | Consumer Defensive     | 24.10%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -5.77%         | -6.71%           | 34.26%  | 38.89%  | 2.78%         | 108  | -3.82%         | 0.45%            | 56.48%  | 37.96%  | 16.67%        |
| 2006     | 120  | 120  | -12.78%        | -12.34%          | 25.00%  | 45.83%  | 5.00%         | 120  | 0.99%          | 1.77%            | 58.33%  | 75.83%  | 5.83%         |
| 2007     | 116  | 116  | 3.61%          | 4.61%            | 64.66%  | 60.34%  | 1.72%         | 116  | 7.28%          | 7.59%            | 77.59%  | 43.10%  | 12.07%        |
| 2008     | 120  | 120  | 8.70%          | 10.72%           | 62.50%  | 76.67%  | 0.83%         | 120  | 6.99%          | 7.63%            | 85.00%  | 11.67%  | 3.33%         |
| 2009     | 114  | 114  | 7.04%          | 7.96%            | 59.65%  | 11.40%  | 7.02%         | 114  | -0.67%         | -0.31%           | 46.49%  | 8.77%   | 11.40%        |
| 2010     | 120  | 120  | 26.70%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 10.12%         | 9.50%            | 77.50%  | 1.67%   | 4.17%         |
| 2011     | 109  | 109  | 11.53%         | 10.02%           | 66.06%  | 21.10%  | 5.50%         | 109  | 4.63%          | 4.41%            | 68.81%  | 9.17%   | 8.26%         |
| 2012     | 108  | 108  | -2.50%         | -3.62%           | 44.44%  | 18.52%  | 0.00%         | 108  | -0.10%         | 2.68%            | 54.63%  | 14.81%  | 0.93%         |
| 2013     | 114  | 114  | -1.00%         | -1.44%           | 43.86%  | 14.04%  | 2.63%         | 114  | 2.18%          | 3.68%            | 64.04%  | 17.54%  | 5.26%         |
| 2014     | 113  | 113  | 13.55%         | 16.66%           | 73.45%  | 15.93%  | 1.77%         | 113  | 2.92%          | 1.88%            | 53.98%  | 17.70%  | 4.42%         |
| 2015     | 108  | 108  | 6.66%          | 4.39%            | 63.89%  | 25.93%  | 0.00%         | 108  | 3.58%          | 6.55%            | 72.22%  | 12.96%  | 5.56%         |
| 2016     | 108  | 108  | -2.05%         | -4.38%           | 39.81%  | 12.96%  | 2.78%         | 108  | 1.06%          | 4.80%            | 62.04%  | 20.37%  | 6.48%         |
| 2017     | 100  | 100  | 1.06%          | -2.85%           | 47.00%  | 24.00%  | 5.00%         | 100  | 0.97%          | -0.24%           | 49.00%  | 22.00%  | 18.00%        |
| 2018     | 97   | 97   | 8.81%          | 6.45%            | 70.10%  | 22.68%  | 0.00%         | 97   | 4.40%          | 0.12%            | 51.55%  | 4.12%   | 9.28%         |
| 2019     | 104  | 104  | -3.73%         | -6.01%           | 41.35%  | 37.50%  | 0.00%         | 104  | -5.65%         | -5.45%           | 19.23%  | 12.50%  | 0.00%         |
| 2020     | 83   | 83   | -12.89%        | -14.44%          | 36.14%  | 28.92%  | 0.00%         | 83   | -1.51%         | -1.42%           | 42.17%  | 24.10%  | 10.84%        |
| all buys | 1742 | 1742 | 3.28%          | 1.89%            | 53.27%  | 29.28%  | 2.35%         | 1742 | 2.25%          | 2.62%            | 59.47%  | 21.18%  | 7.52%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -3.82%      | -7.65%            | 3.84%         | -3.00%       | -0.82%   | 37.96%    | 51.93%          | 45.06%     |
| 2006     | 120  | 0.99%       | -9.20%            | 10.19%        | -2.57%       | 3.56%    | 75.83%    | 77.47%          | 73.20%     |
| 2007     | 116  | 7.28%       | -6.61%            | 13.88%        | -0.07%       | 7.35%    | 43.10%    | 69.62%          | 63.70%     |
| 2008     | 120  | 6.99%       | -1.41%            | 8.40%         | 1.90%        | 5.09%    | 11.67%    | 42.57%          | 35.21%     |
| 2009     | 114  | -0.67%      | -0.01%            | -0.66%        | 1.73%        | -2.40%   | 8.77%     | 24.96%          | 15.99%     |
| 2010     | 120  | 10.12%      | -5.91%            | 16.03%        | -1.12%       | 11.24%   | 1.67%     | 27.42%          | 15.73%     |
| 2011     | 109  | 4.63%       | -7.68%            | 12.31%        | -3.77%       | 8.41%    | 9.17%     | 27.47%          | 16.68%     |
| 2012     | 108  | -0.10%      | -7.07%            | 6.98%         | -3.11%       | 3.02%    | 14.81%    | 27.79%          | 18.56%     |
| 2013     | 114  | 2.18%       | -10.38%           | 12.57%        | -4.59%       | 6.77%    | 17.54%    | 39.52%          | 27.93%     |
| 2014     | 113  | 2.92%       | -11.40%           | 14.31%        | -5.10%       | 8.02%    | 17.70%    | 41.08%          | 29.98%     |
| 2015     | 108  | 3.58%       | -10.39%           | 13.97%        | -4.78%       | 8.36%    | 12.96%    | 37.61%          | 27.15%     |
| 2016     | 108  | 1.06%       | -9.18%            | 10.24%        | -4.27%       | 5.33%    | 20.37%    | 35.01%          | 24.90%     |
| 2017     | 100  | 0.97%       | -14.54%           | 15.51%        | -7.09%       | 8.07%    | 22.00%    | 50.60%          | 38.43%     |
| 2018     | 97   | 4.40%       | -11.65%           | 16.05%        | -4.97%       | 9.37%    | 4.12%     | 36.68%          | 21.51%     |
| 2019     | 104  | -5.65%      | -11.93%           | 6.28%         | -4.95%       | -0.70%   | 12.50%    | 39.82%          | 23.50%     |
| 2020     | 83   | -1.51%      | -8.77%            | 7.26%         | -2.73%       | 1.22%    | 24.10%    | 39.44%          | 24.42%     |
| all buys | 1742 | 2.25%       | -8.20%            | 10.45%        | -2.93%       | 5.18%    | 21.18%    | 42.54%          | 31.80%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -5.77%      | 5.25%             | -11.02%       | 5.09%        | -10.86%  | 38.89%    | 38.73%          | 33.28%     |
| 2006     | 120  | -12.78%     | -0.15%            | -12.63%       | 1.46%        | -14.24%  | 45.83%    | 38.08%          | 27.57%     |
| 2007     | 116  | 3.61%       | -7.00%            | 10.61%        | 1.25%        | 2.36%    | 60.34%    | 73.36%          | 67.12%     |
| 2008     | 120  | 8.70%       | 4.28%             | 4.42%         | 3.93%        | 4.76%    | 76.67%    | 73.80%          | 75.39%     |
| 2009     | 114  | 7.04%       | 31.66%            | -24.62%       | 15.39%       | -8.35%   | 11.40%    | 23.03%          | 16.54%     |
| 2010     | 120  | 26.70%      | 5.09%             | 21.61%        | 6.60%        | 20.09%   | 8.33%     | 33.28%          | 23.89%     |
| 2011     | 109  | 11.53%      | -7.55%            | 19.08%        | -4.75%       | 16.28%   | 21.10%    | 48.29%          | 39.85%     |
| 2012     | 108  | -2.50%      | 3.72%             | -6.22%        | 2.41%        | -4.91%   | 18.52%    | 27.49%          | 19.78%     |
| 2013     | 114  | -1.00%      | 1.72%             | -2.72%        | 0.72%        | -1.72%   | 14.04%    | 28.73%          | 19.10%     |
| 2014     | 113  | 13.55%      | -7.02%            | 20.57%        | -2.97%       | 16.53%   | 15.93%    | 47.37%          | 37.27%     |
| 2015     | 108  | 6.66%       | -9.45%            | 16.10%        | -3.06%       | 9.71%    | 25.93%    | 56.17%          | 46.67%     |
| 2016     | 108  | -2.05%      | 2.15%             | -4.19%        | -0.86%       | -1.19%   | 12.96%    | 30.43%          | 23.69%     |
| 2017     | 100  | 1.06%       | -1.39%            | 2.45%         | -1.52%       | 2.58%    | 24.00%    | 40.54%          | 32.72%     |
| 2018     | 97   | 8.81%       | -9.90%            | 18.71%        | -1.45%       | 10.26%   | 22.68%    | 53.76%          | 40.66%     |
| 2019     | 104  | -3.73%      | -9.73%            | 6.00%         | -5.13%       | 1.40%    | 37.50%    | 55.97%          | 43.88%     |
| 2020     | 83   | -12.89%     | 33.15%            | -46.04%       | 5.27%        | -18.17%  | 28.92%    | 22.31%          | 13.80%     |
| all buys | 1742 | 3.28%       | 2.26%             | 1.02%         | 1.47%        | 1.81%    | 29.28%    | 43.57%          | 35.52%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 109
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3220.5 (min 2912)
- mean with a tradable quote: 3143.5 (min 2860)
- forced delisting liquidations: 69 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 13 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `9152848ec411f217`, train run `8f3eb8f1d305`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_v141_8f3eb8f1d305`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s1776_v141_e1306d8eb51f7dec_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s1776_v141_e1306d8eb51f7dec_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s1776_v141_e1306d8eb51f7dec_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s1776_v141_e1306d8eb51f7dec_equity.png`
