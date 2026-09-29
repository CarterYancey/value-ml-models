# Label rungs around the from-entry cell, read on pick outcomes

Detail behind the [logbook](../logbook.md) entries for
`baseline_pick_outcomes_3y` and `forest_label_rungs_dd_entry_3y`,
both run and read 2026-09-29 in the sandbox.

3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`). Numbers are
selection-biased by the trial counts and none is a result of record.
Pick outcomes read the top 20 rows per test year with no costs, no
investability filter and equal weights: a screen, not a backtest.

## What ran, and how it was checked

- `forest_label_rungs_dd_entry_3y`: 9 cells × 1 forest configuration
  (set1 of `forest_candidate_sets_3y`, class weight 1.0) × 3 seeds
  (23, 232, 1776) = 27 runs, 0 failed, git `cbb03f9`, the `ranks`
  group (112 columns, from `*_config.json`). All 27 config hashes of
  the summary CSV are in the sandbox's ledger shard: 432 fold rows,
  16 per hash, no duplicates.
- The centre cell reproduces the reference run of the same
  parameters, seeds and columns
  (`forest_drawdown_compounder_seeds_3y`, git `86ef0c4`): p@20 0.5000,
  seed std 0.0162, fold-mean PR-AUC 0.3267, 2013–20 p@20 0.5354, all
  equal. The hashes differ because `pick_outcomes` is in the hash.
- `baseline_pick_outcomes_3y`: 2 deterministic runs, git `c03a322`.
  p@20 0.3875, hit rate 0.4906 and pooled median excess CAGR −0.0023
  equal the smoke test of 2026-09-28.
- Trials: each of the eight outer cells had none before and has 3
  now; the centre cell has 69.

Every figure below is the mean over the 16 test years of the yearly
statistic (and over seeds), unless it says pooled. For a median that
is not the pooled median: the bar's median excess CAGR is −0.0023
pooled and −0.0037 as a mean of yearly medians.

## The bar

Top 20 per year by highest `conservative_score_rank`, no model:

| | all years | 2005–12 | 2013–20 |
|---|---|---|---|
| picks beat SPY | 0.491 | 0.544 | 0.438 |
| all test rows beat SPY | 0.359 | 0.412 | 0.305 |
| picks, median excess CAGR | −0.004 | +0.012 | −0.019 |
| picks, mean excess CAGR | −0.021 | +0.004 | −0.045 |
| all rows, median excess CAGR | −0.073 | −0.044 | −0.102 |
| picks, median drawdown from entry | 0.26 | 0.25 | 0.27 |
| distinct stocks per 20 picks | 15.4 | 15.8 | 15.0 |

## The rungs

"floor / cap" is the CAGR floor and the drawdown-from-entry cap of
the label. Seed means; "worst" is the lowest seed.

| floor / cap | base rate | p@20 | 2013–20 | PR-AUC | beat SPY | worst | 2013–20 | worst | median excess | worst | 2013–20 | worst | mean excess | median drawdown | stocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.08 / 0.15 | 0.190 | 0.485 | 0.531 | 0.323 | 0.468 | 0.450 | 0.454 | 0.431 | −0.006 | −0.009 | −0.011 | −0.015 | −0.018 | 0.189 | 14.7 |
| 0.08 / 0.20 | 0.226 | 0.541 | 0.583 | 0.365 | 0.495 | 0.491 | 0.471 | 0.456 | +0.001 | −0.000 | −0.008 | −0.014 | −0.009 | 0.187 | 13.4 |
| 0.08 / 0.30 | 0.277 | 0.567 | 0.621 | 0.416 | 0.481 | 0.472 | 0.475 | 0.438 | −0.006 | −0.007 | −0.012 | −0.017 | −0.013 | 0.192 | 13.8 |
| 0.10 / 0.15 | 0.175 | 0.451 | 0.506 | 0.289 | 0.475 | 0.463 | 0.483 | 0.475 | −0.008 | −0.011 | −0.011 | −0.017 | −0.018 | 0.200 | 15.3 |
| **0.10 / 0.20** | 0.207 | 0.500 | 0.535 | 0.327 | 0.498 | 0.478 | 0.477 | 0.444 | −0.003 | −0.006 | −0.013 | −0.018 | −0.009 | 0.200 | 14.2 |
| 0.10 / 0.30 | 0.252 | 0.508 | 0.544 | 0.370 | 0.473 | 0.469 | 0.471 | 0.469 | −0.010 | −0.011 | −0.020 | −0.023 | −0.017 | 0.204 | 14.7 |
| 0.15 / 0.15 | 0.135 | 0.244 | 0.267 | 0.193 | 0.449 | 0.425 | 0.423 | 0.400 | −0.011 | −0.017 | −0.022 | −0.026 | −0.023 | 0.217 | 16.1 |
| 0.15 / 0.20 | 0.159 | 0.253 | 0.275 | 0.221 | 0.472 | 0.450 | 0.454 | 0.419 | −0.005 | −0.008 | −0.013 | −0.021 | −0.019 | 0.217 | 15.5 |
| 0.15 / 0.30 | 0.193 | 0.233 | 0.260 | 0.252 | 0.429 | 0.384 | 0.423 | 0.375 | −0.015 | −0.026 | −0.021 | −0.033 | −0.038 | 0.248 | 16.0 |
| bar (single factor) | | 0.388 | 0.419 | | 0.491 | | 0.438 | | −0.004 | | −0.019 | | −0.021 | 0.26 | 15.4 |

p@20, PR-AUC and base rate are each against the cell's own label and
are not comparable down the column.

By period, picks beat SPY / median excess CAGR (seed means):

| floor / cap | 2005–12 | 2013–16 | 2017–20 |
|---|---|---|---|
| 0.08 / 0.15 | 0.48 / −0.001 | 0.61 / +0.022 | 0.30 / −0.044 |
| 0.08 / 0.20 | 0.52 / +0.010 | 0.65 / +0.022 | 0.30 / −0.038 |
| 0.08 / 0.30 | 0.49 / +0.000 | 0.68 / +0.025 | 0.28 / −0.048 |
| 0.10 / 0.15 | 0.47 / −0.005 | 0.65 / +0.029 | 0.32 / −0.051 |
| 0.10 / 0.20 | 0.52 / +0.007 | 0.65 / +0.019 | 0.30 / −0.045 |
| 0.10 / 0.30 | 0.48 / +0.001 | 0.65 / +0.020 | 0.30 / −0.061 |
| 0.15 / 0.15 | 0.48 / −0.000 | 0.54 / +0.009 | 0.30 / −0.052 |
| 0.15 / 0.20 | 0.49 / +0.003 | 0.55 / +0.009 | 0.36 / −0.036 |
| 0.15 / 0.30 | 0.44 / −0.010 | 0.51 / +0.001 | 0.34 / −0.042 |
| all test rows, beat SPY | 0.41 | 0.32 | 0.29 |

The single factor by year, for comparison: picks beat SPY 0.60–0.75
for entry years 2013–16 and 0.10–0.35 for 2017–20.

## The pass rule

Written in the config: a cell passes when its picks beat the bar on
the beat_spy hit rate and on median excess CAGR, in 2013–20 and not
only over all years, on every seed.

**No cell passes.** Seeds passing all four comparisons: 0.08 / 0.20
two of three, 0.10 / 0.20 two of three, 0.15 / 0.20 one of three,
the other six cells none. Where a cell beats the bar the margin is
0.00–0.03 on the hit rate and 0.00–0.01 on median excess CAGR; the
standard error of a hit rate over 320 picks is about 0.03.

## Against the predictions in the config

| prediction | measured | matched? |
|---|---|---|
| a tighter cap lowers the picks' median drawdown | at floor 0.08: 0.189, 0.187, 0.192 for caps 0.15, 0.20, 0.30; at 0.10: 0.200, 0.200, 0.204; at 0.15: 0.217, 0.217, 0.248 | **no** for floors 0.08 and 0.10 (flat within 0.005); yes between caps 0.20 and 0.30 at floor 0.15 |
| a tighter cap lowers the picks' mean excess CAGR | cap 0.20 is the highest at every floor; cap 0.15 is below it by 0.004–0.009 | **no**: not monotone |
| the hit rate moves by less than 0.05 across caps | 0.027, 0.025, 0.043 | yes |
| the 0.15 floor has the lowest p@20 | 0.23–0.25 against 0.45–0.57 | yes |
| the 0.15 floor raises the picks' drawdown | 0.217–0.248 against 0.187–0.204 | yes |
| the 0.15 floor raises the picks' mean excess CAGR | −0.019 to −0.038 against −0.009 to −0.018 | **no**: it lowers it |
| no cell reaches a median excess CAGR above +0.03 in 2013–20 | highest −0.008 | yes |

Three predictions failed, so by the stop rule in
[agents.md](../agents.md) the queue was not continued.

## Measured

1. **Nine labels, one set of outcomes.** Across the six cells with
   floors 0.08 and 0.10 the picks' hit rate on beat_spy is 0.47–0.50,
   their median excess CAGR −0.010 to +0.001 and their median
   drawdown 0.19–0.20. The label's thresholds move p@20 from 0.45 to
   0.57 and PR-AUC from 0.29 to 0.42 and leave what the picks went on
   to do where it was.
2. **The forests' picks are not told apart from the single factor's
   on returns.** Centre cell against the bar: hit rate 0.498 against
   0.491, median excess −0.003 against −0.004, 2013–20 0.477 against
   0.438 and −0.013 against −0.019. The forest scores 0.50 on its
   label where the factor scores 0.39, and that 0.11 does not show in
   the picks' excess return.
3. **The forests' picks do have a lower drawdown than the factor's:**
   median 0.19–0.20 against 0.26 (means of yearly medians).
4. **The picks beat the average row and do not beat SPY.** Hit rate
   0.47–0.50 against 0.36 for all test rows; median excess CAGR about
   zero against −0.07. Read against zero (findings, conclusion 9),
   the picks match the index before costs.
5. **The 0.15 floor is the worst rung on every outcome:** lowest hit
   rate (0.43–0.47), lowest mean excess CAGR, highest drawdown, and
   a p@20 of 0.23–0.25 against base rates of 0.13–0.19.
6. **Everything depends on the entry year.** Entry years 2013–16:
   hit rate 0.61–0.68 in the six lower-floor cells, median excess
   +0.02 to +0.03. Entry years 2017–20: 0.28–0.32 and −0.04 to −0.06,
   at or below the hit rate of all rows (0.29). 2008 entries, all nine cells: 0.77–
   0.87. The single factor shows the same pattern.

## What it might mean (hypotheses, not tested)

- *Why the label's thresholds do not move the outcomes.* Rivals:
  (a) the nine forests pick largely the same rows, because every one
  of them ranks on the volatility ranks
  ([feature sets](2026-09-29-feature-sets-dd-entry.md)) and the
  thresholds change which of those rows count as hits, not which rows
  are picked; (b) the picks differ and the outcome distributions
  happen to agree. Separating them needs the overlap of the picked
  rows between cells, which a sweep does not save: two `vml-run`
  fold bundles (centre and one corner) compared row by row.
- *Why the 0.15 floor lowers excess return.* Rivals: (a) a harder
  label with a lower base rate is learned worse (p@20 is 1.3–1.8
  times the base rate against 2.0–2.6 for the other floors), so its
  picks are closer to noise; (b) a high CAGR floor pulls the model
  towards volatile stocks, which the higher drawdown of its picks
  (0.22–0.25) is consistent with. Both can hold.
- *Why 2017–20 entries lose to SPY.* The windows of those entries
  hold 2020 and the index's large-cap run. Calm stocks lagging a
  rising index would produce this; so would a weakening signal.
  Four entry years cannot separate them.

## What this changes

- The screen ranks no rung above the centre cell, and none passes
  the rule that earns a backtest. The primary cell is not displaced;
  it is also not confirmed as a label that beats the market.
- The question the plan's track 2 asks has a first answer on this
  screen: with the top 20 per year, equal weights and no costs,
  models of this kind match SPY on the median and carry a lower
  drawdown than the single factor. Whether that is worth a model is
  Carter's call, and a backtest with costs is the instrument.

## Proposed, not run

1. **Put `pick_outcomes` in the three parameter-search configs**
   before they run (none has run, so they can still be edited). The
   searches rank on PR-AUC of the label, and this sweep shows PR-AUC
   and p@20 moving without the picks' outcomes moving. Without the
   outcomes a search can only find a better predictor of the label.
2. **Decide whether the parameter searches run at all as queued**
   (120 runs in the primary cell). The case for: the label is
   learnable and the searches were planned. The case against: a
   0.11 gain in p@20 over the single factor bought nothing on excess
   return here, so a further gain in PR-AUC may buy nothing either.
3. **Overlap of picks between cells**, from two `vml-run` bundles
   (centre, and 0.15 / 0.30), to separate the rivals above.
4. **A backtest of the centre cell's forest against the single
   factor**, one template, buys ending 2020-12-31. It waits on
   `cost_bps` and the investability filter, which are Carter's.
