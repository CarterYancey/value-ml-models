# Portfolio backtest — bt_nonloser_mom_top10_cap2_sell20

- run `f4bc1906dfdd`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `7d919d3c1942b957`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 674,816.74  | 482,816.74 | 10.93%         | 9.87%    | -51.66%      | 13,540.78  |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 15.53%       | 6.51%         | 9.01%   | 12,000.00 | 102    | -314.0784       |
| 2006              | 17.90%       | 12.67%        | 5.23%   | 12,000.00 | 118    | -374.2458       |
| 2007              | -0.79%       | 7.28%         | -8.08%  | 12,000.00 | 120    | -293.4292       |
| 2008 (GFC)        | -41.39%      | -43.21%       | 1.82%   | 12,000.00 | 120    | -249.3625       |
| 2009 (GFC)        | 22.47%       | 39.07%        | -16.60% | 12,000.00 | 117    | -132.4487       |
| 2010              | 25.04%       | 10.86%        | 14.18%  | 12,000.00 | 118    | -380.1568       |
| 2011              | 22.33%       | 5.33%         | 17.00%  | 12,000.00 | 116    | -314.8060       |
| 2012              | 9.97%        | 15.60%        | -5.63%  | 12,000.00 | 115    | -169.5696       |
| 2013              | 29.25%       | 30.42%        | -1.17%  | 12,000.00 | 120    | -258.2417       |
| 2014              | 18.63%       | 16.18%        | 2.45%   | 12,000.00 | 112    | -326.7098       |
| 2015              | 13.33%       | 4.46%         | 8.86%   | 12,000.00 | 115    | -217.1609       |
| 2016              | 3.19%        | 6.48%         | -3.29%  | 12,000.00 | 109    | -164.7339       |
| 2017              | 27.38%       | 22.88%        | 4.50%   | 12,000.00 | 109    | -298.7890       |
| 2018              | 6.99%        | 7.53%         | -0.55%  | 12,000.00 | 109    | -293.7798       |
| 2019              | 14.90%       | 13.81%        | 1.09%   | 12,000.00 | 106    | -210.0755       |
| 2020 (COVID)      | 9.79%        | 19.77%        | -9.98%  | 12,000.00 | 100    | -208.7150       |
| 2021              | 12.76%       | 24.81%        | -12.06% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -5.49%       | -8.20%        | 2.70%   | 0.00      | 0      | —               |
| 2023              | 11.37%       | 19.00%        | -7.63%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 2 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `equal`-weighted; strategy `sell_below_criteria`; at most 2 of a rebalance's buys per `sector`, walked in score order
- sell discipline (`sell_below_criteria`): a held position failing the sell criteria at a rebalance is sold entirely (proceeds fund that month's buys); falling out of the top 10 alone is never a sell. A holding whose snapshot has aged out of the cross-section fails the criteria.
- sell floors (inherited from buy): (none)
- sell filters: (none)
- sell rank: a held position is sold once it is no longer among the top 20% of the month's buy candidates by combined score (after every buy screen), or is not a candidate at all
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 253  | 14.01% |
| Consumer Cyclical      | 237  | 13.12% |
| Industrials            | 224  | 12.40% |
| Real Estate            | 192  | 10.63% |
| Healthcare             | 186  | 10.30% |
| Utilities              | 180  | 9.97%  |
| Energy                 | 178  | 9.86%  |
| Basic Materials        | 133  | 7.36%  |
| Technology             | 114  | 6.31%  |
| Communication Services | 84   | 4.65%  |
| Financial Services     | 25   | 1.38%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 102  | 29     | 9      | Real Estate        | 23.53%        |
| 2006 | 118  | 37     | 11     | Real Estate        | 17.80%        |
| 2007 | 120  | 37     | 10     | Energy             | 17.50%        |
| 2008 | 120  | 33     | 9      | Industrials        | 17.50%        |
| 2009 | 117  | 33     | 9      | Consumer Defensive | 20.51%        |
| 2010 | 118  | 33     | 8      | Energy             | 20.34%        |
| 2011 | 116  | 33     | 8      | Healthcare         | 18.10%        |
| 2012 | 115  | 32     | 10     | Consumer Defensive | 20.87%        |
| 2013 | 120  | 35     | 9      | Consumer Cyclical  | 17.50%        |
| 2014 | 112  | 28     | 9      | Industrials        | 18.75%        |
| 2015 | 115  | 29     | 11     | Consumer Defensive | 20.87%        |
| 2016 | 109  | 34     | 7      | Consumer Defensive | 19.27%        |
| 2017 | 109  | 38     | 8      | Industrials        | 20.18%        |
| 2018 | 109  | 30     | 11     | Industrials        | 19.27%        |
| 2019 | 106  | 34     | 9      | Utilities          | 16.98%        |
| 2020 | 100  | 36     | 10     | Consumer Defensive | 21.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 102  | 102  | 7.45%          | 2.89%            | 56.86%  | 29.41%  | 11.76%        | 102  | 3.25%          | 3.15%            | 63.73%  | 32.35%  | 24.51%        |
| 2006     | 118  | 118  | 0.41%          | -1.91%           | 44.07%  | 30.51%  | 14.41%        | 118  | -0.09%         | 1.49%            | 57.63%  | 77.97%  | 16.95%        |
| 2007     | 120  | 120  | 2.50%          | 0.33%            | 51.67%  | 72.50%  | 5.83%         | 120  | 6.39%          | 6.19%            | 77.50%  | 50.83%  | 5.83%         |
| 2008     | 120  | 120  | 3.72%          | 2.62%            | 55.00%  | 76.67%  | 4.17%         | 120  | 4.52%          | 5.16%            | 72.50%  | 22.50%  | 11.67%        |
| 2009     | 117  | 117  | 1.36%          | -1.02%           | 47.01%  | 17.09%  | 3.42%         | 117  | 3.35%          | 2.92%            | 58.12%  | 1.71%   | 9.40%         |
| 2010     | 118  | 118  | 9.87%          | 6.80%            | 59.32%  | 16.95%  | 17.80%        | 118  | 2.97%          | 4.40%            | 61.02%  | 7.63%   | 27.97%        |
| 2011     | 116  | 116  | 6.68%          | 4.86%            | 56.90%  | 27.59%  | 7.76%         | 116  | 1.00%          | -0.31%           | 49.14%  | 6.03%   | 7.76%         |
| 2012     | 115  | 115  | -2.04%         | -5.31%           | 40.00%  | 18.26%  | 7.83%         | 115  | -2.03%         | -0.14%           | 49.57%  | 17.39%  | 7.83%         |
| 2013     | 120  | 120  | -0.15%         | -1.99%           | 46.67%  | 20.00%  | 2.50%         | 120  | 0.70%          | 2.05%            | 59.17%  | 19.17%  | 3.33%         |
| 2014     | 112  | 112  | 9.66%          | 13.59%           | 68.75%  | 25.00%  | 0.00%         | 112  | 3.15%          | 7.15%            | 64.29%  | 17.86%  | 9.82%         |
| 2015     | 115  | 115  | 3.46%          | 0.33%            | 51.30%  | 35.65%  | 4.35%         | 115  | -3.85%         | -3.02%           | 39.13%  | 24.35%  | 10.43%        |
| 2016     | 109  | 109  | -5.87%         | -5.59%           | 35.78%  | 22.94%  | 2.75%         | 109  | -2.15%         | 0.65%            | 52.29%  | 16.51%  | 8.26%         |
| 2017     | 109  | 109  | -1.88%         | -3.61%           | 44.95%  | 30.28%  | 6.42%         | 109  | -1.90%         | -0.16%           | 48.62%  | 28.44%  | 17.43%        |
| 2018     | 109  | 109  | 10.94%         | 7.15%            | 77.06%  | 15.60%  | 8.26%         | 109  | 1.90%          | 2.38%            | 60.55%  | 11.01%  | 11.01%        |
| 2019     | 106  | 106  | -6.61%         | -6.83%           | 35.85%  | 39.62%  | 2.83%         | 106  | -4.15%         | -5.30%           | 30.19%  | 19.81%  | 2.83%         |
| 2020     | 100  | 100  | -23.46%        | -25.28%          | 14.00%  | 34.00%  | 0.00%         | 100  | -8.32%         | -6.47%           | 26.00%  | 35.00%  | 6.00%         |
| all buys | 1806 | 1806 | 1.21%          | -0.36%           | 49.34%  | 32.23%  | 6.31%         | 1806 | 0.41%          | 1.31%            | 54.76%  | 24.31%  | 11.30%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 68
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 413 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 7 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 18 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_top10_cap2_sell20_7d919d3c1942b957_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_top10_cap2_sell20_7d919d3c1942b957_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_top10_cap2_sell20_7d919d3c1942b957_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_top10_cap2_sell20_7d919d3c1942b957_equity.png`
