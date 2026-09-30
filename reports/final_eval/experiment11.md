# Experiment report — experiment11

- run id: `8db6f3a12152`
- dataset version: `1.0` (pinned, immutable)
- config hash: `77e2629f49d8d1f7`
- git SHA: `3e538762292296d1a53cd3d83eb6feb9eebce253`
- seed: 8
- model: `decision_tree` params `{"max_depth": 5}`
- label: `label_2y_cagr_ge_0` — horizon 2y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 2** (from the append-only results store; failed runs count)

## Fold definition (cited from `split_folds.parquet`)

Frozen fold manifest for the folds evaluated below — boundaries and role counts as built upstream; this report is invalid if the folds are redefined.

| fold | test_start | test_end | embargo_days | n_train | n_test | n_purged | n_embargoed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 2022-01-01 | 9999-12-31 | 30 | 1212247 | 43789 | 98556 | 3440 |

## Effective sample size

Σ `sample_weight_{H}y` over the rows actually fitted — the honest sample size under overlapping label windows; raw row counts are shown only for reconciliation.

| fold | train_rows | effective_train_size | test_rows |
| --- | --- | --- | --- |
| 2022 | 1212247 | 58073.6854 | 43789 |

Cross-check: `manifest.json["effective_rows"]` for 2y = 69247.5 (whole dataset; every per-fold effective size above must be ≤ this).

## Metrics per fold (era-sliced)

One row per walk-forward fold = one test year; pooled numbers are never presented alone. Brier is reported only for probabilistic scores; ROC-AUC is logged, never headline.

| fold | n_test | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.75 | recall_at_thr_0.75 | n_at_thr_0.75 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 43789 | 0.5049 | 0.6663 | 0.7070 | 0.2223 | 0.7333 | 0.0005 | 0.6141 | 0.7740 | 27273 | 0.6965 | 0.1971 | 6122 |

## Era-sliced metrics (per test year)

Sliced on the calendar year of each test row's `snapshot_date`. The pooled row is context for the era rows, never a stand-alone result.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.75 | recall_at_thr_0.75 | n_at_thr_0.75 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 18415 | 878.9086 | 0.5130 | 0.6893 | 0.7279 | 0.2164 | 0.4000 | 0.0007 | 0.6313 | 0.7898 | 11365 | 0.6829 | 0.1586 | 2110 |
| 2023 | 17019 | 790.5184 | 0.4999 | 0.6687 | 0.7024 | 0.2238 | 0.9333 | 0.0017 | 0.6029 | 0.7644 | 10620 | 0.7229 | 0.2209 | 2559 |
| 2024 | 8355 | 385.3285 | 0.4970 | 0.6216 | 0.6717 | 0.2326 | 0.4000 | 0.0014 | 0.5997 | 0.7590 | 5288 | 0.6696 | 0.2329 | 1453 |
| pooled | 43789 | 2054.7555 | 0.5049 | 0.6663 | 0.7070 | 0.2223 | 0.7333 | 0.0005 | 0.6141 | 0.7740 | 27273 | 0.6965 | 0.1971 | 6122 |

## Crash-era metrics

Drawdown eras broken out separately — the defensive thesis is only testable here. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.75 | recall_at_thr_0.75 | n_at_thr_0.75 | precision_at_15_ci95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate-shock 2022 | 18415 | 878.9086 | 0.5130 | 0.6893 | 0.7279 | 0.2164 | 0.4000 | 0.0007 | 0.6313 | 0.7898 | 11365 | 0.6829 | 0.1586 | 2110 | [0.20, 0.64] |

## Discrimination curves

Pooled over folds. Read precision–recall against the base rate (the no-skill line moves with prevalence, which is extreme in some cells); ROC is logged against the chance diagonal but never headlined (CLAUDE.md) — PR-AUC is the metric of record.

![PR curve](experiment11_pr_curve.png)

![ROC curve](experiment11_roc_curve.png)

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](experiment11_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Interpretability artifacts

- extracted rules (one tree per fold): [experiment11_rules.md](experiment11_rules.md)
- tree diagram (fold 2022, the widest training window): [experiment11_tree.png](experiment11_tree.png)
