# Experiment report — lightgbm_ranks-valuation-ranks-trend_2y_cagr_ge_0_e8728774

- run id: `c243dcac0620`
- dataset version: `1.1` (pinned, immutable)
- config hash: `27bcd39f2ddaf342`
- git SHA: `60768d70fa2a848eabc08bd73031084eb0d3e096`
- seed: 23
- model: `lightgbm` params `{"class_weight": 1.0, "learning_rate": 0.03, "min_child_samples": 500, "n_estimators": 800, "num_leaves": 3, "reg_lambda": 0}`
- label: `label_2y_cagr_ge_0` — horizon 2y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 1** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era               | n_test | base_rate | precision_at_35 | conf_at_35 | brier  | base_rate_brier | pr_auc |
| ----------------- | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2022 (rate-shock) | 18267  | 0.5158    | 0.8286          | 0.8702     | 0.2369 | 0.2497          | 0.6259 |
| 2023              | 16875  | 0.5020    | 0.7714          | 0.8977     | 0.2403 | 0.2500          | 0.6273 |
| 2024              | 10445  | 0.5028    | 0.8571          | 0.9021     | 0.2435 | 0.2500          | 0.6263 |
| pooled*           | 45587  | 0.5078    | 0.8190          | 0.8900     | 0.2397 | 0.2499          | 0.6222 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits  |
| ------------ | ------- | -------------- | ---------- | --------- | ----- |
| top 5/yr     | 15      | 5              | 0.8963     | 0.6667    | 10    |
| top 10/yr    | 30      | 10             | 0.8948     | 0.7667    | 23    |
| top 20/yr    | 60      | 20             | 0.8927     | 0.8000    | 48    |
| top 50/yr    | 150     | 50             | 0.8881     | 0.8333    | 125   |
| score >= 0.9 | 31      | 10.3000        | 0.9033     | 0.8387    | 26    |
| score >= 0.8 | 4036    | 1345.3000      | 0.8329     | 0.6826    | 2755  |
| score >= 0.7 | 11132   | 3710.7000      | 0.7844     | 0.6307    | 7021  |
| score >= 0.6 | 18408   | 6136           | 0.7310     | 0.6127    | 11278 |
| score >= 0.5 | 26241   | 8747           | 0.6756     | 0.5872    | 15408 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](lightgbm_ranks-valuation-ranks-trend_2y_cagr_ge_0_e8728774_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Appendix — provenance & accounting

The material every report must carry (honest-evaluation checklist), kept out of the reading path.

### Fold definition (cited from `split_folds.parquet`)

Frozen fold manifest for the folds evaluated above — boundaries and role counts as built upstream; this report is invalid if the folds are redefined.

| fold | test_start | test_end   | embargo_days | n_train | n_test | n_purged | n_embargoed |
| ---- | ---------- | ---------- | ------------ | ------- | ------ | -------- | ----------- |
| 2022 | 2022-01-01 | 9999-12-31 | 30           | 1199285 | 45587  | 97074    | 3400        |

### Effective sample size

Σ `sample_weight_{H}y` over the rows actually fitted — the honest sample size under overlapping label windows; raw row counts are shown only for reconciliation.

| fold | train_rows | effective_train_size | test_rows |
| ---- | ---------- | -------------------- | --------- |
| 2022 | 1199285    | 57554.4235           | 45587     |

Cross-check: `manifest.json["effective_rows"]` for 2y = 68841.8 (whole dataset; every per-fold effective size above must be ≤ this).

### Crash-era metrics (with intervals)

Drawdown eras broken out with uncertainty — the same years are tagged in the era table above. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era             | n_test | effective_n | base_rate | pr_auc | roc_auc | brier  | base_rate_brier | precision_at_35 | conf_at_35 | recall_at_35 | precision_at_35_ci95 |
| --------------- | ------ | ----------- | --------- | ------ | ------- | ------ | --------------- | --------------- | ---------- | ------------ | -------------------- |
| rate-shock 2022 | 18267  | 871.6788    | 0.5158    | 0.6259 | 0.6416  | 0.2369 | 0.2497          | 0.8286          | 0.8702     | 0.0032       | [0.67, 0.92]         |
