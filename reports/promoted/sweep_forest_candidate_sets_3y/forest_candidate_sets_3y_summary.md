# Sweep summary — forest_candidate_sets_3y

- sweep config: `experiments/sweeps/forest_candidate_sets_3y.toml`
- dataset version: `dataset_v1.4` (pinned, immutable)
- scheme: `walkforward`, folds: `all`, git `b649c58e1d8c19bd5fe35da9f4cfec3cfed01da9`
- model family: `random_forest`, fixed params `{"bootstrap": true, "class_weight": 1.0, "n_jobs": 8}`
- grid: `{}`
- parameter sets (6, each taken as a unit):
  - `set0`: `{"criterion": "gini", "max_depth": 3, "max_features": 0.914775, "max_samples": 0.441152, "min_samples_leaf": 248, "n_estimators": 126}`
  - `set1`: `{"criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490}`
  - `set2`: `{"criterion": "gini", "max_depth": 3, "max_features": 0.205, "max_samples": 1.0, "min_samples_leaf": 123, "n_estimators": 133}`
  - `set3`: `{"criterion": "entropy", "max_depth": 3, "max_features": 0.504, "max_samples": 0.589, "min_samples_leaf": 38, "n_estimators": 407}`
  - `set4`: `{"criterion": "entropy", "max_depth": 3, "max_features": 0.408, "max_samples": 1.0, "min_samples_leaf": 133, "n_estimators": 300}`
  - `set5`: `{"criterion": "entropy", "max_depth": 13, "max_features": 0.205, "max_samples": 0.281, "min_samples_leaf": 173, "n_estimators": 389}`
- expanded runs: 18 (0 failed), seeds [23, 232, 1776]
- 6 candidates × 3 seeds: ranked by the **mean** pooled `precision_at_20` across seeds (higher is better), with its std / min / max / 95% t-interval lower bound beside it; one seed-stability report per candidate (`<candidate>.md`, pooled and per-era spread), every metric's across-seed statistics in `forest_candidate_sets_3y_summary_seeds.csv`, per-seed run reports under `seeds/`

**This ranking is model selection on walk-forward folds.** The winner's numbers are selection-biased by every configuration tried below (and before); they are candidates for the sealed holdout, never final results. Pooled numbers here are for ranking only — the per-candidate reports in this directory carry the era-sliced spread across seeds, and the per-seed reports under `seeds/` the full era tables, that an honest read requires.

## Trial ledger

- `label_3y_beat_spy` (3y): 22 configurations ever tried against this cell (append-only ledger, failures included)

## Ranked candidates (mean over seeds of the pooled metrics)

| candidate                                         | seeds_completed | label             | param_set | grid_params | precision_at_20_mean | precision_at_20_std | precision_at_20_min | precision_at_20_max | precision_at_20_ci95_low | recall_at_prec_0.75_mean | n_at_prec_0.75_mean | recall_at_prec_0.9_mean | n_at_prec_0.9_mean | conf_at_20_mean | recall_at_20_mean | precision_at_50_mean | conf_at_50_mean | recall_at_50_mean | pr_auc_mean | brier_mean | base_rate_brier_mean | base_rate_mean |
| ------------------------------------------------- | --------------- | ----------------- | --------- | ----------- | -------------------- | ------------------- | ------------------- | ------------------- | ------------------------ | ------------------------ | ------------------- | ----------------------- | ------------------ | --------------- | ----------------- | -------------------- | --------------- | ----------------- | ----------- | ---------- | -------------------- | -------------- |
| forest_candidate_sets_3y__label_3y_beat_spy__set3 | 3/3             | label_3y_beat_spy | 3         | {}          | 0.4354               | 0.0095              | 0.4250              | 0.4437              | 0.4117                   | 0.0023                   | 278.6667            | 0.0002                  | 19.3333            | 0.6920          | 0.0015            | 0.4208               | 0.6883          | 0.0036            | 0.4527      | 0.2398     | 0.2285               | 0.3535         |
| forest_candidate_sets_3y__label_3y_beat_spy__set2 | 3/3             | label_3y_beat_spy | 2         | {}          | 0.4323               | 0.0213              | 0.4156              | 0.4562              | 0.3795                   | 0.0016                   | 190                 | 0.0002                  | 16                 | 0.6593          | 0.0015            | 0.4183               | 0.6560          | 0.0036            | 0.4595      | 0.2396     | 0.2285               | 0.3535         |
| forest_candidate_sets_3y__label_3y_beat_spy__set1 | 3/3             | label_3y_beat_spy | 1         | {}          | 0.4292               | 0.0018              | 0.4281              | 0.4313              | 0.4247                   | 0.0010                   | 118.3333            | 0.0002                  | 21                 | 0.7093          | 0.0015            | 0.4108               | 0.6998          | 0.0035            | 0.4568      | 0.2386     | 0.2285               | 0.3535         |
| forest_candidate_sets_3y__label_3y_beat_spy__set4 | 3/3             | label_3y_beat_spy | 4         | {}          | 0.4240               | 0.0090              | 0.4188              | 0.4344              | 0.4015                   | 0.0022                   | 271.6667            | 0.0001                  | 9                  | 0.6845          | 0.0015            | 0.4154               | 0.6825          | 0.0036            | 0.4513      | 0.2400     | 0.2285               | 0.3535         |
| forest_candidate_sets_3y__label_3y_beat_spy__set0 | 3/3             | label_3y_beat_spy | 0         | {}          | 0.4177               | 0.0280              | 0.4000              | 0.4500              | 0.3481                   | 0.0021                   | 258                 | 0.0002                  | 22                 | 0.7107          | 0.0014            | 0.4154               | 0.7080          | 0.0036            | 0.4486      | 0.2406     | 0.2285               | 0.3535         |
| forest_candidate_sets_3y__label_3y_beat_spy__set5 | 3/3             | label_3y_beat_spy | 5         | {}          | 0.4010               | 0.0065              | 0.3937              | 0.4062              | 0.3849                   | 0.0030                   | 364.6667            | 0.0003                  | 27.6667            | 0.7634          | 0.0014            | 0.3925               | 0.7448          | 0.0034            | 0.4549      | 0.2380     | 0.2285               | 0.3535         |

A candidate is only as good as its worst seed: read `_min` and `_ci95_low` before `_mean`. With few seeds the t-interval is wide by construction — that is the honest width.

Full pooled metrics for every run: `forest_candidate_sets_3y_summary.csv`. Per-run reports (era slices, crash eras, calibration, baselines): `seeds/<run name>.md`; seed-stability reports: `<candidate>.md` in this directory.
