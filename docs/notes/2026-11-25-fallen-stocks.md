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
