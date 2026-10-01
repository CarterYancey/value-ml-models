# Portfolio backtest — bt_nonloser_roc_top10_cap2

- run `44a39cc125cd`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `10f732359cf923db`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 694,944.59  | 502,944.59 | 11.18%         | 9.65%    | -41.16%      | 1,045.13   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.35%        | 6.51%         | -4.17%  | 12,000.00 | 105    | -82.2714        |
| 2006              | 11.46%       | 12.67%        | -1.21%  | 12,000.00 | 117    | -86.4444        |
| 2007              | 2.84%        | 7.28%         | -4.44%  | 12,000.00 | 120    | -100.9375       |
| 2008 (GFC)        | -31.63%      | -43.21%       | 11.58%  | 12,000.00 | 120    | -85.5875        |
| 2009 (GFC)        | 35.30%       | 39.07%        | -3.77%  | 12,000.00 | 117    | -73.5043        |
| 2010              | 14.92%       | 10.86%        | 4.06%   | 12,000.00 | 120    | -85.2417        |
| 2011              | 8.64%        | 5.33%         | 3.32%   | 12,000.00 | 114    | -76.9167        |
| 2012              | 10.83%       | 15.60%        | -4.76%  | 12,000.00 | 109    | -79.6147        |
| 2013              | 28.54%       | 30.42%        | -1.88%  | 12,000.00 | 113    | -62.7124        |
| 2014              | 19.35%       | 16.18%        | 3.17%   | 12,000.00 | 108    | -53.8657        |
| 2015              | 10.73%       | 4.46%         | 6.27%   | 12,000.00 | 105    | -51.1143        |
| 2016              | 8.84%        | 6.48%         | 2.37%   | 12,000.00 | 103    | -68.3883        |
| 2017              | 19.55%       | 22.88%        | -3.33%  | 12,000.00 | 109    | -54.9862        |
| 2018              | 6.23%        | 7.53%         | -1.30%  | 12,000.00 | 111    | -69.0135        |
| 2019              | 17.50%       | 13.81%        | 3.69%   | 12,000.00 | 110    | -81.1500        |
| 2020 (COVID)      | 10.87%       | 19.77%        | -8.90%  | 12,000.00 | 102    | -61.4755        |
| 2021              | 13.39%       | 24.81%        | -11.42% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 5.88%        | -8.20%        | 14.08%  | 0.00      | 0      | —               |
| 2023              | 4.18%        | 19.00%        | -14.82% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 384  | 21.54% |
| Industrials            | 329  | 18.45% |
| Technology             | 314  | 17.61% |
| Healthcare             | 293  | 16.43% |
| Consumer Cyclical      | 217  | 12.17% |
| Communication Services | 69   | 3.87%  |
| Energy                 | 57   | 3.20%  |
| Financial Services     | 57   | 3.20%  |
| Basic Materials        | 51   | 2.86%  |
| Real Estate            | 9    | 0.50%  |
| Utilities              | 3    | 0.17%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 105  | 15     | 9      | Consumer Defensive | 22.86%        |
| 2006 | 117  | 23     | 8      | Consumer Defensive | 20.51%        |
| 2007 | 120  | 21     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 117  | 17     | 6      | Healthcare         | 20.51%        |
| 2010 | 120  | 19     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 114  | 18     | 7      | Consumer Defensive | 21.05%        |
| 2012 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2013 | 113  | 18     | 7      | Consumer Defensive | 21.24%        |
| 2014 | 108  | 14     | 6      | Consumer Defensive | 22.22%        |
| 2015 | 105  | 15     | 6      | Consumer Defensive | 22.86%        |
| 2016 | 103  | 16     | 8      | Consumer Defensive | 23.30%        |
| 2017 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2018 | 111  | 22     | 8      | Consumer Defensive | 21.62%        |
| 2019 | 110  | 21     | 8      | Consumer Defensive | 21.82%        |
| 2020 | 102  | 21     | 7      | Consumer Defensive | 23.53%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 105  | 105  | -4.89%         | -4.94%           | 32.38%  | 34.29%  | 0.00%         | 105  | -2.61%         | -1.66%           | 32.38%  | 42.86%  | 11.43%        |
| 2006     | 117  | 117  | 0.16%          | -0.41%           | 48.72%  | 11.11%  | 2.56%         | 117  | 2.81%          | 3.60%            | 64.10%  | 64.96%  | 7.69%         |
| 2007     | 120  | 120  | 2.89%          | 4.17%            | 60.83%  | 60.00%  | 0.00%         | 120  | 4.38%          | 5.08%            | 70.83%  | 60.00%  | 2.50%         |
| 2008     | 120  | 120  | 11.91%         | 15.08%           | 78.33%  | 78.33%  | 0.00%         | 120  | 5.85%          | 5.63%            | 78.33%  | 9.17%   | 0.00%         |
| 2009     | 117  | 117  | 3.68%          | -2.23%           | 47.86%  | 10.26%  | 3.42%         | 117  | 1.40%          | -1.13%           | 47.01%  | 0.00%   | 5.13%         |
| 2010     | 120  | 120  | 4.09%          | 4.20%            | 62.50%  | 9.17%   | 0.00%         | 120  | 0.53%          | 0.91%            | 50.83%  | 5.00%   | 0.00%         |
| 2011     | 114  | 114  | 5.36%          | 0.08%            | 50.00%  | 24.56%  | 0.00%         | 114  | 0.19%          | 0.88%            | 52.63%  | 0.88%   | 0.00%         |
| 2012     | 109  | 109  | -2.83%         | -2.52%           | 45.87%  | 16.51%  | 0.00%         | 109  | -2.70%         | 2.49%            | 55.05%  | 18.35%  | 0.92%         |
| 2013     | 113  | 113  | 3.67%          | 4.64%            | 63.72%  | 6.19%   | 0.00%         | 113  | 7.61%          | 6.57%            | 80.53%  | 2.65%   | 0.00%         |
| 2014     | 108  | 108  | 12.65%         | 13.61%           | 77.78%  | 9.26%   | 0.00%         | 108  | 5.52%          | 7.33%            | 73.15%  | 11.11%  | 0.00%         |
| 2015     | 105  | 105  | 11.07%         | 10.80%           | 80.00%  | 18.10%  | 0.00%         | 105  | 0.58%          | 1.99%            | 60.00%  | 19.05%  | 0.00%         |
| 2016     | 103  | 103  | -0.56%         | -0.91%           | 45.63%  | 11.65%  | 0.00%         | 103  | -1.16%         | 3.16%            | 60.19%  | 24.27%  | 2.91%         |
| 2017     | 109  | 109  | 4.70%          | 7.16%            | 64.22%  | 11.93%  | 4.59%         | 109  | 4.67%          | 6.48%            | 75.23%  | 9.17%   | 5.50%         |
| 2018     | 111  | 111  | 11.10%         | 11.97%           | 74.77%  | 17.12%  | 2.70%         | 111  | -1.58%         | -1.50%           | 44.14%  | 0.00%   | 5.41%         |
| 2019     | 110  | 110  | -4.44%         | -6.32%           | 40.91%  | 39.09%  | 0.00%         | 110  | -4.26%         | -3.99%           | 28.18%  | 7.27%   | 1.82%         |
| 2020     | 102  | 102  | -15.21%        | -13.42%          | 21.57%  | 14.71%  | 0.00%         | 102  | -2.44%         | -2.11%           | 40.20%  | 13.73%  | 9.80%         |
| all buys | 1783 | 1783 | 2.86%          | 2.86%            | 56.25%  | 23.67%  | 0.84%         | 1783 | 1.26%          | 1.82%            | 57.32%  | 18.12%  | 3.25%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 108
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 26 (final-print convention, sell cost applied)

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
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_10f732359cf923db_equity.png`
