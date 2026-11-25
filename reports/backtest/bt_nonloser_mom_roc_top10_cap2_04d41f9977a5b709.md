# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2

- run `d3474af92b20`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `04d41f9977a5b709`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 948,956.09  | 756,956.09 | 13.79%         | 12.24%   | -41.22%      | 1,206.32   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 7.80%        | 6.51%         | 1.29%  | 12,000.00 | 108    | -345.7037       |
| 2006              | 9.78%        | 12.67%        | -2.89% | 12,000.00 | 120    | -369.3444       |
| 2007              | 3.46%        | 7.28%         | -3.82% | 12,000.00 | 116    | -335.1466       |
| 2008 (GFC)        | -33.70%      | -43.21%       | 9.50%  | 12,000.00 | 120    | -287.2333       |
| 2009 (GFC)        | 42.34%       | 39.07%        | 3.27%  | 12,000.00 | 115    | -190.0725       |
| 2010              | 27.62%       | 10.86%        | 16.76% | 12,000.00 | 120    | -367.5778       |
| 2011              | 11.29%       | 5.33%         | 5.97%  | 12,000.00 | 109    | -290.7920       |
| 2012              | 15.43%       | 15.60%        | -0.17% | 12,000.00 | 106    | -189.4277       |
| 2013              | 36.12%       | 30.42%        | 5.70%  | 12,000.00 | 114    | -258.4561       |
| 2014              | 12.69%       | 16.18%        | -3.50% | 12,000.00 | 109    | -302.0703       |
| 2015              | 12.41%       | 4.46%         | 7.95%  | 12,000.00 | 105    | -202.6603       |
| 2016              | 4.70%        | 6.48%         | -1.77% | 12,000.00 | 108    | -187.9012       |
| 2017              | 22.92%       | 22.88%        | 0.04%  | 12,000.00 | 105    | -292.7524       |
| 2018              | 9.07%        | 7.53%         | 1.54%  | 12,000.00 | 96     | -260.0521       |
| 2019              | 23.17%       | 13.81%        | 9.36%  | 12,000.00 | 103    | -220.4369       |
| 2020 (COVID)      | 21.82%       | 19.77%        | 2.06%  | 12,000.00 | 87     | -208.9119       |
| 2021              | 15.35%       | 24.81%        | -9.46% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -3.59%       | -8.20%        | 4.61%  | 0.00      | 0      | —               |
| 2023              | 17.05%       | 19.00%        | -1.95% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

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
| Consumer Defensive     | 300  | 17.23% |
| Industrials            | 287  | 16.48% |
| Technology             | 267  | 15.34% |
| Healthcare             | 264  | 15.16% |
| Consumer Cyclical      | 257  | 14.76% |
| Basic Materials        | 139  | 7.98%  |
| Communication Services | 93   | 5.34%  |
| Financial Services     | 74   | 4.25%  |
| Energy                 | 36   | 2.07%  |
| Real Estate            | 15   | 0.86%  |
| Utilities              | 9    | 0.52%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 26     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 29     | 7      | Industrials        | 20.00%        |
| 2007 | 116  | 30     | 8      | Consumer Defensive | 18.10%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 115  | 33     | 10     | Healthcare         | 20.87%        |
| 2010 | 120  | 28     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive | 22.02%        |
| 2012 | 106  | 29     | 8      | Consumer Defensive | 22.64%        |
| 2013 | 114  | 32     | 8      | Healthcare         | 19.30%        |
| 2014 | 109  | 25     | 7      | Technology         | 22.02%        |
| 2015 | 105  | 23     | 8      | Technology         | 20.00%        |
| 2016 | 108  | 27     | 8      | Consumer Defensive | 22.22%        |
| 2017 | 105  | 28     | 9      | Industrials        | 21.90%        |
| 2018 | 96   | 24     | 8      | Consumer Cyclical  | 25.00%        |
| 2019 | 103  | 27     | 7      | Consumer Defensive | 23.30%        |
| 2020 | 87   | 27     | 8      | Technology         | 22.99%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.23%         | -5.65%           | 37.04%  | 37.04%  | 0.00%         | 108  | -5.46%         | 0.56%            | 54.63%  | 40.74%  | 8.33%         |
| 2006     | 120  | 120  | -11.03%        | -11.95%          | 26.67%  | 43.33%  | 5.00%         | 120  | 1.81%          | 2.05%            | 60.00%  | 71.67%  | 5.00%         |
| 2007     | 116  | 116  | 4.84%          | 5.33%            | 66.38%  | 58.62%  | 1.72%         | 116  | 8.12%          | 7.87%            | 81.90%  | 40.52%  | 12.07%        |
| 2008     | 120  | 120  | 9.44%          | 11.35%           | 66.67%  | 77.50%  | 0.83%         | 120  | 7.63%          | 7.76%            | 86.67%  | 10.00%  | 3.33%         |
| 2009     | 115  | 115  | 5.55%          | 6.19%            | 57.39%  | 13.04%  | 6.96%         | 115  | -1.07%         | -0.76%           | 44.35%  | 8.70%   | 11.30%        |
| 2010     | 120  | 120  | 21.81%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 9.43%          | 8.82%            | 79.17%  | 1.67%   | 6.67%         |
| 2011     | 109  | 109  | 9.86%          | 8.10%            | 66.97%  | 19.27%  | 5.50%         | 109  | 5.31%          | 4.45%            | 73.39%  | 6.42%   | 8.26%         |
| 2012     | 106  | 106  | -0.78%         | -1.74%           | 47.17%  | 16.04%  | 0.00%         | 106  | 0.18%          | 4.49%            | 56.60%  | 16.04%  | 0.94%         |
| 2013     | 114  | 114  | -0.78%         | -0.83%           | 43.86%  | 14.04%  | 2.63%         | 114  | 2.84%          | 4.18%            | 67.54%  | 15.79%  | 5.26%         |
| 2014     | 109  | 109  | 13.89%         | 16.34%           | 75.23%  | 16.51%  | 4.59%         | 109  | 4.35%          | 4.14%            | 62.39%  | 12.84%  | 11.01%        |
| 2015     | 105  | 105  | 5.91%          | 3.96%            | 61.90%  | 26.67%  | 0.00%         | 105  | 3.91%          | 5.81%            | 71.43%  | 12.38%  | 2.86%         |
| 2016     | 108  | 108  | -2.47%         | -4.05%           | 38.89%  | 12.96%  | 2.78%         | 108  | 1.61%          | 4.69%            | 62.04%  | 17.59%  | 5.56%         |
| 2017     | 105  | 105  | 0.29%          | -3.29%           | 44.76%  | 25.71%  | 4.76%         | 105  | 1.19%          | 0.12%            | 50.48%  | 20.95%  | 14.29%        |
| 2018     | 96   | 96   | 11.34%         | 6.80%            | 72.92%  | 19.79%  | 0.00%         | 96   | 4.36%          | 2.16%            | 53.12%  | 4.17%   | 6.25%         |
| 2019     | 103  | 103  | -2.83%         | -2.66%           | 42.72%  | 35.92%  | 0.00%         | 103  | -4.92%         | -5.94%           | 20.39%  | 13.59%  | 0.00%         |
| 2020     | 87   | 87   | -13.49%        | -16.50%          | 34.48%  | 29.89%  | 0.00%         | 87   | -1.58%         | -1.32%           | 43.68%  | 25.29%  | 10.34%        |
| all buys | 1741 | 1741 | 3.27%          | 2.25%            | 53.88%  | 28.78%  | 2.35%         | 1741 | 2.51%          | 3.52%            | 61.23%  | 20.16%  | 6.95%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 111
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 65 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 16 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_04d41f9977a5b709_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_04d41f9977a5b709_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_04d41f9977a5b709_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_04d41f9977a5b709_equity.png`
