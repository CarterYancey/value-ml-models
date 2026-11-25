# Portfolio backtest — bt_nonloser_roc_top10_cap2_s232

- run `cce008131b2f`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `a4f97c4193024199`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 752,267.12  | 560,267.12 | 11.85%         | 10.18%   | -42.41%      | 1,105.19   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.09%        | 6.51%         | -4.43%  | 12,000.00 | 108    | -87.7315        |
| 2006              | 12.35%       | 12.67%        | -0.32%  | 12,000.00 | 117    | -84.5641        |
| 2007              | 2.53%        | 7.28%         | -4.75%  | 12,000.00 | 120    | -100.1333       |
| 2008 (GFC)        | -32.43%      | -43.21%       | 10.78%  | 12,000.00 | 120    | -82.1708        |
| 2009 (GFC)        | 34.90%       | 39.07%        | -4.17%  | 12,000.00 | 120    | -76.1167        |
| 2010              | 16.36%       | 10.86%        | 5.50%   | 12,000.00 | 118    | -86.3983        |
| 2011              | 9.04%        | 5.33%         | 3.71%   | 12,000.00 | 114    | -74.7149        |
| 2012              | 12.34%       | 15.60%        | -3.25%  | 12,000.00 | 108    | -77.6528        |
| 2013              | 29.85%       | 30.42%        | -0.57%  | 12,000.00 | 111    | -60.5360        |
| 2014              | 19.82%       | 16.18%        | 3.64%   | 12,000.00 | 108    | -54.1435        |
| 2015              | 12.82%       | 4.46%         | 8.36%   | 12,000.00 | 105    | -53.5857        |
| 2016              | 8.40%        | 6.48%         | 1.92%   | 12,000.00 | 105    | -75.9048        |
| 2017              | 21.23%       | 22.88%        | -1.65%  | 12,000.00 | 110    | -57.9045        |
| 2018              | 7.72%        | 7.53%         | 0.19%   | 12,000.00 | 113    | -69.1637        |
| 2019              | 18.36%       | 13.81%        | 4.55%   | 12,000.00 | 110    | -83.3909        |
| 2020 (COVID)      | 12.24%       | 19.77%        | -7.53%  | 12,000.00 | 97     | -58.5464        |
| 2021              | 14.04%       | 24.81%        | -10.77% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.37%        | -8.20%        | 12.56%  | 0.00      | 0      | —               |
| 2023              | 5.01%        | 19.00%        | -14.00% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 2 walk-forward model(s), combined by `mean_rank`

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
| Consumer Defensive     | 384  | 21.52% |
| Industrials            | 321  | 17.99% |
| Technology             | 318  | 17.83% |
| Healthcare             | 281  | 15.75% |
| Consumer Cyclical      | 232  | 13.00% |
| Communication Services | 66   | 3.70%  |
| Financial Services     | 63   | 3.53%  |
| Energy                 | 54   | 3.03%  |
| Basic Materials        | 50   | 2.80%  |
| Real Estate            | 9    | 0.50%  |
| Utilities              | 6    | 0.34%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 15     | 9      | Consumer Defensive | 22.22%        |
| 2006 | 117  | 21     | 8      | Consumer Defensive | 20.51%        |
| 2007 | 120  | 22     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 120  | 17     | 6      | Healthcare         | 20.00%        |
| 2010 | 118  | 18     | 8      | Consumer Defensive | 20.34%        |
| 2011 | 114  | 18     | 8      | Consumer Defensive | 21.05%        |
| 2012 | 108  | 21     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 111  | 17     | 7      | Consumer Defensive | 21.62%        |
| 2014 | 108  | 15     | 6      | Consumer Defensive | 22.22%        |
| 2015 | 105  | 15     | 6      | Consumer Defensive | 22.86%        |
| 2016 | 105  | 15     | 7      | Consumer Defensive | 22.86%        |
| 2017 | 110  | 21     | 8      | Technology         | 21.82%        |
| 2018 | 113  | 21     | 8      | Consumer Defensive | 21.24%        |
| 2019 | 110  | 21     | 8      | Consumer Defensive | 21.82%        |
| 2020 | 97   | 21     | 7      | Consumer Defensive | 24.74%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -4.76%         | -4.18%           | 33.33%  | 32.41%  | 0.00%         | 108  | -2.06%         | -1.07%           | 39.81%  | 41.67%  | 16.67%        |
| 2006     | 117  | 117  | 0.23%          | -0.41%           | 48.72%  | 11.97%  | 0.00%         | 117  | 1.63%          | 3.17%            | 60.68%  | 63.25%  | 2.56%         |
| 2007     | 120  | 120  | 2.39%          | 3.47%            | 61.67%  | 63.33%  | 0.00%         | 120  | 4.56%          | 6.46%            | 70.83%  | 54.17%  | 2.50%         |
| 2008     | 120  | 120  | 11.65%         | 14.33%           | 75.83%  | 76.67%  | 0.00%         | 120  | 6.79%          | 6.40%            | 83.33%  | 7.50%   | 0.00%         |
| 2009     | 120  | 120  | 4.04%          | -0.15%           | 50.00%  | 10.83%  | 3.33%         | 120  | 2.77%          | 0.12%            | 51.67%  | 0.00%   | 5.00%         |
| 2010     | 118  | 118  | 3.70%          | 2.95%            | 61.02%  | 8.47%   | 0.00%         | 118  | 1.14%          | 2.05%            | 52.54%  | 5.08%   | 0.00%         |
| 2011     | 114  | 114  | 6.19%          | 0.79%            | 54.39%  | 22.81%  | 0.00%         | 114  | 0.46%          | 0.41%            | 50.88%  | 0.88%   | 0.00%         |
| 2012     | 108  | 108  | -2.30%         | -0.75%           | 47.22%  | 13.89%  | 0.00%         | 108  | 2.61%          | 4.93%            | 70.37%  | 4.63%   | 0.93%         |
| 2013     | 111  | 111  | 2.57%          | 3.50%            | 56.76%  | 6.31%   | 0.00%         | 111  | 8.03%          | 7.40%            | 80.18%  | 2.70%   | 0.00%         |
| 2014     | 108  | 108  | 14.18%         | 15.03%           | 81.48%  | 6.48%   | 0.00%         | 108  | 6.80%          | 7.70%            | 76.85%  | 8.33%   | 0.00%         |
| 2015     | 105  | 105  | 11.27%         | 10.80%           | 80.00%  | 18.10%  | 0.00%         | 105  | 0.51%          | 1.97%            | 59.05%  | 19.05%  | 0.00%         |
| 2016     | 105  | 105  | 1.10%          | -0.27%           | 48.57%  | 9.52%   | 0.00%         | 105  | 0.43%          | 4.70%            | 66.67%  | 20.95%  | 0.00%         |
| 2017     | 110  | 110  | 2.83%          | 5.75%            | 60.91%  | 13.64%  | 4.55%         | 110  | 4.39%          | 6.43%            | 75.45%  | 9.09%   | 5.45%         |
| 2018     | 113  | 113  | 8.83%          | 9.43%            | 69.91%  | 22.12%  | 2.65%         | 113  | -2.59%         | -2.00%           | 38.94%  | 1.77%   | 5.31%         |
| 2019     | 110  | 110  | -4.02%         | -5.00%           | 42.73%  | 38.18%  | 0.00%         | 110  | -4.49%         | -4.24%           | 25.45%  | 7.27%   | 1.82%         |
| 2020     | 97   | 97   | -17.78%        | -14.62%          | 19.59%  | 17.53%  | 0.00%         | 97   | -2.38%         | -1.42%           | 42.27%  | 13.40%  | 11.34%        |
| all buys | 1784 | 1784 | 2.71%          | 2.57%            | 56.11%  | 23.71%  | 0.67%         | 1784 | 1.86%          | 2.53%            | 59.25%  | 16.37%  | 3.14%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 106
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 23 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 14 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_s232_a4f97c4193024199_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_s232_a4f97c4193024199_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_s232_a4f97c4193024199_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_s232_a4f97c4193024199_equity.png`
