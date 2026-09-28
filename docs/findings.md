# Findings

What the experiments so far have established, by cell, with the evidence
behind each claim. This is the lab notebook: **read it before starting a
session, and add a dated entry to the log at the bottom before ending
one.** The catalog (`vml-experiments`) and `reports/promoted/README.md`
index individual results; this file carries the conclusions that span
them.

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased**: they come from the ledger after many
configurations were tried in the same cell (counts given). They rank
candidates; none is a result of record.

## State as of 2026-09-28 (evening, after the seven sweeps)

- **3y beat_spy, v1.1 against v1.4: the code and the added columns
  are both ruled out as the cause of the lower scores.** Today's code
  reproduces the August v1.1 numbers exactly, and the v1.1 column set
  scores 0.44 on v1.4 against 0.60 on v1.1. What is left: 17 of the
  shared columns hold different values on v1.4 (the ranks that
  upstream decision 0016 pinned in v1.2), and four columns were
  dropped. Which of the two carried the v1.1 edge is not tested yet;
  two control sweeps are written ("Results of the two tests").
- **No feature set gives a 3y beat_spy edge on v1.4 that can be told
  from noise.** Four ablation arms, one seed each: p@20 0.44–0.54
  pooled, PR-AUC 0.42 in every arm. No finalist for that cell.
- **The drawdown-compounder cells hold over seeds and after 2013**
  ("Drawdown-compounder cells"). Forests: p@20 0.50 against a 0.21
  base rate in the from-entry cell, 0.37 against 0.11 in the
  whole-path cell, seed std at most 0.03, and 2013–20 no weaker than
  2005–12. They fall to the base rate for entry years whose window
  holds a crash (2005–08, 2019). **The models lean on the volatility
  ranks and no low-volatility baseline has run**, so the lift is over
  the base rate, not yet over the obvious single factor.
- **Ledger:** `experiments/results.csv` holds 1,875 runs (by run id)
  on `dataset_v1.0`, `v1.1` and `v1.4`; 60 are from the seven sweeps
  reviewed on 2026-09-28 (56 on v1.4, 4 on v1.1). Results are never
  compared across versions.
- **Baselines on `dataset_v1.4`:** the 20 stored-label cells (80
  runs, seed 7), and now the two compounder cells (random × 3 seeds,
  book-to-market, earnings yield, majority).
- **Sealed holdout:** 19 looks in `reports/final_evals.csv` (listed
  below), unchanged. **Every 3y cell is still unopened.**
- **Next-step configs** (written 2026-09-28, dry-run clean, not yet
  run): `baseline_lowvol_rank_3y`, `forest_v11_column_control_3y`,
  `forest_v14_unchanged_columns_3y`. The plan is the next section.

## Plan as of 2026-09-28

The goal is the best model + parameters + feature set. That is a
question per cell, and the cell comes first: a search in a cell with
no signal returns selection noise (3y beat_spy on v1.4: 39
configurations, nothing separable).

1. **`baseline_lowvol_rank_3y`** (12 runs, seconds). Decides whether
   the compounder models are more than a low-volatility screen. Its
   reading is written in the config. Everything below depends on it.
2. **The two column controls** (12 runs, about 40 minutes):
   `forest_v11_column_control_3y`, then
   `forest_v14_unchanged_columns_3y`. Closes the v1.1 question. It
   does not block step 3: whatever it shows, `dataset_v1.1` is
   superseded and its candidates are not carried forward.
3. **Choose the primary cell.** Proposed:
   `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2`
   (largest absolute lift, base rate 0.21 so p@20 is less granular
   than in the 0.11 cell), with the whole-path cell as the second.
   3y beat_spy is parked until a feature set shows PR-AUC above 0.43.
   This is Carter's call: it is a choice of what to predict.
4. **Feature-set ablation in the primary cell** (forest, the two
   sets already run, 3 seeds): all ranks (the reference, already
   run); ranks minus `ranks/technical`; `ranks/technical` alone;
   ranks plus sector ranks; ranks plus raw `features/technical` and
   `features/trend`. With step 1 this says how much of the signal is
   volatility and what adds to it.
5. **Parameter search in the primary cell, per family**, on the
   feature set step 4 picks. The forest sets so far were tuned on
   beat_spy. Random search, one seed, equal budgets for
   random_forest, lightgbm and xgboost (about 40 draws each), then
   the top five of each on 3 seeds. Rank on the 2013–20 half and on
   the worst seed, with PR-AUC as the tie-break: the standard error
   of a pooled p@20 is about 0.03, so pooled p@20 alone picks noise.
6. **Calibration** for the family that wins (prequential, TODO
   Phase 3): forest Brier beats `base_rate_brier` in only 5–10 of 16
   years in these cells.
7. **One finalist, one holdout look** in that cell (both 3y
   compounder cells are unopened), then the backtest with costs and
   the investability filter. Not before steps 1–6.

Two evaluation gaps to close on the way (TODO): p@K counts test
*rows*, and a stock has up to four median rows per test year, so 20
picks can be a handful of stocks; and the crash-window years need
their own line in every report for these labels.

## 3y beat_spy on dataset_v1.4: same spec, different columns, lower scores

**Correction, 2026-09-28.** This section was first written as "the
carry-forward did not replicate" and the v1.1 section was marked
superseded. That went further than the evidence. The v1.4 sweeps
measured one thing: the carry-forward *spec* scores lower on v1.4.
They did not show that the v1.1 finding was wrong, because the two
sets of runs did not use the same columns, and at the time nobody had
checked what the v1.1 runs used at all (the `-2seeds` config was
lost). What is below is what has been verified since, and what is
still open.

### What was verified

- **The v1.1 configs.** `forest_random_search_3y-2seeds` was rebuilt
  from its summary header and expands to 100 runs whose config hashes
  all equal the recorded ones; `-2seeds2` matches its 74 ledger hashes.
  Both are saved in `experiments/sweeps/`. The carry-forward's six
  parameter sets and its feature spec are the ones that ran in August.
  `xgb_search_cells_features_params` matches its 90 ledger hashes too.
- **The rows.** Fold by fold, the v1.1 and v1.4 runs have the same
  training rows, effective training sizes, test rows and base rates
  (for example 2005: 299,982 / 12,691.0 / 18,684 / 0.408).
- **The columns differ.** The spec resolved to 124 columns on v1.1
  and 133 on v1.4 (from the two promoted importances files). v1.4
  adds 13: raw `beta_12m`, `mom_36_12`, `max_ret_21d`, `dist_5y_high`,
  `price_vs_5y_avg`, the six `*_vs_5y_median_rank` columns,
  `ohlson_o_rank`, `magic_formula_score_rank`. It drops 4:
  `piotroski_f_rank`, `mohanram_g7_rank`, `fundamentals_age_days_rank`,
  `ni_change_scaled_rank`.
- **Checked 2026-09-28 (evening), both datasets at hand:** the 120
  shared columns do *not* all hold the same values, and the code
  changes do not affect the metrics. Both are in "Results of the two
  tests" below. (Until then this bullet read "not verified".)

### The same six candidates on both versions

Shown to locate the cause, not as a performance comparison: results
from different dataset versions are not comparable as results.
Fold-mean p@20.

| candidate | v1.1 seeds | v1.1 pooled | v1.1 2013–20 | v1.4 pooled | v1.4 2013–20 |
|---|---|---|---|---|---|
| set0 (`-2seeds` r30) | 2 | 0.589 | 0.484 | 0.418 | 0.260 |
| set1 (`-2seeds` r48) | 2 | 0.583 | 0.506 | 0.429 | 0.269 |
| set2 (`-2seeds2` r7) | 4 | 0.588 | 0.522 | 0.432 | 0.267 |
| set3 (`-2seeds2` r9) | 4 | 0.586 | 0.505 | 0.435 | 0.267 |
| set4 (`-2seeds2` r10) | 4 | 0.579 | 0.508 | 0.424 | 0.279 |
| set5 (`-2seeds2` r14) | 4 | 0.577 | 0.514 | 0.401 | 0.219 |

Fold-mean PR-AUC of the six: 0.428 on v1.1, 0.409 on v1.4, lower on
v1.4 in 15 of 16 test years.

### What can and cannot be said

- **Selection noise does not explain the gap.** The six were picked
  on p@20, so some fall was expected, but the mean of *all* 238 v1.1
  forest runs is 0.551, still 0.13 above the v1.4 candidates. And
  PR-AUC, which nothing was selected on and whose seed std is 0.0004,
  falls in 15 of 16 years.
- **The four dropped columns probably do not explain it.** Together
  they held 0.05% of the impurity importance in the v1.1 lead run
  (ranks 52, 58, 75 and 103 of 124; 0.053%, first written here as
  0.06%). Importance is a weak witness,
  so "probably".
- **The 13 added columns were the leading suspect.** They
  hold 18% of the importance in v1.4 set3, and two are in its top
  ten. Tested 2026-09-28: removing them does not bring the v1.1
  scores back (below).
- **A code change was the other suspect.** Tested 2026-09-28: ruled
  out (below).
- So: **the v1.1 findings stand as found on v1.1, unconfirmed on
  v1.4.** What did not carry over is the assumption that a feature
  spec means the same experiment on a new dataset version.

### What the v1.4 runs showed

`forest_candidate_sets_3y` (6 candidates × 3 seeds) and
`xgb_candidate_sets_3y` (3 × 3), the same cell, feature spec and seeds.
31 configurations tried in this cell on v1.4 (27 models + 4 baselines),
after 713 on v1.1 over the same test years. Mean effective training
size 25.5k (12.7k in the 2005 fold to 37.2k in 2020, Σ
`sample_weight_3y`); `split_folds.parquet` of `dataset_v1.4`.

Fold-mean p@20 per family, averaged over every run of the family:

| family | runs | 2005–12 | 2013–20 | 2013–19 | pooled | PR-AUC |
|---|---|---|---|---|---|---|
| random_forest | 18 | 0.59 | 0.26 | 0.22 | 0.42 | 0.41 |
| xgboost | 9 | 0.54 | 0.20 | 0.17 | 0.37 | 0.41 |
| random baseline (1 seed) | 1 | 0.45 | 0.33 | 0.32 | 0.39 | 0.35 |
| earnings-yield rank | 1 | 0.24 | 0.19 | 0.16 | 0.22 | 0.38 |
| book-to-market rank | 1 | 0.21 | 0.18 | 0.18 | 0.19 | 0.34 |
| base rate | | 0.41 | 0.29 | 0.28 | 0.35 | |

Per test year (p@20; forest and xgb are family means):

| year | base rate | forest | xgb | random |
|---|---|---|---|---|
| 2005 | 0.41 | 0.64 | 0.57 | 0.45 |
| 2006 | 0.46 | 0.68 | 0.68 | 0.50 |
| 2007 | 0.46 | 0.61 | 0.58 | 0.40 |
| 2008 (GFC) | 0.46 | 0.71 | 0.67 | 0.45 |
| 2009 (GFC) | 0.44 | 0.60 | 0.56 | 0.45 |
| 2010 | 0.36 | 0.49 | 0.40 | 0.45 |
| 2011 | 0.32 | 0.56 | 0.55 | 0.45 |
| 2012 | 0.34 | 0.41 | 0.32 | 0.45 |
| 2013 | 0.32 | 0.30 | 0.23 | 0.20 |
| 2014 | 0.30 | 0.10 | 0.15 | 0.40 |
| 2015 | 0.30 | 0.34 | 0.26 | 0.40 |
| 2016 | 0.31 | 0.38 | 0.31 | 0.30 |
| 2017 | 0.24 | 0.15 | 0.02 | 0.20 |
| 2018 | 0.26 | 0.11 | 0.06 | 0.40 |
| 2019 | 0.27 | 0.18 | 0.16 | 0.35 |
| 2020 (COVID) | 0.33 | 0.53 | 0.41 | 0.40 |

Candidates, seed-mean pooled p@20 (std over 3 seeds): forest set3
0.435 (0.010), set2 0.432 (0.021), set1 0.429 (0.002), set4 0.424
(0.009), set0 0.418 (0.028), set5 0.401 (0.007); xgb set0 0.381
(0.009), set1 0.369 (0.006), set2 0.357 (0.012).

- **With these columns there is no edge after 2013.** The forests
  score 0.26 in 2013–20 against a 0.29 base rate, and 0.22
  against 0.28 without 2020. Each forest candidate's top-20 picks were
  worse than the base rate in four to six of the seven years 2013–19
  (2015 and 2016 are the exceptions). xgb is lower still (0.17), with
  3 hits in 180 picks in 2017 across its nine runs.
- **The pooled lift is a 2005–12 lift.** Every forest candidate beat
  the base rate in all eight of those years (0.59 against 0.41 for
  the family) and again in 2020. A
  pooled 0.42 hides that the model would have been useless, or
  harmful, for the seven years in between.
- **The whole ranking still carries signal; the top of it does not.**
  PR-AUC beats the base rate in 15 of 16 years for forests and xgb
  alike, 2018 being the miss (2013–20: 0.33 and 0.34 against 0.29),
  though by 0.01–0.02 in 2017–19. So the scores order the
  cross-section slightly better than chance, while the 20 highest
  scores are the wrong names after 2013. The two families have the
  same PR-AUC (0.41); the forests' p@20 advantage over xgb (+0.05) is
  a top-of-ranking difference only.
- **What the models lean on shifts over the folds.** In the forest
  (set3), raw `vol_12m` + `beta_12m` carry 0.55 of the importance in
  the 2005 fold and 0.12 in 2020; `ocf_yield_rank` +
  `cfo_to_assets_rank` go from 0.07 to 0.32. xgb shows the same shift.
  The v1.1 lead run shows the same shift (`vol_12m` 0.64 in 2005),
  so it is not what separates the two versions.
- **Against the baselines:** the catalog's reference is the best
  baseline in the cell, which is the random ranking at 0.39. That
  number is one seed, and 0.04 above the base rate by chance (the
  standard error of p@20 over 320 picks is about 0.027). Read against
  the base rate, forests are +0.07 pooled and xgb +0.02. Both
  single-factor ranks are far *below* the base rate (0.19–0.22): the
  cheapest stocks by book-to-market or earnings yield were poor
  3-year bets against SPY in nearly every year.
- **Seeds are stable, candidates are indistinguishable.** Seed std is
  0.002–0.028, and the five shallow forest candidates span 0.42–0.44,
  inside one standard error of each other. set5 (max_depth 13) is
  last at 0.40.
- **Scores are still not calibrated.** Forest Brier is worse than
  `base_rate_brier` in 11–13 of 16 years (0.239 against 0.222, fold
  means). xgb set1 and set2 (class_weight 0.5) are level with it
  (0.221–0.222, worse in 7–8 years); xgb set0 (class_weight 0.1) is
  worse in all 16 (0.283).

### The two tests, and what each outcome would mean

Written before either has run.

1. `forest_v11_code_control_3y` (4 runs): r30 and r48 on
   `dataset_v1.1` with today's code. The per-fold metrics should equal
   the August ledger rows. If they do not, a code change moved the
   numbers and every v1.4 result waits on finding it.
2. `forest_feature_ablation_3y` (24 runs), arm fs0: the carry-forward
   spec minus the 13 added columns, which is the v1.1 column set less
   the four dropped columns. If fs0 comes back to about 0.58 pooled
   and 0.50 in 2013–20, the added columns are the cause and the v1.1
   candidates carry forward *with that column selection*. If fs0 stays
   near 0.43, the cause is in the shared columns' values or the four
   dropped columns, and that goes upstream as a question.

### Results of the two tests (2026-09-28)

Both ran at git `86ef0c4`. What was measured comes first, what it
might mean after.

**1. Code control: the code is not the cause.**
`forest_v11_code_control_3y` (4 runs, `dataset_v1.1`). All 64 fold
rows equal the August ledger rows of r30 and r48 (seeds 23, 232; git
`e587a66`): training rows, effective sizes, test rows, base rates,
p@20, PR-AUC and ROC-AUC are identical, Brier and conf@20 to within
3e-16. Pooled p@20 0.589 (r30) and 0.583 (r48), as in August. The
config hashes differ from August's because the hash includes the
sweep name; the match is on the numbers. The v1.1 cell now counts 717
configurations.

**2. Ablation: the 13 added columns are not the cause.**
`forest_feature_ablation_3y`, `dataset_v1.4`, **8 runs, not the 24
its header describes**: the config carried `seeds = [23]`, so every
arm is one seed. 39 configurations tried in this cell on v1.4 (717 on
v1.1 over the same test years). Resolved columns checked from each
run's `*_config.json`: fs0 120, fs1 118, fs2 73, fs3 112. fs0 is
exactly the v1.1 column set less the four dropped columns. The
reference arm (133 columns) is seed 23 of `forest_candidate_sets_3y`,
same parameters.

Fold-mean p@20, seed 23. "Years" is how many of the seven years
2013–19 the top 20 beat the base rate:

| set | arm (columns) | pooled | 2005–12 | 2013–20 | 2013–19 | years | p@50 | PR-AUC |
|---|---|---|---|---|---|---|---|---|
| set1 | v1.1, r48 (124) | 0.597 | 0.675 | 0.519 | 0.479 | 6 | n/a | 0.429 |
| set1 | reference (133) | 0.428 | 0.600 | 0.256 | 0.214 | 2 | 0.411 | 0.413 |
| set1 | fs0, v1.1 columns (120) | 0.441 | 0.562 | 0.319 | 0.293 | 3 | 0.458 | 0.424 |
| set1 | fs1, no raw technicals (118) | 0.494 | 0.638 | 0.350 | 0.336 | 4 | 0.475 | 0.423 |
| set1 | fs2, fundamental ranks (73) | 0.472 | 0.606 | 0.338 | 0.321 | 3 | 0.465 | 0.422 |
| set1 | fs3, all ranks (112) | 0.544 | 0.650 | 0.438 | 0.429 | 6 | 0.479 | 0.424 |
| set3 | reference (133) | 0.425 | 0.588 | 0.262 | 0.214 | 1 | 0.424 | 0.406 |
| set3 | fs0, v1.1 columns (120) | 0.444 | 0.606 | 0.281 | 0.264 | 2 | 0.462 | 0.423 |
| set3 | fs1, no raw technicals (118) | 0.481 | 0.588 | 0.375 | 0.343 | 3 | 0.506 | 0.422 |
| set3 | fs2, fundamental ranks (73) | 0.516 | 0.612 | 0.419 | 0.407 | 2 | 0.489 | 0.421 |
| set3 | fs3, all ranks (112) | 0.472 | 0.612 | 0.331 | 0.307 | 4 | 0.521 | 0.420 |
| | base rate | 0.35 | 0.41 | 0.29 | 0.28 | | | |

Per test year, p@20:

| year | base | v1.1 r48 | set1 ref | set1 fs0 | set1 fs1 | set1 fs2 | set1 fs3 | set3 ref | set3 fs0 | set3 fs1 | set3 fs2 | set3 fs3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2005 | 0.41 | 0.85 | 0.75 | 0.80 | 0.90 | 0.60 | 0.70 | 0.75 | 0.80 | 0.80 | 0.75 | 0.65 |
| 2006 | 0.46 | 0.65 | 0.60 | 0.55 | 0.75 | 0.65 | 0.70 | 0.65 | 0.75 | 0.70 | 0.80 | 0.85 |
| 2007 | 0.46 | 0.85 | 0.60 | 0.70 | 0.75 | 0.75 | 0.60 | 0.60 | 0.75 | 0.60 | 0.95 | 0.50 |
| 2008 (GFC) | 0.46 | 0.90 | 0.70 | 0.65 | 0.85 | 0.70 | 0.70 | 0.75 | 0.80 | 0.90 | 0.80 | 0.75 |
| 2009 (GFC) | 0.44 | 0.55 | 0.60 | 0.65 | 0.80 | 0.80 | 0.55 | 0.60 | 0.55 | 0.65 | 0.60 | 0.50 |
| 2010 | 0.36 | 0.60 | 0.55 | 0.35 | 0.60 | 0.55 | 0.60 | 0.40 | 0.50 | 0.50 | 0.45 | 0.50 |
| 2011 | 0.32 | 0.35 | 0.60 | 0.45 | 0.25 | 0.35 | 0.80 | 0.55 | 0.40 | 0.25 | 0.45 | 0.60 |
| 2012 | 0.34 | 0.65 | 0.40 | 0.35 | 0.20 | 0.45 | 0.55 | 0.40 | 0.30 | 0.30 | 0.10 | 0.55 |
| 2013 | 0.32 | 0.65 | 0.25 | 0.50 | 0.75 | 0.65 | 0.70 | 0.25 | 0.45 | 0.85 | 0.95 | 0.50 |
| 2014 | 0.30 | 0.65 | 0.10 | 0.25 | 0.60 | 0.55 | 0.45 | 0.10 | 0.25 | 0.55 | 0.95 | 0.35 |
| 2015 | 0.30 | 0.70 | 0.30 | 0.40 | 0.30 | 0.35 | 0.50 | 0.25 | 0.40 | 0.30 | 0.25 | 0.40 |
| 2016 | 0.31 | 0.55 | 0.35 | 0.30 | 0.20 | 0.25 | 0.50 | 0.45 | 0.25 | 0.30 | 0.30 | 0.35 |
| 2017 | 0.24 | 0.10 | 0.20 | 0.10 | 0.05 | 0.05 | 0.10 | 0.15 | 0.10 | 0.10 | 0.10 | 0.15 |
| 2018 | 0.26 | 0.30 | 0.10 | 0.20 | 0.10 | 0.15 | 0.35 | 0.10 | 0.20 | 0.15 | 0.10 | 0.15 |
| 2019 | 0.27 | 0.40 | 0.20 | 0.30 | 0.35 | 0.25 | 0.40 | 0.20 | 0.20 | 0.15 | 0.20 | 0.25 |
| 2020 (COVID) | 0.33 | 0.80 | 0.55 | 0.50 | 0.45 | 0.45 | 0.50 | 0.60 | 0.40 | 0.60 | 0.50 | 0.50 |

Measured:

- **fs0 did not return to the v1.1 numbers.** The prediction written
  before the run was 0.58 pooled and 0.50 in 2013–20 if the added
  columns were the cause. fs0 scored 0.44 and 0.28–0.32. Same
  parameters and seed on the two versions (set1 = r48, seed 23):
  0.597 on v1.1, 0.441 on v1.4 with the v1.1 columns; v1.1 is higher
  in 13 of the 16 years and lower in 2.
- **Removing the added columns does raise PR-AUC**, in 15 of 16
  years for both sets: 0.413 → 0.424 (set1) and 0.406 → 0.423
  (set3). Its seed std is 0.0004, so that difference is not noise.
  It leaves fs0 0.006 below the v1.1 run (0.429), and that remainder
  sits in 2015–19 (mean gap 0.015 there, 0.001 over 2005–14).
- **Every arm has the same PR-AUC, 0.420–0.424,** and every arm's
  Brier (0.236–0.244) is worse than `base_rate_brier` (0.222).
- **The arms cannot be ranked on p@20.** They span 0.44–0.54, the
  best arm for set1 (fs3, 0.544) is fourth for set3 (0.472), and the
  best for set3 (fs2, 0.516) is third for set1. One seed each, a
  standard error of about 0.03 pooled and 0.04 on a half. All eight
  are above the reference in 2013–20 (0.28–0.44 against 0.26), which
  is consistent with the added columns hurting and says nothing
  about which arm is better. 2017 is below the base rate in every
  arm and on v1.1.

**3. The shared columns: 17 of the 120 changed values between v1.1
and v1.4.** Checked on the two `dataset.parquet` files, not run
through the harness. The two versions have the same 1,530,843 rows in
the same order. Of the 120 columns the v1.1 and v1.4 feature sets
share, 103 are equal to within 2e-10 (no NULL differs) and 17 are
not: `asset_turnover_rank`, `asset_turnover_delta_1y_rank`,
`capex_to_assets_rank`, `debt_to_equity_rank`, `dividend_yield_rank`,
`ev_to_marketcap_rank`, `ext_financing_to_assets_rank`, `gmi_rank`,
`gp_to_assets_rank`, `gross_margin_rank`,
`gross_margin_delta_1y_rank`, `gross_margin_delta_2y_rank`,
`net_payout_yield_rank`, `rnd_to_assets_rank`, `sales_yield_rank`,
`share_count_growth_1y_rank`, and raw `conservative_score`.

- They differ in 84–100% of their non-NULL rows. Mean absolute
  change 0.02–0.23 on a 0–1 rank (largest: `gp_to_assets_rank`
  0.23); Spearman correlation between the versions 0.988 or more,
  except `dividend_yield_rank` (0.83) and `rnd_to_assets_rank`
  (0.88).
- The change entered at v1.2 (all 17 differ between v1.1 and v1.2,
  none between v1.2 and v1.4). It is upstream decision 0016: ranks of
  features with a mass point are pinned, so that the tied group's
  rank no longer encodes the quarter. `conservative_score` is built
  from `net_payout_yield_rank`. `data/manual.md` documents the
  boundary as breaking; the v1.2 row of `data/versions.md` named only
  the removed columns (corrected today). "v1.4 is additive" is true
  of v1.2 → v1.4, which is what that row describes.
- In the v1.1 lead run (r30, seed 23) the 17 held 14.8% of the
  impurity importance, `rnd_to_assets_rank` (5.9%) and
  `dividend_yield_rank` (4.1%) first. Those two are among the four
  columns the era probe found to identify the quarter. In fs0 on
  v1.4 the 17 hold 5.5–6.6%.

What is left, and what would separate it. Between the v1.1 runs and
fs0 two things differ, and nothing else that was checked (rows, code,
parameters, seeds):

- **(a) the four dropped columns**, 0.05% of the importance in the
  v1.1 lead run;
- **(b) the values of the 17 changed columns.** Within (b) there are
  two readings, and no run separates them yet: the v1.1 ranks
  carried a quarter identifier that the forest used (then the v1.1
  p@20 was partly a market-state signal, and decision 0016's
  statement that walk-forward is not inflated by the keys would need
  a second look upstream), or pinning removed cross-sectional
  information a stock picker could use.

`forest_v11_column_control_3y` and `forest_v14_unchanged_columns_3y`
separate (a) from (b); their predictions are written in the configs.
Separating the two readings of (b) needs per-quarter picks (p@K
within each test quarter on v1.1: an edge that came from choosing
the quarter disappears), which the harness does not report today.

**What this changes.** The v1.1 forest numbers cannot be reproduced
on any dataset from v1.2 on with the same columns, whatever (a)/(b)
shows, because the columns no longer exist in that form. The v1.1
findings stay as found on v1.1. Candidates for 3y beat_spy have to
be found on v1.4, and on v1.4 nothing tried so far has an edge after
2013 that holds across parameter sets.

**Decision: no 3y beat_spy holdout look.** There is no candidate one
would act on yet. The cell stays unopened.

Promoted (2026-09-27, notes revised 2026-09-28):
`sweep_forest_candidate_sets_3y`, `sweep_xgb_candidate_sets_3y`, and
the era report of forest set3, seed 23.

## 3y beat_spy: model families (dataset_v1.1)

Found on v1.1 and not confirmed on v1.4: the same configurations
score lower there. The code and the columns v1.4 added are ruled
out as the cause; 17 of the columns used here changed values at
v1.2 and four were dropped (section above, "Results of the two
tests"). These numbers describe `dataset_v1.1` only.

713 configurations tried in this cell (`label_3y_beat_spy`, 3y,
walkforward, v1.1). Base rate 0.35 pooled (0.41 in 2005–12, 0.29 in
2013–20); the v1.0 random-ranking baseline scored p@20 0.33 in both
halves. Mean effective training size ≈ 25k (Σ `sample_weight_3y`).

Family means, each averaged over **every** run of the family, not the
winner (so these carry less selection bias than any top-of-sweep
number). Fold p@20, or p@50 where the sweep logged only that (the lgbm
random searches):

| family (sweeps) | runs | 2005–12 | 2013–20 | pooled |
|---|---|---|---|---|
| random_forest (`forest_random_search_3y`, `-2seeds`, `-2seeds2`) | 223 | 0.61 | **0.49** | 0.55 |
| xgboost (`xgb_random_search_3y`, `xgb_search_cells_features_params`) | 206 | 0.60 | 0.38 | 0.49 |
| lightgbm (`lgbm_random_search_3y`, `-2`; p@50) | 106 | 0.56 | 0.38 | 0.47 |
| lightgbm_regressor, quantile reframe (`lgbm_cagr_quantile_3y*`; p@50/p@20) | 177 | 0.52 | 0.36 | 0.44 |
| base rate | | 0.41 | 0.29 | 0.35 |

- **Every family is strong before 2013, and only forests keep a real
  edge after it** (+0.20 over the base rate against about +0.09 for the
  boosted families). That is the most useful single fact to carry
  forward. 2017 is weak for everyone (forests 0.15, base 0.24).
- **Hyperparameters barely matter inside a family.** Forest p@20 spans
  0.48–0.60 across 50 draws, with PR-AUC flat at 0.46–0.47; with
  320 picks per run the standard error of p@20 is about 0.028, so the
  sweep "winner" is mostly selection noise. The top eight seed-replicated
  forest candidates sit at 0.575–0.589. What they share: **shallow trees
  (max_depth 3–4), class_weight 1**. xgb's seed spread is small (≤ 0.02),
  and its best candidate (set2) sits at 0.560 ± 0.018 over 3 seeds.
- **Scores are not calibrated.** The lead forest candidate's Brier is
  worse than `base_rate_brier` in most test years, although its ranking
  is good. Use rank or top-K selection, and do not read the scores as
  probabilities until calibration is added (see TODO, prequential
  calibration).
- **Features:** `ranks` vs `ranks + sector_ranks` are indistinguishable
  in the xgb search. The forest and xgb follow-ups used a mixed set:
  `ranks` minus the technical/trend rank families, plus raw
  `features/trend` and `features/technical`. On v1.1 that set includes
  `piotroski_f_rank` / `mohanram_g7_rank`, which v1.2 removed as era
  fingerprints, which is one more reason for the v1.4 re-run.
- **The regression reframe didn't beat the classifiers** (quantile
  regressor 0.44 pooled against 0.47–0.55). `alpha = 0.25` was the best
  quantile, and winsorizing made no difference.

Promoted: `sweep_forest_random_search_3y-2seeds`, `sweep_xgb_random_search_3y`,
`sweep_xgb_search_cells_features_params`, and the lead forest candidate's
per-run report (for its era table).

**Selection-bias disclosure for the carry-forward.** The v1.4 sweeps
re-test candidates that were chosen on the *same walk-forward test
years* with v1.1 data, so their v1.4 numbers are not fresh. They
confirm or refute a candidate; they do not measure it. Disclose the
713 prior configurations alongside the v1.4 trial count whenever a
carry-forward number is reported. The only unbiased number is the 3y
holdout, which is still unopened. Spend it on one finalist, once.

## Drawdown-compounder cells (dataset_v1.4, 3 seeds)

Two cells, 3y, walk-forward, test years 2005–2020,
`split_folds.parquet` of `dataset_v1.4`, git `86ef0c4`:

- **A, whole path:** `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3`.
  Base rate 0.11 pooled (0.12 in 2005–12, 0.10 in 2013–20), 0.02 to
  0.25 by year. 25 configurations tried.
- **B, from entry:**
  `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2`. Base
  rate 0.21 pooled (0.22 / 0.20), 0.04 to 0.37 by year. 30
  configurations tried.

Sweeps: `forest_drawdown_compounder_seeds_3y` (2 parameter sets × 2
class weights × 3 seeds per cell), `lgbm_drawdown_compounder_seeds_3y`
(2 class weights × 3 seeds), and the three
`baseline_*_drawdown_compounder_3y` sweeps. Features: the `ranks`
group, 112 columns, in every model. Seeds 23, 232, 1776. Training
rows and effective sizes are those of the beat_spy cell (mean Σ
`sample_weight_3y` 25.5k, 12.7k in the 2005 fold to 37.2k in 2020).
The forest sets are set3 and set1 of `forest_candidate_sets_3y`
(named set0 and set1 in this sweep); they were tuned on beat_spy, not
here. The numbers are selection-biased by the counts above and none
is a result of record.

Seed-mean fold-mean p@20. "Years" is how many of the 16 test years
the seed-mean p@20 beat the base rate; "Brier yrs" how many years
Brier beat `base_rate_brier`, averaged over seeds:

| cell | candidate | p@20 | seed std | worst seed | 2005–12 | 2013–20 | years | p@50 | PR-AUC | Brier yrs |
|---|---|---|---|---|---|---|---|---|---|---|
| A | forest set1, cw 1.0 | 0.389 | 0.002 | 0.388 | 0.356 | 0.421 | 13 | 0.381 | 0.268 | 9.0 |
| A | forest set0, cw 1.0 | 0.374 | 0.005 | 0.369 | 0.308 | 0.440 | 12 | 0.371 | 0.268 | 8.7 |
| A | forest set0, cw 0.5 | 0.369 | 0.003 | 0.366 | 0.340 | 0.398 | 14 | 0.376 | 0.268 | 8.0 |
| A | forest set1, cw 0.5 | 0.365 | 0.016 | 0.350 | 0.342 | 0.388 | 12 | 0.369 | 0.267 | 8.0 |
| A | lightgbm, cw 0.25 | 0.348 | 0.007 | 0.341 | 0.321 | 0.375 | 11 | 0.355 | 0.257 | 4.0 |
| A | lightgbm, cw 0.5 | 0.327 | 0.022 | 0.303 | 0.294 | 0.360 | 10 | 0.343 | 0.258 | 7.7 |
| A | random (3 seeds) | 0.110 | 0.010 | 0.100 | 0.121 | 0.100 | 9 | 0.108 | 0.112 | |
| A | book-to-market rank | 0.038 | | | 0.050 | 0.025 | 2 | 0.021 | 0.104 | |
| A | earnings-yield rank | 0.028 | | | 0.031 | 0.025 | 3 | 0.031 | 0.146 | |
| A | base rate | 0.112 | | | 0.124 | 0.100 | | | | |
| B | forest set1, cw 1.0 | 0.500 | 0.016 | 0.491 | 0.465 | 0.535 | 14 | 0.479 | 0.327 | 10.0 |
| B | forest set0, cw 1.0 | 0.499 | 0.016 | 0.481 | 0.454 | 0.544 | 14 | 0.488 | 0.327 | 9.3 |
| B | forest set0, cw 0.5 | 0.498 | 0.028 | 0.466 | 0.460 | 0.535 | 14 | 0.493 | 0.328 | 5.0 |
| B | forest set1, cw 0.5 | 0.481 | 0.008 | 0.475 | 0.433 | 0.529 | 13 | 0.484 | 0.327 | 5.0 |
| B | lightgbm, cw 0.5 | 0.400 | 0.014 | 0.384 | 0.371 | 0.429 | 11 | 0.391 | 0.303 | 5.0 |
| B | lightgbm, cw 0.25 | 0.394 | 0.019 | 0.381 | 0.390 | 0.398 | 11 | 0.403 | 0.303 | 1.0 |
| B | random (3 seeds) | 0.214 | 0.014 | 0.200 | 0.212 | 0.215 | 6 | 0.208 | 0.208 | |
| B | book-to-market rank | 0.106 | | | 0.125 | 0.088 | 3 | 0.084 | 0.197 | |
| B | earnings-yield rank | 0.075 | | | 0.062 | 0.088 | 2 | 0.099 | 0.245 | |
| B | base rate | 0.207 | | | 0.216 | 0.199 | | | | |

Per test year, family means over every run of the family (12 forest
runs, 6 lightgbm, 3 random):

| year | A base | A forest | A lgbm | A random | B base | B forest | B lgbm | B random |
|---|---|---|---|---|---|---|---|---|
| 2005 | 0.10 | 0.08 | 0.08 | 0.10 | 0.21 | 0.14 | 0.03 | 0.27 |
| 2006 | 0.05 | 0.03 | 0.01 | 0.07 | 0.09 | 0.16 | 0.02 | 0.07 |
| 2007 | 0.02 | 0.00 | 0.00 | 0.00 | 0.04 | 0.13 | 0.00 | 0.03 |
| 2008 (GFC) | 0.03 | 0.11 | 0.00 | 0.03 | 0.05 | 0.16 | 0.17 | 0.08 |
| 2009 (GFC) | 0.16 | 1.00 | 0.65 | 0.13 | 0.36 | 0.84 | 0.79 | 0.33 |
| 2010 | 0.17 | 0.57 | 0.59 | 0.18 | 0.32 | 0.74 | 0.87 | 0.32 |
| 2011 | 0.21 | 0.47 | 0.78 | 0.18 | 0.27 | 0.70 | 0.56 | 0.23 |
| 2012 | 0.25 | 0.43 | 0.34 | 0.27 | 0.37 | 0.75 | 0.61 | 0.37 |
| 2013 | 0.15 | 0.48 | 0.36 | 0.20 | 0.28 | 0.57 | 0.38 | 0.40 |
| 2014 | 0.14 | 0.60 | 0.64 | 0.12 | 0.21 | 0.66 | 0.45 | 0.15 |
| 2015 | 0.15 | 0.60 | 0.49 | 0.10 | 0.18 | 0.66 | 0.49 | 0.13 |
| 2016 | 0.17 | 0.71 | 0.58 | 0.18 | 0.30 | 0.79 | 0.60 | 0.37 |
| 2017 | 0.06 | 0.36 | 0.43 | 0.08 | 0.18 | 0.50 | 0.62 | 0.15 |
| 2018 | 0.03 | 0.35 | 0.37 | 0.05 | 0.13 | 0.69 | 0.71 | 0.18 |
| 2019 | 0.02 | 0.04 | 0.02 | 0.00 | 0.09 | 0.01 | 0.00 | 0.08 |
| 2020 (COVID) | 0.08 | 0.15 | 0.07 | 0.07 | 0.22 | 0.41 | 0.07 | 0.25 |

Measured:

- **The single-seed results held.** LightGBM over three seeds: 0.33–
  0.35 in A (0.36 on seed 7 before) and 0.39–0.40 in B (0.40–0.42
  before). Seed std is 0.002–0.028 across all twelve candidates.
- **The lift is not a 2005–12 lift.** Every model candidate scores
  higher in 2013–20 than in 2005–12, the opposite of beat_spy.
  Forests, 2013–20: 0.39–0.44 in A against a 0.10 base rate,
  0.53–0.54 in B against 0.20.
- **Forests are ahead of LightGBM in both cells, on p@20 and on
  PR-AUC.** B: 0.48–0.50 against 0.39–0.40, PR-AUC 0.327 against
  0.303. A: 0.37–0.39 against 0.33–0.35, PR-AUC 0.268 against 0.258.
  The B gap (0.08–0.10) is three or more seed standard deviations;
  the A gap is smaller and the families swap places year by year. LightGBM ran
  one untuned parameter set, so this compares two configurations,
  not two tuned families.
- **Inside the forest family nothing separates.** The four forest
  candidates span 0.48–0.50 in B and 0.37–0.39 in A, within one
  standard error (about 0.03). class_weight 1.0 has the better Brier
  (B: better than `base_rate_brier` in 9–10 of 16 years against 5
  for class_weight 0.5) at the same p@20 and PR-AUC.
- **The lift sits in entry years 2009–2018.** Forest family there:
  0.56 in A (base 0.15) and 0.69 in B (base 0.26). In 2005–08 the
  forests score 0.05 in A (base 0.05) and 0.15 in B (base 0.10); in
  2019, 9 hits in 240 picks in A and 3 in 240 in B (base 0.02 and
  0.09), with all twelve forest runs below the base rate in B. Those
  are the entry years whose 3-year window holds the 2008 or the 2020
  crash, and the base rate is at its lowest there (A: 0.02–0.10;
  B: 0.04–0.09 in 2006–08 and 2019, 0.21 in 2005).
  Explanation, untested: the models rank stocks by how calm they
  have been, which does not protect against a market-wide fall.
  2020 entries are above the base rate for forests (0.41 in B) and
  not for LightGBM (0.07).
- **PR-AUC beats the base rate in all 16 years** for every forest
  and LightGBM candidate, in both cells.
- **The value baselines are far below the base rate** (0.03–0.11),
  as on beat_spy: the cheapest stocks are rarely drawdown-free
  compounders. The random baseline sits at the base rate (0.110 and
  0.214, three seeds). The majority baseline's p@K is a tie-break
  and is not read.
- **What the models use.** `vol_12m_rank` + `vol_36m_rank` hold 0.53
  of the forest importance in A and 0.42 in B (LightGBM: 0.47 and
  0.31). The forest share is 0.38–0.50 in the 2005–12 folds and
  0.45–0.56 in the 2013–20 folds, so it does not fade. Next in B: `ret_1m_rank`, `conservative_score_rank`,
  `ocf_yield_rank`.

Open, and what would close it:

- **Is this more than a low-volatility screen?** No baseline in
  these cells ranks on volatility. Lift over book-to-market or over
  random is not evidence against "buy the calmest stocks".
  `baseline_lowvol_rank_3y` is written to test it, with its reading
  stated in the config.
- **Treat the size of the lift as suspect until that baseline has
  run** (a result far above baseline is leakage first). What was
  checked: tags, rows and effective sizes are the beat_spy cell's,
  which shows no such lift with the same code; labels are loader
  expressions over the manifest's label columns. What was not: that
  the top 20 rows are different stocks. p@K counts test rows, a
  stock has up to four median rows per test year, and in A every one
  of the twelve forest runs scored 20 of 20 in 2009. If the 20 rows
  are five stocks, the standard errors quoted here are too small.
  Needs distinct-`permaticker` counts for the picks in the report.
- **Scores are not probabilities.** conf@20 is 0.46–0.48 for the
  class_weight 1.0 forests against a realized 0.37–0.39 in A and
  0.50 in B, and Brier beats the no-skill reference in about half
  the years only.

**Decision: no holdout look in either cell.** The candidates are
untuned and have not met their real baseline. Both cells stay
unopened.

## Derived-label cells (dataset_v1.4, single seeds)

| label | model | p@20 | base rate | note |
|---|---|---|---|---|
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` | lightgbm | 0.36 | 0.11 | 3.2× the base rate, the largest relative lift so far (promoted) |
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` | lightgbm | 0.40–0.42 | 0.21 | `lgbm_drawdown_rungs_3y` (promoted) |
| `… < 0.3` / `… < 0.4` / no drawdown clause | lightgbm | 0.35–0.42 | 0.25 / 0.28 / 0.34 | same sweep; p@20 stays ~0.4 while the base rate falls, so the lift grows as the rung tightens |
| `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` | decision_tree d3 | 0.49 | 0.39 | `tree_depth3_3y_survive_dd30` |
| `fwd_3y_excess_cagr >= 0.08` | xgboost ×120 | 0.22 mean (0.31 max) | 0.22 | **no skill** (promoted as a negative) |
| `fwd_3y_excess_cagr >= 0.08` | random_forest + isotonic | 0.12 | 0.22 | below the base rate |
| `fwd_1y_excess_cagr >= 0.5 \| fwd_1y_max_drawdown_from_entry < 0.1 & fwd_3y_excess_cagr > 0` | lightgbm | 0.20 | 0.22 | no skill |

- **Drawdown-constrained compounding looks learnable; large excess
  return does not.** Absolute "compound without a crash" targets beat
  their base rates by 1.5–3×, while "beat SPY by 8 points" sits at the
  base rate across 120 xgb configs and a forest. This is the most
  promising new direction. The rows of this table are one seed each
  and had no baseline in their cell when written. The first two
  cells have since been run on three seeds with baselines and held
  (2026-09-28, section above); the other rows are still single
  seeds.
- In `lgbm_drawdown_rungs_3y`, class_weight 0.25–0.5 beat 1.0 on one
  seed; over three seeds (section above) 0.25 and 0.5 are level. Its
  feature axis was a no-op: the `ranks` group already contains the
  `*_vs_5y_median_rank` columns, so `+ ranks/relvalue` added nothing
  (identical numbers in both arms; the column count was written here
  as 125, but `ranks` resolves to 112 columns on v1.4 and the
  sweep's per-run files are gone, so its count is unverified).

## Earlier work (dataset_v1.0 / v1.1, July – August)

- 1y/2y/5y beat_spy and cagr_ge_0 LightGBM feature-set sweeps
  (`lightgbm_sweep_4fs_*`, `lgbm_spy_*`): rank features beat raw
  features at 1y/2y/5y beat_spy on v1.0 (p@10 ~0.73–0.83 against
  ~0.37–0.53). Metrics were p@10/p@50 on few seeds, so treat these as
  directional only.
- `lgbm_precision_grid_1-2y_absFeatures` (v1.0): 1y cagr_ge_0 p@50
  0.72 mean against a random baseline of 0.53. **2y cagr_ge_0 and 2y
  cagr_ge_10 were below the random baseline** (0.31 against 0.54, 0.11
  against 0.39), which is worth remembering before running raw-feature
  models on 2y absolute labels.
- Depth-limited trees (experiments 4–14, `tree_depth*`): interpretable
  but weak off 2y cagr_ge_0; `tree_depth3_2y_cagr_ge_0` is promoted with
  its rules.

## Sealed holdout record

From `reports/final_evals.csv` (19 looks; the counts are part of every
holdout number). PR-AUC against the base rate, holdout test year in
brackets:

| cell | looks | what the looks showed |
|---|---|---|
| 2y cagr_ge_0 (v1.0 [2022], v1.1 [2022]) | 3 + 2 | PR-AUC 0.62–0.68 vs base 0.51 |
| 1y cagr_ge_0 (v1.1 [2023]) | 3 | PR-AUC 0.59–0.65 vs 0.51 |
| 1y beat_spy (v1.1 [2023]) | 3 | 0.29–0.31 vs 0.27, barely any skill |
| 2y beat_spy (v1.0, v1.1 [2022]) | 1 + 2 | technicals 0.20 vs 0.21 (**none**); valuation 0.26 |
| 5y beat_spy (v1.1 [2019]) | 2 | technicals 0.18 vs 0.17 (**none**); valuation 0.24 |
| 5y cagr_ge_0 (v1.1 [2019]) | 2 | 0.66–0.68 vs 0.50 |
| 2y cagr_ge_8 (v1.0) | 1 | p@20 0.35 vs 0.30 |

The Aug 24 batch opened 12 looks in ~50 minutes, comparing
technicals-vs-valuation pairs on the holdout. That is the pattern the
one-look-per-cell rule now prevents. Read those cells as consumed. The
one consistent signal: **technical-rank models had no holdout skill on
the relative (beat_spy) labels, and valuation/trend models kept some.**

## Process issues found in this review

- Sweep TOMLs were edited in place between runs.
  `forest_random_search_3y.toml` no longer matches its own summary, and
  `-2seeds` ran from an edit that was not kept. **Copy a sweep to a
  new file before changing it.** (2026-09-28: the `-2seeds` config was
  rebuilt and hash-verified. Every sweep now copies its config into
  its report directory, every run writes its full config and resolved
  feature columns beside its report, and a sweep whose file was edited
  is refused its old report directory.)
- The tracked `lgbm_random_search_3y.toml` and
  `lgbm_cagr_quantile_3y.toml` do not reproduce the config hashes of
  their ledger runs (0 of 57 and 0 of 144), so they are not the files
  that ran either. Their results have no verified config.
- Promoted sweep configs could not be loaded: `vml-promote --note`
  writes `note` into the file and the sweep parser rejected the key.
  Fixed 2026-09-28; `note` is outside the sweep identity and the run
  hashes.
- `forest_random_search_3y-2seeds2` finished its runs but never wrote a
  summary (interrupted before the summary step?). Its runs are in the
  ledger only.
- `vml-experiments sweeps` ranks rows that use different metrics (p@10,
  p@20, p@50) in one table. Read a row's metric before comparing it.
- `reports/final_evals.csv` and `reports/final_eval/` were untracked
  despite being "always tracked". Now committed.
- `lgbm_candidate_sets_3y.toml` is pinned to `dataset_v1.0` and was never
  run.

Found on 2026-09-27:

- An interrupted run was logged as `completed`: fold rows were written
  as each fold finished, so the first attempt at forest set0 seed 23
  (run `9f357ea6b798`, stopped after 5 of 16 folds) looks like a short
  finished run. **Fixed 2026-09-28**: fold rows are now written only
  once every fold has finished, and a stopped run (Ctrl-C included)
  leaves a single `failed` row. That one old run stays in the ledger
  (rows are never rewritten); the sweep summary used the full re-run,
  but a ledger query that averages by experiment name should skip it.
- The majority-class baseline's p@K is a tie-break over constant
  scores (0.00 to 0.50 by year). Only its Brier means anything.
- Forest set4 took about 78 minutes per run against 2–15 for the
  other sets, for no gain. Check the cost of a set before giving it
  three seeds.

Found on 2026-09-28 (evening):

- `forest_feature_ablation_3y` ran 8 runs, not 24: its header says
  three seeds and its body `seeds = [23]`. The summary is right about
  what ran. The missing seeds need a new config (a config that has
  run is not edited). **Read the `expanded runs` line of a summary
  against the config's header before reading its table.**
- The two ledger hashes of a re-run differ from the original's when
  the sweep name differs, because the name is inside the config
  hash. "Same configuration" across sweeps has to be shown on the
  parameters and the per-fold numbers (as done for the code control),
  or on a hash that leaves the name out.
- `data/versions.md` described v1.2 by its removed columns only. The
  changed values of the pinned rank columns are now in its v1.2 row.
- The compounder cells had only baselines that cannot win (value
  ranks, random). **A cell's baselines should include the single
  factor the label is closest to**, here volatility.
- This session worked in a clone of the repository: the ledger, the
  reports and the untracked configs were read from the host copy,
  and the three new configs are committed with `git add -f` so that
  they travel with the branch.

## Log

Newest first. One entry per working session: what ran, what it showed,
what's next. Record trial counts, not just winners.

### 2026-09-28 (evening): seven sweeps reviewed; code and added columns ruled out; compounder cells hold

- Ran (by Carter, 2026-09-27/28, git `86ef0c4`), 60 runs:
  `forest_feature_ablation_3y` (8 runs, one seed),
  `baseline_majority_` / `_random_` / `_rank_factor_drawdown_compounder_3y`
  (2 + 6 + 4), `forest_drawdown_compounder_seeds_3y` (24),
  `lgbm_drawdown_compounder_seeds_3y` (12),
  `forest_v11_code_control_3y` (4, on `dataset_v1.1`). No failures.
  Trial counts now: 3y beat_spy 39 on v1.4 and 717 on v1.1;
  compounder cell A 25, cell B 30.
- Showed: (1) today's code reproduces the August v1.1 fold rows
  exactly; (2) the v1.1 column set on v1.4 scores p@20 0.44, not the
  0.58 predicted if the added columns were the cause, though
  removing them raises PR-AUC by 0.01–0.02; (3) no ablation arm can
  be told from another; (4) the compounder cells hold over three
  seeds and after 2013, forests ahead of LightGBM, no lift in the
  crash-window entry years.
- Checked on the parquet files (no harness run): 17 of the 120
  shared columns changed values at v1.2 (decision 0016).
- Wrote three configs, dry-run clean, resolved columns checked
  against both manifests (120 / 103 / 103), none run:
  `baseline_lowvol_rank_3y` (12 runs),
  `forest_v11_column_control_3y` (8),
  `forest_v14_unchanged_columns_3y` (4).
- Nothing promoted, no holdout look.
- Next: "Plan as of 2026-09-28" at the top. First the low-volatility
  baseline, then the column controls.

### 2026-09-28: the non-replication claim withdrawn; configs now travel with reports

- Carter questioned the 2026-09-27 conclusion: the v1.1 sweep's
  config was lost, so what the v1.4 runs were being compared with was
  not known. Checked it. The config was recoverable (100 of 100
  hashes), the spec and parameters were the right ones, the rows are
  identical, and the columns are not: 13 added, 4 dropped. The claim
  "did not replicate" is withdrawn; "scores lower on a different
  column set, cause open" replaces it. Promoted notes reworded.
- What went wrong in the reasoning is written up in CLAUDE.md,
  "Before writing a conclusion".
- Wrote `forest_v11_code_control_3y` (4 runs); it and the ablation
  now come before the drawdown-compounder sweeps.
- Code: config copies in report directories, `note` accepted in sweep
  files (above, under process issues). No experiments run.

### 2026-09-28: interrupted runs no longer log as completed

- Code only, no experiments run. `RunLog` in `src/harness/results.py`
  holds a run's fold rows until the last fold finishes; used by
  `vml-run` / `vml-sweep`, `vml-eval` and the era probe. Regression
  test in `tests/test_runner.py`. A process that is killed outright
  (OOM, `kill -9`) still leaves no row at all.

### 2026-09-27: v1.4 carry-forward sweeps reviewed

- Ran (by Carter, 2026-09-26/27, git `b649c58`): the v1.4 baseline
  grid (80 runs), `forest_candidate_sets_3y` (18 runs, plus one
  interrupted) and `xgb_candidate_sets_3y` (9 runs). 31 configurations
  in the 3y beat_spy cell on v1.4.
- Showed (as read that day; see the 2026-09-28 entry for the
  correction): neither family replicates. Forests p@20 0.42 pooled, 0.59
  in 2005–12, 0.22 in 2013–19 (base 0.28); xgb 0.37 / 0.54 / 0.17.
  PR-AUC stays above the base rate every year. Details in "3y beat_spy
  on dataset_v1.4".
- Promoted 3 (two sweep summaries as negatives, one era report). No
  holdout look.
- Wrote six sweep configs (git-ignored until promoted), all dry-run
  clean, none run: `forest_feature_ablation_3y` (24 runs),
  `lgbm_drawdown_compounder_seeds_3y` (12),
  `forest_drawdown_compounder_seeds_3y` (24), and the random /
  rank-factor / majority baselines for the two drawdown-compounder
  cells (6 + 4 + 2).
- Next: run the three baseline sweeps, then the two compounder
  sweeps, then the ablation. Read each era table before the pooled
  number. If the compounder lift also sits in 2005–12 only, the
  problem is the post-2013 regime and not the label.

### 2026-09-26: review after the August/September hiatus

- Reviewed the ledger, every sweep summary and the holdout record. Wrote
  this file.
- Promoted 7 results (see `reports/promoted/README.md`), including 2
  negatives.
- Wrote `forest_candidate_sets_3y` / `xgb_candidate_sets_3y` (v1.4).
- Cleared the working tree (archived outside the repo first): 87
  untracked configs, unpromoted reports, walk-forward bundles and cached
  refits. Kept: the ledger, the holdout record, promoted reports, tracked
  configs, and the 16 deployment bundles.
- Next: v1.4 baselines → both carry-forward sweeps → compare the family
  era slices → multi-seed the drawdown-compounder label with a v1.4
  baseline.
