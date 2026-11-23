# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_mcap

- run `b39a2adfbdeb`, git `295d71b84d154c875a993defd3f9571d934ea0a1`, backtest config `8cc854eea82f9453`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 1,108,043.90 | 916,043.90 | 15.09%         | 13.82%   | -37.03%      | 1,096.42   |
| benchmark | 192,000.00 | 732,110.07   | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 12.69%       | 6.51%         | 6.18%   | 12,000.00 | 61     | -350            |
| 2006              | 18.13%       | 12.67%        | 5.46%   | 12,000.00 | 80     | -371.0542       |
| 2007              | 5.46%        | 7.28%         | -1.82%  | 12,000.00 | 77     | -329.8571       |
| 2008 (GFC)        | -31.59%      | -43.21%       | 11.62%  | 12,000.00 | 63     | -287.1746       |
| 2009 (GFC)        | 40.39%       | 39.07%        | 1.32%   | 12,000.00 | 85     | -185.0667       |
| 2010              | 18.48%       | 10.86%        | 7.62%   | 12,000.00 | 49     | -377.7415       |
| 2011              | 18.62%       | 5.33%         | 13.29%  | 12,000.00 | 64     | -294.9792       |
| 2012              | 19.60%       | 15.60%        | 4.00%   | 12,000.00 | 41     | -175.8780       |
| 2013              | 19.59%       | 30.42%        | -10.83% | 12,000.00 | 67     | -254.6070       |
| 2014              | 23.16%       | 16.18%        | 6.97%   | 12,000.00 | 85     | -298.4706       |
| 2015              | 7.95%        | 4.46%         | 3.48%   | 12,000.00 | 63     | -193.2116       |
| 2016              | 6.37%        | 6.48%         | -0.10%  | 12,000.00 | 60     | -176.1889       |
| 2017              | 25.02%       | 22.88%        | 2.14%   | 12,000.00 | 55     | -303.0364       |
| 2018              | 4.36%        | 7.53%         | -3.17%  | 12,000.00 | 60     | -256.3611       |
| 2019              | 24.71%       | 13.81%        | 10.90%  | 12,000.00 | 56     | -224.0179       |
| 2020 (COVID)      | 30.76%       | 19.77%        | 11.00%  | 12,000.00 | 34     | -212.9412       |
| 2021              | 23.32%       | 24.81%        | -1.50%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 0.12%        | -8.20%        | 8.31%   | 0.00      | 0      | —               |
| 2023              | 16.02%       | 19.00%        | -2.98%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `marketcap`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 234  | 23.40% |
| Industrials            | 182  | 18.20% |
| Technology             | 151  | 15.10% |
| Healthcare             | 137  | 13.70% |
| Consumer Cyclical      | 109  | 10.90% |
| Communication Services | 62   | 6.20%  |
| Financial Services     | 50   | 5.00%  |
| Basic Materials        | 43   | 4.30%  |
| Energy                 | 13   | 1.30%  |
| Real Estate            | 12   | 1.20%  |
| Utilities              | 7    | 0.70%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 61   | 19     | 8      | Industrials            | 29.51%        |
| 2006 | 80   | 21     | 7      | Healthcare             | 22.50%        |
| 2007 | 77   | 21     | 8      | Consumer Defensive     | 24.68%        |
| 2008 | 63   | 16     | 7      | Consumer Defensive     | 38.10%        |
| 2009 | 85   | 27     | 10     | Consumer Defensive     | 24.71%        |
| 2010 | 49   | 12     | 7      | Technology             | 24.49%        |
| 2011 | 64   | 18     | 8      | Consumer Defensive     | 28.12%        |
| 2012 | 41   | 10     | 5      | Technology             | 29.27%        |
| 2013 | 67   | 21     | 8      | Communication Services | 22.39%        |
| 2014 | 85   | 19     | 7      | Industrials            | 24.71%        |
| 2015 | 63   | 13     | 6      | Consumer Defensive     | 28.57%        |
| 2016 | 60   | 15     | 6      | Consumer Defensive     | 40.00%        |
| 2017 | 55   | 18     | 8      | Technology             | 29.09%        |
| 2018 | 60   | 17     | 8      | Industrials            | 25.00%        |
| 2019 | 56   | 19     | 7      | Consumer Cyclical      | 25.00%        |
| 2020 | 34   | 12     | 8      | Technology             | 26.47%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 61   | 61   | 3.72%          | 1.86%            | 52.46%  | 24.59%  | 0.00%         | 61   | -3.97%         | 0.08%            | 50.82%  | 37.70%  | 3.28%         |
| 2006     | 80   | 80   | -9.87%         | -11.73%          | 26.25%  | 41.25%  | 0.00%         | 80   | 2.58%          | 2.68%            | 67.50%  | 72.50%  | 0.00%         |
| 2007     | 77   | 77   | 7.07%          | 5.96%            | 68.83%  | 61.04%  | 0.00%         | 77   | 8.46%          | 7.35%            | 83.12%  | 45.45%  | 9.09%         |
| 2008     | 63   | 63   | 8.22%          | 11.20%           | 65.08%  | 77.78%  | 0.00%         | 63   | 7.12%          | 6.99%            | 88.89%  | 9.52%   | 0.00%         |
| 2009     | 85   | 85   | 6.97%          | 7.32%            | 61.18%  | 12.94%  | 7.06%         | 85   | 0.55%          | -0.79%           | 43.53%  | 4.71%   | 10.59%        |
| 2010     | 49   | 49   | 26.45%         | 17.74%           | 81.63%  | 2.04%   | 0.00%         | 49   | 7.57%          | 7.10%            | 75.51%  | 4.08%   | 0.00%         |
| 2011     | 64   | 64   | 15.60%         | 12.48%           | 75.00%  | 14.06%  | 0.00%         | 64   | 6.48%          | 4.62%            | 79.69%  | 0.00%   | 4.69%         |
| 2012     | 41   | 41   | -8.32%         | -9.91%           | 36.59%  | 21.95%  | 0.00%         | 41   | -0.51%         | 2.31%            | 53.66%  | 12.20%  | 0.00%         |
| 2013     | 67   | 67   | 0.74%          | 0.86%            | 52.24%  | 13.43%  | 4.48%         | 67   | 1.93%          | 3.85%            | 70.15%  | 17.91%  | 4.48%         |
| 2014     | 85   | 85   | 13.91%         | 16.30%           | 80.00%  | 14.12%  | 5.88%         | 85   | 1.35%          | 3.83%            | 58.82%  | 18.82%  | 12.94%        |
| 2015     | 63   | 63   | 8.43%          | 5.73%            | 69.84%  | 19.05%  | 0.00%         | 63   | 1.64%          | 4.79%            | 69.84%  | 15.87%  | 4.76%         |
| 2016     | 60   | 60   | -7.27%         | -5.53%           | 33.33%  | 18.33%  | 0.00%         | 60   | -3.36%         | 0.11%            | 50.00%  | 26.67%  | 5.00%         |
| 2017     | 55   | 55   | 3.45%          | 3.20%            | 56.36%  | 16.36%  | 1.82%         | 55   | 4.50%          | 0.55%            | 54.55%  | 16.36%  | 5.45%         |
| 2018     | 60   | 60   | 16.33%         | 18.07%           | 75.00%  | 16.67%  | 0.00%         | 60   | 0.48%          | -0.66%           | 48.33%  | 13.33%  | 5.00%         |
| 2019     | 56   | 56   | -1.75%         | -3.51%           | 42.86%  | 33.93%  | 0.00%         | 56   | -0.83%         | -3.25%           | 30.36%  | 1.79%   | 0.00%         |
| 2020     | 34   | 34   | -0.01%         | -2.40%           | 44.12%  | 2.94%   | 0.00%         | 34   | 1.39%          | 2.62%            | 61.76%  | 11.76%  | 8.82%         |
| all buys | 1000 | 1000 | 5.44%          | 4.42%            | 58.40%  | 25.70%  | 1.50%         | 1000 | 2.30%          | 2.97%            | 62.00%  | 20.90%  | 5.00%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 189
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 36 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 30 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_8cc854eea82f9453_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_8cc854eea82f9453_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_8cc854eea82f9453_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_8cc854eea82f9453_equity.png`
