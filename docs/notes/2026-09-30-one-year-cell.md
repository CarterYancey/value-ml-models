# A one-year "not a loser" cell

Detail behind the [logbook](../logbook.md) entry of 2026-09-30 for
`forest_nonloser_dd20_1y` and `baseline_factors_nonloser_1y_dv100k`.
Decision 22 of the [decision log](2026-09-29-decisions.md).

1y, `dataset_v1.4`, walk-forward, folds 2005–2020 of the 1-year fold
calendar (16 of its 20 folds; `split_folds.parquet` of
`dataset_v1.4`; 2021–22 left unseen because those snapshots are in
the 3-year holdout window). Cell:
`fwd_1y_cagr >= 0 & fwd_1y_max_drawdown_from_entry < 0.2`, inside the
universe `dollar_volume_3m >= 100000` (the forest trained on every
row, scope `test`). One seed (23). Six configurations in the cell,
all from this session. Not a result of record.

## What ran

- `forest_nonloser_dd20_1y` (run `8723a42cfc5e`, git `ba55f7d`): the
  candidate's forest configuration, 112 rank columns, isotonic
  calibration with the label lag (folds 2005–06 raw, 2007–20
  calibrated on folds up to Y−2).
- Five single factors in the same cell (`rank_factor`).
- The reference: cell C's 3-year forest (run `53ceedd93e6d`) read on
  the same 1-year outcomes (`vml-eval`,
  `eval_screen_1y_outcomes_dv100k`). Same test rows.

## Screen, 1-year outcomes

Top 10 per test quarter, at most 2 per sector; losers are
`fwd_1y_cagr < 0`.

| | precision on the 1y label | losers | mean 1y excess | median | deep drawdown (0.3 or more) |
|---|---|---|---|---|---|
| **3-year forest (cell C)** | | **0.236** | **+0.008** | +0.010 | 0.080 |
| 1-year forest | 0.689 | 0.275 | −0.004 | −0.005 | 0.097 |
| lowest 36-month volatility | 0.720 | 0.250 | −0.024 | −0.018 | 0.089 |
| highest conservative score | 0.620 | 0.325 | +0.006 | −0.005 | 0.153 |
| highest return on capital | 0.533 | 0.381 | −0.031 | −0.032 | 0.275 |
| highest earnings yield | 0.284 | 0.544 | −0.021 | −0.153 | 0.555 |
| highest 12-month momentum | 0.222 | 0.614 | −0.076 | −0.289 | 0.648 |

The 1-year forest: p@20 0.666 against a base rate of 0.458
(fold mean), fold-mean PR-AUC 0.603.

By entry year, losers among the screen's picks (3-year forest /
1-year forest): 2007 0.65 / 0.60; 2008 0.70 / 0.75; 2009 0.00 / 0.10;
2019 0.48 / 0.50; 2020 0.25 / 0.25. The 1-year forest's p@20 is 0.15
for 2007 entries, 0.05 for 2008 and 0.05 for 2019 (base rates 0.25,
0.10, 0.23).

## Calibrated thresholds (1-year forest)

| entry year | rows at 0.5 or more | precision | at 0.6 or more | precision |
|---|---|---|---|---|
| 2007 | 10,150 | 0.26 | 6,299 | 0.29 |
| 2008 | 9,785 | 0.10 | 6,594 | 0.11 |
| 2009 | 4,753 | 0.74 | 256 | 0.86 |
| 2010 | 0 | | 0 | |
| 2011 | 1,708 | 0.72 | 0 | |
| 2012 | 3,716 | 0.84 | 0 | |
| 2013 | 3,472 | 0.82 | 0 | |
| 2014 | 4,916 | 0.63 | 0 | |
| 2015 | 6,327 | 0.44 | 0 | |
| 2016 | 6,130 | 0.76 | 3,907 | 0.81 |
| 2017 | 4,994 | 0.65 | 2,730 | 0.68 |
| 2018 | 6,114 | 0.52 | 3,544 | 0.61 |
| 2019 | 6,126 | 0.27 | 4,019 | 0.29 |
| 2020 | 5,635 | 0.64 | 2,856 | 0.66 |

No row reaches 0.7 after 2008. Brier, fold mean: 0.248 against the
no-skill reference's 0.222; better than it in 8 of 16 years.

## Against the predictions in the config

| | prediction | measured | matched? |
|---|---|---|---|
| 1 | p@20 0.70–0.80; under 0.40 for 2007 and 2008 entries | 0.666; 0.15 and 0.05 | level **no**, crash years yes |
| 2 | screen losers 0.20–0.30, mean 1y excess −0.01 to +0.02 | 0.275, −0.004 | yes |
| 3 | losers and mean excess within 0.02 of the 3-year forest's | 0.039 more losers, 0.012 less excess | **no**: the 3-year forest is better on 1-year outcomes |
| 3, rival | the 1-year model has 0.05 fewer losers among 2008–09 and 2020 entries | 0.05 more, 0.10 more, equal | no |
| 4 | calibrated `score >= 0.7` precise to within 0.10 of its score | no row at 0.7 in a calibrated fold after 2008; in 2007–08 precision 0.31 and 0.12 | not testable as written; at 0.5 the precision runs from 0.10 to 0.84 by year |
| baselines | momentum's picks look better on 1-year outcomes than on 3-year ones (losers under 0.55) | 0.614 | no |

## Measured

1. **The 3-year forest picks better for one year ahead than a forest
   trained on one year ahead**: fewer losers (0.236 against 0.275),
   more excess (+0.008 against −0.004), in a cell that is the 1-year
   forest's own.
2. **A fresher label does not see a crash sooner.** For 2007 and 2008
   entries the 1-year forest's top 20 are right 15% and 5% of the
   time; its calibrated scores put 0.5 or more on 73% and 78%
   of the rows inside the floor in those years.
3. **Calibration with a two-year lag is no more usable than with a
   four-year one.** The precision of rows at a calibrated 0.5 runs
   from 0.10 to 0.84 by entry year, and the calibrated Brier is worse
   than the no-skill reference.

## What it might mean (hypothesis)

Whether a stock falls within a year is mostly whether the market
does: the 1-year base rate runs from 0.10 (2008) to 0.65 (2012,
2013), and nothing in a stock's own columns says which year it is.
Over three years more of the outcome belongs to the stock, and the
label is easier to learn. Upstream deferred market-state features
(PLAN §5.6); without them a confidence that means the same thing in
2008 and 2012 is not available from these columns.

## Decision

Neither condition of decision 22 holds. The 1-year cell is closed:
no backtest, no further runs. The 3-year forest stays the model;
selection stays by rank within the period.
