# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_v141

- run `61f07b58edc9`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `0d86c0074c6ba825`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 984,128.29  | 792,128.29 | 14.10%         | 12.51%   | -39.31%      | 1,250.59   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 7.85%        | 7.09%         | 0.76%  | 12,000.00 | 114    | -266.1520       |
| 2006              | 10.17%       | 13.61%        | -3.44% | 12,000.00 | 120    | -275.7611       |
| 2007              | 0.78%        | 4.40%         | -3.62% | 12,000.00 | 118    | -248.0085       |
| 2008 (GFC)        | -21.20%      | -34.30%       | 13.10% | 12,000.00 | 120    | -231.6222       |
| 2009 (GFC)        | 27.43%       | 24.74%        | 2.68%  | 12,000.00 | 115    | -166.2464       |
| 2010              | 25.16%       | 14.30%        | 10.86% | 12,000.00 | 120    | -266.9333       |
| 2011              | 9.01%        | 2.46%         | 6.55%  | 12,000.00 | 109    | -213.9969       |
| 2012              | 18.15%       | 17.09%        | 1.06%  | 12,000.00 | 103    | -153.9676       |
| 2013              | 36.05%       | 27.75%        | 8.30%  | 12,000.00 | 114    | -195.5673       |
| 2014              | 15.03%       | 14.49%        | 0.54%  | 12,000.00 | 109    | -200.8379       |
| 2015              | 7.23%        | -0.11%        | 7.34%  | 12,000.00 | 110    | -149.8152       |
| 2016              | 12.33%       | 14.45%        | -2.13% | 12,000.00 | 107    | -137.5047       |
| 2017              | 22.24%       | 21.63%        | 0.61%  | 12,000.00 | 103    | -203.3592       |
| 2018              | -2.47%       | -5.13%        | 2.66%  | 12,000.00 | 99     | -181.9899       |
| 2019              | 40.70%       | 32.30%        | 8.40%  | 12,000.00 | 109    | -165.2936       |
| 2020 (COVID)      | 20.26%       | 15.69%        | 4.57%  | 12,000.00 | 86     | -155.8411       |
| 2021              | 22.37%       | 31.26%        | -8.89% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -15.48%      | -18.98%       | 3.49%  | 0.00      | 0      | —               |
| 2023              | 23.01%       | 26.71%        | -3.70% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `log_marketcap_rank >= 0.5`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 317  | 18.05% |
| Technology             | 288  | 16.40% |
| Healthcare             | 285  | 16.23% |
| Industrials            | 282  | 16.06% |
| Consumer Cyclical      | 237  | 13.50% |
| Communication Services | 123  | 7.00%  |
| Basic Materials        | 80   | 4.56%  |
| Financial Services     | 62   | 3.53%  |
| Energy                 | 57   | 3.25%  |
| Real Estate            | 13   | 0.74%  |
| Utilities              | 12   | 0.68%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 114  | 27     | 10     | Industrials            | 21.05%        |
| 2006 | 120  | 30     | 8      | Healthcare             | 20.00%        |
| 2007 | 118  | 28     | 9      | Consumer Defensive     | 20.34%        |
| 2008 | 120  | 32     | 8      | Healthcare             | 20.00%        |
| 2009 | 115  | 31     | 10     | Technology             | 20.87%        |
| 2010 | 120  | 29     | 10     | Consumer Defensive     | 20.00%        |
| 2011 | 109  | 27     | 9      | Consumer Defensive     | 22.02%        |
| 2012 | 103  | 23     | 8      | Consumer Defensive     | 23.30%        |
| 2013 | 114  | 30     | 8      | Communication Services | 18.42%        |
| 2014 | 109  | 26     | 7      | Technology             | 22.02%        |
| 2015 | 110  | 23     | 8      | Consumer Defensive     | 21.82%        |
| 2016 | 107  | 28     | 7      | Technology             | 22.43%        |
| 2017 | 103  | 26     | 8      | Technology             | 21.36%        |
| 2018 | 99   | 26     | 8      | Consumer Cyclical      | 24.24%        |
| 2019 | 109  | 25     | 6      | Consumer Defensive     | 22.02%        |
| 2020 | 86   | 28     | 8      | Technology             | 22.09%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 114  | 114  | -6.43%         | -7.29%           | 28.07%  | 41.23%  | 0.00%         | 114  | -4.32%         | 0.62%            | 56.14%  | 41.23%  | 10.53%        |
| 2006     | 120  | 120  | -10.78%        | -11.95%          | 27.50%  | 44.17%  | 7.50%         | 120  | 0.13%          | 1.39%            | 57.50%  | 79.17%  | 7.50%         |
| 2007     | 118  | 118  | 8.32%          | 6.54%            | 70.34%  | 56.78%  | 1.69%         | 118  | 9.73%          | 7.74%            | 87.29%  | 41.53%  | 9.32%         |
| 2008     | 120  | 120  | 10.42%         | 13.23%           | 70.00%  | 78.33%  | 0.83%         | 120  | 6.60%          | 6.89%            | 82.50%  | 13.33%  | 3.33%         |
| 2009     | 115  | 115  | 3.53%          | 2.61%            | 55.65%  | 12.17%  | 6.96%         | 115  | -0.29%         | -0.58%           | 45.22%  | 6.09%   | 11.30%        |
| 2010     | 120  | 120  | 20.04%         | 16.82%           | 70.00%  | 10.83%  | 5.00%         | 120  | 7.86%          | 8.61%            | 78.33%  | 4.17%   | 12.50%        |
| 2011     | 109  | 109  | 12.55%         | 10.58%           | 66.97%  | 20.18%  | 5.50%         | 109  | 5.05%          | 4.81%            | 74.31%  | 3.67%   | 8.26%         |
| 2012     | 103  | 103  | -2.88%         | -1.02%           | 48.54%  | 15.53%  | 0.00%         | 103  | 0.78%          | 4.51%            | 58.25%  | 16.50%  | 0.00%         |
| 2013     | 114  | 114  | 0.25%          | -0.50%           | 47.37%  | 9.65%   | 2.63%         | 114  | 3.21%          | 4.18%            | 70.18%  | 13.16%  | 5.26%         |
| 2014     | 109  | 109  | 9.85%          | 13.42%           | 70.64%  | 17.43%  | 1.83%         | 109  | 2.19%          | 1.47%            | 53.21%  | 18.35%  | 7.34%         |
| 2015     | 110  | 110  | 7.08%          | 4.31%            | 61.82%  | 29.09%  | 0.00%         | 110  | 4.22%          | 6.70%            | 70.91%  | 14.55%  | 5.45%         |
| 2016     | 107  | 107  | -2.07%         | -4.05%           | 40.19%  | 11.21%  | 2.80%         | 107  | 2.11%          | 5.60%            | 66.36%  | 17.76%  | 5.61%         |
| 2017     | 103  | 103  | -0.56%         | -4.05%           | 43.69%  | 31.07%  | 4.85%         | 103  | 2.25%          | 0.69%            | 55.34%  | 20.39%  | 16.50%        |
| 2018     | 99   | 99   | 10.03%         | 6.80%            | 73.74%  | 18.18%  | 0.00%         | 99   | 5.08%          | 1.61%            | 52.53%  | 3.03%   | 8.08%         |
| 2019     | 109  | 109  | -3.28%         | -6.07%           | 40.37%  | 36.70%  | 0.00%         | 109  | -5.51%         | -5.32%           | 18.35%  | 11.93%  | 0.00%         |
| 2020     | 86   | 86   | -13.48%        | -10.76%          | 32.56%  | 25.58%  | 0.00%         | 86   | -0.53%         | -5.54%           | 39.53%  | 19.77%  | 10.47%        |
| all buys | 1756 | 1756 | 2.94%          | 1.86%            | 53.25%  | 29.16%  | 2.56%         | 1756 | 2.50%          | 3.16%            | 61.05%  | 20.73%  | 7.57%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -4.32%      | -3.52%            | -0.79%        | -2.24%       | -2.08%   | 41.23%    | 46.14%          | 43.91%     |
| 2006     | 120  | 0.13%       | -5.01%            | 5.14%         | -1.98%       | 2.11%    | 79.17%    | 74.75%          | 72.68%     |
| 2007     | 118  | 9.73%       | -1.96%            | 11.69%        | 1.07%        | 8.67%    | 41.53%    | 65.41%          | 62.43%     |
| 2008     | 120  | 6.60%       | 2.22%             | 4.38%         | 2.70%        | 3.90%    | 13.33%    | 36.38%          | 33.71%     |
| 2009     | 115  | -0.29%      | 1.96%             | -2.25%        | 1.87%        | -2.15%   | 6.09%     | 18.84%          | 14.98%     |
| 2010     | 120  | 7.86%       | -1.65%            | 9.51%         | -0.69%       | 8.55%    | 4.17%     | 18.94%          | 14.32%     |
| 2011     | 109  | 5.05%       | -4.05%            | 9.10%         | -3.03%       | 8.09%    | 3.67%     | 19.44%          | 15.31%     |
| 2012     | 103  | 0.78%       | -3.66%            | 4.44%         | -1.85%       | 2.63%    | 16.50%    | 20.30%          | 15.17%     |
| 2013     | 114  | 3.21%       | -6.50%            | 9.71%         | -3.82%       | 7.04%    | 13.16%    | 31.99%          | 26.13%     |
| 2014     | 109  | 2.19%       | -6.93%            | 9.12%         | -4.90%       | 7.09%    | 18.35%    | 33.81%          | 29.93%     |
| 2015     | 110  | 4.22%       | -6.11%            | 10.33%        | -4.61%       | 8.83%    | 14.55%    | 30.88%          | 27.02%     |
| 2016     | 107  | 2.11%       | -4.81%            | 6.92%         | -3.82%       | 5.93%    | 17.76%    | 27.64%          | 23.66%     |
| 2017     | 103  | 2.25%       | -9.76%            | 12.00%        | -6.94%       | 9.19%    | 20.39%    | 43.75%          | 38.60%     |
| 2018     | 99   | 5.08%       | -7.73%            | 12.81%        | -4.84%       | 9.93%    | 3.03%     | 29.24%          | 21.10%     |
| 2019     | 109  | -5.51%      | -7.57%            | 2.06%         | -4.62%       | -0.89%   | 11.93%    | 31.82%          | 22.25%     |
| 2020     | 86   | -0.53%      | -4.35%            | 3.82%         | -2.95%       | 2.42%    | 19.77%    | 31.76%          | 24.71%     |
| all buys | 1756 | 2.50%       | -4.20%            | 6.70%         | -2.43%       | 4.93%    | 20.73%    | 35.81%          | 30.85%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -6.43%      | 5.34%             | -11.78%       | 5.04%        | -11.48%  | 41.23%    | 33.73%          | 32.22%     |
| 2006     | 120  | -10.78%     | 0.00%             | -10.79%       | 1.68%        | -12.47%  | 44.17%    | 32.42%          | 26.29%     |
| 2007     | 118  | 8.32%       | -2.31%            | 10.64%        | 2.55%        | 5.78%    | 56.78%    | 70.51%          | 66.32%     |
| 2008     | 120  | 10.42%      | 4.28%             | 6.14%         | 4.04%        | 6.38%    | 78.33%    | 73.93%          | 76.01%     |
| 2009     | 115  | 3.53%       | 20.37%            | -16.84%       | 14.78%       | -11.24%  | 12.17%    | 18.60%          | 15.79%     |
| 2010     | 120  | 20.04%      | 7.44%             | 12.59%        | 7.06%        | 12.98%   | 10.83%    | 26.27%          | 21.96%     |
| 2011     | 109  | 12.55%      | -4.28%            | 16.84%        | -3.86%       | 16.41%   | 20.18%    | 42.61%          | 38.13%     |
| 2012     | 103  | -2.88%      | 4.70%             | -7.58%        | 1.46%        | -4.34%   | 15.53%    | 20.78%          | 17.03%     |
| 2013     | 114  | 0.25%       | 0.30%             | -0.05%        | 0.63%        | -0.38%   | 9.65%     | 23.11%          | 17.73%     |
| 2014     | 109  | 9.85%       | -3.90%            | 13.75%        | -2.87%       | 12.72%   | 17.43%    | 41.15%          | 37.30%     |
| 2015     | 110  | 7.08%       | -5.69%            | 12.77%        | -2.93%       | 10.01%   | 29.09%    | 51.29%          | 46.51%     |
| 2016     | 107  | -2.07%      | 2.16%             | -4.24%        | -1.17%       | -0.90%   | 11.21%    | 24.94%          | 23.00%     |
| 2017     | 103  | -0.56%      | -1.38%            | 0.82%         | -1.47%       | 0.91%    | 31.07%    | 35.88%          | 32.80%     |
| 2018     | 99   | 10.03%      | -4.82%            | 14.85%        | -0.96%       | 10.99%   | 18.18%    | 47.30%          | 40.10%     |
| 2019     | 109  | -3.28%      | -10.72%           | 7.43%         | -4.62%       | 1.33%    | 36.70%    | 52.03%          | 43.33%     |
| 2020     | 86   | -13.48%     | 17.24%            | -30.72%       | 5.96%        | -19.43%  | 25.58%    | 17.97%          | 13.66%     |
| all buys | 1756 | 2.94%       | 1.92%             | 1.02%         | 1.66%        | 1.28%    | 29.16%    | 38.65%          | 34.77%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 101
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 1983.1 (min 1813)
- mean with a tradable quote: 1939.0 (min 1780)
- forced delisting liquidations: 62 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 4 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `0aeea637e84c41d9`, train run `f259c702a6a6`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_v141_f259c702a6a6`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_v141_0d86c0074c6ba825_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_v141_0d86c0074c6ba825_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_v141_0d86c0074c6ba825_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_v141_0d86c0074c6ba825_equity.png`
