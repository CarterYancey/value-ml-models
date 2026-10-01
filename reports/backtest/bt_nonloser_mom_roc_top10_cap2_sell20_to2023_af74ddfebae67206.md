# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_sell20_to2023

- run `032e873c1cb5`, git `295d71b84d154c875a993defd3f9571d934ea0a1`, backtest config `af74ddfebae67206`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2023 (last buy 2023-12-29), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 228,000.00 | 1,054,923.80 | 826,923.80 | 14.32%         | 12.70%   | -39.49%      | 8,672.84   |
| benchmark | 228,000.00 | 774,140.22   | 546,140.22 | 11.61%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 7.66%        | 6.51%         | 1.14%  | 12,000.00 | 108    | -345.7037       |
| 2006              | 10.07%       | 12.67%        | -2.59% | 12,000.00 | 120    | -369.3444       |
| 2007              | 2.75%        | 7.28%         | -4.53% | 12,000.00 | 118    | -336.0480       |
| 2008 (GFC)        | -33.08%      | -43.21%       | 10.13% | 12,000.00 | 120    | -287.2333       |
| 2009 (GFC)        | 41.23%       | 39.07%        | 2.16%  | 12,000.00 | 117    | -189.4701       |
| 2010              | 26.51%       | 10.86%        | 15.65% | 12,000.00 | 120    | -367.5778       |
| 2011              | 16.81%       | 5.33%         | 11.49% | 12,000.00 | 113    | -290.5546       |
| 2012              | 15.58%       | 15.60%        | -0.02% | 12,000.00 | 110    | -189.2758       |
| 2013              | 23.73%       | 30.42%        | -6.69% | 12,000.00 | 116    | -258.4483       |
| 2014              | 19.51%       | 16.18%        | 3.33%  | 12,000.00 | 111    | -302.3063       |
| 2015              | 17.10%       | 4.46%         | 12.63% | 12,000.00 | 107    | -202.5483       |
| 2016              | 6.63%        | 6.48%         | 0.16%  | 12,000.00 | 109    | -187.6850       |
| 2017              | 23.83%       | 22.88%        | 0.95%  | 12,000.00 | 107    | -293.0717       |
| 2018              | 16.13%       | 7.53%         | 8.60%  | 12,000.00 | 101    | -260.5248       |
| 2019              | 26.75%       | 13.81%        | 12.94% | 12,000.00 | 103    | -219.7961       |
| 2020 (COVID)      | 19.91%       | 19.77%        | 0.15%  | 12,000.00 | 98     | -210.6020       |
| 2021              | 16.95%       | 24.82%        | -7.87% | 12,000.00 | 96     | -358.8889       |
| 2022 (rate-shock) | -7.04%       | -8.20%        | 1.16%  | 12,000.00 | 92     | -250.8225       |
| 2023              | 12.28%       | 19.01%        | -6.72% | 12,000.00 | 89     | -218.8315       |

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
| Industrials            | 343  | 16.69% |
| Consumer Defensive     | 339  | 16.50% |
| Technology             | 327  | 15.91% |
| Healthcare             | 317  | 15.43% |
| Consumer Cyclical      | 310  | 15.09% |
| Basic Materials        | 163  | 7.93%  |
| Communication Services | 108  | 5.26%  |
| Financial Services     | 81   | 3.94%  |
| Energy                 | 42   | 2.04%  |
| Real Estate            | 16   | 0.78%  |
| Utilities              | 9    | 0.44%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 26     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 29     | 7      | Industrials        | 20.00%        |
| 2007 | 118  | 31     | 8      | Industrials        | 18.64%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 117  | 33     | 10     | Healthcare         | 20.51%        |
| 2010 | 120  | 28     | 9      | Consumer Defensive | 20.00%        |
| 2011 | 113  | 30     | 9      | Consumer Defensive | 21.24%        |
| 2012 | 110  | 31     | 9      | Consumer Defensive | 21.82%        |
| 2013 | 116  | 33     | 8      | Healthcare         | 18.97%        |
| 2014 | 111  | 27     | 7      | Technology         | 21.62%        |
| 2015 | 107  | 24     | 8      | Technology         | 19.63%        |
| 2016 | 109  | 28     | 8      | Consumer Defensive | 22.02%        |
| 2017 | 107  | 29     | 9      | Industrials        | 21.50%        |
| 2018 | 101  | 26     | 8      | Consumer Cyclical  | 23.76%        |
| 2019 | 103  | 29     | 7      | Consumer Defensive | 23.30%        |
| 2020 | 98   | 32     | 8      | Technology         | 20.41%        |
| 2021 | 96   | 33     | 7      | Technology         | 20.83%        |
| 2022 | 92   | 34     | 9      | Industrials        | 20.65%        |
| 2023 | 89   | 29     | 8      | Technology         | 26.97%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.23%         | -5.65%           | 37.04%  | 37.04%  | 0.00%         | 108  | -5.46%         | 0.56%            | 54.63%  | 40.74%  | 8.33%         |
| 2006     | 120  | 120  | -11.03%        | -11.95%          | 26.67%  | 43.33%  | 5.00%         | 120  | 1.81%          | 2.05%            | 60.00%  | 71.67%  | 5.00%         |
| 2007     | 118  | 118  | 4.78%          | 5.33%            | 66.10%  | 58.47%  | 1.69%         | 118  | 8.29%          | 7.87%            | 82.20%  | 40.68%  | 11.86%        |
| 2008     | 120  | 120  | 9.44%          | 11.35%           | 66.67%  | 77.50%  | 0.83%         | 120  | 7.63%          | 7.76%            | 86.67%  | 10.00%  | 3.33%         |
| 2009     | 117  | 117  | 5.92%          | 7.22%            | 58.12%  | 12.82%  | 6.84%         | 117  | -0.69%         | -0.58%           | 45.30%  | 8.55%   | 11.11%        |
| 2010     | 120  | 120  | 21.81%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 9.43%          | 8.82%            | 79.17%  | 1.67%   | 6.67%         |
| 2011     | 113  | 113  | 9.94%          | 8.39%            | 67.26%  | 18.58%  | 5.31%         | 113  | 5.27%          | 4.79%            | 73.45%  | 6.19%   | 7.96%         |
| 2012     | 110  | 110  | -0.50%         | -3.05%           | 45.45%  | 15.45%  | 0.00%         | 110  | -0.41%         | 4.49%            | 56.36%  | 17.27%  | 0.91%         |
| 2013     | 116  | 116  | -0.60%         | -0.75%           | 44.83%  | 13.79%  | 2.59%         | 116  | 2.78%          | 4.08%            | 67.24%  | 15.52%  | 5.17%         |
| 2014     | 111  | 111  | 13.49%         | 16.30%           | 74.77%  | 17.12%  | 4.50%         | 111  | 4.22%          | 4.14%            | 62.16%  | 13.51%  | 10.81%        |
| 2015     | 107  | 107  | 5.48%          | 3.74%            | 61.68%  | 27.10%  | 0.00%         | 107  | 3.88%          | 5.81%            | 70.09%  | 13.08%  | 2.80%         |
| 2016     | 109  | 109  | -2.84%         | -4.04%           | 38.53%  | 13.76%  | 2.75%         | 109  | 1.41%          | 3.94%            | 61.47%  | 17.43%  | 5.50%         |
| 2017     | 107  | 107  | 0.74%          | -1.86%           | 45.79%  | 24.30%  | 4.67%         | 107  | 1.38%          | 0.22%            | 51.40%  | 20.56%  | 14.02%        |
| 2018     | 101  | 101  | 10.91%         | 6.87%            | 73.27%  | 19.80%  | 0.00%         | 101  | 3.40%          | 1.61%            | 51.49%  | 5.94%   | 5.94%         |
| 2019     | 103  | 103  | -3.60%         | -4.37%           | 42.72%  | 37.86%  | 0.00%         | 103  | -5.11%         | -6.09%           | 20.39%  | 12.62%  | 0.00%         |
| 2020     | 98   | 98   | -13.30%        | -15.05%          | 35.71%  | 27.55%  | 0.00%         | 98   | -1.85%         | -1.67%           | 42.86%  | 22.45%  | 9.18%         |
| 2021     | 96   | 96   | -15.34%        | -13.34%          | 21.88%  | 72.92%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2022     | 92   | 92   | -1.77%         | -5.70%           | 38.04%  | 53.26%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2023     | 89   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2055 | 1966 | 2.02%          | 1.03%            | 51.63%  | 31.89%  | 2.09%         | 1778 | 2.40%          | 3.31%            | 60.97%  | 20.08%  | 6.81%         |

## Coverage & diagnostics

- rebalance months: 228; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 108
- mean stocks in the point-in-time cross-section: 4107.5 (min 3653)
- mean after the per-model min_score floor: 4107.5 (min 3653)
- mean after the column filters: 4107.5 (min 3653)
- mean after the investability filter: 3243.1 (min 2669)
- mean with a tradable quote: 3166.4 (min 2640)
- criteria sells: 287 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 3 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 29 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `087f2d7dfea489b2`, train run `53ceedd93e6d`, folds 2005–2020; 2021–2023 served by year-end refits (from `experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020; 2021–2023 served by year-end refits (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020; 2021–2023 served by year-end refits (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Simulated year-end refits

One refit per (bundle, trade year) past that bundle's folds — trained on rows whose labels were observable by Jan 1, all snapshot kinds, delistings included, no split tags read. `source = cache` rows were reused from the refit cache (identical by construction: the cache key pins train config, dataset version, year, and label lag):

| bundle                   | trade_year | n_train_rows | effective_train_size | last_usable_snapshot | source |
| ------------------------ | ---------- | ------------ | -------------------- | -------------------- | ------ |
| forest_nonloser_dd30_3y  | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| forest_nonloser_dd30_3y  | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| forest_nonloser_dd30_3y  | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |
| factor_mom_12_2_3y       | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| factor_mom_12_2_3y       | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| factor_mom_12_2_3y       | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |
| factor_roc_greenblatt_3y | 2021       | 1109611      | 38597.9000           | 2017-11-17           | cache  |
| factor_roc_greenblatt_3y | 2022       | 1153516      | 40022.4000           | 2018-11-16           | cache  |
| factor_roc_greenblatt_3y | 2023       | 1198004      | 41447.9000           | 2019-11-15           | cache  |

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_to2023_af74ddfebae67206_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_to2023_af74ddfebae67206_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_to2023_af74ddfebae67206_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_to2023_af74ddfebae67206_equity.png`
