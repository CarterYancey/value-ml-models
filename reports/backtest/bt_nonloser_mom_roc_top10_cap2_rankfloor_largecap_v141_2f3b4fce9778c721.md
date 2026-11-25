# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_largecap_v141

- run `b1562fbc2fe0`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `2f3b4fce9778c721`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 957,369.99  | 765,369.99 | 13.87%         | 12.06%   | -40.16%      | 1,217.84   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 5.93%        | 7.09%         | -1.16% | 12,000.00 | 120    | -140.1111       |
| 2006              | 11.90%       | 13.61%        | -1.71% | 12,000.00 | 120    | -143.2333       |
| 2007              | -2.68%       | 4.40%         | -7.08% | 12,000.00 | 118    | -125.9350       |
| 2008 (GFC)        | -19.94%      | -34.30%       | 14.36% | 12,000.00 | 120    | -131.8444       |
| 2009 (GFC)        | 24.44%       | 24.74%        | -0.30% | 12,000.00 | 111    | -90.4655        |
| 2010              | 22.01%       | 14.30%        | 7.72%  | 12,000.00 | 120    | -135.0667       |
| 2011              | 9.63%        | 2.46%         | 7.17%  | 12,000.00 | 109    | -106.0245       |
| 2012              | 18.46%       | 17.09%        | 1.36%  | 12,000.00 | 105    | -85.9619        |
| 2013              | 32.68%       | 27.75%        | 4.93%  | 12,000.00 | 114    | -95.7427        |
| 2014              | 17.08%       | 14.49%        | 2.58%  | 12,000.00 | 109    | -102.2110       |
| 2015              | 7.15%        | -0.11%        | 7.26%  | 12,000.00 | 106    | -79.2201        |
| 2016              | 12.96%       | 14.45%        | -1.50% | 12,000.00 | 101    | -73.1584        |
| 2017              | 23.87%       | 21.63%        | 2.24%  | 12,000.00 | 104    | -97.2404        |
| 2018              | -2.22%       | -5.13%        | 2.92%  | 12,000.00 | 104    | -94.8462        |
| 2019              | 37.41%       | 32.30%        | 5.11%  | 12,000.00 | 109    | -88.8165        |
| 2020 (COVID)      | 18.39%       | 15.69%        | 2.70%  | 12,000.00 | 89     | -88.9700        |
| 2021              | 23.71%       | 31.26%        | -7.55% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -13.67%      | -18.98%       | 5.30%  | 0.00      | 0      | —               |
| 2023              | 20.60%       | 26.71%        | -6.11% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `log_marketcap_rank >= 0.8`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 350  | 19.90% |
| Industrials            | 307  | 17.45% |
| Technology             | 283  | 16.09% |
| Healthcare             | 274  | 15.58% |
| Consumer Cyclical      | 194  | 11.03% |
| Communication Services | 123  | 6.99%  |
| Financial Services     | 89   | 5.06%  |
| Basic Materials        | 88   | 5.00%  |
| Energy                 | 30   | 1.71%  |
| Utilities              | 15   | 0.85%  |
| Real Estate            | 6    | 0.34%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 120  | 26     | 8      | Industrials        | 20.00%        |
| 2006 | 120  | 30     | 8      | Consumer Defensive | 20.00%        |
| 2007 | 118  | 30     | 9      | Consumer Defensive | 20.34%        |
| 2008 | 120  | 27     | 7      | Industrials        | 20.00%        |
| 2009 | 111  | 26     | 9      | Consumer Defensive | 21.62%        |
| 2010 | 120  | 25     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 109  | 26     | 9      | Consumer Defensive | 22.02%        |
| 2012 | 105  | 23     | 8      | Consumer Defensive | 22.86%        |
| 2013 | 114  | 23     | 8      | Consumer Defensive | 21.05%        |
| 2014 | 109  | 24     | 8      | Technology         | 22.02%        |
| 2015 | 106  | 20     | 7      | Consumer Defensive | 22.64%        |
| 2016 | 101  | 26     | 8      | Consumer Defensive | 23.76%        |
| 2017 | 104  | 20     | 8      | Technology         | 20.19%        |
| 2018 | 104  | 26     | 7      | Industrials        | 21.15%        |
| 2019 | 109  | 23     | 7      | Consumer Defensive | 22.02%        |
| 2020 | 89   | 28     | 8      | Consumer Defensive | 22.47%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | -2.49%         | -4.02%           | 41.67%  | 35.00%  | 2.50%         | 120  | -6.16%         | -1.83%           | 35.83%  | 51.67%  | 7.50%         |
| 2006     | 120  | 120  | -5.22%         | -5.32%           | 35.00%  | 26.67%  | 5.00%         | 120  | 1.31%          | 2.10%            | 62.50%  | 74.17%  | 5.00%         |
| 2007     | 118  | 118  | 8.92%          | 8.55%            | 74.58%  | 55.08%  | 0.00%         | 118  | 9.22%          | 7.38%            | 86.44%  | 42.37%  | 7.63%         |
| 2008     | 120  | 120  | 8.18%          | 9.92%            | 67.50%  | 82.50%  | 0.00%         | 120  | 5.30%          | 5.32%            | 81.67%  | 13.33%  | 2.50%         |
| 2009     | 111  | 111  | 1.10%          | 0.19%            | 52.25%  | 9.01%   | 1.80%         | 111  | 0.94%          | -0.06%           | 48.65%  | 2.70%   | 3.60%         |
| 2010     | 120  | 120  | 21.76%         | 18.15%           | 74.17%  | 12.50%  | 11.67%        | 120  | 7.61%          | 9.03%            | 80.00%  | 5.00%   | 20.00%        |
| 2011     | 109  | 109  | 10.67%         | 10.08%           | 67.89%  | 16.51%  | 1.83%         | 109  | 3.10%          | 4.45%            | 72.48%  | 4.59%   | 1.83%         |
| 2012     | 105  | 105  | -3.03%         | -2.45%           | 47.62%  | 18.10%  | 0.00%         | 105  | 4.97%          | 7.12%            | 74.29%  | 8.57%   | 1.90%         |
| 2013     | 114  | 114  | 1.16%          | 2.39%            | 55.26%  | 7.02%   | 0.00%         | 114  | 6.49%          | 7.07%            | 81.58%  | 7.89%   | 0.00%         |
| 2014     | 109  | 109  | 15.67%         | 17.17%           | 85.32%  | 9.17%   | 0.00%         | 109  | 3.94%          | 7.96%            | 64.22%  | 14.68%  | 2.75%         |
| 2015     | 106  | 106  | 6.78%          | 5.79%            | 65.09%  | 29.25%  | 0.00%         | 106  | 2.29%          | 5.86%            | 68.87%  | 18.87%  | 5.66%         |
| 2016     | 101  | 101  | 1.39%          | -0.97%           | 48.51%  | 7.92%   | 2.97%         | 101  | 1.12%          | 3.93%            | 62.38%  | 18.81%  | 2.97%         |
| 2017     | 104  | 104  | -2.71%         | -5.47%           | 41.35%  | 28.85%  | 7.69%         | 104  | 1.50%          | 0.14%            | 50.96%  | 18.27%  | 14.42%        |
| 2018     | 104  | 104  | 12.25%         | 9.36%            | 75.96%  | 17.31%  | 0.00%         | 104  | 3.71%          | 1.43%            | 51.92%  | 0.96%   | 8.65%         |
| 2019     | 109  | 109  | -1.40%         | -0.66%           | 48.62%  | 33.03%  | 0.00%         | 109  | -3.60%         | -3.86%           | 21.10%  | 6.42%   | 0.00%         |
| 2020     | 89   | 89   | -13.73%        | -23.20%          | 35.96%  | 22.47%  | 0.00%         | 89   | -0.69%         | -3.26%           | 35.96%  | 19.10%  | 10.11%        |
| all buys | 1759 | 1759 | 3.98%          | 3.36%            | 57.59%  | 26.21%  | 2.16%         | 1759 | 2.63%          | 3.36%            | 61.74%  | 19.78%  | 5.91%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -6.16%      | -0.83%            | -5.34%        | -0.69%       | -5.47%   | 51.67%    | 40.72%          | 40.61%     |
| 2006     | 120  | 1.31%       | -1.43%            | 2.75%         | -0.78%       | 2.09%    | 74.17%    | 72.36%          | 72.04%     |
| 2007     | 118  | 9.22%       | 0.95%             | 8.27%         | 1.39%        | 7.82%    | 42.37%    | 62.94%          | 62.72%     |
| 2008     | 120  | 5.30%       | 3.31%             | 1.99%         | 2.59%        | 2.71%    | 13.33%    | 32.31%          | 33.71%     |
| 2009     | 111  | 0.94%       | 1.91%             | -0.97%        | 0.59%        | 0.35%    | 2.70%     | 14.37%          | 12.72%     |
| 2010     | 120  | 7.61%       | -0.60%            | 8.21%         | -0.71%       | 8.32%    | 5.00%     | 13.72%          | 13.72%     |
| 2011     | 109  | 3.10%       | -2.10%            | 5.21%         | -2.25%       | 5.35%    | 4.59%     | 13.53%          | 13.09%     |
| 2012     | 105  | 4.97%       | -1.57%            | 6.54%         | -1.46%       | 6.43%    | 8.57%     | 15.30%          | 14.10%     |
| 2013     | 114  | 6.49%       | -3.14%            | 9.62%         | -3.00%       | 9.49%    | 7.89%     | 25.17%          | 24.62%     |
| 2014     | 109  | 3.94%       | -4.68%            | 8.62%         | -4.63%       | 8.57%    | 14.68%    | 29.21%          | 29.44%     |
| 2015     | 106  | 2.29%       | -4.95%            | 7.24%         | -4.49%       | 6.78%    | 18.87%    | 27.89%          | 26.64%     |
| 2016     | 101  | 1.12%       | -3.36%            | 4.48%         | -3.53%       | 4.65%    | 18.81%    | 22.38%          | 22.77%     |
| 2017     | 104  | 1.50%       | -6.17%            | 7.66%         | -5.44%       | 6.94%    | 18.27%    | 36.53%          | 35.60%     |
| 2018     | 104  | 3.71%       | -4.45%            | 8.16%         | -4.31%       | 8.02%    | 0.96%     | 21.01%          | 19.93%     |
| 2019     | 109  | -3.60%      | -4.83%            | 1.23%         | -3.32%       | -0.28%   | 6.42%     | 23.22%          | 18.72%     |
| 2020     | 89   | -0.69%      | -3.25%            | 2.56%         | -2.96%       | 2.27%    | 19.10%    | 26.86%          | 25.09%     |
| all buys | 1759 | 2.63%       | -2.06%            | 4.69%         | -1.95%       | 4.59%    | 19.78%    | 30.68%          | 29.63%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -2.49%      | 4.07%             | -6.56%        | 4.05%        | -6.54%   | 35.00%    | 30.83%          | 30.93%     |
| 2006     | 120  | -5.22%      | 2.71%             | -7.93%        | 2.56%        | -7.78%   | 26.67%    | 24.96%          | 23.52%     |
| 2007     | 118  | 8.92%       | 1.79%             | 7.14%         | 3.31%        | 5.61%    | 55.08%    | 67.56%          | 65.39%     |
| 2008     | 120  | 8.18%       | 3.79%             | 4.39%         | 3.98%        | 4.20%    | 82.50%    | 75.51%          | 75.96%     |
| 2009     | 111  | 1.10%       | 13.24%            | -12.15%       | 7.17%        | -6.07%   | 9.01%     | 14.77%          | 14.58%     |
| 2010     | 120  | 21.76%      | 6.24%             | 15.51%        | 6.09%        | 15.67%   | 12.50%    | 21.59%          | 21.35%     |
| 2011     | 109  | 10.67%      | -3.01%            | 13.68%        | -2.94%       | 13.61%   | 16.51%    | 37.92%          | 36.19%     |
| 2012     | 105  | -3.03%      | 3.29%             | -6.32%        | 0.86%        | -3.89%   | 18.10%    | 16.77%          | 16.67%     |
| 2013     | 114  | 1.16%       | 1.47%             | -0.31%        | 1.26%        | -0.10%   | 7.02%     | 16.64%          | 16.09%     |
| 2014     | 109  | 15.67%      | -1.39%            | 17.06%        | -2.64%       | 18.31%   | 9.17%     | 35.17%          | 36.81%     |
| 2015     | 106  | 6.78%       | -3.49%            | 10.27%        | -2.94%       | 9.71%    | 29.25%    | 47.40%          | 46.80%     |
| 2016     | 101  | 1.39%       | -1.28%            | 2.67%         | -1.32%       | 2.71%    | 7.92%     | 23.28%          | 22.87%     |
| 2017     | 104  | -2.71%      | -1.28%            | -1.44%        | -1.37%       | -1.34%   | 28.85%    | 31.83%          | 31.23%     |
| 2018     | 104  | 12.25%      | -0.59%            | 12.84%        | -0.19%       | 12.44%   | 17.31%    | 40.11%          | 38.90%     |
| 2019     | 109  | -1.40%      | -5.33%            | 3.93%         | -2.66%       | 1.26%    | 33.03%    | 44.32%          | 40.72%     |
| 2020     | 89   | -13.73%     | 7.92%             | -21.65%       | 4.45%        | -18.19%  | 22.47%    | 15.15%          | 14.28%     |
| all buys | 1759 | 3.98%       | 1.90%             | 2.09%         | 1.31%        | 2.67%    | 26.21%    | 34.41%          | 33.75%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 104
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 794.5 (min 726)
- mean with a tradable quote: 780.0 (min 715)
- forced delisting liquidations: 44 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 5 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `0aeea637e84c41d9`, train run `f259c702a6a6`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_v141_f259c702a6a6`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largecap_v141_2f3b4fce9778c721_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largecap_v141_2f3b4fce9778c721_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largecap_v141_2f3b4fce9778c721_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_largecap_v141_2f3b4fce9778c721_equity.png`
