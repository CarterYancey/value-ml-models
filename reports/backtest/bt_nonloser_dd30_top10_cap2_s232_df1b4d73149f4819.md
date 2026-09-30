# Portfolio backtest — bt_nonloser_dd30_top10_cap2_s232

- run `ae772d95b74f`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `df1b4d73149f4819`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 630,423.03  | 438,423.03 | 10.36%         | 9.35%    | -47.11%      | 1,463.10   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 6.42%        | 6.51%         | -0.09%  | 12,000.00 | 119    | 0.7224          |
| 2006              | 12.82%       | 12.67%        | 0.16%   | 12,000.00 | 111    | 0.7436          |
| 2007              | -3.39%       | 7.28%         | -10.67% | 12,000.00 | 116    | 0.8135          |
| 2008 (GFC)        | -30.36%      | -43.21%       | 12.85%  | 12,000.00 | 118    | 0.8322          |
| 2009 (GFC)        | 30.00%       | 39.07%        | -9.07%  | 12,000.00 | 120    | 0.8064          |
| 2010              | 26.80%       | 10.86%        | 15.94%  | 12,000.00 | 120    | 0.7405          |
| 2011              | 14.02%       | 5.33%         | 8.69%   | 12,000.00 | 117    | 0.6793          |
| 2012              | 16.06%       | 15.60%        | 0.46%   | 12,000.00 | 120    | 0.6445          |
| 2013              | 17.28%       | 30.42%        | -13.14% | 12,000.00 | 120    | 0.6630          |
| 2014              | 21.39%       | 16.18%        | 5.21%   | 12,000.00 | 117    | 0.6837          |
| 2015              | 4.26%        | 4.46%         | -0.20%  | 12,000.00 | 117    | 0.6966          |
| 2016              | 11.48%       | 6.48%         | 5.00%   | 12,000.00 | 110    | 0.7214          |
| 2017              | 18.41%       | 22.88%        | -4.46%  | 12,000.00 | 115    | 0.7310          |
| 2018              | 6.04%        | 7.53%         | -1.49%  | 12,000.00 | 114    | 0.7239          |
| 2019              | 17.65%       | 13.81%        | 3.84%   | 12,000.00 | 102    | 0.7305          |
| 2020 (COVID)      | 3.22%        | 19.77%        | -16.54% | 12,000.00 | 103    | 0.7358          |
| 2021              | 16.52%       | 24.81%        | -8.29%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.80%        | -8.20%        | 12.99%  | 0.00      | 0      | —               |
| 2023              | 0.53%        | 19.00%        | -18.47% | 0.00      | 0      | —               |

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
| Utilities              | 357  | 19.41% |
| Real Estate            | 301  | 16.37% |
| Consumer Defensive     | 281  | 15.28% |
| Industrials            | 245  | 13.32% |
| Energy                 | 210  | 11.42% |
| Healthcare             | 134  | 7.29%  |
| Consumer Cyclical      | 114  | 6.20%  |
| Communication Services | 87   | 4.73%  |
| Technology             | 66   | 3.59%  |
| Financial Services     | 30   | 1.63%  |
| Basic Materials        | 14   | 0.76%  |

| year | buys | stocks | groups | largest_group | largest_share |
| ---- | ---- | ------ | ------ | ------------- | ------------- |
| 2005 | 119  | 22     | 9      | Real Estate   | 20.17%        |
| 2006 | 111  | 21     | 8      | Real Estate   | 21.62%        |
| 2007 | 116  | 21     | 9      | Real Estate   | 20.69%        |
| 2008 | 118  | 18     | 7      | Real Estate   | 20.34%        |
| 2009 | 120  | 24     | 6      | Energy        | 20.00%        |
| 2010 | 120  | 22     | 8      | Energy        | 20.00%        |
| 2011 | 117  | 24     | 8      | Utilities     | 20.51%        |
| 2012 | 120  | 26     | 8      | Energy        | 20.00%        |
| 2013 | 120  | 29     | 8      | Utilities     | 20.00%        |
| 2014 | 117  | 27     | 9      | Utilities     | 20.51%        |
| 2015 | 117  | 31     | 8      | Utilities     | 20.51%        |
| 2016 | 110  | 27     | 9      | Utilities     | 21.82%        |
| 2017 | 115  | 26     | 8      | Utilities     | 20.87%        |
| 2018 | 114  | 22     | 8      | Utilities     | 21.05%        |
| 2019 | 102  | 18     | 7      | Utilities     | 23.53%        |
| 2020 | 103  | 27     | 8      | Utilities     | 20.39%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 119  | 119  | -3.61%         | -5.53%           | 35.29%  | 38.66%  | 0.84%         | 119  | -2.78%         | -3.16%           | 36.97%  | 47.90%  | 15.13%        |
| 2006     | 111  | 111  | -1.30%         | -0.63%           | 47.75%  | 15.32%  | 13.51%        | 111  | -4.64%         | -1.43%           | 40.54%  | 77.48%  | 16.22%        |
| 2007     | 116  | 116  | 4.70%          | 5.03%            | 60.34%  | 65.52%  | 2.59%         | 116  | 5.92%          | 5.55%            | 62.07%  | 50.00%  | 2.59%         |
| 2008     | 118  | 118  | 6.86%          | 12.44%           | 66.95%  | 77.97%  | 0.00%         | 118  | 6.25%          | 7.85%            | 73.73%  | 15.25%  | 0.00%         |
| 2009     | 120  | 120  | 7.30%          | 6.25%            | 66.67%  | 0.83%   | 2.50%         | 120  | 7.01%          | 6.63%            | 76.67%  | 0.00%   | 2.50%         |
| 2010     | 120  | 120  | 6.07%          | 4.86%            | 64.17%  | 6.67%   | 0.00%         | 120  | 2.83%          | 2.69%            | 60.83%  | 1.67%   | 4.17%         |
| 2011     | 117  | 117  | 6.65%          | 6.19%            | 63.25%  | 19.66%  | 0.00%         | 117  | -1.08%         | -0.75%           | 43.59%  | 5.13%   | 2.56%         |
| 2012     | 120  | 120  | 1.30%          | 0.90%            | 50.83%  | 5.83%   | 0.00%         | 120  | -1.38%         | -0.92%           | 46.67%  | 5.00%   | 0.00%         |
| 2013     | 120  | 120  | -8.54%         | -9.77%           | 30.83%  | 20.00%  | 2.50%         | 120  | 2.06%          | 0.45%            | 55.00%  | 2.50%   | 13.33%        |
| 2014     | 117  | 117  | 4.98%          | 6.95%            | 62.39%  | 20.51%  | 0.00%         | 117  | 3.47%          | 2.87%            | 58.97%  | 7.69%   | 2.56%         |
| 2015     | 117  | 117  | 11.21%         | 11.06%           | 77.78%  | 18.80%  | 3.42%         | 117  | -0.39%         | 0.95%            | 54.70%  | 11.11%  | 3.42%         |
| 2016     | 110  | 110  | -2.87%         | -4.07%           | 40.91%  | 7.27%   | 3.64%         | 110  | 0.72%          | 1.73%            | 58.18%  | 7.27%   | 3.64%         |
| 2017     | 115  | 115  | -5.68%         | -6.06%           | 33.91%  | 27.83%  | 0.00%         | 115  | -1.79%         | -0.60%           | 44.35%  | 12.17%  | 5.22%         |
| 2018     | 114  | 114  | 16.42%         | 14.95%           | 88.60%  | 6.14%   | 7.02%         | 114  | -2.36%         | -0.68%           | 42.98%  | 4.39%   | 7.89%         |
| 2019     | 102  | 102  | -9.25%         | -10.30%          | 23.53%  | 39.22%  | 0.00%         | 102  | -4.43%         | -4.33%           | 27.45%  | 10.78%  | 0.00%         |
| 2020     | 103  | 103  | -18.69%        | -22.36%          | 9.71%   | 26.21%  | 0.97%         | 103  | -3.54%         | -2.90%           | 37.86%  | 17.48%  | 6.80%         |
| all buys | 1839 | 1839 | 1.21%          | 1.24%            | 51.98%  | 24.69%  | 2.28%         | 1839 | 0.47%          | 0.33%            | 51.66%  | 17.07%  | 5.38%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 60
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 45 (final-print convention, sell cost applied)

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

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_dd30_top10_cap2_s232_df1b4d73149f4819_equity.csv`
- trades: `reports/backtest/bt_nonloser_dd30_top10_cap2_s232_df1b4d73149f4819_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_dd30_top10_cap2_s232_df1b4d73149f4819_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_dd30_top10_cap2_s232_df1b4d73149f4819_equity.png`
