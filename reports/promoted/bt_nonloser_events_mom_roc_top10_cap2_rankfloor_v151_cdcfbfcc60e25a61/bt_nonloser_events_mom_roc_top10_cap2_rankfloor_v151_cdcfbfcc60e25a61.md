# Portfolio backtest — bt_nonloser_events_mom_roc_top10_cap2_rankfloor_v151

- run `8d2e7a4e36d2`, git `5ffe77dda39e88854216eff3cbbae20f86a0bd76`, backtest config `cdcfbfcc60e25a61`
- dataset `1.5.1` (sha256 `225174868902e363fa8e78a42edfd661fb67fdaaac0fa5b03d073524d2776682`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | cagr   | max_drawdown | twr    | costs_paid |
| --------- | ---------- | ----------- | ---------- | ------ | ------------ | ------ | ---------- |
| strategy  | 192,000.00 | 851,928.13  | 659,928.13 | 12.89% | -40.17%      | 11.24% | 1,279.78   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62% | -52.87%      | 9.58%  | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 3.37%        | 7.09%         | -3.71% | 12,000.00 | 108    | -360.1821       |
| 2006              | 8.07%        | 13.61%        | -5.54% | 12,000.00 | 120    | -379.6639       |
| 2007              | -0.05%       | 4.40%         | -4.45% | 12,000.00 | 116    | -335.4943       |
| 2008 (GFC)        | -22.01%      | -34.30%       | 12.29% | 12,000.00 | 120    | -306.7194       |
| 2009 (GFC)        | 29.20%       | 24.74%        | 4.46%  | 12,000.00 | 115    | -210.2696       |
| 2010              | 28.45%       | 14.30%        | 14.15% | 12,000.00 | 120    | -375.6361       |
| 2011              | 8.66%        | 2.46%         | 6.21%  | 12,000.00 | 120    | -269.7528       |
| 2012              | 15.39%       | 17.09%        | -1.70% | 12,000.00 | 118    | -197.4661       |
| 2013              | 39.37%       | 27.75%        | 11.62% | 12,000.00 | 120    | -246.6528       |
| 2014              | 7.32%        | 14.49%        | -7.17% | 12,000.00 | 110    | -278.9000       |
| 2015              | 5.07%        | -0.11%        | 5.18%  | 12,000.00 | 106    | -202.9874       |
| 2016              | 13.64%       | 14.45%        | -0.82% | 12,000.00 | 103    | -185.6019       |
| 2017              | 21.20%       | 21.63%        | -0.44% | 12,000.00 | 106    | -289.6195       |
| 2018              | -4.48%       | -5.13%        | 0.65%  | 12,000.00 | 96     | -254.8229       |
| 2019              | 36.85%       | 32.30%        | 4.55%  | 12,000.00 | 99     | -216.6128       |
| 2020 (COVID)      | 18.60%       | 15.69%        | 2.92%  | 12,000.00 | 83     | -201.3775       |
| 2021              | 22.63%       | 31.26%        | -8.63% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -15.99%      | -18.98%       | 2.98%  | 0.00      | 0      | —               |
| 2023              | 20.55%       | 26.71%        | -6.16% | 0.00      | 0      | —               |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

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
| Consumer Cyclical      | 283  | 16.08% |
| Industrials            | 277  | 15.74% |
| Consumer Defensive     | 273  | 15.51% |
| Technology             | 258  | 14.66% |
| Healthcare             | 256  | 14.55% |
| Communication Services | 127  | 7.22%  |
| Basic Materials        | 101  | 5.74%  |
| Energy                 | 93   | 5.28%  |
| Financial Services     | 70   | 3.98%  |
| Real Estate            | 13   | 0.74%  |
| Utilities              | 9    | 0.51%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 25     | 10     | Industrials            | 22.22%        |
| 2006 | 120  | 29     | 9      | Healthcare             | 20.00%        |
| 2007 | 116  | 31     | 9      | Consumer Defensive     | 18.10%        |
| 2008 | 120  | 31     | 8      | Healthcare             | 20.00%        |
| 2009 | 115  | 32     | 10     | Healthcare             | 20.87%        |
| 2010 | 120  | 30     | 8      | Consumer Cyclical      | 20.00%        |
| 2011 | 120  | 32     | 8      | Consumer Cyclical      | 18.33%        |
| 2012 | 118  | 30     | 10     | Consumer Cyclical      | 20.34%        |
| 2013 | 120  | 25     | 8      | Healthcare             | 20.00%        |
| 2014 | 110  | 26     | 9      | Communication Services | 21.82%        |
| 2015 | 106  | 25     | 9      | Consumer Defensive     | 19.81%        |
| 2016 | 103  | 26     | 8      | Consumer Defensive     | 23.30%        |
| 2017 | 106  | 27     | 9      | Consumer Cyclical      | 21.70%        |
| 2018 | 96   | 24     | 8      | Consumer Cyclical      | 25.00%        |
| 2019 | 99   | 27     | 7      | Consumer Defensive     | 23.23%        |
| 2020 | 83   | 27     | 8      | Consumer Defensive     | 22.89%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -7.15%         | -7.08%           | 31.48%  | 40.74%  | 2.78%         | 108  | -4.53%         | 0.32%            | 53.70%  | 40.74%  | 16.67%        |
| 2006     | 120  | 120  | -12.89%        | -12.64%          | 25.00%  | 46.67%  | 5.00%         | 120  | 0.73%          | 1.61%            | 57.50%  | 75.83%  | 5.00%         |
| 2007     | 116  | 116  | 5.41%          | 5.97%            | 65.52%  | 56.90%  | 1.72%         | 116  | 7.39%          | 7.74%            | 77.59%  | 42.24%  | 12.07%        |
| 2008     | 120  | 120  | 10.06%         | 11.37%           | 65.00%  | 76.67%  | 0.83%         | 120  | 7.81%          | 7.73%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 115  | 115  | 5.58%          | 6.19%            | 57.39%  | 13.04%  | 6.96%         | 115  | -0.76%         | -0.35%           | 46.09%  | 8.70%   | 11.30%        |
| 2010     | 120  | 120  | 25.33%         | 25.06%           | 83.33%  | 2.50%   | 0.00%         | 120  | 8.19%          | 9.29%            | 76.67%  | 6.67%   | 5.00%         |
| 2011     | 120  | 120  | 7.49%          | 9.54%            | 60.00%  | 25.83%  | 2.50%         | 120  | 3.23%          | 4.09%            | 62.50%  | 12.50%  | 5.00%         |
| 2012     | 118  | 118  | 8.66%          | 6.55%            | 61.86%  | 11.02%  | 0.00%         | 118  | 0.54%          | 0.62%            | 51.69%  | 16.95%  | 3.39%         |
| 2013     | 120  | 120  | -3.42%         | -3.42%           | 39.17%  | 16.67%  | 5.00%         | 120  | 0.18%          | 1.62%            | 58.33%  | 17.50%  | 5.00%         |
| 2014     | 110  | 110  | 8.49%          | 13.57%           | 64.55%  | 20.00%  | 0.00%         | 110  | 3.31%          | 3.39%            | 58.18%  | 14.55%  | 5.45%         |
| 2015     | 106  | 106  | 3.51%          | 1.98%            | 54.72%  | 35.85%  | 0.00%         | 106  | 0.86%          | 4.34%            | 63.21%  | 17.92%  | 2.83%         |
| 2016     | 103  | 103  | -0.04%         | -2.70%           | 44.66%  | 11.65%  | 2.91%         | 103  | 2.91%          | 4.87%            | 66.99%  | 12.62%  | 5.83%         |
| 2017     | 106  | 106  | 0.16%          | -3.39%           | 44.34%  | 27.36%  | 4.72%         | 106  | 2.98%          | 0.63%            | 53.77%  | 18.87%  | 16.98%        |
| 2018     | 96   | 96   | 9.25%          | 6.67%            | 71.88%  | 20.83%  | 0.00%         | 96   | 4.72%          | 0.08%            | 51.04%  | 3.12%   | 9.38%         |
| 2019     | 99   | 99   | -3.84%         | -3.99%           | 42.42%  | 35.35%  | 0.00%         | 99   | -5.91%         | -6.15%           | 16.16%  | 13.13%  | 0.00%         |
| 2020     | 83   | 83   | -18.14%        | -21.24%          | 28.92%  | 30.12%  | 0.00%         | 83   | -2.93%         | -3.03%           | 37.35%  | 24.10%  | 10.84%        |
| all buys | 1760 | 1760 | 2.86%          | 1.76%            | 53.01%  | 29.60%  | 2.10%         | 1760 | 1.97%          | 2.41%            | 58.30%  | 21.19%  | 7.27%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -4.53%      | -7.65%            | 3.12%         | -3.03%       | -1.50%   | 40.74%    | 51.93%          | 45.06%     |
| 2006     | 120  | 0.73%       | -9.20%            | 9.93%         | -2.58%       | 3.31%    | 75.83%    | 77.47%          | 73.30%     |
| 2007     | 116  | 7.39%       | -6.61%            | 14.00%        | -0.06%       | 7.46%    | 42.24%    | 69.62%          | 63.65%     |
| 2008     | 120  | 7.81%       | -1.41%            | 9.22%         | 2.03%        | 5.78%    | 9.17%     | 42.57%          | 35.23%     |
| 2009     | 115  | -0.76%      | -0.01%            | -0.75%        | 1.79%        | -2.55%   | 8.70%     | 24.96%          | 15.61%     |
| 2010     | 120  | 8.19%       | -5.91%            | 14.10%        | -1.75%       | 9.94%    | 6.67%     | 27.42%          | 17.25%     |
| 2011     | 120  | 3.23%       | -7.68%            | 10.91%        | -4.71%       | 7.94%    | 12.50%    | 27.47%          | 19.13%     |
| 2012     | 118  | 0.54%       | -7.07%            | 7.61%         | -4.81%       | 5.35%    | 16.95%    | 27.79%          | 22.47%     |
| 2013     | 120  | 0.18%       | -10.38%           | 10.56%        | -6.00%       | 6.18%    | 17.50%    | 39.52%          | 30.30%     |
| 2014     | 110  | 3.31%       | -11.40%           | 14.71%        | -5.69%       | 9.00%    | 14.55%    | 41.08%          | 30.57%     |
| 2015     | 106  | 0.86%       | -10.39%           | 11.25%        | -4.54%       | 5.40%    | 17.92%    | 37.61%          | 26.50%     |
| 2016     | 103  | 2.91%       | -9.18%            | 12.09%        | -3.97%       | 6.88%    | 12.62%    | 35.01%          | 24.01%     |
| 2017     | 106  | 2.98%       | -14.54%           | 17.52%        | -7.30%       | 10.28%   | 18.87%    | 50.60%          | 38.98%     |
| 2018     | 96   | 4.72%       | -11.65%           | 16.36%        | -5.00%       | 9.71%    | 3.12%     | 36.68%          | 21.62%     |
| 2019     | 99   | -5.91%      | -11.93%           | 6.02%         | -5.00%       | -0.91%   | 13.13%    | 39.82%          | 23.48%     |
| 2020     | 83   | -2.93%      | -8.77%            | 5.84%         | -2.82%       | -0.11%   | 24.10%    | 39.44%          | 24.85%     |
| all buys | 1760 | 1.97%       | -8.20%            | 10.17%        | -3.27%       | 5.24%    | 21.19%    | 42.54%          | 32.37%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -7.15%      | 5.25%             | -12.40%       | 5.27%        | -12.42%  | 40.74%    | 38.73%          | 33.08%     |
| 2006     | 120  | -12.89%     | -0.15%            | -12.73%       | 1.48%        | -14.36%  | 46.67%    | 38.08%          | 27.55%     |
| 2007     | 116  | 5.41%       | -7.00%            | 12.41%        | 1.32%        | 4.09%    | 56.90%    | 73.36%          | 66.94%     |
| 2008     | 120  | 10.06%      | 4.28%             | 5.79%         | 4.15%        | 5.92%    | 76.67%    | 73.80%          | 75.76%     |
| 2009     | 115  | 5.58%       | 31.66%            | -26.08%       | 15.24%       | -9.66%   | 13.04%    | 23.03%          | 16.16%     |
| 2010     | 120  | 25.33%      | 5.09%             | 20.24%        | 6.63%        | 18.69%   | 2.50%     | 33.28%          | 24.43%     |
| 2011     | 120  | 7.49%       | -7.55%            | 15.04%        | -5.26%       | 12.75%   | 25.83%    | 48.29%          | 42.70%     |
| 2012     | 118  | 8.66%       | 3.72%             | 4.94%         | 4.21%        | 4.45%    | 11.02%    | 27.49%          | 22.46%     |
| 2013     | 120  | -3.42%      | 1.72%             | -5.13%        | 1.07%        | -4.48%   | 16.67%    | 28.73%          | 20.34%     |
| 2014     | 110  | 8.49%       | -7.02%            | 15.51%        | -3.16%       | 11.66%   | 20.00%    | 47.37%          | 37.84%     |
| 2015     | 106  | 3.51%       | -9.45%            | 12.96%        | -3.12%       | 6.63%    | 35.85%    | 56.17%          | 46.81%     |
| 2016     | 103  | -0.04%      | 2.15%             | -2.19%        | -0.97%       | 0.93%    | 11.65%    | 30.43%          | 23.28%     |
| 2017     | 106  | 0.16%       | -1.39%            | 1.55%         | -1.96%       | 2.12%    | 27.36%    | 40.54%          | 33.21%     |
| 2018     | 96   | 9.25%       | -9.90%            | 19.15%        | -1.31%       | 10.56%   | 20.83%    | 53.76%          | 40.59%     |
| 2019     | 99   | -3.84%      | -9.73%            | 5.90%         | -5.29%       | 1.45%    | 35.35%    | 55.97%          | 43.46%     |
| 2020     | 83   | -18.14%     | 33.15%            | -51.29%       | 5.93%        | -24.07%  | 30.12%    | 22.31%          | 13.98%     |
| all buys | 1760 | 2.86%       | 2.26%             | 0.60%         | 1.59%        | 1.27%    | 29.60%    | 43.57%          | 35.88%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 82
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

- backtest configurations tried against dataset `1.5.1`: 4 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.5.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_events_v151` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `e77bbdd029222519`, train run `ff4822397404`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_events_v151_ff4822397404`)
- `factor_mom_12_2_3y_v151` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `5a558bd472f35c81`, train run `14024723ce51`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_v151_14024723ce51`)
- `factor_roc_greenblatt_3y_v151` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `ef0ded7417428fd3`, train run `05dc2c455efc`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_v151_05dc2c455efc`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_events_mom_roc_top10_cap2_rankfloor_v151_cdcfbfcc60e25a61_equity.csv`
- trades: `reports/backtest/bt_nonloser_events_mom_roc_top10_cap2_rankfloor_v151_cdcfbfcc60e25a61_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_events_mom_roc_top10_cap2_rankfloor_v151_cdcfbfcc60e25a61_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_events_mom_roc_top10_cap2_rankfloor_v151_cdcfbfcc60e25a61_equity.png`
