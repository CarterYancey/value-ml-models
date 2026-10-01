# Portfolio backtest — bt_nonloser_mom_roc_top10_cap2_rankfloor_frac_to2026

- run `dec259400062`, git `88572e12c94aa693fdc65de98344598d7cb6cc21`, backtest config `6dc31b99d5373827`
- dataset `1.4`, price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | mwr_annualized | twr_cagr | max_drawdown | costs_paid |
| --------- | ---------- | ------------ | ------------ | -------------- | -------- | ------------ | ---------- |
| strategy  | 260,000.00 | 1,172,559.92 | 912,559.92   | 12.28%         | 11.21%   | -43.06%      | 1,554.30   |
| benchmark | 260,000.00 | 1,326,613.94 | 1,066,613.94 | 13.21%         | 10.94%   | -52.91%      | 0.00       |

Money-weighted (MWR/XIRR) is what the deposits earned; time-weighted (TWR) is the strategy's per-period compounding with deposits treated as external flows. Both legs get identical deposit dates and accounting.

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 4.65%        | 7.18%         | -2.52%  | 12,000.00 | 120    | -356.2333       |
| 2006              | 13.39%       | 13.64%        | -0.25%  | 12,000.00 | 120    | -383.1056       |
| 2007              | -1.90%       | 4.40%         | -6.30%  | 12,000.00 | 120    | -343.9806       |
| 2008 (GFC)        | -23.81%      | -34.33%       | 10.52%  | 12,000.00 | 120    | -299.0500       |
| 2009 (GFC)        | 29.48%       | 24.75%        | 4.74%   | 12,000.00 | 120    | -208.2472       |
| 2010              | 28.51%       | 14.31%        | 14.20%  | 12,000.00 | 120    | -383.7250       |
| 2011              | 7.73%        | 2.45%         | 5.28%   | 12,000.00 | 120    | -297.1500       |
| 2012              | 16.51%       | 17.10%        | -0.58%  | 12,000.00 | 120    | -194.9500       |
| 2013              | 37.11%       | 27.76%        | 9.34%   | 12,000.00 | 120    | -263.0250       |
| 2014              | 10.47%       | 14.50%        | -4.03%  | 12,000.00 | 120    | -295.2889       |
| 2015              | 6.97%        | -0.11%        | 7.08%   | 12,000.00 | 120    | -201.4361       |
| 2016              | 12.60%       | 14.46%        | -1.86%  | 12,000.00 | 120    | -184.9611       |
| 2017              | 21.11%       | 21.64%        | -0.53%  | 12,000.00 | 120    | -286.0639       |
| 2018              | -2.26%       | -5.14%        | 2.88%   | 12,000.00 | 120    | -253.4472       |
| 2019              | 40.96%       | 32.31%        | 8.65%   | 12,000.00 | 120    | -220.2056       |
| 2020 (COVID)      | 17.73%       | 15.68%        | 2.05%   | 12,000.00 | 120    | -205.5972       |
| 2021              | 23.55%       | 31.28%        | -7.72%  | 12,000.00 | 120    | -335.9278       |
| 2022 (rate-shock) | -14.83%      | -18.99%       | 4.15%   | 12,000.00 | 120    | -233.7056       |
| 2023              | 22.45%       | 26.01%        | -3.56%  | 12,000.00 | 120    | -219.4778       |
| 2024              | 12.89%       | 25.28%        | -12.39% | 12,000.00 | 120    | -250.8806       |
| 2025              | 3.64%        | 18.22%        | -14.58% | 12,000.00 | 120    | -236.3583       |
| 2026              | -0.53%       | 12.68%        | -13.21% | 8,000.00  | 80     | -289.5417       |

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
| Industrials            | 442  | 17.00% |
| Healthcare             | 427  | 16.42% |
| Technology             | 415  | 15.96% |
| Consumer Defensive     | 391  | 15.04% |
| Consumer Cyclical      | 387  | 14.88% |
| Basic Materials        | 224  | 8.62%  |
| Communication Services | 123  | 4.73%  |
| Financial Services     | 117  | 4.50%  |
| Energy                 | 44   | 1.69%  |
| Real Estate            | 21   | 0.81%  |
| Utilities              | 9    | 0.35%  |

| year | buys | stocks | groups | largest_group          | largest_share |
| ---- | ---- | ------ | ------ | ---------------------- | ------------- |
| 2005 | 120  | 24     | 9      | Consumer Cyclical      | 20.00%        |
| 2006 | 120  | 31     | 7      | Consumer Cyclical      | 20.00%        |
| 2007 | 120  | 32     | 8      | Industrials            | 20.00%        |
| 2008 | 120  | 29     | 7      | Healthcare             | 20.00%        |
| 2009 | 120  | 32     | 10     | Healthcare             | 20.00%        |
| 2010 | 120  | 27     | 8      | Consumer Defensive     | 20.00%        |
| 2011 | 120  | 30     | 9      | Consumer Cyclical      | 20.00%        |
| 2012 | 120  | 31     | 9      | Consumer Defensive     | 20.00%        |
| 2013 | 120  | 32     | 8      | Communication Services | 20.00%        |
| 2014 | 120  | 30     | 7      | Industrials            | 20.00%        |
| 2015 | 120  | 25     | 8      | Consumer Defensive     | 20.00%        |
| 2016 | 120  | 28     | 8      | Technology             | 20.00%        |
| 2017 | 120  | 29     | 9      | Consumer Cyclical      | 20.00%        |
| 2018 | 120  | 28     | 8      | Consumer Cyclical      | 20.00%        |
| 2019 | 120  | 30     | 7      | Consumer Defensive     | 20.00%        |
| 2020 | 120  | 32     | 8      | Consumer Defensive     | 17.50%        |
| 2021 | 120  | 34     | 7      | Consumer Cyclical      | 20.00%        |
| 2022 | 120  | 34     | 9      | Healthcare             | 20.00%        |
| 2023 | 120  | 29     | 8      | Healthcare             | 20.00%        |
| 2024 | 120  | 28     | 7      | Technology             | 20.00%        |
| 2025 | 120  | 27     | 8      | Technology             | 17.50%        |
| 2026 | 80   | 24     | 8      | Technology             | 20.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys | n_1y | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ---- | ---- | -------------- | ---------------- | ------- | ------- | ------------- | ---- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 120  | 120  | -2.08%         | -4.86%           | 40.00%  | 34.17%  | 0.00%         | 120  | -5.69%         | -0.38%           | 47.50%  | 42.50%  | 10.00%        |
| 2006     | 120  | 120  | -11.46%        | -11.95%          | 25.83%  | 43.33%  | 5.00%         | 120  | 1.39%          | 2.19%            | 60.83%  | 73.33%  | 6.67%         |
| 2007     | 120  | 120  | 4.99%          | 4.77%            | 64.17%  | 58.33%  | 1.67%         | 120  | 7.64%          | 7.59%            | 80.00%  | 43.33%  | 11.67%        |
| 2008     | 120  | 120  | 9.78%          | 11.35%           | 65.83%  | 76.67%  | 0.83%         | 120  | 7.82%          | 7.91%            | 87.50%  | 9.17%   | 3.33%         |
| 2009     | 120  | 120  | 6.82%          | 7.96%            | 59.17%  | 12.50%  | 6.67%         | 120  | 0.19%          | -0.16%           | 48.33%  | 8.33%   | 10.83%        |
| 2010     | 120  | 120  | 22.93%         | 18.01%           | 74.17%  | 8.33%   | 1.67%         | 120  | 10.58%         | 9.75%            | 79.17%  | 1.67%   | 5.00%         |
| 2011     | 120  | 120  | 11.02%         | 11.55%           | 67.50%  | 17.50%  | 5.00%         | 120  | 5.16%          | 4.63%            | 70.83%  | 5.83%   | 7.50%         |
| 2012     | 120  | 120  | -0.02%         | -3.05%           | 45.00%  | 15.00%  | 0.00%         | 120  | -0.91%         | 3.56%            | 56.67%  | 16.67%  | 0.83%         |
| 2013     | 120  | 120  | -0.08%         | -0.51%           | 47.50%  | 13.33%  | 2.50%         | 120  | 2.24%          | 2.84%            | 64.17%  | 16.67%  | 5.00%         |
| 2014     | 120  | 120  | 12.57%         | 16.05%           | 75.00%  | 15.83%  | 1.67%         | 120  | 3.59%          | 3.75%            | 58.33%  | 17.50%  | 9.17%         |
| 2015     | 120  | 120  | 4.00%          | 3.06%            | 58.33%  | 31.67%  | 0.00%         | 120  | 3.10%          | 5.47%            | 65.83%  | 13.33%  | 2.50%         |
| 2016     | 120  | 120  | -2.85%         | -3.08%           | 40.00%  | 14.17%  | 2.50%         | 120  | 1.82%          | 4.38%            | 62.50%  | 15.83%  | 5.00%         |
| 2017     | 120  | 120  | 2.48%          | 0.65%            | 50.83%  | 22.50%  | 4.17%         | 120  | 2.33%          | 0.76%            | 55.83%  | 19.17%  | 12.50%        |
| 2018     | 120  | 120  | 12.11%         | 8.44%            | 76.67%  | 17.50%  | 0.00%         | 120  | 3.38%          | 1.39%            | 53.33%  | 8.33%   | 5.83%         |
| 2019     | 120  | 120  | -1.97%         | -1.45%           | 45.00%  | 33.33%  | 0.00%         | 120  | -5.03%         | -5.94%           | 20.00%  | 13.33%  | 0.00%         |
| 2020     | 120  | 120  | -14.03%        | -16.06%          | 32.50%  | 28.33%  | 0.00%         | 120  | -2.69%         | -3.58%           | 39.17%  | 21.67%  | 7.50%         |
| 2021     | 120  | 120  | -15.36%        | -13.22%          | 21.67%  | 71.67%  | 0.00%         | 120  | -13.80%        | -8.09%           | 23.33%  | 45.83%  | 0.00%         |
| 2022     | 120  | 120  | -1.71%         | -3.02%           | 40.00%  | 50.00%  | 0.00%         | 120  | -8.70%         | -7.68%           | 29.17%  | 25.00%  | 5.00%         |
| 2023     | 120  | 120  | -9.95%         | -12.10%          | 28.33%  | 30.83%  | 0.00%         | 80   | -13.50%        | -15.84%          | 21.25%  | 28.75%  | 0.00%         |
| 2024     | 120  | 120  | -4.08%         | -3.58%           | 43.33%  | 32.50%  | 0.00%         | 0    | —              | —                | —       | —       | —             |
| 2025     | 120  | 80   | -20.76%        | -16.55%          | 22.50%  | 42.50%  | 8.75%         | 0    | —              | —                | —       | —       | —             |
| 2026     | 80   | 0    | —              | —                | —       | —       | —             | 0    | —              | —                | —       | —       | —             |
| all buys | 2600 | 2480 | 0.45%          | -0.30%           | 49.15%  | 31.73%  | 1.81%         | 2240 | 0.18%          | 1.25%            | 54.46%  | 22.32%  | 5.80%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -5.69%      | -7.64%            | 1.95%         | -3.39%       | -2.30%   | 42.50%    | 51.96%          | 45.56%     |
| 2006     | 120  | 1.39%       | -9.20%            | 10.59%        | -2.58%       | 3.98%    | 73.33%    | 77.46%          | 73.02%     |
| 2007     | 120  | 7.64%       | -6.61%            | 14.25%        | -0.10%       | 7.74%    | 43.33%    | 69.63%          | 63.72%     |
| 2008     | 120  | 7.82%       | -1.40%            | 9.22%         | 2.12%        | 5.70%    | 9.17%     | 42.59%          | 34.96%     |
| 2009     | 120  | 0.19%       | -0.05%            | 0.24%         | 1.78%        | -1.59%   | 8.33%     | 25.04%          | 15.62%     |
| 2010     | 120  | 10.58%      | -5.94%            | 16.52%        | -1.55%       | 12.13%   | 1.67%     | 27.56%          | 16.74%     |
| 2011     | 120  | 5.16%       | -7.79%            | 12.95%        | -3.70%       | 8.86%    | 5.83%     | 27.66%          | 17.28%     |
| 2012     | 120  | -0.91%      | -7.18%            | 6.27%         | -2.96%       | 2.05%    | 16.67%    | 28.01%          | 18.48%     |
| 2013     | 120  | 2.24%       | -10.47%           | 12.71%        | -4.59%       | 6.83%    | 16.67%    | 39.74%          | 27.73%     |
| 2014     | 120  | 3.59%       | -11.48%           | 15.07%        | -4.99%       | 8.58%    | 17.50%    | 41.27%          | 29.99%     |
| 2015     | 120  | 3.10%       | -10.46%           | 13.56%        | -4.92%       | 8.02%    | 13.33%    | 37.75%          | 27.63%     |
| 2016     | 120  | 1.82%       | -9.20%            | 11.02%        | -4.10%       | 5.92%    | 15.83%    | 35.02%          | 24.58%     |
| 2017     | 120  | 2.33%       | -14.53%           | 16.87%        | -7.43%       | 9.76%    | 19.17%    | 50.60%          | 39.45%     |
| 2018     | 120  | 3.38%       | -11.71%           | 15.08%        | -4.71%       | 8.09%    | 8.33%     | 36.78%          | 20.93%     |
| 2019     | 120  | -5.03%      | -11.93%           | 6.90%         | -4.87%       | -0.16%   | 13.33%    | 39.90%          | 23.42%     |
| 2020     | 120  | -2.69%      | -8.86%            | 6.17%         | -2.87%       | 0.19%    | 21.67%    | 39.56%          | 25.24%     |
| 2021     | 120  | -13.80%     | -21.54%           | 7.74%         | -10.36%      | -3.44%   | 45.83%    | 56.38%          | 43.64%     |
| 2022     | 120  | -8.70%      | -22.37%           | 13.67%        | -9.80%       | 1.10%    | 25.00%    | 52.61%          | 36.35%     |
| 2023     | 80   | -13.50%     | -21.43%           | 7.93%         | -10.53%      | -2.97%   | 28.75%    | 46.10%          | 29.20%     |
| all buys | 2240 | 0.18%       | -10.33%           | 10.51%        | -4.07%       | 4.26%    | 22.32%    | 44.12%          | 32.35%     |

Over 1 year:

| year     | buys | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ---- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 120  | -2.08%      | 5.35%             | -7.43%        | 5.10%        | -7.18%   | 34.17%    | 38.75%          | 33.93%     |
| 2006     | 120  | -11.46%     | -0.16%            | -11.30%       | 1.55%        | -13.01%  | 43.33%    | 38.09%          | 27.98%     |
| 2007     | 120  | 4.99%       | -6.96%            | 11.95%        | 1.24%        | 3.76%    | 58.33%    | 73.37%          | 67.79%     |
| 2008     | 120  | 9.78%       | 4.29%             | 5.49%         | 3.99%        | 5.80%    | 76.67%    | 73.78%          | 75.64%     |
| 2009     | 120  | 6.82%       | 31.52%            | -24.71%       | 15.02%       | -8.20%   | 12.50%    | 23.14%          | 16.37%     |
| 2010     | 120  | 22.93%      | 5.19%             | 17.74%        | 6.11%        | 16.82%   | 8.33%     | 33.33%          | 24.52%     |
| 2011     | 120  | 11.02%      | -7.74%            | 18.76%        | -4.89%       | 15.92%   | 17.50%    | 48.48%          | 40.01%     |
| 2012     | 120  | -0.02%      | 3.78%             | -3.81%        | 2.81%        | -2.84%   | 15.00%    | 27.67%          | 19.61%     |
| 2013     | 120  | -0.08%      | 1.80%             | -1.88%        | 0.83%        | -0.91%   | 13.33%    | 28.86%          | 18.77%     |
| 2014     | 120  | 12.57%      | -7.06%            | 19.63%        | -2.84%       | 15.41%   | 15.83%    | 47.50%          | 37.24%     |
| 2015     | 120  | 4.00%       | -9.48%            | 13.48%        | -3.15%       | 7.15%    | 31.67%    | 56.21%          | 47.36%     |
| 2016     | 120  | -2.85%      | 2.11%             | -4.96%        | -0.69%       | -2.16%   | 14.17%    | 30.44%          | 23.63%     |
| 2017     | 120  | 2.48%       | -1.43%            | 3.91%         | -1.67%       | 4.15%    | 22.50%    | 40.55%          | 33.59%     |
| 2018     | 120  | 12.11%      | -9.94%            | 22.05%        | -1.26%       | 13.37%   | 17.50%    | 53.78%          | 40.79%     |
| 2019     | 120  | -1.97%      | -9.50%            | 7.53%         | -5.40%       | 3.43%    | 33.33%    | 55.93%          | 44.32%     |
| 2020     | 120  | -14.03%     | 33.10%            | -47.14%       | 5.33%        | -19.36%  | 28.33%    | 22.32%          | 14.95%     |
| 2021     | 120  | -15.36%     | -16.40%           | 1.03%         | -7.04%       | -8.33%   | 71.67%    | 66.50%          | 57.26%     |
| 2022     | 120  | -1.71%      | -11.57%           | 9.86%         | -2.75%       | 1.04%    | 50.00%    | 58.36%          | 49.29%     |
| 2023     | 120  | -9.95%      | -18.01%           | 8.06%         | -8.90%       | -1.05%   | 30.83%    | 46.16%          | 29.09%     |
| 2024     | 120  | -4.08%      | -10.83%           | 6.75%         | -6.86%       | 2.79%    | 32.50%    | 53.24%          | 41.74%     |
| 2025     | 80   | -20.76%     | 10.25%            | -31.01%       | 2.06%        | -22.82%  | 42.50%    | 40.91%          | 35.22%     |
| all buys | 2480 | 0.45%       | -0.84%            | 1.29%         | -0.10%       | 0.55%    | 31.73%    | 46.08%          | 37.13%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10 picks: 0
- mean stocks in the point-in-time cross-section: 4080.3 (min 3653)
- mean after the per-model min_score floor: 4080.3 (min 3653)
- mean after the column filters: 4080.3 (min 3653)
- mean after the investability filter: 3258.0 (min 2923)
- mean with a tradable quote: 3178.2 (min 2870)
- forced delisting liquidations: 83 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
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

- equity_curve: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_frac_to2026_6dc31b99d5373827_equity.csv`
- trades: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_frac_to2026_6dc31b99d5373827_trades.csv`
- rebalances: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_frac_to2026_6dc31b99d5373827_rebalances.csv`
- equity_plot: `reports/backtest/bt_nonloser_mom_roc_top10_cap2_rankfloor_frac_to2026_6dc31b99d5373827_equity.png`
