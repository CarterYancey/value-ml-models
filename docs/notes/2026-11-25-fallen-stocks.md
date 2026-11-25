# Fallen stocks: does a model find the ones that recover?

This note belongs to decision 61 in the [decision log](2026-09-29-decisions.md).
The terms are in [GLOSSARY.md](../../GLOSSARY.md). Every number below comes from
`dataset_v1.4.1` on the walk-forward test rows of 2005 to 2020. Those
rows are median-kind and label-observable. I did not read the holdout
rows.

## The question

Carter asked on 2026-11-25 whether the models take full advantage of a
stock's prior years. A value investor buys a stock whose price took a
hit out of proportion to the company's trouble. The company has a
long history of success, and the investor expects it to come back two
to three times over the next few years. Carter asked whether we could find all
examples of a deep fall and identify which ones are most likely to
recover.

## What the dataset holds about a stock's prior years

The features are built upstream, and this repository may only select
them. The table lists the columns that look back more than one year.
Every other feature describes the current filing or the last twelve
months.

| window | price columns | fundamental columns |
|---|---|---|
| 2 to 3 years | `mom_36_12`, `vol_36m` | `revenue_growth_3y`, the `*_trend_8q` and `*_trend_12q` slopes, the matching `*_consistency` and `*_up_frac` columns, `roa_variability_3y`, `revenue_growth_variability_3y`, `gross_margin_delta_2y` |
| 5 years | `dist_5y_high`, `price_vs_5y_avg` | the `*_trend_20q` slopes for revenue, tangible book and operating cash flow, with their consistency and up-fraction columns, `ocf_positive_frac_20q`, `fund_history_quarters`, the twelve relative-value columns that price today's yield against the stock's own 5-year history |
| 10 years | none | `div_years_paid_10y`, `div_streak_10y`, `div_cuts_10y`, `div_history_years_10y` |

Three things follow. The dataset has no 10-year record of anything but
dividends. It has no column that says how far earnings, revenue or
cash flow fell from their own peak. So a reader can judge "the price
fell more than the business did" only indirectly, through the
relative-value columns. It has no column for the duration of a fall or
for the number of earlier falls. It has none for how the stock's fall
compares with its sector's. Those belong upstream and are listed at the end.

**How the candidate's forest uses the history columns.** The table
gives the mean importance over the 16 folds of the forest
`forest_nonloser_dd30_3y_v141`.

| column | importance | position among 112 |
|---|---|---|
| `vol_12m_rank` | 0.198 | 1 |
| `vol_36m_rank` | 0.126 | 2 |
| `ocf_trend_4q_rank` | 0.067 | 3 |
| `dist_52w_high_rank` | 0.022 | 11 |
| `dist_5y_high_rank` | 0.013 | 16 |
| `price_vs_5y_avg_rank` | 0.012 | 17 |
| `earnings_yield_vs_5y_median_rank` | 0.011 | 18 |
| `mom_36_12_rank` | 0.003 | 45 |
| `ocf_trend_20q_rank` | 0.001 | 58 |
| `revenue_trend_20q_rank` | 0.000 | 87 |

The forest reads a stock's past mostly as volatility. The 5-year
drawdown and the 3-year reversal together carry under 2% of the
importance. The label explains this. "Not a loser" is a calm-stock
label, and nothing in it asks for a recovery.

## Base rates among fallen stocks

I define the fallen universe F50 as `dist_5y_high <= -0.5` inside the
100k floor. A stock in it trades at half or less of its own 5-year
high. The 3-year outcomes of the test rows, by how far the stock sat
below its 5-year high at entry, are these:

| distance from the 5-year high | rows | stocks | not a loser | doubled | beat SPY | lost half | mean 3y CAGR | median 3y excess CAGR |
|---|---|---|---|---|---|---|---|---|
| 80% or more below | 17,122 | 2,479 | 0.19 | 0.18 | 0.28 | 0.45 | −0.136 | −0.239 |
| 70% to 80% below | 10,051 | 2,551 | 0.31 | 0.19 | 0.36 | 0.27 | −0.017 | −0.098 |
| 60% to 70% below | 11,341 | 2,910 | 0.35 | 0.18 | 0.38 | 0.23 | −0.000 | −0.079 |
| 50% to 60% below | 12,373 | 3,159 | 0.38 | 0.17 | 0.38 | 0.20 | +0.014 | −0.065 |
| 30% to 50% below | 29,223 | | 0.42 | 0.14 | 0.39 | 0.16 | +0.024 | −0.053 |
| 10% to 30% below | 42,176 | | 0.47 | 0.11 | 0.41 | 0.11 | +0.042 | −0.036 |
| within 10% | 39,381 | 3,556 | 0.58 | 0.10 | 0.45 | 0.06 | +0.061 | −0.018 |

"Doubled" is the recovery label `fwd_3y_cagr >= 0.26`. "Lost half" is
a 3-year CAGR at or below −0.206. The deeper the fall was, the more doublers and the many more losers
the population holds. The mean return falls with the
depth of the fall. Within the fallen universe the outcome depends on
the year of entry more than on anything else:

| entry year | F50 rows | F50 not a loser | F50 doubled | F50 lost half | F50 mean CAGR | all liquid doubled | all liquid mean CAGR |
|---|---|---|---|---|---|---|---|
| 2005 | 3,874 | 0.32 | 0.10 | 0.32 | -0.099 | 0.10 | -0.037 |
| 2006 | 2,961 | 0.15 | 0.04 | 0.51 | -0.237 | 0.03 | -0.156 |
| 2007 | 2,494 | 0.07 | 0.04 | 0.46 | -0.223 | 0.03 | -0.122 |
| 2008 | 4,367 | 0.16 | 0.23 | 0.19 | +0.037 | 0.15 | +0.032 |
| 2009 | 5,398 | 0.58 | 0.35 | 0.12 | +0.151 | 0.30 | +0.145 |
| 2010 | 4,133 | 0.42 | 0.20 | 0.18 | +0.038 | 0.19 | +0.080 |
| 2011 | 3,551 | 0.36 | 0.23 | 0.19 | +0.044 | 0.20 | +0.088 |
| 2012 | 3,143 | 0.49 | 0.24 | 0.21 | +0.051 | 0.22 | +0.096 |
| 2013 | 1,949 | 0.31 | 0.11 | 0.41 | -0.146 | 0.10 | -0.006 |
| 2014 | 1,821 | 0.16 | 0.08 | 0.49 | -0.215 | 0.09 | -0.027 |
| 2015 | 2,321 | 0.16 | 0.12 | 0.38 | -0.132 | 0.11 | +0.004 |
| 2016 | 2,723 | 0.37 | 0.15 | 0.33 | -0.077 | 0.14 | +0.030 |
| 2017 | 2,466 | 0.17 | 0.09 | 0.49 | -0.198 | 0.10 | -0.042 |
| 2018 | 2,733 | 0.12 | 0.16 | 0.35 | -0.084 | 0.17 | +0.037 |
| 2019 | 3,068 | 0.11 | 0.18 | 0.33 | -0.057 | 0.14 | +0.011 |
| 2020 | 3,885 | 0.35 | 0.25 | 0.32 | -0.012 | 0.16 | -0.008 |

Fallen stocks that an investor bought from 2008 to 2012 earned about
what the average liquid stock earned, and more of them doubled. Fallen
stocks bought in any other year earned less than the average liquid
stock, by 5 to 20 points a year. The fallen population is a bet on the market's recovery more
than any other population in the data.

**What separates the recoveries inside F50.** Each row of the table
is a sub-population of F50 defined by one column that was known at
the snapshot.

| inside F50 | rows | not a loser | doubled | beat SPY | lost half | mean 3y CAGR | mean 3y excess CAGR |
|---|---|---|---|---|---|---|---|
| all of F50 | 50,887 | 0.30 | 0.18 | 0.34 | 0.30 | −0.046 | −0.149 |
| operating cash flow positive | 31,535 | 0.37 | 0.21 | 0.40 | 0.21 | +0.022 | −0.087 |
| operating cash flow and net income both negative | 17,068 | 0.16 | 0.13 | 0.24 | 0.47 | −0.167 | −0.262 |
| dividends paid 10 years running | 4,730 | 0.44 | 0.26 | 0.45 | 0.14 | +0.088 | −0.044 |
| no dividend record | 39,634 | 0.27 | 0.17 | 0.32 | 0.33 | −0.069 | −0.168 |
| earnings yield above 90% of its own 5-year history | 7,523 | 0.33 | 0.23 | 0.44 | 0.21 | +0.040 | −0.067 |
| Altman Z'' in the top quarter | 8,725 | 0.36 | 0.16 | 0.37 | 0.20 | +0.013 | −0.088 |
| Altman Z'' in the bottom quarter | 17,330 | 0.19 | 0.14 | 0.26 | 0.45 | −0.150 | −0.245 |
| the largest tenth by market cap | 1,802 | 0.50 | 0.19 | 0.42 | 0.10 | +0.078 | −0.039 |
| the smallest quarter by market cap | 10,846 | 0.15 | 0.12 | 0.21 | 0.51 | −0.196 | −0.299 |
| 3-year return before the last year below −50% | 14,328 | 0.25 | 0.15 | 0.28 | 0.39 | −0.113 | −0.229 |
| the last 6 months positive | 18,191 | 0.35 | 0.16 | 0.34 | 0.27 | −0.032 | −0.132 |

Each of these columns moves the recovery rate and the loser share by a
lot, and in the direction a value investor would expect. A stock
that fell by half while it still earned cash and paid its dividend
recovered far more often than one that did not. None of the
sub-populations beat SPY on average. The best of them, the dividend
payers, trailed SPY by 4 points a year on average. They beat SPY 45%
of the time.

## The fold restriction

`dist_5y_high` needs five years of prices and the data start in 1998,
so no row before 2002 is inside F50. Fold 2005 trains on rows up to
2001 and has no training row inside the universe. I run the F50 sweeps
on the 15 folds from 2006 to 2020. The training rows inside F50 are:

| fold | training rows | effective size |
|---|---|---|
| 2006 | 11,936 | 351 |
| 2007 | 24,811 | 729 |
| 2020 | 155,184 | 4,626 |
 The first
launch of the baseline sweep failed on fold 2005 before I saw this.
Its 23 failed runs are in the ledger and count as trials.

## Runs

The runs are listed in decision 61 and their results follow below.

## What needs an upstream change

Carter asked me to document the ideas that need a dataset change and
move on. These are the columns and labels this program could not test.
Each is a point-in-time quantity of a stock's own history, or an
aggregate across rows of a date, so each belongs upstream under
invariant 4.

1. **Fundamental drawdowns are missing.** The dataset does not say how
   far trailing earnings, revenue and operating cash flow sit below
   their own 5-year and 10-year peaks. With `dist_5y_high` beside such
   columns, a model could read "the price fell by half and the business
   fell by a tenth" directly. The relative-value columns are the nearest
   thing on disk, and they compare yields with a median rather than
   levels with a peak.
2. **The shape of the fall is missing.** Two columns would describe it.
   The first is the number of trading days since the 5-year high, which
   says whether the fall is fresh or three years old. The second is the
   number of earlier falls of 50% or more in the stock's history, with
   the share of them that recovered. It says whether the stock has done
   this before.
3. **A 10-year record exists only for dividends.** Three counts over the last ten
   fiscal years would extend it:
   - the years with positive net income
   - the years with positive operating cash flow
   - the years with revenue above the year before
 The dividend columns carry the
   strongest conditioning of any column in the tables above.
4. **The fall is not measured against the sector or the market.** Two
   columns would do that: the stock's `dist_5y_high` minus its sector's
   median, and SPY's own distance from its 5-year high at the snapshot
   date. A stock that fell by half while its sector fell by half is a
   different case from one that fell alone. The market's distance from
   its high is part of the market-state request of 2026-11-23.
5. **A true recovery label is missing.** "The forward path reached the
   entry-date 5-year high within H years" is a row-wise label. It needs
   the forward path's maximum, which the labels do not store. The dataset
   stores only the terminal window's maximum. Such a label would say
   whether a stock came all the way back. The recovery label here says
   only that it doubled.
6. **The peer-relative label of 2026-11-23 is still wanted.** Inside the
   fallen universe every label's base rate depends on the year of entry
   and ranges from 0.04 to 0.35. No model of a stock's own columns can be
   calibrated to that.
7. **The price history is short.** Sharadar's prices start in 1998, so
   `dist_5y_high` exists from 2002, and a 10-year high would exist from
   2008. Nothing can be done about the start date. A 10-year high
   column would still be worth having for the deployment years.
