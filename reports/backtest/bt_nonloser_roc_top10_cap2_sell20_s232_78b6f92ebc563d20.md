# Portfolio backtest — bt_nonloser_roc_top10_cap2_sell20_s232

- run `6da6aa76305c`, git `ba55f7d9adc1654cdb466dee924ac976e3f9a828`, backtest config `78b6f92ebc563d20`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2020 (last buy 2020-12-31), valuation through 2023-12-29; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value | profit     | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ----------- | ---------- | -------------- | -------- | ------------ | ---------- |
| strategy  | 192,000.00 | 852,325.38  | 660,325.38 | 12.90%         | 11.09%   | -39.70%      | 2,247.17   |
| benchmark | 192,000.00 | 732,110.07  | 540,110.07 | 11.62%         | 9.58%    | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 2.41%        | 6.51%         | -4.10%  | 12,000.00 | 108    | -87.7315        |
| 2006              | 10.49%       | 12.67%        | -2.17%  | 12,000.00 | 117    | -84.5641        |
| 2007              | 7.07%        | 7.28%         | -0.21%  | 12,000.00 | 120    | -100.1333       |
| 2008 (GFC)        | -32.95%      | -43.21%       | 10.26%  | 12,000.00 | 120    | -82.1708        |
| 2009 (GFC)        | 37.66%       | 39.07%        | -1.41%  | 12,000.00 | 120    | -76.1167        |
| 2010              | 15.28%       | 10.86%        | 4.42%   | 12,000.00 | 119    | -87.0504        |
| 2011              | 8.73%        | 5.33%         | 3.40%   | 12,000.00 | 115    | -75.0435        |
| 2012              | 13.62%       | 15.60%        | -1.97%  | 12,000.00 | 108    | -77.4722        |
| 2013              | 28.04%       | 30.42%        | -2.38%  | 12,000.00 | 113    | -61.4867        |
| 2014              | 17.40%       | 16.18%        | 1.21%   | 12,000.00 | 109    | -54.2936        |
| 2015              | 20.57%       | 4.46%         | 16.10%  | 12,000.00 | 107    | -54.0561        |
| 2016              | 7.23%        | 6.48%         | 0.75%   | 12,000.00 | 108    | -75.9676        |
| 2017              | 21.22%       | 22.88%        | -1.65%  | 12,000.00 | 111    | -58.2883        |
| 2018              | 12.21%       | 7.53%         | 4.68%   | 12,000.00 | 116    | -69.7759        |
| 2019              | 20.60%       | 13.81%        | 6.79%   | 12,000.00 | 107    | -82.6822        |
| 2020 (COVID)      | 15.52%       | 19.77%        | -4.24%  | 12,000.00 | 101    | -59.2475        |
| 2021              | 9.28%        | 24.81%        | -15.53% | 0.00      | 0      | —               |
| 2022 (rate-shock) | 8.16%        | -8.20%        | 16.36%  | 0.00      | 0      | —               |
| 2023              | 6.16%        | 19.00%        | -12.84% | 0.00      | 0      | —               |

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
| Consumer Defensive     | 384  | 21.35% |
| Industrials            | 325  | 18.07% |
| Technology             | 316  | 17.57% |
| Healthcare             | 283  | 15.73% |
| Consumer Cyclical      | 240  | 13.34% |
| Financial Services     | 66   | 3.67%  |
| Communication Services | 65   | 3.61%  |
| Energy                 | 54   | 3.00%  |
| Basic Materials        | 51   | 2.83%  |
| Real Estate            | 9    | 0.50%  |
| Utilities              | 6    | 0.33%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 108  | 15     | 9      | Consumer Defensive | 22.22%        |
| 2006 | 117  | 21     | 8      | Consumer Defensive | 20.51%        |
| 2007 | 120  | 22     | 9      | Consumer Defensive | 20.00%        |
| 2008 | 120  | 19     | 7      | Consumer Defensive | 20.00%        |
| 2009 | 120  | 17     | 6      | Healthcare         | 20.00%        |
| 2010 | 119  | 18     | 8      | Consumer Defensive | 20.17%        |
| 2011 | 115  | 19     | 8      | Consumer Defensive | 20.87%        |
| 2012 | 108  | 21     | 8      | Consumer Defensive | 22.22%        |
| 2013 | 113  | 18     | 7      | Consumer Defensive | 21.24%        |
| 2014 | 109  | 16     | 6      | Consumer Defensive | 22.02%        |
| 2015 | 107  | 16     | 6      | Consumer Defensive | 22.43%        |
| 2016 | 108  | 17     | 7      | Consumer Defensive | 22.22%        |
| 2017 | 111  | 21     | 8      | Technology         | 21.62%        |
| 2018 | 116  | 22     | 8      | Consumer Defensive | 20.69%        |
| 2019 | 107  | 21     | 8      | Consumer Defensive | 22.43%        |
| 2020 | 101  | 23     | 8      | Consumer Defensive | 23.76%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -4.76%         | -4.18%           | 33.33%  | 32.41%  | 0.00%         | 108  | -2.06%         | -1.07%           | 39.81%  | 41.67%  | 16.67%        |
| 2006     | 117  | 117  | 0.23%          | -0.41%           | 48.72%  | 11.97%  | 0.00%         | 117  | 1.63%          | 3.17%            | 60.68%  | 63.25%  | 2.56%         |
| 2007     | 120  | 120  | 2.39%          | 3.47%            | 61.67%  | 63.33%  | 0.00%         | 120  | 4.56%          | 6.46%            | 70.83%  | 54.17%  | 2.50%         |
| 2008     | 120  | 120  | 11.65%         | 14.33%           | 75.83%  | 76.67%  | 0.00%         | 120  | 6.79%          | 6.40%            | 83.33%  | 7.50%   | 0.00%         |
| 2009     | 120  | 120  | 4.04%          | -0.15%           | 50.00%  | 10.83%  | 3.33%         | 120  | 2.77%          | 0.12%            | 51.67%  | 0.00%   | 5.00%         |
| 2010     | 119  | 119  | 3.71%          | 3.48%            | 61.34%  | 8.40%   | 0.00%         | 119  | 1.25%          | 2.09%            | 52.94%  | 5.04%   | 0.00%         |
| 2011     | 115  | 115  | 6.31%          | 0.90%            | 54.78%  | 22.61%  | 0.00%         | 115  | 0.50%          | 0.55%            | 51.30%  | 0.87%   | 0.00%         |
| 2012     | 108  | 108  | -2.31%         | -0.75%           | 47.22%  | 13.89%  | 0.00%         | 108  | 2.58%          | 4.93%            | 70.37%  | 4.63%   | 0.93%         |
| 2013     | 113  | 113  | 2.56%          | 2.75%            | 57.52%  | 6.19%   | 0.00%         | 113  | 8.09%          | 7.78%            | 80.53%  | 2.65%   | 0.00%         |
| 2014     | 109  | 109  | 14.19%         | 15.07%           | 81.65%  | 6.42%   | 0.00%         | 109  | 6.82%          | 7.73%            | 77.06%  | 8.26%   | 0.00%         |
| 2015     | 107  | 107  | 10.92%         | 10.46%           | 78.50%  | 17.76%  | 0.00%         | 107  | 0.27%          | 1.83%            | 57.01%  | 18.69%  | 0.00%         |
| 2016     | 108  | 108  | 0.68%          | -0.33%           | 48.15%  | 10.19%  | 0.00%         | 108  | 0.41%          | 4.38%            | 66.67%  | 20.37%  | 0.00%         |
| 2017     | 111  | 111  | 3.13%          | 5.88%            | 61.26%  | 13.51%  | 4.50%         | 111  | 4.52%          | 6.48%            | 75.68%  | 9.01%   | 5.41%         |
| 2018     | 116  | 116  | 9.12%          | 9.49%            | 70.69%  | 21.55%  | 2.59%         | 116  | -2.64%         | -2.24%           | 37.93%  | 1.72%   | 5.17%         |
| 2019     | 107  | 107  | -4.01%         | -4.96%           | 42.06%  | 39.25%  | 0.00%         | 107  | -4.44%         | -4.06%           | 25.23%  | 6.54%   | 1.87%         |
| 2020     | 101  | 101  | -17.34%        | -14.62%          | 18.81%  | 14.85%  | 0.00%         | 101  | -2.49%         | -1.63%           | 40.59%  | 10.89%  | 9.90%         |
| all buys | 1799 | 1799 | 2.73%          | 2.55%            | 56.09%  | 23.46%  | 0.67%         | 1799 | 1.86%          | 2.50%            | 59.09%  | 16.06%  | 3.06%         |

## Coverage & diagnostics

- rebalance months: 192; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 95
- mean stocks in the point-in-time cross-section: 4051.8 (min 3653)
- mean after the per-model min_score floor: 4051.8 (min 3653)
- mean after the column filters: 4051.8 (min 3653)
- mean after the investability filter: 3152.8 (min 2669)
- mean with a tradable quote: 3079.2 (min 2640)
- criteria sells: 73 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 3 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 21 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_s232` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `013621dbe24966cb`, train run `de629f13deec`, folds 2005–2020 (from `experiments/models/forest_nonloser_dd30_3y_s232_de629f13deec`)
- `factor_roc_greenblatt_3y` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `306c61a9fe13b111`, train run `da640394cbba`, folds 2005–2020 (from `experiments/models/factor_roc_greenblatt_3y_da640394cbba`)

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s232_78b6f92ebc563d20_equity.csv`
- trades: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s232_78b6f92ebc563d20_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s232_78b6f92ebc563d20_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_roc_top10_cap2_sell20_s232_78b6f92ebc563d20_equity.png`
