# Portfolio backtest — bt_nonloser_dd30_top10_cap2_s1776

- run `c2a505797f7b`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `f9cab04c4808f47b`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 661,485.08  | 469,485.08 | 10.76%         | 9.90%    | -44.23%      | 1,539.12   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 5.52%        | 6.51%         | -0.99%  | 12,000.00 | 120    | 0.7138          |
| 2006              | 14.83%       | 12.67%        | 2.16%   | 12,000.00 | 111    | 0.7467          |
| 2007              | -0.81%       | 7.28%         | -8.10%  | 12,000.00 | 116    | 0.8178          |
| 2008 (GFC)        | -29.55%      | -43.21%       | 13.65%  | 12,000.00 | 118    | 0.8329          |
| 2009 (GFC)        | 30.72%       | 39.07%        | -8.35%  | 12,000.00 | 120    | 0.8017          |
| 2010              | 27.43%       | 10.86%        | 16.57%  | 12,000.00 | 120    | 0.7429          |
| 2011              | 14.77%       | 5.33%         | 9.44%   | 12,000.00 | 117    | 0.6810          |
| 2012              | 16.25%       | 15.60%        | 0.66%   | 12,000.00 | 120    | 0.6465          |
| 2013              | 18.78%       | 30.42%        | -11.64% | 12,000.00 | 120    | 0.6652          |
| 2014              | 21.65%       | 16.18%        | 5.47%   | 12,000.00 | 116    | 0.6814          |
| 2015              | 3.87%        | 4.46%         | -0.59%  | 12,000.00 | 117    | 0.6985          |
| 2016              | 11.06%       | 6.48%         | 4.58%   | 12,000.00 | 110    | 0.7260          |
| 2017              | 19.15%       | 22.88%        | -3.73%  | 12,000.00 | 115    | 0.7294          |
| 2018              | 6.96%        | 7.53%         | -0.58%  | 12,000.00 | 117    | 0.7292          |
| 2019              | 17.19%       | 13.81%        | 3.38%   | 12,000.00 | 107    | 0.7320          |
| 2020 (COVID)      | 3.82%        | 19.77%        | -15.94% | 12,000.00 | 103    | 0.7383          |
| 2021              | 15.80%       | 24.81%        | -9.02%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.58%        | -8.20%        | 12.78%  | 0.00      | 0      | —               |
| 2023              | 1.93%        | 19.00%        | -17.07% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `product`
- the `product` combination is a conviction ranking, not a joint probability — the per-model scores are correlated
- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Utilities              | 363  | 19.65% |
| Real Estate            | 294  | 15.92% |
| Consumer Defensive     | 269  | 14.56% |
| Industrials            | 230  | 12.45% |
| Energy                 | 213  | 11.53% |
| Healthcare             | 138  | 7.47%  |
| Consumer Cyclical      | 112  | 6.06%  |
| Communication Services | 93   | 5.04%  |
| Technology             | 76   | 4.11%  |
| Financial Services     | 30   | 1.62%  |
| Basic Materials        | 29   | 1.57%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2005 | 120  | 24     | 9      | Real Estate   | 20.00%        |
| 2006 | 111  | 21     | 8      | Real Estate   | 21.62%        |
| 2007 | 116  | 21     | 9      | Real Estate   | 20.69%        |
| 2008 | 118  | 16     | 7      | Real Estate   | 20.34%        |
| 2009 | 120  | 24     | 6      | Utilities     | 20.00%        |
| 2010 | 120  | 21     | 7      | Energy        | 20.00%        |
| 2011 | 117  | 27     | 8      | Utilities     | 20.51%        |
| 2012 | 120  | 28     | 8      | Energy        | 20.00%        |
| 2013 | 120  | 26     | 8      | Utilities     | 20.00%        |
| 2014 | 116  | 28     | 9      | Utilities     | 20.69%        |
| 2015 | 117  | 29     | 7      | Industrials   | 20.51%        |
| 2016 | 110  | 25     | 8      | Utilities     | 21.82%        |
| 2017 | 115  | 23     | 8      | Utilities     | 20.87%        |
| 2018 | 117  | 21     | 8      | Utilities     | 20.51%        |
| 2019 | 107  | 21     | 7      | Utilities     | 22.43%        |
| 2020 | 103  | 24     | 8      | Utilities     | 20.39%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | -2.64%         | -4.72%           | 35.83%  | 38.33%  | 0.83%         | 120  | -1.10%         | -1.39%           | 45.00%  | 38.33%  | 12.50%        |
| 2006     | 111  | 111  | -2.69%         | -1.78%           | 46.85%  | 19.82%  | 5.41%         | 111  | -3.58%         | -1.36%           | 44.14%  | 75.68%  | 8.11%         |
| 2007     | 116  | 116  | 10.06%         | 12.42%           | 68.10%  | 58.62%  | 0.00%         | 116  | 8.25%          | 11.25%           | 68.10%  | 38.79%  | 0.00%         |
| 2008     | 118  | 118  | 6.48%          | 8.34%            | 69.49%  | 72.88%  | 0.00%         | 118  | 6.47%          | 8.24%            | 72.03%  | 20.34%  | 0.00%         |
| 2009     | 120  | 120  | 6.61%          | 6.25%            | 65.00%  | 1.67%   | 2.50%         | 120  | 6.54%          | 6.33%            | 75.00%  | 0.00%   | 2.50%         |
| 2010     | 120  | 120  | 6.65%          | 4.62%            | 66.67%  | 5.00%   | 0.00%         | 120  | 2.85%          | 3.57%            | 66.67%  | 4.17%   | 9.17%         |
| 2011     | 117  | 117  | 8.10%          | 8.37%            | 64.96%  | 17.09%  | 0.00%         | 117  | -0.99%         | -0.13%           | 47.86%  | 5.13%   | 2.56%         |
| 2012     | 120  | 120  | 3.92%          | 4.97%            | 59.17%  | 5.83%   | 0.00%         | 120  | -1.93%         | -1.17%           | 45.83%  | 2.50%   | 2.50%         |
| 2013     | 120  | 120  | -7.87%         | -7.49%           | 35.00%  | 19.17%  | 5.00%         | 120  | 1.43%          | 1.80%            | 59.17%  | 5.00%   | 13.33%        |
| 2014     | 116  | 116  | 3.53%          | 5.44%            | 59.48%  | 26.72%  | 0.00%         | 116  | 2.86%          | 1.41%            | 56.03%  | 8.62%   | 2.59%         |
| 2015     | 117  | 117  | 11.45%         | 11.33%           | 76.07%  | 17.09%  | 3.42%         | 117  | -1.39%         | -0.56%           | 49.57%  | 13.68%  | 3.42%         |
| 2016     | 110  | 110  | -4.82%         | -5.27%           | 36.36%  | 15.45%  | 3.64%         | 110  | -0.56%         | -0.02%           | 50.00%  | 11.82%  | 3.64%         |
| 2017     | 115  | 115  | -2.94%         | -4.45%           | 39.13%  | 21.74%  | 0.00%         | 115  | 0.10%          | 0.19%            | 50.43%  | 9.57%   | 5.22%         |
| 2018     | 117  | 117  | 17.03%         | 15.35%           | 88.03%  | 5.98%   | 7.69%         | 117  | -2.07%         | -1.17%           | 40.17%  | 1.71%   | 7.69%         |
| 2019     | 107  | 107  | -10.55%        | -10.73%          | 23.36%  | 39.25%  | 1.87%         | 107  | -4.98%         | -3.84%           | 28.97%  | 14.95%  | 1.87%         |
| 2020     | 103  | 103  | -16.12%        | -19.30%          | 12.62%  | 24.27%  | 0.97%         | 103  | -2.72%         | -1.24%           | 42.72%  | 12.62%  | 6.80%         |
| all buys | 1847 | 1847 | 1.88%          | 1.80%            | 53.44%  | 24.20%  | 1.95%         | 1847 | 0.65%          | 0.66%            | 52.90%  | 16.24%  | 5.14%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 57
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 45 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 13 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_cap2_s1776_f9cab04c4808f47b_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_cap2_s1776_f9cab04c4808f47b_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_cap2_s1776_f9cab04c4808f47b_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_cap2_s1776_f9cab04c4808f47b_equity.png`
