# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026

- run `797b6a30152d`, git `88572e12c94aa693fdc65de98344598d7cb6cc21`, backtest config `8615c4b983d0a4f9`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ------------ | -------------- | -------- | ------------ | ---------- |
| strategy  | 260,000.00 | 1,193,902.49 | 933,902.49   | 12.42%         | 11.31%   | -41.42%      | 1,584.91   |
| benchmark | 260,000.00 | 1,326,083.97 | 1,066,083.97 | 13.20%         | 10.93%   | -52.87%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 4.07%        | 7.09%         | -3.02%  | 12,000.00 | 108    | -365.6883       |
| 2006              | 11.65%       | 13.61%        | -1.96%  | 12,000.00 | 120    | -383.1056       |
| 2007              | -0.81%       | 4.40%         | -5.20%  | 12,000.00 | 116    | -342.9483       |
| 2008 (GFC)        | -22.90%      | -34.30%       | 11.41%  | 12,000.00 | 120    | -299.0500       |
| 2009 (GFC)        | 29.41%       | 24.74%        | 4.67%   | 12,000.00 | 115    | -209.9565       |
| 2010              | 28.66%       | 14.30%        | 14.36%  | 12,000.00 | 120    | -383.7250       |
| 2011              | 7.96%        | 2.46%         | 5.50%   | 12,000.00 | 109    | -298.4709       |
| 2012              | 16.69%       | 17.09%        | -0.40%  | 12,000.00 | 108    | -196.1204       |
| 2013              | 37.48%       | 27.75%        | 9.73%   | 12,000.00 | 114    | -263.0409       |
| 2014              | 10.50%       | 14.49%        | -3.99%  | 12,000.00 | 110    | -293.9697       |
| 2015              | 7.08%        | -0.11%        | 7.19%   | 12,000.00 | 106    | -199.8491       |
| 2016              | 13.18%       | 14.45%        | -1.27%  | 12,000.00 | 109    | -187.2875       |
| 2017              | 21.97%       | 21.63%        | 0.34%   | 12,000.00 | 106    | -287.5535       |
| 2018              | -2.52%       | -5.13%        | 2.62%   | 12,000.00 | 96     | -253.0486       |
| 2019              | 41.02%       | 32.30%        | 8.72%   | 12,000.00 | 103    | -216.6828       |
| 2020 (COVID)      | 18.45%       | 15.69%        | 2.76%   | 12,000.00 | 87     | -203.1992       |
| 2021              | 22.70%       | 31.27%        | -8.57%  | 12,000.00 | 87     | -328.1877       |
| 2022 (rate-shock) | -15.74%      | -18.98%       | 3.25%   | 12,000.00 | 81     | -239.5062       |
| 2023              | 23.11%       | 26.01%        | -2.90%  | 12,000.00 | 75     | -222.9733       |
| 2024              | 12.76%       | 25.28%        | -12.52% | 12,000.00 | 64     | -245.5833       |
| 2025              | 3.78%        | 18.21%        | -14.43% | 12,000.00 | 77     | -236.0563       |
| 2026              | -0.02%       | 12.67%        | -12.69% | 8,000.00  | 49     | -294.8503       |

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- selection: top 10 by combined score, `equal`-weighted; strategy `buy_and_hold`; at most 2 of a rebalance's buys per `sector`, walked in score order
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 376  | 17.25% |
| Technology             | 365  | 16.74% |
| Industrials            | 359  | 16.47% |
| Healthcare             | 325  | 14.91% |
| Consumer Cyclical      | 307  | 14.08% |
| Basic Materials        | 188  | 8.62%  |
| Communication Services | 119  | 5.46%  |
| Financial Services     | 72   | 3.30%  |
| Energy                 | 44   | 2.02%  |
| Real Estate            | 16   | 0.73%  |
| Utilities              | 9    | 0.41%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 108  | 23     | 9      | Industrials            | 19.44%        |
| 2006 | 120  | 31     | 7      | Consumer Cyclical      | 20.00%        |
| 2007 | 116  | 31     | 8      | Consumer Defensive     | 18.10%        |
| 2008 | 120  | 29     | 7      | Healthcare             | 20.00%        |
| 2009 | 115  | 32     | 10     | Healthcare             | 20.87%        |
| 2010 | 120  | 27     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 109  | 30     | 9      | Consumer Defensive     | 22.02%        |
| 2012 | 108  | 29     | 8      | Consumer Defensive     | 22.22%        |
| 2013 | 114  | 31     | 8      | Communication Services | 21.05%        |
| 2014 | 110  | 28     | 7      | Technology             | 21.82%        |
| 2015 | 106  | 24     | 8      | Technology             | 19.81%        |
| 2016 | 109  | 27     | 8      | Consumer Defensive     | 22.02%        |
| 2017 | 106  | 28     | 9      | Industrials            | 21.70%        |
| 2018 | 96   | 26     | 8      | Consumer Cyclical      | 25.00%        |
| 2019 | 103  | 27     | 7      | Consumer Defensive     | 23.30%        |
| 2020 | 87   | 27     | 8      | Technology             | 22.99%        |
| 2021 | 87   | 27     | 7      | Consumer Cyclical      | 22.99%        |
| 2022 | 81   | 28     | 8      | Industrials            | 22.22%        |
| 2023 | 75   | 19     | 6      | Technology             | 32.00%        |
| 2024 | 64   | 21     | 6      | Technology             | 31.25%        |
| 2025 | 77   | 18     | 7      | Consumer Defensive     | 25.97%        |
| 2026 | 49   | 19     | 8      | Communication Services | 18.37%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 108  | 108  | -3.31%         | -6.71%           | 34.26%  | 37.96%  | 0.00%         | 108  | -5.57%         | 0.25%            | 51.85%  | 40.74%  | 11.11%        |
| 2006     | 120  | 120  | -11.46%        | -11.95%          | 25.83%  | 43.33%  | 5.00%         | 120  | 1.39%          | 2.19%            | 60.83%  | 73.33%  | 6.67%         |
| 2007     | 116  | 116  | 5.53%          | 5.33%            | 65.52%  | 57.76%  | 1.72%         | 116  | 7.55%          | 7.74%            | 79.31%  | 42.24%  | 12.07%        |
| 2008     | 120  | 120  | 9.78%          | 11.35%           | 65.83%  | 76.67%  | 0.83%         | 120  | 7.82%          | 7.91%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 115  | 115  | 5.58%          | 6.19%            | 57.39%  | 13.04%  | 6.96%         | 115  | -0.76%         | -0.35%           | 46.09%  | 8.70%   | 11.30%        |
| 2010     | 120  | 120  | 22.93%         | 18.01%           | 74.17%  | 8.33%   | 1.67%         | 120  | 10.58%         | 9.75%            | 79.17%  | 1.67%   | 5.00%         |
| 2011     | 109  | 109  | 10.53%         | 10.58%           | 67.89%  | 19.27%  | 5.50%         | 109  | 5.20%          | 4.42%            | 71.56%  | 6.42%   | 8.26%         |
| 2012     | 108  | 108  | -0.85%         | -2.64%           | 46.30%  | 15.74%  | 0.00%         | 108  | 0.51%          | 4.49%            | 57.41%  | 14.81%  | 0.93%         |
| 2013     | 114  | 114  | -0.44%         | -0.83%           | 45.61%  | 14.04%  | 2.63%         | 114  | 2.47%          | 3.95%            | 64.91%  | 17.54%  | 5.26%         |
| 2014     | 110  | 110  | 12.37%         | 16.05%           | 73.64%  | 16.36%  | 1.82%         | 110  | 3.49%          | 3.30%            | 57.27%  | 16.36%  | 8.18%         |
| 2015     | 106  | 106  | 6.48%          | 4.31%            | 64.15%  | 24.53%  | 0.00%         | 106  | 4.20%          | 6.29%            | 71.70%  | 12.26%  | 2.83%         |
| 2016     | 109  | 109  | -2.46%         | -4.04%           | 38.53%  | 12.84%  | 2.75%         | 109  | 1.74%          | 4.70%            | 62.39%  | 17.43%  | 5.50%         |
| 2017     | 106  | 106  | 0.70%          | -2.85%           | 45.28%  | 25.47%  | 4.72%         | 106  | 1.41%          | 0.17%            | 50.94%  | 20.75%  | 14.15%        |
| 2018     | 96   | 96   | 11.66%         | 6.80%            | 73.96%  | 18.75%  | 0.00%         | 96   | 4.77%          | 2.86%            | 55.21%  | 4.17%   | 7.29%         |
| 2019     | 103  | 103  | -3.07%         | -5.13%           | 42.72%  | 36.89%  | 0.00%         | 103  | -4.78%         | -5.93%           | 20.39%  | 12.62%  | 0.00%         |
| 2020     | 87   | 87   | -13.42%        | -16.50%          | 34.48%  | 29.89%  | 0.00%         | 87   | -1.59%         | -1.32%           | 43.68%  | 25.29%  | 10.34%        |
| 2021     | 87   | 87   | -14.54%        | -13.14%          | 19.54%  | 74.71%  | 0.00%         | 87   | -11.58%        | -5.65%           | 26.44%  | 41.38%  | 0.00%         |
| 2022     | 81   | 81   | -2.76%         | -6.66%           | 33.33%  | 54.32%  | 0.00%         | 81   | -10.85%        | -12.38%          | 24.69%  | 32.10%  | 7.41%         |
| 2023     | 75   | 75   | -8.71%         | -11.42%          | 29.33%  | 29.33%  | 0.00%         | 50   | -16.87%        | -19.18%          | 18.00%  | 38.00%  | 0.00%         |
| 2024     | 64   | 64   | -6.63%         | -9.02%           | 42.19%  | 39.06%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2025     | 77   | 49   | -19.05%        | -15.86%          | 22.45%  | 36.73%  | 14.29%        | 0    | —              | —                | —       | —       | —             |
| 2026     | 49   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2180 | 2103 | 1.17%          | -0.16%           | 49.55%  | 31.95%  | 2.14%         | 1965 | 0.88%          | 1.80%            | 56.64%  | 22.34%  | 6.51%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -5.57%      | -7.64%            | 2.07%         | -2.92%       | -2.65%   | 40.74%    | 51.96%          | 44.49%     |
| 2006     | 120  | 1.39%       | -9.20%            | 10.59%        | -2.58%       | 3.98%    | 73.33%    | 77.46%          | 73.02%     |
| 2007     | 116  | 7.55%       | -6.61%            | 14.16%        | -0.15%       | 7.70%    | 42.24%    | 69.63%          | 63.75%     |
| 2008     | 120  | 7.82%       | -1.40%            | 9.22%         | 2.12%        | 5.70%    | 9.17%     | 42.59%          | 34.96%     |
| 2009     | 115  | -0.76%      | -0.05%            | -0.71%        | 1.85%        | -2.61%   | 8.70%     | 25.04%          | 15.65%     |
| 2010     | 120  | 10.58%      | -5.94%            | 16.52%        | -1.55%       | 12.13%   | 1.67%     | 27.56%          | 16.74%     |
| 2011     | 109  | 5.20%       | -7.79%            | 12.99%        | -4.02%       | 9.21%    | 6.42%     | 27.66%          | 17.69%     |
| 2012     | 108  | 0.51%       | -7.18%            | 7.69%         | -2.97%       | 3.49%    | 14.81%    | 28.01%          | 18.63%     |
| 2013     | 114  | 2.47%       | -10.47%           | 12.94%        | -4.61%       | 7.08%    | 17.54%    | 39.74%          | 27.79%     |
| 2014     | 110  | 3.49%       | -11.48%           | 14.97%        | -5.07%       | 8.56%    | 16.36%    | 41.27%          | 30.23%     |
| 2015     | 106  | 4.20%       | -10.46%           | 14.66%        | -4.84%       | 9.05%    | 12.26%    | 37.75%          | 27.44%     |
| 2016     | 109  | 1.74%       | -9.20%            | 10.93%        | -4.25%       | 5.99%    | 17.43%    | 35.02%          | 24.99%     |
| 2017     | 106  | 1.41%       | -14.53%           | 15.94%        | -7.43%       | 8.85%    | 20.75%    | 50.60%          | 39.23%     |
| 2018     | 96   | 4.77%       | -11.71%           | 16.47%        | -4.89%       | 9.66%    | 4.17%     | 36.78%          | 21.25%     |
| 2019     | 103  | -4.78%      | -11.93%           | 7.15%         | -4.87%       | 0.09%    | 12.62%    | 39.90%          | 23.23%     |
| 2020     | 87   | -1.59%      | -8.86%            | 7.27%         | -2.78%       | 1.18%    | 25.29%    | 39.56%          | 25.04%     |
| 2021     | 87   | -11.58%     | -21.54%           | 9.96%         | -10.67%      | -0.91%   | 41.38%    | 56.38%          | 44.09%     |
| 2022     | 81   | -10.85%     | -22.37%           | 11.51%        | -10.50%      | -0.36%   | 32.10%    | 52.61%          | 38.03%     |
| 2023     | 50   | -16.87%     | -21.43%           | 4.56%         | -11.86%      | -5.01%   | 38.00%    | 46.10%          | 32.14%     |
| all buys | 1965 | 0.88%       | -10.33%           | 11.21%        | -3.84%       | 4.72%    | 22.34%    | 44.12%          | 32.74%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 108  | -3.31%      | 5.35%             | -8.66%        | 5.06%        | -8.38%   | 37.96%    | 38.75%          | 33.08%     |
| 2006     | 120  | -11.46%     | -0.16%            | -11.30%       | 1.55%        | -13.01%  | 43.33%    | 38.09%          | 27.98%     |
| 2007     | 116  | 5.53%       | -6.96%            | 12.49%        | 1.24%        | 4.30%    | 57.76%    | 73.37%          | 67.06%     |
| 2008     | 120  | 9.78%       | 4.29%             | 5.49%         | 3.99%        | 5.80%    | 76.67%    | 73.78%          | 75.64%     |
| 2009     | 115  | 5.58%       | 31.52%            | -25.95%       | 15.41%       | -9.83%   | 13.04%    | 23.14%          | 16.14%     |
| 2010     | 120  | 22.93%      | 5.19%             | 17.74%        | 6.11%        | 16.82%   | 8.33%     | 33.33%          | 24.52%     |
| 2011     | 109  | 10.53%      | -7.74%            | 18.26%        | -5.21%       | 15.73%   | 19.27%    | 48.48%          | 40.46%     |
| 2012     | 108  | -0.85%      | 3.78%             | -4.63%        | 2.77%        | -3.62%   | 15.74%    | 27.67%          | 19.82%     |
| 2013     | 114  | -0.44%      | 1.80%             | -2.24%        | 0.78%        | -1.22%   | 14.04%    | 28.86%          | 18.95%     |
| 2014     | 110  | 12.37%      | -7.06%            | 19.43%        | -2.88%       | 15.25%   | 16.36%    | 47.50%          | 36.87%     |
| 2015     | 106  | 6.48%       | -9.48%            | 15.96%        | -3.07%       | 9.55%    | 24.53%    | 56.21%          | 47.04%     |
| 2016     | 109  | -2.46%      | 2.11%             | -4.57%        | -0.53%       | -1.93%   | 12.84%    | 30.44%          | 23.72%     |
| 2017     | 106  | 0.70%       | -1.43%            | 2.13%         | -1.48%       | 2.18%    | 25.47%    | 40.55%          | 33.46%     |
| 2018     | 96   | 11.66%      | -9.94%            | 21.60%        | -1.43%       | 13.08%   | 18.75%    | 53.78%          | 40.81%     |
| 2019     | 103  | -3.07%      | -9.50%            | 6.43%         | -5.21%       | 2.14%    | 36.89%    | 55.93%          | 43.59%     |
| 2020     | 87   | -13.42%     | 33.10%            | -46.53%       | 5.37%        | -18.79%  | 29.89%    | 22.32%          | 14.71%     |
| 2021     | 87   | -14.54%     | -16.40%           | 1.85%         | -7.81%       | -6.73%   | 74.71%    | 66.50%          | 56.97%     |
| 2022     | 81   | -2.76%      | -11.57%           | 8.81%         | -3.08%       | 0.31%    | 54.32%    | 58.36%          | 50.24%     |
| 2023     | 75   | -8.71%      | -18.01%           | 9.30%         | -9.91%       | 1.19%    | 29.33%    | 46.16%          | 29.61%     |
| 2024     | 64   | -6.63%      | -10.83%           | 4.20%         | -7.50%       | 0.87%    | 39.06%    | 53.24%          | 43.92%     |
| 2025     | 49   | -19.05%     | 10.25%            | -29.30%       | 2.22%        | -21.27%  | 36.73%    | 40.91%          | 36.02%     |
| all buys | 2103 | 1.17%       | -0.84%            | 2.02%         | 0.27%        | 0.90%    | 31.95%    | 46.08%          | 37.08%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 176
- mean stocks in the point-in-time cross-section: 4080.3 (min 3653)
- mean after the per-model min_score floor: 4080.3 (min 3653)
- mean after the column filters: 4080.3 (min 3653)
- mean after the investability filter: 3258.0 (min 2923)
- mean with a tradable quote: 3178.2 (min 2870)
- forced delisting liquidations: 80 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), whole shares only (a buy budget's remainder stays in cash for the next month), no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4`: 36 (this one included; every run is logged, failures too)
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

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_8615c4b983d0a4f9_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_8615c4b983d0a4f9_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_8615c4b983d0a4f9_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_8615c4b983d0a4f9_equity.png`
