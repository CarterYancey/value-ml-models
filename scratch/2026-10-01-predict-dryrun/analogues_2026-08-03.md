# Historical analogues — crosssection_2026-08-03

For each pick, the labeled historical rows most similar to it as the models see it, and what they went on to do. **This is an explanation, not an evaluation**: the deployment models were fitted on these very rows, so the analogues' outcome rates are in-sample by construction. They say what kind of history a pick resembles; they are not an accuracy or a probability for it.

- models: `forest_nonloser_dd30_3y` (random_forest); `factor_mom_12_2_3y` (rank_factor, `mom_12_2_rank`); `factor_roc_greenblatt_3y` (rank_factor, `roc_greenblatt_rank`)
- similarity: for a tree model the share of trees in which the row shares the pick's leaf; for a rank factor one minus the distance on its column; the mean of the models' similarities orders the list
- pool: dataset `1.4`, median-kind rows with a 3-year outcome: 462,851 rows of 12,679 stocks; one row per stock is listed, the pick's own history left out
- outcomes are over 3 years from the snapshot (the dataset's label convention: a delisted stock's final price is carried flat to the horizon)

## Summary

What each pick's analogues went on to do over 3 years, beside the whole pool.

| pick | analogues | mean similarity | lost money | median CAGR | mean CAGR | mean excess CAGR | beat the benchmark | fell 30% from entry | delisted | `forest_nonloser_dd30_3y` label true |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| JCI | 15 | 0.93 | 0.0% | 16.0% | 16.9% | 7.2% | 66.7% | 26.7% | 6.7% | 73.3% |
| GOOGL | 15 | 0.93 | 46.7% | 4.2% | 8.3% | -4.3% | 46.7% | 40.0% | 6.7% | 46.7% |
| JNJ | 15 | 0.95 | 13.3% | 16.1% | 15.0% | 4.2% | 73.3% | 20.0% | 0.0% | 80.0% |
| EA | 15 | 0.96 | 20.0% | 15.5% | 14.5% | 2.2% | 60.0% | 20.0% | 6.7% | 73.3% |
| CW | 15 | 0.94 | 13.3% | 19.9% | 17.8% | 2.0% | 60.0% | 6.7% | 6.7% | 80.0% |
| RPRX | 15 | 0.95 | 20.0% | 12.2% | 11.1% | 2.1% | 73.3% | 40.0% | 0.0% | 60.0% |
| AAPL | 15 | 0.95 | 13.3% | 11.3% | 9.1% | -2.8% | 53.3% | 40.0% | 6.7% | 60.0% |
| ESE | 15 | 0.92 | 33.3% | 13.0% | 9.2% | -0.8% | 46.7% | 46.7% | 6.7% | 53.3% |
| CAT | 15 | 0.94 | 26.7% | 10.9% | 7.2% | -4.7% | 46.7% | 46.7% | 20.0% | 46.7% |
| FTI | 15 | 0.92 | 26.7% | 4.6% | 5.4% | -8.2% | 20.0% | 33.3% | 6.7% | 60.0% |
| *whole pool* | 462851 | — | 46.3% | 1.3% | -1.5% | -8.8% | 39.1% | 59.6% | 21.9% | 37.1% |

## JCI

sector Basic Materials; pick 1; mean rank 271.3 of 3,057; forest_nonloser_dd30_3y: rank 220; factor_mom_12_2_3y: rank 542; factor_roc_greenblatt_3y: rank 52.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | JCI |
| --- | --- | --- |
| vol_12m_rank | 54.5% | 0.127 |
| vol_36m_rank | 49.6% | 0.137 |
| conservative_score_rank | 30.0% | 1.000 |
| price_vs_5y_avg_rank | 18.6% | 0.902 |
| max_ret_21d_rank | 17.8% | 0.306 |
| dist_5y_high_rank | 15.1% | 0.975 |

Analogues by era: 2000-04: 1, 2005-09: 4, 2010-14: 3, 2015-19: 4, 2020-24: 3.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ROST | 2015-02-17 | 0.94 | 0.87 | 0.99 | 0.95 | Consumer Cyclical | 12.9% | 19.8% | 8.2% | 6.8% | false | yes | 0.132 | 0.134 | 0.943 | 0.863 | 0.246 | 0.998 |
| 2 | ACN | 2007-06-13 | 0.94 | 0.82 | 0.99 | 0.99 | Technology | -0.2% | 0.5% | 8.8% | 30.7% | false | no | 0.122 | 0.122 | 0.982 | 0.708 | 0.465 | 0.818 |
| 3 | EFX | 2013-01-16 | 0.93 | 0.81 | 0.99 | 1.00 | Industrials | 22.6% | 25.9% | 13.0% | 5.8% | false | yes | 0.104 | 0.071 | 0.971 | 0.846 | 0.395 | 0.972 |
| 4 | CLB | 2011-11-14 | 0.93 | 0.83 | 0.98 | 0.98 | Energy | -5.9% | 8.7% | -10.4% | 10.5% | false | yes | 0.154 | 0.135 | 0.919 | 0.944 | 0.289 | 0.937 |
| 5 | GGG | 2002-04-23 | 0.93 | 0.82 | 0.98 | 0.99 | Industrials | 2.5% | 29.8% | 26.2% | 19.9% | false | yes | 0.105 | 0.076 | 0.904 | 0.924 | 0.296 | 0.936 |
| 6 | SHW | 2008-11-10 | 0.93 | 0.85 | 0.94 | 0.99 | Basic Materials | 9.9% | 16.8% | 4.1% | 21.3% | false | yes | 0.113 | 0.123 | 0.950 | 0.927 | 0.542 | 0.962 |
| 7 | CHH | 2018-01-24 | 0.93 | 0.82 | 0.97 | 1.00 | Consumer Cyclical | -8.3% | 10.5% | -1.5% | 32.0% | false | no | 0.124 | 0.105 | 0.920 | 0.844 | 0.469 | 0.963 |
| 8 | AAPL | 2020-11-05 | 0.93 | 0.85 | 0.94 | 0.99 | Technology | 24.9% | 14.4% | 6.0% | 4.2% | false | yes | 0.126 | 0.127 | 0.998 | 0.960 | 0.425 | 0.804 |
| 9 | DPZ | 2017-05-19 | 0.93 | 0.81 | 0.99 | 0.99 | Consumer Cyclical | 26.5% | 24.7% | 16.3% | 13.4% | false | yes | 0.117 | 0.160 | 0.979 | 0.970 | 0.262 | 0.983 |
| 10 | APAGF | 2006-02-07 | 0.93 | 0.82 | 1.00 | 0.97 | Energy | 35.1% | 16.0% | 26.4% | 3.0% | false | yes | 0.117 | 0.112 | 0.939 | 0.908 | 0.373 | 0.974 |
| 11 | WDFC | 2009-01-14 | 0.93 | 0.82 | 0.99 | 0.98 | Basic Materials | 31.5% | 20.8% | 4.1% | 12.4% | false | yes | 0.120 | 0.126 | 0.941 | 0.808 | 0.161 | 0.887 |
| 12 | MAR | 2020-01-28 | 0.93 | 0.82 | 0.99 | 0.97 | Consumer Cyclical | -10.3% | 4.4% | -3.6% | 58.0% | false | no | 0.140 | 0.134 | 0.988 | 0.791 | 0.238 | 0.853 |
| 13 | LNCR | 2010-06-07 | 0.93 | 0.81 | 1.00 | 0.97 | Healthcare | -1.2% | 12.2% | -6.3% | 33.4% | acquisitionby | no | 0.106 | 0.032 | 1.000 | 0.871 | 0.316 | 0.972 |
| 14 | ITW | 2023-07-06 | 0.93 | 0.82 | 0.97 | 0.99 | Industrials | 0.2% | 5.0% | -15.5% | 7.7% | false | yes | 0.128 | 0.041 | 0.974 | 0.796 | 0.338 | 0.968 |
| 15 | MSCI | 2017-11-07 | 0.93 | 0.81 | 0.98 | 0.99 | Financial Services | 20.8% | 43.9% | 32.0% | 1.4% | false | yes | 0.151 | 0.093 | 0.998 | 0.953 | 0.694 | 0.943 |

## GOOGL

sector Communication Services; pick 2; mean rank 303.7 of 3,057; forest_nonloser_dd30_3y: rank 302; factor_mom_12_2_3y: rank 325; factor_roc_greenblatt_3y: rank 284.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | GOOGL |
| --- | --- | --- |
| vol_12m_rank | 54.9% | 0.162 |
| vol_36m_rank | 51.0% | 0.161 |
| conservative_score_rank | 30.0% | 0.955 |
| price_vs_5y_avg_rank | 19.0% | 0.928 |
| max_ret_21d_rank | 18.4% | 0.242 |
| dist_5y_high_rank | 15.7% | 0.851 |

Analogues by era: 2000-04: 3, 2005-09: 3, 2015-19: 3, 2020-24: 6.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | CRL | 2020-11-09 | 0.95 | 0.88 | 0.99 | 0.98 | Healthcare | 73.6% | -8.8% | -16.8% | 30.7% | false | no | 0.173 | 0.162 | 0.867 | 0.922 | 0.291 | 0.899 |
| 2 | WOOF1 | 2015-04-29 | 0.94 | 0.89 | 0.96 | 0.99 | Basic Materials | 13.9% | 20.8% | 10.7% | 14.4% | acquisitionby | yes | 0.164 | 0.175 | 0.995 | 0.912 | 0.266 | 0.854 |
| 3 | GNRC | 2020-11-24 | 0.94 | 0.86 | 0.98 | 0.99 | Industrials | 112.0% | -21.7% | -29.7% | 61.6% | false | no | 0.195 | 0.175 | 0.892 | 0.984 | 0.252 | 0.854 |
| 4 | FAST | 2009-01-12 | 0.94 | 0.87 | 0.98 | 0.98 | Industrials | 32.0% | 41.7% | 26.3% | 19.0% | false | yes | 0.175 | 0.167 | 0.903 | 0.847 | 0.252 | 0.873 |
| 5 | EXLS | 2022-02-09 | 0.94 | 0.90 | 0.99 | 0.92 | Technology | 36.8% | 25.1% | 14.1% | 9.3% | false | yes | 0.167 | 0.164 | 0.962 | 0.894 | 0.216 | 0.806 |
| 6 | CTXS | 2009-07-31 | 0.93 | 0.81 | 0.99 | 1.00 | Technology | 30.8% | 29.8% | 16.4% | 4.4% | false | yes | 0.176 | 0.156 | 0.938 | 0.888 | 0.339 | 0.905 |
| 7 | DRI | 2002-04-04 | 0.93 | 0.88 | 0.98 | 0.93 | Consumer Cyclical | -26.9% | 4.2% | 0.6% | 34.0% | false | no | 0.169 | 0.156 | 0.976 | 0.919 | 0.232 | 0.819 |
| 8 | STRT | 2003-02-14 | 0.93 | 0.80 | 0.99 | 1.00 | Consumer Cyclical | 34.2% | -4.0% | -20.7% | 17.0% | false | no | 0.163 | 0.079 | 0.999 | 0.862 | 0.269 | 0.858 |
| 9 | AWI | 2019-09-16 | 0.93 | 0.81 | 0.99 | 0.99 | Basic Materials | -24.1% | -2.4% | -14.6% | 37.7% | false | no | 0.153 | 0.173 | 0.984 | 0.937 | 0.294 | 0.907 |
| 10 | MATW | 2008-12-09 | 0.93 | 0.84 | 0.96 | 0.99 | Industrials | -12.1% | -6.1% | -19.8% | 31.7% | false | no | 0.166 | 0.183 | 0.869 | 0.886 | 0.190 | 0.943 |
| 11 | HEI | 2022-09-15 | 0.93 | 0.82 | 0.98 | 0.98 | Industrials | 9.2% | 27.6% | 7.6% | 8.1% | false | yes | 0.181 | 0.167 | 0.852 | 0.826 | 0.271 | 0.942 |
| 12 | EHC | 2018-11-15 | 0.93 | 0.82 | 0.99 | 0.97 | Healthcare | -4.3% | -1.7% | -22.8% | 29.2% | false | no | 0.132 | 0.160 | 0.942 | 0.920 | 0.260 | 0.847 |
| 13 | EL | 2020-01-30 | 0.93 | 0.80 | 0.99 | 0.99 | Consumer Defensive | 28.2% | 10.9% | 2.9% | 27.1% | false | yes | 0.214 | 0.164 | 0.958 | 0.903 | 0.183 | 0.817 |
| 14 | RMD | 2020-04-16 | 0.93 | 0.85 | 0.96 | 0.97 | Healthcare | 22.1% | 11.2% | -3.5% | 4.5% | false | yes | 0.164 | 0.165 | 0.915 | 0.949 | 0.502 | 0.951 |
| 15 | PNR | 2004-11-04 | 0.93 | 0.79 | 0.99 | 0.99 | Industrials | -11.7% | -2.5% | -14.2% | 30.6% | false | no | 0.163 | 0.152 | 0.941 | 0.881 | 0.607 | 0.993 |

## JNJ

sector Healthcare; pick 3; mean rank 315.3 of 3,057; forest_nonloser_dd30_3y: rank 29; factor_mom_12_2_3y: rank 804; factor_roc_greenblatt_3y: rank 113.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | JNJ |
| --- | --- | --- |
| vol_12m_rank | 55.5% | 0.034 |
| vol_36m_rank | 50.0% | 0.005 |
| conservative_score_rank | 29.6% | 0.988 |
| price_vs_5y_avg_rank | 19.4% | 0.792 |
| max_ret_21d_rank | 17.1% | 0.151 |
| dist_52w_high_rank | 14.3% | 0.808 |

Analogues by era: 2000-04: 1, 2005-09: 5, 2015-19: 8, 2020-24: 1.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_52w_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PEP | 2019-12-18 | 0.96 | 0.90 | 1.00 | 0.99 | Consumer Defensive | 9.3% | 13.5% | 4.2% | 23.0% | false | yes | 0.017 | 0.007 | 0.975 | 0.722 | 0.061 | 0.906 |
| 2 | IEX | 2016-12-16 | 0.96 | 0.92 | 1.00 | 0.97 | Industrials | 46.1% | 22.8% | 9.1% | 1.8% | false | yes | 0.029 | 0.032 | 0.941 | 0.779 | 0.110 | 0.822 |
| 3 | RTN | 2008-02-06 | 0.96 | 0.89 | 0.99 | 0.99 | Industrials | -20.4% | -5.3% | -6.5% | 46.8% | false | no | 0.025 | 0.015 | 0.985 | 0.884 | 0.174 | 0.978 |
| 4 | ACN | 2020-05-08 | 0.96 | 0.89 | 1.00 | 0.99 | Technology | 55.5% | 15.2% | 1.4% | 4.5% | false | yes | 0.053 | 0.027 | 0.947 | 0.847 | 0.120 | 0.862 |
| 5 | GNI | 2003-08-14 | 0.96 | 0.92 | 0.98 | 0.97 | Basic Materials | 32.2% | 21.5% | 11.1% | 1.4% | false | yes | 0.033 | 0.022 | 1.000 | 0.863 | 0.099 | 0.965 |
| 6 | ITW | 2015-02-05 | 0.96 | 0.89 | 0.98 | 0.99 | Industrials | -10.2% | 23.4% | 10.6% | 16.6% | false | yes | 0.020 | 0.042 | 0.991 | 0.785 | 0.151 | 1.000 |
| 7 | BMY | 2009-08-13 | 0.96 | 0.87 | 1.00 | 0.99 | Healthcare | 23.0% | 21.7% | 8.7% | 0.9% | false | yes | 0.029 | 0.028 | 0.983 | 0.773 | 0.079 | 0.913 |
| 8 | COL | 2007-10-30 | 0.95 | 0.86 | 1.00 | 1.00 | Industrials | -48.7% | -4.9% | 1.5% | 61.3% | false | no | 0.029 | 0.042 | 0.988 | 0.835 | 0.060 | 0.953 |
| 9 | MMM | 2008-12-04 | 0.95 | 0.90 | 0.97 | 0.98 | Industrials | 35.0% | 13.4% | -2.1% | 28.5% | false | yes | 0.036 | 0.024 | 0.946 | 0.734 | 0.174 | 0.874 |
| 10 | HON | 2019-06-05 | 0.95 | 0.89 | 0.97 | 0.99 | Industrials | -15.6% | 6.6% | -7.7% | 37.7% | false | no | 0.042 | 0.013 | 0.983 | 0.839 | 0.044 | 0.935 |
| 11 | GD | 2016-06-02 | 0.95 | 0.90 | 0.97 | 0.99 | Industrials | 43.8% | 8.4% | -4.4% | 5.0% | false | yes | 0.034 | 0.033 | 0.983 | 0.834 | 0.100 | 0.793 |
| 12 | HD | 2017-11-16 | 0.95 | 0.90 | 0.99 | 0.96 | Consumer Cyclical | 9.5% | 21.3% | 9.1% | 3.5% | false | yes | 0.020 | 0.031 | 0.997 | 0.838 | 0.098 | 0.977 |
| 13 | MKC | 2015-12-14 | 0.95 | 0.89 | 1.00 | 0.97 | Consumer Defensive | 10.3% | 23.2% | 11.2% | 5.2% | false | yes | 0.018 | 0.015 | 0.958 | 0.747 | 0.118 | 0.937 |
| 14 | TTC | 2015-11-04 | 0.95 | 0.87 | 0.99 | 0.99 | Industrials | 27.3% | 16.1% | 4.5% | 12.2% | false | yes | 0.022 | 0.055 | 0.959 | 0.867 | 0.119 | 0.979 |
| 15 | BF.B | 2009-05-28 | 0.95 | 0.88 | 0.98 | 0.98 | Consumer Defensive | 29.6% | 27.9% | 11.4% | 6.2% | false | yes | 0.028 | 0.022 | 0.936 | 0.793 | 0.103 | 0.784 |

## EA

sector Communication Services; pick 4; mean rank 333.0 of 3,057; forest_nonloser_dd30_3y: rank 52; factor_mom_12_2_3y: rank 924; factor_roc_greenblatt_3y: rank 23.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | EA |
| --- | --- | --- |
| vol_12m_rank | 56.1% | 0.076 |
| vol_36m_rank | 50.2% | 0.070 |
| conservative_score_rank | 29.4% | 0.985 |
| price_vs_5y_avg_rank | 19.6% | 0.782 |
| max_ret_21d_rank | 17.1% | 0.058 |
| dist_5y_high_rank | 14.7% | 0.991 |

Analogues by era: 2005-09: 5, 2010-14: 2, 2015-19: 4, 2020-24: 4.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | V | 2023-08-11 | 0.96 | 0.91 | 0.98 | 1.00 | Financial Services | 10.2% | 15.5% | -5.1% | 4.7% | false | yes | 0.087 | 0.079 | 0.916 | 0.730 | 0.057 | 0.975 |
| 2 | NLSN | 2016-08-17 | 0.96 | 0.91 | 1.00 | 0.98 | Industrials | -20.0% | -21.8% | -34.4% | 56.8% | false | no | 0.072 | 0.086 | 0.931 | 0.756 | 0.047 | 0.857 |
| 3 | INTU | 2009-01-15 | 0.96 | 0.89 | 1.00 | 0.99 | Technology | 29.6% | 30.7% | 14.1% | 10.7% | false | yes | 0.060 | 0.076 | 0.901 | 0.848 | 0.086 | 0.916 |
| 4 | IDXX | 2012-03-02 | 0.96 | 0.89 | 1.00 | 0.98 | Healthcare | 8.9% | 22.6% | 5.4% | 3.8% | false | yes | 0.090 | 0.075 | 0.945 | 0.821 | 0.032 | 0.900 |
| 5 | JKHY | 2009-08-18 | 0.96 | 0.90 | 0.99 | 0.98 | Technology | 16.0% | 18.6% | 4.5% | 2.8% | false | yes | 0.077 | 0.070 | 0.970 | 0.809 | 0.102 | 0.899 |
| 6 | FDS | 2011-04-04 | 0.96 | 0.88 | 1.00 | 0.98 | Financial Services | -7.0% | 1.6% | -12.6% | 25.7% | false | yes | 0.083 | 0.091 | 0.961 | 0.908 | 0.125 | 0.977 |
| 7 | LH | 2007-06-28 | 0.96 | 0.90 | 0.99 | 0.98 | Healthcare | -7.3% | -0.3% | 8.0% | 31.7% | false | no | 0.103 | 0.042 | 0.984 | 0.747 | 0.048 | 0.910 |
| 8 | CHH | 2019-09-24 | 0.95 | 0.88 | 0.99 | 0.99 | Consumer Cyclical | 8.9% | 9.1% | -2.6% | 39.4% | false | no | 0.074 | 0.067 | 0.898 | 0.796 | 0.074 | 0.871 |
| 9 | ACN | 2016-08-15 | 0.95 | 0.89 | 0.98 | 0.99 | Technology | 15.8% | 21.5% | 9.0% | 3.3% | false | yes | 0.089 | 0.062 | 0.901 | 0.808 | 0.120 | 0.855 |
| 10 | SNPS | 2016-10-11 | 0.95 | 0.90 | 0.97 | 0.99 | Technology | 35.7% | 31.9% | 18.3% | 4.6% | false | yes | 0.073 | 0.057 | 0.953 | 0.830 | 0.113 | 0.964 |
| 11 | MTD | 2020-05-07 | 0.95 | 0.90 | 0.99 | 0.97 | Healthcare | 75.5% | 27.6% | 13.3% | 5.9% | false | yes | 0.073 | 0.061 | 0.945 | 0.839 | 0.141 | 0.892 |
| 12 | TYL | 2009-12-21 | 0.95 | 0.88 | 1.00 | 0.98 | Technology | 10.9% | 35.4% | 24.8% | 20.7% | false | yes | 0.037 | 0.075 | 0.998 | 0.954 | 0.063 | 0.953 |
| 13 | INFO1 | 2020-09-16 | 0.95 | 0.88 | 0.98 | 0.99 | Industrials | 52.5% | 11.3% | 0.2% | 3.8% | acquisitionby | yes | 0.093 | 0.044 | 0.980 | 0.868 | 0.132 | 0.943 |
| 14 | MKC | 2020-02-21 | 0.95 | 0.91 | 0.96 | 0.99 | Consumer Defensive | 12.6% | -0.9% | -9.6% | 29.8% | false | no | 0.076 | 0.079 | 0.887 | 0.835 | 0.058 | 0.884 |
| 15 | FISV | 2009-07-22 | 0.95 | 0.87 | 1.00 | 0.99 | Technology | -3.7% | 13.9% | -0.6% | 6.3% | false | yes | 0.072 | 0.053 | 0.965 | 0.804 | 0.074 | 0.918 |

## CW

sector Industrials; pick 5; mean rank 333.7 of 3,057; forest_nonloser_dd30_3y: rank 304; factor_mom_12_2_3y: rank 447; factor_roc_greenblatt_3y: rank 250.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | CW |
| --- | --- | --- |
| vol_12m_rank | 55.1% | 0.212 |
| vol_36m_rank | 51.4% | 0.146 |
| conservative_score_rank | 30.0% | 0.961 |
| max_ret_21d_rank | 19.2% | 0.215 |
| price_vs_5y_avg_rank | 19.0% | 0.958 |
| dist_5y_high_rank | 15.7% | 0.981 |

Analogues by era: 2000-04: 2, 2010-14: 2, 2015-19: 4, 2020-24: 7.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | max_ret_21d_rank | price_vs_5y_avg_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | EL | 2020-01-30 | 0.95 | 0.90 | 0.97 | 0.98 | Consumer Defensive | 28.2% | 10.9% | 2.9% | 27.1% | false | yes | 0.214 | 0.164 | 0.958 | 0.183 | 0.903 | 0.817 |
| 2 | HEI | 2018-12-12 | 0.94 | 0.85 | 1.00 | 0.98 | Industrials | 53.9% | 19.9% | -2.7% | 25.8% | false | yes | 0.222 | 0.140 | 0.896 | 0.381 | 0.965 | 0.860 |
| 3 | FELE | 2003-06-23 | 0.94 | 0.86 | 0.97 | 0.99 | Industrials | 23.8% | 25.3% | 15.0% | 2.8% | false | yes | 0.219 | 0.128 | 0.960 | 0.269 | 0.859 | 0.909 |
| 4 | PZZA | 2012-10-04 | 0.94 | 0.87 | 0.95 | 1.00 | Consumer Cyclical | 34.2% | 39.1% | 26.9% | 10.5% | false | yes | 0.245 | 0.139 | 0.994 | 0.216 | 0.931 | 0.961 |
| 5 | DRI | 2019-06-20 | 0.94 | 0.84 | 0.99 | 0.99 | Consumer Cyclical | -32.4% | 2.7% | -9.4% | 70.6% | false | no | 0.183 | 0.147 | 0.954 | 0.182 | 0.895 | 0.886 |
| 6 | CSW | 2023-05-19 | 0.94 | 0.85 | 0.98 | 0.98 | Industrials | 75.0% | 26.6% | 5.0% | 3.8% | false | yes | 0.206 | 0.143 | 0.953 | 0.145 | 0.887 | 0.948 |
| 7 | ROST | 2016-02-03 | 0.94 | 0.85 | 0.99 | 0.97 | Consumer Cyclical | 20.9% | 19.2% | 6.1% | 4.7% | false | yes | 0.215 | 0.165 | 0.944 | 0.312 | 0.929 | 0.969 |
| 8 | HAS | 2016-02-23 | 0.94 | 0.87 | 0.98 | 0.96 | Consumer Cyclical | 26.3% | 8.9% | -5.6% | 0.0% | false | yes | 0.217 | 0.158 | 0.954 | 0.197 | 0.916 | 0.904 |
| 9 | COO | 2003-01-08 | 0.94 | 0.83 | 0.99 | 0.98 | Healthcare | 75.2% | 23.8% | 10.4% | 10.7% | false | yes | 0.210 | 0.152 | 0.942 | 0.284 | 0.907 | 0.924 |
| 10 | WTS | 2023-03-16 | 0.93 | 0.85 | 0.99 | 0.97 | Industrials | 23.9% | 25.8% | 4.4% | 5.4% | false | yes | 0.213 | 0.096 | 0.933 | 0.189 | 0.859 | 0.742 |
| 11 | PH | 2023-08-17 | 0.93 | 0.86 | 0.98 | 0.96 | Industrials | 39.7% | 37.7% | 16.1% | 7.9% | false | yes | 0.196 | 0.145 | 0.908 | 0.313 | 0.919 | 0.926 |
| 12 | MTD | 2023-05-16 | 0.93 | 0.87 | 0.99 | 0.94 | Healthcare | -5.2% | -3.7% | -26.1% | 29.9% | false | no | 0.240 | 0.122 | 0.960 | 0.191 | 0.804 | 0.788 |
| 13 | COV | 2014-08-22 | 0.93 | 0.83 | 0.99 | 0.98 | Healthcare | 21.8% | 6.8% | -2.7% | 6.5% | acquisitionby | yes | 0.269 | 0.105 | 0.982 | 0.214 | 0.860 | 0.885 |
| 14 | ORLY | 2022-09-20 | 0.93 | 0.83 | 0.96 | 0.99 | Consumer Cyclical | 34.0% | 30.8% | 10.1% | 1.8% | false | yes | 0.213 | 0.061 | 0.996 | 0.193 | 0.912 | 0.967 |
| 15 | EVTC | 2022-01-25 | 0.93 | 0.81 | 1.00 | 0.98 | Technology | -19.5% | -7.0% | -19.6% | 29.0% | false | no | 0.226 | 0.148 | 0.891 | 0.121 | 0.774 | 0.756 |

## RPRX

sector Healthcare; pick 6; mean rank 338.3 of 3,057; forest_nonloser_dd30_3y: rank 86; factor_mom_12_2_3y: rank 847; factor_roc_greenblatt_3y: rank 82.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | RPRX |
| --- | --- | --- |
| vol_12m_rank | 55.9% | 0.075 |
| vol_36m_rank | 49.8% | 0.064 |
| conservative_score_rank | 29.2% | 0.974 |
| price_vs_5y_avg_rank | 19.8% | 0.828 |
| max_ret_21d_rank | 17.1% | 0.172 |
| dist_5y_high_rank | 14.5% | 0.984 |

Analogues by era: 2005-09: 6, 2010-14: 2, 2015-19: 2, 2020-24: 5.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TT | 2021-05-20 | 0.96 | 0.94 | 0.99 | 0.96 | Basic Materials | -22.4% | 22.6% | 13.6% | 31.7% | false | no | 0.087 | 0.061 | 0.993 | 0.903 | 0.170 | 0.909 |
| 2 | TWX | 2013-07-24 | 0.96 | 0.91 | 0.98 | 1.00 | Communication Services | 29.8% | 10.3% | 0.3% | 2.4% | false | yes | 0.082 | 0.084 | 0.993 | 0.856 | 0.166 | 0.974 |
| 3 | PAYX | 2019-10-15 | 0.96 | 0.90 | 0.99 | 0.98 | Industrials | -2.6% | 13.5% | 4.4% | 39.7% | false | no | 0.062 | 0.035 | 0.954 | 0.829 | 0.167 | 0.939 |
| 4 | ITW | 2020-10-15 | 0.96 | 0.89 | 0.99 | 0.99 | Industrials | 7.3% | 7.0% | -2.1% | 10.2% | false | yes | 0.079 | 0.059 | 0.994 | 0.806 | 0.115 | 0.985 |
| 5 | BR | 2014-05-12 | 0.96 | 0.91 | 0.98 | 0.98 | Technology | 40.5% | 23.8% | 13.8% | 1.2% | false | yes | 0.061 | 0.051 | 0.993 | 0.797 | 0.174 | 0.931 |
| 6 | JKHY | 2009-08-18 | 0.96 | 0.89 | 0.99 | 1.00 | Technology | 16.0% | 18.6% | 4.5% | 2.8% | false | yes | 0.077 | 0.070 | 0.970 | 0.809 | 0.102 | 0.899 |
| 7 | SHW | 2020-08-20 | 0.96 | 0.89 | 0.98 | 1.00 | Basic Materials | 34.2% | 8.1% | -3.5% | 8.1% | false | yes | 0.088 | 0.060 | 0.952 | 0.898 | 0.131 | 0.995 |
| 8 | CSCO | 2023-08-10 | 0.96 | 0.89 | 1.00 | 0.98 | Technology | -9.2% | 32.9% | 12.4% | 13.5% | false | yes | 0.100 | 0.066 | 0.961 | 0.681 | 0.214 | 0.846 |
| 9 | HPQ | 2009-09-01 | 0.95 | 0.87 | 0.99 | 1.00 | Technology | -6.8% | -23.9% | -38.3% | 60.3% | false | no | 0.084 | 0.061 | 0.967 | 0.903 | 0.108 | 0.932 |
| 10 | PM | 2022-01-12 | 0.95 | 0.87 | 0.99 | 0.99 | Consumer Defensive | 5.2% | 12.2% | 2.6% | 14.8% | false | yes | 0.087 | 0.028 | 0.976 | 0.654 | 0.148 | 0.982 |
| 11 | ACN | 2008-12-17 | 0.95 | 0.88 | 0.98 | 0.99 | Technology | 39.7% | 25.6% | 12.7% | 11.8% | false | yes | 0.094 | 0.081 | 0.938 | 0.867 | 0.094 | 0.930 |
| 12 | MKC | 2019-03-06 | 0.95 | 0.89 | 0.99 | 0.97 | Consumer Defensive | 18.1% | 15.0% | -3.6% | 15.4% | false | yes | 0.099 | 0.054 | 0.887 | 0.859 | 0.180 | 0.815 |
| 13 | GD | 2006-12-12 | 0.95 | 0.87 | 0.99 | 0.99 | Industrials | 23.3% | -1.1% | 4.9% | 48.9% | false | no | 0.067 | 0.025 | 0.911 | 0.696 | 0.221 | 0.866 |
| 14 | BF.B | 2008-06-04 | 0.95 | 0.86 | 0.99 | 1.00 | Consumer Defensive | -18.6% | 10.3% | 9.2% | 34.7% | false | no | 0.074 | 0.044 | 0.963 | 0.739 | 0.071 | 0.944 |
| 15 | HON | 2007-09-18 | 0.95 | 0.86 | 0.99 | 0.99 | Industrials | -14.6% | -7.7% | 0.9% | 57.8% | false | no | 0.049 | 0.056 | 0.998 | 0.783 | 0.115 | 0.895 |

## AAPL

sector Technology; pick 7; mean rank 338.7 of 3,057; forest_nonloser_dd30_3y: rank 90; factor_mom_12_2_3y: rank 884; factor_roc_greenblatt_3y: rank 42.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | AAPL |
| --- | --- | --- |
| vol_12m_rank | 55.9% | 0.083 |
| vol_36m_rank | 50.2% | 0.102 |
| conservative_score_rank | 29.6% | 0.931 |
| price_vs_5y_avg_rank | 19.8% | 0.814 |
| max_ret_21d_rank | 17.3% | 0.162 |
| dist_5y_high_rank | 14.3% | 0.892 |

Analogues by era: 2000-04: 1, 2005-09: 4, 2010-14: 3, 2015-19: 3, 2020-24: 4.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | price_vs_5y_avg_rank | max_ret_21d_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | INTU | 2012-09-20 | 0.96 | 0.92 | 0.97 | 0.99 | Technology | 11.6% | 15.2% | 2.8% | 2.1% | false | yes | 0.080 | 0.101 | 0.961 | 0.831 | 0.148 | 0.902 |
| 2 | MTD | 2020-05-07 | 0.96 | 0.91 | 0.99 | 0.97 | Healthcare | 75.5% | 27.6% | 13.3% | 5.9% | false | yes | 0.073 | 0.061 | 0.945 | 0.839 | 0.141 | 0.892 |
| 3 | V | 2023-08-11 | 0.96 | 0.88 | 0.99 | 0.99 | Financial Services | 10.2% | 15.5% | -5.1% | 4.7% | false | yes | 0.087 | 0.079 | 0.916 | 0.730 | 0.057 | 0.975 |
| 4 | IDXX | 2021-02-08 | 0.95 | 0.88 | 1.00 | 0.98 | Healthcare | 4.3% | 2.7% | -6.5% | 34.5% | false | no | 0.075 | 0.091 | 0.935 | 0.912 | 0.213 | 0.920 |
| 5 | JKHY | 2008-03-11 | 0.95 | 0.90 | 0.98 | 0.98 | Technology | -32.9% | 11.5% | 9.4% | 39.3% | false | no | 0.073 | 0.100 | 0.916 | 0.686 | 0.169 | 0.847 |
| 6 | FDS | 2011-04-04 | 0.95 | 0.87 | 0.99 | 0.99 | Financial Services | -7.0% | 1.6% | -12.6% | 25.7% | false | yes | 0.083 | 0.091 | 0.961 | 0.908 | 0.125 | 0.977 |
| 7 | STRA | 2009-08-13 | 0.95 | 0.86 | 0.99 | 1.00 | Consumer Defensive | 7.5% | -24.8% | -37.7% | 64.9% | false | no | 0.076 | 0.105 | 0.934 | 0.967 | 0.066 | 0.961 |
| 8 | INFO1 | 2020-09-16 | 0.95 | 0.87 | 1.00 | 0.98 | Industrials | 52.5% | 11.3% | 0.2% | 3.8% | acquisitionby | yes | 0.093 | 0.044 | 0.980 | 0.868 | 0.132 | 0.943 |
| 9 | HPQ | 2009-09-01 | 0.95 | 0.89 | 0.98 | 0.98 | Technology | -6.8% | -23.9% | -38.3% | 60.3% | false | no | 0.084 | 0.061 | 0.967 | 0.903 | 0.108 | 0.932 |
| 10 | LDR | 2004-10-22 | 0.95 | 0.86 | 1.00 | 0.98 | Technology | 5.3% | 6.6% | -7.3% | 7.4% | false | yes | 0.074 | 0.038 | 0.985 | 0.753 | 0.119 | 0.904 |
| 11 | AME | 2007-09-05 | 0.95 | 0.87 | 1.00 | 0.98 | Industrials | 19.8% | 3.7% | 11.5% | 37.9% | false | no | 0.074 | 0.097 | 0.890 | 0.821 | 0.145 | 0.913 |
| 12 | ACN | 2016-08-15 | 0.95 | 0.88 | 0.97 | 1.00 | Technology | 15.8% | 21.5% | 9.0% | 3.3% | false | yes | 0.089 | 0.062 | 0.901 | 0.808 | 0.120 | 0.855 |
| 13 | TDG | 2010-06-16 | 0.95 | 0.87 | 1.00 | 0.97 | Industrials | 51.6% | 44.9% | 28.8% | 6.5% | false | yes | 0.089 | 0.117 | 0.998 | 0.952 | 0.185 | 0.955 |
| 14 | PAYX | 2019-10-15 | 0.95 | 0.86 | 0.98 | 1.00 | Industrials | -2.6% | 13.5% | 4.4% | 39.7% | false | no | 0.062 | 0.035 | 0.954 | 0.829 | 0.167 | 0.939 |
| 15 | FISV | 2018-12-12 | 0.95 | 0.87 | 0.99 | 0.98 | Technology | 47.7% | 8.9% | -13.8% | 11.1% | false | yes | 0.074 | 0.019 | 0.989 | 0.873 | 0.194 | 0.946 |

## ESE

sector Technology; pick 8; mean rank 340.7 of 3,057; forest_nonloser_dd30_3y: rank 402; factor_mom_12_2_3y: rank 490; factor_roc_greenblatt_3y: rank 130.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | ESE |
| --- | --- | --- |
| vol_12m_rank | 55.7% | 0.188 |
| vol_36m_rank | 50.0% | 0.165 |
| conservative_score_rank | 29.4% | 0.867 |
| max_ret_21d_rank | 19.6% | 0.456 |
| price_vs_5y_avg_rank | 18.6% | 0.952 |
| dist_52w_high_rank | 16.7% | 1.000 |

Analogues by era: 2000-04: 4, 2005-09: 2, 2010-14: 2, 2015-19: 3, 2020-24: 4.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | max_ret_21d_rank | price_vs_5y_avg_rank | dist_52w_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | GPN | 2006-01-12 | 0.94 | 0.85 | 1.00 | 0.97 | Industrials | -11.1% | -12.9% | -3.1% | 37.8% | false | no | 0.158 | 0.152 | 0.846 | 0.642 | 0.920 | 0.978 |
| 2 | MANH | 2012-05-18 | 0.94 | 0.83 | 1.00 | 0.99 | Technology | 52.7% | 66.6% | 46.7% | 11.0% | false | yes | 0.193 | 0.168 | 0.985 | 0.760 | 0.909 | 0.781 |
| 3 | CACI | 2020-03-04 | 0.93 | 0.83 | 0.98 | 0.97 | Technology | -10.5% | 4.8% | -6.0% | 35.3% | false | no | 0.181 | 0.170 | 0.827 | 0.505 | 0.934 | 0.748 |
| 4 | MSCI | 2020-08-04 | 0.92 | 0.83 | 0.96 | 0.99 | Financial Services | 59.4% | 13.5% | 0.9% | 6.7% | false | yes | 0.202 | 0.155 | 0.971 | 0.386 | 0.966 | 0.845 |
| 5 | WINA | 2010-05-26 | 0.92 | 0.83 | 0.97 | 0.97 | Consumer Cyclical | 29.6% | 29.6% | 12.1% | 4.8% | false | yes | 0.208 | 0.158 | 0.994 | 0.468 | 0.939 | 0.923 |
| 6 | WOOF1 | 2016-05-17 | 0.92 | 0.79 | 0.99 | 0.99 | Basic Materials | 42.5% | 13.0% | -1.4% | 7.4% | acquisitionby | yes | 0.217 | 0.197 | 0.843 | 0.561 | 0.969 | 0.968 |
| 7 | TFX | 2020-01-03 | 0.92 | 0.86 | 0.99 | 0.92 | Healthcare | 5.6% | -12.6% | -20.8% | 49.6% | false | no | 0.184 | 0.169 | 0.826 | 0.299 | 0.919 | 0.969 |
| 8 | PRSU | 2017-08-21 | 0.92 | 0.80 | 0.97 | 1.00 | Industrials | 10.0% | -31.5% | -44.6% | 77.3% | false | no | 0.190 | 0.195 | 0.865 | 0.659 | 0.950 | 0.926 |
| 9 | GTK | 2003-08-25 | 0.92 | 0.77 | 0.99 | 1.00 | Communication Services | 3.0% | 20.5% | 9.7% | 1.9% | false | yes | 0.226 | 0.150 | 0.942 | 0.366 | 0.961 | 0.877 |
| 10 | USPH | 2018-08-03 | 0.92 | 0.76 | 1.00 | 1.00 | Healthcare | 11.5% | 0.5% | -17.0% | 57.5% | false | no | 0.207 | 0.221 | 0.878 | 0.834 | 0.956 | 0.932 |
| 11 | COO | 2003-05-13 | 0.92 | 0.80 | 0.99 | 0.96 | Healthcare | 70.5% | 19.1% | 5.7% | 1.2% | false | yes | 0.240 | 0.156 | 0.788 | 0.461 | 0.932 | 1.000 |
| 12 | PZZA | 2006-07-07 | 0.92 | 0.78 | 0.97 | 1.00 | Consumer Cyclical | -13.9% | -9.9% | -1.6% | 61.3% | false | no | 0.163 | 0.166 | 0.980 | 0.588 | 0.891 | 0.910 |
| 13 | SGA | 2002-04-29 | 0.92 | 0.84 | 0.99 | 0.93 | Communication Services | -13.1% | -11.8% | -16.5% | 36.3% | false | no | 0.171 | 0.169 | 0.860 | 0.379 | 0.871 | 0.988 |
| 14 | YDNT | 2002-04-23 | 0.92 | 0.81 | 0.95 | 0.98 | Healthcare | -5.7% | 17.7% | 14.0% | 23.0% | false | yes | 0.233 | 0.175 | 0.996 | 0.418 | 0.944 | 1.000 |
| 15 | LLY | 2023-08-14 | 0.92 | 0.82 | 0.95 | 0.99 | Healthcare | 57.3% | 30.8% | 10.3% | 2.4% | false | yes | 0.176 | 0.156 | 0.898 | 0.901 | 0.991 | 1.000 |

## CAT

sector Industrials; pick 9; mean rank 353.0 of 3,057; forest_nonloser_dd30_3y: rank 404; factor_mom_12_2_3y: rank 343; factor_roc_greenblatt_3y: rank 312.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | CAT |
| --- | --- | --- |
| vol_12m_rank | 54.9% | 0.219 |
| vol_36m_rank | 50.8% | 0.172 |
| conservative_score_rank | 29.8% | 0.973 |
| max_ret_21d_rank | 19.2% | 0.700 |
| price_vs_5y_avg_rank | 18.2% | 0.966 |
| dist_5y_high_rank | 16.5% | 0.946 |

Analogues by era: 2000-04: 1, 2005-09: 2, 2010-14: 1, 2015-19: 7, 2020-24: 4.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | max_ret_21d_rank | price_vs_5y_avg_rank | dist_5y_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FRK | 2005-08-17 | 0.95 | 0.89 | 1.00 | 0.97 | Basic Materials | -26.7% | 6.4% | 3.1% | 32.6% | acquisitionby | no | 0.202 | 0.158 | 0.977 | 0.411 | 0.951 | 0.914 |
| 2 | TDG | 2023-05-25 | 0.95 | 0.87 | 0.98 | 1.00 | Industrials | 70.8% | 20.7% | -1.6% | 1.7% | false | yes | 0.193 | 0.167 | 0.936 | 0.429 | 0.897 | 0.955 |
| 3 | WOOF1 | 2015-02-13 | 0.94 | 0.90 | 0.95 | 0.99 | Basic Materials | -7.5% | 20.8% | 9.0% | 14.4% | acquisitionby | yes | 0.229 | 0.173 | 0.967 | 0.360 | 0.917 | 0.930 |
| 4 | NDSN | 2016-11-11 | 0.94 | 0.88 | 0.97 | 0.98 | Industrials | 19.5% | 14.8% | 0.8% | 1.1% | false | yes | 0.263 | 0.179 | 0.968 | 0.428 | 0.859 | 1.000 |
| 5 | GNRC | 2020-08-14 | 0.94 | 0.85 | 0.98 | 0.99 | Industrials | 141.9% | -9.0% | -21.0% | 48.8% | false | no | 0.201 | 0.177 | 0.875 | 0.528 | 0.985 | 0.980 |
| 6 | IR | 2023-05-10 | 0.94 | 0.88 | 0.97 | 0.96 | Industrials | 55.8% | 12.1% | -9.4% | 3.0% | false | yes | 0.226 | 0.166 | 0.872 | 0.600 | 0.870 | 0.949 |
| 7 | NWL | 2016-05-02 | 0.93 | 0.88 | 0.96 | 0.97 | Consumer Defensive | 0.9% | -29.9% | -43.9% | 68.6% | false | no | 0.220 | 0.138 | 0.904 | 0.498 | 0.934 | 0.964 |
| 8 | RL | 2007-06-15 | 0.93 | 0.83 | 0.97 | 1.00 | Consumer Cyclical | -31.0% | -3.5% | 5.4% | 66.1% | false | no | 0.255 | 0.187 | 0.942 | 0.377 | 0.916 | 0.876 |
| 9 | AOS | 2015-11-10 | 0.93 | 0.87 | 0.97 | 0.96 | Industrials | 22.8% | 7.5% | -4.2% | 19.4% | false | yes | 0.206 | 0.177 | 0.934 | 0.586 | 0.963 | 0.975 |
| 10 | MAS | 2019-11-22 | 0.93 | 0.85 | 0.99 | 0.96 | Basic Materials | 20.7% | 2.4% | -6.9% | 40.1% | false | no | 0.215 | 0.169 | 0.986 | 0.356 | 0.776 | 0.973 |
| 11 | ROST | 2018-08-17 | 0.93 | 0.87 | 0.97 | 0.95 | Consumer Cyclical | 15.3% | 10.9% | -6.9% | 33.5% | false | no | 0.261 | 0.179 | 0.990 | 0.410 | 0.865 | 0.956 |
| 12 | WWE | 2023-04-11 | 0.93 | 0.86 | 0.98 | 0.95 | Communication Services | -2.0% | -0.7% | -19.3% | 6.0% | delisted | no | 0.216 | 0.176 | 0.871 | 0.725 | 0.937 | 1.000 |
| 13 | MHK | 2002-02-14 | 0.93 | 0.81 | 0.99 | 0.99 | Consumer Cyclical | -12.7% | 15.0% | 11.3% | 27.8% | false | yes | 0.201 | 0.184 | 0.892 | 0.345 | 0.952 | 0.981 |
| 14 | SBUX | 2011-11-09 | 0.93 | 0.80 | 1.00 | 0.99 | Consumer Cyclical | 13.2% | 22.3% | 3.2% | 4.5% | false | yes | 0.183 | 0.183 | 0.917 | 0.446 | 0.950 | 0.963 |
| 15 | PRFT | 2019-11-15 | 0.93 | 0.83 | 0.97 | 0.98 | Technology | 5.8% | 18.3% | 9.6% | 46.3% | false | no | 0.249 | 0.182 | 0.941 | 0.512 | 0.945 | 0.965 |

## FTI

sector Energy; pick 10; mean rank 360.3 of 3,057; forest_nonloser_dd30_3y: rank 415; factor_mom_12_2_3y: rank 292; factor_roc_greenblatt_3y: rank 374.

What the tree model split on along this stock's paths (share of trees), with the stock's value:

| feature | share of trees | FTI |
| --- | --- | --- |
| vol_12m_rank | 55.7% | 0.189 |
| vol_36m_rank | 51.0% | 0.266 |
| conservative_score_rank | 30.8% | 0.971 |
| max_ret_21d_rank | 20.2% | 0.192 |
| price_vs_5y_avg_rank | 17.6% | 0.976 |
| dist_52w_high_rank | 17.6% | 0.789 |

Analogues by era: 2000-04: 2, 2010-14: 2, 2015-19: 1, 2020-24: 10.

| analogue | ticker | snapshot_date | similarity | sim_forest_nonloser_dd30_3y | sim_factor_mom_12_2_3y | sim_factor_roc_greenblatt_3y | sector | fwd_1y_cagr | fwd_3y_cagr | fwd_3y_excess_cagr | fwd_3y_max_drawdown_from_entry | delisted_in_window_3y | label_forest_nonloser_dd30_3y | vol_12m_rank | vol_36m_rank | conservative_score_rank | max_ret_21d_rank | price_vs_5y_avg_rank | dist_52w_high_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | HBI | 2013-12-16 | 0.92 | 0.82 | 0.99 | 0.96 | Consumer Cyclical | 67.2% | 13.0% | 3.3% | 5.2% | false | yes | 0.203 | 0.248 | 0.889 | 0.070 | 0.928 | 0.741 |
| 2 | ULTA | 2023-05-17 | 0.92 | 0.81 | 0.99 | 0.97 | Consumer Cyclical | -19.9% | 1.9% | -20.0% | 37.6% | false | no | 0.207 | 0.210 | 0.943 | 0.093 | 0.900 | 0.807 |
| 3 | SAFM | 2002-08-15 | 0.92 | 0.78 | 0.99 | 1.00 | Consumer Defensive | 57.9% | 52.5% | 40.8% | 15.9% | false | yes | 0.232 | 0.262 | 0.970 | 0.138 | 0.907 | 0.602 |
| 4 | LKQ | 2022-01-20 | 0.92 | 0.82 | 0.99 | 0.96 | Consumer Cyclical | 5.0% | -9.6% | -21.0% | 27.9% | false | no | 0.183 | 0.261 | 0.936 | 0.235 | 0.808 | 0.748 |
| 5 | VVV | 2022-02-07 | 0.92 | 0.76 | 1.00 | 1.00 | Energy | 10.1% | 4.6% | -7.2% | 22.2% | false | yes | 0.187 | 0.243 | 0.943 | 0.153 | 0.762 | 0.710 |
| 6 | FSS | 2020-01-06 | 0.92 | 0.77 | 0.99 | 1.00 | Industrials | 2.4% | 13.5% | 5.7% | 26.2% | false | yes | 0.239 | 0.260 | 0.862 | 0.283 | 0.910 | 0.825 |
| 7 | MOCO | 2010-11-15 | 0.92 | 0.79 | 0.97 | 0.99 | Technology | 23.0% | 5.6% | -10.5% | 7.4% | false | yes | 0.205 | 0.204 | 0.967 | 0.191 | 0.803 | 0.719 |
| 8 | QCOM | 2020-09-23 | 0.92 | 0.82 | 0.96 | 0.97 | Technology | 29.6% | 2.4% | -10.4% | 2.4% | false | yes | 0.196 | 0.245 | 0.977 | 0.241 | 0.914 | 0.791 |
| 9 | WWE | 2022-09-15 | 0.92 | 0.79 | 0.98 | 0.98 | Communication Services | 56.8% | 14.0% | -6.0% | 1.5% | delisted | yes | 0.201 | 0.220 | 0.920 | 0.190 | 0.714 | 0.846 |
| 10 | FICO | 2003-06-19 | 0.92 | 0.79 | 0.97 | 0.99 | Technology | -2.3% | 0.8% | -9.1% | 31.0% | false | no | 0.173 | 0.213 | 0.987 | 0.111 | 0.954 | 0.849 |
| 11 | PLOW | 2020-02-19 | 0.92 | 0.79 | 0.98 | 0.98 | Consumer Cyclical | -12.5% | -5.8% | -13.9% | 50.6% | false | no | 0.205 | 0.258 | 0.890 | 0.274 | 0.883 | 0.822 |
| 12 | BYD | 2023-08-15 | 0.91 | 0.86 | 0.89 | 0.99 | Consumer Cyclical | -12.4% | 9.9% | -11.1% | 23.9% | false | yes | 0.183 | 0.287 | 0.923 | 0.091 | 0.873 | 0.786 |
| 13 | TFX | 2019-09-20 | 0.91 | 0.77 | 1.00 | 0.98 | Healthcare | 10.2% | -12.2% | -24.1% | 35.2% | false | no | 0.189 | 0.194 | 0.838 | 0.233 | 0.921 | 0.791 |
| 14 | SAM | 2020-10-16 | 0.91 | 0.77 | 0.98 | 0.99 | Consumer Defensive | -45.0% | -26.9% | -36.0% | 69.4% | false | no | 0.218 | 0.266 | 0.850 | 0.183 | 0.986 | 0.903 |
| 15 | BKNG | 2023-06-21 | 0.91 | 0.82 | 0.99 | 0.92 | Industrials | 45.5% | 17.0% | -4.1% | 1.1% | false | yes | 0.214 | 0.233 | 0.983 | 0.231 | 0.792 | 0.877 |
