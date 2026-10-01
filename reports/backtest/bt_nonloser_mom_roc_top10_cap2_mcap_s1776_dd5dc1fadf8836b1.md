# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_mcap_s1776

- run `856d61de7914`, git `8e0cdcdc679f7a9b71a57f7c20e916506f9f91fe`, backtest config `dd5dc1fadf8836b1`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 1,090,347.24 | 898,347.24 | 14.95%         | 13.91%   | -37.68%      | 1,046.18   |
| benchmark | 192,000.00 | 732,110.07   | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 16.83%       | 6.51%         | 10.32%  | 12,000.00 | 61     | -347.3934       |
| 2006              | 17.34%       | 12.67%        | 4.67%   | 12,000.00 | 79     | -377.8650       |
| 2007              | 7.56%        | 7.28%         | 0.28%   | 12,000.00 | 78     | -327.7436       |
| 2008 (GFC)        | -32.69%      | -43.21%       | 10.52%  | 12,000.00 | 61     | -287.6776       |
| 2009 (GFC)        | 40.78%       | 39.07%        | 1.71%   | 12,000.00 | 81     | -188.0535       |
| 2010              | 18.11%       | 10.86%        | 7.25%   | 12,000.00 | 46     | -377.3986       |
| 2011              | 17.67%       | 5.33%         | 12.35%  | 12,000.00 | 41     | -290.9350       |
| 2012              | 20.06%       | 15.60%        | 4.46%   | 12,000.00 | 42     | -182.7778       |
| 2013              | 18.87%       | 30.42%        | -11.55% | 12,000.00 | 73     | -262.3105       |
| 2014              | 23.46%       | 16.18%        | 7.28%   | 12,000.00 | 85     | -295.1529       |
| 2015              | 7.30%        | 4.46%         | 2.83%   | 12,000.00 | 62     | -192.2151       |
| 2016              | 5.81%        | 6.48%         | -0.66%  | 12,000.00 | 58     | -177.2989       |
| 2017              | 26.23%       | 22.88%        | 3.36%   | 12,000.00 | 62     | -294.3871       |
| 2018              | 4.50%        | 7.53%         | -3.03%  | 12,000.00 | 55     | -261.6364       |
| 2019              | 23.50%       | 13.81%        | 9.69%   | 12,000.00 | 53     | -231.3836       |
| 2020 (COVID)      | 30.07%       | 19.77%        | 10.30%  | 12,000.00 | 41     | -215.5447       |
| 2021              | 23.05%       | 24.81%        | -1.76%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | 0.43%        | -8.20%        | 8.63%   | 0.00      | 0      | —               |
| 2023              | 16.48%       | 19.00%        | -2.52%  | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m >= 100000.0`
- selection: top 10 by combined score, `marketcap`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 237  | 24.23% |
| Industrials            | 172  | 17.59% |
| Healthcare             | 145  | 14.83% |
| Technology             | 137  | 14.01% |
| Consumer Cyclical      | 106  | 10.84% |
| Communication Services | 61   | 6.24%  |
| Financial Services     | 48   | 4.91%  |
| Basic Materials        | 40   | 4.09%  |
| Energy                 | 13   | 1.33%  |
| Real Estate            | 12   | 1.23%  |
| Utilities              | 7    | 0.72%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 61   | 16     | 8      | Industrials            | 29.51%        |
| 2006 | 79   | 22     | 7      | Consumer Defensive     | 26.58%        |
| 2007 | 78   | 22     | 8      | Consumer Defensive     | 25.64%        |
| 2008 | 61   | 17     | 7      | Consumer Defensive     | 34.43%        |
| 2009 | 81   | 26     | 10     | Consumer Defensive     | 25.93%        |
| 2010 | 46   | 13     | 7      | Communication Services | 28.26%        |
| 2011 | 41   | 12     | 6      | Consumer Defensive     | 36.59%        |
| 2012 | 42   | 11     | 5      | Technology             | 28.57%        |
| 2013 | 73   | 21     | 8      | Consumer Defensive     | 21.92%        |
| 2014 | 85   | 19     | 7      | Industrials            | 24.71%        |
| 2015 | 62   | 15     | 6      | Consumer Defensive     | 33.87%        |
| 2016 | 58   | 16     | 5      | Consumer Defensive     | 41.38%        |
| 2017 | 62   | 23     | 9      | Industrials            | 22.58%        |
| 2018 | 55   | 17     | 8      | Industrials            | 27.27%        |
| 2019 | 53   | 18     | 6      | Consumer Cyclical      | 26.42%        |
| 2020 | 41   | 15     | 8      | Consumer Defensive     | 21.95%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 61   | 61   | 3.80%          | -0.74%           | 49.18%  | 27.87%  | 0.00%         | 61   | -4.75%         | 0.08%            | 50.82%  | 39.34%  | 1.64%         |
| 2006     | 79   | 79   | -9.58%         | -11.47%          | 30.38%  | 39.24%  | 0.00%         | 79   | 2.18%          | 2.52%            | 69.62%  | 78.48%  | 3.80%         |
| 2007     | 78   | 78   | 6.47%          | 4.60%            | 65.38%  | 62.82%  | 0.00%         | 78   | 8.28%          | 7.28%            | 80.77%  | 48.72%  | 10.26%        |
| 2008     | 61   | 61   | 7.78%          | 11.20%           | 63.93%  | 77.05%  | 0.00%         | 61   | 7.12%          | 6.78%            | 88.52%  | 9.84%   | 0.00%         |
| 2009     | 81   | 81   | 3.88%          | 5.41%            | 60.49%  | 12.35%  | 6.17%         | 81   | 0.87%          | -0.76%           | 44.44%  | 1.23%   | 7.41%         |
| 2010     | 46   | 46   | 36.05%         | 16.82%           | 82.61%  | 0.00%   | 0.00%         | 46   | 8.75%          | 7.27%            | 80.43%  | 4.35%   | 0.00%         |
| 2011     | 41   | 41   | 23.61%         | 21.11%           | 85.37%  | 2.44%   | 0.00%         | 41   | 8.89%          | 7.41%            | 90.24%  | 0.00%   | 0.00%         |
| 2012     | 42   | 42   | -7.75%         | -9.15%           | 38.10%  | 21.43%  | 0.00%         | 42   | -0.25%         | 2.47%            | 54.76%  | 11.90%  | 0.00%         |
| 2013     | 73   | 73   | 2.12%          | 0.86%            | 52.05%  | 12.33%  | 4.11%         | 73   | 1.66%          | 3.41%            | 65.75%  | 16.44%  | 4.11%         |
| 2014     | 85   | 85   | 14.50%         | 17.67%           | 81.18%  | 12.94%  | 0.00%         | 85   | 1.34%          | 1.88%            | 55.29%  | 17.65%  | 7.06%         |
| 2015     | 62   | 62   | 5.04%          | 2.88%            | 61.29%  | 27.42%  | 0.00%         | 62   | -1.21%         | 4.11%            | 66.13%  | 22.58%  | 4.84%         |
| 2016     | 58   | 58   | -3.40%         | -4.05%           | 41.38%  | 17.24%  | 0.00%         | 58   | -1.94%         | 2.47%            | 62.07%  | 25.86%  | 10.34%        |
| 2017     | 62   | 62   | 4.28%          | 3.05%            | 54.84%  | 19.35%  | 6.45%         | 62   | 2.44%          | 0.79%            | 54.84%  | 20.97%  | 11.29%        |
| 2018     | 55   | 55   | 12.15%         | 16.39%           | 70.91%  | 21.82%  | 0.00%         | 55   | -1.22%         | -1.58%           | 41.82%  | 14.55%  | 10.91%        |
| 2019     | 53   | 53   | -1.47%         | -2.66%           | 43.40%  | 30.19%  | 0.00%         | 53   | -3.31%         | -5.19%           | 18.87%  | 3.77%   | 0.00%         |
| 2020     | 41   | 41   | -0.55%         | -3.52%           | 43.90%  | 4.88%   | 0.00%         | 41   | 2.55%          | 2.30%            | 53.66%  | 12.20%  | 7.32%         |
| all buys | 978  | 978  | 5.53%          | 4.24%            | 57.77%  | 25.87%  | 1.23%         | 978  | 1.89%          | 2.47%            | 61.04%  | 22.70%  | 5.32%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 191
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 32 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 32 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s1776_dd5dc1fadf8836b1_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s1776_dd5dc1fadf8836b1_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s1776_dd5dc1fadf8836b1_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s1776_dd5dc1fadf8836b1_equity.png`
