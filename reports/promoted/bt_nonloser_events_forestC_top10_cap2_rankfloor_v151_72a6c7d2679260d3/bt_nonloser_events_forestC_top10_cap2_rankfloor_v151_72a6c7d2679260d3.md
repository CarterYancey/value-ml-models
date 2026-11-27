# Portfolio backtest — bt_nonloser_events_forestC_top10_cap2_rankfloor_v151

- run `ce2d41fde824`, git `5ffe77dda39e88854216eff3cbbae20f86a0bd76`, backtest config `72a6c7d2679260d3`
- dataset `1.5.1` (sha256 `225174868902e363fa8e78a42edfd661fb67fdaaac0fa5b03d073524d2776682`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | cagr   | max_drawdown | twr   | costs_paid |
| --------- | ---------- | ----------- | ---------- | ------ | ------------ | ----- | ---------- |
| strategy  | 192,000.00 | 571,211.28  | 379,211.28 | 9.52%  | -45.80%      | 9.17% | 1,430.67   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62% | -52.87%      | 9.58% | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 9.37%        | 7.09%         | 2.28%   | 12,000.00 | 120    | 0.7349          |
| 2006              | 18.27%       | 13.61%        | 4.66%   | 12,000.00 | 111    | 0.7685          |
| 2007              | -7.83%       | 4.40%         | -12.23% | 12,000.00 | 114    | 0.8156          |
| 2008 (GFC)        | -19.62%      | -34.30%       | 14.68%  | 12,000.00 | 115    | 0.8411          |
| 2009 (GFC)        | 25.98%       | 24.74%        | 1.24%   | 12,000.00 | 120    | 0.8075          |
| 2010              | 26.43%       | 14.30%        | 12.14%  | 12,000.00 | 120    | 0.7191          |
| 2011              | 10.95%       | 2.46%         | 8.49%   | 12,000.00 | 120    | 0.6752          |
| 2012              | 15.00%       | 17.09%        | -2.10%  | 12,000.00 | 120    | 0.6551          |
| 2013              | 18.35%       | 27.75%        | -9.40%  | 12,000.00 | 120    | 0.6659          |
| 2014              | 24.74%       | 14.49%        | 10.24%  | 12,000.00 | 120    | 0.6701          |
| 2015              | 1.31%        | -0.11%        | 1.42%   | 12,000.00 | 119    | 0.6805          |
| 2016              | 15.30%       | 14.45%        | 0.85%   | 12,000.00 | 114    | 0.7080          |
| 2017              | 9.10%        | 21.63%        | -12.54% | 12,000.00 | 118    | 0.7212          |
| 2018              | -4.00%       | -5.13%        | 1.13%   | 12,000.00 | 116    | 0.7264          |
| 2019              | 27.27%       | 32.30%        | -5.03%  | 12,000.00 | 102    | 0.7298          |
| 2020 (COVID)      | -1.03%       | 15.69%        | -16.71% | 12,000.00 | 109    | 0.7356          |
| 2021              | 24.95%       | 31.26%        | -6.31%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -10.24%      | -18.98%       | 8.74%   | 0.00      | 0      | —               |
| 2023              | 6.42%        | 26.71%        | -20.28% | 0.00      | 0      | —               |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

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
| Utilities              | 348  | 18.73% |
| Industrials            | 276  | 14.85% |
| Real Estate            | 232  | 12.49% |
| Consumer Defensive     | 215  | 11.57% |
| Healthcare             | 164  | 8.83%  |
| Energy                 | 156  | 8.40%  |
| Communication Services | 141  | 7.59%  |
| Consumer Cyclical      | 125  | 6.73%  |
| Financial Services     | 121  | 6.51%  |
| Technology             | 63   | 3.39%  |
| Basic Materials        | 17   | 0.91%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 120  | 25     | 8      | Financial Services | 20.00%        |
| 2006 | 111  | 19     | 8      | Real Estate        | 21.62%        |
| 2007 | 114  | 18     | 9      | Real Estate        | 21.05%        |
| 2008 | 115  | 19     | 6      | Real Estate        | 20.87%        |
| 2009 | 120  | 23     | 7      | Utilities          | 20.00%        |
| 2010 | 120  | 19     | 8      | Utilities          | 20.00%        |
| 2011 | 120  | 20     | 7      | Utilities          | 20.00%        |
| 2012 | 120  | 19     | 8      | Utilities          | 20.00%        |
| 2013 | 120  | 13     | 8      | Utilities          | 20.00%        |
| 2014 | 120  | 18     | 8      | Utilities          | 20.00%        |
| 2015 | 119  | 23     | 9      | Industrials        | 20.17%        |
| 2016 | 114  | 27     | 8      | Utilities          | 21.05%        |
| 2017 | 118  | 25     | 7      | Utilities          | 20.34%        |
| 2018 | 116  | 24     | 9      | Industrials        | 20.69%        |
| 2019 | 102  | 19     | 9      | Utilities          | 23.53%        |
| 2020 | 109  | 25     | 9      | Utilities          | 19.27%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | 2.34%          | -0.95%           | 46.67%  | 29.17%  | 0.00%         | 120  | -1.48%         | 0.23%            | 50.83%  | 39.17%  | 20.00%        |
| 2006     | 111  | 111  | -0.91%         | 2.06%            | 51.35%  | 17.12%  | 19.82%        | 111  | -1.10%         | -0.51%           | 45.95%  | 75.68%  | 27.03%        |
| 2007     | 114  | 114  | 4.02%          | 0.68%            | 53.51%  | 70.18%  | 8.77%         | 114  | 5.93%          | 2.23%            | 56.14%  | 55.26%  | 8.77%         |
| 2008     | 115  | 115  | 9.93%          | 15.16%           | 75.65%  | 71.30%  | 4.35%         | 115  | 7.33%          | 8.70%            | 83.48%  | 13.04%  | 10.43%        |
| 2009     | 120  | 120  | 5.00%          | 3.52%            | 61.67%  | 0.83%   | 0.00%         | 120  | 5.10%          | 4.55%            | 72.50%  | 0.00%   | 0.00%         |
| 2010     | 120  | 120  | 4.47%          | 6.77%            | 60.00%  | 20.83%  | 0.00%         | 120  | 1.71%          | -0.38%           | 49.17%  | 5.00%   | 2.50%         |
| 2011     | 120  | 120  | -3.12%         | -0.16%           | 48.33%  | 30.83%  | 0.00%         | 120  | 0.83%          | -2.91%           | 45.83%  | 7.50%   | 0.00%         |
| 2012     | 120  | 120  | 1.29%          | 1.20%            | 52.50%  | 19.17%  | 0.00%         | 120  | -1.42%         | -0.07%           | 49.17%  | 10.83%  | 0.83%         |
| 2013     | 120  | 120  | 2.31%          | 1.36%            | 53.33%  | 7.50%   | 0.00%         | 120  | 1.75%          | 5.31%            | 73.33%  | 15.83%  | 0.00%         |
| 2014     | 120  | 120  | 4.83%          | 5.46%            | 64.17%  | 15.83%  | 0.00%         | 120  | 2.16%          | 2.73%            | 64.17%  | 9.17%   | 0.00%         |
| 2015     | 119  | 119  | 11.99%         | 11.33%           | 78.99%  | 17.65%  | 0.84%         | 119  | -1.65%         | -1.26%           | 43.70%  | 17.65%  | 3.36%         |
| 2016     | 114  | 114  | -4.06%         | -4.46%           | 40.35%  | 12.28%  | 0.00%         | 114  | -2.15%         | -1.48%           | 42.11%  | 15.79%  | 0.00%         |
| 2017     | 118  | 118  | -7.37%         | -7.44%           | 29.66%  | 30.51%  | 0.00%         | 118  | -3.54%         | -2.58%           | 37.29%  | 17.80%  | 5.08%         |
| 2018     | 116  | 116  | 15.34%         | 14.83%           | 87.07%  | 7.76%   | 5.17%         | 116  | -2.33%         | -0.45%           | 43.97%  | 4.31%   | 5.17%         |
| 2019     | 102  | 102  | -10.62%        | -10.59%          | 20.59%  | 40.20%  | 0.00%         | 102  | -5.21%         | -5.34%           | 26.47%  | 16.67%  | 0.00%         |
| 2020     | 109  | 109  | -14.52%        | -22.46%          | 14.68%  | 25.69%  | 0.92%         | 109  | -3.31%         | -1.10%           | 42.20%  | 15.60%  | 6.42%         |
| all buys | 1858 | 1858 | 1.49%          | 1.34%            | 52.85%  | 25.78%  | 2.42%         | 1858 | 0.22%          | 0.44%            | 51.94%  | 19.70%  | 5.54%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -1.48%      | -7.65%            | 6.17%         | -2.43%       | 0.95%    | 39.17%    | 51.93%          | 43.93%     |
| 2006     | 111  | -1.10%      | -9.20%            | 8.10%         | -3.51%       | 2.41%    | 75.68%    | 77.47%          | 73.09%     |
| 2007     | 114  | 5.93%       | -6.61%            | 12.53%        | -0.21%       | 6.14%    | 55.26%    | 69.62%          | 63.59%     |
| 2008     | 115  | 7.33%       | -1.41%            | 8.74%         | 0.73%        | 6.60%    | 13.04%    | 42.57%          | 37.07%     |
| 2009     | 120  | 5.10%       | -0.01%            | 5.11%         | 0.97%        | 4.14%    | 0.00%     | 24.96%          | 15.78%     |
| 2010     | 120  | 1.71%       | -5.91%            | 7.61%         | -1.56%       | 3.27%    | 5.00%     | 27.42%          | 16.27%     |
| 2011     | 120  | 0.83%       | -7.68%            | 8.51%         | -4.14%       | 4.97%    | 7.50%     | 27.47%          | 19.45%     |
| 2012     | 120  | -1.42%      | -7.07%            | 5.65%         | -4.78%       | 3.37%    | 10.83%    | 27.79%          | 21.75%     |
| 2013     | 120  | 1.75%       | -10.38%           | 12.14%        | -6.77%       | 8.52%    | 15.83%    | 39.52%          | 30.36%     |
| 2014     | 120  | 2.16%       | -11.40%           | 13.56%        | -5.39%       | 7.55%    | 9.17%     | 41.08%          | 29.52%     |
| 2015     | 119  | -1.65%      | -10.39%           | 8.74%         | -5.89%       | 4.24%    | 17.65%    | 37.61%          | 29.38%     |
| 2016     | 114  | -2.15%      | -9.18%            | 7.03%         | -3.73%       | 1.58%    | 15.79%    | 35.01%          | 24.30%     |
| 2017     | 118  | -3.54%      | -14.54%           | 11.00%        | -5.59%       | 2.06%    | 17.80%    | 50.60%          | 34.35%     |
| 2018     | 116  | -2.33%      | -11.65%           | 9.32%         | -4.74%       | 2.42%    | 4.31%     | 36.68%          | 21.76%     |
| 2019     | 102  | -5.21%      | -11.93%           | 6.72%         | -4.61%       | -0.60%   | 16.67%    | 39.82%          | 22.65%     |
| 2020     | 109  | -3.31%      | -8.77%            | 5.46%         | -2.94%       | -0.36%   | 15.60%    | 39.44%          | 25.96%     |
| all buys | 1858 | 0.22%       | -8.20%            | 8.42%         | -3.42%       | 3.64%    | 19.70%    | 42.54%          | 31.68%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | 2.34%       | 5.25%             | -2.91%        | 4.79%        | -2.45%   | 29.17%    | 38.73%          | 32.30%     |
| 2006     | 111  | -0.91%      | -0.15%            | -0.76%        | 1.73%        | -2.64%   | 17.12%    | 38.08%          | 28.92%     |
| 2007     | 114  | 4.02%       | -7.00%            | 11.02%        | 0.16%        | 3.86%    | 70.18%    | 73.36%          | 68.38%     |
| 2008     | 115  | 9.93%       | 4.28%             | 5.65%         | 3.73%        | 6.20%    | 71.30%    | 73.80%          | 74.08%     |
| 2009     | 120  | 5.00%       | 31.66%            | -26.65%       | 15.31%       | -10.31%  | 0.83%     | 23.03%          | 17.54%     |
| 2010     | 120  | 4.47%       | 5.09%             | -0.62%        | 5.82%        | -1.35%   | 20.83%    | 33.28%          | 24.78%     |
| 2011     | 120  | -3.12%      | -7.55%            | 4.43%         | -4.10%       | 0.98%    | 30.83%    | 48.29%          | 41.80%     |
| 2012     | 120  | 1.29%       | 3.72%             | -2.43%        | 3.17%        | -1.89%   | 19.17%    | 27.49%          | 22.52%     |
| 2013     | 120  | 2.31%       | 1.72%             | 0.59%         | -0.17%       | 2.48%    | 7.50%     | 28.73%          | 21.00%     |
| 2014     | 120  | 4.83%       | -7.02%            | 11.85%        | -2.66%       | 7.49%    | 15.83%    | 47.37%          | 36.89%     |
| 2015     | 119  | 11.99%      | -9.45%            | 21.43%        | -4.67%       | 16.66%   | 17.65%    | 56.17%          | 49.00%     |
| 2016     | 114  | -4.06%      | 2.15%             | -6.21%        | 0.38%        | -4.44%   | 12.28%    | 30.43%          | 23.19%     |
| 2017     | 118  | -7.37%      | -1.39%            | -5.98%        | -1.71%       | -5.66%   | 30.51%    | 40.54%          | 31.76%     |
| 2018     | 116  | 15.34%      | -9.90%            | 25.24%        | -1.34%       | 16.68%   | 7.76%     | 53.76%          | 40.58%     |
| 2019     | 102  | -10.62%     | -9.73%            | -0.88%        | -5.20%       | -5.42%   | 40.20%    | 55.97%          | 43.43%     |
| 2020     | 109  | -14.52%     | 33.15%            | -47.66%       | 7.65%        | -22.17%  | 25.69%    | 22.31%          | 14.84%     |
| all buys | 1858 | 1.49%       | 2.26%             | -0.77%        | 1.47%        | 0.02%    | 25.78%    | 43.57%          | 35.59%     |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 48
- mean stocks in the point-in-time cross-section: 4031.4 (min 3639)
- mean after the per-model min_score floor: 4031.4 (min 3639)
- mean after the column filters: 4031.4 (min 3639)
- mean after the investability filter: 3220.5 (min 2912)
- mean with a tradable quote: 3143.5 (min 2860)
- forced delisting liquidations: 52 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.5.1`: 2 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.5.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_events_v151` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `e77bbdd029222519`, train run `ff4822397404`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_events_v151_ff4822397404`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_events_forestC_top10_cap2_rankfloor_v151_72a6c7d2679260d3_equity.csv`
- trades: `reports/backtest/bt_nonloser_events_forestC_top10_cap2_rankfloor_v151_72a6c7d2679260d3_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_events_forestC_top10_cap2_rankfloor_v151_72a6c7d2679260d3_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_events_forestC_top10_cap2_rankfloor_v151_72a6c7d2679260d3_equity.png`
