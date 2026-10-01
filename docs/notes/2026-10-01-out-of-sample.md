# The candidate outside 2005–2023: traded to 2026-08-21

Detail behind the [logbook](../logbook.md) entries of 2026-10-01 for
the runs to 2026 and their diagnostics. Decisions 28, 29, 30 and 32 of
the [decision log](2026-09-29-decisions.md). The candidate:
[the candidate](2026-10-01-candidate.md).

**Simulated, cost-adjusted paper results, not live performance, and
not results of record.** `dataset_v1.4`, `prices_v1.0` (to
2026-08-21), fold definitions `split_folds.parquet` of `dataset_v1.4`.
35 backtest configurations have been tried on `dataset_v1.4`; the four
here are the first to be valued past 2023-12-29, and they are the
fixed candidate and its named variant, not a selection.

## What ran, and how it was checked

- Backtests 32 to 35, git `5ed44ef` and `09bb3ac` (the second commit
  adds configs and the decision log, no code): decision 24's blend
  (cell C's forest seed 23, 12-month momentum, return on capital, by
  mean rank; top 10 a month, at most 2 per sector, equal weights) with
  the floor Carter chose for deployment (`dollar_volume_3m_rank >=
  0.2`), buys and deposits to 2026-08-21, valued that day. Buy and
  hold, the rank sell discipline (`[sell] max_rank_pct = 0.2`), and
  each again with `fractional_shares = true`. Predictions in each
  config before the run.
- Trade years after the forest's last fold (2020) are served by
  year-end refits on rows whose 3-year label was observable by Jan 1
  of the trade year (2021–23 from decision 26's cache, 2024–26 new).
  No split tags are read. The years overlap the sealed 3-year holdout
  window, whose one look in cell C Carter took the same day
  (decision 29).
- Check: the buy-and-hold equity curve to 2020-12-31 equals that of
  backtest 27 (`bt_nonloser_mom_roc_top10_cap2_rankfloor`, config
  `6005c9c0a2869bc9`) to the cent, on all 192 monthly valuations.
- Diagnostics (decision 30): a script outside the ledger
  (`scratch/2026-10-01-oos-diagnostics/` on the lab branch) that
  rebuilds every month's investable cross-section, scores it with the
  same fold models and refits, takes the capped top 10 of every
  combination of the three legs, and reads every pick and every
  investable candidate (826,329 candidate-months) on the report's
  per-buy convention. Its outcomes equal
  `portfolio.report.buy_outcomes` to 1e-15 on the candidate's 2,480
  picks. No label column is read and no portfolio is simulated.
  `claude/backtest-universe-outcomes` has since put the same reading
  in the backtest report (last section).

## Results

| | deposits | final value 2026-08-21 | time-weighted | money-weighted | worst drawdown | costs |
|---|---|---|---|---|---|---|
| SPY, same deposits | 260,000 | 1,326,084 | 10.93% | 13.20% | −52.9% | |
| candidate, buy and hold | 260,000 | 1,193,902 | 11.31% | 12.42% | −41.4% | 1,585 |
| candidate, sell discipline | 260,000 | 1,344,630 | 11.99% | 13.31% | −39.6% | 14,725 |
| buy and hold, fractional shares | 260,000 | 1,172,560 | 11.21% | 12.28% | −43.1% | 1,554 |
| sell discipline, fractional shares | 260,000 | 1,329,280 | 11.96% | 13.22% | −41.2% | 14,670 |

(SPY with fractional shares: 1,326,614.)

In money, buy and hold was 37% ahead of SPY on 2020-12-01 (737,211
against 536,924), 29% ahead on 2024-01-02 (992,886 against 770,810)
and is 10% behind at the end.

Time-weighted, by period: 2005–2020, 12.7% a year against SPY's 9.4%
(sell discipline 13.6%); 2021 to 2026-08, 7.3% against 15.4% (7.6%).
Worst drawdown inside 2021–26, monthly values: −21.2% against −22.4%
(−24.1%). Monthly volatility over the whole run 15.4% a year against
16.5%, beta 0.86.

Calendar years against SPY, points (from the equity curves, first
trading day of January to the next; the reports of these four runs
print years that run December to December, see
[process issues](process-issues.md)):

| | SPY | buy and hold | sell discipline | buy and hold, fractional | sell, fractional |
|---|---|---|---|---|---|
| 2005 | +7.1% | −3.0 | −2.0 | | |
| 2006 | +13.6% | −2.0 | −1.9 | | |
| 2007 | +4.4% | −5.2 | −6.7 | | |
| 2008 | −34.3% | +11.4 | +12.7 | | |
| 2009 | +24.7% | +4.7 | −1.3 | | |
| 2010 | +14.3% | +14.4 | +16.8 | | |
| 2011 | +2.5% | +5.5 | +10.0 | | |
| 2012 | +17.1% | −0.4 | −1.2 | | |
| 2013 | +27.8% | +9.7 | −1.9 | | |
| 2014 | +14.5% | −4.0 | +4.1 | | |
| 2015 | −0.1% | +7.2 | +9.9 | | |
| 2016 | +14.5% | −1.3 | +0.1 | | |
| 2017 | +21.6% | +0.3 | +1.1 | | |
| 2018 | −5.1% | +2.6 | +9.2 | | |
| 2019 | +32.3% | +8.7 | +11.1 | +8.7 | +11.4 |
| 2020 | +15.7% | +2.8 | +1.9 | +2.0 | +2.1 |
| 2021 | +31.3% | −8.6 | −8.2 | −7.7 | −8.1 |
| 2022 | −19.0% | +3.2 | +0.6 | +4.2 | +0.5 |
| 2023 | +26.0% | −2.9 | −7.9 | −3.6 | −8.1 |
| 2024 | +25.3% | −12.5 | −9.1 | −12.4 | −9.2 |
| 2025 | +18.2% | −14.4 | −12.4 | −14.6 | −12.6 |
| 2026 to 08-21 | +12.7% | −12.7 | −9.3 | −13.2 | −9.2 |
| sum 2005–12 | | +25.3 | +26.5 | | |
| sum 2013–20 | | +26.1 | +35.5 | | |
| sum 2021–26 | | −47.9 | −46.3 | | |
| years ahead, of 22 | | 11 | 11 | | |

In the 13 months of 2021–26 in which SPY fell 3% or more, buy and
hold was ahead of it in 8, by 0.2 points on average; in the 31 such
months of 2005–2020, in 24, by 1.3 points.

Per buy (buy and hold, whole shares; each buy over the three years
after its trade date against SPY over the same dates):

| buy year | buys | mean excess a year, 1y | lost money, 1y | with a 3y outcome | mean excess a year, 3y | beat SPY, 3y | lost money, 3y |
|---|---|---|---|---|---|---|---|
| 2005–2020 (decision 24, dollar floor) | 1,741 with a 3y outcome | | | | +0.025 | 0.61 | 0.20 |
| 2021 | 87 | −0.145 | 0.75 | 87 | −0.116 | 0.26 | 0.41 |
| 2022 | 81 | −0.028 | 0.54 | 81 | −0.109 | 0.25 | 0.32 |
| 2023 | 75 | −0.087 | 0.29 | 50 | −0.169 | 0.18 | 0.38 |
| 2024 | 64 | −0.066 | 0.39 | | | | |
| 2025 | 77 | −0.191 (49 buys) | 0.37 | | | | |
| all buys, 2005–2026 | 2,180 | +0.012 | 0.32 | 1,965 | +0.009 | 0.57 | 0.22 |

With fractional shares every order fills (2,600 buys, 2,240 with a
3-year outcome): +0.002 a year over all buys.

The whole-share rule: 64 to 87 buys a year from 120 orders in 2020–25
(108 to 120 in 2005–12), 176 of 260 months short of ten buys.

## Against the predictions in the configs

| | prediction | measured | matched? |
|---|---|---|---|
| buy and hold | 2021–23 within 1.5 points of the dollar-floor run's years | the report's years −9.3 / +4.2 / −1.5 against −9.6 / +4.3 / −2.2 (both December to December; the 2023 rows differ because the earlier run's last year ended on 12-29) | yes for 2021–22; 2023 not comparable |
| | 2024 behind SPY by 2 to 12 points | −12.5 | **no**, by half a point |
| | 2025 and 2026 within 6 points either way | −14.4, −12.7 | **no** |
| | final value above SPY's, lead under 27% | 10% below | **no** |
| | the 2021 buys −0.10 to −0.02 a year over 3y; 2022's within 0.04 of zero; 2023's behind; losers under 0.30 in each | −0.116, −0.109, −0.169; losers 0.41, 0.32, 0.38 | sign yes for 2021 and 2023; size and losers **no** |
| sell discipline | value at 2023-12-29 within 10% of the dollar-floor variant's 1,054,924 | 1,032,015 on 2024-01-02 | yes |
| | each of 2024–26 within 4 points of buy and hold | 3.4, 2.0, 3.4 | yes |
| | final value above SPY's, within 10% of buy and hold | 1.4% above SPY; 12.6% above buy and hold | SPY yes; **no** on the second |
| | costs 3 to 6 times buy and hold's | 9.3 times | **no** |
| fractional, both | to 2020 within 0.5 points of whole shares; 2024–26 within 5 points a year and behind SPY; final value within 10% and (buy and hold) below SPY | 12.56% against 12.74%; within 1 point each year; −1.8% and −1.1% | yes |

## Why: the diagnostics

Three readings were written down before the diagnostics ran (decision
30): (a) the era, (b) the fit, (c) the template.

**(c) is out.** The fractional runs are within a point of the
whole-share runs in every year of 2021–26.

### The stocks the picks were chosen from

Every investable candidate of every month (rank floor, a quote within
three days), equal-weighted, read as a buy is read:

| | 2005–12 | 2013–20 | 2021–23 cohorts |
|---|---|---|---|
| mean 3y excess over SPY, a year | −0.057 | −0.111 | −0.218 |
| median | −0.022 | −0.071 | −0.169 |
| beat SPY | 0.45 | 0.35 | 0.25 |
| lost money over 3y | 0.45 | 0.40 | 0.52 |
| candidate-months | 322,555 | 284,132 | 110,251 |

One-year excess by cohort year, 2021 to 2025: −0.164, −0.116, −0.180,
−0.108, +0.102 (2025: 23,733 candidate-months with an outcome).

By market-capitalization rank, mean 3y excess over SPY:

| capitalization rank | 2005–12 | 2013–20 | 2021–23 cohorts |
|---|---|---|---|
| smaller half | −0.116 | −0.179 | −0.333 |
| 50th to 80th percentile | −0.033 | −0.083 | −0.176 |
| 80th to 95th | −0.002 | −0.049 | −0.120 |
| largest 5% | +0.002 | −0.025 | −0.065 |
| largest 2% | +0.011 | −0.018 | −0.050 |
| largest 1% (30 to 37 stocks) | +0.010 | −0.022 | −0.033 |

### The picks, per leg, against all candidates and against same-size candidates

All ten orders a month (whole shares do not enter), 960 picks in each
half of 2005–2020 and 320 with a 3-year outcome for 2021–23. "Peers":
the same month's candidates in the same 5% band of
`log_marketcap_rank`.

| picks | period | mean 3y excess over SPY | minus all candidates | minus same-size peers | lost money | peers lost money | mean cap rank |
|---|---|---|---|---|---|---|---|
| forest alone | 2005–12 | +0.009 | +0.067 | +0.023 | 0.24 | 0.35 | 0.84 |
| | 2013–20 | −0.014 | +0.097 | +0.027 | 0.12 | 0.25 | 0.92 |
| | 2021–23 | −0.079 | +0.139 | +0.006 | 0.22 | 0.34 | 0.94 |
| forest + return on capital | 2005–12 | +0.010 | +0.067 | +0.015 | 0.26 | 0.34 | 0.90 |
| | 2013–20 | +0.010 | +0.120 | +0.052 | 0.10 | 0.26 | 0.92 |
| | 2021–23 | −0.079 | +0.140 | +0.005 | 0.18 | 0.34 | 0.95 |
| forest + momentum | 2005–12 | +0.018 | +0.075 | +0.033 | 0.29 | 0.36 | 0.82 |
| | 2013–20 | −0.019 | +0.091 | +0.034 | 0.22 | 0.29 | 0.86 |
| | 2021–23 | −0.077 | +0.141 | +0.027 | 0.29 | 0.37 | 0.89 |
| **the candidate (all three)** | 2005–12 | +0.033 | +0.090 | **+0.046** | 0.25 | 0.36 | 0.83 |
| | 2013–20 | +0.011 | +0.122 | **+0.059** | 0.16 | 0.27 | 0.89 |
| | 2021–23 | −0.118 | +0.100 | **−0.016** | 0.34 | 0.37 | 0.90 |
| return on capital alone | 2005–12 | −0.002 | +0.056 | +0.034 | 0.33 | 0.40 | 0.69 |
| | 2013–20 | −0.070 | +0.040 | +0.010 | 0.34 | 0.34 | 0.72 |
| | 2021–23 | −0.206 | +0.012 | −0.034 | 0.43 | 0.46 | 0.70 |
| momentum alone | 2005–12 | −0.229 | −0.172 | −0.130 | 0.66 | 0.51 | 0.42 |
| | 2013–20 | −0.260 | −0.149 | −0.089 | 0.64 | 0.50 | 0.41 |
| | 2021–23 | −0.418 | −0.200 | −0.189 | 0.76 | 0.54 | 0.52 |

The candidate against its same-size peers, by buy year: positive in
12 of the 14 cohorts of 2005–2018 (+0.020 to +0.121; 2005 −0.023 and
2009 −0.016), then −0.002, +0.002, −0.034, +0.011 and −0.030 for 2019
to 2023: five cohorts at about zero, two of them inside the selection
window. Over one year: −0.194, −0.083, +0.010, −0.011, +0.028 and
−0.228 for 2020 to 2025.

### Inside the largest fifth

Stocks with `log_marketcap_rank >= 0.8` (718 to 911 a month), by
quintile of the forest's score within the month, mean 3y excess over
SPY and the share losing money:

| forest quintile | 2005–12 | 2013–20 | 2021–23 | lost: 2005–12 | 2013–20 | 2021–23 |
|---|---|---|---|---|---|---|
| lowest | −0.038 | −0.088 | −0.203 | 0.44 | 0.41 | 0.57 |
| 2 | −0.010 | −0.058 | −0.088 | 0.39 | 0.33 | 0.40 |
| 3 | +0.005 | −0.032 | −0.077 | 0.35 | 0.25 | 0.35 |
| 4 | +0.024 | −0.016 | −0.077 | 0.29 | 0.18 | 0.31 |
| highest | +0.016 | −0.022 | −0.087 | 0.25 | 0.16 | 0.30 |

Return on capital among large caps: lowest quintile −0.026 / −0.092 /
−0.145, highest +0.012 / −0.014 / −0.092, the three in between +0.005
to +0.017 / −0.046 to −0.025 / −0.094 to −0.087. Momentum among large
caps: the lowest and the highest quintile are the two worst in every
period.

### Where the index's largest members ranked

Position among the investable stocks, first trading day of January
(1 is best):

| | NVDA | TSLA | META | AMZN | MSFT | AAPL |
|---|---|---|---|---|---|---|
| 2023, of 3,673: forest | 1,599 | 1,987 | 1,940 | 1,209 | 349 | 290 |
| 2023: all three legs | 1,477 | 1,633 | 1,941 | 1,529 | 608 | 38 |
| 2024, of 3,332: forest | 1,308 | 1,705 | 926 | 793 | 186 | 144 |
| 2024: all three legs | 141 | 923 | 202 | 561 | 20 | 31 |
| 2025, of 3,096: forest | 1,478 | 1,675 | 993 | 783 | 225 | 223 |
| 2025: all three legs | 174 | 1,677 | 274 | 610 | 308 | 132 |

The 36-month volatility ranks of NVDA, TSLA and META were 0.32 to
0.59 in those Januaries (0 is calmest); JNJ, PG, WMT and COST were at
0.00 to 0.07.

## Measured

1. **Traded past 2023 the candidate lost its lead over SPY.** Buy and
   hold ends 10% behind in money; the sell variant 1.4% ahead. Both
   trailed SPY in five of the six years 2021–26, by 9 to 14 points a
   year from 2024 on. Over the whole 21.6 years the time-weighted
   return is 11.3% (12.0%) against 10.9%, the money-weighted 12.4%
   (13.3%) against 13.2%, with a worst drawdown of −41% (−40%) against
   −53%.
2. **The protection in falls was smaller after 2020**: 3.2 points
   ahead in 2022 (11.4 in 2008), 0.2 points a month in SPY's down
   months against 1.3 before, and the same drawdown as SPY inside
   2021–26.
3. **The buys of 2021–23 trailed SPY by 11 to 17 points a year over
   three years, and 32% to 41% of them lost money** (2005–2020: +2.5,
   20%).
4. **It is not the whole-share rule.**
5. **The average investable stock trailed SPY by 22 points a year**
   for the same cohorts, twice the gap of 2013–20 and four times that
   of 2005–12; the largest 5% by 6.5 points, the largest 1% by 3.3.
   SPY outran the equal-weighted mean of every size band, its own
   thirty largest members included.
6. **Size decides more than the models do.** Between the smaller half
   and the largest 5% lie 12, 15 and 27 points a year in the three
   periods. The candidate's picks sit at a mean capitalization rank
   of 0.83 to 0.90.
7. **Against same-size stocks the candidate led by 4.6 and 5.9 points
   a year in 2005–12 and 2013–20 and trailed by 1.6 for the buys of
   2021–23.** Its lead over all candidates (9.0, 12.2, 10.0) was
   mostly size. The forest alone: +2.3, +2.7, +0.6.
8. **What momentum and return on capital added to the forest reversed
   after 2020**: +2.3 and +3.2 points a year against same-size stocks
   in the two halves of 2005–2020, −2.2 for 2021–23. Either one alone
   beside the forest did not reverse (+0.5 and +2.7 for 2021–23).
   The candidate's same-size lead was already zero for the cohorts of
   2019 and 2020, inside the selection window.
9. **The forest kept avoiding losers, net of size**: 22% of its picks
   lost money over three years for 2021–23 against 34% of their
   same-size peers (12% against 25% for 2013–20). The candidate's
   picks: 34% against 37%.
10. **Among large caps the forest's ranking separates the worst
    quintile and nothing above it**, in every period; in 2021–23 the
    worst quintile trailed SPY by 20 points a year and 57% of it lost
    money, and the other four quintiles trailed by 8 to 9.
11. **The index's most volatile giants rank in the middle of the
    forest's list** (NVDA 1,308th to 1,599th of about 3,400 in three
    Januaries), and in the Januaries of 2022 to 2026 the candidate
    ranked none of NVDA, TSLA, META and AMZN inside its top 100.

## What it might mean (hypotheses)

- *The era, in its plainest form.* From 2023 the index was carried by
  a few very large, fast-growing and volatile companies. A model of
  "did not lose and did not fall 30%" is a model of calm, and ranks
  them in the middle; an equal-weighted portfolio of anything else
  trailed. Measured: items 5, 6, 10, 11. This is condition (2) of the
  thesis and it covers the whole of 2021–26. What it predicts: the
  candidate leads again when the index's largest members stop
  leading, as it did in 2005–2020 when the largest 5% matched SPY.
  Nothing in the data to 2026-08 can test that.
- *The blend's increment was fitted.* Item 8. Rivals: (i) 2021 alone:
  the momentum leg's picks of 2021 lost 60 points a year against SPY
  (95% lost money), and one cohort of 120 picks moves a mean of 320;
  without 2021 the candidate's same-size lead for 2022–23 is −0.005.
  (ii) the lead had already gone by 2019 (item 8, last sentence), in
  which case it ended inside the sample and 2005–2018 was the period
  it described. The two are not exclusive; three to five cohorts
  cannot separate them.
- *What the forest is.* It finds stocks that will not lose, and among
  large companies that is the bottom fifth to avoid, not a top ten to
  buy (item 10). A top-10 rule spends the ranking where it has no
  resolution.

## What this changes

- The candidate is not shown to beat SPY; its record is "the index's
  return over 21 years with three quarters of its worst drawdown, 37%
  ahead at the end of 2020 and 10% behind in August 2026". Whether
  that is worth trading is Carter's call.
- Every comparison with "all rows" or "the average stock" in the
  earlier notes overstates selection: the same-size reference is the
  one to read ([process issues](process-issues.md)).
- The open question is no longer "does it hold outside 2005–2023"
  but "is there any ranking that chooses well among large companies":
  decision 32's experiment.

## The last bubble: a stand-in on 1999–2004 (decision 35)

Carter's reading of 2021–26 (2026-10-01): a temporary change in
market behaviour, perhaps a bubble, in which returns are dominated by
stocks that fail a value investor's test; a value strategy trails
through it and dominates again during and after the correction. The
dataset's snapshots begin at the end of 1997 and nothing here was ever
run before 2005, so 1999–2004 can be read. No fold model exists
there; the stand-in is the lowest `vol_12m_rank` (the forest's
largest input), 12-month momentum and return on capital by mean rank,
with the candidate's rule (rank floor, top 10 a month, at most 2 per
sector), every pick read as in the diagnostics above
(`scratch/2026-10-01-oos-diagnostics/diag_standin.py`, git `1d5b4ec`;
columns and the price panel only). Predictions were written in the
decision log before the run.

Is the stand-in the candidate? Same-size lead over three years,
2005–12 / 2013–20 / 2021–23: +0.020 / +0.055 / −0.016, against the
candidate's +0.046 / +0.059 / −0.016; against SPY +0.013 / +0.010 /
−0.127 against +0.033 / +0.011 / −0.118. Close enough to read.

| buys of | 1y: against SPY | against same-size peers | beat SPY | 3y: against SPY | against same-size peers | beat SPY | lost money (peers) | all candidates against SPY, 1y / 3y |
|---|---|---|---|---|---|---|---|---|
| 1999 | −0.027 | −0.147 | 0.29 | +0.082 | +0.071 | 0.83 | 0.34 (0.55) | +0.295 / −0.010 |
| 2000 | +0.132 | +0.096 | 0.64 | +0.066 | +0.103 | 0.61 | 0.62 (0.64) | +0.045 |
| 2001 | +0.187 | +0.128 | 0.87 | +0.098 | +0.088 | 0.88 | 0.13 (0.41) | +0.120 |
| 2002 | +0.150 | +0.072 | 0.68 | +0.112 | +0.084 | 0.80 | 0.02 (0.26) | +0.184 |
| 2000–02 | +0.156 | +0.098 | 0.73 | +0.092 | +0.092 | 0.76 | 0.25 (0.44) | +0.113 / +0.009 |
| 2003 | +0.080 | −0.066 | 0.61 | −0.003 | −0.027 | 0.43 | 0.12 (0.21) | +0.323 |
| 2004 | +0.089 | +0.030 | 0.57 | +0.013 | +0.015 | 0.62 | 0.20 (0.25) | +0.048 |

Within 1999, the first-year excess over SPY was −0.137 for the buys
of January to June and +0.082 for July to December. The stand-in's
1999 picks: General Mills, Ecolab, Abbott, Waters, McGraw-Hill.

The two run-ups, by size (mean excess over SPY of all candidates):

| | smaller half | 50th–80th | 80th–95th | largest 5% |
|---|---|---|---|---|
| buys of 1999, first year | +0.513 | +0.201 | +0.158 | +0.007 |
| buys of 2021–23, three years, a year | −0.333 | −0.176 | −0.120 | −0.065 |

**Measured:** on six cohorts no choice here was made on, the stand-in
lagged in the last year of the run-up (behind SPY, 15 points behind
its same-size peers) and then led for the buys of 2000 to 2002 by 9
points a year over three years, against SPY and against same-size
stocks alike; the buys of 1999 themselves were 8 points a year ahead
after three years. The buys of 2003–04 had no lead. Predictions 1
and 3 held; 2 held on return and missed on losers (the buys of 2000
lost money as often as their peers).

**What the test cannot reach** (Carter, 2026-10-01): the growth of
the bubble. The data begins at the end of 1997 and the first picks
are January 1999, so this is the run-up's last year and its
aftermath. It supports "leads again during and after the
correction"; on "trails while the bubble grows" it has one year. The
several years of trailing a rising market that 2021–26 would have to
be compared with are before the data.

**What it supports, and what it does not** (decision 35): the
pattern Carter describes happened once before in this data, with
this kind of selection. One precedent, a stand-in, and factors that
are known to have paid after 2000. The episodes differ in kind: 1999
was a run-up in small stocks with the largest level with the index;
2021–26 is the reverse, the excess sitting in a few giants inside
the index the candidate is measured against. And in the precedent
the correction came within a year of the lag seen here; the buys of
2021–23 have had none in their three years. Whether they recover
against SPY when one comes cannot be read from anything on disk.

## The report's own table

`claude/backtest-universe-outcomes` reads every candidate of every
rebalance inside `vml-backtest` and prints the buys beside all
candidates and beside their same-size peers. The three runs above
were run again on that code (same config hashes, the same figures to
the cent); their tables are in the reports and summarised in the
logbook entry.
