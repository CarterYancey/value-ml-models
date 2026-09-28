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

## State as of 2026-09-28

- **The Aug/Sep forest and xgb winners score lower on `dataset_v1.4`
  than on `v1.1`, and the cause is not isolated** (next section).
  Same parameters, same feature spec, same train and test rows; the
  spec resolves to a different column set (13 added, 4 dropped). Two
  sweeps are written to find the cause. Until they run, the v1.1
  findings are neither confirmed nor refuted, and no finalist exists
  for the 3y beat_spy holdout.
- **Ledger:** `experiments/results.csv` holds the ~1,570 walk-forward
  runs reviewed on 2026-09-26 (`dataset_v1.0`, `v1.1`, `v1.4`) plus
  108 new `v1.4` runs: the baseline grid and the two carry-forward
  sweeps. Results are never compared across versions.
- **Baselines now exist on `dataset_v1.4`** for the 20 stored-label
  cells (1/2/3/5y × cagr_ge_0/5/8/10 and beat_spy; 80 runs, seed 7).
  Derived-label cells still have none: `scripts/run_baselines.py`
  covers stored labels only.
- **Sealed holdout:** 19 looks in `reports/final_evals.csv` (listed
  below), unchanged. **Every 3y cell is still unopened.**
- **Next-step configs** (written 2026-09-27/28, not yet run), in
  order: `forest_v11_code_control_3y`,
  `forest_feature_ablation_3y`, `lgbm_drawdown_compounder_seeds_3y`,
  `forest_drawdown_compounder_seeds_3y` and three
  `baseline_*_drawdown_compounder_3y` sweeps, all in
  `experiments/sweeps/`.

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
- **Not verified:** whether the 120 shared columns hold the same
  values in both versions (`data/versions.md` says v1.4 is additive;
  neither dataset was available to check), and whether the code
  changes between git `e587a66` (v1.1 runs) and `b649c58` (v1.4 runs)
  affect a fit or a metric.

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
  they held 0.06% of the impurity importance in the v1.1 lead run
  (ranks 52, 58, 75 and 103 of 124). Importance is a weak witness,
  so "probably".
- **The 13 added columns are the leading suspect, untested.** They
  hold 18% of the importance in v1.4 set3, and two are in its top
  ten. That a forest gets worse when offered more columns is
  possible (shallow trees, `max_features` below 1) but it is a
  hypothesis until `forest_feature_ablation_3y` runs.
- **A code change is the other suspect**, tested by
  `forest_v11_code_control_3y`.
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

**Decision: no 3y beat_spy holdout look.** There is no candidate one
would act on yet. The cell stays unopened.

Promoted (2026-09-27, notes revised 2026-09-28):
`sweep_forest_candidate_sets_3y`, `sweep_xgb_candidate_sets_3y`, and
the era report of forest set3, seed 23.

## 3y beat_spy: model families (dataset_v1.1)

Found on v1.1 and not yet confirmed on v1.4: the same configurations
score lower there, on a different column set, for a reason still
being isolated (section above).

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
  promising new direction, but everything here is one seed and has no
  baseline in its cell (the v1.4 baseline grid covers stored labels
  only). After the 3y beat_spy non-replication, read these as
  unconfirmed: the seed-stability sweeps and cell baselines written on
  2026-09-27 are the test, and the era table matters as much as the
  pooled lift (beat_spy's lift was all 2005–12).
- In `lgbm_drawdown_rungs_3y`, class_weight 0.25–0.5 beat 1.0. Its
  feature axis was a no-op: the `ranks` group already contains the
  `*_vs_5y_median_rank` columns, so `+ ranks/relvalue` added nothing
  (125 features in both arms, identical numbers).

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

## Log

Newest first. One entry per working session: what ran, what it showed,
what's next. Record trial counts, not just winners.

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
