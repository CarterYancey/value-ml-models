# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_frac

- run `71e1e1f053f4`, git `ba55f7d9adc1654cdb466dee924ac976e3f9a828`, backtest config `f8b5054944c86da0`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 936,539.99  | 744,539.99 | 13.68%         | 12.12%   | -42.97%      | 1,198.84   |
| benchmark | 192,000.00 | 732,355.97  | 540,355.97 | 11.62%         | 9.59%    | -52.91%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 8.22%        | 6.60%         | 1.62%  | 12,000.00 | 120    | -336.2833       |
| 2006              | 11.10%       | 12.70%        | -1.60% | 12,000.00 | 120    | -369.3444       |
| 2007              | 1.93%        | 7.29%         | -5.36% | 12,000.00 | 120    | -336.2722       |
| 2008 (GFC)        | -34.71%      | -43.24%       | 8.53%  | 12,000.00 | 120    | -287.2333       |
| 2009 (GFC)        | 43.17%       | 39.09%        | 4.08%  | 12,000.00 | 120    | -188.5806       |
| 2010              | 27.60%       | 10.87%        | 16.73% | 12,000.00 | 120    | -367.5778       |
| 2011              | 11.04%       | 5.32%         | 5.72%  | 12,000.00 | 120    | -289.3972       |
| 2012              | 15.27%       | 15.60%        | -0.33% | 12,000.00 | 120    | -189.0972       |
| 2013              | 35.59%       | 30.43%        | 5.16%  | 12,000.00 | 120    | -258.3583       |
| 2014              | 12.39%       | 16.19%        | -3.80% | 12,000.00 | 120    | -303.8278       |
| 2015              | 12.51%       | 4.46%         | 8.05%  | 12,000.00 | 120    | -204.4444       |
| 2016              | 4.21%        | 6.48%         | -2.26% | 12,000.00 | 120    | -186.0583       |
| 2017              | 21.92%       | 22.88%        | -0.97% | 12,000.00 | 120    | -291.1944       |
| 2018              | 9.19%        | 7.54%         | 1.65%  | 12,000.00 | 120    | -259.8194       |
| 2019              | 23.46%       | 13.81%        | 9.65%  | 12,000.00 | 120    | -224.0194       |
| 2020 (COVID)      | 21.06%       | 19.76%        | 1.31%  | 12,000.00 | 120    | -211.2889       |
| 2021              | 15.99%       | 24.83%        | -8.84% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -2.41%       | -8.20%        | 5.79%  | 0.00      | 0      | —               |
| 2023              | 16.57%       | 19.01%        | -2.44% | 0.00      | 0      | —               |

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
| Industrials            | 314  | 16.35% |
| Consumer Defensive     | 308  | 16.04% |
| Consumer Cyclical      | 307  | 15.99% |
| Healthcare             | 307  | 15.99% |
| Technology             | 286  | 14.90% |
| Basic Materials        | 144  | 7.50%  |
| Communication Services | 95   | 4.95%  |
| Financial Services     | 94   | 4.90%  |
| Energy                 | 36   | 1.88%  |
| Real Estate            | 20   | 1.04%  |
| Utilities              | 9    | 0.47%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 120  | 27     | 9      | Consumer Cyclical  | 20.00%        |
| 2006 | 120  | 29     | 7      | Industrials        | 20.00%        |
| 2007 | 120  | 31     | 8      | Industrials        | 20.00%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 120  | 33     | 10     | Healthcare         | 20.00%        |
| 2010 | 120  | 28     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 120  | 30     | 9      | Consumer Cyclical  | 20.00%        |
| 2012 | 120  | 31     | 9      | Consumer Defensive | 20.00%        |
| 2013 | 120  | 33     | 8      | Healthcare         | 18.33%        |
| 2014 | 120  | 27     | 7      | Industrials        | 20.00%        |
| 2015 | 120  | 24     | 8      | Consumer Defensive | 20.00%        |
| 2016 | 120  | 28     | 8      | Technology         | 20.00%        |
| 2017 | 120  | 29     | 9      | Consumer Cyclical  | 20.00%        |
| 2018 | 120  | 26     | 8      | Consumer Cyclical  | 20.00%        |
| 2019 | 120  | 30     | 7      | Consumer Defensive | 20.00%        |
| 2020 | 120  | 32     | 8      | Consumer Defensive | 17.50%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | -2.01%         | -4.42%           | 42.50%  | 33.33%  | 0.00%         | 120  | -5.59%         | -0.09%           | 50.00%  | 42.50%  | 7.50%         |
| 2006     | 120  | 120  | -11.03%        | -11.95%          | 26.67%  | 43.33%  | 5.00%         | 120  | 1.81%          | 2.05%            | 60.00%  | 71.67%  | 5.00%         |
| 2007     | 120  | 120  | 4.32%          | 4.77%            | 65.00%  | 59.17%  | 1.67%         | 120  | 8.19%          | 7.79%            | 82.50%  | 41.67%  | 11.67%        |
| 2008     | 120  | 120  | 9.44%          | 11.35%           | 66.67%  | 77.50%  | 0.83%         | 120  | 7.63%          | 7.76%            | 86.67%  | 10.00%  | 3.33%         |
| 2009     | 120  | 120  | 6.79%          | 7.96%            | 59.17%  | 12.50%  | 6.67%         | 120  | -0.10%         | -0.31%           | 46.67%  | 8.33%   | 10.83%        |
| 2010     | 120  | 120  | 21.81%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 9.43%          | 8.82%            | 79.17%  | 1.67%   | 6.67%         |
| 2011     | 120  | 120  | 10.42%         | 9.21%            | 66.67%  | 17.50%  | 5.00%         | 120  | 5.26%          | 4.80%            | 72.50%  | 5.83%   | 7.50%         |
| 2012     | 120  | 120  | -0.28%         | -3.05%           | 45.00%  | 15.83%  | 0.00%         | 120  | -1.66%         | 2.62%            | 55.00%  | 19.17%  | 0.83%         |
| 2013     | 120  | 120  | -0.40%         | -0.73%           | 45.83%  | 13.33%  | 2.50%         | 120  | 2.59%          | 3.68%            | 66.67%  | 15.00%  | 5.00%         |
| 2014     | 120  | 120  | 13.72%         | 16.32%           | 75.83%  | 16.67%  | 4.17%         | 120  | 3.91%          | 4.17%            | 61.67%  | 15.83%  | 11.67%        |
| 2015     | 120  | 120  | 3.45%          | 2.64%            | 56.67%  | 33.33%  | 0.00%         | 120  | 3.00%          | 5.07%            | 65.83%  | 13.33%  | 2.50%         |
| 2016     | 120  | 120  | -2.85%         | -3.08%           | 40.00%  | 14.17%  | 2.50%         | 120  | 1.82%          | 4.38%            | 62.50%  | 15.83%  | 5.00%         |
| 2017     | 120  | 120  | 2.48%          | 0.65%            | 50.83%  | 22.50%  | 4.17%         | 120  | 2.33%          | 0.76%            | 55.83%  | 19.17%  | 12.50%        |
| 2018     | 120  | 120  | 11.99%         | 8.80%            | 75.83%  | 18.33%  | 0.00%         | 120  | 2.87%          | 0.18%            | 51.67%  | 8.33%   | 5.00%         |
| 2019     | 120  | 120  | -1.83%         | -1.45%           | 45.00%  | 33.33%  | 0.00%         | 120  | -5.05%         | -5.94%           | 20.00%  | 13.33%  | 0.00%         |
| 2020     | 120  | 120  | -14.03%        | -16.06%          | 32.50%  | 28.33%  | 0.00%         | 120  | -2.69%         | -3.58%           | 39.17%  | 21.67%  | 7.50%         |
| all buys | 1920 | 1920 | 3.25%          | 2.57%            | 54.32%  | 27.97%  | 2.14%         | 1920 | 2.11%          | 2.70%            | 59.74%  | 20.21%  | 6.41%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 0
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 67 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 23 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_frac_f8b5054944c86da0_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_frac_f8b5054944c86da0_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_frac_f8b5054944c86da0_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_frac_f8b5054944c86da0_equity.png`
