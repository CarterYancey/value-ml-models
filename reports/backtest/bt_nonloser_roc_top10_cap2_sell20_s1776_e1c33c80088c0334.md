# Portfolio backtest — bt_nonloser_roc_top10_cap2_sell20_s1776

- run `847a381e9899`, git `ba55f7d9adc1654cdb466dee924ac976e3f9a828`, backtest config `e1c33c80088c0334`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 803,800.37  | 611,800.37 | 12.40%         | 10.79%   | -39.45%      | 2,242.84   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 4.56%        | 6.51%         | -1.95%  | 12,000.00 | 108    | -82.8472        |
| 2006              | 9.61%        | 12.67%        | -3.06%  | 12,000.00 | 117    | -87.1282        |
| 2007              | 7.75%        | 7.28%         | 0.47%   | 12,000.00 | 120    | -91.2375        |
| 2008 (GFC)        | -32.43%      | -43.21%       | 10.78%  | 12,000.00 | 120    | -86.2417        |
| 2009 (GFC)        | 37.42%       | 39.07%        | -1.65%  | 12,000.00 | 120    | -77.4000        |
| 2010              | 14.18%       | 10.86%        | 3.32%   | 12,000.00 | 117    | -85.0256        |
| 2011              | 9.01%        | 5.33%         | 3.68%   | 12,000.00 | 115    | -75.7391        |
| 2012              | 12.57%       | 15.60%        | -3.02%  | 12,000.00 | 108    | -79.3565        |
| 2013              | 27.73%       | 30.42%        | -2.69%  | 12,000.00 | 114    | -68.6842        |
| 2014              | 15.28%       | 16.18%        | -0.90%  | 12,000.00 | 109    | -49.6835        |
| 2015              | 18.05%       | 4.46%         | 13.59%  | 12,000.00 | 106    | -55.2311        |
| 2016              | 8.02%        | 6.48%         | 1.54%   | 12,000.00 | 106    | -72.0094        |
| 2017              | 19.90%       | 22.88%        | -2.97%  | 12,000.00 | 105    | -58.1524        |
| 2018              | 11.36%       | 7.53%         | 3.83%   | 12,000.00 | 112    | -71.1295        |
| 2019              | 20.77%       | 13.81%        | 6.96%   | 12,000.00 | 105    | -85.0524        |
| 2020 (COVID)      | 15.74%       | 19.77%        | -4.02%  | 12,000.00 | 108    | -58.6667        |
| 2021              | 9.94%        | 24.81%        | -14.87% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 7.82%        | -8.20%        | 16.02%  | 0.00      | 0      | —               |
| 2023              | 4.83%        | 19.00%        | -14.17% | 0.00      | 0      | —               |

**Defensive hypothesis:** Benchmark down-years in window: 2; strategy lost less (positive excess) in 2 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 2 walk-forward model(s), combined by `mean_rank`

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
| Consumer Defensive     | 384  | 21.45% |
| Industrials            | 325  | 18.16% |
| Technology             | 318  | 17.77% |
| Healthcare             | 297  | 16.59% |
| Consumer Cyclical      | 223  | 12.46% |
| Communication Services | 74   | 4.13%  |
| Energy                 | 54   | 3.02%  |
| Financial Services     | 54   | 3.02%  |
| Basic Materials        | 49   | 2.74%  |
| Real Estate            | 9    | 0.50%  |
| Utilities              | 3    | 0.17%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 15     | 9      | Consumer Defensive | 22.22%        |
| 2006 | 117  | 24     | 8      | Healthcare         | 20.51%        |
| 2007 | 120  | 22     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 120  | 19     | 7      | Healthcare         | 20.00%        |
| 2010 | 117  | 18     | 9      | Consumer Defensive | 20.51%        |
| 2011 | 115  | 19     | 7      | Consumer Defensive | 20.87%        |
| 2012 | 108  | 18     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 114  | 21     | 7      | Consumer Defensive | 21.05%        |
| 2014 | 109  | 16     | 6      | Consumer Defensive | 22.02%        |
| 2015 | 106  | 16     | 6      | Consumer Defensive | 22.64%        |
| 2016 | 106  | 18     | 8      | Consumer Defensive | 22.64%        |
| 2017 | 105  | 20     | 8      | Technology         | 22.86%        |
| 2018 | 112  | 21     | 8      | Consumer Defensive | 21.43%        |
| 2019 | 105  | 21     | 7      | Consumer Defensive | 22.86%        |
| 2020 | 108  | 22     | 8      | Consumer Defensive | 22.22%        |

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
| 2011     | 115  | 115  | 5.62%          | 0.32%            | 52.17%  | 24.35%  | 0.00%         | 115  | 0.51%          | 1.27%            | 53.04%  | 0.87%   | 0.00%         |
| 2012     | 108  | 108  | -4.06%         | -3.33%           | 41.67%  | 17.59%  | 0.00%         | 108  | -0.44%         | 3.87%            | 63.89%  | 17.59%  | 0.93%         |
| 2013     | 114  | 114  | 1.59%          | 2.09%            | 55.26%  | 7.02%   | 0.00%         | 114  | 5.82%          | 6.10%            | 76.32%  | 7.02%   | 0.00%         |
| 2014     | 109  | 109  | 14.58%         | 15.59%           | 82.57%  | 8.26%   | 0.00%         | 109  | 5.89%          | 7.38%            | 73.39%  | 11.01%  | 0.92%         |
| 2015     | 106  | 106  | 9.51%          | 10.66%           | 73.58%  | 23.58%  | 0.00%         | 106  | 0.13%          | 1.61%            | 56.60%  | 20.75%  | 0.00%         |
| 2016     | 106  | 106  | -1.88%         | -2.46%           | 43.40%  | 12.26%  | 0.00%         | 106  | -2.06%         | 2.97%            | 59.43%  | 24.53%  | 2.83%         |
| 2017     | 105  | 105  | 2.15%          | 4.79%            | 60.95%  | 13.33%  | 4.76%         | 105  | 3.20%          | 5.64%            | 71.43%  | 11.43%  | 5.71%         |
| 2018     | 112  | 112  | 10.19%         | 11.67%           | 71.43%  | 20.54%  | 2.68%         | 112  | -1.98%         | -2.38%           | 38.39%  | 0.00%   | 5.36%         |
| 2019     | 105  | 105  | -3.04%         | -4.37%           | 44.76%  | 37.14%  | 0.00%         | 105  | -4.40%         | -3.91%           | 30.48%  | 9.52%   | 1.90%         |
| 2020     | 108  | 108  | -16.39%        | -14.08%          | 22.22%  | 16.67%  | 0.00%         | 108  | -2.97%         | -1.86%           | 38.89%  | 12.96%  | 14.81%        |
| all buys | 1790 | 1790 | 2.45%          | 2.59%            | 55.92%  | 24.02%  | 0.84%         | 1790 | 1.17%          | 1.99%            | 57.65%  | 18.66%  | 4.13%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 106
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 73 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 4 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 22 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s1776` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `eb90655c2d0557f7`, train run `003a8739d3d5`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s1776_003a8739d3d5`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s1776_e1c33c80088c0334_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s1776_e1c33c80088c0334_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s1776_e1c33c80088c0334_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s1776_e1c33c80088c0334_equity.png`
