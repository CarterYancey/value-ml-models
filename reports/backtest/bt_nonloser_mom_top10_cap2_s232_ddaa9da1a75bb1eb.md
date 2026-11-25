# Portfolio backtest — bt_nonloser_mom_top10_cap2_s232

- run `67bc737af73a`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `ddaa9da1a75bb1eb`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 764,061.68  | 572,061.68 | 11.98%         | 11.73%   | -46.73%      | 1,584.53   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 19.83%       | 6.51%         | 13.32%  | 12,000.00 | 108    | -317.7963       |
| 2006              | 19.83%       | 12.67%        | 7.16%   | 12,000.00 | 116    | -371.2198       |
| 2007              | 7.62%        | 7.28%         | 0.34%   | 12,000.00 | 119    | -295.8529       |
| 2008 (GFC)        | -40.47%      | -43.21%       | 2.74%   | 12,000.00 | 119    | -254.7479       |
| 2009 (GFC)        | 46.77%       | 39.07%        | 7.70%   | 12,000.00 | 114    | -130.5658       |
| 2010              | 28.91%       | 10.86%        | 18.05%  | 12,000.00 | 117    | -380.5812       |
| 2011              | 11.89%       | 5.33%         | 6.57%   | 12,000.00 | 115    | -314.6174       |
| 2012              | 10.10%       | 15.60%        | -5.50%  | 12,000.00 | 109    | -169.9358       |
| 2013              | 29.45%       | 30.42%        | -0.97%  | 12,000.00 | 120    | -258.7542       |
| 2014              | 15.42%       | 16.18%        | -0.77%  | 12,000.00 | 106    | -325.2689       |
| 2015              | 1.44%        | 4.46%         | -3.02%  | 12,000.00 | 116    | -216.7500       |
| 2016              | 10.36%       | 6.48%         | 3.88%   | 12,000.00 | 115    | -166.8652       |
| 2017              | 19.06%       | 22.88%        | -3.82%  | 12,000.00 | 111    | -302.0315       |
| 2018              | 10.87%       | 7.53%         | 3.33%   | 12,000.00 | 101    | -295.0941       |
| 2019              | 17.14%       | 13.81%        | 3.33%   | 12,000.00 | 109    | -210.3716       |
| 2020 (COVID)      | 11.36%       | 19.77%        | -8.41%  | 12,000.00 | 88     | -206.9261       |
| 2021              | 20.46%       | 24.81%        | -4.35%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 8.39%        | -8.20%        | 16.59%  | 0.00      | 0      | —               |
| 2023              | 1.90%        | 19.00%        | -17.10% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 253  | 14.19% |
| Industrials            | 230  | 12.90% |
| Consumer Cyclical      | 216  | 12.11% |
| Real Estate            | 199  | 11.16% |
| Utilities              | 190  | 10.66% |
| Energy                 | 173  | 9.70%  |
| Healthcare             | 171  | 9.59%  |
| Basic Materials        | 135  | 7.57%  |
| Technology             | 113  | 6.34%  |
| Communication Services | 81   | 4.54%  |
| Financial Services     | 22   | 1.23%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 25     | 8      | Real Estate        | 22.22%        |
| 2006 | 116  | 34     | 11     | Real Estate        | 18.10%        |
| 2007 | 119  | 34     | 10     | Utilities          | 17.65%        |
| 2008 | 119  | 36     | 9      | Utilities          | 17.65%        |
| 2009 | 114  | 31     | 8      | Utilities          | 21.05%        |
| 2010 | 117  | 29     | 8      | Energy             | 20.51%        |
| 2011 | 115  | 32     | 8      | Healthcare         | 18.26%        |
| 2012 | 109  | 30     | 11     | Consumer Defensive | 22.02%        |
| 2013 | 120  | 33     | 9      | Consumer Cyclical  | 17.50%        |
| 2014 | 106  | 26     | 8      | Healthcare         | 19.81%        |
| 2015 | 116  | 29     | 11     | Consumer Defensive | 20.69%        |
| 2016 | 115  | 31     | 7      | Real Estate        | 20.87%        |
| 2017 | 111  | 36     | 8      | Consumer Cyclical  | 19.82%        |
| 2018 | 101  | 29     | 10     | Consumer Cyclical  | 17.82%        |
| 2019 | 109  | 35     | 9      | Industrials        | 16.51%        |
| 2020 | 88   | 29     | 9      | Consumer Defensive | 22.73%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | 9.16%          | 4.44%            | 59.26%  | 27.78%  | 13.89%        | 108  | 3.33%          | 3.23%            | 63.89%  | 32.41%  | 25.93%        |
| 2006     | 116  | 116  | -0.19%         | -4.07%           | 43.97%  | 31.03%  | 14.66%        | 116  | 0.87%          | 2.19%            | 59.48%  | 79.31%  | 17.24%        |
| 2007     | 119  | 119  | 4.81%          | 1.26%            | 53.78%  | 68.07%  | 3.36%         | 119  | 7.57%          | 6.34%            | 81.51%  | 50.42%  | 3.36%         |
| 2008     | 119  | 119  | 3.46%          | 2.88%            | 56.30%  | 76.47%  | 4.20%         | 119  | 3.90%          | 4.35%            | 70.59%  | 26.05%  | 11.76%        |
| 2009     | 114  | 114  | 0.17%          | -2.28%           | 42.98%  | 17.54%  | 2.63%         | 114  | 2.24%          | 1.46%            | 55.26%  | 1.75%   | 6.14%         |
| 2010     | 117  | 117  | 14.27%         | 13.99%           | 64.10%  | 14.53%  | 18.80%        | 117  | 3.41%          | 5.60%            | 61.54%  | 10.26%  | 31.62%        |
| 2011     | 115  | 115  | 7.19%          | 6.86%            | 58.26%  | 30.43%  | 5.22%         | 115  | 2.48%          | 1.56%            | 53.91%  | 6.09%   | 5.22%         |
| 2012     | 109  | 109  | -3.52%         | -5.31%           | 38.53%  | 19.27%  | 7.34%         | 109  | -1.53%         | -0.14%           | 49.54%  | 18.35%  | 7.34%         |
| 2013     | 120  | 120  | -2.56%         | -3.27%           | 45.00%  | 18.33%  | 2.50%         | 120  | 0.21%          | 1.32%            | 58.33%  | 16.67%  | 3.33%         |
| 2014     | 106  | 106  | 10.03%         | 12.90%           | 68.87%  | 21.70%  | 0.00%         | 106  | 2.52%          | 5.83%            | 63.21%  | 18.87%  | 9.43%         |
| 2015     | 116  | 116  | 3.06%          | -0.23%           | 49.14%  | 38.79%  | 4.31%         | 116  | -5.09%         | -2.82%           | 38.79%  | 28.45%  | 10.34%        |
| 2016     | 115  | 115  | -6.30%         | -6.85%           | 37.39%  | 25.22%  | 0.00%         | 115  | -2.25%         | 0.56%            | 50.43%  | 16.52%  | 5.22%         |
| 2017     | 111  | 111  | -2.38%         | -4.35%           | 44.14%  | 30.63%  | 5.41%         | 111  | -2.10%         | -0.57%           | 46.85%  | 27.93%  | 18.92%        |
| 2018     | 101  | 101  | 10.17%         | 7.15%            | 74.26%  | 18.81%  | 5.94%         | 101  | 3.74%          | 2.89%            | 60.40%  | 6.93%   | 8.91%         |
| 2019     | 109  | 109  | -6.70%         | -7.01%           | 36.70%  | 38.53%  | 2.75%         | 109  | -4.02%         | -5.28%           | 28.44%  | 19.27%  | 2.75%         |
| 2020     | 88   | 88   | -24.06%        | -25.14%          | 15.91%  | 39.77%  | 0.00%         | 88   | -8.98%         | -7.37%           | 20.45%  | 40.91%  | 6.82%         |
| all buys | 1783 | 1783 | 1.34%          | -0.23%           | 49.58%  | 32.53%  | 5.78%         | 1783 | 0.54%          | 1.30%            | 54.51%  | 25.01%  | 10.94%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 90
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 123 (final-print convention, sell cost applied)

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
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_top10_cap2_s232_ddaa9da1a75bb1eb_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_top10_cap2_s232_ddaa9da1a75bb1eb_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_top10_cap2_s232_ddaa9da1a75bb1eb_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_top10_cap2_s232_ddaa9da1a75bb1eb_equity.png`
