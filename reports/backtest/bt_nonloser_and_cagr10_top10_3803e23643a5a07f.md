# Portfolio backtest — bt_nonloser_and_cagr10_top10

- run `35dd46130cbc`, git `319144c0016b771eeeb57b9d17f1cb63915225d3`, backtest config `3803e23643a5a07f`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 541,571.39  | 349,571.39 | 9.07%          | 7.72%    | -64.75%      | 1,513.37   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 6.40%        | 6.51%         | -0.12%  | 12,000.00 | 120    | -7.7000         |
| 2006              | 31.82%       | 12.67%        | 19.15%  | 12,000.00 | 120    | -7.2917         |
| 2007              | -22.44%      | 7.28%         | -29.73% | 12,000.00 | 118    | -7.1186         |
| 2008 (GFC)        | -46.69%      | -43.21%       | -3.48%  | 12,000.00 | 118    | -7.1356         |
| 2009 (GFC)        | 49.29%       | 39.07%        | 10.22%  | 12,000.00 | 120    | -7.5500         |
| 2010              | 27.26%       | 10.86%        | 16.40%  | 12,000.00 | 120    | -8.7000         |
| 2011              | 13.05%       | 5.33%         | 7.72%   | 12,000.00 | 120    | -14.3375        |
| 2012              | 17.12%       | 15.60%        | 1.52%   | 12,000.00 | 120    | -13.5125        |
| 2013              | 14.28%       | 30.42%        | -16.14% | 12,000.00 | 120    | -13.0375        |
| 2014              | 23.78%       | 16.18%        | 7.60%   | 12,000.00 | 117    | -8.5769         |
| 2015              | 2.93%        | 4.46%         | -1.53%  | 12,000.00 | 120    | -13.2750        |
| 2016              | 11.35%       | 6.48%         | 4.87%   | 12,000.00 | 116    | -10.2974        |
| 2017              | 19.79%       | 22.88%        | -3.08%  | 12,000.00 | 113    | -8.6637         |
| 2018              | 5.03%        | 7.53%         | -2.51%  | 12,000.00 | 120    | -9.1125         |
| 2019              | 15.87%       | 13.81%        | 2.06%   | 12,000.00 | 117    | -11.2692        |
| 2020 (COVID)      | 0.11%        | 19.77%        | -19.65% | 12,000.00 | 114    | -9.6974         |
| 2021              | 15.46%       | 24.81%        | -9.35%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 5.32%        | -8.20%        | 13.51%  | 0.00      | 0      | —               |
| 2023              | -2.15%       | 19.00%        | -21.15% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 1 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 2 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`
- costs: 35.0 bps per side (benchmark 0.0 bps)

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 23
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 49 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 3 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `forest_cagr10_dd20_3y` — label `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` (3y), model `random_forest`, config `8b3d0dc22175d8e7`, train run `df10b2ee396f`, folds 2005–2020 (from `experiments/models/forest_cagr10_dd20_3y_df10b2ee396f`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_and_cagr10_top10_3803e23643a5a07f_equity.csv`
- trades: `reports/backtest/bt_nonloser_and_cagr10_top10_3803e23643a5a07f_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_and_cagr10_top10_3803e23643a5a07f_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_and_cagr10_top10_3803e23643a5a07f_equity.png`
