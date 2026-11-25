# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_v141

- run `4ac764da0cc9`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `f2236a06a7cf9526`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 932,471.09  | 740,471.09 | 13.65%         | 11.76%   | -41.02%      | 1,231.12   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 3.37%        | 7.09%         | -3.71% | 12,000.00 | 108    | -359.0864       |
| 2006              | 7.78%        | 13.61%        | -5.83% | 12,000.00 | 120    | -381.4222       |
| 2007              | -0.20%       | 4.40%         | -4.60% | 12,000.00 | 116    | -338.5345       |
| 2008 (GFC)        | -22.64%      | -34.30%       | 11.67% | 12,000.00 | 120    | -294.5472       |
| 2009 (GFC)        | 28.78%       | 24.74%        | 4.04%  | 12,000.00 | 113    | -208.6991       |
| 2010              | 29.70%       | 14.30%        | 15.40% | 12,000.00 | 120    | -380.4889       |
| 2011              | 7.26%        | 2.46%         | 4.80%  | 12,000.00 | 109    | -294.2752       |
| 2012              | 15.63%       | 17.09%        | -1.46% | 12,000.00 | 106    | -195.5440       |
| 2013              | 38.88%       | 27.75%        | 11.13% | 12,000.00 | 114    | -262.2778       |
| 2014              | 9.98%        | 14.49%        | -4.52% | 12,000.00 | 111    | -292.0420       |
| 2015              | 6.78%        | -0.11%        | 6.89%  | 12,000.00 | 110    | -200            |
| 2016              | 13.58%       | 14.45%        | -0.87% | 12,000.00 | 109    | -187.6544       |
| 2017              | 22.12%       | 21.63%        | 0.48%  | 12,000.00 | 100    | -289.1400       |
| 2018              | -2.35%       | -5.13%        | 2.79%  | 12,000.00 | 97     | -252.5086       |
| 2019              | 39.28%       | 32.30%        | 6.98%  | 12,000.00 | 102    | -215.7157       |
| 2020 (COVID)      | 19.17%       | 15.69%        | 3.49%  | 12,000.00 | 86     | -200.9264       |
| 2021              | 22.36%       | 31.26%        | -8.90% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -16.45%      | -18.98%       | 2.53%  | 0.00      | 0      | —               |
| 2023              | 23.61%       | 26.71%        | -3.09% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 306  | 17.58% |
| Healthcare             | 275  | 15.80% |
| Industrials            | 274  | 15.74% |
| Technology             | 271  | 15.57% |
| Consumer Cyclical      | 261  | 14.99% |
| Communication Services | 114  | 6.55%  |
| Basic Materials        | 97   | 5.57%  |
| Financial Services     | 61   | 3.50%  |
| Energy                 | 60   | 3.45%  |
| Real Estate            | 13   | 0.75%  |
| Utilities              | 9    | 0.52%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 25     | 10     | Industrials            | 22.22%        |
| 2006 | 120  | 29     | 9      | Consumer Cyclical      | 20.00%        |
| 2007 | 116  | 30     | 9      | Consumer Cyclical      | 19.83%        |
| 2008 | 120  | 31     | 8      | Healthcare             | 20.00%        |
| 2009 | 113  | 32     | 10     | Healthcare             | 21.24%        |
| 2010 | 120  | 29     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive     | 22.02%        |
| 2012 | 106  | 28     | 8      | Consumer Defensive     | 22.64%        |
| 2013 | 114  | 29     | 8      | Communication Services | 21.05%        |
| 2014 | 111  | 27     | 7      | Technology             | 21.62%        |
| 2015 | 110  | 24     | 8      | Consumer Defensive     | 21.82%        |
| 2016 | 109  | 30     | 7      | Consumer Defensive     | 22.02%        |
| 2017 | 100  | 27     | 9      | Technology             | 22.00%        |
| 2018 | 97   | 24     | 8      | Consumer Cyclical      | 24.74%        |
| 2019 | 102  | 27     | 7      | Consumer Defensive     | 23.53%        |
| 2020 | 86   | 26     | 8      | Consumer Defensive     | 23.26%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -7.15%         | -7.08%           | 31.48%  | 40.74%  | 2.78%         | 108  | -4.53%         | 0.32%            | 53.70%  | 40.74%  | 16.67%        |
| 2006     | 120  | 120  | -12.58%        | -12.64%          | 25.00%  | 46.67%  | 5.00%         | 120  | 0.78%          | 1.61%            | 58.33%  | 75.83%  | 5.00%         |
| 2007     | 116  | 116  | 3.34%          | 3.87%            | 62.07%  | 62.93%  | 1.72%         | 116  | 6.82%          | 7.19%            | 76.72%  | 47.41%  | 12.07%        |
| 2008     | 120  | 120  | 8.99%          | 11.16%           | 63.33%  | 76.67%  | 0.83%         | 120  | 7.20%          | 7.73%            | 85.83%  | 10.83%  | 3.33%         |
| 2009     | 113  | 113  | 6.62%          | 5.41%            | 59.29%  | 11.50%  | 7.08%         | 113  | -0.70%         | -0.35%           | 46.02%  | 8.85%   | 14.16%        |
| 2010     | 120  | 120  | 26.44%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 10.26%         | 9.15%            | 77.50%  | 1.67%   | 5.00%         |
| 2011     | 109  | 109  | 8.84%          | 7.72%            | 65.14%  | 21.10%  | 5.50%         | 109  | 4.50%          | 4.41%            | 68.81%  | 9.17%   | 8.26%         |
| 2012     | 106  | 106  | -3.08%         | -5.54%           | 42.45%  | 19.81%  | 0.00%         | 106  | -0.67%         | 2.36%            | 53.77%  | 16.04%  | 0.94%         |
| 2013     | 114  | 114  | 0.31%          | -0.75%           | 46.49%  | 12.28%  | 2.63%         | 114  | 2.29%          | 3.68%            | 64.91%  | 17.54%  | 5.26%         |
| 2014     | 111  | 111  | 12.62%         | 16.30%           | 72.97%  | 16.22%  | 1.80%         | 111  | 3.45%          | 3.17%            | 55.86%  | 17.12%  | 5.41%         |
| 2015     | 110  | 110  | 6.48%          | 4.39%            | 63.64%  | 26.36%  | 0.00%         | 110  | 3.74%          | 6.63%            | 72.73%  | 12.73%  | 5.45%         |
| 2016     | 109  | 109  | -1.75%         | -4.55%           | 37.61%  | 12.84%  | 2.75%         | 109  | 1.47%          | 5.30%            | 61.47%  | 20.18%  | 5.50%         |
| 2017     | 100  | 100  | 0.16%          | -3.82%           | 45.00%  | 25.00%  | 5.00%         | 100  | 2.15%          | 0.26%            | 52.00%  | 19.00%  | 15.00%        |
| 2018     | 97   | 97   | 8.81%          | 6.45%            | 70.10%  | 22.68%  | 0.00%         | 97   | 4.40%          | 0.12%            | 51.55%  | 4.12%   | 9.28%         |
| 2019     | 102  | 102  | -3.80%         | -8.10%           | 40.20%  | 39.22%  | 0.00%         | 102  | -4.84%         | -5.94%           | 20.59%  | 12.75%  | 0.00%         |
| 2020     | 86   | 86   | -15.52%        | -17.88%          | 32.56%  | 30.23%  | 0.00%         | 86   | -2.49%         | -4.24%           | 37.21%  | 24.42%  | 10.47%        |
| all buys | 1741 | 1741 | 2.79%          | 1.42%            | 52.38%  | 29.87%  | 2.35%         | 1741 | 2.29%          | 2.65%            | 59.45%  | 21.48%  | 7.52%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -4.53%      | -7.65%            | 3.12%         | -3.03%       | -1.50%   | 40.74%    | 51.93%          | 45.06%     |
| 2006     | 120  | 0.78%       | -9.20%            | 9.99%         | -2.58%       | 3.37%    | 75.83%    | 77.47%          | 73.30%     |
| 2007     | 116  | 6.82%       | -6.61%            | 13.42%        | -0.08%       | 6.89%    | 47.41%    | 69.62%          | 63.58%     |
| 2008     | 120  | 7.20%       | -1.41%            | 8.61%         | 1.77%        | 5.43%    | 10.83%    | 42.57%          | 35.54%     |
| 2009     | 113  | -0.70%      | -0.01%            | -0.69%        | 1.76%        | -2.46%   | 8.85%     | 24.96%          | 16.42%     |
| 2010     | 120  | 10.26%      | -5.91%            | 16.16%        | -1.10%       | 11.36%   | 1.67%     | 27.42%          | 15.83%     |
| 2011     | 109  | 4.50%       | -7.68%            | 12.18%        | -3.49%       | 7.99%    | 9.17%     | 27.47%          | 16.62%     |
| 2012     | 106  | -0.67%      | -7.07%            | 6.41%         | -3.09%       | 2.43%    | 16.04%    | 27.79%          | 18.57%     |
| 2013     | 114  | 2.29%       | -10.38%           | 12.67%        | -4.29%       | 6.58%    | 17.54%    | 39.52%          | 27.34%     |
| 2014     | 111  | 3.45%       | -11.40%           | 14.85%        | -5.10%       | 8.55%    | 17.12%    | 41.08%          | 30.18%     |
| 2015     | 110  | 3.74%       | -10.39%           | 14.13%        | -4.80%       | 8.54%    | 12.73%    | 37.61%          | 27.22%     |
| 2016     | 109  | 1.47%       | -9.18%            | 10.65%        | -4.14%       | 5.61%    | 20.18%    | 35.01%          | 24.64%     |
| 2017     | 100  | 2.15%       | -14.54%           | 16.69%        | -7.39%       | 9.54%    | 19.00%    | 50.60%          | 39.65%     |
| 2018     | 97   | 4.40%       | -11.65%           | 16.05%        | -4.97%       | 9.37%    | 4.12%     | 36.68%          | 21.51%     |
| 2019     | 102  | -4.84%      | -11.93%           | 7.09%         | -5.10%       | 0.25%    | 12.75%    | 39.82%          | 23.74%     |
| 2020     | 86   | -2.49%      | -8.77%            | 6.28%         | -2.77%       | 0.28%    | 24.42%    | 39.44%          | 24.80%     |
| all buys | 1741 | 2.29%       | -8.20%            | 10.49%        | -2.92%       | 5.21%    | 21.48%    | 42.54%          | 31.93%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -7.15%      | 5.25%             | -12.40%       | 5.27%        | -12.42%  | 40.74%    | 38.73%          | 33.08%     |
| 2006     | 120  | -12.58%     | -0.15%            | -12.43%       | 1.48%        | -14.05%  | 46.67%    | 38.08%          | 27.55%     |
| 2007     | 116  | 3.34%       | -7.00%            | 10.33%        | 1.31%        | 2.02%    | 62.93%    | 73.36%          | 67.06%     |
| 2008     | 120  | 8.99%       | 4.28%             | 4.72%         | 3.92%        | 5.08%    | 76.67%    | 73.80%          | 75.57%     |
| 2009     | 113  | 6.62%       | 31.66%            | -25.04%       | 15.94%       | -9.32%   | 11.50%    | 23.03%          | 16.68%     |
| 2010     | 120  | 26.44%      | 5.09%             | 21.35%        | 6.67%        | 19.77%   | 8.33%     | 33.28%          | 23.80%     |
| 2011     | 109  | 8.84%       | -7.55%            | 16.38%        | -4.31%       | 13.15%   | 21.10%    | 48.29%          | 39.55%     |
| 2012     | 106  | -3.08%      | 3.72%             | -6.79%        | 2.38%        | -5.46%   | 19.81%    | 27.49%          | 19.84%     |
| 2013     | 114  | 0.31%       | 1.72%             | -1.40%        | 0.74%        | -0.43%   | 12.28%    | 28.73%          | 18.63%     |
| 2014     | 111  | 12.62%      | -7.02%            | 19.64%        | -2.95%       | 15.57%   | 16.22%    | 47.37%          | 36.93%     |
| 2015     | 110  | 6.48%       | -9.45%            | 15.93%        | -2.96%       | 9.45%    | 26.36%    | 56.17%          | 46.50%     |
| 2016     | 109  | -1.75%      | 2.15%             | -3.90%        | -1.20%       | -0.56%   | 12.84%    | 30.43%          | 23.77%     |
| 2017     | 100  | 0.16%       | -1.39%            | 1.55%         | -1.80%       | 1.96%    | 25.00%    | 40.54%          | 33.66%     |
| 2018     | 97   | 8.81%       | -9.90%            | 18.71%        | -1.45%       | 10.26%   | 22.68%    | 53.76%          | 40.66%     |
| 2019     | 102  | -3.80%      | -9.73%            | 5.94%         | -5.53%       | 1.74%    | 39.22%    | 55.97%          | 44.48%     |
| 2020     | 86   | -15.52%     | 33.15%            | -48.67%       | 6.33%        | -21.85%  | 30.23%    | 22.31%          | 14.15%     |
| all buys | 1741 | 2.79%       | 2.26%             | 0.53%         | 1.56%        | 1.23%    | 29.87%    | 43.57%          | 35.54%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 106
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3220.5 (min 2912)
- mean with a tradable quote: 3143.5 (min 2860)
- forced delisting liquidations: 71 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 1 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `0aeea637e84c41d9`, train run `f259c702a6a6`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_v141_f259c702a6a6`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_v141_f2236a06a7cf9526_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_v141_f2236a06a7cf9526_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_v141_f2236a06a7cf9526_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_v141_f2236a06a7cf9526_equity.png`
