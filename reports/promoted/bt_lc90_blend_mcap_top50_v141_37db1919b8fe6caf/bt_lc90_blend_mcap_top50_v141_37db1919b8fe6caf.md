# Portfolio backtest — bt_lc90_blend_mcap_top50_v141

- run `b03bdcda8712`, git `e5d655a2eddc519c72386e6260ab7d3f9e07e08b`, backtest config `37db1919b8fe6caf`
- dataset `1.4.1` (sha256 `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085`), price panel `prices_v1.0` (benchmark `SPY`)
- buy window: 2005–2026 (last buy 2026-08-21), valuation through 2026-08-21; trade years past a bundle's walk-forward folds are served by `model_update = "refit"` (see the bundle list below)
- deposits: 1,000.00 on the first trading day of each month, identically into both legs

**These are simulated, cost-adjusted paper results under the assumptions below — not live performance.** Scores come from walk-forward fold models (each trade year scored by a model trained, purged and embargoed, on years before it); deployment bundles are never backtested.

## Headline

| leg       | deposits   | final_value  | profit       | cagr   | max_drawdown | twr    | costs_paid |
| --------- | ---------- | ------------ | ------------ | ------ | ------------ | ------ | ---------- |
| strategy  | 260,000.00 | 1,255,864.08 | 995,864.08   | 12.80% | -37.39%      | 11.88% | 1,115.58   |
| benchmark | 260,000.00 | 1,326,613.94 | 1,066,613.94 | 13.21% | -52.91%      | 10.94% | 0.00       |

`cagr` is the money-weighted annual growth rate of the deposits into the final value (XIRR), the metric of record: both legs get identical deposit dates and accounting, so it ranks them as the final value does. `twr` is the time-weighted return, the compounding of one unit held from the first day to the last; it gives a month on a tiny early account the weight of a month on a full one, so it is read only beside the final value, the CAGR and the per-year table (decision 72).

## Per-year results (era slice)

| year              | strategy_twr | benchmark_twr | excess | deposits  | n_buys | mean_pick_score |
| ----------------- | ------------ | ------------- | ------ | --------- | ------ | --------------- |
| 2005              | 11.63%       | 7.18%         | 4.45%  | 12,000.00 | 600    | -108.1922       |
| 2006              | 17.47%       | 13.64%        | 3.83%  | 12,000.00 | 600    | -108.3772       |
| 2007              | 15.55%       | 4.40%         | 11.15% | 12,000.00 | 600    | -102.2794       |
| 2008 (GFC)        | -21.90%      | -34.33%       | 12.43% | 12,000.00 | 600    | -102.1133       |
| 2009 (GFC)        | 16.04%       | 24.75%        | -8.71% | 12,000.00 | 600    | -76.3011        |
| 2010              | 12.26%       | 14.31%        | -2.04% | 12,000.00 | 600    | -100.7183       |
| 2011              | 10.37%       | 2.45%         | 7.92%  | 12,000.00 | 600    | -89.8500        |
| 2012              | 13.39%       | 17.10%        | -3.71% | 12,000.00 | 600    | -76.9439        |
| 2013              | 23.56%       | 27.76%        | -4.21% | 12,000.00 | 600    | -77.4500        |
| 2014              | 15.62%       | 14.50%        | 1.12%  | 12,000.00 | 600    | -86.2178        |
| 2015              | 1.70%        | -0.11%        | 1.81%  | 12,000.00 | 600    | -82.8617        |
| 2016              | 13.47%       | 14.46%        | -0.99% | 12,000.00 | 600    | -70.8128        |
| 2017              | 21.24%       | 21.64%        | -0.40% | 12,000.00 | 600    | -84.1511        |
| 2018              | -4.32%       | -5.14%        | 0.82%  | 12,000.00 | 600    | -80.7528        |
| 2019              | 35.59%       | 32.31%        | 3.28%  | 12,000.00 | 600    | -81.8972        |
| 2020 (COVID)      | 16.10%       | 15.68%        | 0.42%  | 12,000.00 | 600    | -81.7733        |
| 2021              | 29.75%       | 31.28%        | -1.53% | 12,000.00 | 600    | -96.5561        |
| 2022 (rate-shock) | -10.59%      | -18.99%       | 8.39%  | 12,000.00 | 600    | -93.1722        |
| 2023              | 17.99%       | 26.01%        | -8.02% | 12,000.00 | 600    | -80.1928        |
| 2024              | 16.98%       | 25.28%        | -8.30% | 12,000.00 | 600    | -86.8139        |
| 2025              | 11.36%       | 18.22%        | -6.86% | 12,000.00 | 600    | -85.1017        |
| 2026              | 9.48%        | 12.68%        | -3.20% | 8,000.00  | 400    | -94.1825        |

Per-year returns are time-weighted within the year: a year's return is the same whatever the account held, so an early year on a small account reads like a late year on a full one. The headline CAGR weights the years by the money invested.

**Defensive hypothesis:** Benchmark down-years in window: 4; strategy lost less (positive excess) in 4 of them. See the tagged rows above — few, correlated observations, wide uncertainty.

## Strategy definition

- signal: 3 walk-forward model(s), combined by `mean_rank`

- filters (NULL fails any screen):
- (none)
- investability filter:
- `dollar_volume_3m_rank >= 0.2`
- `log_marketcap_rank >= 0.9`
- selection: top 50 by combined score, `marketcap`-weighted; strategy `buy_and_hold`
- costs: 35.0 bps per side (benchmark 0.0 bps)

## What was bought, by `sector`

Shares of the number of buys. A portfolio whose buys sit in one group is one bet, however many stocks it holds.

| group                  | buys | share  |
| ---------------------- | ---- | ------ |
| Consumer Defensive     | 3013 | 23.18% |
| Industrials            | 2936 | 22.58% |
| Technology             | 2017 | 15.52% |
| Healthcare             | 1932 | 14.86% |
| Consumer Cyclical      | 1429 | 10.99% |
| Communication Services | 566  | 4.35%  |
| Financial Services     | 505  | 3.88%  |
| Basic Materials        | 321  | 2.47%  |
| Energy                 | 221  | 1.70%  |
| Utilities              | 39   | 0.30%  |
| Real Estate            | 21   | 0.16%  |

| year | buys | stocks | groups | largest_group      | largest_share |
| ---- | ---- | ------ | ------ | ------------------ | ------------- |
| 2005 | 600  | 93     | 10     | Consumer Defensive | 26.50%        |
| 2006 | 600  | 100    | 10     | Industrials        | 28.33%        |
| 2007 | 600  | 91     | 10     | Industrials        | 26.17%        |
| 2008 | 600  | 82     | 9      | Industrials        | 30.33%        |
| 2009 | 600  | 85     | 9      | Consumer Defensive | 35.17%        |
| 2010 | 600  | 108    | 9      | Consumer Defensive | 26.00%        |
| 2011 | 600  | 91     | 9      | Consumer Defensive | 27.00%        |
| 2012 | 600  | 84     | 9      | Consumer Defensive | 36.83%        |
| 2013 | 600  | 88     | 8      | Consumer Defensive | 28.00%        |
| 2014 | 600  | 92     | 9      | Industrials        | 24.50%        |
| 2015 | 600  | 89     | 10     | Consumer Defensive | 28.17%        |
| 2016 | 600  | 89     | 8      | Consumer Defensive | 37.33%        |
| 2017 | 600  | 92     | 8      | Industrials        | 32.33%        |
| 2018 | 600  | 90     | 9      | Industrials        | 28.00%        |
| 2019 | 600  | 91     | 10     | Consumer Defensive | 21.50%        |
| 2020 | 600  | 107    | 9      | Consumer Defensive | 27.50%        |
| 2021 | 600  | 104    | 8      | Technology         | 27.00%        |
| 2022 | 600  | 101    | 8      | Industrials        | 22.83%        |
| 2023 | 600  | 90     | 8      | Industrials        | 30.00%        |
| 2024 | 600  | 96     | 9      | Industrials        | 31.00%        |
| 2025 | 600  | 91     | 9      | Industrials        | 32.00%        |
| 2026 | 400  | 88     | 9      | Industrials        | 33.50%        |

## What the buys went on to do

Every buy read on its own, over the 1, 3 years after its trade date, from the price panel: `mean_excess` and `median_excess` are the buys' annualized return minus the benchmark's over the same dates, `beat` the share above it, `lost` the share with a negative return, `early_exit` the share that stopped printing before the horizon (they exit at the final print and the proceeds ride the benchmark to the horizon, as a portfolio reinvests what an acquisition pays out). `n` counts the buys whose horizon ends inside the valuation window. One buy, one vote, no costs: this reads the selection, where the headline reads the portfolio (time-weighted return gives the small early portfolio the weight of the large late one; money-weighted return the reverse).

| year     | buys  | n_1y  | mean_excess_1y | median_excess_1y | beat_1y | lost_1y | early_exit_1y | n_3y  | mean_excess_3y | median_excess_3y | beat_3y | lost_3y | early_exit_3y |
| -------- | ----- | ----- | -------------- | ---------------- | ------- | ------- | ------------- | ----- | -------------- | ---------------- | ------- | ------- | ------------- |
| 2005     | 600   | 600   | 2.17%          | 1.47%            | 52.67%  | 24.00%  | 2.00%         | 600   | 2.35%          | 2.39%            | 59.00%  | 31.50%  | 3.50%         |
| 2006     | 600   | 600   | 0.69%          | 0.36%            | 51.33%  | 14.33%  | 4.33%         | 600   | 4.56%          | 5.88%            | 75.50%  | 63.33%  | 8.17%         |
| 2007     | 600   | 600   | 6.12%          | 8.36%            | 65.00%  | 57.67%  | 0.83%         | 600   | 6.06%          | 7.07%            | 78.17%  | 47.67%  | 4.17%         |
| 2008     | 600   | 600   | 7.33%          | 8.20%            | 69.83%  | 78.33%  | 3.50%         | 600   | 2.59%          | 3.61%            | 66.17%  | 23.17%  | 3.50%         |
| 2009     | 600   | 600   | -2.68%         | -2.29%           | 44.67%  | 11.50%  | 1.33%         | 600   | 0.80%          | 0.61%            | 51.83%  | 4.33%   | 4.17%         |
| 2010     | 600   | 600   | 7.59%          | 6.02%            | 63.00%  | 12.67%  | 0.17%         | 600   | 3.45%          | 4.24%            | 61.83%  | 4.17%   | 3.83%         |
| 2011     | 600   | 600   | 6.45%          | 2.70%            | 57.17%  | 19.83%  | 0.00%         | 600   | 1.11%          | 1.86%            | 56.50%  | 6.33%   | 4.00%         |
| 2012     | 600   | 600   | 0.46%          | -0.14%           | 49.67%  | 11.83%  | 0.67%         | 600   | 2.96%          | 3.17%            | 63.00%  | 5.50%   | 4.83%         |
| 2013     | 600   | 600   | 0.46%          | -1.98%           | 46.00%  | 9.83%   | 1.00%         | 600   | 2.50%          | 3.39%            | 64.67%  | 10.33%  | 1.50%         |
| 2014     | 600   | 600   | 7.36%          | 6.89%            | 64.83%  | 15.83%  | 2.67%         | 600   | 0.84%          | 1.03%            | 53.33%  | 12.67%  | 7.50%         |
| 2015     | 600   | 600   | 5.33%          | 5.67%            | 65.33%  | 27.67%  | 3.00%         | 600   | -1.46%         | 1.17%            | 53.67%  | 17.50%  | 6.67%         |
| 2016     | 600   | 600   | -6.35%         | -5.92%           | 37.17%  | 24.67%  | 2.33%         | 600   | -1.64%         | -0.57%           | 47.83%  | 15.33%  | 5.83%         |
| 2017     | 600   | 600   | 2.27%          | 3.13%            | 55.50%  | 19.50%  | 1.83%         | 600   | 1.67%          | 2.10%            | 58.17%  | 17.17%  | 5.33%         |
| 2018     | 600   | 600   | 9.09%          | 8.32%            | 71.17%  | 22.67%  | 2.67%         | 600   | 1.10%          | 1.00%            | 54.17%  | 6.00%   | 7.50%         |
| 2019     | 600   | 600   | 0.91%          | -1.47%           | 46.00%  | 29.33%  | 1.50%         | 600   | -1.84%         | -2.62%           | 39.67%  | 11.67%  | 1.50%         |
| 2020     | 600   | 600   | -9.69%         | -10.96%          | 33.33%  | 17.50%  | 0.17%         | 600   | -2.20%         | -2.90%           | 37.33%  | 16.83%  | 3.67%         |
| 2021     | 600   | 600   | -3.39%         | -3.70%           | 41.83%  | 54.83%  | 1.50%         | 600   | -4.51%         | -4.46%           | 28.83%  | 29.00%  | 3.50%         |
| 2022     | 600   | 600   | -2.21%         | -2.44%           | 44.17%  | 45.83%  | 0.33%         | 600   | -7.85%         | -8.46%           | 26.33%  | 30.67%  | 0.33%         |
| 2023     | 600   | 600   | -6.62%         | -10.81%          | 32.67%  | 22.83%  | 0.00%         | 400   | -12.32%        | -11.58%          | 18.75%  | 26.50%  | 1.75%         |
| 2024     | 600   | 600   | -2.75%         | -2.73%           | 45.17%  | 24.33%  | 0.00%         | 0     | —              | —                | —       | —       | —             |
| 2025     | 600   | 400   | -17.44%        | -18.86%          | 23.75%  | 47.50%  | 1.75%         | 0     | —              | —                | —       | —       | —             |
| 2026     | 400   | 0     | —              | —                | —       | —       | —             | 0     | —              | —                | —       | —       | —             |
| all buys | 13000 | 12400 | 0.53%          | 0.40%            | 50.92%  | 27.90%  | 1.50%         | 11200 | 0.12%          | 0.84%            | 52.96%  | 19.87%  | 4.32%         |

### Against the stocks they were chosen from

The same reading for every candidate of every rebalance (each stock that passed the screens and had a quote), equal-weighted: `candidates_excess` is their mean annualized return minus the benchmark's, `vs_candidates` the buys' mean minus theirs, `*_lost` the shares with a negative return. `peers_excess` is the mean, over the buys, of the candidates of the same rebalance in the same band of `log_marketcap_rank` (20 bands), and `vs_peers` the buys' mean lead over them. **Read `vs_peers` for the selection.** Against a capitalization-weighted benchmark the average small stock trails by a wide margin in every period, so a ranking that only prefers large companies beats `candidates` without choosing well among them; and when `candidates_excess` and `peers_excess` are far below zero, the benchmark outran equal-weighted stocks of every kind and no equal-weighted selection from this universe kept up with it.

Over 3 years:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 600   | 2.35%       | 0.19%             | 2.16%         | 0.31%        | 2.05%    | 31.50%    | 39.77%          | 39.55%     |
| 2006     | 600   | 4.56%       | -0.40%            | 4.95%         | 0.01%        | 4.54%    | 63.33%    | 71.71%          | 70.96%     |
| 2007     | 600   | 6.06%       | 1.00%             | 5.06%         | 1.39%        | 4.67%    | 47.67%    | 63.76%          | 63.67%     |
| 2008     | 600   | 2.59%       | 2.24%             | 0.36%         | 1.67%        | 0.92%    | 23.17%    | 34.33%          | 35.40%     |
| 2009     | 600   | 0.80%       | 1.59%             | -0.79%        | 0.83%        | -0.03%   | 4.33%     | 12.08%          | 11.99%     |
| 2010     | 600   | 3.45%       | -0.65%            | 4.11%         | -0.68%       | 4.13%    | 4.17%     | 13.06%          | 12.98%     |
| 2011     | 600   | 1.11%       | -1.00%            | 2.10%         | -1.03%       | 2.14%    | 6.33%     | 11.95%          | 11.83%     |
| 2012     | 600   | 2.96%       | -1.50%            | 4.46%         | -1.47%       | 4.42%    | 5.50%     | 14.02%          | 13.87%     |
| 2013     | 600   | 2.50%       | -2.91%            | 5.41%         | -2.67%       | 5.17%    | 10.33%    | 23.67%          | 22.80%     |
| 2014     | 600   | 0.84%       | -4.27%            | 5.11%         | -4.04%       | 4.88%    | 12.67%    | 28.31%          | 27.30%     |
| 2015     | 600   | -1.46%      | -4.05%            | 2.59%         | -3.86%       | 2.39%    | 17.50%    | 25.35%          | 24.64%     |
| 2016     | 600   | -1.64%      | -2.82%            | 1.17%         | -2.59%       | 0.95%    | 15.33%    | 21.17%          | 20.62%     |
| 2017     | 600   | 1.67%       | -4.33%            | 6.00%         | -4.04%       | 5.71%    | 17.17%    | 30.99%          | 30.32%     |
| 2018     | 600   | 1.10%       | -3.61%            | 4.71%         | -3.31%       | 4.41%    | 6.00%     | 17.53%          | 17.05%     |
| 2019     | 600   | -1.84%      | -2.86%            | 1.03%         | -2.70%       | 0.86%    | 11.67%    | 17.82%          | 17.32%     |
| 2020     | 600   | -2.20%      | -2.60%            | 0.40%         | -2.49%       | 0.30%    | 16.83%    | 24.33%          | 23.52%     |
| 2021     | 600   | -4.51%      | -7.61%            | 3.09%         | -7.23%       | 2.72%    | 29.00%    | 38.64%          | 37.40%     |
| 2022     | 600   | -7.85%      | -8.72%            | 0.87%         | -7.86%       | 0.01%    | 30.67%    | 34.81%          | 32.72%     |
| 2023     | 400   | -12.32%     | -10.30%           | -2.02%        | -9.51%       | -2.82%   | 26.50%    | 28.85%          | 27.06%     |
| all buys | 11200 | 0.12%       | -2.63%            | 2.75%         | -2.47%       | 2.59%    | 19.87%    | 29.93%          | 28.50%     |

Over 1 year:

| year     | buys  | buys_excess | candidates_excess | vs_candidates | peers_excess | vs_peers | buys_lost | candidates_lost | peers_lost |
| -------- | ----- | ----------- | ----------------- | ------------- | ------------ | -------- | --------- | --------------- | ---------- |
| 2005     | 600   | 2.17%       | 3.62%             | -1.46%        | 3.26%        | -1.09%   | 24.00%    | 30.25%          | 30.27%     |
| 2006     | 600   | 0.69%       | 2.59%             | -1.90%        | 2.61%        | -1.93%   | 14.33%    | 23.32%          | 22.68%     |
| 2007     | 600   | 6.12%       | 2.88%             | 3.24%         | 4.28%        | 1.83%    | 57.67%    | 66.41%          | 64.79%     |
| 2008     | 600   | 7.33%       | 3.50%             | 3.83%         | 3.77%        | 3.56%    | 78.33%    | 76.38%          | 76.77%     |
| 2009     | 600   | -2.68%      | 8.36%             | -11.04%       | 6.46%        | -9.14%   | 11.50%    | 14.80%          | 15.11%     |
| 2010     | 600   | 7.59%       | 4.28%             | 3.30%         | 4.18%        | 3.40%    | 12.67%    | 20.91%          | 20.91%     |
| 2011     | 600   | 6.45%       | -2.05%            | 8.50%         | -2.08%       | 8.53%    | 19.83%    | 34.87%          | 34.76%     |
| 2012     | 600   | 0.46%       | 1.31%             | -0.85%        | 1.07%        | -0.61%   | 11.83%    | 16.17%          | 16.23%     |
| 2013     | 600   | 0.46%       | 1.56%             | -1.10%        | 1.57%        | -1.11%   | 9.83%     | 14.33%          | 13.63%     |
| 2014     | 600   | 7.36%       | -1.97%            | 9.33%         | -1.68%       | 9.04%    | 15.83%    | 35.73%          | 34.94%     |
| 2015     | 600   | 5.33%       | -2.83%            | 8.16%         | -2.81%       | 8.14%    | 27.67%    | 46.85%          | 46.47%     |
| 2016     | 600   | -6.35%      | -1.32%            | -5.02%        | -1.53%       | -4.82%   | 24.67%    | 22.96%          | 22.34%     |
| 2017     | 600   | 2.27%       | -2.30%            | 4.57%         | -1.82%       | 4.10%    | 19.50%    | 30.97%          | 30.40%     |
| 2018     | 600   | 9.09%       | 0.67%             | 8.42%         | 0.83%        | 8.26%    | 22.67%    | 37.35%          | 37.03%     |
| 2019     | 600   | 0.91%       | -2.11%            | 3.02%         | -1.90%       | 2.80%    | 29.33%    | 39.44%          | 39.08%     |
| 2020     | 600   | -9.69%      | 3.03%             | -12.71%       | 1.94%        | -11.62%  | 17.50%    | 14.13%          | 14.21%     |
| 2021     | 600   | -3.39%      | -3.99%            | 0.61%         | -4.11%       | 0.73%    | 54.83%    | 54.54%          | 53.84%     |
| 2022     | 600   | -2.21%      | -3.00%            | 0.79%         | -2.19%       | -0.02%   | 45.83%    | 49.51%          | 48.58%     |
| 2023     | 600   | -6.62%      | -9.54%            | 2.92%         | -8.57%       | 1.95%    | 22.83%    | 28.41%          | 26.85%     |
| 2024     | 600   | -2.75%      | -5.12%            | 2.38%         | -4.47%       | 1.72%    | 24.33%    | 38.98%          | 37.75%     |
| 2025     | 400   | -17.44%     | -1.27%            | -16.17%       | -0.36%       | -17.09%  | 47.50%    | 36.13%          | 35.06%     |
| all buys | 12400 | 0.53%       | -0.14%            | 0.66%         | -0.07%       | 0.60%    | 27.90%    | 35.36%          | 34.36%     |

## Coverage & diagnostics

- rebalance months: 260; months with **no** qualifying picks (cash held): 0; months with fewer than top_k=50 picks: 0
- mean stocks in the point-in-time cross-section: 4063.3 (min 3639)
- mean after the per-model min_score floor: 4063.3 (min 3639)
- mean after the column filters: 4063.3 (min 3639)
- mean after the investability filter: 400.8 (min 363)
- mean with a tradable quote: 396.2 (min 360)
- forced delisting liquidations: 110 (final-print convention, sell cost applied)

## Assumptions (all of them)

- Execution at the trade date's total-return adjusted close (dividends implicitly reinvested), fractional shares, no market impact beyond the flat per-side cost.
- Candidates need a print within 3 day(s) of the trade date; positions silent for 30+ days are liquidated at their final print (the upstream delisting convention).
- Signals use each stock's latest completed-quarter median-kind snapshot, at most 200 days old — up to a quarter-plus staler than a live inference run, and ranked within the snapshot's own quarter rather than the trade date's cross-section.
- Trade years inside a bundle's walk-forward folds use that year's fold model (trained purged/embargoed on years before it). Years past the last fold are served by **simulated year-end deployment refits**: the same config refit on every row whose label window was fully observable by Jan 1 of the trade year (+45d settlement lag) — data/manual.md §4 rule 7 applied point-in-time; no split tags are read and no test set exists (see the refit appendix).
- Those later trade years — and all valuation past the last fold — overlap the sealed holdout era. That is what a live simulation requires, but it makes this segment selection-toxic: results there are context; feeding them back into model or strategy selection erodes the holdout.

## Provenance

- backtest configurations tried against dataset `1.4.1`: 42 (this one included; every run is logged, failures too)
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

- equity_curve: `reports/backtest/bt_lc90_blend_mcap_top50_v141_37db1919b8fe6caf_equity.csv`
- trades: `reports/backtest/bt_lc90_blend_mcap_top50_v141_37db1919b8fe6caf_trades.csv`
- rebalances: `reports/backtest/bt_lc90_blend_mcap_top50_v141_37db1919b8fe6caf_rebalances.csv`
- equity_plot: `reports/backtest/bt_lc90_blend_mcap_top50_v141_37db1919b8fe6caf_equity.png`
