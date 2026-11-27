# Portfolio backtest — bt_lc90_mcap_all_v141

- run `0aa2941c5281`, git `2df8c944be4c056fac96f90f90e48a7ec214d772`, backtest config `6c79822d076add76`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | cagr   | max_drawdown | twr    | costs_paid |
| --------- | ---------- | ------------ | ------------ | ------ | ------------ | ------ | ---------- |
| strategy  | 260,000.00 | 1,421,189.39 | 1,161,189.39 | 13.72% | -45.91%      | 11.87% | 1,285.17   |
| benchmark | 260,000.00 | 1,326,613.94 | 1,066,613.94 | 13.21% | -52.91%      | 10.94% | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 6.78%        | 7.18%         | -0.40% | 12,000.00 | 5414   | -228.7758       |
| 2006              | 13.20%       | 13.64%        | -0.44% | 12,000.00 | 5334   | -226.5217       |
| 2007              | 10.79%       | 4.40%         | 6.39%  | 12,000.00 | 5243   | -223.3366       |
| 2008 (GFC)        | -29.34%      | -34.33%       | 4.99%  | 12,000.00 | 5106   | -217.4058       |
| 2009 (GFC)        | 26.57%       | 24.75%        | 1.82%  | 12,000.00 | 4892   | -207.8645       |
| 2010              | 14.73%       | 14.31%        | 0.42%  | 12,000.00 | 4716   | -199.6522       |
| 2011              | 6.09%        | 2.45%         | 3.64%  | 12,000.00 | 4586   | -192.9778       |
| 2012              | 15.21%       | 17.10%        | -1.88% | 12,000.00 | 4465   | -188.1104       |
| 2013              | 26.58%       | 27.76%        | -1.18% | 12,000.00 | 4410   | -185.3041       |
| 2014              | 14.13%       | 14.50%        | -0.37% | 12,000.00 | 4500   | -188.8953       |
| 2015              | -0.75%       | -0.11%        | -0.64% | 12,000.00 | 4549   | -193.2192       |
| 2016              | 13.72%       | 14.46%        | -0.74% | 12,000.00 | 4464   | -190.0719       |
| 2017              | 20.93%       | 21.64%        | -0.71% | 12,000.00 | 4388   | -185.7582       |
| 2018              | -3.42%       | -5.14%        | 1.72%  | 12,000.00 | 4386   | -185.3324       |
| 2019              | 31.97%       | 32.31%        | -0.34% | 12,000.00 | 4354   | -184.8383       |
| 2020 (COVID)      | 17.63%       | 15.68%        | 1.95%  | 12,000.00 | 4382   | -183.9500       |
| 2021              | 30.84%       | 31.28%        | -0.44% | 12,000.00 | 4974   | -208.8277       |
| 2022 (rate-shock) | -15.71%      | -18.99%       | 3.28%  | 12,000.00 | 5447   | -229.4922       |
| 2023              | 24.14%       | 26.01%        | -1.87% | 12,000.00 | 5161   | -216.4425       |
| 2024              | 22.48%       | 25.28%        | -2.80% | 12,000.00 | 4736   | -198.8573       |
| 2025              | 18.77%       | 18.22%        | 0.55%  | 12,000.00 | 4499   | -188.4270       |
| 2026              | 14.35%       | 12.68%        | 1.67%  | 8,000.00  | 2996   | -188.8141       |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 3 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 1 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `log_marketcap_rank >= 0.9`
- selection: top 10000 by combined score, `marketcap`-weighted; strategy `buy_and_hold`
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys  | share  |
| ---------------------- | ----- | ------ |
| Technology             | 17195 | 16.69% |
| Industrials            | 14780 | 14.35% |
| Healthcare             | 13043 | 12.66% |
| Consumer Cyclical      | 12343 | 11.98% |
| Energy                 | 10055 | 9.76%  |
| Consumer Defensive     | 10026 | 9.73%  |
| Communication Services | 7062  | 6.86%  |
| Utilities              | 6505  | 6.32%  |
| Real Estate            | 5351  | 5.20%  |
| Basic Materials        | 4953  | 4.81%  |
| Financial Services     | 1689  | 1.64%  |

| year | buys | stocks | groups | largest_group     | largest_share |
| ---- | ---- | ------ | ------ | ----------------- | ------------- |
| 2005 | 5414 | 499    | 11     | Consumer Cyclical | 15.63%        |
| 2006 | 5334 | 496    | 11     | Technology        | 15.71%        |
| 2007 | 5243 | 487    | 11     | Technology        | 15.28%        |
| 2008 | 5106 | 477    | 11     | Technology        | 14.85%        |
| 2009 | 4892 | 463    | 11     | Technology        | 14.17%        |
| 2010 | 4716 | 432    | 11     | Technology        | 14.59%        |
| 2011 | 4586 | 423    | 11     | Technology        | 14.33%        |
| 2012 | 4465 | 410    | 11     | Technology        | 13.89%        |
| 2013 | 4410 | 396    | 11     | Energy            | 13.74%        |
| 2014 | 4500 | 409    | 11     | Energy            | 14.02%        |
| 2015 | 4549 | 428    | 11     | Healthcare        | 13.78%        |
| 2016 | 4464 | 417    | 11     | Technology        | 14.07%        |
| 2017 | 4388 | 401    | 11     | Industrials       | 14.63%        |
| 2018 | 4386 | 405    | 11     | Technology        | 16.19%        |
| 2019 | 4354 | 407    | 11     | Technology        | 18.63%        |
| 2020 | 4382 | 422    | 11     | Technology        | 20.13%        |
| 2021 | 4974 | 455    | 11     | Technology        | 22.50%        |
| 2022 | 5447 | 503    | 11     | Technology        | 21.41%        |
| 2023 | 5161 | 468    | 11     | Technology        | 20.15%        |
| 2024 | 4736 | 432    | 11     | Technology        | 21.03%        |
| 2025 | 4499 | 409    | 11     | Technology        | 21.89%        |
| 2026 | 2996 | 408    | 11     | Technology        | 22.20%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys   | n_1y  | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y  | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ------ | ----- | -------------- | ---------------- | ------- | ------- | ------------- | ----- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 5414   | 5414  | 3.62%          | 0.45%            | 50.92%  | 30.25%  | 4.01%         | 5414  | 0.19%          | 0.44%            | 51.09%  | 39.77%  | 12.19%        |
| 2006     | 5334   | 5334  | 2.59%          | -0.25%           | 49.44%  | 23.32%  | 3.73%         | 5334  | -0.40%         | 1.69%            | 55.27%  | 71.71%  | 10.31%        |
| 2007     | 5243   | 5243  | 2.88%          | 0.57%            | 51.40%  | 66.41%  | 3.49%         | 5243  | 1.00%          | 2.75%            | 59.74%  | 63.76%  | 7.82%         |
| 2008     | 5106   | 5106  | 3.50%          | 1.74%            | 52.70%  | 76.38%  | 2.29%         | 5106  | 2.24%          | 2.89%            | 58.50%  | 34.33%  | 6.11%         |
| 2009     | 4892   | 4892  | 8.36%          | 4.17%            | 56.23%  | 14.80%  | 1.96%         | 4892  | 1.59%          | 1.65%            | 54.64%  | 12.08%  | 5.52%         |
| 2010     | 4716   | 4716  | 4.28%          | 3.07%            | 55.81%  | 20.91%  | 1.29%         | 4716  | -0.65%         | 0.27%            | 50.91%  | 13.06%  | 4.16%         |
| 2011     | 4586   | 4586  | -2.05%         | -2.63%           | 44.94%  | 34.87%  | 1.50%         | 4586  | -1.00%         | -0.68%           | 47.54%  | 11.95%  | 4.16%         |
| 2012     | 4465   | 4465  | 1.31%          | -0.45%           | 48.96%  | 16.17%  | 1.10%         | 4465  | -1.50%         | -0.97%           | 45.82%  | 14.02%  | 4.55%         |
| 2013     | 4410   | 4410  | 1.56%          | -0.99%           | 48.30%  | 14.33%  | 1.02%         | 4410  | -2.91%         | -0.89%           | 46.76%  | 23.67%  | 5.85%         |
| 2014     | 4500   | 4500  | -1.97%         | -1.83%           | 46.96%  | 35.73%  | 1.62%         | 4500  | -4.27%         | -2.54%           | 41.11%  | 28.31%  | 7.69%         |
| 2015     | 4549   | 4549  | -2.83%         | -1.64%           | 46.71%  | 46.85%  | 3.14%         | 4549  | -4.05%         | -3.30%           | 40.18%  | 25.35%  | 8.57%         |
| 2016     | 4464   | 4464  | -1.32%         | -3.19%           | 43.48%  | 22.96%  | 3.02%         | 4464  | -2.82%         | -1.42%           | 44.58%  | 21.17%  | 8.67%         |
| 2017     | 4388   | 4388  | -2.30%         | -4.03%           | 42.98%  | 30.97%  | 2.39%         | 4388  | -4.33%         | -2.66%           | 42.23%  | 30.99%  | 7.57%         |
| 2018     | 4386   | 4386  | 0.67%          | 1.88%            | 53.37%  | 37.35%  | 3.26%         | 4386  | -3.61%         | -3.19%           | 41.11%  | 17.53%  | 6.61%         |
| 2019     | 4354   | 4354  | -2.11%         | -4.65%           | 42.37%  | 39.44%  | 2.04%         | 4354  | -2.86%         | -3.13%           | 39.02%  | 17.82%  | 4.09%         |
| 2020     | 4382   | 4382  | 3.03%          | -4.17%           | 44.34%  | 14.13%  | 1.10%         | 4382  | -2.60%         | -2.44%           | 42.49%  | 24.33%  | 3.58%         |
| 2021     | 4974   | 4974  | -3.99%         | -4.09%           | 43.26%  | 54.54%  | 1.29%         | 4974  | -7.61%         | -5.76%           | 32.75%  | 38.64%  | 3.92%         |
| 2022     | 5447   | 5447  | -3.00%         | -3.63%           | 43.69%  | 49.51%  | 0.84%         | 5447  | -8.72%         | -9.64%           | 28.97%  | 34.81%  | 3.23%         |
| 2023     | 5161   | 5161  | -9.54%         | -13.05%          | 31.64%  | 28.41%  | 1.09%         | 3494  | -10.30%        | -11.90%          | 24.47%  | 28.85%  | 3.32%         |
| 2024     | 4736   | 4736  | -5.12%         | -9.85%           | 35.94%  | 38.98%  | 0.40%         | 0     | —              | —                | —       | —       | —             |
| 2025     | 4499   | 3017  | -1.27%         | -10.87%          | 35.80%  | 36.13%  | 0.76%         | 0     | —              | —                | —       | —       | —             |
| 2026     | 2996   | 0     | —              | —                | —       | —       | —             | 0     | —              | —                | —       | —       | —             |
| all buys | 103002 | 98524 | -0.14%         | -2.11%           | 46.37%  | 35.36%  | 2.01%         | 89104 | -2.63%         | -1.58%           | 45.05%  | 29.93%  | 6.30%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 5414  | 0.19%       | 0.19%             | -0.00%        | 0.19%        | 0.00%    | 39.77%    | 39.77%          | 39.77%     |
| 2006     | 5334  | -0.40%      | -0.40%            | -0.00%        | -0.40%       | -0.00%   | 71.71%    | 71.71%          | 71.71%     |
| 2007     | 5243  | 1.00%       | 1.00%             | 0.00%         | 1.00%        | -0.00%   | 63.76%    | 63.76%          | 63.76%     |
| 2008     | 5106  | 2.24%       | 2.24%             | -0.00%        | 2.24%        | -0.00%   | 34.33%    | 34.33%          | 34.33%     |
| 2009     | 4892  | 1.59%       | 1.59%             | 0.00%         | 1.59%        | 0.00%    | 12.08%    | 12.08%          | 12.08%     |
| 2010     | 4716  | -0.65%      | -0.65%            | -0.00%        | -0.65%       | 0.00%    | 13.06%    | 13.06%          | 13.06%     |
| 2011     | 4586  | -1.00%      | -1.00%            | 0.00%         | -1.00%       | 0.00%    | 11.95%    | 11.95%          | 11.95%     |
| 2012     | 4465  | -1.50%      | -1.50%            | 0.00%         | -1.50%       | 0.00%    | 14.02%    | 14.02%          | 14.02%     |
| 2013     | 4410  | -2.91%      | -2.91%            | 0.00%         | -2.91%       | -0.00%   | 23.67%    | 23.67%          | 23.67%     |
| 2014     | 4500  | -4.27%      | -4.27%            | 0.00%         | -4.27%       | -0.00%   | 28.31%    | 28.31%          | 28.31%     |
| 2015     | 4549  | -4.05%      | -4.05%            | 0.00%         | -4.05%       | -0.00%   | 25.35%    | 25.35%          | 25.35%     |
| 2016     | 4464  | -2.82%      | -2.82%            | 0.00%         | -2.82%       | 0.00%    | 21.17%    | 21.17%          | 21.17%     |
| 2017     | 4388  | -4.33%      | -4.33%            | 0.00%         | -4.33%       | 0.00%    | 30.99%    | 30.99%          | 30.99%     |
| 2018     | 4386  | -3.61%      | -3.61%            | 0.00%         | -3.61%       | 0.00%    | 17.53%    | 17.53%          | 17.53%     |
| 2019     | 4354  | -2.86%      | -2.86%            | -0.00%        | -2.86%       | 0.00%    | 17.82%    | 17.82%          | 17.82%     |
| 2020     | 4382  | -2.60%      | -2.60%            | 0.00%         | -2.60%       | -0.00%   | 24.33%    | 24.33%          | 24.33%     |
| 2021     | 4974  | -7.61%      | -7.61%            | 0.00%         | -7.61%       | 0.00%    | 38.64%    | 38.64%          | 38.64%     |
| 2022     | 5447  | -8.72%      | -8.72%            | 0.00%         | -8.72%       | 0.00%    | 34.81%    | 34.81%          | 34.81%     |
| 2023     | 3494  | -10.30%     | -10.30%           | 0.00%         | -10.30%      | -0.00%   | 28.85%    | 28.85%          | 28.85%     |
| all buys | 89104 | -2.63%      | -2.63%            | -0.00%        | -2.63%       | -0.00%   | 29.93%    | 29.93%          | 29.93%     |

Over 1 year:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 5414  | 3.62%       | 3.62%             | 0.00%         | 3.62%        | -0.00%   | 30.25%    | 30.25%          | 30.25%     |
| 2006     | 5334  | 2.59%       | 2.59%             | 0.00%         | 2.59%        | 0.00%    | 23.32%    | 23.32%          | 23.32%     |
| 2007     | 5243  | 2.88%       | 2.88%             | 0.00%         | 2.88%        | 0.00%    | 66.41%    | 66.41%          | 66.41%     |
| 2008     | 5106  | 3.50%       | 3.50%             | 0.00%         | 3.50%        | 0.00%    | 76.38%    | 76.38%          | 76.38%     |
| 2009     | 4892  | 8.36%       | 8.36%             | 0.00%         | 8.36%        | -0.00%   | 14.80%    | 14.80%          | 14.80%     |
| 2010     | 4716  | 4.28%       | 4.28%             | 0.00%         | 4.28%        | 0.00%    | 20.91%    | 20.91%          | 20.91%     |
| 2011     | 4586  | -2.05%      | -2.05%            | 0.00%         | -2.05%       | 0.00%    | 34.87%    | 34.87%          | 34.87%     |
| 2012     | 4465  | 1.31%       | 1.31%             | 0.00%         | 1.31%        | -0.00%   | 16.17%    | 16.17%          | 16.17%     |
| 2013     | 4410  | 1.56%       | 1.56%             | 0.00%         | 1.56%        | -0.00%   | 14.33%    | 14.33%          | 14.33%     |
| 2014     | 4500  | -1.97%      | -1.97%            | -0.00%        | -1.97%       | 0.00%    | 35.73%    | 35.73%          | 35.73%     |
| 2015     | 4549  | -2.83%      | -2.83%            | 0.00%         | -2.83%       | -0.00%   | 46.85%    | 46.85%          | 46.85%     |
| 2016     | 4464  | -1.32%      | -1.32%            | 0.00%         | -1.32%       | 0.00%    | 22.96%    | 22.96%          | 22.96%     |
| 2017     | 4388  | -2.30%      | -2.30%            | 0.00%         | -2.30%       | 0.00%    | 30.97%    | 30.97%          | 30.97%     |
| 2018     | 4386  | 0.67%       | 0.67%             | -0.00%        | 0.67%        | -0.00%   | 37.35%    | 37.35%          | 37.35%     |
| 2019     | 4354  | -2.11%      | -2.11%            | 0.00%         | -2.11%       | 0.00%    | 39.44%    | 39.44%          | 39.44%     |
| 2020     | 4382  | 3.03%       | 3.03%             | -0.00%        | 3.03%        | -0.00%   | 14.13%    | 14.13%          | 14.13%     |
| 2021     | 4974  | -3.99%      | -3.99%            | 0.00%         | -3.99%       | 0.00%    | 54.54%    | 54.54%          | 54.54%     |
| 2022     | 5447  | -3.00%      | -3.00%            | 0.00%         | -3.00%       | -0.00%   | 49.51%    | 49.51%          | 49.51%     |
| 2023     | 5161  | -9.54%      | -9.54%            | 0.00%         | -9.54%       | -0.00%   | 28.41%    | 28.41%          | 28.41%     |
| 2024     | 4736  | -5.12%      | -5.12%            | 0.00%         | -5.12%       | 0.00%    | 38.98%    | 38.98%          | 38.98%     |
| 2025     | 3017  | -1.27%      | -1.27%            | -0.00%        | -1.27%       | 0.00%    | 36.13%    | 36.13%          | 36.13%     |
| all buys | 98524 | -0.14%      | -0.14%            | 0.00%         | -0.14%       | -0.00%   | 35.36%    | 35.36%          | 35.36%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=10000 picks: 260
- mean stocks in the point-in-time cross-section: 4063.3 (min 3639)
- mean after the per-model min_score floor: 4063.3 (min 3639)
- mean after the column filters: 4063.3 (min 3639)
- mean after the investability filter: 400.8 (min 363)
- mean with a tradable quote: 396.2 (min 360)
- forced delisting liquidations: 381 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 33 (this one included; every run is logged, failures too)
- fold definitions: `data/datasets/dataset_v1.4.1/split_folds.parquet` (frozen upstream; the buy window is the intersection of every bundle's fold years)
- model bundles:
- `forest_nonloser_dd30_3y_v141` — label `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y), model `random_forest`, config `0aeea637e84c41d9`, train run `f259c702a6a6`, folds 2005–2020; 2021–2026 served by year-end refits (from `experiments/models/forest_nonloser_dd30_3y_v141_f259c702a6a6`)

### Simulated year-end refits

One refit per (bundle, trade year) past that bundle's folds — trained on rows whose labels were observable by Jan 1, all snapshot kinds, delistings included, no split tags read. `source = cache` rows were reused from the refit cache (identical by construction: the cache key pins train config, dataset version, year, and label lag):

| bundle                       | trade_year | n_train_rows | effective_train_size | last_usable_snapshot | source |
| ---------------------------- | ---------- | ------------ | -------------------- | -------------------- | ------ |
| forest_nonloser_dd30_3y_v141 | 2021       | 1105684      | 38493.8000           | 2017-11-17           | cache  |
| forest_nonloser_dd30_3y_v141 | 2022       | 1149454      | 39914.7000           | 2018-11-16           | cache  |
| forest_nonloser_dd30_3y_v141 | 2023       | 1193792      | 41336                | 2019-11-15           | cache  |
| forest_nonloser_dd30_3y_v141 | 2024       | 1238172      | 42767.3000           | 2020-11-17           | cache  |
| forest_nonloser_dd30_3y_v141 | 2025       | 1289260      | 44618.4000           | 2021-11-17           | cache  |
| forest_nonloser_dd30_3y_v141 | 2026       | 1344427      | 46562.4000           | 2022-11-17           | cache  |

### Artifacts

- equity_curve: `reports/backtest/bt_lc90_mcap_all_v141_6c79822d076add76_equity.csv`
- trades: `reports/backtest/bt_lc90_mcap_all_v141_6c79822d076add76_trades.csv`
- rebalances: `reports/backtest/bt_lc90_mcap_all_v141_6c79822d076add76_rebalances.csv`
- equity_plot: `reports/backtest/bt_lc90_mcap_all_v141_6c79822d076add76_equity.png`
