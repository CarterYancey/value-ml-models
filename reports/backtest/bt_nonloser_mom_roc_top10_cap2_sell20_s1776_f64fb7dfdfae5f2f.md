# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_sell20_s1776

- run `843f8a0f3377`, git `0b8c053e4592471721d4f16d3f3d529ee814b140`, backtest config `f64fb7dfdfae5f2f`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 1,028,084.79 | 836,084.79 | 14.46%         | 12.66%   | -40.52%      | 4,899.46   |
| benchmark | 192,000.00 | 732,110.07   | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 8.72%        | 6.51%         | 2.21%  | 12,000.00 | 108    | -341.5278       |
| 2006              | 8.48%        | 12.67%        | -4.19% | 12,000.00 | 120    | -375.1194       |
| 2007              | 2.26%        | 7.28%         | -5.02% | 12,000.00 | 118    | -334.8446       |
| 2008 (GFC)        | -33.12%      | -43.21%       | 10.09% | 12,000.00 | 120    | -286.2361       |
| 2009 (GFC)        | 38.33%       | 39.07%        | -0.74% | 12,000.00 | 117    | -191.5214       |
| 2010              | 28.76%       | 10.86%        | 17.90% | 12,000.00 | 120    | -366.8361       |
| 2011              | 12.62%       | 5.33%         | 7.29%  | 12,000.00 | 112    | -289.3274       |
| 2012              | 15.99%       | 15.60%        | 0.39%  | 12,000.00 | 111    | -193.1201       |
| 2013              | 24.74%       | 30.42%        | -5.68% | 12,000.00 | 116    | -262.9856       |
| 2014              | 19.23%       | 16.18%        | 3.04%  | 12,000.00 | 113    | -299.3894       |
| 2015              | 17.30%       | 4.46%         | 12.83% | 12,000.00 | 110    | -204.3970       |
| 2016              | 6.88%        | 6.48%         | 0.40%  | 12,000.00 | 112    | -188.2470       |
| 2017              | 23.72%       | 22.88%        | 0.85%  | 12,000.00 | 105    | -295.3619       |
| 2018              | 16.49%       | 7.53%         | 8.96%  | 12,000.00 | 100    | -263.6800       |
| 2019              | 24.74%       | 13.81%        | 10.93% | 12,000.00 | 103    | -222.5275       |
| 2020 (COVID)      | 19.84%       | 19.77%        | 0.08%  | 12,000.00 | 99     | -208.0741       |
| 2021              | 15.20%       | 24.81%        | -9.61% | 0.00      | 0      | —               |
| 2022 (rate-shock) | -1.92%       | -8.20%        | 6.28%  | 0.00      | 0      | —               |
| 2023              | 12.92%       | 19.00%        | -6.08% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 309  | 17.32% |
| Healthcare             | 293  | 16.42% |
| Industrials            | 280  | 15.70% |
| Consumer Cyclical      | 274  | 15.36% |
| Technology             | 270  | 15.13% |
| Basic Materials        | 117  | 6.56%  |
| Communication Services | 95   | 5.33%  |
| Financial Services     | 75   | 4.20%  |
| Energy                 | 42   | 2.35%  |
| Real Estate            | 20   | 1.12%  |
| Utilities              | 9    | 0.50%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 24     | 9      | Industrials        | 19.44%        |
| 2006 | 120  | 31     | 8      | Healthcare         | 20.00%        |
| 2007 | 118  | 33     | 9      | Industrials        | 18.64%        |
| 2008 | 120  | 31     | 7      | Healthcare         | 20.00%        |
| 2009 | 117  | 32     | 10     | Healthcare         | 20.51%        |
| 2010 | 120  | 31     | 8      | Consumer Defensive | 17.50%        |
| 2011 | 112  | 29     | 9      | Consumer Defensive | 18.75%        |
| 2012 | 111  | 32     | 9      | Consumer Defensive | 21.62%        |
| 2013 | 116  | 31     | 8      | Healthcare         | 18.10%        |
| 2014 | 113  | 27     | 7      | Technology         | 21.24%        |
| 2015 | 110  | 27     | 8      | Consumer Defensive | 20.00%        |
| 2016 | 112  | 29     | 7      | Consumer Defensive | 21.43%        |
| 2017 | 105  | 29     | 9      | Consumer Cyclical  | 20.95%        |
| 2018 | 100  | 26     | 8      | Consumer Cyclical  | 24.00%        |
| 2019 | 103  | 28     | 7      | Consumer Defensive | 23.30%        |
| 2020 | 99   | 33     | 8      | Consumer Defensive | 20.20%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -1.93%         | -4.86%           | 38.89%  | 35.19%  | 2.78%         | 108  | -3.71%         | 0.65%            | 58.33%  | 37.96%  | 11.11%        |
| 2006     | 120  | 120  | -11.69%        | -11.95%          | 28.33%  | 44.17%  | 5.00%         | 120  | 0.79%          | 1.97%            | 60.00%  | 78.33%  | 7.50%         |
| 2007     | 118  | 118  | 3.76%          | 4.65%            | 62.71%  | 61.02%  | 1.69%         | 118  | 7.51%          | 7.34%            | 77.97%  | 45.76%  | 11.86%        |
| 2008     | 120  | 120  | 9.53%          | 11.35%           | 66.67%  | 77.50%  | 0.83%         | 120  | 7.88%          | 8.08%            | 86.67%  | 10.00%  | 3.33%         |
| 2009     | 117  | 117  | 5.74%          | 5.41%            | 58.12%  | 11.97%  | 6.84%         | 117  | 0.09%          | -0.22%           | 47.86%  | 5.98%   | 11.11%        |
| 2010     | 120  | 120  | 25.67%         | 18.01%           | 75.00%  | 7.50%   | 4.17%         | 120  | 8.59%          | 7.50%            | 78.33%  | 1.67%   | 6.67%         |
| 2011     | 112  | 112  | 13.01%         | 12.70%           | 68.75%  | 16.96%  | 5.36%         | 112  | 5.99%          | 5.65%            | 74.11%  | 6.25%   | 5.36%         |
| 2012     | 111  | 111  | -0.21%         | -1.02%           | 47.75%  | 14.41%  | 0.00%         | 111  | -0.31%         | 4.51%            | 57.66%  | 18.02%  | 0.90%         |
| 2013     | 116  | 116  | 1.16%          | -0.50%           | 47.41%  | 11.21%  | 2.59%         | 116  | 2.65%          | 3.95%            | 65.52%  | 15.52%  | 5.17%         |
| 2014     | 113  | 113  | 13.77%         | 17.67%           | 75.22%  | 16.81%  | 0.00%         | 113  | 3.53%          | 3.22%            | 57.52%  | 15.04%  | 6.19%         |
| 2015     | 110  | 110  | 4.03%          | 2.88%            | 57.27%  | 31.82%  | 0.00%         | 110  | 2.55%          | 5.47%            | 67.27%  | 16.36%  | 2.73%         |
| 2016     | 112  | 112  | -0.31%         | -2.56%           | 44.64%  | 11.61%  | 2.68%         | 112  | 2.41%          | 4.80%            | 68.75%  | 16.96%  | 8.04%         |
| 2017     | 105  | 105  | -0.04%         | -2.41%           | 44.76%  | 24.76%  | 4.76%         | 105  | 2.28%          | 0.55%            | 54.29%  | 19.05%  | 15.24%        |
| 2018     | 100  | 100  | 9.37%          | 6.83%            | 73.00%  | 21.00%  | 0.00%         | 100  | 4.15%          | 1.67%            | 52.00%  | 6.00%   | 7.00%         |
| 2019     | 103  | 103  | -3.94%         | -5.13%           | 41.75%  | 36.89%  | 0.00%         | 103  | -5.46%         | -5.58%           | 20.39%  | 11.65%  | 0.00%         |
| 2020     | 99   | 99   | -15.36%        | -21.24%          | 32.32%  | 29.29%  | 0.00%         | 99   | -3.21%         | -6.02%           | 36.36%  | 27.27%  | 9.09%         |
| all buys | 1784 | 1784 | 3.51%          | 2.37%            | 54.15%  | 28.48%  | 2.35%         | 1784 | 2.37%          | 2.99%            | 60.87%  | 20.96%  | 6.95%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 84
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 228 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 6 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 26 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s1776_f64fb7dfdfae5f2f_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s1776_f64fb7dfdfae5f2f_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s1776_f64fb7dfdfae5f2f_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_sell20_s1776_f64fb7dfdfae5f2f_equity.png`
