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
