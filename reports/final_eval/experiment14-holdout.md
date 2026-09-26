# Experiment report — experiment14-holdout

- run id: `71995d92b0cf`
- dataset version: `1.0` (pinned, immutable)
- config hash: `93196a10ed201fec`
- git SHA: `3e538762292296d1a53cd3d83eb6feb9eebce253`
- seed: 9
- model: `decision_tree` params `{"class_weight": "balanced", "max_depth": 10}`
- label: `label_2y_cagr_ge_0` — horizon 2y, scheme `holdout`
- **configurations tried against this cell (dataset, scheme, horizon, label): 3** (from the append-only results store; failed runs count)

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

| fold | n_test | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 43789 | 0.5049 | 0.6615 | 0.6985 | 0.2217 | 0.8000 | 0.0006 | 0.6167 | 0.7161 | 25127 | 0.7089 | 0.2187 | 6677 |

## Era-sliced metrics (per test year)

Sliced on the calendar year of each test row's `snapshot_date`. The pooled row is context for the era rows, never a stand-alone result.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 18415 | 878.9086 | 0.5130 | 0.6785 | 0.7145 | 0.2172 | 0.5333 | 0.0009 | 0.6313 | 0.7308 | 10517 | 0.7150 | 0.1878 | 2386 |
| 2023 | 17019 | 790.5184 | 0.4999 | 0.6679 | 0.6979 | 0.2221 | 0.8000 | 0.0014 | 0.6092 | 0.7085 | 9741 | 0.7182 | 0.2383 | 2779 |
| 2024 | 8355 | 385.3285 | 0.4970 | 0.6191 | 0.6667 | 0.2312 | 0.3333 | 0.0012 | 0.6003 | 0.6996 | 4869 | 0.6819 | 0.2468 | 1512 |
| pooled | 43789 | 2054.7555 | 0.5049 | 0.6615 | 0.6985 | 0.2217 | 0.8000 | 0.0006 | 0.6167 | 0.7161 | 25127 | 0.7089 | 0.2187 | 6677 |

## Crash-era metrics

Drawdown eras broken out separately — the defensive thesis is only testable here. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era | n_test | effective_n | base_rate | pr_auc | roc_auc | brier | precision_at_15 | recall_at_15 | precision_at_thr_0.5 | recall_at_thr_0.5 | n_at_thr_0.5 | precision_at_thr_0.7 | recall_at_thr_0.7 | n_at_thr_0.7 | precision_at_15_ci95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate-shock 2022 | 18415 | 878.9086 | 0.5130 | 0.6785 | 0.7145 | 0.2172 | 0.5333 | 0.0009 | 0.6313 | 0.7308 | 10517 | 0.7150 | 0.1878 | 2386 | [0.30, 0.75] |

## Discrimination curves

Pooled over folds. Read precision–recall against the base rate (the no-skill line moves with prevalence, which is extreme in some cells); ROC is logged against the chance diagonal but never headlined (CLAUDE.md) — PR-AUC is the metric of record.

![PR curve](experiment14-holdout_pr_curve.png)

![ROC curve](experiment14-holdout_roc_curve.png)

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](experiment14-holdout_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Interpretability artifacts

- extracted rules (one tree per fold): [experiment14-holdout_rules.md](experiment14-holdout_rules.md)
- tree diagram (fold 2022, the widest training window): [experiment14-holdout_tree.png](experiment14-holdout_tree.png)
