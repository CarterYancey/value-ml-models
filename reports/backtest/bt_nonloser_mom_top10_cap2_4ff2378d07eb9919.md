# Portfolio backtest — bt_nonloser_mom_top10_cap2

- run `8aefec89c719`, git `e2c2e4a1a90815ac91ab18a6618222f25957bebd`, backtest config `4ff2378d07eb9919`
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

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 102  | 102  | 7.45%          | 2.89%            | 56.86%  | 29.41%  | 11.76%        | 102  | 3.25%          | 3.15%            | 63.73%  | 32.35%  | 24.51%        |
| 2006     | 117  | 117  | 0.67%          | -1.73%           | 44.44%  | 29.91%  | 14.53%        | 117  | 0.38%          | 1.50%            | 58.12%  | 77.78%  | 17.09%        |
| 2007     | 119  | 119  | 2.51%          | 0.21%            | 51.26%  | 72.27%  | 5.88%         | 119  | 6.51%          | 6.31%            | 78.15%  | 50.42%  | 5.88%         |
| 2008     | 120  | 120  | 3.72%          | 2.62%            | 55.00%  | 76.67%  | 4.17%         | 120  | 4.52%          | 5.16%            | 72.50%  | 22.50%  | 11.67%        |
| 2009     | 114  | 114  | 0.38%          | -1.36%           | 45.61%  | 17.54%  | 3.51%         | 114  | 2.84%          | 1.92%            | 57.02%  | 1.75%   | 9.65%         |
| 2010     | 117  | 117  | 9.97%          | 6.97%            | 59.83%  | 17.09%  | 17.95%        | 117  | 2.95%          | 4.44%            | 60.68%  | 7.69%   | 28.21%        |
| 2011     | 115  | 115  | 6.59%          | 6.11%            | 57.39%  | 27.83%  | 7.83%         | 115  | 0.94%          | -0.48%           | 48.70%  | 6.09%   | 7.83%         |
| 2012     | 112  | 112  | -2.65%         | -5.57%           | 39.29%  | 18.75%  | 7.14%         | 112  | -1.73%         | -0.15%           | 49.11%  | 16.96%  | 7.14%         |
| 2013     | 119  | 119  | -0.61%         | -2.09%           | 46.22%  | 20.17%  | 2.52%         | 119  | 0.58%          | 1.83%            | 58.82%  | 19.33%  | 3.36%         |
| 2014     | 109  | 109  | 8.72%          | 12.38%           | 66.97%  | 26.61%  | 0.00%         | 109  | 2.90%          | 7.82%            | 63.30%  | 19.27%  | 9.17%         |
| 2015     | 116  | 116  | 3.38%          | 0.50%            | 51.72%  | 35.34%  | 4.31%         | 116  | -3.80%         | -2.82%           | 38.79%  | 24.14%  | 10.34%        |
| 2016     | 112  | 112  | -5.74%         | -5.24%           | 37.50%  | 23.21%  | 2.68%         | 112  | -1.93%         | 0.66%            | 52.68%  | 15.18%  | 8.04%         |
| 2017     | 111  | 111  | -1.49%         | -3.61%           | 45.95%  | 29.73%  | 5.41%         | 111  | -1.27%         | -0.10%           | 49.55%  | 27.03%  | 16.22%        |
| 2018     | 103  | 103  | 10.73%         | 6.87%            | 77.67%  | 14.56%  | 8.74%         | 103  | 1.92%          | 1.69%            | 58.25%  | 9.71%   | 11.65%        |
| 2019     | 108  | 108  | -6.66%         | -6.83%           | 36.11%  | 38.89%  | 2.78%         | 108  | -4.53%         | -5.50%           | 27.78%  | 20.37%  | 2.78%         |
| 2020     | 89   | 89   | -23.59%        | -23.65%          | 14.61%  | 37.08%  | 0.00%         | 89   | -7.39%         | -6.35%           | 25.84%  | 33.71%  | 6.74%         |
| all buys | 1783 | 1783 | 1.12%          | -0.31%           | 49.47%  | 32.47%  | 6.28%         | 1783 | 0.51%          | 1.27%            | 54.46%  | 24.06%  | 11.27%        |

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

- backtest configurations tried against dataset `1.4`: 13 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_top10_cap2_4ff2378d07eb9919_equity.png`
