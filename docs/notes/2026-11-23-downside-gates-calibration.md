# Downside models, gates on the huber regressor, calibration arms (2026-11-23, second round)

Carter's three directions of decision 43; decisions 43–46 of the
[decision log](2026-09-29-decisions.md). `dataset_v1.4`, walk-forward
test years 2005–2020 (`split_folds.parquet`), every run trained on all
rows and read inside the 100k floor (`dollar_volume_3m >= 100000`,
scope `test`). Figures are selection-biased by the trial counts given.
The screen and the "lead" are read as in
[the first round](2026-11-23-crash-growth-worst-rank.md).

## 1. Downside: max drawdown from entry ≥ 30% / ≥ 50% within 1 and 3 years

One configuration per cell: three single factors
(`baseline_factors_downside_cells`) and the candidate forest's
parameters (`forest_downside_cells_3y`, models saved).

| cell | base rate | vol_12m PR-AUC (p@20) | vol_36m | beta_12m | forest PR-AUC (p@20) |
|---|---|---|---|---|---|
| 1y ≥ 30% | 0.352 | **0.538** (0.83) | 0.509 | 0.410 | 0.536 (0.70) |
| 1y ≥ 50% | 0.182 | 0.359 (0.68) | 0.324 | 0.224 | **0.369** (0.64) |
| 3y ≥ 30% | 0.542 | 0.678 (0.88) | 0.658 | 0.593 | **0.710** (0.88) |
| 3y ≥ 50% | 0.378 | 0.549 (0.82) | 0.522 | 0.422 | **0.589** (0.81) |

Over one year a drawdown is predicted as well by last year's
volatility as by a forest on 112 ranks; over three years the forest
adds 0.03–0.04. Predictions: factor bars held (but for the 3y 50% cell,
+0.17 over base against a predicted ≤ 0.15); forest 1 held, 2 half
(1y 30% p@20 0.70, not 0.80), 3 half.

Rows at score ≥ 0.5, by entry year (forest), with that year's base rate:

| year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1y ≥ 30%, n | 4455 | 3969 | 3594 | 2500 | 2013 | 3273 | 3005 | 2623 | 3034 | 3760 | 3748 | 3250 | 3625 | 3786 | 3728 | 4363 |
| base rate | .23 | .24 | .57 | .79 | .19 | .24 | .37 | .18 | .15 | .32 | .47 | .21 | .25 | .42 | .63 | .32 |
| 3y ≥ 30%, n | 9836 | 9611 | 6789 | 5142 | 4098 | 5467 | 6699 | 7279 | 6961 | 7441 | 7100 | 6270 | 6199 | 6444 | 6308 | 7185 |
| base rate | .46 | .71 | .81 | .80 | .31 | .37 | .42 | .29 | .40 | .53 | .55 | .35 | .57 | .68 | .73 | .55 |

The downside model was *least* alarmed going into 2007–08, the same
wrong-way lag as cell C's forest (calibration plan): its training
window then held the 2000–02 crash only in its oldest years.

## 2. The huber regressor on new seeds

| target, seed | lead 05–12 | lead 13–20 | losers | peers' losers |
|---|---|---|---|---|
| CAGR, 23 | +0.072 | +0.054 | 0.394 / 0.372 | 0.474 / 0.451 |
| CAGR, 232 | +0.073 | +0.032 | 0.394 / 0.416 | 0.469 / 0.457 |
| CAGR, 1776 | +0.082 | +0.054 | 0.381 / 0.391 | 0.467 / 0.455 |
| excess, 23 | +0.028 | +0.009 | 0.425 / 0.378 | 0.446 / 0.419 |
| excess, 232 | +0.023 | +0.019 | 0.437 / 0.366 | 0.444 / 0.422 |
| excess, 1776 | +0.027 | +0.006 | 0.425 / 0.394 | 0.436 / 0.420 |

Predictions: 1 (CAGR ≥ +0.05 in both halves on both new seeds) failed
on seed 232's 2013–20; 2 (excess stays below) held: not the seed.

## 3. Calibration step 3: level columns × `year_balance` (decision 44)

`calib_levels_nonloser_{plain,yb}_3y`, four runs, cell C, seed 23.
"levels" = the 112 ranks + 15 raw columns (vol, beta, yields, momentum,
distance from highs).

| arm | PR-AUC | p@10 | p@20 | year_calib_corr | year_calib_mae | conf_at_20 vs base rate (corr) |
|---|---|---|---|---|---|---|
| ranks, plain | 0.549 | 0.731 | 0.747 | −0.06 | 0.139 | −0.53 |
| levels, plain | 0.522 | 0.750 | 0.734 | −0.33 | 0.146 | −0.52 |
| ranks, year_balance | **0.572** | 0.769 | 0.744 | +0.07 | 0.140 | −0.68 |
| levels, year_balance | 0.551 | 0.750 | 0.728 | −0.25 | 0.142 | −0.66 |

Per year (mean score over all test rows; rows at ≥ 0.5 and their precision):

| year | base | ranks: mean | n ≥ .5 | prec | yb ranks: mean | n ≥ .5 | prec |
|---|---|---|---|---|---|---|---|
| 2005 | .47 | .36 | 2950 | .65 | .34 | 2165 | .67 |
| 2006 | .26 | .38 | 3415 | .30 | .35 | 2246 | .30 |
| 2007 | .18 | .46 | 6222 | .17 | .39 | 3424 | .19 |
| 2008 | .18 | .50 | 6537 | .21 | .42 | 4132 | .25 |
| 2009 | .66 | .51 | 6153 | .79 | .44 | 4056 | .84 |
| 2010 | .60 | .46 | 5348 | .80 | .41 | 3609 | .86 |
| 2011 | .55 | .41 | 3883 | .82 | .39 | 2839 | .86 |
| 2012 | .66 | .39 | 2839 | .89 | .37 | 2204 | .91 |
| 2013 | .54 | .40 | 3617 | .77 | .38 | 2680 | .80 |
| 2014 | .43 | .40 | 4209 | .69 | .38 | 3330 | .71 |
| 2015 | .41 | .41 | 4558 | .68 | .39 | 3711 | .72 |
| 2016 | .59 | .43 | 4946 | .76 | .41 | 4140 | .78 |
| 2017 | .39 | .43 | 5122 | .51 | .41 | 4279 | .54 |
| 2018 | .29 | .42 | 5124 | .42 | .40 | 4200 | .46 |
| 2019 | .24 | .42 | 5017 | .33 | .41 | 4320 | .34 |
| 2020 | .39 | .41 | 4872 | .57 | .40 | 4033 | .57 |

**No arm passes** (rule: `year_calib_corr` ≥ +0.3). Predictions: plain
ranks "about −0.6" contradicted (−0.06; the −0.58 of the plan was the
top 50's confidence, not the mean over all rows, and the top's
confidence is still −0.53); levels plain "−0.4 to +0.2" held; yb ranks
"−0.2 to +0.2" held; levels yb "+0.1 to +0.4" contradicted (−0.25);
the rival contradicted.

Readings:

- The score level moves little (0.34–0.52) while the base rate moves
  from 0.18 to 0.66, and what it does move is the wrong way: highest
  for the 2007–08 entries in every arm.
- **The level columns make it worse.** Hypothesis: before a crash the
  market is calm (low volatility everywhere, high momentum, prices
  near their highs), and the training years taught that calm stocks
  survive. Two or three cycles in a window cannot separate "calm" from
  "complacent". Per-stock levels are not market state.
- `year_balance` removes the training prior (lower, flatter level) and
  raises PR-AUC by 0.02–0.03 on both feature sets, but not where the
  picks are: on the screen the yb ranks forest leads same-size peers by
  +0.032 / +0.013 (plain: +0.036 / +0.024), losers 0.197 / 0.162
  (0.200 / 0.134). Not carried forward.
- This run's plain ranks forest screens at +0.036 / +0.024, the
  candidate forest bundle at +0.030 / +0.027 with the same parameters.
  The difference was not traced (both runs' configs would have to be
  expanded and compared); no comparison is drawn across them.

**What it means for the threshold rule:** with the inputs on disk, no
forest's score says how good the coming three years will be, so "every
stock over X" buys most at the top of a market. The level has to come
from market-state information upstream, and even then it is learned
from few cycles: decision 46.
