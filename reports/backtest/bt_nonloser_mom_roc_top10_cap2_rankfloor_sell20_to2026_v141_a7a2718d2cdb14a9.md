# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_v141

- run `102021bd2d3c`, git `eeb268f42ee06caddb332e0eec5322664aa1ccea`, backtest config `a7a2718d2cdb14a9`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ------------ | -------------- | -------- | ------------ | ---------- |
| strategy  | 260,000.00 | 1,294,413.56 | 1,034,413.56 | 13.02%         | 11.48%   | -41.31%      | 15,166.17  |
| benchmark | 260,000.00 | 1,326,083.97 | 1,066,083.97 | 13.20%         | 10.93%   | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 3.70%        | 7.09%         | -3.39%  | 12,000.00 | 108    | -359.0864       |
| 2006              | 8.15%        | 13.61%        | -5.46%  | 12,000.00 | 120    | -381.4222       |
| 2007              | -2.29%       | 4.40%         | -6.69%  | 12,000.00 | 118    | -339.3023       |
| 2008 (GFC)        | -23.74%      | -34.30%       | 10.56%  | 12,000.00 | 120    | -294.5472       |
| 2009 (GFC)        | 23.67%       | 24.74%        | -1.07%  | 12,000.00 | 115    | -208.1159       |
| 2010              | 34.01%       | 14.30%        | 19.71%  | 12,000.00 | 120    | -380.4889       |
| 2011              | 9.91%        | 2.46%         | 7.45%   | 12,000.00 | 113    | -294.0855       |
| 2012              | 14.40%       | 17.09%        | -2.69%  | 12,000.00 | 110    | -195.4212       |
| 2013              | 26.08%       | 27.75%        | -1.67%  | 12,000.00 | 116    | -262.3362       |
| 2014              | 18.69%       | 14.49%        | 4.20%   | 12,000.00 | 114    | -291.4415       |
| 2015              | 9.60%        | -0.11%        | 9.70%   | 12,000.00 | 108    | -199.7623       |
| 2016              | 14.44%       | 14.45%        | -0.01%  | 12,000.00 | 112    | -187.1161       |
| 2017              | 23.09%       | 21.63%        | 1.46%   | 12,000.00 | 103    | -287.6505       |
| 2018              | 3.60%        | -5.13%        | 8.73%   | 12,000.00 | 98     | -252.7959       |
| 2019              | 42.76%       | 32.30%        | 10.46%  | 12,000.00 | 95     | -211.9684       |
| 2020 (COVID)      | 19.43%       | 15.69%        | 3.74%   | 12,000.00 | 97     | -203.9313       |
| 2021              | 22.04%       | 31.27%        | -9.23%  | 12,000.00 | 91     | -340.6740       |
| 2022 (rate-shock) | -17.82%      | -18.98%       | 1.16%   | 12,000.00 | 94     | -241.6348       |
| 2023              | 16.48%       | 26.01%        | -9.53%  | 12,000.00 | 93     | -220.1290       |
| 2024              | 16.54%       | 25.28%        | -8.74%  | 12,000.00 | 86     | -261.5426       |
| 2025              | 5.63%        | 18.21%        | -12.58% | 12,000.00 | 89     | -236.1311       |
| 2026              | 2.73%        | 12.67%        | -9.94%  | 8,000.00  | 56     | -295.0476       |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

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
| Consumer Defensive     | 395  | 17.36% |
| Industrials            | 381  | 16.74% |
| Technology             | 376  | 16.52% |
| Healthcare             | 359  | 15.77% |
| Consumer Cyclical      | 341  | 14.98% |
| Communication Services | 148  | 6.50%  |
| Basic Materials        | 108  | 4.75%  |
| Financial Services     | 75   | 3.30%  |
| Energy                 | 68   | 2.99%  |
| Real Estate            | 16   | 0.70%  |
| Utilities              | 9    | 0.40%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 25     | 10     | Industrials            | 22.22%        |
| 2006 | 120  | 29     | 9      | Consumer Cyclical      | 20.00%        |
| 2007 | 118  | 31     | 9      | Consumer Cyclical      | 20.34%        |
| 2008 | 120  | 31     | 8      | Healthcare             | 20.00%        |
| 2009 | 115  | 32     | 10     | Healthcare             | 20.87%        |
| 2010 | 120  | 29     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 113  | 30     | 9      | Consumer Defensive     | 21.24%        |
| 2012 | 110  | 30     | 9      | Consumer Defensive     | 21.82%        |
| 2013 | 116  | 30     | 8      | Communication Services | 20.69%        |
| 2014 | 114  | 27     | 7      | Technology             | 21.05%        |
| 2015 | 108  | 24     | 8      | Consumer Defensive     | 22.22%        |
| 2016 | 112  | 31     | 7      | Technology             | 21.43%        |
| 2017 | 103  | 28     | 9      | Technology             | 21.36%        |
| 2018 | 98   | 26     | 8      | Consumer Cyclical      | 24.49%        |
| 2019 | 95   | 27     | 7      | Consumer Defensive     | 25.26%        |
| 2020 | 97   | 32     | 8      | Technology             | 20.62%        |
| 2021 | 91   | 33     | 8      | Technology             | 21.98%        |
| 2022 | 94   | 32     | 9      | Industrials            | 22.34%        |
| 2023 | 93   | 28     | 8      | Technology             | 25.81%        |
| 2024 | 86   | 29     | 7      | Technology             | 23.26%        |
| 2025 | 89   | 28     | 7      | Consumer Defensive     | 23.60%        |
| 2026 | 56   | 22     | 8      | Consumer Defensive     | 21.43%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -7.15%         | -7.08%           | 31.48%  | 40.74%  | 2.78%         | 108  | -4.53%         | 0.32%            | 53.70%  | 40.74%  | 16.67%        |
| 2006     | 120  | 120  | -12.58%        | -12.64%          | 25.00%  | 46.67%  | 5.00%         | 120  | 0.78%          | 1.61%            | 58.33%  | 75.83%  | 5.00%         |
| 2007     | 118  | 118  | 3.30%          | 3.87%            | 61.86%  | 62.71%  | 1.69%         | 118  | 7.00%          | 7.19%            | 77.12%  | 47.46%  | 11.86%        |
| 2008     | 120  | 120  | 8.99%          | 11.16%           | 63.33%  | 76.67%  | 0.83%         | 120  | 7.20%          | 7.73%            | 85.83%  | 10.83%  | 3.33%         |
| 2009     | 115  | 115  | 6.80%          | 6.19%            | 60.00%  | 11.30%  | 6.96%         | 115  | -0.38%         | -0.26%           | 46.96%  | 8.70%   | 13.91%        |
| 2010     | 120  | 120  | 26.44%         | 18.34%           | 75.00%  | 8.33%   | 1.67%         | 120  | 10.26%         | 9.15%            | 77.50%  | 1.67%   | 5.00%         |
| 2011     | 113  | 113  | 8.95%          | 7.97%            | 65.49%  | 20.35%  | 5.31%         | 113  | 4.49%          | 4.42%            | 69.03%  | 8.85%   | 7.96%         |
| 2012     | 110  | 110  | -2.71%         | -6.01%           | 40.91%  | 19.09%  | 0.00%         | 110  | -1.23%         | 2.36%            | 53.64%  | 17.27%  | 0.91%         |
| 2013     | 116  | 116  | 0.47%          | -0.51%           | 47.41%  | 12.07%  | 2.59%         | 116  | 2.24%          | 3.38%            | 64.66%  | 17.24%  | 5.17%         |
| 2014     | 114  | 114  | 12.88%         | 16.32%           | 73.68%  | 15.79%  | 1.75%         | 114  | 3.79%          | 4.35%            | 57.02%  | 16.67%  | 6.14%         |
| 2015     | 108  | 108  | 6.64%          | 4.39%            | 63.89%  | 25.93%  | 0.00%         | 108  | 3.80%          | 6.63%            | 73.15%  | 12.96%  | 5.56%         |
| 2016     | 112  | 112  | -2.06%         | -4.30%           | 38.39%  | 13.39%  | 2.68%         | 112  | 1.27%          | 4.10%            | 60.71%  | 19.64%  | 5.36%         |
| 2017     | 103  | 103  | 0.70%          | -2.41%           | 45.63%  | 24.27%  | 4.85%         | 103  | 2.52%          | 0.30%            | 53.40%  | 18.45%  | 14.56%        |
| 2018     | 98   | 98   | 8.74%          | 6.67%            | 72.45%  | 21.43%  | 0.00%         | 98   | 4.00%          | 0.86%            | 51.02%  | 6.12%   | 7.14%         |
| 2019     | 95   | 95   | -4.85%         | -7.88%           | 40.00%  | 38.95%  | 0.00%         | 95   | -5.15%         | -5.93%           | 20.00%  | 12.63%  | 0.00%         |
| 2020     | 97   | 97   | -14.97%        | -15.57%          | 34.02%  | 26.80%  | 0.00%         | 97   | -2.56%         | -3.03%           | 37.11%  | 21.65%  | 9.28%         |
| 2021     | 91   | 91   | -15.51%        | -13.30%          | 23.08%  | 72.53%  | 0.00%         | 91   | -13.75%        | -8.70%           | 20.88%  | 45.05%  | 0.00%         |
| 2022     | 94   | 94   | 1.38%          | -2.31%           | 44.68%  | 42.55%  | 0.00%         | 94   | -7.49%         | -7.68%           | 29.79%  | 25.53%  | 6.38%         |
| 2023     | 93   | 93   | -4.63%         | -8.57%           | 33.33%  | 26.88%  | 0.00%         | 64   | -15.36%        | -18.59%          | 18.75%  | 34.38%  | 0.00%         |
| 2024     | 86   | 86   | -4.41%         | -5.03%           | 40.70%  | 33.72%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2025     | 89   | 59   | -22.43%        | -18.34%          | 16.95%  | 44.07%  | 11.86%        | 0    | —              | —                | —       | —       | —             |
| 2026     | 56   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2276 | 2190 | 0.67%          | -0.40%           | 48.86%  | 32.10%  | 2.19%         | 2016 | 0.53%          | 1.35%            | 55.16%  | 23.07%  | 6.75%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -4.53%      | -7.65%            | 3.12%         | -3.03%       | -1.50%   | 40.74%    | 51.93%          | 45.06%     |
| 2006     | 120  | 0.78%       | -9.20%            | 9.99%         | -2.58%       | 3.37%    | 75.83%    | 77.47%          | 73.30%     |
| 2007     | 118  | 7.00%       | -6.61%            | 13.61%        | -0.05%       | 7.05%    | 47.46%    | 69.62%          | 63.66%     |
| 2008     | 120  | 7.20%       | -1.41%            | 8.61%         | 1.77%        | 5.43%    | 10.83%    | 42.57%          | 35.54%     |
| 2009     | 115  | -0.38%      | -0.01%            | -0.37%        | 1.73%        | -2.11%   | 8.70%     | 24.96%          | 16.33%     |
| 2010     | 120  | 10.26%      | -5.91%            | 16.16%        | -1.10%       | 11.36%   | 1.67%     | 27.42%          | 15.83%     |
| 2011     | 113  | 4.49%       | -7.68%            | 12.17%        | -3.40%       | 7.89%    | 8.85%     | 27.47%          | 16.48%     |
| 2012     | 110  | -1.23%      | -7.07%            | 5.85%         | -3.05%       | 1.82%    | 17.27%    | 27.79%          | 18.46%     |
| 2013     | 116  | 2.24%       | -10.38%           | 12.62%        | -4.28%       | 6.52%    | 17.24%    | 39.52%          | 27.29%     |
| 2014     | 114  | 3.79%       | -11.40%           | 15.19%        | -5.08%       | 8.87%    | 16.67%    | 41.08%          | 30.22%     |
| 2015     | 108  | 3.80%       | -10.39%           | 14.19%        | -4.77%       | 8.57%    | 12.96%    | 37.61%          | 27.18%     |
| 2016     | 112  | 1.27%       | -9.18%            | 10.45%        | -4.06%       | 5.33%    | 19.64%    | 35.01%          | 24.39%     |
| 2017     | 103  | 2.52%       | -14.54%           | 17.06%        | -7.40%       | 9.92%    | 18.45%    | 50.60%          | 39.70%     |
| 2018     | 98   | 4.00%       | -11.65%           | 15.65%        | -4.93%       | 8.94%    | 6.12%     | 36.68%          | 21.56%     |
| 2019     | 95   | -5.15%      | -11.93%           | 6.78%         | -4.91%       | -0.24%   | 12.63%    | 39.82%          | 23.56%     |
| 2020     | 97   | -2.56%      | -8.77%            | 6.21%         | -2.69%       | 0.13%    | 21.65%    | 39.44%          | 24.70%     |
| 2021     | 91   | -13.75%     | -21.47%           | 7.72%         | -10.90%      | -2.85%   | 45.05%    | 56.31%          | 44.40%     |
| 2022     | 94   | -7.49%      | -22.27%           | 14.78%        | -10.19%      | 2.70%    | 25.53%    | 52.54%          | 37.39%     |
| 2023     | 64   | -15.36%     | -21.29%           | 5.93%         | -11.07%      | -4.30%   | 34.38%    | 46.03%          | 30.42%     |
| all buys | 2016 | 0.53%       | -10.29%           | 10.82%        | -3.85%       | 4.38%    | 23.07%    | 44.04%          | 32.60%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -7.15%      | 5.25%             | -12.40%       | 5.27%        | -12.42%  | 40.74%    | 38.73%          | 33.08%     |
| 2006     | 120  | -12.58%     | -0.15%            | -12.43%       | 1.48%        | -14.05%  | 46.67%    | 38.08%          | 27.55%     |
| 2007     | 118  | 3.30%       | -7.00%            | 10.30%        | 1.31%        | 1.99%    | 62.71%    | 73.36%          | 67.35%     |
| 2008     | 120  | 8.99%       | 4.28%             | 4.72%         | 3.92%        | 5.08%    | 76.67%    | 73.80%          | 75.57%     |
| 2009     | 115  | 6.80%       | 31.66%            | -24.85%       | 15.76%       | -8.96%   | 11.30%    | 23.03%          | 16.72%     |
| 2010     | 120  | 26.44%      | 5.09%             | 21.35%        | 6.67%        | 19.77%   | 8.33%     | 33.28%          | 23.80%     |
| 2011     | 113  | 8.95%       | -7.55%            | 16.50%        | -4.25%       | 13.20%   | 20.35%    | 48.29%          | 39.46%     |
| 2012     | 110  | -2.71%      | 3.72%             | -6.43%        | 2.55%        | -5.26%   | 19.09%    | 27.49%          | 19.69%     |
| 2013     | 116  | 0.47%       | 1.72%             | -1.25%        | 0.77%        | -0.30%   | 12.07%    | 28.73%          | 18.53%     |
| 2014     | 114  | 12.88%      | -7.02%            | 19.89%        | -2.91%       | 15.79%   | 15.79%    | 47.37%          | 37.44%     |
| 2015     | 108  | 6.64%       | -9.45%            | 16.09%        | -3.09%       | 9.74%    | 25.93%    | 56.17%          | 46.93%     |
| 2016     | 112  | -2.06%      | 2.15%             | -4.20%        | -1.18%       | -0.88%   | 13.39%    | 30.43%          | 23.58%     |
| 2017     | 103  | 0.70%       | -1.39%            | 2.09%         | -1.88%       | 2.58%    | 24.27%    | 40.54%          | 33.24%     |
| 2018     | 98   | 8.74%       | -9.90%            | 18.64%        | -1.56%       | 10.30%   | 21.43%    | 53.76%          | 41.42%     |
| 2019     | 95   | -4.85%      | -9.73%            | 4.88%         | -5.20%       | 0.35%    | 38.95%    | 55.97%          | 44.23%     |
| 2020     | 97   | -14.97%     | 33.15%            | -48.11%       | 6.95%        | -21.92%  | 26.80%    | 22.31%          | 14.06%     |
| 2021     | 91   | -15.51%     | -16.35%           | 0.84%         | -7.87%       | -7.64%   | 72.53%    | 66.45%          | 57.90%     |
| 2022     | 94   | 1.38%       | -11.56%           | 12.95%        | -2.71%       | 4.09%    | 42.55%    | 58.37%          | 49.95%     |
| 2023     | 93   | -4.63%      | -17.92%           | 13.29%        | -9.57%       | 4.94%    | 26.88%    | 46.09%          | 29.91%     |
| 2024     | 86   | -4.41%      | -10.68%           | 6.27%         | -6.82%       | 2.41%    | 33.72%    | 53.22%          | 41.74%     |
| 2025     | 59   | -22.43%     | 10.29%            | -32.72%       | -0.39%       | -22.04%  | 44.07%    | 40.92%          | 35.86%     |
| all buys | 2190 | 0.67%       | -0.84%            | 1.51%         | 0.20%        | 0.47%    | 32.10%    | 46.04%          | 36.95%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 130
- mean stocks in the point-in-time cross-section: 4063.3 (min 3639)
- mean after the per-model min_score floor: 4063.3 (min 3639)
- mean after the column filters: 4063.3 (min 3639)
- mean after the investability filter: 3244.4 (min 2912)
- mean with a tradable quote: 3164.5 (min 2860)
- criteria sells: 346 (per-cause breakdown in the trades CSV `reason` column)
- forced delisting liquidations: 3 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 3 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `0aeea637e84c41d9`, train run `f259c702a6a6`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/forest_nonloser_dd30_3y_v141_f259c702a6a6`)
- `factor_mom_12_2_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `d74f9884a6361e2a`, train run `121349f6e682`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/factor_mom_12_2_3y_v141_121349f6e682`)
- `factor_roc_greenblatt_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `rank_factor`, config `90bce6a3aa84aacf`, train run `4457ca01bcfb`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/factor_roc_greenblatt_3y_v141_4457ca01bcfb`)

### Simulated year-end refits

One refit per (bundle, trade year) past that bundle's folds — trained on rows whose labels were observable by Jan 1, all snapshot kinds, delistings included, no split tags read. `source = cache` rows were reused from the refit cache (identical by construction: the cache key pins train config, dataset version, year, and label lag):

| bundle                        | trade_year | n_train_rows | effective_train_size | last_usable_snapshot | source |
| ----------------------------- | ---------- | ------------ | -------------------- | -------------------- | ------ |
| forest_nonloser_dd30_3y_v141  | 2021       | 1105684      | 38493.8000           | 2017-11-17           | cache  |
| forest_nonloser_dd30_3y_v141  | 2022       | 1149454      | 39914.7000           | 2018-11-16           | cache  |
| forest_nonloser_dd30_3y_v141  | 2023       | 1193792      | 41336                | 2019-11-15           | cache  |
| forest_nonloser_dd30_3y_v141  | 2024       | 1238172      | 42767.3000           | 2020-11-17           | cache  |
| forest_nonloser_dd30_3y_v141  | 2025       | 1289260      | 44618.4000           | 2021-11-17           | cache  |
| forest_nonloser_dd30_3y_v141  | 2026       | 1344427      | 46562.4000           | 2022-11-17           | cache  |
| factor_mom_12_2_3y_v141       | 2021       | 1105684      | 38493.8000           | 2017-11-17           | cache  |
| factor_mom_12_2_3y_v141       | 2022       | 1149454      | 39914.7000           | 2018-11-16           | cache  |
| factor_mom_12_2_3y_v141       | 2023       | 1193792      | 41336                | 2019-11-15           | cache  |
| factor_mom_12_2_3y_v141       | 2024       | 1238172      | 42767.3000           | 2020-11-17           | cache  |
| factor_mom_12_2_3y_v141       | 2025       | 1289260      | 44618.4000           | 2021-11-17           | cache  |
| factor_mom_12_2_3y_v141       | 2026       | 1344427      | 46562.4000           | 2022-11-17           | cache  |
| factor_roc_greenblatt_3y_v141 | 2021       | 1105684      | 38493.8000           | 2017-11-17           | cache  |
| factor_roc_greenblatt_3y_v141 | 2022       | 1149454      | 39914.7000           | 2018-11-16           | cache  |
| factor_roc_greenblatt_3y_v141 | 2023       | 1193792      | 41336                | 2019-11-15           | cache  |
| factor_roc_greenblatt_3y_v141 | 2024       | 1238172      | 42767.3000           | 2020-11-17           | cache  |
| factor_roc_greenblatt_3y_v141 | 2025       | 1289260      | 44618.4000           | 2021-11-17           | cache  |
| factor_roc_greenblatt_3y_v141 | 2026       | 1344427      | 46562.4000           | 2022-11-17           | cache  |

### Artifacts

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_v141_a7a2718d2cdb14a9_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_v141_a7a2718d2cdb14a9_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_v141_a7a2718d2cdb14a9_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026_v141_a7a2718d2cdb14a9_equity.png`
