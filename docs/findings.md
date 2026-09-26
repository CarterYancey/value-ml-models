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

## State as of 2026-09-26

- **Ledger:** `experiments/results.csv` holds ~1,570 walk-forward runs
  (≈25.8k fold rows) across `dataset_v1.0`, `v1.1` and `v1.4`. Results
  are never compared across versions; the v1.1 work below has to be
  re-validated on v1.4 before it counts for anything current.
- **Baselines exist on `dataset_v1.0` only.** No v1.1 or v1.4 cell has a
  same-version baseline, so the catalog shows `none run` and no lift for
  every recent result. First action of the next session:
  `uv run python scripts/run_baselines.py dataset_v1.4`.
- **Sealed holdout:** 19 looks in `reports/final_evals.csv` (listed
  below). **Every 3y cell is still unopened**, including 3y beat_spy,
  where almost all Phase-3 work happened.
- **Carry-forward configs:** `experiments/sweeps/forest_candidate_sets_3y.toml`
  and `experiments/sweeps/xgb_candidate_sets_3y.toml` re-run the
  Aug/Sep winners on v1.4 (18 + 9 runs), the same cell, features and
  seeds for both, so the family comparison is like for like.

## 3y beat_spy: model families (dataset_v1.1)

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
  v1.4 baseline yet.
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
  `-2seeds` ran from an uncommitted edit that doesn't exist anymore.
  **Copy a sweep to a new file before changing it**; the summary header
  is the only surviving record of the original.
- `forest_random_search_3y-2seeds2` finished its runs but never wrote a
  summary (interrupted before the summary step?). Its runs are in the
  ledger only.
- `vml-experiments sweeps` ranks rows that use different metrics (p@10,
  p@20, p@50) in one table. Read a row's metric before comparing it.
- `vml-promote`'s own `git add` failed for all seven promotions on
  2026-09-26 (staged by hand; not reproducible afterwards).
- `reports/final_evals.csv` and `reports/final_eval/` were untracked
  despite being "always tracked". Now committed.
- `lgbm_candidate_sets_3y.toml` is pinned to `dataset_v1.0` and was never
  run.

## Log

Newest first. One entry per working session: what ran, what it showed,
what's next. Record trial counts, not just winners.

### 2026-09-26: review after the August/September hiatus

- Reviewed the ledger, every sweep summary and the holdout record. Wrote
  this file.
- Promoted 7 results (see `reports/promoted/README.md`), including 2
  negatives.
- Wrote `forest_candidate_sets_3y` / `xgb_candidate_sets_3y` (v1.4).
- Next: v1.4 baselines → both carry-forward sweeps → compare the family
  era slices → multi-seed the drawdown-compounder label with a v1.4
  baseline.
