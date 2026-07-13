# value-ml-models

Model training, evaluation, and portfolio construction on top of the versioned
datasets produced by `sharadar-dataset`. This repo begins where that one ends:
it consumes `dataset_vX.Y.parquet` and never touches raw Sharadar data.

Status: **planning** — development begins after `sharadar-dataset` M5
(first versioned dataset).

---

## 1. Objective

Train classification models that predict, from point-in-time fundamentals,
whether a stock will meet return criteria over 1/2/3/5-year horizons — e.g.,
"≥ 5% CAGR over the next 3 years" or "beats SPY over the next year" — and turn
calibrated predictions into ranked stock lists / portfolios.

One model per (horizon, threshold) cell of the label matrix, sharing a common
training/evaluation harness.

## 2. Design principles

- **Dataset is pinned and immutable.** Every experiment records the exact
  dataset version. Fixing data bugs happens upstream, producing a new version.
- **Explainability first.** v1 models are single decision trees, because rules
  like "P/B rank < X → Y% probability of meeting criteria" are the point.
  Interpretability is a feature requirement, not a nice-to-have.
- **Calibration matters more than accuracy.** Portfolio construction ranks by
  predicted probability. A model whose 0.7 means 70% is more useful than a
  slightly more accurate model whose probabilities are meaningless. Single trees
  are poorly calibrated; this is a known v1 limitation, addressed in v2.
- **Relative labels are expected to work better than absolute ones.** Absolute
  thresholds force implicit market-level prediction. Train both; compare; be
  unsurprised if absolute-threshold models underperform out-of-time.

## 3. Roadmap

### Phase 1 — Harness + baseline trees
- Experiment harness: load pinned dataset, apply per-horizon purged splits
  (split tags come from upstream), train, evaluate, log everything
  (params, dataset version, git SHA, metrics) — MLflow or a plain results table.
- Baselines to beat, computed first: predict-majority-class; rank by a single
  factor (P/B rank, earnings yield rank); random.
- Single decision trees (sklearn), depth-limited, class-weighted where needed.
  Deliverable per model: the tree diagram + extracted human-readable rules.

### Phase 2 — Evaluation done right
- Metrics: precision/recall at top-K (portfolio-relevant), PR-AUC (base rates
  vary hugely by horizon/threshold/era — ROC-AUC misleads), calibration curves,
  Brier score.
- **Era-sliced evaluation:** every metric reported per year/regime, not just
  pooled. A model that only works 2009–2020 is a bull-market artifact.
- **Crash-era evaluation is first-class:** the project's core thesis
  (crash-resistant high-precision picks) is only testable in drawdown eras, of
  which the sample contains ~4 (2000–02, 2008–09, 2020, 2022), each mechanically
  different. Report metrics on these eras separately, with honest uncertainty —
  and expect wide error bars, since precision@K on few, correlated picks carries
  the statistical weight of far fewer than K independent bets. Relative
  (beat-benchmark) labels are the primary lens here; absolute labels can't see
  "lost 5% when the market lost 15%."
- Walk-forward evaluation: retrain on expanding window, test on next period,
  respecting purge/embargo. This is the honest estimate of live performance.

### Phase 3 — Better models, kept interpretable
- Gradient-boosted trees (LightGBM/XGBoost) + post-hoc calibration
  (isotonic / Platt on a purged validation fold).
- SHAP values for global and per-prediction explanation; compare discovered
  structure against the single-tree rules from Phase 1.
- Feature ablations: raw vs. rank features, with/without technicals,
  with/without industry columns.

### Phase 4 — Portfolio construction & backtest
- Turn top-K probability rankings into quarterly-rebalanced portfolios.
- Backtest with transaction-cost assumptions and an investability filter
  (use the upstream `min_marketcap` flag).
- Compare against SPY and an equal-weight universe benchmark; report drawdowns
  and era-sliced results, not just CAGR.
- Explicitly test the "defensive" hypothesis from the project's motivation:
  in market-down years, do selected stocks lose less?

## 4. Anti-overfitting rules

- The final test period (defined upstream) is touched once, at the end of a
  phase — never during model selection.
- Every experiment is logged; failed experiments count. If 40 configurations
  were tried, the reported result accounts for that (deflated expectations,
  not the max).
- No feature engineering in this repo. If a model "needs" a new feature, that's
  an upstream change and a new dataset version.

## 5. Repo layout (planned)

```
value-ml-models/
├── experiments/      # one config file per experiment, results logged
├── src/
│   ├── harness/      # data loading, split application, run logging
│   ├── models/       # tree, gbm, calibration wrappers
│   ├── eval/         # metrics, era-slicing, walk-forward
│   ├── explain/      # rule extraction, SHAP
│   └── portfolio/    # ranking → holdings, backtest
├── reports/          # generated evaluation reports per experiment
└── tests/
```

## 6. Open questions

- [ ] One model per (horizon, threshold) vs. predicting continuous CAGR and
      thresholding afterward (regression reframe). Start with classification as
      planned; revisit after Phase 2.
- [ ] Class-imbalance handling per cell (some cells are ~90/10).
- [ ] Retraining cadence in walk-forward (annual vs. quarterly).
- [ ] Transaction-cost model fidelity for microcaps.
