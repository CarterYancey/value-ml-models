# Experiment report — lightgbm_features-valuation-features-trend_5y_beat_spy_b1c59ec7

- run id: `f8900f7b03a0`
- dataset version: `1.1` (pinned, immutable)
- config hash: `f6a215141360dbec`
- git SHA: `60768d70fa2a848eabc08bd73031084eb0d3e096`
- seed: 23
- model: `lightgbm` params `{"class_weight": 1.0, "learning_rate": 0.03, "min_child_samples": 500, "n_estimators": 800, "num_leaves": 3, "reg_lambda": 0}`
- label: `label_5y_beat_spy` — horizon 5y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 2** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era          | n_test | base_rate | precision_at_35 | conf_at_35 | brier  | base_rate_brier | pr_auc |
| ------------ | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2019         | 14743  | 0.1816    | 0.3429          | 0.7517     | 0.1905 | 0.1486          | 0.2163 |
| 2020 (COVID) | 14944  | 0.1988    | 0.3429          | 0.7356     | 0.1716 | 0.1593          | 0.3006 |
| 2021         | 11263  | 0.1171    | 0.1714          | 0.6960     | 0.1351 | 0.1034          | 0.1981 |
| pooled*      | 40950  | 0.1677    | 0.2857          | 0.7277     | 0.1667 | 0.1396          | 0.2410 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits |
| ------------ | ------- | -------------- | ---------- | --------- | ---- |
| top 5/yr     | 15      | 5              | 0.7566     | 0.4667    | 7    |
| top 10/yr    | 30      | 10             | 0.7487     | 0.4000    | 12   |
| top 20/yr    | 60      | 20             | 0.7386     | 0.3167    | 19   |
| top 50/yr    | 150     | 50             | 0.7197     | 0.2733    | 41   |
| score >= 0.9 | 0       | 0              | —          | —         | 0    |
| score >= 0.8 | 0       | 0              | —          | —         | 0    |
| score >= 0.7 | 184     | 61.3000        | 0.7239     | 0.2337    | 43   |
| score >= 0.6 | 1396    | 465.3000       | 0.6514     | 0.2765    | 386  |
| score >= 0.5 | 5577    | 1859           | 0.5664     | 0.2962    | 1652 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](lightgbm_features-valuation-features-trend_5y_beat_spy_b1c59ec7_calibration.png)

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
| COVID 2020 | 14944  | 322.6290    | 0.1988    | 0.3006 | 0.6686  | 0.1716 | 0.1593          | 0.3429          | 0.7356     | 0.0035       | [0.21, 0.51]         |
