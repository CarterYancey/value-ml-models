# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_sell20_s232

- run `4fc545b3684a`, git `0b8c053e4592471721d4f16d3f3d529ee814b140`, backtest config `fbe4826aa743dadb`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 1,042,252.06 | 850,252.06 | 14.58%         | 12.70%   | -40.24%      | 5,061.96   |
| benchmark | 192,000.00 | 732,110.07   | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 9.26%        | 6.51%         | 2.75%  | 12,000.00 | 108    | -345.3117       |
| 2006              | 6.39%        | 12.67%        | -6.28% | 12,000.00 | 120    | -369.5083       |
| 2007              | 1.72%        | 7.28%         | -5.56% | 12,000.00 | 118    | -337.3588       |
| 2008 (GFC)        | -33.65%      | -43.21%       | 9.56%  | 12,000.00 | 120    | -285.9444       |
| 2009 (GFC)        | 41.14%       | 39.07%        | 2.07%  | 12,000.00 | 117    | -189.8034       |
| 2010              | 30.53%       | 10.86%        | 19.67% | 12,000.00 | 120    | -368.0806       |
| 2011              | 13.45%       | 5.33%         | 8.12%  | 12,000.00 | 111    | -292.1171       |
| 2012              | 16.39%       | 15.60%        | 0.79%  | 12,000.00 | 111    | -190.6667       |
| 2013              | 23.01%       | 30.42%        | -7.41% | 12,000.00 | 116    | -261.3448       |
| 2014              | 17.74%       | 16.18%        | 1.56%  | 12,000.00 | 114    | -303.8304       |
| 2015              | 16.64%       | 4.46%         | 12.18% | 12,000.00 | 112    | -204.8452       |
| 2016              | 6.48%        | 6.48%         | -0.00% | 12,000.00 | 110    | -189.1121       |
| 2017              | 23.93%       | 22.88%        | 1.05%  | 12,000.00 | 105    | -295.4095       |
| 2018              | 15.25%       | 7.53%         | 7.72%  | 12,000.00 | 99     | -258.2761       |
| 2019              | 25.46%       | 13.81%        | 11.65% | 12,000.00 | 100    | -217.5867       |
| 2020 (COVID)      | 21.18%       | 19.77%        | 1.41%  | 12,000.00 | 98     | -208.8980       |
| 2021              | 16.54%       | 24.81%        | -8.27% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -1.98%       | -8.20%        | 6.22%  | 0.00      | 0      | —               |
| 2023              | 13.53%       | 19.00%        | -5.47% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

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
| Consumer Defensive     | 305  | 17.14% |
| Industrials            | 292  | 16.41% |
| Healthcare             | 283  | 15.91% |
| Consumer Cyclical      | 275  | 15.46% |
| Technology             | 269  | 15.12% |
| Basic Materials        | 126  | 7.08%  |
| Communication Services | 93   | 5.23%  |
| Financial Services     | 79   | 4.44%  |
| Energy                 | 33   | 1.85%  |
| Real Estate            | 15   | 0.84%  |
| Utilities              | 9    | 0.51%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 25     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 30     | 7      | Healthcare         | 20.00%        |
| 2007 | 118  | 31     | 8      | Industrials        | 18.64%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 117  | 32     | 10     | Consumer Defensive | 17.95%        |
| 2010 | 120  | 29     | 8      | Consumer Defensive | 20.00%        |
| 2011 | 111  | 30     | 9      | Consumer Defensive | 18.92%        |
| 2012 | 111  | 32     | 9      | Consumer Defensive | 21.62%        |
| 2013 | 116  | 33     | 8      | Healthcare         | 18.10%        |
| 2014 | 114  | 28     | 8      | Technology         | 21.05%        |
| 2015 | 112  | 25     | 8      | Consumer Defensive | 21.43%        |
| 2016 | 110  | 32     | 7      | Technology         | 21.82%        |
| 2017 | 105  | 27     | 9      | Consumer Cyclical  | 20.95%        |
| 2018 | 99   | 25     | 8      | Consumer Cyclical  | 21.21%        |
| 2019 | 100  | 29     | 7      | Consumer Defensive | 24.00%        |
| 2020 | 98   | 32     | 8      | Consumer Defensive | 20.41%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.59%         | -4.66%           | 39.81%  | 34.26%  | 2.78%         | 108  | -4.40%         | 0.45%            | 55.56%  | 40.74%  | 11.11%        |
| 2006     | 120  | 120  | -13.13%        | -12.34%          | 22.50%  | 45.00%  | 5.00%         | 120  | 0.51%          | 1.83%            | 58.33%  | 75.83%  | 5.00%         |
| 2007     | 118  | 118  | 4.69%          | 4.78%            | 66.10%  | 59.32%  | 1.69%         | 118  | 8.28%          | 7.87%            | 82.20%  | 41.53%  | 11.86%        |
| 2008     | 120  | 120  | 8.13%          | 9.74%            | 64.17%  | 77.50%  | 0.83%         | 120  | 6.92%          | 7.23%            | 84.17%  | 12.50%  | 3.33%         |
| 2009     | 117  | 117  | 5.58%          | 5.09%            | 57.26%  | 12.82%  | 6.84%         | 117  | -0.47%         | -0.26%           | 47.01%  | 8.55%   | 11.11%        |
| 2010     | 120  | 120  | 27.54%         | 18.99%           | 75.00%  | 8.33%   | 1.67%         | 120  | 9.53%          | 9.15%            | 77.50%  | 1.67%   | 6.67%         |
| 2011     | 111  | 111  | 10.68%         | 8.39%            | 64.86%  | 20.72%  | 5.41%         | 111  | 4.40%          | 4.42%            | 71.17%  | 8.11%   | 8.11%         |
| 2012     | 111  | 111  | 1.14%          | -1.02%           | 47.75%  | 14.41%  | 0.00%         | 111  | 1.21%          | 5.24%            | 60.36%  | 15.32%  | 0.90%         |
| 2013     | 116  | 116  | -1.61%         | -1.44%           | 43.10%  | 13.79%  | 2.59%         | 116  | 2.46%          | 3.46%            | 66.38%  | 15.52%  | 5.17%         |
| 2014     | 114  | 114  | 14.05%         | 16.50%           | 77.19%  | 15.79%  | 1.75%         | 114  | 4.19%          | 4.49%            | 61.40%  | 14.91%  | 7.89%         |
| 2015     | 112  | 112  | 4.91%          | 3.02%            | 58.04%  | 31.25%  | 0.00%         | 112  | 3.09%          | 5.86%            | 69.64%  | 14.29%  | 5.36%         |
| 2016     | 110  | 110  | -0.71%         | -3.08%           | 41.82%  | 12.73%  | 2.73%         | 110  | 1.65%          | 3.87%            | 61.82%  | 17.27%  | 5.45%         |
| 2017     | 105  | 105  | -0.51%         | -4.35%           | 41.90%  | 26.67%  | 4.76%         | 105  | 1.43%          | 0.30%            | 52.38%  | 20.95%  | 17.14%        |
| 2018     | 99   | 99   | 10.23%         | 8.07%            | 75.76%  | 20.20%  | 0.00%         | 99   | 4.65%          | 5.70%            | 55.56%  | 4.04%   | 6.06%         |
| 2019     | 100  | 100  | -3.62%         | -3.32%           | 43.00%  | 37.00%  | 0.00%         | 100  | -5.22%         | -6.01%           | 20.00%  | 12.00%  | 0.00%         |
| 2020     | 98   | 98   | -13.80%        | -15.62%          | 35.71%  | 28.57%  | 0.00%         | 98   | -2.35%         | -2.31%           | 39.80%  | 24.49%  | 9.18%         |
| all buys | 1779 | 1779 | 3.35%          | 2.09%            | 53.57%  | 28.89%  | 2.30%         | 1779 | 2.39%          | 3.22%            | 60.93%  | 20.74%  | 7.14%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 83
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 235 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 5 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 25 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s232_fbe4826aa743dadb_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s232_fbe4826aa743dadb_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s232_fbe4826aa743dadb_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s232_fbe4826aa743dadb_equity.png`
