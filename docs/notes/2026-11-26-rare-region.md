# The run-up labels, fundamentals without price, and the rare region (2026-11-26 and 27, decisions 78 to 80)

Rewritten for readability on 2026-11-27. The numbers are unchanged.

## What this note is about

On 2026-11-26 Carter asked for a second round of experiments. He wanted
three things tried.

1. **New labels.** A stock that rose 50% without ever falling 30%; a
   stock that rose 75%; and a stock that either earned 20% a year or
   fell no further than the S&P 500 did. He asked for other values and
   horizons as well.
2. **Feature sets built from fundamentals.** Sets that lean less on the
   rank columns and leave out volume and momentum, so that the models
   work from financial statements. He was especially interested in the
   new columns that describe a stock's own history, such as the
   five-year z-score of return on equity or revenue against its
   five-year peak, when they sit beside other fundamentals.
3. **A way to find the rare region.** His concern was that a model
   given every column picks the dominant ones (momentum, size,
   volatility) and never finds the columns that separate a small group
   of stocks: those with a strong record that have fallen hard and
   recover within a few years. He asked for a plan to train a model on
   that region if features and labels were not enough.

Decision 78 holds the plan for the labels and feature sets, decision 79
the plan for the region, and decision 80 the verdict. This note holds
the tables and the reading of each sweep.

## How to read the tables

Every number comes from the run ledger
(`experiments/ledger/claude-value-ml-models.csv`) on `dataset_v1.5.1`.
Unless a section says otherwise, the model is the candidate's forest
configuration (decision 24) at seed 23, trained on every row and read
inside the liquidity floor (three-month dollar volume of 100,000 or
more) on the same-size screen. The screen buys the ten highest-scored
stocks each quarter, at most two per sector, and compares them with
stocks of the same size (the same twentieth of the market-cap ranking).

The terms used throughout:

- **Cell C** is the label "not a loser": a three-year CAGR of zero or
  more and never 30% below the entry price. It is the candidate's
  label.
- **The control** is the candidate's forest in cell C on the 112 rank
  columns that `dataset_v1.4.1` had. Every arm is paired with it by
  test year.
- **p@20** is the share of each year's top 20 that met the label.
  **Base** is the share of all test rows that met it.
- **Lead** is the mean three-year CAGR of the screen's picks minus the
  mean for their same-size peers, averaged over the test years.
- **Gain** is an arm's lead minus the control's lead, year by year. The
  table gives the mean gain, its t-statistic over the paired years, and
  the number of years the arm was ahead.
- **Losers** is the share of picks whose three-year CAGR was negative.
  **Lost half** is the share whose price fell 50% or more from entry.
  **Doubled** is the share whose three-year CAGR was 26% or more, which
  doubles the money in three years.
- **The screen rule** (decision 74.4) says when an arm beats the
  control: its gain in lead is positive at about two standard errors,
  it is ahead in ten or more of the sixteen years, neither half of the
  period is worse than its noise, and the same holds for losers. An arm
  that passes goes on to three seeds and then a backtest.
- **Feature sets** are named fs0, fs1 and so on. Each section defines
  the sets it uses, because the numbering differs between sweeps.
- **The region** (decision 79) is the set of liquid stocks 40% or more
  below their five-year high whose operating cash flow was positive in
  at least 18 of the last 20 quarters. **Region share** is the share of
  a selection's picks that sit inside it.

The test years are 2005 to 2020 unless a section says otherwise.

## Sweep A: six labels and five feature sets (`forest_fund_labels_3y`, 30 runs)

The feature sets in this sweep:

- **fs0**: the 112 rank columns of `dataset_v1.4.1`. This is the
  control's set.
- **fs1**: the 193 raw fundamental columns. No technical, event,
  classification or metadata columns, so nothing about price, size,
  volume or volatility.
- **fs2**: the rank columns without the 15 technical ranks, plus the 28
  columns that upstream ships without a rank (history fractions, the
  dividend record, five-year percentiles). 162 columns.
- **fs3**: a compact set of 74 raw columns describing the stock's own
  history: the fundamental-history and relative-value families plus 31
  named fundamentals.
- **fs4**: fs3 plus three columns that place the price against the
  stock's own past (distance from the five-year high, distance from the
  52-week high, price against the five-year average). 77 columns.

The labels, with the shorthand used in the tables: cell C; "a real
gain without a crash" (CAGR of 15% or more, never 30% down); Carter's
union label (CAGR of 20% or more, or a drawdown no deeper than the S&P
500's); "upside without a crash" (a run-up of 50%, never 30% down);
"doubled without a crash" (a run-up of 100%, never 40% down); and "a
run-up of 75%".

| label | set | p@20 | base | lead | gain (t, years ahead of 16) | losers | lost half | doubled | picks' CAGR | peers' CAGR |
|---|---|---|---|---|---|---|---|---|---|---|
| cell C | fs0 | 0.747 | 0.428 | +0.029 | control | 0.167 | 0.077 | 0.052 | 0.096 | 0.067 |
| | fs1 | 0.656 | | +0.025 | −0.004 (−0.5, 7) | 0.234 | 0.170 | 0.058 | 0.071 | 0.046 |
| | fs2 | 0.678 | | +0.029 | +0.000 (0.1, 6) | 0.223 | 0.162 | 0.066 | 0.079 | 0.050 |
| | fs3 | 0.644 | | +0.021 | −0.008 (−0.8, 8) | 0.259 | 0.194 | 0.059 | 0.063 | 0.042 |
| | fs4 | 0.653 | | +0.019 | −0.010 (−1.0, 6) | 0.238 | 0.180 | 0.055 | 0.064 | 0.044 |
| a real gain without a crash | fs0 | 0.244 | 0.211 | +0.022 | −0.006 (−0.9, 7) | 0.247 | 0.158 | 0.067 | 0.070 | 0.048 |
| | fs1 | 0.206 | | −0.022 | −0.051 (−2.8, 3) | 0.403 | 0.359 | 0.116 | −0.002 | 0.020 |
| | fs2 | 0.341 | | +0.032 | +0.003 (0.5, 9) | 0.259 | 0.205 | 0.097 | 0.078 | 0.046 |
| | fs3 | 0.194 | | −0.043 | −0.072 (−3.4, 3) | 0.427 | 0.394 | 0.125 | −0.028 | 0.015 |
| | fs4 | 0.194 | | −0.047 | −0.075 (−4.0, 2) | 0.439 | 0.394 | 0.114 | −0.033 | 0.014 |
| the union label | fs0 | 0.656 | 0.335 | +0.009 | −0.020 (−3.1, 2) | 0.142 | 0.067 | 0.039 | 0.066 | 0.056 |
| | fs1 | 0.456 | | +0.003 | −0.026 (−1.7, 3) | 0.319 | 0.250 | 0.091 | 0.038 | 0.035 |
| | fs2 | 0.459 | | +0.029 | −0.000 (0.0, 8) | 0.253 | 0.173 | 0.072 | 0.083 | 0.054 |
| | fs3 | 0.406 | | −0.004 | −0.033 (−2.5, 2) | 0.352 | 0.291 | 0.092 | 0.023 | 0.027 |
| | fs4 | 0.434 | | −0.001 | −0.030 (−1.7, 3) | 0.320 | 0.280 | 0.091 | 0.025 | 0.026 |
| upside without a crash | fs0 | 0.431 | 0.305 | +0.025 | −0.004 (−0.6, 7) | 0.244 | 0.164 | 0.078 | 0.077 | 0.053 |
| | fs1 | 0.369 | | −0.009 | −0.038 (−1.9, 4) | 0.359 | 0.309 | 0.100 | 0.017 | 0.026 |
| | fs2 | 0.478 | | +0.036 | +0.007 (0.8, 9) | 0.234 | 0.177 | 0.077 | 0.081 | 0.045 |
| | fs3 | 0.375 | | −0.009 | −0.038 (−2.2, 5) | 0.370 | 0.328 | 0.106 | 0.013 | 0.022 |
| | fs4 | 0.362 | | −0.023 | −0.051 (−3.0, 5) | 0.391 | 0.338 | 0.094 | −0.000 | 0.022 |
| doubled without a crash | fs0 | 0.253 | 0.188 | +0.110 | +0.081 (5.3, 15) | 0.381 | 0.356 | 0.192 | 0.069 | −0.041 |
| | fs1 | 0.241 | | −0.037 | −0.066 (−1.7, 4) | 0.530 | 0.566 | 0.172 | −0.072 | −0.034 |
| | fs2 | 0.288 | | +0.020 | −0.009 (−0.4, 7) | 0.452 | 0.452 | 0.189 | 0.011 | −0.009 |
| | fs3 | 0.222 | | −0.048 | −0.077 (−2.1, 4) | 0.514 | 0.558 | 0.175 | −0.079 | −0.031 |
| | fs4 | 0.216 | | −0.066 | −0.095 (−2.8, 4) | 0.534 | 0.573 | 0.152 | −0.096 | −0.031 |
| a run-up of 75% | fs0 | 0.419 | 0.361 | +0.026 | −0.003 (−0.3, 9) | 0.691 | 0.716 | 0.098 | −0.145 | −0.171 |
| | fs1 | 0.488 | | −0.005 | −0.034 (−0.9, 7) | 0.531 | 0.589 | 0.188 | −0.076 | −0.071 |
| | fs2 | 0.547 | | +0.033 | +0.004 (0.2, 7) | 0.556 | 0.572 | 0.183 | −0.049 | −0.082 |
| | fs3 | 0.488 | | −0.047 | −0.076 (−1.6, 7) | 0.555 | 0.605 | 0.181 | −0.099 | −0.053 |
| | fs4 | 0.509 | | −0.067 | −0.096 (−2.2, 4) | 0.575 | 0.639 | 0.180 | −0.122 | −0.055 |

What the picks' price paths looked like, as fold means. The control's
picks had a realized volatility of 0.248 against 0.360 for their peers,
and a drawdown of 0.175 against 0.294. The picks of "a run-up of 75%"
on fs0 had a volatility of 0.848 against 0.884 and a drawdown of 0.644
against 0.634. The picks of "doubled without a crash" on fs0 had a
volatility of 0.501 against 0.648, a run-up of 1.008 against 1.171 and
a drawdown of 0.407 against 0.499.

The year-by-year record of "doubled without a crash" on fs0 beside the
control:

| year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| control's lead | .002 | .058 | .048 | .040 | .060 | .040 | .006 | .019 | .051 | .067 | .022 | .029 | .040 | .000 | −.017 | −.002 |
| doubled's lead | .092 | .080 | .135 | .091 | .078 | .117 | .131 | .132 | .156 | .161 | .159 | .055 | .030 | .011 | .101 | .235 |
| control's picks' CAGR | .010 | −.042 | −.013 | .087 | .217 | .169 | .149 | .154 | .111 | .125 | .090 | .125 | .102 | .113 | .072 | .064 |
| doubled's picks' CAGR | .041 | −.146 | −.084 | .072 | .205 | .122 | .162 | .185 | .069 | .093 | .120 | .034 | −.050 | .020 | .069 | .192 |
| control's peers: share losing | .43 | .66 | .60 | .35 | .16 | .16 | .14 | .17 | .27 | .27 | .28 | .22 | .33 | .23 | .24 | .30 |
| doubled's peers: share losing | .53 | .75 | .73 | .49 | .33 | .44 | .40 | .36 | .55 | .52 | .47 | .45 | .59 | .47 | .51 | .52 |

Which columns the forests split on most (mean importance over folds,
the top three):

| forest | first | second | third | share of the top ten |
|---|---|---|---|---|
| cell C, fs0 (the control) | `vol_12m_rank` 0.198 | `vol_36m_rank` 0.126 | `ocf_trend_4q_rank` 0.067 | 0.66 |
| cell C, fs1 | `ocf_yield` 0.105 | `ocf_trend_4q` 0.078 | `ocf_positive_frac_4q` 0.049 | 0.49 |
| cell C, fs2 | `ocf_trend_4q_rank` 0.091 | `ocf_consistency_4q_rank` 0.075 | `ocf_trend_8q_rank` 0.057 | 0.44 |
| doubled without a crash, fs0 | `ret_1m_rank` 0.128 | `dist_52w_high_rank` 0.060 | `ret_6m_rank` 0.059 | 0.44 |
| a run-up of 75%, fs0 | `ret_1m_rank` 0.207 | `max_ret_21d_rank` 0.129 | `dist_52w_high_rank` 0.102 | 0.69 |
| the union label, fs0 | `vol_12m_rank` 0.163 | `beta_12m_rank` 0.122 | | 0.69 |

### What sweep A showed, against the predictions of decision 78.5

- **Prediction (a) held.** The raw fundamentals (fs1) in cell C scored
  0.091 below fs0 on p@20, inside the predicted range of 0.08 to 0.12.
  Their lead was within 0.02 of fs0's (the difference is −0.004) and
  their share of losers was 6.7 points higher, a little above the
  predicted 3 to 6. The rival prediction, the same lead with no more
  losers, is ruled out.
- **Prediction (b) held in part.** The compact history sets (fs3 and
  fs4) were no better than fs1 on any label. Adding the three fall
  columns (fs4) did not help: in cell C fs4 scored −0.010 against fs3's
  −0.008.
- **Prediction (c) held for "a run-up of 75%" and failed for "doubled
  without a crash".** The 75% run-up label was learned as volatility.
  Its picks had a realized volatility of 0.848 against 0.248 for the
  control's picks, and they lost 14.5% a year. The "doubled without a
  crash" label was predicted to pick stocks like cell C's, and it did
  not. On fs0 that forest splits first on the one-month return and the
  distance from the 52-week high, so it is a short-term reversal
  screen. Its picks led their same-size peers by 0.081 a year more
  than the control's did (t 5.3, ahead in 15 of 16 years, in both
  halves), and 19% of them doubled against 5% of the control's. But
  38% of them lost money against 17%, 36% lost half their value against
  8%, and their mean CAGR was 0.069 against 0.096. In every year after
  2008 the peers of its picks lost money 33% to 59% of the time, where
  the control's peers lost 14% to 33% of the time. The lead is real,
  and it is a lead over stocks that lose. It fails the screen rule on
  losers.
- **Prediction (d) failed as written.** The union label's p@20 was 0.32
  above its base rate, not 0.10 or less. Its lead was 0.020 below cell
  C's (t −3.1, ahead in 2 years) and its share of losers 2.5 points
  lower (1.4 standard errors). It is a calmer, poorer version of cell C:
  its picks had a volatility of 0.190 and a CAGR of 0.066.
- **Prediction (f) held.** No fundamentals-only set passes the screen
  rule against the control. The best of them is fs2, the rank columns
  without the technical family plus the unranked history columns. In
  cell C it matches the control's lead exactly (ahead in 6 of 16 years)
  with 5.6 points more losers and twice the share losing half. On the
  three harder labels it is the only set that leads fs0: +0.032 against
  +0.022 on "a real gain without a crash", +0.036 against +0.025 on
  "upside without a crash", and +0.029 against +0.009 on the union
  label. Each of those leads is within noise of the control's, and each
  comes with 7 to 9 points more losers. Without the volatility ranks
  the forest builds itself on operating cash flow (its yield, trend and
  consistency), as the raw set does.

What this suggests, as hypotheses rather than measurements: the
control's advantage on losers comes from the volatility ranks. The
fundamental sets reach the same lead with more losers because they
cannot see which stocks are calm. The history columns do not add a lead
on their own. The run-up label with a drawdown cap finds a real lead,
carried by short-term reversal, among stocks that lose money.

## Sweep B: ten single-column rankings on the four new labels (`baseline_fund_labels_3y`, 40 runs)

A single-column ranking picks the same stocks whatever the label, so
its screen outcomes are one row per ranking. Only p@20 depends on the
label. Each ranking is paired by test year with the control.

| ranking (direction) | lead | lead 2005–12 | lead 2013–20 | gain (t, years ahead of 16) | losers | losers minus control's (years with fewer) | picks' CAGR | distinct stocks a year |
|---|---|---|---|---|---|---|---|---|
| 36-month volatility, low | +0.013 | −0.008 | +0.034 | −0.016 (−1.6, 6) | 0.173 | +0.006 (8) | 0.071 | 17.1 |
| 12-month volatility, low | −0.021 | −0.006 | −0.036 | −0.050 (−2.5, 1) | 0.239 | +0.072 (3) | 0.026 | 24.0 |
| conservative score, high | +0.031 | +0.027 | +0.035 | +0.002 (0.3, 7) | 0.238 | +0.070 (4) | 0.090 | 28.8 |
| return on capital, high | +0.008 | +0.019 | −0.002 | −0.020 (−1.3, 7) | 0.350 | +0.183 (0) | 0.043 | 26.2 |
| 12-month momentum, high | −0.100 | −0.116 | −0.083 | −0.129 (−7.1, 1) | 0.659 | +0.492 (0) | −0.142 | 29.9 |
| earnings yield, high | −0.009 | −0.032 | +0.014 | −0.038 (−1.5, 8) | 0.569 | +0.402 (0) | −0.096 | 25.2 |
| five-year average earnings yield, high | −0.029 | −0.053 | −0.005 | −0.058 (−1.4, 6) | 0.612 | +0.445 (0) | −0.125 | 21.4 |
| market cap, high | +0.023 | +0.003 | +0.043 | −0.005 (−0.5, 7) | 0.183 | +0.016 (4) | 0.107 | 10.9 |
| distance from five-year high, near the high | +0.013 | +0.018 | +0.009 | −0.016 (−1.0, 6) | 0.256 | +0.089 (3) | 0.051 | 36.6 |
| five-year z-score of return on equity, high | +0.025 | +0.033 | +0.017 | −0.004 (−0.4, 11) | 0.312 | +0.145 (0) | 0.062 | 32.4 |

The precision of the rankings on each label, beside the best forest of
sweep A on that label:

| label | base | best rankings | forest on fs0 | forest on fs2 |
|---|---|---|---|---|
| a real gain without a crash | 0.211 | market cap 0.403, conservative score 0.341 | 0.244 | 0.341 |
| the union label | 0.335 | market cap 0.550, 36-month volatility 0.528, distance from high 0.528 | 0.656 | 0.459 |
| doubled without a crash | 0.188 | market cap 0.269, return on capital 0.234 | 0.253 | 0.288 |
| a run-up of 75% | 0.361 | five-year earnings yield 0.475, earnings yield 0.428 | 0.419 | 0.547 |

### What sweep B showed

- No single-column ranking passes the screen rule against the control.
  The market-cap ranking, which buys the largest liquid stocks (10.9
  distinct names a year), matches the control on both outcomes within
  noise: its lead is 0.005 lower and its losers 1.6 points higher. It
  earns more in absolute terms (0.107 against 0.096) because its peers
  are the largest stocks. It is a different portfolio, a basket of the
  biggest companies, not a selection. The conservative-score ranking
  matches the control's lead with 7 points more losers. Every other
  ranking is 7 to 49 points behind on losers.
- "Big momentum is good" is false in this data. The 12-month momentum
  ranking loses 14.2% a year, trails its same-size peers by 10 points a
  year in both halves, and has 66% losers. The forests never learned
  that momentum is good. What they learned is that calm and size are
  good.
- The ranking on the five-year z-score of return on equity, a strong
  record against the stock's own past, is ahead of the control on lead
  in 11 of 16 years (the mean gain, −0.004, is within noise) and 14.5
  points worse on losers. The history columns carry a lead and not a
  filter against losers. Sweep A's fs2 showed the same pattern.
- On "a real gain without a crash" the market-cap ranking (0.403) beats
  every forest on precision (fs0 0.244, fs2 0.341). On "doubled without
  a crash" its 0.269 is above the fs0 forest's 0.253. On those two
  labels the forests do not beat a trivial ranking as predictors. Cell
  C and the union label are the labels where a forest adds precision.

## Sweep C: the five-year horizon (`forest_fund_labels_5y`, 12 runs, folds 2007 to 2018)

The feature sets here are fs0 (the 112 old ranks), fs1 (the 193 raw
fundamentals) and fs2 (sweep A's fs4, the compact history set plus the
fall columns). The control is cell C's five-year twin on fs0: lead over
same-size peers on the five-year CAGR +0.032 a year, losers 0.092, p@20
0.788, 27.5 distinct stocks a year. The pairing is by test year over 12
years, with halves 2007 to 2012 and 2013 to 2018.

| label | set | p@20 | base | lead | gain (t, years ahead of 12) | losers | lost half | picks' CAGR | peers' CAGR |
|---|---|---|---|---|---|---|---|---|---|
| cell C at five years | fs0 | 0.788 | 0.425 | +0.032 | control | 0.092 | 0.065 | 0.105 | 0.073 |
| | fs1 | 0.638 | | +0.008 | −0.024 (−2.6, 4) | 0.240 | 0.277 | 0.049 | 0.041 |
| | fs2 | 0.638 | | +0.008 | −0.024 (−3.5, 2) | 0.269 | 0.285 | 0.043 | 0.036 |
| a real gain without a crash | fs0 | 0.171 | 0.170 | +0.024 | −0.008 (−1.0, 5) | 0.227 | 0.219 | 0.065 | 0.041 |
| | fs1 | 0.192 | | −0.039 | −0.071 (−6.6, 0) | 0.394 | 0.417 | −0.025 | 0.013 |
| | fs2 | 0.175 | | −0.040 | −0.072 (−5.9, 1) | 0.404 | 0.429 | −0.035 | 0.005 |
| doubled without a crash | fs0 | 0.333 | 0.262 | +0.032 | −0.000 (−0.1, 5) | 0.215 | 0.227 | 0.075 | 0.044 |
| | fs1 | 0.279 | | −0.037 | −0.069 (−4.5, 0) | 0.390 | 0.438 | −0.028 | 0.009 |
| | fs2 | 0.267 | | −0.035 | −0.067 (−4.9, 1) | 0.406 | 0.456 | −0.029 | 0.005 |
| a run-up of 100% | fs0 | 0.438 | 0.371 | +0.103 | +0.071 (4.5, 11) | 0.483 | 0.548 | −0.019 | −0.122 |
| | fs1 | 0.438 | | −0.096 | −0.128 (−5.6, 1) | 0.588 | 0.627 | −0.139 | −0.043 |
| | fs2 | 0.429 | | −0.103 | −0.135 (−6.2, 1) | 0.590 | 0.640 | −0.144 | −0.041 |

### What sweep C showed

- Prediction 78.5(e) held: the five-year results order the sets and
  labels as the three-year results did. The control is the only arm
  that leads on both outcomes. In cell C every fundamentals-only set is
  0.024 a year behind it on lead and 15 to 18 points behind on losers.
  On the harder labels the fundamentals-only sets are 7 points a year
  behind.
- At five years, "doubled without a crash" on fs0 is no longer a
  reversal screen with a lead over losing stocks. It matches the
  control's lead exactly (ahead in 5 of 12 years) with 12 points more
  losers. The run-up label without a drawdown cap repeats the
  three-year pattern: a lead of 0.071 over the control (t 4.5, ahead in
  11 of 12 years), 48% losers, and picks that lose money.
- The compact history set with the fall columns is the worst set at
  five years as at three. The history columns beside a handful of
  fundamentals do not make a selection.

## The rare-region program (decision 79)

The region is defined on feature columns, so that a weight or a
universe can name it: inside the liquidity floor, 40% or more below the
five-year high (`dist_5y_high <= -0.4`) and operating cash flow
positive in 18 of the last 20 quarters (`ocf_positive_frac_20q >= 0.9`).
To measure where a selection's picks come from, the harness gained a
`region` field on the pick screen. It reports the share of the picks,
of their peers and of all test rows that sit inside the region, as the
pick outcome `in_region`.

The feature sets in every sweep of this program are:

- **fs0**: the 112 old ranks, the control's set.
- **fs1**: sweep A's fs2, the rank columns without the technical family
  plus the 28 unranked history columns (162). It replaced the raw set,
  which sweep A placed last.
- **fs2**: sweep A's fs4, the compact history set plus the three fall
  columns (77).

### How much of the region the control buys (`forest_fund_control_region_3y`, 1 run)

The control was run again with the region declared on the screen. Its
model-side numbers reproduced sweep A's run on every fold: p@20,
PR-AUC, the screen's CAGR, the peers' CAGR, losers and distinct stocks
are identical, and one Brier score differs in the fifteenth digit. The
region shares by test year:

| year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| the control's picks | 0 | 0 | 0 | .10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | .006 |
| their same-size peers | .11 | .08 | .06 | .23 | .39 | .20 | .14 | .15 | .06 | .02 | .06 | .09 | .06 | .08 | .09 | .10 | .120 |
| all liquid test rows | .12 | .10 | .09 | .25 | .39 | .25 | .21 | .20 | .10 | .07 | .11 | .15 | .12 | .12 | .15 | .19 | .163 |

The candidate's forest buys almost nothing from the region: four picks
in 2008 and none in any other year, while the region is 7% to 39% of
the liquid rows and 2% to 39% of the picks' own size band. Prediction
79(a) said the control's share would be below 0.15, and it is 0.006.
The rival prediction for an emphasized arm therefore needed a region
share of 0.10 or more.

### Emphasis weights (`forest_emph3_fund_3y` and `forest_emph10_fund_3y`, 9 runs each)

In these sweeps the candidate's forest was trained on every row, with
the training rows inside the region given three times or ten times
their sample weight. Before the multiplier, the region holds none of
the training weight in fold 2005 (its columns need five years of
history), 1.4% in fold 2006, 4.9% in fold 2012 and 7.6% in fold 2020.
So at three times the region is at most a fifth of the training weight
in the late folds, and at ten times at most 45%.

Each arm is paired by test year with the same label and set in sweep A
without emphasis, which this section calls its twin (fs0 with sweep A's
fs0, fs1 with sweep A's fs2, fs2 with sweep A's fs4). The labels are
cell C, "a real gain without a crash" and "doubled without a crash".

| label | set | weight | p@20 | lead | gain against the twin (t, years ahead) | losers (twin's) | picks' CAGR | region share |
|---|---|---|---|---|---|---|---|---|
| cell C | fs0 | ×3 | .772 | +.027 | −.002 (−0.9, 6 of 16) | .166 (.167) | .096 | .006 |
| cell C | fs0 | ×10 | .756 | +.023 | −.006 (−1.4, 7 of 16) | .161 (.167) | .093 | .006 |
| cell C | fs1 | ×3 | .700 | +.031 | +.001 (0.6, 9 of 16) | .206 (.223) | .084 | .061 |
| cell C | fs1 | ×10 | .700 | +.029 | −.001 (−0.1, 6 of 16) | .192 (.223) | .088 | .056 |
| cell C | fs2 | ×3 | .678 | +.019 | −.000 (−0.0, 6 of 16) | .252 (.238) | .062 | .030 |
| cell C | fs2 | ×10 | .678 | +.004 | −.015 (−1.8, 4 of 16) | .270 (.238) | .051 | .045 |
| a real gain without a crash | fs0 | ×3 | .259 | +.027 | +.004 (0.9, 7 of 16) | .230 (.247) | .081 | .044 |
| a real gain without a crash | fs0 | ×10 | .266 | +.017 | −.005 (−1.0, 6 of 16) | .238 (.247) | .077 | .050 |
| a real gain without a crash | fs1 | ×3 | .356 | +.033 | +.001 (0.2, 8 of 16) | .258 (.259) | .079 | .095 |
| a real gain without a crash | fs1 | ×10 | .334 | +.029 | −.003 (−0.6, 7 of 16) | .248 (.259) | .078 | .078 |
| a real gain without a crash | fs2 | ×3 | .169 | −.046 | +.001 (0.0, 8 of 16) | .436 (.439) | −.029 | .605 |
| a real gain without a crash | fs2 | ×10 | .175 | −.048 | −.001 (−0.1, 7 of 16) | .464 (.439) | −.030 | .667 |
| doubled without a crash | fs0 | ×3 | .219 | +.064 | −.046 (−5.6, 1 of 16) | .409 (.381) | .052 | .266 |
| doubled without a crash | fs0 | ×10 | .184 | +.031 | −.079 (−5.8, 1 of 16) | .361 (.381) | .056 | .141 |
| doubled without a crash | fs1 | ×3 | .259 | +.023 | +.003 (0.2, 10 of 16) | .414 (.452) | .036 | .438 |
| doubled without a crash | fs1 | ×10 | .278 | +.011 | −.009 (−0.5, 8 of 16) | .372 (.452) | .038 | .359 |
| doubled without a crash | fs2 | ×3 | .222 | −.059 | +.007 (0.8, 7 of 16) | .536 (.534) | −.091 | .838 |
| doubled without a crash | fs2 | ×10 | .262 | −.050 | +.016 (1.4, 10 of 16) | .538 (.534) | −.085 | .852 |

Against the control, the cell-C forest on fs0 at three times the weight
has a lead 0.002 lower (t −0.9, ahead in 6 of 16 years; 0.001 lower in
2005 to 2012 and 0.003 lower in 2013 to 2020) and 0.2 points fewer
losers. Its region share is 0.006: zero in every year except 2008,
where it is 0.10, which is exactly the control's pattern. At ten times
the weight the lead is 0.006 lower (t −1.4, ahead in 7 of 16; 0.011
lower in the first half and the same in the second), losers are 0.6
points fewer, and the region share is again 0.006.

The importances tell the same story. At three times the weight the
cell-C forest on fs0 splits on the same columns as the control to the
third digit: `vol_12m_rank` 0.196 against the control's 0.198,
`vol_36m_rank` 0.131 against 0.126, then `ocf_trend_4q_rank` and
`conservative_score_rank`. At ten times the weight two of the region's
own columns move into third and fourth place, `dist_5y_high_rank` at
0.078 and `price_vs_5y_avg_rank` at 0.065. They win splits they never
won before, and the picks' region share stays at 0.006. The forest for
"doubled without a crash" on fs0 keeps `ret_1m_rank` first (0.122
against 0.128 without emphasis) and adds `price_vs_5y_avg_rank` at
0.046 and `dist_5y_high_rank` at 0.040. The compact-set forest for "a
real gain without a crash" at ten times the weight splits on
`ocf_yield` (0.156), `ocf_yield_5y_avg` (0.129) and
`earnings_yield_5y_peak` (0.064). No history z-score reaches 0.03.

### What the emphasis sweeps showed, against decision 79

- **Prediction 79(a) held for the threefold weight, and Carter's rival
  prediction failed.** The lead moved by −0.002, losers by −0.2 points
  and the region share by nothing, where the rival needed a region
  share 10 points higher and a lead 0.01 higher. The region's columns
  did not win splits at three times the weight. For the tenfold weight
  the prediction was half right. The lead moved further in the same
  direction (−0.006), but losers fell 0.6 points instead of rising 3
  points or more. The prediction assumed that with the region near 45%
  of the late folds' training weight the forest would come to treat
  fallen stocks as the normal case. It did not. It found the region's
  columns and used them to score the region's rows low, so its picks
  stayed where the control's are.
- **Prediction 79(b) held in cell C and was right for the wrong reason
  on "doubled without a crash".** In cell C every change against the
  twin is inside noise (every |t| is 1.8 or less). On "doubled without a
  crash" the lead was predicted to fall on fs1 and fs2. It fell on fs0
  instead, by 0.046 a year at three times the weight and 0.079 at ten
  times (t −5.6 and −5.8, ahead in 1 year of 16), while the fs1 and fs2
  arms moved inside noise. fs0 is the set that holds the reversal
  columns that carry this label. With emphasis the forest spends splits
  on the region's own columns (`price_vs_5y_avg_rank`,
  `dist_5y_high_rank`) and buys more of the region (27% of its picks at
  three times the weight). Its losers stay at 36% to 41%.
- **Where a forest does buy the region, the region loses.** The compact
  set on the two harder labels puts 60% to 85% of its picks inside the
  region, with or without emphasis. Those arms are the worst in the
  table: a lead of −0.05 to −0.06 a year, 44% to 54% losers, 39% to 58%
  of picks losing half, and a mean CAGR of −0.03 to −0.09. Emphasis
  moves them by less than noise. These arms are not finding the stocks
  that recover. They are finding the region.
- **Emphasis is not a way in.** Of the 18 arms, 16 move against their
  twin by less than two standard errors. The two that move are the
  reversal forests, and they move down. No emphasis arm passes the
  screen rule against the control. The closest is fs1 at three times
  the weight in cell C: a lead of +0.031 (0.002 above the control's,
  ahead in 8 of 16 years) with 3.9 points more losers.

### The region as a universe (`forest_region_universe_3y`, 6 runs, folds 2008 to 2020)

Here the candidate's forest was trained and read on the region's rows
alone, by declaring the region as the run's universe. The peers are
now in-region stocks of the same size. The training weight inside the
region runs from 588 (fold 2008) to 2,810 (fold 2020), against 12,692
to 37,097 for the whole liquid set, and there are 900 to 4,350 test
rows a year. The forest configuration is unchanged, so its leaves of 72
rows are large against these fits.

First, what the region's rows did as a group, against all liquid rows.
These are means over all test rows, 2008 to 2020:

| rows | rows a year | cell C rate | mean CAGR | median CAGR | losers | lost half | doubled | run-up of 100% | volatility |
|---|---|---|---|---|---|---|---|---|---|
| the region | 2,144 | .405 | .019 | .048 | .407 | .403 | .185 | .335 | .552 |
| all liquid rows | 12,217 | .457 | .034 | .063 | .371 | .338 | .159 | .298 | .497 |

By year, the region's mean CAGR was .090, .184, .095, .106 and .096
from 2008 to 2012. From 2013 to 2018 it was −.078, −.117, −.042, −.024,
−.186 and −.051. In 2019 it was .021 and in 2020 .147. The liquid set's
mean CAGR ranged from −.042 to +.145 over the same years and never fell
below −.042 after 2007. The region has more doublers and more losers
than the market: wider tails and a lower mean. It pays after a crash
(2009, 2020) and loses through a long rise (2013 to 2018). It behaves
like a bet on the market's recovery, not like a pool of mispriced
survivors.

Then, what the forest found inside it:

| label | set | p@20 (base) | lead over in-region peers (years ahead of 13) | losers (peers') | picks' CAGR (peers') | doubled (peers') | stocks a year |
|---|---|---|---|---|---|---|---|
| cell C | fs0 | .650 (.405) | +.040 (10) | .331 (.403) | .062 (.022) | .117 (.145) | 30.5 |
| cell C | fs1 | .569 | +.044 (8; 0.004 above fs0, t 0.2) | .331 (.396) | .071 (.027) | .152 (.151) | 28.7 |
| cell C | fs2 | .527 | −.011 (2; 0.051 below fs0, t −3.5) | .387 (.400) | .018 (.029) | .092 (.149) | 25.0 |
| doubled without a crash | fs0 | .296 (.237) | +.051 (9) | .344 (.411) | .062 (.011) | .200 (.173) | 31.7 |
| doubled without a crash | fs1 | .323 | +.039 (8; 0.002 below fs0) | .350 (.411) | .054 (.016) | .192 (.173) | 29.0 |
| doubled without a crash | fs2 | .285 | −.070 (0.110 below fs0, t −2.5) | .527 (.461) | −.087 (−.017) | .194 (.187) | 26.2 |

Year by year, the cell-C forest on fs0 led its in-region peers by .010,
−.010, .020, .092, .049, .102, .038, .091, .029, .139, .059, −.016 and
−.078 from 2008 to 2020. Its share of losers was .30, .23, .18, .13,
.18, .30, .63, .35, .35, .58, .53, .35 and .23. The lead is largest in
the years the region lost most (2013, 2015 and 2017), because the forest
picks the in-region stocks that fall least. Even so, its picks lost
money on average in 2014 and 2017.

Compared with the control's picks over the same 13 years: the control's
picks earned .121 a year with 11% losers. The in-region forest's picks
earned .062, which is .059 less (t −3.4, ahead in 2 of 13 years), with
33% losers, 22 points more (t 5.0). The in-region picks doubled more
often than the control's (.117 against .063), and so did their peers
(.145 against .136). The doublers belong to the region, not to the
forest's selection.

The importances inside the region: on fs0 `dist_5y_high_rank` 0.161,
`price_vs_5y_avg_rank` 0.095, `vol_12m_rank` 0.072, `vol_36m_rank`
0.062 and `dist_52w_high_rank` 0.055. The forest sorts first on how far
a stock has fallen and then on how calm it is. On fs1 the top columns
are `sales_yield_vs_5y_median_rank` 0.073,
`tangible_book_to_market_vs_5y_median_rank` 0.065,
`earnings_yield_5y_peak_rank` 0.039 and `ocf_yield_5y_avg_rank` 0.029.
These are the valuation-against-own-history columns Carter asked about.
Inside the region they lead the forest, and that forest's lead (+.044)
matches fs0's (+.040) at the same share of losers, with a lower p@20
(.569 against .650).

### What the universe sweep showed, against decision 79

- **Prediction 79(c) held on every count except a tie.** The cell-C
  forest on fs0 led its in-region peers in 10 of 13 years (the
  prediction said 10 or more), its losers were .331 (the prediction
  said .30 or more), and neither fs1 nor fs2 beat fs0 inside the region
  (fs1 is 0.004 ahead on lead, inside noise, with a lower p@20; fs2 is
  0.051 behind, t −3.5). The emphasis arm for the same label had fewer
  losers than the universe arm in 12 of the 13 shared years and the
  same share (.225) in 2020, where the prediction said every year.
- **This is decision 63's fallen-stocks result again, on a different
  region.** Inside a pool of fallen stocks the forest finds the ones
  that fall least, by how far they have fallen and how calm they are,
  and leads its in-region peers by 4 points a year. The pool itself
  earns 2% a year with 40% losers, so the picks earn 6% with 33%
  losers: half the control's return with three times its losers. The
  forest trained inside the region does not find the doublers. Its
  picks double less often than their peers.
- **The own-history valuation columns are real inside the region, and
  they are not enough.** On fs1 they are the top splits and they carry
  fs0's lead. This is the first place in the program where the history
  columns bring a forest to the same lead as the price columns. It is a
  lead over a peer group that loses money.
- **What the region is.** Its rows earn a mean three-year CAGR of .019
  against .034 for all liquid rows, with more losers, more halvings and
  more doublers. It earns in 2009 to 2012 and 2020 and loses every year
  from 2013 to 2018. "A strong history, a steep fall, a recovery"
  describes the region's good years, not its rows. The recovery is the
  market's. Whether a model can tell the recovering rows from the rest
  of the region is what the next three sweeps test, on all rows.

### Forests that see 5% of the columns at each split (`forest_subspace_fund_3y`, 12 runs)

The candidate's forest considers 20% of the columns at each split.
These forests consider 5%: 5 of 112 columns on fs0, 8 of 162 on fs1, 3
of 77 on fs2. The idea is that a weak column must be used when the
strong ones are absent from a split, so a column that only matters in
a small region gets a chance. Two shapes were run: depth 8 with leaves
of 30 rows, and the candidate's depth 4 with leaves of 72 rows. The
forests were trained on every row and read on the same-size screen,
paired with the control and, on "doubled without a crash", with the
sweep A run on the same set.

| label | set | shape | p@20 | lead | gain against the control (t, years ahead of 16) | losers (change against the control) | region share | picks' CAGR |
|---|---|---|---|---|---|---|---|---|
| cell C | fs0 | depth 8 | .722 | +.028 | −.001 (−0.2, 7) | .189 (+2.2) | .009 | .092 |
| cell C | fs0 | depth 4 | .634 | +.021 | −.008 (−1.3, 7) | .194 (+2.7) | .022 | .087 |
| cell C | fs1 | depth 8 | .681 | +.023 | −.006 (−0.8, 7) | .238 (+7.0) | .058 | .077 |
| cell C | fs1 | depth 4 | .578 | +.024 | −.005 (−0.5, 4) | .228 (+6.1) | .072 | .077 |
| cell C | fs2 | depth 8 | .650 | +.007 | −.022 (−2.4, 3) | .244 (+7.7) | .033 | .056 |
| cell C | fs2 | depth 4 | .622 | +.010 | −.019 (−2.8, 5) | .252 (+8.4) | .030 | .059 |
| doubled without a crash | fs0 | depth 8 | .244 | +.106 | +.077 (3.8, 15) | .412 (+24.5) | .339 | .055 |
| doubled without a crash | fs0 | depth 4 | .244 | +.101 | +.072 (4.8, 15) | .398 (+23.1) | .344 | .056 |
| doubled without a crash | fs1 | depth 8 | .303 | +.055 | +.026 (1.0, 10) | .419 (+25.2) | .459 | .041 |
| doubled without a crash | fs1 | depth 4 | .316 | +.053 | +.024 (0.9, 9) | .420 (+25.3) | .522 | .041 |
| doubled without a crash | fs2 | depth 8 | .231 | −.042 | −.071 (−2.0, 4) | .523 (+35.6) | .831 | −.073 |
| doubled without a crash | fs2 | depth 4 | .234 | −.069 | −.098 (−2.7, 4) | .538 (+37.0) | .859 | −.098 |

Against the sweep A runs on "doubled without a crash": the fs0 forest
at depth 8 has a lead 0.004 lower than sweep A's +.110 (t −0.5, ahead in
8 of 16), 3 points more losers, and a third of its picks inside the
region. The fs1 forests lead sweep A's fs2 run (+.020) by 0.035 and
0.033 (t 3.3 and 3.5, ahead in 14 and 13 of 16), with 42% losers against
45% and half their picks inside the region. The fs2 forest at depth 8
leads sweep A's fs4 run (−.066) by 0.024 (t 2.5).

The importances flatten, as the design intended. In cell C on fs0 the
top column is `vol_12m_rank` at 0.060 (depth 8) and 0.070 (depth 4),
against 0.198 in the control, and the order below it is the control's:
`vol_36m_rank`, `max_ret_21d_rank`, `conservative_score_rank`,
`ocf_trend_4q_rank`, `ocf_consistency_4q_rank`. On fs1 the top columns
are `ocf_consistency_4q_rank` 0.028, `ocf_consistency_8q_rank` 0.024,
`ocf_trend_4q_rank` 0.021 and `operating_margin_rank` 0.020: the
consistency of cash flow, with no history z-score or own-history yield
above 0.02. On "doubled without a crash" with fs0 the top columns are
`ret_1m_rank` 0.039, `dist_52w_high_rank` 0.025, `max_ret_21d_rank`
0.020 and `ret_6m_rank` 0.020: the one-month reversal again, found five
columns at a time.

### What the subspace sweep showed, against decision 79

- **Prediction 79(d) held in substance, with its p@20 clause split.**
  Depth 8 lost 0.025 of p@20 against the control, less than the
  predicted 0.03 to 0.06; depth 4 lost 0.113, more. The lead is inside
  noise of the control's (−0.001 and −0.008). Losers are 2.2 and 2.7
  points higher, inside the predicted 2 to 4. Depth 8 beats depth 4 on
  p@20 and not on the screen, as predicted. The rival prediction
  failed: the region shares are .009 and .022, against a requirement
  of 10 points above the control's.
- **Forcing weak columns into the splits does not change what the
  forest buys.** The same columns lead, each with a third of its former
  weight, and the picks are the control's kind of stock with a slightly
  higher share of losers. If a column discriminated inside the rare
  region, this is where it would have appeared: the volatility ranks
  are absent from 19 of every 20 splits. None did.
- **The one arm a subspace forest improved is "doubled without a crash"
  on fs1.** It leads the sweep A run by 0.035 a year with 3 points
  fewer losers, and half its picks are inside the region. It is still
  an arm with 42% losers whose picks earn 4% a year, against the
  control's 10%. It is not a candidate. It does suggest that this label
  has more to learn on fs1 than the candidate's forest shape reaches.
  That is recorded as an aside, not followed.
- No subspace arm passes the screen rule against the control on both
  outcomes.

### LightGBM with a tenth of the columns per tree (`lgbm_colsample_fund_3y`, 6 runs)

This sweep took the best LightGBM configuration of decision 76 (373
trees, 60 leaves, class weight 0.25) and set `colsample_bytree` to 0.1
instead of 0.806, so each tree sees a tenth of the columns. The labels
were cell C and "doubled without a crash" on fs0, fs1 and fs2. The
arms are read against the control and, on fs0, against the same
configuration at 0.806 in `lgbm_v151_tuned_nonloser_3y` (decision 76:
lead −.003, losers .183, p@20 .719).

| label | set | p@20 | lead | gain against the control (t, years ahead of 16) | losers (change against the control) | region share | picks' CAGR |
|---|---|---|---|---|---|---|---|
| cell C | fs0 | .669 | +.007 | −.022 (−2.6, 4) | .180 (+1.2) | .020 | .059 |
| cell C | fs1 | .716 | +.027 | −.002 (−0.3, 6) | .191 (+2.3) | .059 | .082 |
| cell C | fs2 | .631 | +.023 | −.006 (−0.7, 6) | .222 (+5.5) | .073 | .076 |
| doubled without a crash | fs0 | .234 | +.027 | −.002 (−0.1, 7) | .411 (+24.4) | .280 | .034 |
| doubled without a crash | fs1 | .175 | +.006 | −.023 (−0.9, 4) | .438 (+27.0) | .359 | .018 |
| doubled without a crash | fs2 | .253 | −.001 | −.029 (−1.0, 4) | .473 (+30.6) | .566 | −.012 |

The importances: in cell C on fs0, `conservative_score_rank` 0.080,
`dist_52w_high_rank` 0.049, `vol_36m_rank` 0.047 and `vol_12m_rank`
0.041. On fs1, `earnings_yield_5y_avg_rank` 0.035, `ocf_trend_4q_rank`
0.033, `marketcap_to_liabilities_rank` 0.022 and
`roa_variability_3y_rank` 0.022. This is the first model in the program
with a fundamentals-history column at the top. On "doubled without a
crash" with fs0, `ret_1m_rank` 0.035 and `dist_52w_high_rank` 0.032:
the reversal again, found weakly (a lead of +.027 against the forest's
+.110 on the same set).

### What the colsample sweep showed, against decision 79

- **The LightGBM clause of prediction 79(d) held on fs1 and fs2 and not
  on fs0.** On fs1 the lead is the control's (+.027, a gain of −.002
  inside noise) with 2.3 points more losers, which is the subspace
  forests' pattern. On fs2 the same holds with 5.5 points more losers.
  On fs0 the lead is 0.022 below the control's (t −2.6). Seeing a tenth
  of the columns lifted this configuration's lead from −.003 (at 0.806)
  to +.007 and no further. The rival prediction failed everywhere: the
  region shares are .02 to .07.
- **A boosted model that sees a tenth of the columns puts a history
  column first and still buys the control's stocks.** On fs1 the
  five-year average earnings yield is the top split, the lead matches
  the control's, losers are 2 points higher and the region share is
  .059. This is the best LightGBM lead on `dataset_v1.5.1` so far
  (decision 76's configurations ran from −.003 to +.006), and it fails
  the screen rule on both outcomes.
- No colsample arm passes the screen rule.

### The upper tail as a regression (`lgbm_quantile_fund_3y`, 6 runs)

These runs used LightGBM quantile regression on the three-year CAGR
itself, at quantiles 0.8 and 0.9 (400 trees, 15 leaves, learning rate
0.05). The score is the predicted 80th or 90th percentile of a stock's
three-year CAGR, so the model is asked where the large gains are rather
than where the average is. Precision is measured on the label "earned
20% a year" (base rate .198). The picks are read inside the liquidity
floor on the same-size screen, paired by year with the control.

| set | quantile | p@20 (base .198) | lead | gain against the control (t, years ahead of 16) | losers | lost half | doubled | volatility | picks' CAGR (peers') | region share |
|---|---|---|---|---|---|---|---|---|---|---|
| fs0 | 0.8 | .234 | −.001 | −.030 (−1.2, 7) | .523 | .553 | .200 | .707 | −.043 (−.042) | .584 |
| fs0 | 0.9 | .272 | −.010 | −.039 (−1.1, 4) | .542 | .592 | .219 | .791 | −.065 (−.055) | .641 |
| fs1 | 0.8 | .297 | +.025 | −.004 (−0.1, 7) | .480 | .527 | .216 | .706 | −.013 (−.038) | .530 |
| fs1 | 0.9 | .281 | −.018 | −.047 (−1.4, 5) | .522 | .562 | .205 | .830 | −.077 (−.059) | .473 |
| fs2 | 0.8 | .281 | −.068 | −.097 (−1.8, 5) | .597 | .650 | .205 | .953 | −.148 (−.080) | .662 |
| fs2 | 0.9 | .250 | −.062 | −.091 (−1.5, 5) | .611 | .667 | .205 | 1.032 | −.171 (−.109) | .627 |

For comparison, the control's picks had losers .167, lost half .077,
doubled .052, volatility .248 and a CAGR of .096.

The importances: on fs0 at the 0.8 quantile, `ret_1m_rank` 0.065,
`max_ret_21d_rank` 0.052, `dist_52w_high_rank` 0.033 and `vol_36m_rank`
0.029, the one-month reversal again; at 0.9, `log_marketcap_rank` 0.055
comes first and the same columns follow. On fs1 at 0.8,
`book_to_market_5y_pctile` 0.078, `log_assets_rank` 0.043,
`book_to_market_vs_5y_median_rank` 0.032, `tangible_book_to_market_rank`
0.028 and `earnings_yield_5y_peak_rank` 0.028: book value against the
stock's own history leads the upper-tail model. On fs2 at 0.8,
`earnings_yield_5y_peak` 0.084, `book_to_market` 0.075, `ocf_yield`
0.070 and `log_assets` 0.051.

### What the quantile sweep showed, against decision 79

- **Prediction 79(e) held on volatility, on losers and on the
  comparison with the run-up labels, and failed on the sign of the
  lead.** The picks' volatility is .71 to 1.03 (the prediction said .5
  or more), losers are .48 to .61 (the prediction said .35 or more), and
  every lead is at or below the run-up labels' (+.110 and +.026). The
  lead was predicted positive. It is −.001 and −.010 on fs0, +.025 and
  −.018 on fs1, and −.068 and −.062 on fs2. The 0.9 quantile is more
  extreme than 0.8 on volatility and losers for every set, and on the
  lead for fs0 and fs1 (both fs2 leads are deeply negative).
- **Asking for the upper tail finds different stocks, and they are the
  region's.** Half to two thirds of the quantile picks are inside the
  region, against 0.6% of the control's. They double four times as
  often as the control's picks (.20 to .22 against .05), and more than
  half of them lose money. Their same-size peers lose money too (−.04
  to −.11 a year). The upper tail of the three-year CAGR, as a boosted
  regression sees it in these columns, is made of small, volatile,
  fallen stocks. It is a lottery, not a set of mispriced survivors.
- **The own-history valuation columns lead the tail model on fs1, and
  that arm is the only one without a negative lead** (+.025, a gain of
  −.004 against the control, ahead in 7 of 16 years, with 48% losers).
  The same columns led inside the region's universe. They show where
  the upside is scattered. They do not pick it out.
- No quantile arm passes the screen rule, and none was expected to.

## Decision 80: the verdict

Decision 80 in [the decision log](2026-11-26-decisions.md) records the
verdict. In short: across the program's 49 runs (the control's re-run,
18 emphasis arms, 6 universe arms, 12 subspace forests, 6 colsample
boosters and 6 quantile regressions), no arm passes the screen rule
against the control on both outcomes. The arms that lead the control on
the three-year CAGR are the reversal forests, by 0.07 to 0.08 a year,
and they carry 38% to 41% losers. The arms within two points of the
control's share of losers carry its lead or less.

One pattern runs through every sweep: the more of a selection sits
inside the region, the more of it loses money.

| region share of the picks | share of losers | which selections |
|---|---|---|
| .006 | 17% | the control |
| .05 to .07 | 19% to 21% | the fs1 forests in cell C |
| .27 to .34 | 36% to 41% | the reversal forests |
| .47 to .86 | 44% to 61% | the compact-set, universe and quantile arms |
