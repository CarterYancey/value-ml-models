# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_mcap_s232

- run `7d37e1de6c26`, git `8e0cdcdc679f7a9b71a57f7c20e916506f9f91fe`, backtest config `226fc3d55d1f4f05`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 1,161,451.34 | 969,451.34 | 15.48%         | 14.40%   | -39.45%      | 1,111.46   |
| benchmark | 192,000.00 | 732,110.07   | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 20.89%       | 6.51%         | 14.38%  | 12,000.00 | 61     | -348.8579       |
| 2006              | 17.96%       | 12.67%        | 5.29%   | 12,000.00 | 82     | -372.5488       |
| 2007              | 4.40%        | 7.28%         | -2.89%  | 12,000.00 | 77     | -332.8225       |
| 2008 (GFC)        | -34.10%      | -43.21%       | 9.11%   | 12,000.00 | 69     | -288.4928       |
| 2009 (GFC)        | 42.40%       | 39.07%        | 3.33%   | 12,000.00 | 87     | -182.6552       |
| 2010              | 19.24%       | 10.86%        | 8.39%   | 12,000.00 | 55     | -376.8848       |
| 2011              | 17.87%       | 5.33%         | 12.55%  | 12,000.00 | 45     | -291.3926       |
| 2012              | 21.24%       | 15.60%        | 5.65%   | 12,000.00 | 42     | -182.1905       |
| 2013              | 18.88%       | 30.42%        | -11.54% | 12,000.00 | 70     | -259.1143       |
| 2014              | 24.66%       | 16.18%        | 8.48%   | 12,000.00 | 84     | -299.1310       |
| 2015              | 8.02%        | 4.46%         | 3.55%   | 12,000.00 | 66     | -192.2929       |
| 2016              | 6.78%        | 6.48%         | 0.30%   | 12,000.00 | 61     | -182.2350       |
| 2017              | 26.68%       | 22.88%        | 3.80%   | 12,000.00 | 58     | -288.4023       |
| 2018              | 5.64%        | 7.53%         | -1.89%  | 12,000.00 | 58     | -256.1494       |
| 2019              | 24.94%       | 13.81%        | 11.13%  | 12,000.00 | 55     | -221.3394       |
| 2020 (COVID)      | 31.61%       | 19.77%        | 11.84%  | 12,000.00 | 34     | -213.6373       |
| 2021              | 23.74%       | 24.81%        | -1.07%  | 0.00      | 0      | —               |
| 2022 (rate-shock) | -1.03%       | -8.20%        | 7.16%   | 0.00      | 0      | —               |
| 2023              | 17.26%       | 19.00%        | -1.74%  | 0.00      | 0      | —               |

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
| Consumer Defensive     | 236  | 23.51% |
| Industrials            | 190  | 18.92% |
| Healthcare             | 141  | 14.04% |
| Technology             | 138  | 13.75% |
| Consumer Cyclical      | 113  | 11.25% |
| Communication Services | 60   | 5.98%  |
| Financial Services     | 57   | 5.68%  |
| Basic Materials        | 43   | 4.28%  |
| Energy                 | 10   | 1.00%  |
| Real Estate            | 9    | 0.90%  |
| Utilities              | 7    | 0.70%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 61   | 15     | 7      | Industrials        | 29.51%        |
| 2006 | 82   | 22     | 6      | Healthcare         | 25.61%        |
| 2007 | 77   | 21     | 8      | Consumer Defensive | 24.68%        |
| 2008 | 69   | 18     | 6      | Consumer Defensive | 34.78%        |
| 2009 | 87   | 25     | 10     | Consumer Defensive | 22.99%        |
| 2010 | 55   | 13     | 7      | Technology         | 21.82%        |
| 2011 | 45   | 13     | 7      | Consumer Defensive | 33.33%        |
| 2012 | 42   | 11     | 6      | Technology         | 28.57%        |
| 2013 | 70   | 22     | 8      | Consumer Defensive | 22.86%        |
| 2014 | 84   | 19     | 8      | Industrials        | 25.00%        |
| 2015 | 66   | 16     | 6      | Consumer Defensive | 36.36%        |
| 2016 | 61   | 18     | 5      | Consumer Defensive | 39.34%        |
| 2017 | 58   | 18     | 9      | Industrials        | 24.14%        |
| 2018 | 58   | 17     | 8      | Industrials        | 31.03%        |
| 2019 | 55   | 19     | 7      | Consumer Cyclical  | 25.45%        |
| 2020 | 34   | 12     | 8      | Technology         | 26.47%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 61   | 61   | 1.18%          | 1.86%            | 50.82%  | 24.59%  | 0.00%         | 61   | -3.72%         | -0.36%           | 49.18%  | 40.98%  | 1.64%         |
| 2006     | 82   | 82   | -12.57%        | -11.73%          | 21.95%  | 42.68%  | 0.00%         | 82   | 1.59%          | 2.17%            | 64.63%  | 76.83%  | 0.00%         |
| 2007     | 77   | 77   | 6.94%          | 4.69%            | 68.83%  | 62.34%  | 0.00%         | 77   | 8.44%          | 7.35%            | 83.12%  | 46.75%  | 9.09%         |
| 2008     | 69   | 69   | 8.24%          | 10.31%           | 63.77%  | 79.71%  | 0.00%         | 69   | 7.46%          | 7.59%            | 89.86%  | 8.70%   | 0.00%         |
| 2009     | 87   | 87   | 7.98%          | 8.61%            | 63.22%  | 12.64%  | 5.75%         | 87   | 1.30%          | -0.26%           | 47.13%  | 4.60%   | 9.20%         |
| 2010     | 55   | 55   | 39.08%         | 18.58%           | 83.64%  | 1.82%   | 0.00%         | 55   | 9.63%          | 8.52%            | 78.18%  | 3.64%   | 0.00%         |
| 2011     | 45   | 45   | 25.81%         | 24.28%           | 86.67%  | 2.22%   | 0.00%         | 45   | 8.89%          | 6.60%            | 91.11%  | 0.00%   | 0.00%         |
| 2012     | 42   | 42   | -7.65%         | -9.15%           | 38.10%  | 21.43%  | 0.00%         | 42   | 0.07%          | 2.62%            | 54.76%  | 11.90%  | 0.00%         |
| 2013     | 70   | 70   | -0.03%         | -0.74%           | 50.00%  | 12.86%  | 4.29%         | 70   | 1.90%          | 3.46%            | 70.00%  | 17.14%  | 4.29%         |
| 2014     | 84   | 84   | 14.57%         | 16.50%           | 83.33%  | 11.90%  | 2.38%         | 84   | 2.13%          | 4.49%            | 59.52%  | 17.86%  | 9.52%         |
| 2015     | 66   | 66   | 5.94%          | 4.01%            | 63.64%  | 25.76%  | 0.00%         | 66   | -0.31%         | 4.90%            | 68.18%  | 21.21%  | 9.09%         |
| 2016     | 61   | 61   | -5.42%         | -5.24%           | 34.43%  | 16.39%  | 0.00%         | 61   | -2.16%         | 1.68%            | 54.10%  | 24.59%  | 4.92%         |
| 2017     | 58   | 58   | 5.09%          | 0.24%            | 50.00%  | 18.97%  | 6.90%         | 58   | 2.44%          | 0.26%            | 51.72%  | 18.97%  | 15.52%        |
| 2018     | 58   | 58   | 15.91%         | 19.62%           | 79.31%  | 17.24%  | 0.00%         | 58   | 2.47%          | 1.67%            | 51.72%  | 10.34%  | 5.17%         |
| 2019     | 55   | 55   | -2.28%         | -3.99%           | 41.82%  | 34.55%  | 0.00%         | 55   | -1.20%         | -3.53%           | 29.09%  | 1.82%   | 0.00%         |
| 2020     | 34   | 34   | -0.01%         | -2.40%           | 44.12%  | 2.94%   | 0.00%         | 34   | 1.39%          | 2.62%            | 61.76%  | 11.76%  | 8.82%         |
| all buys | 1004 | 1004 | 6.18%          | 4.33%            | 58.07%  | 26.10%  | 1.39%         | 1004 | 2.53%          | 3.34%            | 62.85%  | 21.81%  | 5.08%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 188
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

- backtest configurations tried against dataset `1.4`: 31 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_mom_12_2_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `e7032461b70bc338`, train run `97c0f095cf48`, folds 2005–2020 (from `experiments/models/factor_mom_12_2_3y_97c0f095cf48`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s232_226fc3d55d1f4f05_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s232_226fc3d55d1f4f05_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s232_226fc3d55d1f4f05_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_mcap_s232_226fc3d55d1f4f05_equity.png`
