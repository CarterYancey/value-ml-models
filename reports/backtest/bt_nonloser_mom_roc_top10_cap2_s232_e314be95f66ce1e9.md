# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_s232

- run `d33c17304ed9`, git `ba55f7d9adc1654cdb466dee924ac976e3f9a828`, backtest config `e314be95f66ce1e9`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 959,660.23  | 767,660.23 | 13.89%         | 12.26%   | -41.25%      | 1,228.10   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 9.38%        | 6.51%         | 2.86%  | 12,000.00 | 108    | -345.3117       |
| 2006              | 7.36%        | 12.67%        | -5.31% | 12,000.00 | 120    | -369.5083       |
| 2007              | 1.69%        | 7.28%         | -5.59% | 12,000.00 | 117    | -337.1311       |
| 2008 (GFC)        | -33.62%      | -43.21%       | 9.59%  | 12,000.00 | 120    | -285.9444       |
| 2009 (GFC)        | 42.51%       | 39.07%        | 3.44%  | 12,000.00 | 115    | -190.4551       |
| 2010              | 29.28%       | 10.86%        | 18.43% | 12,000.00 | 120    | -368.0806       |
| 2011              | 10.40%       | 5.33%         | 5.07%  | 12,000.00 | 109    | -292.4618       |
| 2012              | 15.53%       | 15.60%        | -0.06% | 12,000.00 | 108    | -191.3580       |
| 2013              | 37.25%       | 30.42%        | 6.82%  | 12,000.00 | 114    | -261.1696       |
| 2014              | 13.06%       | 16.18%        | -3.12% | 12,000.00 | 111    | -305.1081       |
| 2015              | 13.17%       | 4.46%         | 8.71%  | 12,000.00 | 113    | -204.0944       |
| 2016              | 4.73%        | 6.48%         | -1.75% | 12,000.00 | 107    | -189.7819       |
| 2017              | 23.27%       | 22.88%        | 0.39%  | 12,000.00 | 103    | -296.5340       |
| 2018              | 9.90%        | 7.53%         | 2.37%  | 12,000.00 | 95     | -258.2246       |
| 2019              | 22.04%       | 13.81%        | 8.23%  | 12,000.00 | 103    | -220.0065       |
| 2020 (COVID)      | 22.96%       | 19.77%        | 3.20%  | 12,000.00 | 85     | -206.9647       |
| 2021              | 16.47%       | 24.81%        | -8.34% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -5.38%       | -8.20%        | 2.82%  | 0.00      | 0      | —               |
| 2023              | 16.98%       | 19.00%        | -2.02% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 305  | 17.45% |
| Industrials            | 282  | 16.13% |
| Healthcare             | 278  | 15.90% |
| Technology             | 267  | 15.27% |
| Consumer Cyclical      | 261  | 14.93% |
| Basic Materials        | 127  | 7.27%  |
| Communication Services | 93   | 5.32%  |
| Financial Services     | 80   | 4.58%  |
| Energy                 | 33   | 1.89%  |
| Real Estate            | 13   | 0.74%  |
| Utilities              | 9    | 0.51%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 25     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 30     | 7      | Healthcare         | 20.00%        |
| 2007 | 117  | 30     | 8      | Consumer Defensive | 17.95%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 115  | 32     | 10     | Consumer Defensive | 18.26%        |
| 2010 | 120  | 29     | 8      | Consumer Defensive | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive | 19.27%        |
| 2012 | 108  | 30     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 114  | 32     | 8      | Healthcare         | 18.42%        |
| 2014 | 111  | 28     | 8      | Technology         | 21.62%        |
| 2015 | 113  | 25     | 8      | Consumer Defensive | 21.24%        |
| 2016 | 107  | 31     | 7      | Consumer Defensive | 22.43%        |
| 2017 | 103  | 26     | 9      | Consumer Cyclical  | 19.42%        |
| 2018 | 95   | 23     | 8      | Consumer Cyclical  | 22.11%        |
| 2019 | 103  | 27     | 7      | Consumer Defensive | 23.30%        |
| 2020 | 85   | 26     | 8      | Consumer Defensive | 23.53%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.59%         | -4.66%           | 39.81%  | 34.26%  | 2.78%         | 108  | -4.40%         | 0.45%            | 55.56%  | 40.74%  | 11.11%        |
| 2006     | 120  | 120  | -13.13%        | -12.34%          | 22.50%  | 45.00%  | 5.00%         | 120  | 0.51%          | 1.83%            | 58.33%  | 75.83%  | 5.00%         |
| 2007     | 117  | 117  | 4.95%          | 4.88%            | 66.67%  | 58.97%  | 1.71%         | 117  | 8.32%          | 7.92%            | 82.05%  | 41.03%  | 11.97%        |
| 2008     | 120  | 120  | 8.13%          | 9.74%            | 64.17%  | 77.50%  | 0.83%         | 120  | 6.92%          | 7.23%            | 84.17%  | 12.50%  | 3.33%         |
| 2009     | 115  | 115  | 5.20%          | 4.70%            | 56.52%  | 13.04%  | 6.96%         | 115  | -0.84%         | -0.35%           | 46.09%  | 8.70%   | 11.30%        |
| 2010     | 120  | 120  | 27.54%         | 18.99%           | 75.00%  | 8.33%   | 1.67%         | 120  | 9.53%          | 9.15%            | 77.50%  | 1.67%   | 6.67%         |
| 2011     | 109  | 109  | 10.87%         | 8.39%            | 65.14%  | 21.10%  | 5.50%         | 109  | 4.48%          | 4.42%            | 71.56%  | 8.26%   | 8.26%         |
| 2012     | 108  | 108  | 0.82%          | -0.72%           | 49.07%  | 14.81%  | 0.00%         | 108  | 1.61%          | 5.42%            | 60.19%  | 14.81%  | 0.93%         |
| 2013     | 114  | 114  | -1.81%         | -1.99%           | 42.11%  | 14.04%  | 2.63%         | 114  | 2.52%          | 3.68%            | 66.67%  | 15.79%  | 5.26%         |
| 2014     | 111  | 111  | 14.05%         | 16.66%           | 76.58%  | 16.22%  | 1.80%         | 111  | 4.20%          | 3.90%            | 61.26%  | 14.41%  | 8.11%         |
| 2015     | 113  | 113  | 4.88%          | 2.96%            | 58.41%  | 30.97%  | 0.00%         | 113  | 3.13%          | 5.81%            | 69.03%  | 14.16%  | 5.31%         |
| 2016     | 107  | 107  | 0.11%          | -2.70%           | 42.06%  | 11.21%  | 2.80%         | 107  | 2.01%          | 4.50%            | 63.55%  | 17.76%  | 5.61%         |
| 2017     | 103  | 103  | -0.83%         | -4.51%           | 40.78%  | 27.18%  | 4.85%         | 103  | 1.31%          | 0.22%            | 51.46%  | 21.36%  | 17.48%        |
| 2018     | 95   | 95   | 10.91%         | 7.60%            | 74.74%  | 20.00%  | 0.00%         | 95   | 5.96%          | 7.27%            | 57.89%  | 2.11%   | 6.32%         |
| 2019     | 103  | 103  | -2.65%         | -3.99%           | 42.72%  | 35.92%  | 0.00%         | 103  | -4.78%         | -5.93%           | 20.39%  | 12.62%  | 0.00%         |
| 2020     | 85   | 85   | -13.94%        | -20.36%          | 35.29%  | 31.76%  | 0.00%         | 85   | -2.02%         | -1.92%           | 41.18%  | 27.06%  | 10.59%        |
| all buys | 1748 | 1748 | 3.53%          | 2.03%            | 53.49%  | 29.12%  | 2.35%         | 1748 | 2.55%          | 3.39%            | 61.21%  | 20.82%  | 7.27%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 104
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 68 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 19 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s232_e314be95f66ce1e9_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s232_e314be95f66ce1e9_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s232_e314be95f66ce1e9_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_s232_e314be95f66ce1e9_equity.png`
