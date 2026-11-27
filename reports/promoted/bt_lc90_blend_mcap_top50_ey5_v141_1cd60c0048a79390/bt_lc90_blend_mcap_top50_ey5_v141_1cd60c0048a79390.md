# Portfolio backtest — bt_lc90_blend_mcap_top50_ey5_v141

- run `bfa63bccabb4`, git `844d3cc7d9d90b38701e6a2c0e0b6ff147cf90c2`, backtest config `1cd60c0048a79390`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | cagr   | max_drawdown | twr    | costs_paid |
| --------- | ---------- | ------------ | ------------ | ------ | ------------ | ------ | ---------- |
| strategy  | 260,000.00 | 1,274,597.37 | 1,014,597.37 | 12.91% | -36.74%      | 12.08% | 1,109.69   |
| benchmark | 260,000.00 | 1,326,613.94 | 1,066,613.94 | 13.21% | -52.91%      | 10.94% | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess  | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------- | --------- | ------ | --------------- |
| 2005              | 11.37%       | 7.18%         | 4.20%   | 12,000.00 | 600    | -57.3233        |
| 2006              | 19.89%       | 13.64%        | 6.25%   | 12,000.00 | 600    | -59.2217        |
| 2007              | 17.05%       | 4.40%         | 12.65%  | 12,000.00 | 600    | -59.0983        |
| 2008 (GFC)        | -19.99%      | -34.33%       | 14.34%  | 12,000.00 | 600    | -66.7633        |
| 2009 (GFC)        | 14.06%       | 24.75%        | -10.69% | 12,000.00 | 600    | -64.4767        |
| 2010              | 13.34%       | 14.31%        | -0.97%  | 12,000.00 | 600    | -60.9017        |
| 2011              | 12.06%       | 2.45%         | 9.61%   | 12,000.00 | 600    | -61.8033        |
| 2012              | 11.99%       | 17.10%        | -5.10%  | 12,000.00 | 600    | -56.8728        |
| 2013              | 22.83%       | 27.76%        | -4.93%  | 12,000.00 | 600    | -49.4606        |
| 2014              | 14.04%       | 14.50%        | -0.46%  | 12,000.00 | 600    | -44.0100        |
| 2015              | 0.46%        | -0.11%        | 0.57%   | 12,000.00 | 600    | -43.0033        |
| 2016              | 15.38%       | 14.46%        | 0.92%   | 12,000.00 | 600    | -38.5944        |
| 2017              | 18.94%       | 21.64%        | -2.70%  | 12,000.00 | 600    | -37.9744        |
| 2018              | -6.43%       | -5.14%        | -1.29%  | 12,000.00 | 600    | -38.7811        |
| 2019              | 33.48%       | 32.31%        | 1.17%   | 12,000.00 | 600    | -40.4011        |
| 2020 (COVID)      | 13.75%       | 15.68%        | -1.93%  | 12,000.00 | 600    | -32.8506        |
| 2021              | 29.73%       | 31.28%        | -1.55%  | 12,000.00 | 600    | -28.1933        |
| 2022 (rate-shock) | -7.73%       | -18.99%       | 11.25%  | 12,000.00 | 600    | -40.8083        |
| 2023              | 15.57%       | 26.01%        | -10.44% | 12,000.00 | 600    | -43.9411        |
| 2024              | 16.68%       | 25.28%        | -8.61%  | 12,000.00 | 600    | -38.4878        |
| 2025              | 15.21%       | 18.22%        | -3.01%  | 12,000.00 | 600    | -34.3567        |
| 2026              | 13.92%       | 12.68%        | 1.24%   | 8,000.00  | 400    | -30.6825        |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 3 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- `earnings_yield >= 0.05`
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `log_marketcap_rank >= 0.9`
- selection: top 50 by combined score, `marketcap`-weighted; strategy `buy_and_hold`
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Industrials            | 2609 | 20.07% |
| Consumer Defensive     | 2361 | 18.16% |
| Healthcare             | 1611 | 12.39% |
| Technology             | 1508 | 11.60% |
| Consumer Cyclical      | 1455 | 11.19% |
| Communication Services | 1016 | 7.82%  |
| Energy                 | 873  | 6.72%  |
| Utilities              | 739  | 5.68%  |
| Basic Materials        | 527  | 4.05%  |
| Real Estate            | 178  | 1.37%  |
| Financial Services     | 123  | 0.95%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 600  | 96     | 11     | Consumer Defensive | 20.50%        |
| 2006 | 600  | 101    | 11     | Industrials        | 30.50%        |
| 2007 | 600  | 92     | 11     | Industrials        | 27.67%        |
| 2008 | 600  | 92     | 9      | Industrials        | 32.17%        |
| 2009 | 600  | 83     | 9      | Consumer Defensive | 36.50%        |
| 2010 | 600  | 91     | 10     | Consumer Defensive | 28.00%        |
| 2011 | 600  | 88     | 10     | Consumer Defensive | 32.50%        |
| 2012 | 600  | 91     | 10     | Consumer Defensive | 34.50%        |
| 2013 | 600  | 87     | 9      | Consumer Defensive | 23.17%        |
| 2014 | 600  | 85     | 10     | Consumer Defensive | 27.50%        |
| 2015 | 600  | 98     | 11     | Industrials        | 26.33%        |
| 2016 | 600  | 94     | 11     | Industrials        | 27.00%        |
| 2017 | 600  | 98     | 10     | Industrials        | 24.50%        |
| 2018 | 600  | 106    | 11     | Consumer Defensive | 16.00%        |
| 2019 | 600  | 100    | 10     | Industrials        | 30.50%        |
| 2020 | 600  | 96     | 10     | Industrials        | 23.67%        |
| 2021 | 600  | 90     | 9      | Healthcare         | 20.50%        |
| 2022 | 600  | 100    | 10     | Healthcare         | 20.00%        |
| 2023 | 600  | 94     | 9      | Industrials        | 25.00%        |
| 2024 | 600  | 96     | 10     | Energy             | 24.50%        |
| 2025 | 600  | 90     | 11     | Industrials        | 20.50%        |
| 2026 | 400  | 82     | 10     | Energy             | 22.00%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys  | n_1y  | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y  | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ----- | ----- | -------------- | ---------------- | ------- | ------- | ------------- | ----- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 600   | 600   | 4.48%          | 1.53%            | 53.17%  | 23.33%  | 1.50%         | 600   | 2.92%          | 4.06%            | 63.83%  | 27.83%  | 7.00%         |
| 2006     | 600   | 600   | 6.08%          | 2.55%            | 57.33%  | 10.83%  | 3.17%         | 600   | 5.81%          | 6.12%            | 75.50%  | 61.17%  | 8.33%         |
| 2007     | 600   | 600   | 6.01%          | 6.73%            | 62.83%  | 60.50%  | 1.00%         | 600   | 5.18%          | 6.22%            | 75.17%  | 52.83%  | 4.50%         |
| 2008     | 600   | 600   | 4.77%          | 5.60%            | 65.00%  | 79.33%  | 2.33%         | 600   | 2.38%          | 3.05%            | 63.67%  | 26.00%  | 3.83%         |
| 2009     | 600   | 600   | -2.44%         | -2.57%           | 44.00%  | 11.83%  | 0.83%         | 600   | 0.78%          | -0.27%           | 48.83%  | 4.67%   | 2.33%         |
| 2010     | 600   | 600   | 5.63%          | 5.45%            | 61.00%  | 13.83%  | 0.00%         | 600   | 3.19%          | 3.83%            | 62.67%  | 4.17%   | 2.50%         |
| 2011     | 600   | 600   | 7.18%          | 3.06%            | 58.00%  | 17.17%  | 0.00%         | 600   | 1.95%          | 2.15%            | 58.17%  | 2.33%   | 4.50%         |
| 2012     | 600   | 600   | 1.41%          | 1.43%            | 52.67%  | 10.83%  | 1.00%         | 600   | 1.53%          | 2.05%            | 57.83%  | 9.50%   | 6.00%         |
| 2013     | 600   | 600   | 1.46%          | 0.85%            | 51.50%  | 11.67%  | 1.00%         | 600   | 2.13%          | 2.58%            | 61.00%  | 12.67%  | 5.33%         |
| 2014     | 600   | 600   | 3.57%          | 2.78%            | 54.67%  | 23.50%  | 2.17%         | 600   | 0.38%          | 0.76%            | 53.00%  | 13.33%  | 10.17%        |
| 2015     | 600   | 600   | 1.74%          | 4.09%            | 57.17%  | 35.50%  | 3.33%         | 600   | -1.25%         | 0.32%            | 51.17%  | 13.67%  | 10.17%        |
| 2016     | 600   | 600   | -2.85%         | -1.41%           | 47.00%  | 19.50%  | 2.17%         | 600   | -1.92%         | -0.89%           | 45.67%  | 13.50%  | 10.17%        |
| 2017     | 600   | 600   | -1.69%         | -2.24%           | 45.33%  | 26.33%  | 1.83%         | 600   | -3.11%         | -2.32%           | 42.00%  | 24.17%  | 7.17%         |
| 2018     | 600   | 600   | 1.46%          | 0.41%            | 51.00%  | 38.33%  | 3.83%         | 600   | -2.35%         | -3.19%           | 40.33%  | 11.83%  | 4.00%         |
| 2019     | 600   | 600   | -6.62%         | -9.01%           | 34.17%  | 43.50%  | 4.00%         | 600   | -2.23%         | -1.53%           | 42.17%  | 14.33%  | 4.50%         |
| 2020     | 600   | 600   | -3.99%         | -10.04%          | 38.50%  | 18.33%  | 1.17%         | 600   | -1.74%         | -1.26%           | 46.50%  | 20.17%  | 1.67%         |
| 2021     | 600   | 600   | 3.80%          | 2.33%            | 52.83%  | 42.50%  | 0.00%         | 600   | -4.70%         | -3.36%           | 41.17%  | 31.50%  | 1.83%         |
| 2022     | 600   | 600   | -3.08%         | -5.89%           | 41.83%  | 48.00%  | 0.00%         | 600   | -11.60%        | -10.46%          | 21.00%  | 35.00%  | 0.50%         |
| 2023     | 600   | 600   | -12.10%        | -14.96%          | 26.00%  | 26.00%  | 0.00%         | 400   | -9.69%         | -8.65%           | 23.75%  | 22.25%  | 3.50%         |
| 2024     | 600   | 600   | -6.87%         | -9.02%           | 35.83%  | 36.83%  | 0.00%         | 0     | —              | —                | —       | —       | —             |
| 2025     | 600   | 400   | -4.31%         | -7.37%           | 35.50%  | 25.75%  | 0.00%         | 0     | —              | —                | —       | —       | —             |
| 2026     | 400   | 0     | —              | —                | —       | —       | —             | 0     | —              | —                | —       | —       | —             |
| all buys | 13000 | 12400 | 0.25%          | -0.51%           | 49.04%  | 29.75%  | 1.42%         | 11200 | -0.49%         | 0.46%            | 51.72%  | 21.08%  | 5.19%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 600   | 2.92%       | 0.60%             | 2.32%         | 0.80%        | 2.13%    | 27.83%    | 37.87%          | 37.19%     |
| 2006     | 600   | 5.81%       | 1.93%             | 3.89%         | 2.17%        | 3.64%    | 61.17%    | 66.61%          | 66.01%     |
| 2007     | 600   | 5.18%       | 2.42%             | 2.76%         | 2.53%        | 2.64%    | 52.83%    | 60.32%          | 60.59%     |
| 2008     | 600   | 2.38%       | 2.96%             | -0.58%        | 1.83%        | 0.56%    | 26.00%    | 31.34%          | 33.27%     |
| 2009     | 600   | 0.78%       | 1.70%             | -0.92%        | 0.76%        | 0.02%    | 4.67%     | 10.65%          | 10.70%     |
| 2010     | 600   | 3.19%       | -0.48%            | 3.67%         | -0.44%       | 3.62%    | 4.17%     | 11.51%          | 11.66%     |
| 2011     | 600   | 1.95%       | -0.05%            | 2.00%         | 0.00%        | 1.94%    | 2.33%     | 10.17%          | 10.37%     |
| 2012     | 600   | 1.53%       | -1.06%            | 2.59%         | -1.05%       | 2.58%    | 9.50%     | 12.50%          | 12.51%     |
| 2013     | 600   | 2.13%       | -2.43%            | 4.56%         | -2.56%       | 4.69%    | 12.67%    | 22.75%          | 22.29%     |
| 2014     | 600   | 0.38%       | -4.94%            | 5.32%         | -4.40%       | 4.77%    | 13.33%    | 27.27%          | 25.24%     |
| 2015     | 600   | -1.25%      | -2.73%            | 1.48%         | -2.57%       | 1.32%    | 13.67%    | 23.13%          | 22.60%     |
| 2016     | 600   | -1.92%      | -2.58%            | 0.66%         | -2.37%       | 0.46%    | 13.50%    | 18.36%          | 17.62%     |
| 2017     | 600   | -3.11%      | -6.53%            | 3.42%         | -6.28%       | 3.17%    | 24.17%    | 35.80%          | 35.66%     |
| 2018     | 600   | -2.35%      | -5.93%            | 3.59%         | -5.45%       | 3.10%    | 11.83%    | 21.45%          | 21.36%     |
| 2019     | 600   | -2.23%      | -3.06%            | 0.84%         | -2.91%       | 0.68%    | 14.33%    | 17.75%          | 17.60%     |
| 2020     | 600   | -1.74%      | 1.16%             | -2.90%        | 1.12%        | -2.86%   | 20.17%    | 17.34%          | 17.59%     |
| 2021     | 600   | -4.70%      | -4.36%            | -0.34%        | -4.30%       | -0.40%   | 31.50%    | 31.61%          | 31.61%     |
| 2022     | 600   | -11.60%     | -10.02%           | -1.58%        | -9.72%       | -1.88%   | 35.00%    | 33.84%          | 34.89%     |
| 2023     | 400   | -9.69%      | -8.66%            | -1.03%        | -7.88%       | -1.81%   | 22.25%    | 23.22%          | 22.12%     |
| all buys | 11200 | -0.49%      | -1.27%            | 0.78%         | -2.04%       | 1.55%    | 21.08%    | 26.67%          | 26.97%     |

Over 1 year:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 600   | 4.48%       | 3.45%             | 1.03%         | 3.36%        | 1.12%    | 23.33%    | 28.11%          | 28.11%     |
| 2006     | 600   | 6.08%       | 3.91%             | 2.17%         | 4.15%        | 1.93%    | 10.83%    | 18.16%          | 17.36%     |
| 2007     | 600   | 6.01%       | 5.93%             | 0.09%         | 6.88%        | -0.87%   | 60.50%    | 61.91%          | 60.41%     |
| 2008     | 600   | 4.77%       | 4.24%             | 0.53%         | 3.36%        | 1.42%    | 79.33%    | 75.13%          | 77.43%     |
| 2009     | 600   | -2.44%      | 6.84%             | -9.28%        | 4.79%        | -7.23%   | 11.83%    | 13.70%          | 14.81%     |
| 2010     | 600   | 5.63%       | 2.89%             | 2.74%         | 2.97%        | 2.66%    | 13.83%    | 20.30%          | 19.38%     |
| 2011     | 600   | 7.18%       | -0.52%            | 7.70%         | -0.36%       | 7.55%    | 17.17%    | 30.73%          | 31.41%     |
| 2012     | 600   | 1.41%       | 2.36%             | -0.94%        | 2.24%        | -0.82%   | 10.83%    | 14.05%          | 14.08%     |
| 2013     | 600   | 1.46%       | 1.42%             | 0.04%         | 1.33%        | 0.13%    | 11.67%    | 11.92%          | 11.46%     |
| 2014     | 600   | 3.57%       | -4.64%            | 8.21%         | -4.08%       | 7.65%    | 23.50%    | 39.04%          | 38.10%     |
| 2015     | 600   | 1.74%       | -3.02%            | 4.77%         | -3.03%       | 4.77%    | 35.50%    | 48.04%          | 47.87%     |
| 2016     | 600   | -2.85%      | 1.20%             | -4.06%        | 0.54%        | -3.40%   | 19.50%    | 19.11%          | 18.88%     |
| 2017     | 600   | -1.69%      | -4.91%            | 3.22%         | -4.55%       | 2.86%    | 26.33%    | 34.71%          | 34.20%     |
| 2018     | 600   | 1.46%       | -1.67%            | 3.13%         | -1.23%       | 2.70%    | 38.33%    | 43.28%          | 43.36%     |
| 2019     | 600   | -6.62%      | -11.57%           | 4.95%         | -11.50%      | 4.88%    | 43.50%    | 49.21%          | 49.43%     |
| 2020     | 600   | -3.99%      | 4.17%             | -8.15%        | 3.20%        | -7.19%   | 18.33%    | 14.68%          | 15.29%     |
| 2021     | 600   | 3.80%       | 4.66%             | -0.86%        | 4.43%        | -0.63%   | 42.50%    | 42.86%          | 41.86%     |
| 2022     | 600   | -3.08%      | -1.85%            | -1.24%        | -0.40%       | -2.69%   | 48.00%    | 43.46%          | 45.45%     |
| 2023     | 600   | -12.10%     | -10.67%           | -1.43%        | -10.21%      | -1.88%   | 26.00%    | 27.78%          | 26.81%     |
| 2024     | 600   | -6.87%      | -9.36%            | 2.49%         | -9.31%       | 2.44%    | 36.83%    | 41.20%          | 41.23%     |
| 2025     | 400   | -4.31%      | 2.98%             | -7.29%        | 3.10%        | -7.41%   | 25.75%    | 24.39%          | 23.77%     |
| all buys | 12400 | 0.25%       | 0.62%             | -0.37%        | -0.26%       | 0.51%    | 29.75%    | 32.83%          | 33.52%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=50 picks: 0
- mean stocks in the point-in-time cross-section: 4063.3 (min 3639)
- mean after the per-model min_score floor: 4063.3 (min 3639)
- mean after the column filters: 1066.3 (min 456)
- mean after the investability filter: 157.5 (min 58)
- mean with a tradable quote: 156.5 (min 58)
- forced delisting liquidations: 106 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 44 (this one included; every run is logged, failures too)
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

- equity_curve: `reports/backtest/bt_lc90_blend_mcap_top50_ey5_v141_1cd60c0048a79390_equity.csv`
- trades: `reports/backtest/bt_lc90_blend_mcap_top50_ey5_v141_1cd60c0048a79390_trades.csv`
- rebalances: `reports/backtest/bt_lc90_blend_mcap_top50_ey5_v141_1cd60c0048a79390_rebalances.csv`
- equity_plot: `reports/backtest/bt_lc90_blend_mcap_top50_ey5_v141_1cd60c0048a79390_equity.png`
