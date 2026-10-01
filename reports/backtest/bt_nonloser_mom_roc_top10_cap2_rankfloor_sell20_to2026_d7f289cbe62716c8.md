# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026

- run `d0d6d5105bce`, git `2fc9496c18d33f54b327fb18eff37ca0cfabe52f`, backtest config `d7f289cbe62716c8`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ------------ | -------------- | -------- | ------------ | ---------- |
| strategy  | 260,000.00 | 1,344,629.79 | 1,084,629.79 | 13.31%         | 11.99%   | -39.64%      | 14,725.06  |
| benchmark | 260,000.00 | 1,326,083.97 | 1,066,083.97 | 13.20%         | 10.93%   | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 4.12%        | 6.51%         | -2.39%  | 12,000.00 | 108    | -365.6883       |
| 2006              | 10.17%       | 12.67%        | -2.50%  | 12,000.00 | 120    | -383.1056       |
| 2007              | 2.38%        | 7.28%         | -4.90%  | 12,000.00 | 118    | -343.8362       |
| 2008 (GFC)        | -32.42%      | -43.21%       | 10.79%  | 12,000.00 | 120    | -299.0500       |
| 2009 (GFC)        | 36.58%       | 39.07%        | -2.49%  | 12,000.00 | 117    | -209.2707       |
| 2010              | 28.75%       | 10.86%        | 17.89%  | 12,000.00 | 120    | -383.7250       |
| 2011              | 16.75%       | 5.33%         | 11.43%  | 12,000.00 | 112    | -297.9077       |
| 2012              | 15.48%       | 15.60%        | -0.12%  | 12,000.00 | 111    | -195.5255       |
| 2013              | 24.54%       | 30.42%        | -5.88%  | 12,000.00 | 116    | -263.0632       |
| 2014              | 18.48%       | 16.18%        | 2.29%   | 12,000.00 | 113    | -296.0531       |
| 2015              | 17.33%       | 4.46%         | 12.86%  | 12,000.00 | 107    | -198.9502       |
| 2016              | 7.02%        | 6.48%         | 0.54%   | 12,000.00 | 110    | -186.2303       |
| 2017              | 23.89%       | 22.88%        | 1.02%   | 12,000.00 | 107    | -287.8567       |
| 2018              | 16.43%       | 7.53%         | 8.90%   | 12,000.00 | 99     | -253.9495       |
| 2019              | 26.14%       | 13.81%        | 12.33%  | 12,000.00 | 100    | -214.6367       |
| 2020 (COVID)      | 19.87%       | 19.77%        | 0.11%   | 12,000.00 | 98     | -204.9252       |
| 2021              | 16.29%       | 24.82%        | -8.53%  | 12,000.00 | 90     | -333.6852       |
| 2022 (rate-shock) | -7.22%       | -8.20%        | 0.99%   | 12,000.00 | 93     | -240.1720       |
| 2023              | 8.15%        | 14.48%        | -6.33%  | 12,000.00 | 90     | -220.8556       |
| 2024              | 26.67%       | 33.26%        | -6.59%  | 12,000.00 | 83     | -252.1365       |
| 2025              | 0.48%        | 14.06%        | -13.58% | 12,000.00 | 97     | -236.1478       |
| 2026              | 2.48%        | 13.49%        | -11.01% | 8,000.00  | 59     | -296.0621       |

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
| Technology             | 383  | 16.74% |
| Consumer Defensive     | 379  | 16.56% |
| Industrials            | 377  | 16.48% |
| Healthcare             | 354  | 15.47% |
| Consumer Cyclical      | 329  | 14.38% |
| Basic Materials        | 193  | 8.44%  |
| Communication Services | 119  | 5.20%  |
| Financial Services     | 84   | 3.67%  |
| Energy                 | 44   | 1.92%  |
| Real Estate            | 17   | 0.74%  |
| Utilities              | 9    | 0.39%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 23     | 9      | Industrials            | 19.44%        |
| 2006 | 120  | 31     | 7      | Consumer Cyclical      | 20.00%        |
| 2007 | 118  | 32     | 8      | Industrials            | 18.64%        |
| 2008 | 120  | 29     | 7      | Healthcare             | 20.00%        |
| 2009 | 117  | 32     | 10     | Healthcare             | 20.51%        |
| 2010 | 120  | 27     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 112  | 30     | 9      | Consumer Defensive     | 21.43%        |
| 2012 | 111  | 31     | 9      | Consumer Defensive     | 21.62%        |
| 2013 | 116  | 32     | 8      | Communication Services | 20.69%        |
| 2014 | 113  | 30     | 7      | Technology             | 21.24%        |
| 2015 | 107  | 25     | 8      | Technology             | 19.63%        |
| 2016 | 110  | 28     | 8      | Technology             | 21.82%        |
| 2017 | 107  | 29     | 9      | Industrials            | 21.50%        |
| 2018 | 99   | 27     | 8      | Consumer Cyclical      | 24.24%        |
| 2019 | 100  | 30     | 7      | Consumer Defensive     | 24.00%        |
| 2020 | 98   | 32     | 8      | Technology             | 20.41%        |
| 2021 | 90   | 32     | 7      | Consumer Cyclical      | 23.33%        |
| 2022 | 93   | 34     | 9      | Healthcare             | 20.43%        |
| 2023 | 90   | 29     | 8      | Technology             | 26.67%        |
| 2024 | 83   | 28     | 7      | Technology             | 24.10%        |
| 2025 | 97   | 27     | 8      | Consumer Defensive     | 20.62%        |
| 2026 | 59   | 23     | 8      | Technology             | 20.34%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.31%         | -6.71%           | 34.26%  | 37.96%  | 0.00%         | 108  | -5.57%         | 0.25%            | 51.85%  | 40.74%  | 11.11%        |
| 2006     | 120  | 120  | -11.46%        | -11.95%          | 25.83%  | 43.33%  | 5.00%         | 120  | 1.39%          | 2.19%            | 60.83%  | 73.33%  | 6.67%         |
| 2007     | 118  | 118  | 5.46%          | 5.33%            | 65.25%  | 57.63%  | 1.69%         | 118  | 7.72%          | 7.74%            | 79.66%  | 42.37%  | 11.86%        |
| 2008     | 120  | 120  | 9.78%          | 11.35%           | 65.83%  | 76.67%  | 0.83%         | 120  | 7.82%          | 7.91%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 117  | 117  | 5.94%          | 7.22%            | 58.12%  | 12.82%  | 6.84%         | 117  | -0.38%         | -0.26%           | 47.01%  | 8.55%   | 11.11%        |
| 2010     | 120  | 120  | 22.93%         | 18.01%           | 74.17%  | 8.33%   | 1.67%         | 120  | 10.58%         | 9.75%            | 79.17%  | 1.67%   | 5.00%         |
| 2011     | 112  | 112  | 10.50%         | 10.86%           | 67.86%  | 18.75%  | 5.36%         | 112  | 5.15%          | 4.44%            | 71.43%  | 6.25%   | 8.04%         |
| 2012     | 111  | 111  | -0.48%         | -3.27%           | 45.05%  | 15.32%  | 0.00%         | 111  | 0.14%          | 4.51%            | 57.66%  | 15.32%  | 0.90%         |
| 2013     | 116  | 116  | -0.28%         | -0.75%           | 46.55%  | 13.79%  | 2.59%         | 116  | 2.41%          | 3.68%            | 64.66%  | 17.24%  | 5.17%         |
| 2014     | 113  | 113  | 12.11%         | 15.80%           | 73.45%  | 16.81%  | 1.77%         | 113  | 3.49%          | 3.43%            | 57.52%  | 16.81%  | 8.85%         |
| 2015     | 107  | 107  | 6.00%          | 3.96%            | 62.62%  | 26.17%  | 0.00%         | 107  | 3.86%          | 5.91%            | 69.16%  | 13.08%  | 2.80%         |
| 2016     | 110  | 110  | -2.80%         | -4.05%           | 39.09%  | 13.64%  | 2.73%         | 110  | 1.43%          | 4.10%            | 61.82%  | 17.27%  | 5.45%         |
| 2017     | 107  | 107  | 0.74%          | -1.86%           | 45.79%  | 24.30%  | 4.67%         | 107  | 1.38%          | 0.22%            | 51.40%  | 20.56%  | 14.02%        |
| 2018     | 99   | 99   | 11.30%         | 7.15%            | 74.75%  | 18.18%  | 0.00%         | 99   | 4.02%          | 2.70%            | 53.54%  | 6.06%   | 6.06%         |
| 2019     | 100  | 100  | -3.68%         | -3.50%           | 43.00%  | 37.00%  | 0.00%         | 100  | -5.14%         | -5.94%           | 20.00%  | 12.00%  | 0.00%         |
| 2020     | 98   | 98   | -13.30%        | -15.05%          | 35.71%  | 27.55%  | 0.00%         | 98   | -1.85%         | -1.67%           | 42.86%  | 22.45%  | 9.18%         |
| 2021     | 90   | 90   | -15.73%        | -13.33%          | 21.11%  | 74.44%  | 0.00%         | 90   | -12.87%        | -5.72%           | 26.67%  | 41.11%  | 0.00%         |
| 2022     | 93   | 93   | -2.53%         | -5.78%           | 37.63%  | 53.76%  | 0.00%         | 93   | -9.63%         | -9.72%           | 27.96%  | 30.11%  | 6.45%         |
| 2023     | 90   | 90   | -9.34%         | -11.71%          | 28.89%  | 30.00%  | 0.00%         | 62   | -15.72%        | -18.80%          | 19.35%  | 35.48%  | 0.00%         |
| 2024     | 83   | 83   | -4.52%         | -5.12%           | 42.17%  | 37.35%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2025     | 97   | 67   | -20.50%        | -16.63%          | 23.88%  | 43.28%  | 10.45%        | 0    | —              | —                | —       | —       | —             |
| 2026     | 59   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2288 | 2199 | 0.73%          | -0.21%           | 49.39%  | 32.11%  | 2.05%         | 2021 | 0.64%          | 1.62%            | 56.21%  | 22.27%  | 6.33%         |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 128
- mean stocks in the point-in-time cross-section: 4080.3 (min 3653)
- mean after the per-model min_score floor: 4080.3 (min 3653)
- mean after the column filters: 4080.3 (min 3653)
- mean after the investability filter: 3258.0 (min 2923)
- mean with a tradable quote: 3178.2 (min 2870)
- criteria sells: 343 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 3 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 34 (this one included; every run is logged, failures too)
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

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_d7f289cbe62716c8_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_d7f289cbe62716c8_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_d7f289cbe62716c8_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_d7f289cbe62716c8_equity.png`
