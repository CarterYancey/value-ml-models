# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_s1776

- run `8de2b1d8d736`, git `ba55f7d9adc1654cdb466dee924ac976e3f9a828`, backtest config `9c488a62e67ca352`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 949,365.58  | 757,365.58 | 13.80%         | 12.23%   | -41.98%      | 1,170.55   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 8.77%        | 6.51%         | 2.26%  | 12,000.00 | 108    | -341.5278       |
| 2006              | 8.85%        | 12.67%        | -3.81% | 12,000.00 | 120    | -375.1194       |
| 2007              | 2.52%        | 7.28%         | -4.76% | 12,000.00 | 117    | -334.6211       |
| 2008 (GFC)        | -33.89%      | -43.21%       | 9.32%  | 12,000.00 | 120    | -286.2361       |
| 2009 (GFC)        | 42.49%       | 39.07%        | 3.42%  | 12,000.00 | 115    | -192.0841       |
| 2010              | 28.48%       | 10.86%        | 17.63% | 12,000.00 | 120    | -366.8361       |
| 2011              | 9.89%        | 5.33%         | 4.56%  | 12,000.00 | 109    | -290.0275       |
| 2012              | 15.86%       | 15.60%        | 0.26%  | 12,000.00 | 108    | -193.6358       |
| 2013              | 36.88%       | 30.42%        | 6.46%  | 12,000.00 | 114    | -263.0760       |
| 2014              | 12.85%       | 16.18%        | -3.33% | 12,000.00 | 110    | -298.8303       |
| 2015              | 13.04%       | 4.46%         | 8.57%  | 12,000.00 | 106    | -204.5755       |
| 2016              | 4.29%        | 6.48%         | -2.19% | 12,000.00 | 110    | -188.3182       |
| 2017              | 22.85%       | 22.88%        | -0.02% | 12,000.00 | 103    | -295.6990       |
| 2018              | 10.05%       | 7.53%         | 2.52%  | 12,000.00 | 96     | -263.0347       |
| 2019              | 22.04%       | 13.81%        | 8.23%  | 12,000.00 | 106    | -222.7799       |
| 2020 (COVID)      | 22.47%       | 19.77%        | 2.70%  | 12,000.00 | 86     | -207.2636       |
| 2021              | 16.52%       | 24.81%        | -8.29% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -4.89%       | -8.20%        | 3.31%  | 0.00      | 0      | —               |
| 2023              | 17.11%       | 19.00%        | -1.89% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 307  | 17.56% |
| Healthcare             | 284  | 16.25% |
| Industrials            | 274  | 15.68% |
| Technology             | 268  | 15.33% |
| Consumer Cyclical      | 261  | 14.93% |
| Basic Materials        | 121  | 6.92%  |
| Communication Services | 95   | 5.43%  |
| Financial Services     | 68   | 3.89%  |
| Energy                 | 42   | 2.40%  |
| Real Estate            | 19   | 1.09%  |
| Utilities              | 9    | 0.51%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 24     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 31     | 8      | Healthcare         | 20.00%        |
| 2007 | 117  | 32     | 9      | Consumer Defensive | 17.95%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 115  | 32     | 10     | Healthcare         | 20.87%        |
| 2010 | 120  | 31     | 8      | Consumer Defensive | 17.50%        |
| 2011 | 109  | 29     | 9      | Consumer Defensive | 19.27%        |
| 2012 | 108  | 30     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 114  | 30     | 8      | Healthcare         | 18.42%        |
| 2014 | 110  | 25     | 7      | Technology         | 21.82%        |
| 2015 | 106  | 26     | 8      | Consumer Defensive | 19.81%        |
| 2016 | 110  | 28     | 7      | Consumer Defensive | 21.82%        |
| 2017 | 103  | 28     | 9      | Technology         | 20.39%        |
| 2018 | 96   | 24     | 8      | Consumer Cyclical  | 25.00%        |
| 2019 | 106  | 26     | 6      | Consumer Defensive | 22.64%        |
| 2020 | 86   | 28     | 8      | Technology         | 23.26%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -1.93%         | -4.86%           | 38.89%  | 35.19%  | 2.78%         | 108  | -3.71%         | 0.65%            | 58.33%  | 37.96%  | 11.11%        |
| 2006     | 120  | 120  | -11.69%        | -11.95%          | 28.33%  | 44.17%  | 5.00%         | 120  | 0.79%          | 1.97%            | 60.00%  | 78.33%  | 7.50%         |
| 2007     | 117  | 117  | 4.01%          | 4.66%            | 63.25%  | 60.68%  | 1.71%         | 117  | 7.56%          | 7.35%            | 77.78%  | 45.30%  | 11.97%        |
| 2008     | 120  | 120  | 9.53%          | 11.35%           | 66.67%  | 77.50%  | 0.83%         | 120  | 7.88%          | 8.08%            | 86.67%  | 10.00%  | 3.33%         |
| 2009     | 115  | 115  | 5.37%          | 5.09%            | 57.39%  | 12.17%  | 6.96%         | 115  | -0.27%         | -0.26%           | 46.96%  | 6.09%   | 11.30%        |
| 2010     | 120  | 120  | 25.67%         | 18.01%           | 75.00%  | 7.50%   | 4.17%         | 120  | 8.59%          | 7.50%            | 78.33%  | 1.67%   | 6.67%         |
| 2011     | 109  | 109  | 13.10%         | 11.97%           | 68.81%  | 17.43%  | 5.50%         | 109  | 6.06%          | 5.45%            | 74.31%  | 6.42%   | 5.50%         |
| 2012     | 108  | 108  | -0.57%         | -0.72%           | 49.07%  | 14.81%  | 0.00%         | 108  | 0.05%          | 4.49%            | 57.41%  | 17.59%  | 0.93%         |
| 2013     | 114  | 114  | 1.02%          | -0.73%           | 46.49%  | 11.40%  | 2.63%         | 114  | 2.71%          | 4.08%            | 65.79%  | 15.79%  | 5.26%         |
| 2014     | 110  | 110  | 13.75%         | 17.88%           | 74.55%  | 17.27%  | 0.00%         | 110  | 3.72%          | 3.33%            | 58.18%  | 13.64%  | 6.36%         |
| 2015     | 106  | 106  | 4.72%          | 2.93%            | 58.49%  | 30.19%  | 0.00%         | 106  | 2.54%          | 5.47%            | 66.98%  | 16.04%  | 2.83%         |
| 2016     | 110  | 110  | -0.09%         | -2.46%           | 44.55%  | 10.91%  | 2.73%         | 110  | 2.64%          | 5.45%            | 70.00%  | 17.27%  | 8.18%         |
| 2017     | 103  | 103  | -0.05%         | -3.29%           | 43.69%  | 25.24%  | 4.85%         | 103  | 2.27%          | 0.30%            | 53.40%  | 19.42%  | 15.53%        |
| 2018     | 96   | 96   | 8.76%          | 6.22%            | 69.79%  | 22.92%  | 0.00%         | 96   | 3.86%          | 0.08%            | 51.04%  | 4.17%   | 9.38%         |
| 2019     | 106  | 106  | -3.93%         | -7.44%           | 39.62%  | 37.74%  | 0.00%         | 106  | -5.62%         | -5.76%           | 18.87%  | 12.26%  | 0.00%         |
| 2020     | 86   | 86   | -14.62%        | -22.38%          | 33.72%  | 31.40%  | 0.00%         | 86   | -2.77%         | -5.17%           | 37.21%  | 29.07%  | 10.47%        |
| all buys | 1748 | 1748 | 3.63%          | 2.26%            | 53.95%  | 28.83%  | 2.40%         | 1748 | 2.42%          | 3.16%            | 60.87%  | 20.94%  | 7.21%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 110
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 66 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 20 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s1776_9c488a62e67ca352_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s1776_9c488a62e67ca352_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s1776_9c488a62e67ca352_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s1776_9c488a62e67ca352_equity.png`
