# 3y beat_spy: model families on dataset_v1.1

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

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
