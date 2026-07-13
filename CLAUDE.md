# CLAUDE.md — value-ml-models

Guidance for AI-assisted development. Read README.md for the plan. Upstream data
rules live in `sharadar-dataset/CLAUDE.md`; the invariants below are this repo's
equivalents.

## Hard invariants

1. **Never construct splits here.** Split tags come from the upstream dataset.
   Any local re-splitting, shuffling, or "quick random holdout" is a leakage bug.
2. **Never touch the final test period during development.** It is evaluated
   once per phase, by a dedicated script, and the result is logged whether good
   or bad.
3. **Every run is reproducible:** dataset version + config + git SHA + seed are
   logged for every experiment, including abandoned ones.
4. **No feature engineering.** New features are upstream changes. This repo may
   select/subset columns, never derive new ones (prevents ad-hoc lookahead
   creeping in far from the point-in-time machinery).
5. **Report era-sliced metrics.** Pooled metrics alone are never presented as a
   result.

## Conventions

- Python 3.11+, scikit-learn for trees, LightGBM for Phase 3, matplotlib for
  reports. Keep the dependency list short.
- One experiment = one config file in `experiments/`; the harness runs configs,
  code never hardcodes an experiment.
- Metrics of record: precision@K, PR-AUC, Brier, calibration plot. ROC-AUC may
  be logged but never headline (base rates are extreme in some label cells).
- Rule extraction output (human-readable tree rules) is a first-class artifact,
  checked into `reports/`.

## Things Claude should proactively flag

- Any call to `train_test_split` or `KFold`: violates invariant 1.
- Training code that ignores the dataset's per-horizon `sample_weight` column,
  or evaluation code that includes `snapshot_kind != 'close'` (augmented) rows:
  both silently inflate results.
- Validation metrics dramatically above baseline: treat as suspected leakage
  first, breakthrough second. Check split application before celebrating.
- Any comparison across experiments using different dataset versions.
- Class-imbalance "fixes" (SMOTE, oversampling) that operate across time
  boundaries — synthetic samples must never mix eras.
- Backtest results reported without transaction costs or without the
  investability filter.

## Honest-evaluation checklist for any reported result

- [ ] Walk-forward, purged, embargoed.
- [ ] Era-sliced table included (per-year metrics).
- [ ] Compared against the trivial baselines (majority class, single-factor rank).
- [ ] Number of configurations tried is stated.
- [ ] Calibration curve included if probabilities are used downstream.
