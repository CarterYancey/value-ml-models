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

### Round 1: the candidate's forest configuration inside F50

Sweep `forest_fallen50_cells_3y`, seed 23, folds 2006 to 2020, 12 runs.
The screen takes the top 10 per quarter with at most 2 per sector. The
peers are the same-size fallen stocks of the quarter. "Lead" is the
picks' mean 3-year CAGR minus the peers'. The halves are 2006–12 and
2013–20.

| cell inside F50 | feature set | p@20 | base rate | screen precision | peers | mean 3y CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C, not a loser | 112 ranks | 0.533 | 0.285 | 0.430 | 0.331 | +0.037 | −0.017 | +0.047 | +0.060 | 0.388 | 0.464 |
| C, not a loser | theory-led, 144 | 0.440 | 0.285 | 0.370 | 0.322 | +0.022 | −0.022 | +0.002 | +0.080 | 0.438 | 0.475 |
| C, not a loser | ranks + 47, 159 | 0.547 | 0.285 | 0.433 | 0.331 | +0.033 | −0.016 | +0.043 | +0.053 | 0.395 | 0.463 |
| recovery, doubled | 112 ranks | 0.217 | 0.156 | 0.185 | 0.170 | −0.042 | −0.034 | +0.015 | −0.028 | 0.472 | 0.486 |
| recovery, doubled | theory-led | 0.183 | 0.156 | 0.183 | 0.165 | −0.037 | −0.034 | −0.005 | −0.002 | 0.468 | 0.488 |
| recovery, doubled | ranks + 47 | 0.197 | 0.156 | 0.180 | 0.167 | −0.058 | −0.030 | −0.018 | −0.036 | 0.480 | 0.485 |
| beat SPY | 112 ranks | 0.360 | 0.315 | 0.313 | 0.346 | −0.011 | −0.018 | −0.003 | +0.017 | 0.457 | 0.469 |
| beat SPY | theory-led | 0.327 | 0.315 | 0.327 | 0.343 | +0.002 | −0.022 | −0.002 | +0.047 | 0.442 | 0.472 |
| beat SPY | ranks + 47 | 0.323 | 0.315 | 0.323 | 0.345 | −0.002 | −0.020 | +0.002 | +0.033 | 0.440 | 0.471 |
| beat SPY by 10 points | 112 ranks | 0.233 | 0.198 | 0.225 | 0.217 | −0.022 | −0.029 | +0.009 | +0.005 | 0.472 | 0.484 |
| beat SPY by 10 points | theory-led | 0.213 | 0.198 | 0.220 | 0.213 | −0.002 | −0.033 | +0.004 | +0.055 | 0.420 | 0.487 |
| beat SPY by 10 points | ranks + 47 | 0.220 | 0.198 | 0.213 | 0.213 | −0.016 | −0.032 | −0.006 | +0.036 | 0.443 | 0.488 |

The candidate's own bundles, trained on every row and evaluated inside
F50 over all 16 folds, for comparison:

| bundle inside F50 | screen precision | peers | mean 3y CAGR | peers | lead, 2005–12 | lead, 2013–20 | losers | peers |
|---|---|---|---|---|---|---|---|---|
| the candidate's forest | 0.478 | 0.324 | +0.043 | −0.020 | +0.059 | +0.066 | 0.377 | 0.477 |
| the candidate's blend, forest with momentum and return on capital | 0.381 | 0.302 | +0.015 | −0.040 | +0.052 | +0.059 | 0.458 | 0.506 |
| the candidate's blend inside the 100k floor, all stocks | 0.684 | | +0.105 | | | | 0.208 | |

Three readings follow. First, inside F50 the forest learns calm and
nothing else. On cell C it leads same-size fallen peers by 5 points a
year with a fifth fewer losers. Three labels ask for a rise: the
recovery label, beat SPY, and beat SPY by 10 points. On each of them
the forest's screen precision is within 0.03 of the peers'. Its lead
is within 0.02 of zero. Second, the forest trained on every row does as well
inside F50 as the forest trained there. The population did not need its
own model. Third, the picks earn 4% a year, where the candidate's
picks earn 10.5%. The fallen population earns 10 points a year less
than the stocks near their highs, and no selection inside it closed
that gap. In cell C the theory-led set was 0.09 behind the ranks on p@20. That
is the gap seen on all rows, so the rival of prediction 3 held.

### Round 1: the regression reframe inside F50

Sweep `lgbm_regressor_fallen50_3y`, seed 23, folds 2006 to 2020, 6 runs.
The CAGR arms are measured on the recovery label and the excess arms
on beat SPY. The screen columns are as above.

| target | objective | p@20 | base rate | screen precision | peers | mean 3y CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3y CAGR | huber | 0.177 | 0.156 | 0.170 | 0.169 | −0.038 | −0.039 | +0.007 | −0.006 | 0.493 | 0.497 |
| 3y CAGR | quantile 0.5 | 0.200 | 0.156 | 0.177 | 0.166 | −0.008 | −0.034 | +0.026 | +0.026 | 0.468 | 0.488 |
| 3y CAGR | quantile 0.25 | 0.177 | 0.156 | 0.132 | 0.157 | +0.007 | −0.025 | +0.019 | +0.044 | 0.438 | 0.476 |
| 3y excess CAGR | huber | 0.353 | 0.315 | 0.345 | 0.343 | −0.022 | −0.033 | +0.017 | +0.008 | 0.477 | 0.493 |
| 3y excess CAGR | quantile 0.5 | 0.403 | 0.315 | 0.387 | 0.345 | +0.012 | −0.032 | +0.033 | +0.053 | 0.448 | 0.492 |
| 3y excess CAGR | quantile 0.25 | 0.377 | 0.315 | 0.368 | 0.350 | +0.008 | −0.021 | +0.014 | +0.042 | 0.425 | 0.473 |

The quantile arms lead the huber arm, as predicted. The best lead is
0.043 and the best mean CAGR is 0.012, both below the cell C forest's.
Predicting the size of a fallen stock's return adds nothing over
predicting that it will not lose.

### Round 2: the value investor's tests as universes, the depth of the fall, the 5-year horizon

All runs use the candidate's forest configuration on the 112 ranks at
seed 23. The 3-year cells run on folds 2006 to 2020 and the 5-year
cells on folds 2008 to 2018. The screen columns are as in round 1.
"F50 forest" is the round-1 forest for comparison.

| universe | cell | p@20 | base rate | screen precision | peers | mean CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F30 | C | 0.553 | 0.341 | 0.492 | 0.391 | +0.056 | +0.017 | +0.040 | +0.039 | 0.327 | 0.419 |
| F50 | C | 0.533 | 0.285 | 0.430 | 0.331 | +0.037 | −0.017 | +0.047 | +0.060 | 0.388 | 0.464 |
| F70 | C | 0.447 | 0.222 | 0.348 | 0.244 | −0.005 | −0.083 | +0.044 | +0.106 | 0.433 | 0.544 |
| F50, cash flow positive | C | 0.540 | 0.338 | 0.442 | 0.342 | +0.043 | −0.008 | +0.043 | +0.057 | 0.377 | 0.452 |
| F50, the larger half | C | 0.550 | 0.352 | 0.437 | 0.336 | +0.035 | −0.010 | +0.038 | +0.051 | 0.393 | 0.455 |
| F30 | recovery | 0.220 | 0.148 | 0.187 | 0.152 | +0.013 | −0.000 | +0.030 | −0.002 | 0.423 | 0.434 |
| F70 | recovery | 0.230 | 0.157 | 0.205 | 0.182 | −0.074 | −0.078 | −0.026 | +0.029 | 0.530 | 0.546 |
| F50, cash flow positive | recovery | 0.233 | 0.169 | 0.202 | 0.173 | −0.042 | −0.028 | −0.014 | −0.014 | 0.463 | 0.467 |
| F50, the larger half | recovery | 0.213 | 0.163 | 0.195 | 0.162 | −0.008 | −0.028 | +0.020 | +0.019 | 0.440 | 0.476 |
| F50 | doubled in 5 years | 0.336 | 0.222 | 0.298 | 0.259 | +0.002 | −0.023 | +0.054 | +0.000 | 0.386 | 0.429 |
| F50 | tripled in 5 years | 0.159 | 0.115 | 0.145 | 0.127 | −0.013 | −0.030 | +0.064 | −0.023 | 0.384 | 0.443 |

The next table combines the two round-1 forests inside F50 without
refitting:

| combination | screen precision | peers | mean CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|
| worst rank of the cell C forest and the recovery forest | 0.350 | 0.319 | −0.002 | −0.022 | +0.005 | +0.033 | 0.433 | 0.473 |
| mean rank of the two | 0.342 | 0.319 | −0.001 | −0.022 | +0.002 | +0.037 | 0.437 | 0.473 |

Four readings follow. First, the depth of the fall gives a clean
dose-response. The forest's lead over same-size peers grows with the
depth, from 0.039 inside F30 to 0.077 inside F70. The picks' own return
falls with it, from +0.056 to −0.005. The forest separates more where
more is at stake, and the population drags every pick down with it.
Second, the value investor's filters change nothing once the forest is
in place. Inside the cash-positive half and inside the larger half the
forest's picks earn what they earn inside all of F50, within 0.01 a
year. The forest already finds the cash-positive, larger stocks on its
own. Third, the recovery label is not learned in any universe, at any
depth, and the 5-year versions are not learned either. The one lead on
the 5-year cells sits in the first half and is zero in the second.
Fourth, the recovery forest adds nothing to the cell C forest in a
blend. Both combinations are below the cell C forest alone.

### Round 2: the single-factor bars inside F50

Sweep `baseline_factors_fallen50_3y_f06`, 12 factors, four cells, folds
2006 to 2020. The table gives cell C, which is the only cell any factor
has skill in. On the recovery label the best factor's screen precision
is 0.193 against the peers' 0.162. That factor is the earnings yield
against the stock's own 5-year median.

| factor, cell C inside F50 | screen precision | peers | mean CAGR | lead, first half | lead, second half | losers |
|---|---|---|---|---|---|---|
| lowest 36-month volatility | 0.443 | 0.318 | +0.027 | +0.007 | +0.085 | 0.378 |
| conservative score | 0.402 | 0.304 | +0.018 | +0.051 | +0.047 | 0.417 |
| the least fallen of the fallen | 0.383 | 0.299 | +0.015 | +0.052 | +0.055 | 0.423 |
| largest market cap | 0.365 | 0.336 | +0.017 | +0.005 | +0.026 | 0.437 |
| earnings yield against own 5-year median | 0.288 | 0.270 | −0.030 | +0.050 | +0.017 | 0.505 |
| return on capital | 0.258 | 0.278 | −0.054 | +0.006 | +0.012 | 0.523 |
| momentum | 0.158 | 0.236 | −0.183 | −0.075 | −0.097 | 0.678 |
| the deepest fallen | 0.057 | 0.116 | −0.435 | −0.188 | −0.108 | 0.848 |
| the F50 forest, for comparison | 0.430 | 0.331 | +0.037 | +0.047 | +0.060 | 0.388 |

Prediction 1 of decision 61 held on cell C: the two volatility bars
lead on precision. It missed on the recovery label, where return on
capital and the Altman score have no skill. The forest beats the best
bar by 0.01 on mean CAGR and leads in both halves where the volatility
bar leads only in the second. Momentum and the deepest fall are the
worst ways to choose among fallen stocks. The deepest-fallen tenth lost
money 85% of the time.

### Round 4: the fresh fall

W40 is `dist_52w_high <= -0.4` with the 100k floor. Every fold has
training rows, so these runs use all 16 folds and the halves are
2005–12 and 2013–20. "The archetype" is W40 with operating cash flow
positive and the larger half.

| model | universe | screen precision | peers | mean CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|
| forest trained inside W40, cell C | W40 | 0.366 | 0.265 | +0.018 | −0.054 | +0.066 | +0.079 | 0.423 | 0.518 |
| forest trained inside W40 and the larger half, cell C | W40, the larger half | 0.342 | 0.278 | −0.002 | −0.043 | +0.038 | +0.043 | 0.430 | 0.501 |
| forest trained inside W40, recovery | W40 | 0.131 | 0.150 | −0.037 | −0.074 | +0.039 | +0.035 | 0.484 | 0.543 |
| the candidate's forest, evaluated | W40 | 0.341 | 0.258 | −0.030 | −0.062 | +0.011 | +0.054 | 0.470 | 0.530 |
| the candidate's forest, evaluated | the archetype | 0.338 | 0.298 | −0.024 | −0.023 | −0.024 | +0.021 | 0.450 | 0.473 |
| the candidate's blend, evaluated | the archetype | 0.295 | 0.292 | −0.032 | −0.032 | −0.018 | +0.019 | 0.486 | 0.486 |
| the candidate's forest, evaluated | F50, cash flow positive, the larger half | 0.439 | 0.345 | +0.029 | −0.001 | +0.025 | +0.035 | 0.411 | 0.447 |
| lowest 36-month volatility, bar | W40 | 0.347 | 0.264 | −0.047 | −0.063 | −0.007 | +0.038 | 0.481 | 0.526 |

Three readings follow. First, the forest trained inside the fresh-fall
universe leads same-size peers by 7 points a year in both halves. That
is the largest lead in the program, and twice the lead of the
candidate's forest evaluated there. In a fresh fall, training inside
the population does help. Its picks still earn under 2% a year. Second,
the archetype fails. The candidate's forest inside it has no lead over
same-size peers and its picks lose money 45% of the time. The archetype
backtest of decision 64.6 does not run. Third, the base rates misled
the predictions, and the reason matters. The archetype's rows earn
+0.085 a year when every row counts once. They earn −0.028 a year when
every quarter counts once:

| population | rows | share of rows from 2008–09 | mean 3y CAGR, every row once | mean 3y CAGR, every quarter once |
|---|---|---|---|---|
| all liquid stocks | 200,472 | 0.118 | +0.004 | +0.008 |
| F50 | 50,887 | 0.192 | −0.046 | −0.076 |
| W40 | 40,886 | 0.244 | −0.076 | −0.130 |
| the archetype | 10,268 | 0.466 | +0.085 | −0.028 |
| F50, cash flow positive, the larger half | 15,432 | 0.307 | +0.054 | −0.014 |
| F50, dividends 5 years running | 7,990 | 0.287 | +0.059 | −0.045 |

Almost half of the archetype's rows come from the two crash years, when
large, cash-positive companies fell 40% and then recovered with the
market. A portfolio that buys ten fallen stocks every quarter does not
get that return. It buys the same number in 2007 and 2014 as in 2009.
The attraction of "all examples of a deep fall" is therefore mostly the
attraction of buying in a crash. That is market timing, and it is the
market-state question this repository has asked upstream for since
2026-11-23.

### Round 3: deeper trees, LightGBM, and the recovery label learned on every row

All runs are inside F50 on folds 2006 to 2020 at seed 23. The last row
trains on every row and evaluates inside F50.

| model | cell | p@20 | base rate | screen precision | peers | mean CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| forest, depth 4, leaf 72 | recovery | 0.217 | 0.156 | 0.185 | 0.170 | −0.042 | −0.034 | +0.015 | −0.028 | 0.472 | 0.486 |
| forest, depth 6, leaf 40 | recovery | 0.217 | 0.156 | 0.190 | 0.172 | −0.051 | −0.033 | −0.003 | −0.030 | 0.485 | 0.487 |
| forest, depth 8, leaf 30 | recovery | 0.207 | 0.156 | 0.190 | 0.174 | −0.052 | −0.032 | −0.013 | −0.027 | 0.505 | 0.486 |
| forest, depth 4, leaf 72 | `fwd_3y_cagr >= 0.1` | 0.437 | 0.320 | 0.388 | 0.362 | +0.008 | −0.017 | +0.014 | +0.036 | 0.423 | 0.466 |
| forest, depth 6, leaf 40 | `fwd_3y_cagr >= 0.1` | 0.477 | 0.320 | 0.387 | 0.362 | −0.000 | −0.022 | +0.017 | +0.026 | 0.440 | 0.471 |
| forest, depth 8, leaf 30 | `fwd_3y_cagr >= 0.1` | 0.463 | 0.320 | 0.410 | 0.363 | +0.004 | −0.024 | +0.033 | +0.024 | 0.432 | 0.476 |
| LightGBM, 300 trees of 7 leaves | C | 0.527 | 0.285 | 0.470 | 0.317 | +0.028 | −0.025 | +0.050 | +0.056 | 0.352 | 0.480 |
| LightGBM, 500 trees of 7 leaves, strong regularisation | C | 0.493 | 0.285 | 0.447 | 0.320 | +0.013 | −0.024 | +0.032 | +0.041 | 0.405 | 0.479 |
| LightGBM, 300 trees of 7 leaves | recovery | 0.203 | 0.156 | 0.197 | 0.171 | −0.048 | −0.037 | −0.011 | −0.011 | 0.503 | 0.494 |
| LightGBM, 500 trees, strong regularisation | recovery | 0.243 | 0.156 | 0.198 | 0.176 | −0.031 | −0.033 | +0.009 | −0.004 | 0.473 | 0.490 |
| forest trained on every row, evaluated inside F50 | recovery | 0.210 | 0.156 | 0.213 | 0.168 | −0.006 | −0.072 | +0.106 | +0.032 | 0.465 | 0.549 |

Deeper trees do not learn the recovery label, and neither does a second
model family. The path-free target `fwd_3y_cagr >= 0.1` is learned a
little, with a p@20 of 0.46 against 0.32. Its picks earn nothing and
lose 43% of the time. The forest learns calm from it as from cell C,
and the result is worse. LightGBM on cell C matches the forest, with
fewer losers at 0.352 and a lower mean CAGR. The one surprise is the
last row. The recovery forest trained on every row has no skill on its label
inside F50. It still leads same-size peers by 0.106 in the first half. Its peers earn −0.072, which says it picks small fallen stocks,
and its picks lose money 47% of the time. The lead falls to 0.032 in
the second half. It is not carried forward, and it is recorded as an
open oddity.


### Round 5: the two backtests for the record

Decision 65 ordered two backtests. They were not a selection between
candidates but the program's only reading in money. Each backtest
trades the "not a loser" forest trained inside its universe, and
nothing else: every month it buys the 10 highest-ranked stocks that
pass Carter's rank floor, at most 2 from one sector, in equal weights,
paying 35 basis points a side. Buys run from 2006 to 2020 and the
account is valued at the end of 2023. The 2006 start comes from the
fold restriction described above, so the SPY figures below are SPY on
the same deposits over the same years, and they differ from the SPY
figures in the candidate's 2005 to 2020 run. In the table, "lead over
the candidates" is the buys' mean annualized 3-year return minus that
of every stock that passed the screen at the same rebalance, and "lead
over same-size candidates" is the same against the candidates in the
buy's own band of market cap, one of 20. "Losers" is the share of buys
whose 3-year return was below zero, with the candidates' share after
"against". The first write-up of this table on 2026-11-25 labeled the
lead over all candidates as the lead over same-size candidates; the
figures below are corrected and the prediction's reading is unchanged.

| portfolio | final value on 180,000 | TWR | MWR | worst drawdown | buys | lead over the candidates, 3y | lead over same-size candidates, 3y | losers, 3y |
|---|---|---|---|---|---|---|---|---|
| SPY, same deposits | 664,685 | 9.72% | 11.96% | −52.8% | | | | |
| "not a loser" forest inside F50 (`bt_fallen50_forestC_top10_cap2_rankfloor`, config 3bbf0d1552a571ad) | 660,061 | 10.25% | 11.89% | −57.5% | 1,749 | +9.2 points | +6.6 points | 0.347 against 0.493 |
| "not a loser" forest inside F30 (`bt_fallen30_forestC_top10_cap2_rankfloor`, config 3bf38d97bca05b0b) | 634,784 | 10.31% | 11.55% | −48.1% | 1,770 | +6.9 points | +3.9 points | 0.331 against 0.454 |
| the candidate, 2005 to 2020 (decision 55, for scale) | 932,471 on 192,000 | 11.76% | 13.65% | −41.0% | 1,741 | | | |

The predictions of decision 65 and what held:

| prediction | F50 | F30 |
|---|---|---|
| TWR under SPY's | did not hold, 10.25% against 9.72% | did not hold, 10.31% against 9.72% |
| drawdown deeper than −50% | held, −57.5% | did not hold, −48.1% |
| buys lead same-size candidates by 3 points a year or more | held, +6.6 | held, +3.9 |

Both portfolios end with less money than SPY on the same deposits
while their TWR is higher. The reason is timing. The fallen portfolios
earned their excess over SPY in 2006 and from 2009 to 2013, and lost to
SPY in 2014, 2015, 2018, 2019, 2021 and 2023, when the deposits already
in the account were larger. The 1-year outcomes say the same: the buys
trail the candidates they were chosen from in the crash recoveries of
2009 and 2020, when every fallen stock rose, and lead them in ordinary
years. The forest picks the fallen stocks that do not fall further. It
does not pick the ones that recover. Both portfolios are far behind the
candidate's TWR of 11.76%, and at least a third of their buys lost
money over three years. At this point the program had run two
backtests, both for the record, and no further run was planned. Round
6 below changed that.

Both backtests ran twice. The first F50 run finished at 02:55 on
2026-11-25, in the second the sandbox died, so its five report files
are empty and its ledger row was cut inside the metrics. The first F30
run, at 12:42, failed at its last step because the cut row made the
ledger unreadable. Decision 68 records the repair. The F50 rerun
reproduced the cut row's final value and drawdown to the last digit.


### Round 6: the comparison window ends in 2020, and the grid of falls

Carter read round 5 and asked for two things (decision 70). First, the
portfolios should be compared with SPY on the years before 2021,
because the working assumption of this project is that the market
since 2021 is a bubble that will deflate. Second, the depth of the
fall should be varied at two horizons: 30%, 50% and 70% below the
5-year high (F30, F50, F70) and 30%, 40%, 50% and 70% below the
52-week high (W30, W40, W50, W70). The dataset has no other "distance
from a past high" column, so a 2-year or 3-year high is an upstream
request.

**Why the final value and the TWR disagreed.** The portfolio strategy
is buy and hold, so after the last buy in December 2020 both the
portfolio and the SPY leg hold their shares to the end of 2023 with no
further deposits. The gap in final value opened in 2021 and 2023, when
SPY returned 31.3% and 26.7% and the F50 portfolio 22.0% and 21.3%,
with the account at its largest. The time-weighted return gives those
years no more weight than 2006, when the account held a few thousand
dollars. That is why the TWR can be higher while the final value is
lower. Carter's reading was right about the years; the portfolio did
not go to cash, it was simply beaten in the biggest years. The
valuation files of the two round-5 runs give the values before 2021.
On 2020-12-01 the F50 portfolio held 490,613 against SPY's 487,467 on
the same deposits, and the F30 portfolio 472,380. On 2019-12-02 both
were ahead of SPY: 405,139 and 403,702 against 395,313.

**The 2020 window.** From here on the program reads every portfolio on
buys from 2006 to 2020 valued on 2020-12-31, with SPY on the same
deposits, and keeps the run valued at the end of 2023 beside it. This
is a risky choice. It drops the three years in which SPY was strongest,
and it was chosen after we saw the portfolios lose ground in them. If
the market of 2021 to 2026 turns out to be ordinary rather than a
bubble, the 2023 window is the honest one and the 2020 window
flattered the portfolios. Decision 70 says so, and the choice is to be
challenged when the bubble question is answered.

**The grid on the portfolio screen.** Each row is the candidate's
forest configuration (112 ranks, seed 23) trained inside one universe
on the label "not a loser". The 5-year universes run on folds 2006 to
2020 because no row has a 5-year high before 2002, and the 52-week
universes on all 16 folds; the halves are 2005 or 2006 to 2012 and
2013 to 2020. "Rows" are the labeled median-kind rows of 2005 to 2020
inside the universe and the 100k floor. The screen takes the top 10
per test quarter, at most 2 per sector, and reads them against
same-size peers, the test rows of the same quarter in the same of 20
market-cap bands. "Lead" is the picks' mean 3-year CAGR minus the
peers'. The F rows repeat round 2 and the W40 row repeats round 4.

| universe | rows | base rate | p@20 | screen precision | peers | mean 3y CAGR | peers | lead, first half | lead, second half | losers | peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F30, 30% below the 5-year high | 80,110 | 0.341 | 0.553 | 0.492 | 0.391 | +0.056 | +0.017 | +0.040 | +0.039 | 0.327 | 0.419 |
| F50 | 50,887 | 0.285 | 0.533 | 0.430 | 0.331 | +0.037 | −0.017 | +0.047 | +0.060 | 0.388 | 0.464 |
| F70 | 27,173 | 0.222 | 0.447 | 0.348 | 0.244 | −0.005 | −0.083 | +0.044 | +0.106 | 0.433 | 0.544 |
| W30, 30% below the 52-week high | 60,252 | 0.268 | 0.569 | 0.450 | 0.320 | +0.024 | −0.020 | +0.038 | +0.051 | 0.375 | 0.482 |
| W40 | 40,886 | 0.240 | 0.431 | 0.366 | 0.265 | +0.018 | −0.054 | +0.066 | +0.079 | 0.423 | 0.518 |
| W50 | 26,552 | 0.216 | 0.416 | 0.319 | 0.221 | −0.014 | −0.095 | +0.070 | +0.093 | 0.459 | 0.561 |
| W70 | 9,158 | 0.156 | 0.197 | 0.156 | 0.124 | −0.171 | −0.210 | +0.050 | +0.027 | 0.622 | 0.686 |

The recovery label, a stock doubling within three years, was run beside
cell C in every universe. Inside W30, W50 and W70 the forest's
precision at 20 is 0.172, 0.197 and 0.194 against base rates of 0.167,
0.190 and 0.194, and its screen precision is at or below the same-size
peers'. The label is not learned at any depth at either horizon, which
repeats rounds 1 to 4.

Three readings follow. First, the picks' own return falls with the
depth of the fall at both horizons, without exception: from +0.056 to
−0.005 at the 5-year horizon and from +0.024 to −0.171 at the 52-week
horizon. Second, at the same depth the 52-week universe earns less than
the 5-year universe. A stock 50% below its 5-year high may have sat
there for years; a stock 50% below its 52-week high fell within the
year, and more of those are companies in trouble: 57% of W50's rows
lost money over three years against 51% of F50's. Third, the forest's
lead over same-size peers grows with the depth at the 5-year horizon
and up to 50% at the 52-week horizon, then shrinks at W70, where the
universe holds under 200 rows in some years and the forest barely
beats the base rate. The best picks of the grid by their own return
are F30's, at 5.6% a year, which is half of what the candidate's screen
earns inside the 100k floor (10.5%, decision 61.4).

**The grid in money.** Each row is the "not a loser" forest of the
screen table above, traded alone inside its universe: every month the
10 highest-ranked stocks that pass Carter's rank floor, at most 2 from
one sector, equal weights, 35 basis points a side, buys from 2006 to
2020 with year-end refits. The 2020 window values the account on
2020-12-31 and the 2023 window on 2023-12-29. SPY on the same deposits
of 180,000: 500,058 at the end of 2020 (TWR 9.67%, MWR 12.58%, worst
drawdown −52.8%) and 664,685 at the end of 2023 (TWR 9.72%). The last
two columns read the buys of the 2020 window over the three years
after each buy, against the candidates of the same rebalance in the
buy's own market-cap band; "losers" is the share of buys with a
negative 3-year return. The twelve new runs and the two of round 5 are
all the backtests the program has run: fourteen, all for the record.

| universe | final value, 2020 window | TWR | MWR | worst drawdown | final value, 2023 window | TWR, 2023 window | lead over same-size candidates, 3y | losers, 3y |
|---|---|---|---|---|---|---|---|---|
| SPY, same deposits | 500,058 | 9.67% | 12.58% | −52.8% | 664,685 | 9.72% | | |
| F30 | 491,271 | 10.59% | 12.37% | −48.1% | 634,784 | 10.31% | +5.0 points | 0.335 |
| F50 | **514,776** | 10.57% | 12.92% | −57.5% | 660,061 | 10.25% | +7.6 points | 0.358 |
| F70 | 476,627 | 6.78% | 12.02% | −75.5% | 661,625 | 7.57% | +10.0 points | 0.424 |
| W30 | 499,881 | 9.90% | 12.58% | −57.3% | 627,263 | 9.56% | +6.0 points | 0.372 |
| W40 | 470,923 | 10.10% | 11.88% | −61.3% | 608,957 | 9.91% | +8.3 points | 0.398 |
| W50 | 441,845 | 8.80% | 11.13% | −60.2% | 558,797 | 8.69% | +8.4 points | 0.457 |
| W70 | 312,884 | 16.99% | 7.00% | −92.9% | 349,663 | 14.68% | +4.7 points | 0.621 |

The configs are `bt_fallen{30,50,70}_forestC_top10_cap2_rankfloor` and
`bt_fresh{30,40,50,70}_forestC_top10_cap2_rankfloor`, each with a
`_to2020` twin; the config hashes are in the ledger and in the logbook
entry.

Four readings follow.

First, Carter's question. On the years before 2021 the F50 portfolio
beats SPY on every measure: 514,776 against 500,058 on money, 10.57%
against 9.67% on TWR, 12.92% against 12.58% on MWR. F30 and W30 end
within 2% of SPY on money, W30 by 177 dollars, with a higher TWR. Every
universe deeper than 50% ends behind SPY on money, by 5% (F70) to 37%
(W70). The suspicion that started this round was right for F50 and
wrong for everything deeper: the deep-fall portfolios were behind SPY
before the bubble years too.

Second, what a time-weighted return can hide. The W70 portfolio has
the highest TWR in the program, 16.99% a year, and the least money,
312,884 on 180,000, with a worst drawdown of −92.9%. Its 2006 return
was +1,911%. In January 2006 it bought 2,491 shares of Foamex
(`FMXLQ`, in bankruptcy) at 4 cents, about 100 dollars, and the stock
reached 15 dollars by May. That one position took an account of 5,700
to 67,000 in a month, and the TWR carries that month forever, however
small the account was. The money-weighted return of 7.0% and the final
value say what the deposits earned. The rule for reading from here on:
a TWR is never read without the final value, the MWR and the per-year
table beside it. The same run shows a hole in the investability
filter: the 100k dollar-volume floor and Carter's rank floor let a
4-cent bankrupt stock through. Whether to add a price floor is
Carter's call, and it is a config change, not a code change.

Third, the depth of the fall. Money falls with the depth at both
horizons, with F70's 2023 value as the one exception, and the worst
drawdown deepens with it, from −48% to −76% at the 5-year horizon and
from −57% to −93% at the 52-week horizon. The forest's lead over
same-size candidates grows with the depth, from 5 to 10 points at the
5-year horizon and from 6 to 8 at the 52-week horizon, and collapses
at W70. At every depth the 52-week universe ends with less money than
the 5-year universe. The forest keeps finding the fallen stocks that
do not fall further, and the deeper the population has fallen, the
less that is worth.

Fourth, the rule of decision 70.3. F50 is the one portfolio that beats
SPY on both money and TWR on the 2020 window, and its buys lead
same-size candidates by 7.6 points, so it goes to seeds 232 and 1776.
My prediction that no portfolio would meet the rule did not hold. The
seed runs are read below.

The predictions of decision 70 and what held:

| prediction | result |
|---|---|
| the lead over same-size peers grows with the depth at both horizons, and the picks' return falls with it | held at the 5-year horizon and up to W50 at the 52-week horizon; the lead collapses at W70 |
| F50 above SPY on money and TWR on the 2020 window; F30 within 5% on money with a higher TWR | held (readings of the valuation files, not predictions) |
| every 52-week portfolio below SPY on money on both windows | held |
| W50 and W70 below SPY on TWR by 2 points or more | did not hold: W50 by 0.9 points, and W70's TWR is above SPY's for the reason above |
| W30 the closest 52-week portfolio to SPY | held |
| every drawdown deeper than −50% except F30's, deepening with the depth | held, with W50 one point shallower than W40 |
| no portfolio meets the rule of decision 70.3 | did not hold: F50 meets it |

**The F50 portfolio at three seeds.** Decision 61.5 says an arm is read
at seeds 232 and 1776 before it counts, so the F50 "not a loser" forest
was trained twice more (`forest_fallen50_cellC_seeds_3y`) and each
seed's portfolio was backtested on both windows. The screen agreed with
seed 23 within 0.02 on every figure. The portfolios:

| F50 portfolio | final value, 2020 window | TWR | MWR | worst drawdown | final value, 2023 window | TWR, 2023 window | lead over same-size candidates, 3y | losers, 3y |
|---|---|---|---|---|---|---|---|---|
| SPY, same deposits | 500,058 | 9.67% | 12.58% | −52.8% | 664,685 | 9.72% | | |
| seed 23 (`bt_fallen50_forestC_top10_cap2_rankfloor`) | 514,776 | 10.57% | 12.92% | −57.5% | 660,061 | 10.25% | +7.6 points | 0.358 |
| seed 232 (`bt_fallen50_forestC_s232_top10_cap2_rankfloor`) | 512,346 | 10.58% | 12.86% | −58.0% | 649,287 | 10.19% | +8.0 points | 0.352 |
| seed 1776 (`bt_fallen50_forestC_s1776_top10_cap2_rankfloor`) | 524,688 | 10.34% | 13.14% | −58.1% | 697,903 | 10.29% | +7.3 points | 0.353 |
| the candidate, 2005 to 2020 (`bt_nonloser_mom_roc_top10_cap2_rankfloor_v141`), read from its valuation file | 728,211 against SPY's 536,924 on 192,000 | 12.43% against 9.38% | | −41.0% | 932,471 against 732,110 | 11.76% | | |

Before 2021 the F50 portfolio beats SPY at all three seeds, by 2.5% to
4.9% on money and by 0.7 to 0.9 points of TWR, with a worst drawdown 5
points deeper than SPY's. On the 2023 window two seeds end below SPY
and one above. My prediction that one of the two new seeds would end
below SPY on money before 2021 did not hold; the arm passes the rule
of decision 70.3 at every seed. It is still a long way behind the
candidate. On the same 2020 window the candidate holds 36% more than
SPY where F50 holds 3% more, and the candidate's drawdown is 17 points
shallower. The candidate's start of 2005 and its larger deposits do
not change that reading, because both figures are ratios to SPY on the
same deposits.

**What the round concludes.** Carter's suspicion was right about F50
and about F30 and W30, which are within 2% of SPY before 2021, and
wrong about every deeper fall. A model that finds the fallen stocks
that will not fall further gives a portfolio of fallen stocks that
keeps up with SPY, or slightly beats it, before the bubble years. It
does not give a portfolio that competes with the candidate. The grid
adds a dose-response in money: the deeper the fall that defines the
universe, the less the portfolio ends with, at both horizons, while
the forest's lead over the stocks it chose from grows. The W70 run
adds the rule that a TWR is read only beside the final value, the MWR
and the per-year table. Whether the F50 portfolio is worth running as
a second portfolio beside the candidate, for its different population,
is Carter's decision (decision 71). The program's backtest count is
eighteen, all for the record.
