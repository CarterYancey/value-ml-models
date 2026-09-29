# Portfolio backtest — bt_nonloser_mom_top10_cap2_s1776

- run `a1c54ae28c5f`, git `67085188347ba3b65da380d4f8f0329ff997ac3f`, backtest config `5552bd33d02ed4e4`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 717,484.61  | 525,484.61 | 11.45%         | 11.11%   | -48.51%      | 1,641.26   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 17.19%       | 6.51%         | 10.68%  | 12,000.00 | 105    | -314.8905       |
| 2006              | 18.80%       | 12.67%        | 6.13%   | 12,000.00 | 117    | -378.4530       |
| 2007              | 7.85%        | 7.28%         | 0.57%   | 12,000.00 | 117    | -292.2607       |
| 2008 (GFC)        | -41.64%      | -43.21%       | 1.57%   | 12,000.00 | 120    | -251.3458       |
| 2009 (GFC)        | 47.16%       | 39.07%        | 8.09%   | 12,000.00 | 115    | -133.3087       |
| 2010              | 27.98%       | 10.86%        | 17.12%  | 12,000.00 | 120    | -380.4750       |
| 2011              | 12.30%       | 5.33%         | 6.98%   | 12,000.00 | 115    | -311.9435       |
| 2012              | 10.07%       | 15.60%        | -5.53%  | 12,000.00 | 112    | -173.3036       |
| 2013              | 30.35%       | 30.42%        | -0.07%  | 12,000.00 | 119    | -259.3193       |
| 2014              | 15.02%       | 16.18%        | -1.16%  | 12,000.00 | 108    | -318.0833       |
| 2015              | 0.39%        | 4.46%         | -4.07%  | 12,000.00 | 117    | -217.4060       |
| 2016              | 10.06%       | 6.48%         | 3.58%   | 12,000.00 | 113    | -165.4115       |
| 2017              | 17.74%       | 22.88%        | -5.14%  | 12,000.00 | 112    | -301.3438       |
| 2018              | 9.54%        | 7.53%         | 2.00%   | 12,000.00 | 101    | -301.1881       |
| 2019              | 16.12%       | 13.81%        | 2.31%   | 12,000.00 | 107    | -209.5327       |
| 2020 (COVID)      | 11.72%       | 19.77%        | -8.05%  | 12,000.00 | 89     | -201.6404       |
| 2021              | 20.09%       | 24.81%        | -4.73%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 6.59%        | -8.20%        | 14.79%  | 0.00      | 0      | —               |
| 2023              | 2.12%        | 19.00%        | -16.88% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 258  | 14.44% |
| Consumer Cyclical      | 222  | 12.42% |
| Industrials            | 213  | 11.92% |
| Utilities              | 200  | 11.19% |
| Real Estate            | 197  | 11.02% |
| Healthcare             | 176  | 9.85%  |
| Energy                 | 170  | 9.51%  |
| Basic Materials        | 146  | 8.17%  |
| Technology             | 112  | 6.27%  |
| Communication Services | 70   | 3.92%  |
| Financial Services     | 23   | 1.29%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 105  | 29     | 9      | Energy             | 22.86%        |
| 2006 | 117  | 35     | 11     | Consumer Cyclical  | 17.95%        |
| 2007 | 117  | 35     | 10     | Utilities          | 17.95%        |
| 2008 | 120  | 35     | 9      | Utilities          | 20.00%        |
| 2009 | 115  | 33     | 8      | Consumer Defensive | 20.87%        |
| 2010 | 120  | 29     | 8      | Energy             | 20.00%        |
| 2011 | 115  | 32     | 8      | Consumer Defensive | 20.87%        |
| 2012 | 112  | 32     | 10     | Consumer Defensive | 21.43%        |
| 2013 | 119  | 33     | 9      | Consumer Cyclical  | 17.65%        |
| 2014 | 108  | 28     | 9      | Healthcare         | 16.67%        |
| 2015 | 117  | 28     | 10     | Consumer Defensive | 20.51%        |
| 2016 | 113  | 33     | 7      | Consumer Defensive | 21.24%        |
| 2017 | 112  | 35     | 8      | Consumer Cyclical  | 19.64%        |
| 2018 | 101  | 32     | 10     | Industrials        | 18.81%        |
| 2019 | 107  | 33     | 9      | Utilities          | 16.82%        |
| 2020 | 89   | 29     | 9      | Consumer Defensive | 19.10%        |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 81
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 134 (final-print convention, sell cost applied)

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
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_top10_cap2_s1776_5552bd33d02ed4e4_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_top10_cap2_s1776_5552bd33d02ed4e4_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_top10_cap2_s1776_5552bd33d02ed4e4_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_top10_cap2_s1776_5552bd33d02ed4e4_equity.png`
