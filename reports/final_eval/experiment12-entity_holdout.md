# Experiment report — experiment12-entity_holdout

- run id: `dfceeac81a9a`
- dataset version: `1.0` (pinned, immutable)
- config hash: `b6b7493449556222`
- git SHA: `3e538762292296d1a53cd3d83eb6feb9eebce253`
- seed: 7
- model: `decision_tree` params `{"max_depth": 4}`
- label: `label_2y_cagr_ge_8` — horizon 2y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 1** (from the append-only results store; failed runs count)

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

| fold | n_test | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 43789 | 0.3001 | 0.4061 | 0.6533 | 0.2074 | 0.3500 | 0.0005 | 0.4526 | 0.3838 | 11969 | — | 0 | 0 |

## Era-sliced metrics (per test year)

Sliced on the calendar year of each test row's `snapshot_date`. The pooled row is context for the era rows, never a stand-alone result.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 18415 | 878.9086 | 0.2689 | 0.3946 | 0.6818 | 0.1975 | 0.2500 | 0.0009 | 0.4507 | 0.3838 | 4582 | — | 0 | 0 |
| 2023 | 17019 | 790.5184 | 0.3137 | 0.4165 | 0.6440 | 0.2112 | 0.3000 | 0.0011 | 0.4541 | 0.3826 | 4794 | — | 0 | 0 |
| 2024 | 8355 | 385.3285 | 0.3431 | 0.4177 | 0.6128 | 0.2221 | 0.3500 | 0.0023 | 0.4531 | 0.3861 | 2593 | — | 0 | 0 |
| pooled | 43789 | 2054.7555 | 0.3001 | 0.4061 | 0.6533 | 0.2074 | 0.3500 | 0.0005 | 0.4526 | 0.3838 | 11969 | — | 0 | 0 |

## Crash-era metrics

Drawdown eras broken out separately — the defensive thesis is only testable here. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 | precision_at_20_ci95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate-shock 2022 | 18415 | 878.9086 | 0.2689 | 0.3946 | 0.6818 | 0.1975 | 0.2500 | 0.0009 | 0.4507 | 0.3838 | 4582 | — | 0 | 0 | [0.11, 0.47] |

## Discrimination curves

Pooled over folds. Read precision–recall against the base rate (the no-skill line moves with prevalence, which is extreme in some cells); ROC is logged against the chance diagonal but never headlined (CLAUDE.md) — PR-AUC is the metric of record.

![PR curve](experiment12-entity_holdout_pr_curve.png)

![ROC curve](experiment12-entity_holdout_roc_curve.png)

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](experiment12-entity_holdout_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Interpretability artifacts

- extracted rules (one tree per fold): [experiment12-entity_holdout_rules.md](experiment12-entity_holdout_rules.md)
- tree diagram (fold 2022, the widest training window): [experiment12-entity_holdout_tree.png](experiment12-entity_holdout_tree.png)
