# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s1776_v141

- run `b679650d7c1f`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `c181c7da704b8c67`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 994,518.10  | 802,518.10 | 14.19%         | 12.50%   | -39.59%      | 1,243.51   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 7.92%        | 7.09%         | 0.83%  | 12,000.00 | 114    | -268.0380       |
| 2006              | 9.70%        | 13.61%        | -3.91% | 12,000.00 | 120    | -274.7556       |
| 2007              | -0.77%       | 4.40%         | -5.17% | 12,000.00 | 119    | -248.7339       |
| 2008 (GFC)        | -20.89%      | -34.30%       | 13.42% | 12,000.00 | 120    | -235.7444       |
| 2009 (GFC)        | 27.01%       | 24.74%        | 2.27%  | 12,000.00 | 113    | -166.4602       |
| 2010              | 24.49%       | 14.30%        | 10.20% | 12,000.00 | 120    | -272.0472       |
| 2011              | 9.25%        | 2.46%         | 6.79%  | 12,000.00 | 109    | -214.6177       |
| 2012              | 18.08%       | 17.09%        | 0.98%  | 12,000.00 | 105    | -154.3492       |
| 2013              | 38.79%       | 27.75%        | 11.04% | 12,000.00 | 114    | -196.8333       |
| 2014              | 13.58%       | 14.49%        | -0.92% | 12,000.00 | 110    | -201.0939       |
| 2015              | 8.10%        | -0.11%        | 8.21%  | 12,000.00 | 107    | -152.2586       |
| 2016              | 11.75%       | 14.45%        | -2.70% | 12,000.00 | 107    | -137.1121       |
| 2017              | 22.78%       | 21.63%        | 1.15%  | 12,000.00 | 100    | -203.2200       |
| 2018              | -2.52%       | -5.13%        | 2.61%  | 12,000.00 | 100    | -184.1967       |
| 2019              | 41.04%       | 32.30%        | 8.74%  | 12,000.00 | 109    | -166.3670       |
| 2020 (COVID)      | 20.44%       | 15.69%        | 4.76%  | 12,000.00 | 86     | -154.6744       |
| 2021              | 22.13%       | 31.26%        | -9.12% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -15.56%      | -18.98%       | 3.42%  | 0.00      | 0      | —               |
| 2023              | 23.55%       | 26.71%        | -3.16% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 317  | 18.08% |
| Industrials            | 287  | 16.37% |
| Healthcare             | 287  | 16.37% |
| Technology             | 269  | 15.35% |
| Consumer Cyclical      | 245  | 13.98% |
| Communication Services | 119  | 6.79%  |
| Basic Materials        | 82   | 4.68%  |
| Financial Services     | 66   | 3.76%  |
| Energy                 | 56   | 3.19%  |
| Real Estate            | 13   | 0.74%  |
| Utilities              | 12   | 0.68%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 114  | 30     | 10     | Industrials            | 21.05%        |
| 2006 | 120  | 29     | 8      | Healthcare             | 20.00%        |
| 2007 | 119  | 29     | 9      | Consumer Defensive     | 20.17%        |
| 2008 | 120  | 32     | 8      | Healthcare             | 20.00%        |
| 2009 | 113  | 32     | 9      | Consumer Defensive     | 21.24%        |
| 2010 | 120  | 31     | 10     | Consumer Defensive     | 19.17%        |
| 2011 | 109  | 27     | 9      | Consumer Defensive     | 19.27%        |
| 2012 | 105  | 24     | 8      | Consumer Defensive     | 22.86%        |
| 2013 | 114  | 32     | 8      | Communication Services | 18.42%        |
| 2014 | 110  | 27     | 8      | Industrials            | 19.09%        |
| 2015 | 107  | 23     | 8      | Consumer Defensive     | 22.43%        |
| 2016 | 107  | 27     | 8      | Technology             | 22.43%        |
| 2017 | 100  | 24     | 8      | Technology             | 21.00%        |
| 2018 | 100  | 25     | 8      | Consumer Cyclical      | 24.00%        |
| 2019 | 109  | 25     | 6      | Consumer Defensive     | 22.02%        |
| 2020 | 86   | 29     | 8      | Technology             | 20.93%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 114  | 114  | -6.10%         | -7.01%           | 30.70%  | 39.47%  | 2.63%         | 114  | -5.26%         | 0.27%            | 51.75%  | 42.98%  | 14.04%        |
| 2006     | 120  | 120  | -11.92%        | -12.64%          | 25.00%  | 45.00%  | 7.50%         | 120  | 0.01%          | 1.27%            | 57.50%  | 80.00%  | 7.50%         |
| 2007     | 119  | 119  | 7.70%          | 5.96%            | 68.91%  | 58.82%  | 1.68%         | 119  | 9.54%          | 7.71%            | 86.55%  | 41.18%  | 9.24%         |
| 2008     | 120  | 120  | 10.45%         | 12.37%           | 69.17%  | 78.33%  | 0.83%         | 120  | 6.55%          | 7.00%            | 81.67%  | 14.17%  | 3.33%         |
| 2009     | 113  | 113  | 3.55%          | 4.83%            | 57.52%  | 12.39%  | 7.08%         | 113  | -0.11%         | -0.22%           | 47.79%  | 7.96%   | 11.50%        |
| 2010     | 120  | 120  | 24.35%         | 18.95%           | 74.17%  | 10.00%  | 0.00%         | 120  | 9.17%          | 9.03%            | 78.33%  | 4.17%   | 6.67%         |
| 2011     | 109  | 109  | 10.90%         | 8.39%            | 65.14%  | 20.18%  | 5.50%         | 109  | 5.52%          | 4.81%            | 73.39%  | 4.59%   | 8.26%         |
| 2012     | 105  | 105  | 0.33%          | 1.12%            | 51.43%  | 14.29%  | 0.00%         | 105  | 2.81%          | 5.73%            | 62.86%  | 12.38%  | 0.00%         |
| 2013     | 114  | 114  | 1.52%          | -0.24%           | 48.25%  | 8.77%   | 2.63%         | 114  | 3.77%          | 4.29%            | 70.18%  | 13.16%  | 5.26%         |
| 2014     | 110  | 110  | 12.29%         | 15.43%           | 74.55%  | 14.55%  | 1.82%         | 110  | 2.73%          | 2.53%            | 55.45%  | 18.18%  | 7.27%         |
| 2015     | 107  | 107  | 5.55%          | 3.74%            | 60.75%  | 30.84%  | 0.00%         | 107  | 3.36%          | 6.51%            | 68.22%  | 14.95%  | 5.61%         |
| 2016     | 107  | 107  | 0.56%          | -1.12%           | 47.66%  | 8.41%   | 2.80%         | 107  | 2.87%          | 5.30%            | 68.22%  | 14.95%  | 5.61%         |
| 2017     | 100  | 100  | -1.35%         | -4.43%           | 41.00%  | 32.00%  | 5.00%         | 100  | 2.09%          | 0.43%            | 55.00%  | 20.00%  | 18.00%        |
| 2018     | 100  | 100  | 10.07%         | 6.81%            | 73.00%  | 21.00%  | 0.00%         | 100  | 4.92%          | -0.09%           | 50.00%  | 3.00%   | 9.00%         |
| 2019     | 109  | 109  | -4.43%         | -7.76%           | 38.53%  | 37.61%  | 0.00%         | 109  | -5.98%         | -6.09%           | 17.43%  | 13.76%  | 0.00%         |
| 2020     | 86   | 86   | -12.10%        | -13.21%          | 34.88%  | 25.58%  | 0.00%         | 86   | -0.80%         | -2.22%           | 38.37%  | 23.26%  | 10.47%        |
| all buys | 1753 | 1753 | 3.49%          | 2.27%            | 54.08%  | 29.09%  | 2.40%         | 1753 | 2.67%          | 2.91%            | 60.87%  | 20.99%  | 7.53%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -5.26%      | -3.52%            | -1.73%        | -2.12%       | -3.14%   | 42.98%    | 46.14%          | 43.52%     |
| 2006     | 120  | 0.01%       | -5.01%            | 5.02%         | -1.98%       | 1.99%    | 80.00%    | 74.75%          | 72.80%     |
| 2007     | 119  | 9.54%       | -1.96%            | 11.50%        | 1.07%        | 8.47%    | 41.18%    | 65.41%          | 62.39%     |
| 2008     | 120  | 6.55%       | 2.22%             | 4.33%         | 2.74%        | 3.81%    | 14.17%    | 36.38%          | 33.62%     |
| 2009     | 113  | -0.11%      | 1.96%             | -2.07%        | 1.84%        | -1.95%   | 7.96%     | 18.84%          | 15.10%     |
| 2010     | 120  | 9.17%       | -1.65%            | 10.82%        | -0.70%       | 9.87%    | 4.17%     | 18.94%          | 14.48%     |
| 2011     | 109  | 5.52%       | -4.05%            | 9.57%         | -3.19%       | 8.71%    | 4.59%     | 19.44%          | 15.66%     |
| 2012     | 105  | 2.81%       | -3.66%            | 6.47%         | -1.92%       | 4.73%    | 12.38%    | 20.30%          | 15.36%     |
| 2013     | 114  | 3.77%       | -6.50%            | 10.26%        | -3.97%       | 7.73%    | 13.16%    | 31.99%          | 26.43%     |
| 2014     | 110  | 2.73%       | -6.93%            | 9.66%         | -4.99%       | 7.72%    | 18.18%    | 33.81%          | 30.12%     |
| 2015     | 107  | 3.36%       | -6.11%            | 9.47%         | -4.53%       | 7.88%    | 14.95%    | 30.88%          | 26.83%     |
| 2016     | 107  | 2.87%       | -4.81%            | 7.68%         | -3.81%       | 6.68%    | 14.95%    | 27.64%          | 23.64%     |
| 2017     | 100  | 2.09%       | -9.76%            | 11.85%        | -6.94%       | 9.03%    | 20.00%    | 43.75%          | 38.45%     |
| 2018     | 100  | 4.92%       | -7.73%            | 12.65%        | -5.03%       | 9.95%    | 3.00%     | 29.24%          | 21.51%     |
| 2019     | 109  | -5.98%      | -7.57%            | 1.60%         | -4.55%       | -1.42%   | 13.76%    | 31.82%          | 22.20%     |
| 2020     | 86   | -0.80%      | -4.35%            | 3.55%         | -2.89%       | 2.09%    | 23.26%    | 31.76%          | 24.63%     |
| all buys | 1753 | 2.67%       | -4.20%            | 6.87%         | -2.44%       | 5.12%    | 20.99%    | 35.81%          | 30.91%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -6.10%      | 5.34%             | -11.45%       | 4.81%        | -10.91%  | 39.47%    | 33.73%          | 32.08%     |
| 2006     | 120  | -11.92%     | 0.00%             | -11.92%       | 1.79%        | -13.70%  | 45.00%    | 32.42%          | 26.12%     |
| 2007     | 119  | 7.70%       | -2.31%            | 10.01%        | 2.50%        | 5.20%    | 58.82%    | 70.51%          | 66.58%     |
| 2008     | 120  | 10.45%      | 4.28%             | 6.17%         | 4.04%        | 6.40%    | 78.33%    | 73.93%          | 75.95%     |
| 2009     | 113  | 3.55%       | 20.37%            | -16.83%       | 14.84%       | -11.30%  | 12.39%    | 18.60%          | 16.03%     |
| 2010     | 120  | 24.35%      | 7.44%             | 16.91%        | 7.37%        | 16.99%   | 10.00%    | 26.27%          | 21.89%     |
| 2011     | 109  | 10.90%      | -4.28%            | 15.19%        | -4.04%       | 14.94%   | 20.18%    | 42.61%          | 38.45%     |
| 2012     | 105  | 0.33%       | 4.70%             | -4.37%        | 1.48%        | -1.15%   | 14.29%    | 20.78%          | 17.42%     |
| 2013     | 114  | 1.52%       | 0.30%             | 1.22%         | 0.72%        | 0.80%    | 8.77%     | 23.11%          | 17.98%     |
| 2014     | 110  | 12.29%      | -3.90%            | 16.19%        | -2.96%       | 15.25%   | 14.55%    | 41.15%          | 37.50%     |
| 2015     | 107  | 5.55%       | -5.69%            | 11.25%        | -3.19%       | 8.74%    | 30.84%    | 51.29%          | 47.17%     |
| 2016     | 107  | 0.56%       | 2.16%             | -1.60%        | -0.82%       | 1.38%    | 8.41%     | 24.94%          | 22.86%     |
| 2017     | 100  | -1.35%      | -1.38%            | 0.03%         | -1.46%       | 0.12%    | 32.00%    | 35.88%          | 32.63%     |
| 2018     | 100  | 10.07%      | -4.82%            | 14.90%        | -1.20%       | 11.27%   | 21.00%    | 47.30%          | 40.41%     |
| 2019     | 109  | -4.43%      | -10.72%           | 6.29%         | -4.64%       | 0.21%    | 37.61%    | 52.03%          | 43.71%     |
| 2020     | 86   | -12.10%     | 17.24%            | -29.34%       | 5.32%        | -17.42%  | 25.58%    | 17.97%          | 13.90%     |
| all buys | 1753 | 3.49%       | 1.92%             | 1.57%         | 1.62%        | 1.87%    | 29.09%    | 38.65%          | 34.92%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 102
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 1983.1 (min 1813)
- mean with a tradable quote: 1939.0 (min 1780)
- forced delisting liquidations: 65 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 14 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `9152848ec411f217`, train run `8f3eb8f1d305`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_v141_8f3eb8f1d305`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s1776_v141_c181c7da704b8c67_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s1776_v141_c181c7da704b8c67_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s1776_v141_c181c7da704b8c67_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s1776_v141_c181c7da704b8c67_equity.png`
