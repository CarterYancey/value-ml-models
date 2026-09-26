# Experiment report — lightgbm_ranks-technical_5y_cagr_ge_0_928dc824

- run id: `5e72770d513c`
- dataset version: `1.1` (pinned, immutable)
- config hash: `669e7b0b4d09a10c`
- git SHA: `60768d70fa2a848eabc08bd73031084eb0d3e096`
- seed: 23
- model: `lightgbm` params `{"class_weight": 1.0, "learning_rate": 0.03, "min_child_samples": 500, "n_estimators": 800, "num_leaves": 3, "reg_lambda": 0}`
- label: `label_5y_cagr_ge_0` — horizon 5y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 2** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era          | n_test | base_rate | precision_at_35 | conf_at_35 | brier  | base_rate_brier | pr_auc |
| ------------ | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2019         | 14743  | 0.5221    | 0.7429          | 0.9119     | 0.2177 | 0.2495          | 0.6902 |
| 2020 (COVID) | 14944  | 0.5099    | 0.6571          | 0.9144     | 0.2273 | 0.2499          | 0.6591 |
| 2021         | 11263  | 0.4522    | 0.8286          | 0.9079     | 0.2283 | 0.2477          | 0.6164 |
| pooled*      | 40950  | 0.4962    | 0.7429          | 0.9114     | 0.2244 | 0.2500          | 0.6592 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits  |
| ------------ | ------- | -------------- | ---------- | --------- | ----- |
| top 5/yr     | 15      | 5              | 0.9218     | 0.5333    | 8     |
| top 10/yr    | 30      | 10             | 0.9186     | 0.6333    | 19    |
| top 20/yr    | 60      | 20             | 0.9148     | 0.6667    | 40    |
| top 50/yr    | 150     | 50             | 0.9090     | 0.7267    | 109   |
| score >= 0.9 | 183     | 61             | 0.9082     | 0.7377    | 135   |
| score >= 0.8 | 5217    | 1739           | 0.8423     | 0.7140    | 3725  |
| score >= 0.7 | 12906   | 4302           | 0.7874     | 0.6906    | 8913  |
| score >= 0.6 | 19899   | 6633           | 0.7394     | 0.6597    | 13127 |
| score >= 0.5 | 26147   | 8715.7000      | 0.6940     | 0.6260    | 16367 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](lightgbm_ranks-technical_5y_cagr_ge_0_928dc824_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Appendix — provenance & accounting

The material every report must carry (honest-evaluation checklist), kept out of the reading path.

### Fold definition (cited from `split_folds.parquet`)

Frozen fold manifest for the folds evaluated above — boundaries and role counts as built upstream; this report is invalid if the folds are redefined.

| fold | test_start | test_end   | embargo_days | n_train | n_test | n_purged | n_embargoed |
| ---- | ---------- | ---------- | ------------ | ------- | ------ | -------- | ----------- |
| 2019 | 2019-01-01 | 9999-12-31 | 30           | 928008  | 40950  | 226986   | 3462        |

### Effective sample size

Σ `sample_weight_{H}y` over the rows actually fitted — the honest sample size under overlapping label windows; raw row counts are shown only for reconciliation.

| fold | train_rows | effective_train_size | test_rows |
| ---- | ---------- | -------------------- | --------- |
| 2019 | 928008     | 22804.8002           | 40950     |

Cross-check: `manifest.json["effective_rows"]` for 5y = 30499.0 (whole dataset; every per-fold effective size above must be ≤ this).

### Crash-era metrics (with intervals)

Drawdown eras broken out with uncertainty — the same years are tagged in the era table above. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era        | n_test | effective_n | base_rate | pr_auc | roc_auc | brier  | base_rate_brier | precision_at_35 | conf_at_35 | recall_at_35 | precision_at_35_ci95 |
| ---------- | ------ | ----------- | --------- | ------ | ------- | ------ | --------------- | --------------- | ---------- | ------------ | -------------------- |
| COVID 2020 | 14944  | 322.6290    | 0.5099    | 0.6591 | 0.6874  | 0.2273 | 0.2499          | 0.6571          | 0.9144     | 0.0029       | [0.49, 0.79]         |
