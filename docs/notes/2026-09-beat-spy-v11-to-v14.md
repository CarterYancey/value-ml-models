# 3y beat_spy: why v1.4 scores lower than v1.1

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

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
`forest_feature_ablation_3y`, `dataset_v1.4`, 8 runs on one seed.
Carter cut the config from three seeds to one on purpose: the
question was the comparison with v1.1, which one seed answers (the
header comment still describes 24 runs). 39 configurations tried in this cell on v1.4 (717 on
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

**4. Column controls: the edge is in the v1.1 values of the 17
changed columns.** Added 2026-09-28 (night).
`forest_v11_column_control_3y` (8 runs, `dataset_v1.1`) and
`forest_v14_unchanged_columns_3y` (4 runs, `dataset_v1.4`), git
`3f2bfdf`, seeds 23 and 232, r30 and r48. The report directories'
config copies are identical to the committed files, and each run's
`*_config.json` gives the expected column count (120, 103, 103).
Trial counts after them: 725 on v1.1, 47 on v1.4.

Seed-mean fold-mean p@20 (two seeds; the v1.4 120-column row is arm
fs0 of the ablation, seed 23 only, and exists for r48 alone):

| set | dataset, columns | pooled | 2005–12 | 2013–20 | 2013–19 | PR-AUC |
|---|---|---|---|---|---|---|
| r30 | v1.1, all 124 | 0.589 | 0.694 | 0.484 | 0.446 | 0.427 |
| r30 | v1.1, 120 (four dropped columns out) | 0.583 | 0.678 | 0.488 | 0.450 | 0.427 |
| r30 | v1.1, 103 (17 changed columns out too) | 0.430 | 0.587 | 0.272 | 0.257 | 0.418 |
| r30 | v1.4, the same 103 | 0.430 | 0.587 | 0.272 | 0.257 | 0.418 |
| r30 | v1.4, carry-forward spec (133) | 0.427 | 0.569 | 0.284 | 0.254 | 0.403 |
| r48 | v1.1, all 124 | 0.583 | 0.659 | 0.506 | 0.464 | 0.429 |
| r48 | v1.1, 120 | 0.570 | 0.647 | 0.494 | 0.450 | 0.429 |
| r48 | v1.1, 103 | 0.466 | 0.625 | 0.306 | 0.300 | 0.420 |
| r48 | v1.4, the same 103 | 0.466 | 0.625 | 0.306 | 0.300 | 0.420 |
| r48 | v1.4, 120 (the 17 in pinned form; seed 23) | 0.441 | 0.562 | 0.319 | 0.293 | 0.424 |
| r48 | v1.4, carry-forward spec (133) | 0.430 | 0.597 | 0.262 | 0.225 | 0.413 |
| | base rate | 0.35 | 0.41 | 0.29 | 0.28 | |

Per test year, v1.1, seed-mean p@20 with and without the 17:

| year | base | r30, 120 | r30, 103 | r48, 120 | r48, 103 |
|---|---|---|---|---|---|
| 2005 | 0.41 | 0.82 | 0.75 | 0.70 | 0.95 |
| 2006 | 0.46 | 0.60 | 0.80 | 0.60 | 0.70 |
| 2007 | 0.46 | 0.78 | 0.73 | 0.85 | 0.75 |
| 2008 (GFC) | 0.46 | 0.85 | 0.77 | 0.92 | 0.60 |
| 2009 (GFC) | 0.44 | 0.52 | 0.57 | 0.57 | 0.50 |
| 2010 | 0.36 | 0.68 | 0.20 | 0.52 | 0.38 |
| 2011 | 0.32 | 0.60 | 0.45 | 0.48 | 0.60 |
| 2012 | 0.34 | 0.57 | 0.42 | 0.52 | 0.52 |
| 2013 | 0.32 | 0.52 | 0.43 | 0.60 | 0.55 |
| 2014 | 0.30 | 0.55 | 0.20 | 0.57 | 0.18 |
| 2015 | 0.30 | 0.68 | 0.32 | 0.65 | 0.43 |
| 2016 | 0.31 | 0.72 | 0.35 | 0.52 | 0.43 |
| 2017 | 0.24 | 0.18 | 0.30 | 0.10 | 0.05 |
| 2018 | 0.26 | 0.12 | 0.02 | 0.30 | 0.18 |
| 2019 | 0.27 | 0.38 | 0.18 | 0.40 | 0.30 |
| 2020 (COVID) | 0.33 | 0.75 | 0.38 | 0.80 | 0.35 |

Against the predictions written in the configs:

- **The four dropped columns are not the cause.** Without them the
  v1.1 runs score 0.583 and 0.570 against 0.589 and 0.583 with them,
  inside the seed spread, and PR-AUC is the same to 0.002 in every
  year. Reading (a) is ruled out.
- **Nothing else differs between the versions.** On the 103
  unchanged columns all 64 fold rows of the v1.1 runs equal those of
  the v1.4 runs: counts, base rates, p@20, PR-AUC and ROC-AUC
  exactly, Brier to within 1e-16. As predicted.
- **Taking the 17 out of the v1.1 runs takes the edge out:** 0.583 →
  0.430 (r30) and 0.570 → 0.466 (r48) pooled, 0.49 → 0.27–0.31 in
  2013–20, higher with the 17 in 12–13 of 16 years, PR-AUC 0.427 →
  0.418 and 0.429 → 0.420. The difference is after 2009: over
  2005–09 the two are level on average.
- **In their pinned v1.4 form the 17 add nothing at the top of the
  ranking** (r48, seed 23: 0.441 with them, 0.469 without) and
  0.004 of PR-AUC.

So what was measured: the v1.1 forest results on 3y beat_spy depend
on the v1.1 form of 17 rank columns, the form decision 0016 removed
because it lets a model identify the calendar quarter. The same
columns that let `entity_holdout` models date a row are the ones
whose removal costs the walk-forward forests 0.10–0.15 of p@20.

What that means is a hypothesis, with two readings that no run has
separated:

- *Quarter information.* A v1.1 rank of a mass-point feature mixes
  the stock's standing with the share of the quarter's cross-section
  sitting on the mass point, for every row and not only the tied
  ones. That share is a market-state variable. A walk-forward test
  quarter is unseen, so the model cannot look its base rate up, but
  it can have learned how the state relates to outcomes, and top-20
  per *year* rewards choosing the right quarter of the year. On
  this reading the v1.1 p@20 was partly market timing, and decision
  0016's note that walk-forward is not inflated by the keys is too
  strong.
- *Stock information.* The re-mapping changed how the non-tied
  stocks are spread (mean absolute change up to 0.23 of rank), and
  the v1.1 spread may have suited shallow trees better.

What would separate them: p@K within each test quarter on v1.1 (an
edge that came from choosing the quarter disappears; one that came
from choosing the stock stays), or the distribution of the v1.1
picks over the four quarters of each test year. Both need per-row
predictions or per-quarter metrics from the harness. Worth a note
upstream either way, because it bears on decision 0016. It does not
bear on what to run next: the v1.1 form is gone from every dataset
after v1.1, including the inference datasets.

Written before the column controls ran (evening): between the v1.1
runs and fs0 two things differ, and nothing else that was checked (rows, code,
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
(They have run: item 4 above. It is (b).)

**5. A single factor matches the forests on v1.4.**
`baseline_lowvol_rank_3y`, beat_spy cell, one deterministic run per
factor. Fold-mean p@20:

| factor | pooled | 2005–12 | 2013–20 | years above base (of 16) | PR-AUC |
|---|---|---|---|---|---|
| highest `conservative_score_rank` | 0.491 | 0.544 | 0.438 | 12 | 0.415 |
| lowest `vol_36m_rank` | 0.378 | 0.462 | 0.294 | 9 | 0.418 |
| lowest `beta_12m_rank` | 0.231 | 0.262 | 0.200 | 3 | 0.324 |
| lowest `vol_12m_rank` | 0.178 | 0.256 | 0.100 | 1 | 0.411 |
| forests, carry-forward spec (18 runs) | 0.42 | 0.59 | 0.26 | | 0.41 |
| forest ablation arms (8 runs, one seed) | 0.44–0.54 | 0.56–0.65 | 0.28–0.44 | | 0.42 |
| base rate | 0.35 | 0.41 | 0.29 | | |

`conservative_score_rank` on its own is level with the best
ablation arm in 2013–20 (0.438) and above the other seven; it is
0.60–0.80 in 2013–16 and 0.10–0.20 in 2017, 2019 and 2020. It is an
upstream composite of low volatility, momentum and net payout. 47
configurations on v1.4 have not produced a forest that is clearly
better than it.

**What this changes.** The v1.1 forest numbers cannot be reproduced
on any dataset from v1.2 on, because the columns no longer exist in
that form. The v1.1
findings stay as found on v1.1. Candidates for 3y beat_spy have to
be found on v1.4, and on v1.4 nothing tried so far has an edge after
2013 that holds across parameter sets.

**Decision: no 3y beat_spy holdout look.** There is no candidate one
would act on yet. The cell stays unopened.

Promoted (2026-09-27, notes revised 2026-09-28):
`sweep_forest_candidate_sets_3y`, `sweep_xgb_candidate_sets_3y`, and
the era report of forest set3, seed 23.
