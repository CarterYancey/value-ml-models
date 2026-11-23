# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor

- run `8a67e6f8ca6c`, git `f96037d3f0ef0806e1bd64eae36d7400aea2289c`, backtest config `6005c9c0a2869bc9`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 965,380.01  | 773,380.01 | 13.94%         | 12.15%   | -41.42%      | 1,214.51   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 3.71%        | 6.51%         | -2.81% | 12,000.00 | 108    | -365.6883       |
| 2006              | 10.23%       | 12.67%        | -2.44% | 12,000.00 | 120    | -383.1056       |
| 2007              | 2.70%        | 7.28%         | -4.58% | 12,000.00 | 116    | -342.9483       |
| 2008 (GFC)        | -33.30%      | -43.21%       | 9.91%  | 12,000.00 | 120    | -299.0500       |
| 2009 (GFC)        | 41.18%       | 39.07%        | 2.11%  | 12,000.00 | 115    | -209.9565       |
| 2010              | 28.11%       | 10.86%        | 17.25% | 12,000.00 | 120    | -383.7250       |
| 2011              | 11.68%       | 5.33%         | 6.36%  | 12,000.00 | 109    | -298.4709       |
| 2012              | 16.22%       | 15.60%        | 0.62%  | 12,000.00 | 108    | -196.1204       |
| 2013              | 36.17%       | 30.42%        | 5.75%  | 12,000.00 | 114    | -263.0409       |
| 2014              | 12.37%       | 16.18%        | -3.82% | 12,000.00 | 110    | -293.9697       |
| 2015              | 12.84%       | 4.46%         | 8.37%  | 12,000.00 | 106    | -199.8491       |
| 2016              | 5.44%        | 6.48%         | -1.04% | 12,000.00 | 109    | -187.2875       |
| 2017              | 22.94%       | 22.88%        | 0.06%  | 12,000.00 | 106    | -287.5535       |
| 2018              | 9.10%        | 7.53%         | 1.56%  | 12,000.00 | 96     | -253.0486       |
| 2019              | 23.53%       | 13.81%        | 9.72%  | 12,000.00 | 103    | -216.6828       |
| 2020 (COVID)      | 21.43%       | 19.77%        | 1.66%  | 12,000.00 | 87     | -203.1992       |
| 2021              | 15.60%       | 24.81%        | -9.21% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -3.82%       | -8.20%        | 4.38%  | 0.00      | 0      | —               |
| 2023              | 17.77%       | 19.00%        | -1.23% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 299  | 17.12% |
| Industrials            | 290  | 16.60% |
| Technology             | 272  | 15.57% |
| Healthcare             | 271  | 15.51% |
| Consumer Cyclical      | 257  | 14.71% |
| Basic Materials        | 134  | 7.67%  |
| Communication Services | 93   | 5.32%  |
| Financial Services     | 70   | 4.01%  |
| Energy                 | 36   | 2.06%  |
| Real Estate            | 16   | 0.92%  |
| Utilities              | 9    | 0.52%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 23     | 9      | Industrials            | 19.44%        |
| 2006 | 120  | 31     | 7      | Consumer Cyclical      | 20.00%        |
| 2007 | 116  | 31     | 8      | Consumer Defensive     | 18.10%        |
| 2008 | 120  | 29     | 7      | Healthcare             | 20.00%        |
| 2009 | 115  | 32     | 10     | Healthcare             | 20.87%        |
| 2010 | 120  | 27     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive     | 22.02%        |
| 2012 | 108  | 29     | 8      | Consumer Defensive     | 22.22%        |
| 2013 | 114  | 31     | 8      | Communication Services | 21.05%        |
| 2014 | 110  | 28     | 7      | Technology             | 21.82%        |
| 2015 | 106  | 24     | 8      | Technology             | 19.81%        |
| 2016 | 109  | 27     | 8      | Consumer Defensive     | 22.02%        |
| 2017 | 106  | 28     | 9      | Industrials            | 21.70%        |
| 2018 | 96   | 26     | 8      | Consumer Cyclical      | 25.00%        |
| 2019 | 103  | 27     | 7      | Consumer Defensive     | 23.30%        |
| 2020 | 87   | 27     | 8      | Technology             | 22.99%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.31%         | -6.71%           | 34.26%  | 37.96%  | 0.00%         | 108  | -5.57%         | 0.25%            | 51.85%  | 40.74%  | 11.11%        |
| 2006     | 120  | 120  | -11.46%        | -11.95%          | 25.83%  | 43.33%  | 5.00%         | 120  | 1.39%          | 2.19%            | 60.83%  | 73.33%  | 6.67%         |
| 2007     | 116  | 116  | 5.53%          | 5.33%            | 65.52%  | 57.76%  | 1.72%         | 116  | 7.55%          | 7.74%            | 79.31%  | 42.24%  | 12.07%        |
| 2008     | 120  | 120  | 9.78%          | 11.35%           | 65.83%  | 76.67%  | 0.83%         | 120  | 7.82%          | 7.91%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 115  | 115  | 5.58%          | 6.19%            | 57.39%  | 13.04%  | 6.96%         | 115  | -0.76%         | -0.35%           | 46.09%  | 8.70%   | 11.30%        |
| 2010     | 120  | 120  | 22.93%         | 18.01%           | 74.17%  | 8.33%   | 1.67%         | 120  | 10.58%         | 9.75%            | 79.17%  | 1.67%   | 5.00%         |
| 2011     | 109  | 109  | 10.53%         | 10.58%           | 67.89%  | 19.27%  | 5.50%         | 109  | 5.20%          | 4.42%            | 71.56%  | 6.42%   | 8.26%         |
| 2012     | 108  | 108  | -0.85%         | -2.64%           | 46.30%  | 15.74%  | 0.00%         | 108  | 0.51%          | 4.49%            | 57.41%  | 14.81%  | 0.93%         |
| 2013     | 114  | 114  | -0.44%         | -0.83%           | 45.61%  | 14.04%  | 2.63%         | 114  | 2.47%          | 3.95%            | 64.91%  | 17.54%  | 5.26%         |
| 2014     | 110  | 110  | 12.37%         | 16.05%           | 73.64%  | 16.36%  | 1.82%         | 110  | 3.49%          | 3.30%            | 57.27%  | 16.36%  | 8.18%         |
| 2015     | 106  | 106  | 6.48%          | 4.31%            | 64.15%  | 24.53%  | 0.00%         | 106  | 4.20%          | 6.29%            | 71.70%  | 12.26%  | 2.83%         |
| 2016     | 109  | 109  | -2.46%         | -4.04%           | 38.53%  | 12.84%  | 2.75%         | 109  | 1.74%          | 4.70%            | 62.39%  | 17.43%  | 5.50%         |
| 2017     | 106  | 106  | 0.70%          | -2.85%           | 45.28%  | 25.47%  | 4.72%         | 106  | 1.41%          | 0.17%            | 50.94%  | 20.75%  | 14.15%        |
| 2018     | 96   | 96   | 11.66%         | 6.80%            | 73.96%  | 18.75%  | 0.00%         | 96   | 4.77%          | 2.86%            | 55.21%  | 4.17%   | 7.29%         |
| 2019     | 103  | 103  | -3.07%         | -5.13%           | 42.72%  | 36.89%  | 0.00%         | 103  | -4.78%         | -5.93%           | 20.39%  | 12.62%  | 0.00%         |
| 2020     | 87   | 87   | -13.42%        | -16.50%          | 34.48%  | 29.89%  | 0.00%         | 87   | -1.59%         | -1.32%           | 43.68%  | 25.29%  | 10.34%        |
| all buys | 1747 | 1747 | 3.42%          | 2.22%            | 53.69%  | 28.51%  | 2.18%         | 1747 | 2.55%          | 3.37%            | 60.73%  | 20.49%  | 6.98%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 109
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3236.9 (min 2923)
- mean with a tradable quote: 3159.8 (min 2870)
- forced delisting liquidations: 68 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 27 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_6005c9c0a2869bc9_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_6005c9c0a2869bc9_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_6005c9c0a2869bc9_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_6005c9c0a2869bc9_equity.png`
