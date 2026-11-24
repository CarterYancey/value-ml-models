# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_frac_to2026

- run `8cf06803d06f`, git `09bb3ace4e9e1b904dc93220f7dd8ee5b08116d0`, backtest config `d5812ac1d6401831`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ------------ | -------------- | -------- | ------------ | ---------- |
| strategy  | 260,000.00 | 1,329,279.54 | 1,069,279.54 | 13.22%         | 11.96%   | -41.23%      | 14,670.48  |
| benchmark | 260,000.00 | 1,326,613.94 | 1,066,613.94 | 13.21%         | 10.94%   | -52.91%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 5.16%        | 6.60%         | -1.44%  | 12,000.00 | 120    | -356.2333       |
| 2006              | 11.43%       | 12.70%        | -1.27%  | 12,000.00 | 120    | -383.1056       |
| 2007              | 1.18%        | 7.29%         | -6.11%  | 12,000.00 | 120    | -343.9806       |
| 2008 (GFC)        | -32.97%      | -43.24%       | 10.26%  | 12,000.00 | 120    | -299.0500       |
| 2009 (GFC)        | 36.81%       | 39.09%        | -2.27%  | 12,000.00 | 120    | -208.2472       |
| 2010              | 28.86%       | 10.87%        | 17.99%  | 12,000.00 | 120    | -383.7250       |
| 2011              | 17.04%       | 5.32%         | 11.72%  | 12,000.00 | 120    | -297.1500       |
| 2012              | 15.20%       | 15.60%        | -0.40%  | 12,000.00 | 120    | -194.9500       |
| 2013              | 24.70%       | 30.43%        | -5.74%  | 12,000.00 | 120    | -263.0250       |
| 2014              | 18.52%       | 16.19%        | 2.33%   | 12,000.00 | 120    | -295.2889       |
| 2015              | 17.43%       | 4.46%         | 12.97%  | 12,000.00 | 120    | -201.4361       |
| 2016              | 6.75%        | 6.48%         | 0.27%   | 12,000.00 | 120    | -184.9611       |
| 2017              | 23.00%       | 22.88%        | 0.12%   | 12,000.00 | 120    | -286.0639       |
| 2018              | 16.29%       | 7.54%         | 8.75%   | 12,000.00 | 120    | -253.4472       |
| 2019              | 26.20%       | 13.81%        | 12.39%  | 12,000.00 | 120    | -220.2056       |
| 2020 (COVID)      | 20.10%       | 19.76%        | 0.34%   | 12,000.00 | 120    | -205.5972       |
| 2021              | 16.52%       | 24.83%        | -8.31%  | 12,000.00 | 120    | -335.9278       |
| 2022 (rate-shock) | -7.40%       | -8.20%        | 0.80%   | 12,000.00 | 120    | -233.7056       |
| 2023              | 8.00%        | 14.49%        | -6.49%  | 12,000.00 | 120    | -219.4778       |
| 2024              | 26.50%       | 33.27%        | -6.76%  | 12,000.00 | 120    | -250.8806       |
| 2025              | 0.32%        | 14.06%        | -13.74% | 12,000.00 | 120    | -236.3583       |
| 2026              | 2.57%        | 13.49%        | -10.92% | 8,000.00  | 80     | -289.5417       |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
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
| Industrials            | 442  | 17.00% |
| Healthcare             | 427  | 16.42% |
| Technology             | 415  | 15.96% |
| Consumer Defensive     | 391  | 15.04% |
| Consumer Cyclical      | 387  | 14.88% |
| Basic Materials        | 224  | 8.62%  |
| Communication Services | 123  | 4.73%  |
| Financial Services     | 117  | 4.50%  |
| Energy                 | 44   | 1.69%  |
| Real Estate            | 21   | 0.81%  |
| Utilities              | 9    | 0.35%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 120  | 24     | 9      | Consumer Cyclical      | 20.00%        |
| 2006 | 120  | 31     | 7      | Consumer Cyclical      | 20.00%        |
| 2007 | 120  | 32     | 8      | Industrials            | 20.00%        |
| 2008 | 120  | 29     | 7      | Healthcare             | 20.00%        |
| 2009 | 120  | 32     | 10     | Healthcare             | 20.00%        |
| 2010 | 120  | 27     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 120  | 30     | 9      | Consumer Cyclical      | 20.00%        |
| 2012 | 120  | 31     | 9      | Consumer Defensive     | 20.00%        |
| 2013 | 120  | 32     | 8      | Communication Services | 20.00%        |
| 2014 | 120  | 30     | 7      | Industrials            | 20.00%        |
| 2015 | 120  | 25     | 8      | Consumer Defensive     | 20.00%        |
| 2016 | 120  | 28     | 8      | Technology             | 20.00%        |
| 2017 | 120  | 29     | 9      | Consumer Cyclical      | 20.00%        |
| 2018 | 120  | 28     | 8      | Consumer Cyclical      | 20.00%        |
| 2019 | 120  | 30     | 7      | Consumer Defensive     | 20.00%        |
| 2020 | 120  | 32     | 8      | Consumer Defensive     | 17.50%        |
| 2021 | 120  | 34     | 7      | Consumer Cyclical      | 20.00%        |
| 2022 | 120  | 34     | 9      | Healthcare             | 20.00%        |
| 2023 | 120  | 29     | 8      | Healthcare             | 20.00%        |
| 2024 | 120  | 28     | 7      | Technology             | 20.00%        |
| 2025 | 120  | 27     | 8      | Technology             | 17.50%        |
| 2026 | 80   | 24     | 8      | Technology             | 20.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | -2.08%         | -4.86%           | 40.00%  | 34.17%  | 0.00%         | 120  | -5.69%         | -0.38%           | 47.50%  | 42.50%  | 10.00%        |
| 2006     | 120  | 120  | -11.46%        | -11.95%          | 25.83%  | 43.33%  | 5.00%         | 120  | 1.39%          | 2.19%            | 60.83%  | 73.33%  | 6.67%         |
| 2007     | 120  | 120  | 4.99%          | 4.77%            | 64.17%  | 58.33%  | 1.67%         | 120  | 7.64%          | 7.59%            | 80.00%  | 43.33%  | 11.67%        |
| 2008     | 120  | 120  | 9.78%          | 11.35%           | 65.83%  | 76.67%  | 0.83%         | 120  | 7.82%          | 7.91%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 120  | 120  | 6.82%          | 7.96%            | 59.17%  | 12.50%  | 6.67%         | 120  | 0.19%          | -0.16%           | 48.33%  | 8.33%   | 10.83%        |
| 2010     | 120  | 120  | 22.93%         | 18.01%           | 74.17%  | 8.33%   | 1.67%         | 120  | 10.58%         | 9.75%            | 79.17%  | 1.67%   | 5.00%         |
| 2011     | 120  | 120  | 11.02%         | 11.55%           | 67.50%  | 17.50%  | 5.00%         | 120  | 5.16%          | 4.63%            | 70.83%  | 5.83%   | 7.50%         |
| 2012     | 120  | 120  | -0.02%         | -3.05%           | 45.00%  | 15.00%  | 0.00%         | 120  | -0.91%         | 3.56%            | 56.67%  | 16.67%  | 0.83%         |
| 2013     | 120  | 120  | -0.08%         | -0.51%           | 47.50%  | 13.33%  | 2.50%         | 120  | 2.24%          | 2.84%            | 64.17%  | 16.67%  | 5.00%         |
| 2014     | 120  | 120  | 12.57%         | 16.05%           | 75.00%  | 15.83%  | 1.67%         | 120  | 3.59%          | 3.75%            | 58.33%  | 17.50%  | 9.17%         |
| 2015     | 120  | 120  | 4.00%          | 3.06%            | 58.33%  | 31.67%  | 0.00%         | 120  | 3.10%          | 5.47%            | 65.83%  | 13.33%  | 2.50%         |
| 2016     | 120  | 120  | -2.85%         | -3.08%           | 40.00%  | 14.17%  | 2.50%         | 120  | 1.82%          | 4.38%            | 62.50%  | 15.83%  | 5.00%         |
| 2017     | 120  | 120  | 2.48%          | 0.65%            | 50.83%  | 22.50%  | 4.17%         | 120  | 2.33%          | 0.76%            | 55.83%  | 19.17%  | 12.50%        |
| 2018     | 120  | 120  | 12.11%         | 8.44%            | 76.67%  | 17.50%  | 0.00%         | 120  | 3.38%          | 1.39%            | 53.33%  | 8.33%   | 5.83%         |
| 2019     | 120  | 120  | -1.97%         | -1.45%           | 45.00%  | 33.33%  | 0.00%         | 120  | -5.03%         | -5.94%           | 20.00%  | 13.33%  | 0.00%         |
| 2020     | 120  | 120  | -14.03%        | -16.06%          | 32.50%  | 28.33%  | 0.00%         | 120  | -2.69%         | -3.58%           | 39.17%  | 21.67%  | 7.50%         |
| 2021     | 120  | 120  | -15.36%        | -13.22%          | 21.67%  | 71.67%  | 0.00%         | 120  | -13.80%        | -8.09%           | 23.33%  | 45.83%  | 0.00%         |
| 2022     | 120  | 120  | -1.71%         | -3.02%           | 40.00%  | 50.00%  | 0.00%         | 120  | -8.70%         | -7.68%           | 29.17%  | 25.00%  | 5.00%         |
| 2023     | 120  | 120  | -9.95%         | -12.10%          | 28.33%  | 30.83%  | 0.00%         | 80   | -13.50%        | -15.84%          | 21.25%  | 28.75%  | 0.00%         |
| 2024     | 120  | 120  | -4.08%         | -3.58%           | 43.33%  | 32.50%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2025     | 120  | 80   | -20.76%        | -16.55%          | 22.50%  | 42.50%  | 8.75%         | 0    | —              | —                | —       | —       | —             |
| 2026     | 80   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2600 | 2480 | 0.45%          | -0.30%           | 49.15%  | 31.73%  | 1.81%         | 2240 | 0.18%          | 1.25%            | 54.46%  | 22.32%  | 5.80%         |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 0
- mean stocks in the point-in-time cross-section: 4080.3 (min 3653)
- mean after the per-model min_score floor: 4080.3 (min 3653)
- mean after the column filters: 4080.3 (min 3653)
- mean after the investability filter: 3258.0 (min 2923)
- mean with a tradable quote: 3178.2 (min 2870)
- criteria sells: 345 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 3 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 36 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Simulated year-end refits

One refit per (bundle, trade year) past that bundle's folds — trained on rows whose labels were observable by Jan 1, all snapshot kinds, delistings included, no split tags read. `source = cache` rows were reused from the refit cache (identical by construction: the cache key pins train config, dataset version, year, and label lag):

| bundle                   | trade_year | n_train_rows | effective_train_size | last_usable_snapshot | source |
| ------------------------ | ---------- | ------------ | -------------------- | -------------------- | ------ |
| forest_nonloser_dd30_3y  | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| forest_nonloser_dd30_3y  | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| forest_nonloser_dd30_3y  | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |
| forest_nonloser_dd30_3y  | 2024       | 1242554      | 42885.4000           | 2020-11-17           | cache  |
| forest_nonloser_dd30_3y  | 2025       | 1293773      | 44742                | 2021-11-17           | cache  |
| forest_nonloser_dd30_3y  | 2026       | 1349041      | 46690.5000           | 2022-11-17           | cache  |
| factor_mom_12_2_3y       | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| factor_mom_12_2_3y       | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| factor_mom_12_2_3y       | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |
| factor_mom_12_2_3y       | 2024       | 1242554      | 42885.4000           | 2020-11-17           | cache  |
| factor_mom_12_2_3y       | 2025       | 1293773      | 44742                | 2021-11-17           | cache  |
| factor_mom_12_2_3y       | 2026       | 1349041      | 46690.5000           | 2022-11-17           | cache  |
| factor_roc_greenblatt_3y | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| factor_roc_greenblatt_3y | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| factor_roc_greenblatt_3y | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |
| factor_roc_greenblatt_3y | 2024       | 1242554      | 42885.4000           | 2020-11-17           | cache  |
| factor_roc_greenblatt_3y | 2025       | 1293773      | 44742                | 2021-11-17           | cache  |
| factor_roc_greenblatt_3y | 2026       | 1349041      | 46690.5000           | 2022-11-17           | cache  |

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_frac_to2026_d5812ac1d6401831_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_frac_to2026_d5812ac1d6401831_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_frac_to2026_d5812ac1d6401831_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_frac_to2026_d5812ac1d6401831_equity.png`
