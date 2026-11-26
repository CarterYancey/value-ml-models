# Portfolio backtest — bt_nonloser_forestC_top10_cap2_rankfloor_v151

- run `21a026abb6f7`, git `5ffe77dda39e88854216eff3cbbae20f86a0bd76`, backtest config `a7158119062b9d6f`
- dataset `1.5.1` (sha256 `225174868902e363fa8e78a42edfd661fb67fdaaac0fa5b03d073524d2776682`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | cagr   | max_drawdown | twr   | costs_paid |
| --------- | ---------- | ----------- | ---------- | ------ | ------------ | ----- | ---------- |
| strategy  | 192,000.00 | 602,078.54  | 410,078.54 | 9.97%  | -48.33%      | 9.38% | 1,505.88   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62% | -52.87%      | 9.58% | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 10.13%       | 7.09%         | 3.04%   | 12,000.00 | 119    | 0.7331          |
| 2006              | 20.66%       | 13.61%        | 7.05%   | 12,000.00 | 111    | 0.7611          |
| 2007              | -10.03%      | 4.40%         | -14.43% | 12,000.00 | 118    | 0.8183          |
| 2008 (GFC)        | -21.71%      | -34.30%       | 12.59%  | 12,000.00 | 118    | 0.8351          |
| 2009 (GFC)        | 25.11%       | 24.74%        | 0.36%   | 12,000.00 | 120    | 0.8035          |
| 2010              | 27.08%       | 14.30%        | 12.79%  | 12,000.00 | 120    | 0.7434          |
| 2011              | 14.39%       | 2.46%         | 11.93%  | 12,000.00 | 117    | 0.6784          |
| 2012              | 13.68%       | 17.09%        | -3.41%  | 12,000.00 | 120    | 0.6424          |
| 2013              | 12.51%       | 27.75%        | -15.24% | 12,000.00 | 120    | 0.6609          |
| 2014              | 24.84%       | 14.49%        | 10.35%  | 12,000.00 | 114    | 0.6841          |
| 2015              | -0.19%       | -0.11%        | -0.08%  | 12,000.00 | 116    | 0.6958          |
| 2016              | 17.99%       | 14.45%        | 3.53%   | 12,000.00 | 111    | 0.7232          |
| 2017              | 11.38%       | 21.63%        | -10.25% | 12,000.00 | 116    | 0.7303          |
| 2018              | -3.43%       | -5.13%        | 1.70%   | 12,000.00 | 116    | 0.7249          |
| 2019              | 29.29%       | 32.30%        | -3.01%  | 12,000.00 | 107    | 0.7302          |
| 2020 (COVID)      | 0.40%        | 15.69%        | -15.29% | 12,000.00 | 107    | 0.7337          |
| 2021              | 26.09%       | 31.26%        | -5.16%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -6.38%       | -18.98%       | 12.60%  | 0.00      | 0      | —               |
| 2023              | 3.92%        | 26.71%        | -22.79% | 0.00      | 0      | —               |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 3 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
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
| Utilities              | 354  | 19.14% |
| Real Estate            | 280  | 15.14% |
| Consumer Defensive     | 252  | 13.62% |
| Industrials            | 223  | 12.05% |
| Energy                 | 213  | 11.51% |
| Financial Services     | 145  | 7.84%  |
| Healthcare             | 135  | 7.30%  |
| Consumer Cyclical      | 88   | 4.76%  |
| Communication Services | 87   | 4.70%  |
| Technology             | 59   | 3.19%  |
| Basic Materials        | 14   | 0.76%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2005 | 119  | 25     | 9      | Real Estate   | 20.17%        |
| 2006 | 111  | 19     | 7      | Real Estate   | 21.62%        |
| 2007 | 118  | 21     | 9      | Real Estate   | 20.34%        |
| 2008 | 118  | 20     | 6      | Real Estate   | 20.34%        |
| 2009 | 120  | 24     | 7      | Utilities     | 20.00%        |
| 2010 | 120  | 23     | 8      | Utilities     | 20.00%        |
| 2011 | 117  | 26     | 8      | Energy        | 20.51%        |
| 2012 | 120  | 26     | 8      | Energy        | 20.00%        |
| 2013 | 120  | 26     | 9      | Utilities     | 20.00%        |
| 2014 | 114  | 25     | 8      | Utilities     | 21.05%        |
| 2015 | 116  | 28     | 8      | Utilities     | 20.69%        |
| 2016 | 111  | 26     | 9      | Utilities     | 21.62%        |
| 2017 | 116  | 26     | 8      | Utilities     | 20.69%        |
| 2018 | 116  | 24     | 9      | Utilities     | 20.69%        |
| 2019 | 107  | 21     | 9      | Utilities     | 22.43%        |
| 2020 | 107  | 25     | 9      | Utilities     | 19.63%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 119  | 119  | 3.63%          | 0.84%            | 51.26%  | 27.73%  | 0.84%         | 119  | -2.19%         | -0.68%           | 47.90%  | 37.82%  | 17.65%        |
| 2006     | 111  | 111  | 0.79%          | 2.87%            | 54.95%  | 15.32%  | 21.62%        | 111  | -1.91%         | -0.62%           | 45.05%  | 78.38%  | 26.13%        |
| 2007     | 118  | 118  | 0.43%          | 1.60%            | 54.24%  | 72.03%  | 8.47%         | 118  | 3.59%          | 2.86%            | 59.32%  | 51.69%  | 8.47%         |
| 2008     | 118  | 118  | 9.33%          | 14.24%           | 74.58%  | 72.88%  | 4.24%         | 118  | 6.10%          | 8.26%            | 75.42%  | 18.64%  | 10.17%        |
| 2009     | 120  | 120  | 5.67%          | 3.79%            | 64.17%  | 1.67%   | 2.50%         | 120  | 5.92%          | 5.61%            | 75.00%  | 0.00%   | 2.50%         |
| 2010     | 120  | 120  | 7.30%          | 4.46%            | 70.83%  | 4.17%   | 0.00%         | 120  | 2.55%          | 2.97%            | 64.17%  | 6.67%   | 4.17%         |
| 2011     | 117  | 117  | 6.16%          | 6.47%            | 64.10%  | 19.66%  | 0.00%         | 117  | -2.65%         | -2.83%           | 39.32%  | 7.69%   | 0.00%         |
| 2012     | 120  | 120  | -0.16%         | -0.46%           | 46.67%  | 8.33%   | 0.00%         | 120  | -1.81%         | -2.54%           | 40.83%  | 2.50%   | 0.00%         |
| 2013     | 120  | 120  | -8.05%         | -9.31%           | 34.17%  | 18.33%  | 5.00%         | 120  | 1.54%          | 1.38%            | 57.50%  | 1.67%   | 15.83%        |
| 2014     | 114  | 114  | 2.58%          | 3.46%            | 56.14%  | 26.32%  | 0.00%         | 114  | 2.52%          | 2.08%            | 60.53%  | 7.89%   | 5.26%         |
| 2015     | 116  | 116  | 9.00%          | 8.44%            | 71.55%  | 22.41%  | 6.03%         | 116  | -1.86%         | 0.24%            | 50.86%  | 14.66%  | 6.03%         |
| 2016     | 111  | 111  | -3.60%         | -4.76%           | 39.64%  | 11.71%  | 3.60%         | 111  | -0.40%         | -0.14%           | 49.55%  | 12.61%  | 3.60%         |
| 2017     | 116  | 116  | -6.26%         | -7.15%           | 31.90%  | 26.72%  | 0.00%         | 116  | -1.97%         | -0.54%           | 43.97%  | 13.79%  | 2.59%         |
| 2018     | 116  | 116  | 15.08%         | 14.04%           | 87.07%  | 6.90%   | 9.48%         | 116  | -2.92%         | -0.71%           | 41.38%  | 9.48%   | 9.48%         |
| 2019     | 107  | 107  | -12.91%        | -10.73%          | 20.56%  | 43.93%  | 0.00%         | 107  | -7.10%         | -5.99%           | 23.36%  | 26.17%  | 0.00%         |
| 2020     | 107  | 107  | -14.61%        | -21.18%          | 12.15%  | 23.36%  | 0.93%         | 107  | -2.39%         | -1.10%           | 41.12%  | 10.28%  | 6.54%         |
| all buys | 1850 | 1850 | 1.07%          | 1.23%            | 52.54%  | 25.03%  | 3.89%         | 1850 | -0.12%         | 0.27%            | 51.24%  | 18.54%  | 7.41%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 119  | -2.19%      | -7.65%            | 5.46%         | -2.49%       | 0.30%    | 37.82%    | 51.93%          | 44.30%     |
| 2006     | 111  | -1.91%      | -9.20%            | 7.29%         | -3.46%       | 1.55%    | 78.38%    | 77.47%          | 73.05%     |
| 2007     | 118  | 3.59%       | -6.61%            | 10.20%        | 0.09%        | 3.50%    | 51.69%    | 69.62%          | 63.46%     |
| 2008     | 118  | 6.10%       | -1.41%            | 7.51%         | 0.36%        | 5.74%    | 18.64%    | 42.57%          | 37.77%     |
| 2009     | 120  | 5.92%       | -0.01%            | 5.93%         | 1.05%        | 4.86%    | 0.00%     | 24.96%          | 15.78%     |
| 2010     | 120  | 2.55%       | -5.91%            | 8.46%         | -1.92%       | 4.47%    | 6.67%     | 27.42%          | 16.42%     |
| 2011     | 117  | -2.65%      | -7.68%            | 5.03%         | -2.29%       | -0.36%   | 7.69%     | 27.47%          | 15.15%     |
| 2012     | 120  | -1.81%      | -7.07%            | 5.26%         | -2.57%       | 0.75%    | 2.50%     | 27.79%          | 16.67%     |
| 2013     | 120  | 1.54%       | -10.38%           | 11.92%        | -3.87%       | 5.41%    | 1.67%     | 39.52%          | 25.21%     |
| 2014     | 114  | 2.52%       | -11.40%           | 13.91%        | -3.76%       | 6.28%    | 7.89%     | 41.08%          | 25.35%     |
| 2015     | 116  | -1.86%      | -10.39%           | 8.53%         | -4.46%       | 2.60%    | 14.66%    | 37.61%          | 26.25%     |
| 2016     | 111  | -0.40%      | -9.18%            | 8.78%         | -3.14%       | 2.73%    | 12.61%    | 35.01%          | 22.62%     |
| 2017     | 116  | -1.97%      | -14.54%           | 12.57%        | -4.93%       | 2.96%    | 13.79%    | 50.60%          | 33.02%     |
| 2018     | 116  | -2.92%      | -11.65%           | 8.72%         | -4.87%       | 1.95%    | 9.48%     | 36.68%          | 21.99%     |
| 2019     | 107  | -7.10%      | -11.93%           | 4.83%         | -5.24%       | -1.86%   | 26.17%    | 39.82%          | 24.48%     |
| 2020     | 107  | -2.39%      | -8.77%            | 6.38%         | -3.00%       | 0.61%    | 10.28%    | 39.44%          | 26.41%     |
| all buys | 1850 | -0.12%      | -8.20%            | 8.08%         | -2.75%       | 2.63%    | 18.54%    | 42.54%          | 30.41%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 119  | 3.63%       | 5.25%             | -1.62%        | 4.96%        | -1.33%   | 27.73%    | 38.73%          | 32.57%     |
| 2006     | 111  | 0.79%       | -0.15%            | 0.94%         | 1.61%        | -0.82%   | 15.32%    | 38.08%          | 28.78%     |
| 2007     | 118  | 0.43%       | -7.00%            | 7.43%         | 0.56%        | -0.13%   | 72.03%    | 73.36%          | 67.86%     |
| 2008     | 118  | 9.33%       | 4.28%             | 5.05%         | 3.80%        | 5.53%    | 72.88%    | 73.80%          | 75.07%     |
| 2009     | 120  | 5.67%       | 31.66%            | -25.99%       | 14.75%       | -9.08%   | 1.67%     | 23.03%          | 17.48%     |
| 2010     | 120  | 7.30%       | 5.09%             | 2.21%         | 5.36%        | 1.94%    | 4.17%     | 33.28%          | 23.78%     |
| 2011     | 117  | 6.16%       | -7.55%            | 13.70%        | -3.45%       | 9.60%    | 19.66%    | 48.29%          | 38.65%     |
| 2012     | 120  | -0.16%      | 3.72%             | -3.88%        | 2.29%        | -2.44%   | 8.33%     | 27.49%          | 18.17%     |
| 2013     | 120  | -8.05%      | 1.72%             | -9.77%        | 1.68%        | -9.73%   | 18.33%    | 28.73%          | 15.62%     |
| 2014     | 114  | 2.58%       | -7.02%            | 9.60%         | -0.61%       | 3.20%    | 26.32%    | 47.37%          | 32.77%     |
| 2015     | 116  | 9.00%       | -9.45%            | 18.45%        | -3.26%       | 12.27%   | 22.41%    | 56.17%          | 47.20%     |
| 2016     | 111  | -3.60%      | 2.15%             | -5.75%        | -0.57%       | -3.04%   | 11.71%    | 30.43%          | 22.85%     |
| 2017     | 116  | -6.26%      | -1.39%            | -4.87%        | -1.63%       | -4.62%   | 26.72%    | 40.54%          | 31.13%     |
| 2018     | 116  | 15.08%      | -9.90%            | 24.99%        | -1.58%       | 16.66%   | 6.90%     | 53.76%          | 41.09%     |
| 2019     | 107  | -12.91%     | -9.73%            | -3.18%        | -6.19%       | -6.72%   | 43.93%    | 55.97%          | 45.23%     |
| 2020     | 107  | -14.61%     | 33.15%            | -47.76%       | 8.37%        | -22.98%  | 23.36%    | 22.31%          | 14.76%     |
| all buys | 1850 | 1.07%       | 2.26%             | -1.19%        | 1.69%        | -0.62%   | 25.03%    | 43.57%          | 34.60%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 60
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3220.5 (min 2912)
- mean with a tradable quote: 3143.5 (min 2860)
- forced delisting liquidations: 54 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.5.1`: 1 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.5.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v151` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `18622748bbbb3719`, train run `3ae9c4fdd685`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_v151_3ae9c4fdd685`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_forestC_top10_cap2_rankfloor_v151_a7158119062b9d6f_equity.csv`
- trades: `reports/backtest/bt_nonloser_forestC_top10_cap2_rankfloor_v151_a7158119062b9d6f_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_forestC_top10_cap2_rankfloor_v151_a7158119062b9d6f_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_forestC_top10_cap2_rankfloor_v151_a7158119062b9d6f_equity.png`
