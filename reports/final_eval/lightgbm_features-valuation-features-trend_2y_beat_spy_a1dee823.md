# Experiment report — lightgbm_features-valuation-features-trend_2y_beat_spy_a1dee823

- run id: `8a5739bc4ed8`
- dataset version: `1.1` (pinned, immutable)
- config hash: `cc93c28c743979ed`
- git SHA: `60768d70fa2a848eabc08bd73031084eb0d3e096`
- seed: 23
- model: `lightgbm` params `{"class_weight": 1.0, "learning_rate": 0.03, "min_child_samples": 500, "n_estimators": 800, "num_leaves": 3, "reg_lambda": 0}`
- label: `label_2y_beat_spy` — horizon 2y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 2** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era               | n_test | base_rate | precision_at_35 | conf_at_35 | brier  | base_rate_brier | pr_auc |
| ----------------- | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2022 (rate-shock) | 18267  | 0.2130    | 0.3143          | 0.6284     | 0.1821 | 0.1676          | 0.2952 |
| 2023              | 16875  | 0.1889    | 0.3429          | 0.6464     | 0.1887 | 0.1532          | 0.2313 |
| 2024              | 10445  | 0.2353    | 0.2000          | 0.6321     | 0.2035 | 0.1799          | 0.2668 |
| pooled*           | 45587  | 0.2092    | 0.2857          | 0.6357     | 0.1894 | 0.1654          | 0.2627 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits |
| ------------ | ------- | -------------- | ---------- | --------- | ---- |
| top 5/yr     | 15      | 5              | 0.6668     | 0.1333    | 2    |
| top 10/yr    | 30      | 10             | 0.6552     | 0.2667    | 8    |
| top 20/yr    | 60      | 20             | 0.6449     | 0.2333    | 14   |
| top 50/yr    | 150     | 50             | 0.6293     | 0.2600    | 39   |
| score >= 0.9 | 0       | 0              | —          | —         | 0    |
| score >= 0.8 | 0       | 0              | —          | —         | 0    |
| score >= 0.7 | 1       | 0.3000         | 0.7133     | 0         | 0    |
| score >= 0.6 | 243     | 81             | 0.6207     | 0.2593    | 63   |
| score >= 0.5 | 4152    | 1384           | 0.5375     | 0.2974    | 1235 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](lightgbm_features-valuation-features-trend_2y_beat_spy_a1dee823_calibration.png)

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
| rate-shock 2022 | 18267  | 871.6788    | 0.2130    | 0.2952 | 0.6442  | 0.1821 | 0.1676          | 0.3143          | 0.6284     | 0.0027       | [0.19, 0.48]         |
