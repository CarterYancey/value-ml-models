# Experiment report — lightgbm_ranks-technical_5y_beat_spy_17f18492

- run id: `419f98ace435`
- dataset version: `1.1` (pinned, immutable)
- config hash: `f1aa6e02408f38b3`
- git SHA: `60768d70fa2a848eabc08bd73031084eb0d3e096`
- seed: 23
- model: `lightgbm` params `{"class_weight": 1.0, "learning_rate": 0.03, "min_child_samples": 500, "n_estimators": 800, "num_leaves": 3, "reg_lambda": 0}`
- label: `label_5y_beat_spy` — horizon 5y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 1** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era          | n_test | base_rate | precision_at_35 | conf_at_35 | brier  | base_rate_brier | pr_auc |
| ------------ | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2019         | 14743  | 0.1816    | 0.1429          | 0.7554     | 0.2167 | 0.1486          | 0.1827 |
| 2020 (COVID) | 14944  | 0.1988    | 0.1429          | 0.7511     | 0.2207 | 0.1593          | 0.1968 |
| 2021         | 11263  | 0.1171    | 0.0571          | 0.7430     | 0.2020 | 0.1034          | 0.1455 |
| pooled*      | 40950  | 0.1677    | 0.1143          | 0.7498     | 0.2136 | 0.1396          | 0.1750 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits |
| ------------ | ------- | -------------- | ---------- | --------- | ---- |
| top 5/yr     | 15      | 5              | 0.7749     | 0         | 0    |
| top 10/yr    | 30      | 10             | 0.7657     | 0.0667    | 2    |
| top 20/yr    | 60      | 20             | 0.7573     | 0.0833    | 5    |
| top 50/yr    | 150     | 50             | 0.7446     | 0.1067    | 16   |
| score >= 0.9 | 0       | 0              | —          | —         | 0    |
| score >= 0.8 | 0       | 0              | —          | —         | 0    |
| score >= 0.7 | 367     | 122.3000       | 0.7280     | 0.0817    | 30   |
| score >= 0.6 | 3516    | 1172           | 0.6450     | 0.1502    | 528  |
| score >= 0.5 | 11846   | 3948.7000      | 0.5749     | 0.2067    | 2449 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](lightgbm_ranks-technical_5y_beat_spy_17f18492_calibration.png)

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
| COVID 2020 | 14944  | 322.6290    | 0.1988    | 0.1968 | 0.5215  | 0.2207 | 0.1593          | 0.1429          | 0.7511     | 0.0015       | [0.06, 0.29]         |
