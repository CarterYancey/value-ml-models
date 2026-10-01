# Portfolio backtest — bt_nonloser_roc_top10_cap2_sell20

- run `799e7f5ec380`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `5fc4fd669e5a9d55`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 800,456.04  | 608,456.04 | 12.37%         | 10.64%   | -38.81%      | 2,209.52   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.56%        | 6.51%         | -3.96%  | 12,000.00 | 105    | -82.2714        |
| 2006              | 9.61%        | 12.67%        | -3.06%  | 12,000.00 | 117    | -86.4444        |
| 2007              | 7.43%        | 7.28%         | 0.15%   | 12,000.00 | 120    | -100.9375       |
| 2008 (GFC)        | -32.46%      | -43.21%       | 10.75%  | 12,000.00 | 120    | -85.5875        |
| 2009 (GFC)        | 38.14%       | 39.07%        | -0.93%  | 12,000.00 | 117    | -73.5043        |
| 2010              | 13.78%       | 10.86%        | 2.92%   | 12,000.00 | 120    | -85.2417        |
| 2011              | 8.40%        | 5.33%         | 3.08%   | 12,000.00 | 115    | -77.2870        |
| 2012              | 12.24%       | 15.60%        | -3.36%  | 12,000.00 | 109    | -79.5413        |
| 2013              | 27.43%       | 30.42%        | -2.99%  | 12,000.00 | 115    | -63.0087        |
| 2014              | 16.58%       | 16.18%        | 0.39%   | 12,000.00 | 109    | -54.1193        |
| 2015              | 18.16%       | 4.46%         | 13.69%  | 12,000.00 | 107    | -51.3738        |
| 2016              | 8.19%        | 6.48%         | 1.71%   | 12,000.00 | 106    | -68.6698        |
| 2017              | 19.64%       | 22.88%        | -3.24%  | 12,000.00 | 109    | -55.0046        |
| 2018              | 11.19%       | 7.53%         | 3.65%   | 12,000.00 | 112    | -69.8795        |
| 2019              | 22.13%       | 13.81%        | 8.32%   | 12,000.00 | 107    | -80.5421        |
| 2020 (COVID)      | 13.70%       | 19.77%        | -6.07%  | 12,000.00 | 106    | -62.2170        |
| 2021              | 8.72%        | 24.81%        | -16.09% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 9.14%        | -8.20%        | 17.33%  | 0.00      | 0      | —               |
| 2023              | 5.06%        | 19.00%        | -13.95% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 384  | 21.40% |
| Industrials            | 334  | 18.62% |
| Technology             | 313  | 17.45% |
| Healthcare             | 294  | 16.39% |
| Consumer Cyclical      | 221  | 12.32% |
| Communication Services | 68   | 3.79%  |
| Financial Services     | 60   | 3.34%  |
| Energy                 | 57   | 3.18%  |
| Basic Materials        | 51   | 2.84%  |
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
| 2011 | 115  | 19     | 7      | Consumer Defensive | 20.87%        |
| 2012 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2013 | 115  | 19     | 7      | Consumer Defensive | 20.87%        |
| 2014 | 109  | 15     | 6      | Consumer Defensive | 22.02%        |
| 2015 | 107  | 15     | 6      | Consumer Defensive | 22.43%        |
| 2016 | 106  | 18     | 8      | Consumer Defensive | 22.64%        |
| 2017 | 109  | 18     | 8      | Consumer Defensive | 22.02%        |
| 2018 | 112  | 23     | 8      | Consumer Defensive | 21.43%        |
| 2019 | 107  | 21     | 8      | Consumer Defensive | 22.43%        |
| 2020 | 106  | 22     | 7      | Consumer Defensive | 22.64%        |

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
| 2011     | 115  | 115  | 5.49%          | 0.16%            | 50.43%  | 24.35%  | 0.00%         | 115  | 0.24%          | 0.91%            | 53.04%  | 0.87%   | 0.00%         |
| 2012     | 109  | 109  | -2.81%         | -2.15%           | 45.87%  | 16.51%  | 0.00%         | 109  | -2.71%         | 2.49%            | 55.05%  | 18.35%  | 0.92%         |
| 2013     | 115  | 115  | 3.56%          | 4.62%            | 63.48%  | 6.09%   | 0.00%         | 115  | 7.58%          | 6.57%            | 80.87%  | 2.61%   | 0.00%         |
| 2014     | 109  | 109  | 12.67%         | 13.64%           | 77.98%  | 9.17%   | 0.00%         | 109  | 5.55%          | 7.38%            | 73.39%  | 11.01%  | 0.00%         |
| 2015     | 107  | 107  | 10.67%         | 10.46%           | 78.50%  | 18.69%  | 0.00%         | 107  | 0.47%          | 1.97%            | 57.94%  | 18.69%  | 0.00%         |
| 2016     | 106  | 106  | -0.97%         | -0.93%           | 45.28%  | 12.26%  | 0.00%         | 106  | -1.15%         | 3.00%            | 59.43%  | 23.58%  | 2.83%         |
| 2017     | 109  | 109  | 4.89%          | 8.76%            | 64.22%  | 11.93%  | 4.59%         | 109  | 4.70%          | 6.48%            | 75.23%  | 9.17%   | 5.50%         |
| 2018     | 112  | 112  | 11.42%         | 12.02%           | 75.89%  | 16.96%  | 2.68%         | 112  | -1.48%         | -1.71%           | 43.75%  | 0.00%   | 5.36%         |
| 2019     | 107  | 107  | -4.61%         | -6.74%           | 40.19%  | 40.19%  | 0.00%         | 107  | -4.21%         | -4.06%           | 28.04%  | 6.54%   | 1.87%         |
| 2020     | 106  | 106  | -15.21%        | -13.42%          | 20.75%  | 13.21%  | 0.00%         | 106  | -2.49%         | -2.11%           | 39.62%  | 12.26%  | 9.43%         |
| all buys | 1794 | 1794 | 2.82%          | 2.79%            | 56.13%  | 23.58%  | 0.84%         | 1794 | 1.27%          | 1.79%            | 57.19%  | 17.89%  | 3.23%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 102
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 69 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 4 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 17 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_5fc4fd669e5a9d55_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_5fc4fd669e5a9d55_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_5fc4fd669e5a9d55_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_5fc4fd669e5a9d55_equity.png`
