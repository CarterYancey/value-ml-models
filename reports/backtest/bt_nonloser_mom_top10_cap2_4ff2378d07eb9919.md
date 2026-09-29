# Portfolio backtest — bt_nonloser_mom_top10_cap2

- run `4bf40ca96a19`, git `52f2ccda31ca487d3a79a5e38c8ddb6dfcf6cf8f`, backtest config `4ff2378d07eb9919`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 711,494.43  | 519,494.43 | 11.38%         | 11.07%   | -47.83%      | 1,592.12   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 15.28%       | 6.51%         | 8.77%   | 12,000.00 | 102    | -314.0784       |
| 2006              | 20.78%       | 12.67%        | 8.11%   | 12,000.00 | 117    | -373.2821       |
| 2007              | 6.94%        | 7.28%         | -0.34%  | 12,000.00 | 119    | -292.5210       |
| 2008 (GFC)        | -40.57%      | -43.21%       | 2.64%   | 12,000.00 | 120    | -249.3625       |
| 2009 (GFC)        | 47.50%       | 39.07%        | 8.43%   | 12,000.00 | 114    | -132.0570       |
| 2010              | 27.69%       | 10.86%        | 16.83%  | 12,000.00 | 117    | -379.8547       |
| 2011              | 11.84%       | 5.33%         | 6.51%   | 12,000.00 | 115    | -314.9000       |
| 2012              | 9.44%        | 15.60%        | -6.16%  | 12,000.00 | 112    | -169            |
| 2013              | 30.76%       | 30.42%        | 0.34%   | 12,000.00 | 119    | -258.1513       |
| 2014              | 14.68%       | 16.18%        | -1.50%  | 12,000.00 | 109    | -325.3899       |
| 2015              | 1.22%        | 4.46%         | -3.25%  | 12,000.00 | 116    | -217.5733       |
| 2016              | 9.64%        | 6.48%         | 3.17%   | 12,000.00 | 112    | -164.1607       |
| 2017              | 18.40%       | 22.88%        | -4.47%  | 12,000.00 | 111    | -303.2658       |
| 2018              | 9.56%        | 7.53%         | 2.03%   | 12,000.00 | 103    | -293.0728       |
| 2019              | 15.58%       | 13.81%        | 1.77%   | 12,000.00 | 108    | -208.9583       |
| 2020 (COVID)      | 11.84%       | 19.77%        | -7.92%  | 12,000.00 | 89     | -209.7865       |
| 2021              | 19.98%       | 24.81%        | -4.83%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 5.21%        | -8.20%        | 13.41%  | 0.00      | 0      | —               |
| 2023              | 2.18%        | 19.00%        | -16.83% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 249  | 13.97% |
| Consumer Cyclical      | 229  | 12.84% |
| Industrials            | 220  | 12.34% |
| Real Estate            | 192  | 10.77% |
| Utilities              | 180  | 10.10% |
| Healthcare             | 180  | 10.10% |
| Energy                 | 178  | 9.98%  |
| Basic Materials        | 138  | 7.74%  |
| Technology             | 114  | 6.39%  |
| Communication Services | 80   | 4.49%  |
| Financial Services     | 23   | 1.29%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 102  | 29     | 9      | Real Estate        | 23.53%        |
| 2006 | 117  | 36     | 11     | Real Estate        | 17.95%        |
| 2007 | 119  | 37     | 10     | Energy             | 17.65%        |
| 2008 | 120  | 33     | 9      | Industrials        | 17.50%        |
| 2009 | 114  | 32     | 9      | Consumer Defensive | 21.05%        |
| 2010 | 117  | 32     | 8      | Energy             | 20.51%        |
| 2011 | 115  | 33     | 8      | Healthcare         | 18.26%        |
| 2012 | 112  | 30     | 10     | Consumer Defensive | 21.43%        |
| 2013 | 119  | 35     | 9      | Consumer Cyclical  | 17.65%        |
| 2014 | 109  | 27     | 9      | Healthcare         | 19.27%        |
| 2015 | 116  | 29     | 11     | Consumer Defensive | 20.69%        |
| 2016 | 112  | 33     | 7      | Real Estate        | 19.64%        |
| 2017 | 111  | 36     | 8      | Consumer Cyclical  | 19.82%        |
| 2018 | 103  | 29     | 11     | Consumer Cyclical  | 20.39%        |
| 2019 | 108  | 33     | 9      | Utilities          | 16.67%        |
| 2020 | 89   | 29     | 9      | Consumer Defensive | 22.47%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 84
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 134 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 8 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_equity.png`
