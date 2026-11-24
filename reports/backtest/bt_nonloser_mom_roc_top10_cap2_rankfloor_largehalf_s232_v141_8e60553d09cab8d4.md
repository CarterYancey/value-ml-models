# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s232_v141

- run `bf6e4a9510fb`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `8e60553d09cab8d4`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 995,840.90  | 803,840.90 | 14.20%         | 12.56%   | -38.59%      | 1,234.76   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 6.40%        | 7.09%         | -0.69% | 12,000.00 | 114    | -268.5322       |
| 2006              | 9.84%        | 13.61%        | -3.77% | 12,000.00 | 120    | -275.4250       |
| 2007              | 1.46%        | 4.40%         | -2.94% | 12,000.00 | 119    | -250.2773       |
| 2008 (GFC)        | -20.82%      | -34.30%       | 13.48% | 12,000.00 | 120    | -239.4444       |
| 2009 (GFC)        | 27.35%       | 24.74%        | 2.61%  | 12,000.00 | 115    | -166.4029       |
| 2010              | 25.68%       | 14.30%        | 11.39% | 12,000.00 | 120    | -269.1167       |
| 2011              | 8.76%        | 2.46%         | 6.30%  | 12,000.00 | 109    | -216.6422       |
| 2012              | 18.85%       | 17.09%        | 1.75%  | 12,000.00 | 105    | -155.7714       |
| 2013              | 37.56%       | 27.75%        | 9.81%  | 12,000.00 | 114    | -195.7865       |
| 2014              | 13.48%       | 14.49%        | -1.02% | 12,000.00 | 110    | -203.3455       |
| 2015              | 6.96%        | -0.11%        | 7.07%  | 12,000.00 | 105    | -149.5365       |
| 2016              | 12.84%       | 14.45%        | -1.61% | 12,000.00 | 106    | -135.1195       |
| 2017              | 22.12%       | 21.63%        | 0.48%  | 12,000.00 | 102    | -206.4183       |
| 2018              | -2.88%       | -5.13%        | 2.25%  | 12,000.00 | 101    | -184.5941       |
| 2019              | 41.46%       | 32.30%        | 9.15%  | 12,000.00 | 108    | -166.8858       |
| 2020 (COVID)      | 20.74%       | 15.69%        | 5.05%  | 12,000.00 | 84     | -151.3770       |
| 2021              | 22.26%       | 31.26%        | -9.00% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -15.67%      | -18.98%       | 3.30%  | 0.00      | 0      | —               |
| 2023              | 23.60%       | 26.71%        | -3.11% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 315  | 17.98% |
| Technology             | 292  | 16.67% |
| Industrials            | 289  | 16.50% |
| Healthcare             | 268  | 15.30% |
| Consumer Cyclical      | 242  | 13.81% |
| Communication Services | 126  | 7.19%  |
| Basic Materials        | 82   | 4.68%  |
| Energy                 | 57   | 3.25%  |
| Financial Services     | 56   | 3.20%  |
| Real Estate            | 13   | 0.74%  |
| Utilities              | 12   | 0.68%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 114  | 26     | 9      | Industrials            | 21.05%        |
| 2006 | 120  | 30     | 9      | Healthcare             | 20.00%        |
| 2007 | 119  | 32     | 9      | Consumer Defensive     | 20.17%        |
| 2008 | 120  | 31     | 8      | Industrials            | 20.00%        |
| 2009 | 115  | 32     | 10     | Consumer Defensive     | 20.87%        |
| 2010 | 120  | 27     | 10     | Consumer Defensive     | 20.00%        |
| 2011 | 109  | 28     | 9      | Consumer Defensive     | 19.27%        |
| 2012 | 105  | 25     | 8      | Consumer Defensive     | 22.86%        |
| 2013 | 114  | 31     | 8      | Communication Services | 18.42%        |
| 2014 | 110  | 27     | 7      | Industrials            | 19.09%        |
| 2015 | 105  | 23     | 8      | Consumer Defensive     | 22.86%        |
| 2016 | 106  | 27     | 7      | Technology             | 22.64%        |
| 2017 | 102  | 25     | 8      | Technology             | 21.57%        |
| 2018 | 101  | 25     | 8      | Consumer Cyclical      | 23.76%        |
| 2019 | 108  | 26     | 6      | Consumer Cyclical      | 22.22%        |
| 2020 | 84   | 27     | 8      | Consumer Defensive     | 25.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 114  | 114  | -7.45%         | -8.03%           | 25.44%  | 43.86%  | 0.00%         | 114  | -5.86%         | 0.62%            | 56.14%  | 41.23%  | 10.53%        |
| 2006     | 120  | 120  | -11.18%        | -11.95%          | 25.00%  | 43.33%  | 5.00%         | 120  | 0.77%          | 2.05%            | 60.00%  | 74.17%  | 5.00%         |
| 2007     | 119  | 119  | 8.04%          | 6.17%            | 68.91%  | 57.14%  | 2.52%         | 119  | 9.79%          | 7.71%            | 86.55%  | 42.02%  | 11.76%        |
| 2008     | 120  | 120  | 10.55%         | 11.51%           | 70.00%  | 78.33%  | 0.83%         | 120  | 7.17%          | 7.43%            | 85.00%  | 10.83%  | 3.33%         |
| 2009     | 115  | 115  | 2.85%          | 2.45%            | 54.78%  | 13.04%  | 6.96%         | 115  | -0.41%         | -0.58%           | 46.09%  | 7.83%   | 12.17%        |
| 2010     | 120  | 120  | 20.43%         | 17.64%           | 72.50%  | 8.33%   | 10.00%        | 120  | 10.02%         | 9.50%            | 81.67%  | 1.67%   | 17.50%        |
| 2011     | 109  | 109  | 12.72%         | 9.81%            | 67.89%  | 17.43%  | 5.50%         | 109  | 5.38%          | 4.79%            | 76.15%  | 4.59%   | 8.26%         |
| 2012     | 105  | 105  | -0.15%         | 0.41%            | 50.48%  | 15.24%  | 0.00%         | 105  | 1.88%          | 5.07%            | 60.00%  | 15.24%  | 0.00%         |
| 2013     | 114  | 114  | 0.58%          | -0.24%           | 49.12%  | 9.65%   | 2.63%         | 114  | 2.36%          | 3.95%            | 67.54%  | 15.79%  | 5.26%         |
| 2014     | 110  | 110  | 13.17%         | 16.05%           | 75.45%  | 14.55%  | 1.82%         | 110  | 2.68%          | 2.53%            | 55.45%  | 18.18%  | 7.27%         |
| 2015     | 105  | 105  | 6.25%          | 3.96%            | 60.95%  | 29.52%  | 0.00%         | 105  | 4.18%          | 6.60%            | 71.43%  | 12.38%  | 5.71%         |
| 2016     | 106  | 106  | -2.71%         | -4.98%           | 37.74%  | 13.21%  | 2.83%         | 106  | 1.66%          | 5.09%            | 64.15%  | 17.92%  | 5.66%         |
| 2017     | 102  | 102  | -0.15%         | -4.19%           | 44.12%  | 28.43%  | 7.84%         | 102  | 2.59%          | 0.70%            | 55.88%  | 17.65%  | 19.61%        |
| 2018     | 101  | 101  | 9.41%          | 6.53%            | 71.29%  | 22.77%  | 0.00%         | 101  | 4.97%          | 0.24%            | 52.48%  | 2.97%   | 8.91%         |
| 2019     | 108  | 108  | -3.21%         | -4.70%           | 41.67%  | 33.33%  | 0.00%         | 108  | -5.01%         | -5.34%           | 18.52%  | 8.33%   | 0.00%         |
| 2020     | 84   | 84   | -11.73%        | -16.53%          | 34.52%  | 25.00%  | 0.00%         | 84   | 0.21%          | -2.18%           | 40.48%  | 21.43%  | 10.71%        |
| all buys | 1752 | 1752 | 3.24%          | 1.88%            | 53.42%  | 28.82%  | 2.97%         | 1752 | 2.75%          | 3.42%            | 61.82%  | 19.92%  | 8.22%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -5.86%      | -3.52%            | -2.34%        | -2.35%       | -3.51%   | 41.23%    | 46.14%          | 44.08%     |
| 2006     | 120  | 0.77%       | -5.01%            | 5.78%         | -2.16%       | 2.93%    | 74.17%    | 74.75%          | 72.81%     |
| 2007     | 119  | 9.79%       | -1.96%            | 11.75%        | 0.97%        | 8.82%    | 42.02%    | 65.41%          | 62.75%     |
| 2008     | 120  | 7.17%       | 2.22%             | 4.94%         | 2.75%        | 4.42%    | 10.83%    | 36.38%          | 33.67%     |
| 2009     | 115  | -0.41%      | 1.96%             | -2.37%        | 1.89%        | -2.29%   | 7.83%     | 18.84%          | 14.95%     |
| 2010     | 120  | 10.02%      | -1.65%            | 11.66%        | -0.64%       | 10.66%   | 1.67%     | 18.94%          | 14.21%     |
| 2011     | 109  | 5.38%       | -4.05%            | 9.43%         | -3.03%       | 8.40%    | 4.59%     | 19.44%          | 15.13%     |
| 2012     | 105  | 1.88%       | -3.66%            | 5.54%         | -1.91%       | 3.79%    | 15.24%    | 20.30%          | 15.30%     |
| 2013     | 114  | 2.36%       | -6.50%            | 8.86%         | -3.65%       | 6.01%    | 15.79%    | 31.99%          | 25.80%     |
| 2014     | 110  | 2.68%       | -6.93%            | 9.61%         | -5.09%       | 7.77%    | 18.18%    | 33.81%          | 30.22%     |
| 2015     | 105  | 4.18%       | -6.11%            | 10.29%        | -4.70%       | 8.88%    | 12.38%    | 30.88%          | 27.21%     |
| 2016     | 106  | 1.66%       | -4.81%            | 6.48%         | -3.95%       | 5.61%    | 17.92%    | 27.64%          | 23.87%     |
| 2017     | 102  | 2.59%       | -9.76%            | 12.35%        | -6.95%       | 9.54%    | 17.65%    | 43.75%          | 38.56%     |
| 2018     | 101  | 4.97%       | -7.73%            | 12.70%        | -4.98%       | 9.95%    | 2.97%     | 29.24%          | 21.62%     |
| 2019     | 108  | -5.01%      | -7.57%            | 2.56%         | -4.36%       | -0.65%   | 8.33%     | 31.82%          | 21.54%     |
| 2020     | 84   | 0.21%       | -4.35%            | 4.56%         | -2.89%       | 3.10%    | 21.43%    | 31.76%          | 24.17%     |
| all buys | 1752 | 2.75%       | -4.20%            | 6.94%         | -2.45%       | 5.19%    | 19.92%    | 35.81%          | 30.87%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 114  | -7.45%      | 5.34%             | -12.79%       | 4.98%        | -12.43%  | 43.86%    | 33.73%          | 32.48%     |
| 2006     | 120  | -11.18%     | 0.00%             | -11.18%       | 1.74%        | -12.92%  | 43.33%    | 32.42%          | 26.72%     |
| 2007     | 119  | 8.04%       | -2.31%            | 10.35%        | 2.56%        | 5.48%    | 57.14%    | 70.51%          | 66.63%     |
| 2008     | 120  | 10.55%      | 4.28%             | 6.28%         | 3.91%        | 6.64%    | 78.33%    | 73.93%          | 76.00%     |
| 2009     | 115  | 2.85%       | 20.37%            | -17.53%       | 14.73%       | -11.89%  | 13.04%    | 18.60%          | 15.79%     |
| 2010     | 120  | 20.43%      | 7.44%             | 12.98%        | 7.19%        | 13.23%   | 8.33%     | 26.27%          | 21.61%     |
| 2011     | 109  | 12.72%      | -4.28%            | 17.01%        | -3.80%       | 16.52%   | 17.43%    | 42.61%          | 37.99%     |
| 2012     | 105  | -0.15%      | 4.70%             | -4.84%        | 1.32%        | -1.46%   | 15.24%    | 20.78%          | 17.54%     |
| 2013     | 114  | 0.58%       | 0.30%             | 0.28%         | 0.77%        | -0.20%   | 9.65%     | 23.11%          | 17.34%     |
| 2014     | 110  | 13.17%      | -3.90%            | 17.08%        | -3.04%       | 16.21%   | 14.55%    | 41.15%          | 37.61%     |
| 2015     | 105  | 6.25%       | -5.69%            | 11.94%        | -3.35%       | 9.61%    | 29.52%    | 51.29%          | 47.68%     |
| 2016     | 106  | -2.71%      | 2.16%             | -4.88%        | -1.24%       | -1.47%   | 13.21%    | 24.94%          | 23.35%     |
| 2017     | 102  | -0.15%      | -1.38%            | 1.23%         | -1.47%       | 1.32%    | 28.43%    | 35.88%          | 32.91%     |
| 2018     | 101  | 9.41%       | -4.82%            | 14.23%        | -1.10%       | 10.51%   | 22.77%    | 47.30%          | 40.97%     |
| 2019     | 108  | -3.21%      | -10.72%           | 7.51%         | -4.28%       | 1.07%    | 33.33%    | 52.03%          | 43.02%     |
| 2020     | 84   | -11.73%     | 17.24%            | -28.97%       | 3.67%        | -15.40%  | 25.00%    | 17.97%          | 13.26%     |
| all buys | 1752 | 3.24%       | 1.92%             | 1.31%         | 1.53%        | 1.70%    | 28.82%    | 38.65%          | 34.93%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 99
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

- backtest configurations tried against dataset `1.4.1`: 12 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `8a0bce14753d0088`, train run `20e0e1dc874c`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_v141_20e0e1dc874c`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s232_v141_8e60553d09cab8d4_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s232_v141_8e60553d09cab8d4_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s232_v141_8e60553d09cab8d4_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largehalf_s232_v141_8e60553d09cab8d4_equity.png`
