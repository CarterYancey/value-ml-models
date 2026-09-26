# Experiment report — tree_depth3_2y_cagr_ge_0

- run id: `6e6fb0dc82d1`
- dataset version: `1.0` (pinned, immutable)
- config hash: `319daa83f71fd5f0`
- git SHA: `3e538762292296d1a53cd3d83eb6feb9eebce253`
- seed: 7
- model: `decision_tree` params `{"max_depth": 3}`
- label: `label_2y_cagr_ge_0` — horizon 2y, scheme `holdout`
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

| fold | n_test | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_50 | recall_at_50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 43789 | 0.5049 | 0.6492 | 0.6979 | 0.2252 | 0.8500 | 0.0008 | 0.5800 | 0.0013 |

## Era-sliced metrics (per test year)

Sliced on the calendar year of each test row's `snapshot_date`. The pooled row is context for the era rows, never a stand-alone result.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_50 | recall_at_50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 18415 | 878.9086 | 0.5130 | 0.6737 | 0.7228 | 0.2193 | 0.4500 | 0.0010 | 0.6600 | 0.0036 |
| 2023 | 17019 | 790.5184 | 0.4999 | 0.6476 | 0.6913 | 0.2270 | 0.7000 | 0.0017 | 0.8200 | 0.0049 |
| 2024 | 8355 | 385.3285 | 0.4970 | 0.6079 | 0.6587 | 0.2351 | 0.5500 | 0.0026 | 0.6000 | 0.0072 |
| pooled | 43789 | 2054.7555 | 0.5049 | 0.6492 | 0.6979 | 0.2252 | 0.8500 | 0.0008 | 0.5800 | 0.0013 |

## Crash-era metrics

Drawdown eras broken out separately — the defensive thesis is only testable here. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_20 | recall_at_20 | precision_at_50 | recall_at_50 | precision_at_20_ci95 | precision_at_50_ci95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate-shock 2022 | 18415 | 878.9086 | 0.5130 | 0.6737 | 0.7228 | 0.2193 | 0.4500 | 0.0010 | 0.6600 | 0.0036 | [0.26, 0.66] | [0.52, 0.78] |

## Discrimination curves

Pooled over folds. Read precision–recall against the base rate (the no-skill line moves with prevalence, which is extreme in some cells); ROC is logged against the chance diagonal but never headlined (CLAUDE.md) — PR-AUC is the metric of record.

![PR curve](tree_depth3_2y_cagr_ge_0_pr_curve.png)

![ROC curve](tree_depth3_2y_cagr_ge_0_roc_curve.png)

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](tree_depth3_2y_cagr_ge_0_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Interpretability artifacts

- extracted rules (one tree per fold): [tree_depth3_2y_cagr_ge_0_rules.md](tree_depth3_2y_cagr_ge_0_rules.md)
- tree diagram (fold 2022, the widest training window): [tree_depth3_2y_cagr_ge_0_tree.png](tree_depth3_2y_cagr_ge_0_tree.png)
