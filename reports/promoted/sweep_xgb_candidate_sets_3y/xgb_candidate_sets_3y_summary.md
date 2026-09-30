# Sweep summary — xgb_candidate_sets_3y

- sweep config: `experiments/sweeps/xgb_candidate_sets_3y.toml`
- dataset version: `dataset_v1.4` (pinned, immutable)
- scheme: `walkforward`, folds: `all`, git `b649c58e1d8c19bd5fe35da9f4cfec3cfed01da9`
- model family: `xgboost`, fixed params `{"device": "cuda"}`
- grid: `{}`
- parameter sets (3, each taken as a unit):
  - `set0`: `{"class_weight": 0.1, "colsample_bytree": 0.638389, "gamma": 0.00994761, "learning_rate": 0.0113265, "max_depth": 6, "min_child_weight": 59.9175, "n_estimators": 195, "reg_alpha": 0.000140183, "reg_lambda": 0.418799, "subsample": 0.887142}`
  - `set1`: `{"class_weight": 0.5, "colsample_bytree": 0.407286, "gamma": 0.000106243, "learning_rate": 0.0118662, "max_depth": 8, "min_child_weight": 89.3656, "n_estimators": 556, "reg_alpha": 0.436331, "reg_lambda": 21.3796, "subsample": 0.6872}`
  - `set2`: `{"class_weight": 0.5, "colsample_bytree": 0.825382, "gamma": 4.79144, "learning_rate": 0.126577, "max_depth": 6, "min_child_weight": 5.09555, "n_estimators": 274, "reg_alpha": 4.30687, "reg_lambda": 0.235585, "subsample": 0.920096}`
- expanded runs: 9 (0 failed), seeds [23, 232, 1776]
- 3 candidates × 3 seeds: ranked by the **mean** pooled `precision_at_20` across seeds (higher is better), with its std / min / max / 95% t-interval lower bound beside it; one seed-stability report per candidate (`<candidate>.md`, pooled and per-era spread), every metric's across-seed statistics in `xgb_candidate_sets_3y_summary_seeds.csv`, per-seed run reports under `seeds/`

**This ranking is model selection on walk-forward folds.** The winner's numbers are selection-biased by every configuration tried below (and before); they are candidates for the sealed holdout, never final results. Pooled numbers here are for ranking only — the per-candidate reports in this directory carry the era-sliced spread across seeds, and the per-seed reports under `seeds/` the full era tables, that an honest read requires.

## Trial ledger

- `label_3y_beat_spy` (3y): 31 configurations ever tried against this cell (append-only ledger, failures included)

## Ranked candidates (mean over seeds of the pooled metrics)

| candidate                                      | seeds_completed | label             | param_set | grid_params | precision_at_20_mean | precision_at_20_std | precision_at_20_min | precision_at_20_max | precision_at_20_ci95_low | recall_at_prec_0.75_mean | n_at_prec_0.75_mean | recall_at_prec_0.9_mean | n_at_prec_0.9_mean | conf_at_20_mean | recall_at_20_mean | precision_at_50_mean | conf_at_50_mean | recall_at_50_mean | pr_auc_mean | brier_mean | base_rate_brier_mean | base_rate_mean |
| ---------------------------------------------- | --------------- | ----------------- | --------- | ----------- | -------------------- | ------------------- | ------------------- | ------------------- | ------------------------ | ------------------------ | ------------------- | ----------------------- | ------------------ | --------------- | ----------------- | -------------------- | --------------- | ----------------- | ----------- | ---------- | -------------------- | -------------- |
| xgb_candidate_sets_3y__label_3y_beat_spy__set0 | 3/3             | label_3y_beat_spy | 0         | {}          | 0.3813               | 0.0094              | 0.3719              | 0.3906              | 0.3580                   | 0.0007                   | 80.3333             | 0.0002                  | 17.3333            | 0.2770          | 0.0013            | 0.3746               | 0.2590          | 0.0032            | 0.4435      | 0.2856     | 0.2285               | 0.3535         |
| xgb_candidate_sets_3y__label_3y_beat_spy__set1 | 3/3             | label_3y_beat_spy | 1         | {}          | 0.3688               | 0.0063              | 0.3625              | 0.3750              | 0.3532                   | 0.0003                   | 31.6667             | 0.0001                  | 12.3333            | 0.6991          | 0.0013            | 0.3671               | 0.6656          | 0.0032            | 0.4448      | 0.2229     | 0.2285               | 0.3535         |
| xgb_candidate_sets_3y__label_3y_beat_spy__set2 | 3/3             | label_3y_beat_spy | 2         | {}          | 0.3573               | 0.0118              | 0.3438              | 0.3656              | 0.3279                   | 0.0003                   | 29.3333             | 0.0002                  | 18                 | 0.6917          | 0.0012            | 0.3542               | 0.6594          | 0.0030            | 0.4412      | 0.2233     | 0.2285               | 0.3535         |

A candidate is only as good as its worst seed: read `_min` and `_ci95_low` before `_mean`. With few seeds the t-interval is wide by construction — that is the honest width.

Full pooled metrics for every run: `xgb_candidate_sets_3y_summary.csv`. Per-run reports (era slices, crash eras, calibration, baselines): `seeds/<run name>.md`; seed-stability reports: `<candidate>.md` in this directory.
