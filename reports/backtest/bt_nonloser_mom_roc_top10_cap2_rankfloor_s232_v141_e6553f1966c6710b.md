# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_s232_v141

- run `7f40654a33da`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `e6553f1966c6710b`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 940,636.22  | 748,636.22 | 13.72%         | 11.86%   | -40.50%      | 1,190.88   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 3.37%        | 7.09%         | -3.71% | 12,000.00 | 108    | -362.5802       |
| 2006              | 8.35%        | 13.61%        | -5.26% | 12,000.00 | 120    | -382.7556       |
| 2007              | 0.75%        | 4.40%         | -3.65% | 12,000.00 | 116    | -340.2500       |
| 2008 (GFC)        | -22.62%      | -34.30%       | 11.68% | 12,000.00 | 120    | -302.3194       |
| 2009 (GFC)        | 28.48%       | 24.74%        | 3.74%  | 12,000.00 | 113    | -208.4484       |
| 2010              | 29.25%       | 14.30%        | 14.95% | 12,000.00 | 120    | -381.9028       |
| 2011              | 7.42%        | 2.46%         | 4.96%  | 12,000.00 | 109    | -298.6055       |
| 2012              | 15.69%       | 17.09%        | -1.40% | 12,000.00 | 108    | -198.8704       |
| 2013              | 38.15%       | 27.75%        | 10.39% | 12,000.00 | 114    | -262.9737       |
| 2014              | 9.95%        | 14.49%        | -4.54% | 12,000.00 | 112    | -293.3750       |
| 2015              | 6.99%        | -0.11%        | 7.09%  | 12,000.00 | 111    | -200.6817       |
| 2016              | 13.33%       | 14.45%        | -1.12% | 12,000.00 | 105    | -182.9302       |
| 2017              | 21.74%       | 21.63%        | 0.11%  | 12,000.00 | 105    | -293.3841       |
| 2018              | -2.12%       | -5.13%        | 3.02%  | 12,000.00 | 96     | -254.4514       |
| 2019              | 39.49%       | 32.30%        | 7.19%  | 12,000.00 | 103    | -218.1359       |
| 2020 (COVID)      | 19.35%       | 15.69%        | 3.67%  | 12,000.00 | 84     | -198.1667       |
| 2021              | 23.08%       | 31.26%        | -8.18% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -16.58%      | -18.98%       | 2.39%  | 0.00      | 0      | —               |
| 2023              | 24.23%       | 26.71%        | -2.48% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 296  | 16.97% |
| Technology             | 288  | 16.51% |
| Healthcare             | 275  | 15.77% |
| Industrials            | 269  | 15.42% |
| Consumer Cyclical      | 264  | 15.14% |
| Communication Services | 110  | 6.31%  |
| Basic Materials        | 98   | 5.62%  |
| Financial Services     | 62   | 3.56%  |
| Energy                 | 60   | 3.44%  |
| Real Estate            | 13   | 0.75%  |
| Utilities              | 9    | 0.52%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 25     | 10     | Industrials        | 22.22%        |
| 2006 | 120  | 29     | 9      | Consumer Cyclical  | 20.00%        |
| 2007 | 116  | 33     | 9      | Consumer Defensive | 18.10%        |
| 2008 | 120  | 31     | 8      | Consumer Defensive | 20.00%        |
| 2009 | 113  | 33     | 10     | Technology         | 21.24%        |
| 2010 | 120  | 30     | 8      | Consumer Defensive | 20.00%        |
| 2011 | 109  | 29     | 9      | Consumer Defensive | 19.27%        |
| 2012 | 108  | 30     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 114  | 30     | 8      | Healthcare         | 18.42%        |
| 2014 | 112  | 26     | 7      | Technology         | 21.43%        |
| 2015 | 111  | 25     | 8      | Consumer Defensive | 21.62%        |
| 2016 | 105  | 30     | 7      | Consumer Defensive | 22.86%        |
| 2017 | 105  | 27     | 9      | Technology         | 21.90%        |
| 2018 | 96   | 24     | 8      | Consumer Cyclical  | 25.00%        |
| 2019 | 103  | 27     | 7      | Consumer Defensive | 23.30%        |
| 2020 | 84   | 27     | 8      | Technology         | 23.81%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -7.15%         | -7.08%           | 31.48%  | 40.74%  | 2.78%         | 108  | -4.53%         | 0.32%            | 53.70%  | 40.74%  | 16.67%        |
| 2006     | 120  | 120  | -11.13%        | -11.73%          | 27.50%  | 44.17%  | 5.00%         | 120  | 1.14%          | 1.97%            | 60.83%  | 75.83%  | 5.00%         |
| 2007     | 116  | 116  | 4.11%          | 4.65%            | 62.93%  | 60.34%  | 1.72%         | 116  | 7.37%          | 7.34%            | 77.59%  | 45.69%  | 12.07%        |
| 2008     | 120  | 120  | 8.15%          | 10.14%           | 60.83%  | 76.67%  | 0.83%         | 120  | 6.59%          | 7.73%            | 83.33%  | 13.33%  | 3.33%         |
| 2009     | 113  | 113  | 7.22%          | 9.17%            | 61.06%  | 12.39%  | 7.08%         | 113  | -0.15%         | -0.22%           | 47.79%  | 8.85%   | 14.16%        |
| 2010     | 120  | 120  | 25.75%         | 17.75%           | 75.83%  | 7.50%   | 4.17%         | 120  | 9.44%          | 9.15%            | 80.00%  | 1.67%   | 7.50%         |
| 2011     | 109  | 109  | 10.94%         | 7.72%            | 65.14%  | 21.10%  | 5.50%         | 109  | 3.57%          | 3.95%            | 66.97%  | 9.17%   | 8.26%         |
| 2012     | 108  | 108  | -1.11%         | -2.64%           | 46.30%  | 17.59%  | 0.00%         | 108  | 0.21%          | 2.53%            | 54.63%  | 14.81%  | 0.93%         |
| 2013     | 114  | 114  | 1.12%          | -0.50%           | 47.37%  | 12.28%  | 2.63%         | 114  | 3.03%          | 4.29%            | 68.42%  | 15.79%  | 5.26%         |
| 2014     | 112  | 112  | 13.70%         | 17.15%           | 73.21%  | 16.07%  | 1.79%         | 112  | 3.26%          | 3.10%            | 56.25%  | 16.96%  | 4.46%         |
| 2015     | 111  | 111  | 5.21%          | 3.19%            | 60.36%  | 29.73%  | 0.00%         | 111  | 3.50%          | 6.08%            | 71.17%  | 13.51%  | 5.41%         |
| 2016     | 105  | 105  | -1.08%         | -4.04%           | 41.90%  | 13.33%  | 2.86%         | 105  | 2.35%          | 4.72%            | 65.71%  | 15.24%  | 8.57%         |
| 2017     | 105  | 105  | -1.08%         | -4.51%           | 41.90%  | 27.62%  | 4.76%         | 105  | 2.56%          | 0.30%            | 53.33%  | 19.05%  | 14.29%        |
| 2018     | 96   | 96   | 8.65%          | 6.22%            | 69.79%  | 22.92%  | 0.00%         | 96   | 4.44%          | 0.08%            | 51.04%  | 4.17%   | 9.38%         |
| 2019     | 103  | 103  | -2.91%         | -4.37%           | 41.75%  | 35.92%  | 0.00%         | 103  | -4.79%         | -5.58%           | 20.39%  | 12.62%  | 0.00%         |
| 2020     | 84   | 84   | -12.93%        | -13.31%          | 34.52%  | 28.57%  | 0.00%         | 84   | -1.69%         | -2.22%           | 41.67%  | 23.81%  | 10.71%        |
| all buys | 1744 | 1744 | 3.31%          | 1.86%            | 52.98%  | 29.53%  | 2.52%         | 1744 | 2.42%          | 3.02%            | 60.38%  | 21.04%  | 7.80%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -4.53%      | -7.65%            | 3.12%         | -3.03%       | -1.50%   | 40.74%    | 51.93%          | 45.06%     |
| 2006     | 120  | 1.14%       | -9.20%            | 10.35%        | -2.65%       | 3.79%    | 75.83%    | 77.47%          | 73.28%     |
| 2007     | 116  | 7.37%       | -6.61%            | 13.98%        | 0.12%        | 7.25%    | 45.69%    | 69.62%          | 63.43%     |
| 2008     | 120  | 6.59%       | -1.41%            | 8.00%         | 1.77%        | 4.82%    | 13.33%    | 42.57%          | 35.54%     |
| 2009     | 113  | -0.15%      | -0.01%            | -0.14%        | 1.96%        | -2.11%   | 8.85%     | 24.96%          | 15.92%     |
| 2010     | 120  | 9.44%       | -5.91%            | 15.34%        | -1.44%       | 10.88%   | 1.67%     | 27.42%          | 16.43%     |
| 2011     | 109  | 3.57%       | -7.68%            | 11.25%        | -3.32%       | 6.89%    | 9.17%     | 27.47%          | 15.97%     |
| 2012     | 108  | 0.21%       | -7.07%            | 7.28%         | -3.16%       | 3.37%    | 14.81%    | 27.79%          | 18.67%     |
| 2013     | 114  | 3.03%       | -10.38%           | 13.41%        | -4.20%       | 7.23%    | 15.79%    | 39.52%          | 27.03%     |
| 2014     | 112  | 3.26%       | -11.40%           | 14.66%        | -5.28%       | 8.54%    | 16.96%    | 41.08%          | 30.43%     |
| 2015     | 111  | 3.50%       | -10.39%           | 13.89%        | -4.85%       | 8.35%    | 13.51%    | 37.61%          | 27.29%     |
| 2016     | 105  | 2.35%       | -9.18%            | 11.53%        | -3.96%       | 6.31%    | 15.24%    | 35.01%          | 23.95%     |
| 2017     | 105  | 2.56%       | -14.54%           | 17.10%        | -7.53%       | 10.09%   | 19.05%    | 50.60%          | 39.80%     |
| 2018     | 96   | 4.44%       | -11.65%           | 16.08%        | -4.99%       | 9.43%    | 4.17%     | 36.68%          | 21.58%     |
| 2019     | 103  | -4.79%      | -11.93%           | 7.14%         | -4.98%       | 0.19%    | 12.62%    | 39.82%          | 23.54%     |
| 2020     | 84   | -1.69%      | -8.77%            | 7.08%         | -2.82%       | 1.13%    | 23.81%    | 39.44%          | 24.62%     |
| all buys | 1744 | 2.42%       | -8.20%            | 10.62%        | -2.93%       | 5.36%    | 21.04%    | 42.54%          | 31.87%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -7.15%      | 5.25%             | -12.40%       | 5.27%        | -12.42%  | 40.74%    | 38.73%          | 33.08%     |
| 2006     | 120  | -11.13%     | -0.15%            | -10.98%       | 1.50%        | -12.63%  | 44.17%    | 38.08%          | 27.60%     |
| 2007     | 116  | 4.11%       | -7.00%            | 11.11%        | 1.52%        | 2.59%    | 60.34%    | 73.36%          | 66.79%     |
| 2008     | 120  | 8.15%       | 4.28%             | 3.87%         | 3.92%        | 4.23%    | 76.67%    | 73.80%          | 75.57%     |
| 2009     | 113  | 7.22%       | 31.66%            | -24.44%       | 16.03%       | -8.81%   | 12.39%    | 23.03%          | 16.31%     |
| 2010     | 120  | 25.75%      | 5.09%             | 20.66%        | 6.47%        | 19.27%   | 7.50%     | 33.28%          | 24.49%     |
| 2011     | 109  | 10.94%      | -7.55%            | 18.49%        | -4.09%       | 15.03%   | 21.10%    | 48.29%          | 39.08%     |
| 2012     | 108  | -1.11%      | 3.72%             | -4.83%        | 2.40%        | -3.51%   | 17.59%    | 27.49%          | 20.04%     |
| 2013     | 114  | 1.12%       | 1.72%             | -0.60%        | 0.75%        | 0.37%    | 12.28%    | 28.73%          | 18.35%     |
| 2014     | 112  | 13.70%      | -7.02%            | 20.72%        | -2.95%       | 16.65%   | 16.07%    | 47.37%          | 37.42%     |
| 2015     | 111  | 5.21%       | -9.45%            | 14.65%        | -3.19%       | 8.39%    | 29.73%    | 56.17%          | 46.84%     |
| 2016     | 105  | -1.08%      | 2.15%             | -3.23%        | -1.37%       | 0.29%    | 13.33%    | 30.43%          | 23.56%     |
| 2017     | 105  | -1.08%      | -1.39%            | 0.31%         | -1.97%       | 0.88%    | 27.62%    | 40.54%          | 34.22%     |
| 2018     | 96   | 8.65%       | -9.90%            | 18.56%        | -1.47%       | 10.13%   | 22.92%    | 53.76%          | 40.81%     |
| 2019     | 103  | -2.91%      | -9.73%            | 6.82%         | -5.16%       | 2.25%    | 35.92%    | 55.97%          | 43.72%     |
| 2020     | 84   | -12.93%     | 33.15%            | -46.08%       | 5.45%        | -18.39%  | 28.57%    | 22.31%          | 13.99%     |
| all buys | 1744 | 3.31%       | 2.26%             | 1.05%         | 1.51%        | 1.81%    | 29.53%    | 43.57%          | 35.58%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 109
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3220.5 (min 2912)
- mean with a tradable quote: 3143.5 (min 2860)
- forced delisting liquidations: 70 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 11 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `8a0bce14753d0088`, train run `20e0e1dc874c`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_v141_20e0e1dc874c`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s232_v141_e6553f1966c6710b_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s232_v141_e6553f1966c6710b_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s232_v141_e6553f1966c6710b_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_s232_v141_e6553f1966c6710b_equity.png`
