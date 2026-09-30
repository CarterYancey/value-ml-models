# Portfolio backtest — bt_nonloser_roc_top10_cap2_s1776

- run `3cbe5232887a`, git `c3ff72fce9c700ba3c45604a87d9fd4b9d250363`, backtest config `00ff6fb492c82b77`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 721,825.68  | 529,825.68 | 11.50%         | 10.04%   | -41.34%      | 1,126.22   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 4.18%        | 6.51%         | -2.34%  | 12,000.00 | 108    | -82.8472        |
| 2006              | 11.23%       | 12.67%        | -1.43%  | 12,000.00 | 117    | -87.1282        |
| 2007              | 3.87%        | 7.28%         | -3.41%  | 12,000.00 | 120    | -91.2375        |
| 2008 (GFC)        | -31.87%      | -43.21%       | 11.34%  | 12,000.00 | 120    | -86.2417        |
| 2009 (GFC)        | 35.21%       | 39.07%        | -3.86%  | 12,000.00 | 120    | -77.4000        |
| 2010              | 15.16%       | 10.86%        | 4.31%   | 12,000.00 | 117    | -85.0256        |
| 2011              | 9.39%        | 5.33%         | 4.06%   | 12,000.00 | 114    | -75.4825        |
| 2012              | 10.98%       | 15.60%        | -4.62%  | 12,000.00 | 108    | -79.3565        |
| 2013              | 29.70%       | 30.42%        | -0.72%  | 12,000.00 | 113    | -68.2434        |
| 2014              | 19.46%       | 16.18%        | 3.28%   | 12,000.00 | 108    | -49.3935        |
| 2015              | 12.00%       | 4.46%         | 7.54%   | 12,000.00 | 104    | -55.0144        |
| 2016              | 8.89%        | 6.48%         | 2.41%   | 12,000.00 | 102    | -71.8039        |
| 2017              | 19.96%       | 22.88%        | -2.91%  | 12,000.00 | 106    | -58.2406        |
| 2018              | 6.65%        | 7.53%         | -0.88%  | 12,000.00 | 110    | -70.1682        |
| 2019              | 17.30%       | 13.81%        | 3.49%   | 12,000.00 | 110    | -85.8545        |
| 2020 (COVID)      | 12.21%       | 19.77%        | -7.55%  | 12,000.00 | 104    | -57.9375        |
| 2021              | 14.15%       | 24.81%        | -10.66% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 4.85%        | -8.20%        | 13.04%  | 0.00      | 0      | —               |
| 2023              | 4.20%        | 19.00%        | -14.80% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 384  | 21.56% |
| Industrials            | 322  | 18.08% |
| Technology             | 320  | 17.97% |
| Healthcare             | 296  | 16.62% |
| Consumer Cyclical      | 218  | 12.24% |
| Communication Services | 75   | 4.21%  |
| Energy                 | 54   | 3.03%  |
| Financial Services     | 52   | 2.92%  |
| Basic Materials        | 48   | 2.70%  |
| Real Estate            | 9    | 0.51%  |
| Utilities              | 3    | 0.17%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 15     | 9      | Consumer Defensive | 22.22%        |
| 2006 | 117  | 24     | 8      | Healthcare         | 20.51%        |
| 2007 | 120  | 22     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 120  | 19     | 7      | Healthcare         | 20.00%        |
| 2010 | 117  | 18     | 9      | Consumer Defensive | 20.51%        |
| 2011 | 114  | 18     | 7      | Consumer Defensive | 21.05%        |
| 2012 | 108  | 18     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 113  | 20     | 7      | Consumer Defensive | 21.24%        |
| 2014 | 108  | 15     | 6      | Consumer Defensive | 22.22%        |
| 2015 | 104  | 16     | 6      | Consumer Defensive | 23.08%        |
| 2016 | 102  | 16     | 8      | Consumer Defensive | 23.53%        |
| 2017 | 106  | 20     | 8      | Technology         | 22.64%        |
| 2018 | 110  | 20     | 8      | Consumer Defensive | 21.82%        |
| 2019 | 110  | 22     | 8      | Consumer Defensive | 21.82%        |
| 2020 | 104  | 21     | 7      | Consumer Defensive | 23.08%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -4.60%         | -3.14%           | 36.11%  | 30.56%  | 0.00%         | 108  | -1.61%         | -0.49%           | 41.67%  | 37.96%  | 19.44%        |
| 2006     | 117  | 117  | 0.24%          | -0.41%           | 49.57%  | 13.68%  | 2.56%         | 117  | 2.39%          | 3.05%            | 61.54%  | 67.52%  | 7.69%         |
| 2007     | 120  | 120  | 4.03%          | 6.32%            | 68.33%  | 57.50%  | 0.00%         | 120  | 4.55%          | 6.18%            | 72.50%  | 55.83%  | 2.50%         |
| 2008     | 120  | 120  | 11.02%         | 13.09%           | 77.50%  | 78.33%  | 0.00%         | 120  | 5.82%          | 6.07%            | 79.17%  | 11.67%  | 0.00%         |
| 2009     | 120  | 120  | 3.83%          | -1.30%           | 48.33%  | 9.17%   | 3.33%         | 120  | 1.74%          | -0.75%           | 48.33%  | 0.00%   | 5.00%         |
| 2010     | 117  | 117  | 4.56%          | 4.19%            | 63.25%  | 9.40%   | 0.00%         | 117  | 0.77%          | 2.76%            | 53.85%  | 7.69%   | 0.00%         |
| 2011     | 114  | 114  | 5.49%          | 0.32%            | 51.75%  | 24.56%  | 0.00%         | 114  | 0.46%          | 1.06%            | 52.63%  | 0.88%   | 0.00%         |
| 2012     | 108  | 108  | -4.06%         | -3.33%           | 41.67%  | 17.59%  | 0.00%         | 108  | -0.44%         | 3.87%            | 63.89%  | 17.59%  | 0.93%         |
| 2013     | 113  | 113  | 1.58%          | 1.69%            | 54.87%  | 7.08%   | 0.00%         | 113  | 5.77%          | 5.95%            | 76.11%  | 7.08%   | 0.00%         |
| 2014     | 108  | 108  | 14.57%         | 16.02%           | 82.41%  | 8.33%   | 0.00%         | 108  | 5.86%          | 7.33%            | 73.15%  | 11.11%  | 0.93%         |
| 2015     | 104  | 104  | 9.88%          | 11.07%           | 75.00%  | 23.08%  | 0.00%         | 104  | 0.24%          | 2.37%            | 58.65%  | 21.15%  | 0.00%         |
| 2016     | 102  | 102  | -1.65%         | -2.46%           | 43.14%  | 11.76%  | 0.00%         | 102  | -2.19%         | 3.00%            | 59.80%  | 25.49%  | 2.94%         |
| 2017     | 106  | 106  | 1.99%          | 4.62%            | 60.38%  | 13.21%  | 4.72%         | 106  | 3.13%          | 5.43%            | 71.70%  | 11.32%  | 5.66%         |
| 2018     | 110  | 110  | 10.01%         | 11.67%           | 70.00%  | 20.00%  | 2.73%         | 110  | -1.99%         | -2.15%           | 39.09%  | 0.00%   | 5.45%         |
| 2019     | 110  | 110  | -2.68%         | -4.28%           | 45.45%  | 35.45%  | 0.00%         | 110  | -4.37%         | -3.89%           | 30.91%  | 10.00%  | 1.82%         |
| 2020     | 104  | 104  | -16.99%        | -14.54%          | 22.12%  | 18.27%  | 0.00%         | 104  | -2.82%         | -1.86%           | 40.38%  | 14.42%  | 15.38%        |
| all buys | 1781 | 1781 | 2.46%          | 2.59%            | 55.87%  | 24.03%  | 0.84%         | 1781 | 1.17%          | 2.01%            | 57.89%  | 18.87%  | 4.15%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 112
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- forced delisting liquidations: 25 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 15 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_s1776_00ff6fb492c82b77_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_s1776_00ff6fb492c82b77_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_s1776_00ff6fb492c82b77_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_s1776_00ff6fb492c82b77_equity.png`
