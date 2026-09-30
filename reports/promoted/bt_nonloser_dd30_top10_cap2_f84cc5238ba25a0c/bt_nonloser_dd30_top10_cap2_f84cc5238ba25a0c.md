# Portfolio backtest — bt_nonloser_dd30_top10_cap2

- run `c002116eefbe`, git `499884bdad9045e076ea5f4cef753aa1cbb4473f`, backtest config `f84cc5238ba25a0c`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 633,756.90  | 441,756.90 | 10.40%         | 9.74%    | -46.10%      | 1,442.67   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 10.31%       | 6.51%         | 3.79%   | 12,000.00 | 120    | 0.7166          |
| 2006              | 16.53%       | 12.67%        | 3.86%   | 12,000.00 | 111    | 0.7442          |
| 2007              | -4.48%       | 7.28%         | -11.77% | 12,000.00 | 113    | 0.8110          |
| 2008 (GFC)        | -29.84%      | -43.21%       | 13.37%  | 12,000.00 | 118    | 0.8312          |
| 2009 (GFC)        | 30.77%       | 39.07%        | -8.30%  | 12,000.00 | 120    | 0.8023          |
| 2010              | 26.92%       | 10.86%        | 16.06%  | 12,000.00 | 120    | 0.7432          |
| 2011              | 13.59%       | 5.33%         | 8.26%   | 12,000.00 | 117    | 0.6801          |
| 2012              | 16.89%       | 15.60%        | 1.30%   | 12,000.00 | 120    | 0.6409          |
| 2013              | 17.56%       | 30.42%        | -12.86% | 12,000.00 | 120    | 0.6620          |
| 2014              | 20.51%       | 16.18%        | 4.32%   | 12,000.00 | 115    | 0.6840          |
| 2015              | 4.15%        | 4.46%         | -0.31%  | 12,000.00 | 117    | 0.6974          |
| 2016              | 11.01%       | 6.48%         | 4.54%   | 12,000.00 | 111    | 0.7238          |
| 2017              | 19.40%       | 22.88%        | -3.47%  | 12,000.00 | 117    | 0.7288          |
| 2018              | 5.94%        | 7.53%         | -1.59%  | 12,000.00 | 116    | 0.7251          |
| 2019              | 16.38%       | 13.81%        | 2.57%   | 12,000.00 | 106    | 0.7335          |
| 2020 (COVID)      | 3.52%        | 19.77%        | -16.25% | 12,000.00 | 106    | 0.7338          |
| 2021              | 15.46%       | 24.81%        | -9.35%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.18%        | -8.20%        | 12.38%  | 0.00      | 0      | —               |
| 2023              | 2.44%        | 19.00%        | -16.56% | 0.00      | 0      | —               |

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
| Real Estate            | 293  | 15.86% |
| Consumer Defensive     | 270  | 14.62% |
| Industrials            | 238  | 12.89% |
| Energy                 | 210  | 11.37% |
| Healthcare             | 152  | 8.23%  |
| Consumer Cyclical      | 130  | 7.04%  |
| Communication Services | 71   | 3.84%  |
| Technology             | 62   | 3.36%  |
| Financial Services     | 39   | 2.11%  |
| Basic Materials        | 19   | 1.03%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 120  | 25     | 9      | Real Estate        | 20.00%        |
| 2006 | 111  | 19     | 8      | Real Estate        | 21.62%        |
| 2007 | 113  | 21     | 9      | Real Estate        | 21.24%        |
| 2008 | 118  | 22     | 7      | Real Estate        | 20.34%        |
| 2009 | 120  | 23     | 6      | Energy             | 20.00%        |
| 2010 | 120  | 18     | 8      | Utilities          | 20.00%        |
| 2011 | 117  | 23     | 8      | Utilities          | 20.51%        |
| 2012 | 120  | 27     | 7      | Energy             | 20.00%        |
| 2013 | 120  | 26     | 8      | Utilities          | 20.00%        |
| 2014 | 115  | 27     | 9      | Utilities          | 20.87%        |
| 2015 | 117  | 30     | 7      | Utilities          | 20.51%        |
| 2016 | 111  | 26     | 8      | Consumer Defensive | 21.62%        |
| 2017 | 117  | 24     | 8      | Consumer Defensive | 20.51%        |
| 2018 | 116  | 25     | 8      | Utilities          | 20.69%        |
| 2019 | 106  | 18     | 7      | Utilities          | 22.64%        |
| 2020 | 106  | 25     | 8      | Industrials        | 22.64%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 61
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 50 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 4 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_cap2_f84cc5238ba25a0c_equity.png`
