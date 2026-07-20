# CLAUDE.md — value-ml-models

Guidance for AI-assisted development. Read [PLAN.md](PLAN.md) for the design,
[TODO.md](TODO.md) for what to work on next, and
[data/manual.md](data/manual.md) — the dataset contract — before touching any
modeling code. Upstream data rules live in `sharadar-dataset/CLAUDE.md`; the
invariants below are this repo's equivalents.

## Orientation

- **README.md** — overview + setup/usage only.
- **PLAN.md** — architecture, design principles, phase roadmap.
- **TODO.md** — the live task list; update it as tasks complete or appear.
- **data/*.md** — the dataset docs, from upstream:
  [manual.md](data/manual.md) (how to consume the dataset — start here),
  [dataset.md](data/dataset.md) (directory layout, column groups),
  [labels.md](data/labels.md) (label matrix), [splits.md](data/splits.md)
  (schemes/roles/folds), [features.md](data/features.md) (feature registry).
- Datasets live (git-ignored) at `data/datasets/dataset_vX.Y/`:
  `dataset.parquet`, `splits.parquet`, `split_folds.parquet`,
  `manifest.json`. Never edit files inside a dataset directory; data fixes
  are upstream changes producing a new version.

## Dataset facts every change must respect

- Row grain: `(permaticker, snapshot_date, snapshot_kind)`, three snapshots
  per stock-quarter (`low`/`median`/`high`). `permaticker` is the entity
  key; never join or group on `ticker`.
- Train on `role = 'train'` rows only, all kinds. Test rows come from the
  tags and are median-kind, label-observable only.
- Schemes: `walkforward` for all model selection; `holdout` is sealed (one
  evaluation per phase, via a dedicated script); `entity_holdout` and
  `random_kfold` are diagnostic-only, and `random_kfold` is deliberately
  leaky.
- `sample_weight_{H}y` is passed as a native sample weight in every fit;
  effective sample size (Σ weights) is what gets reported, not row counts.
- Delisted rows (`delisted_in_window_{H}` ≠ 'false') are labeled rows like
  any other. Filtering them out reintroduces survivorship bias.
- Select columns via `manifest.json["columns"]`, never by pattern-matching
  names.
- NULLs are meaningful (no filing, burn-in, structural gaps, rank guards).
  No global imputation; fold-internal only, and disclosed.

## Hard invariants

1. **Never construct splits here.** Split tags come from the upstream
   dataset. Any local re-splitting, shuffling, or "quick random holdout" is
   a leakage bug.
2. **Never touch the sealed holdout during development.** It is evaluated
   once per phase, by a dedicated script, and the result is logged whether
   good or bad.
3. **Every run is reproducible:** dataset version + config + git SHA + seed
   are logged for every experiment, including abandoned ones.
4. **No feature engineering.** New features are upstream changes. This repo
   may select/subset columns, never derive new ones (prevents ad-hoc
   lookahead creeping in far from the point-in-time machinery).
5. **Report era-sliced metrics.** Pooled metrics alone are never presented
   as a result.

## Conventions

- Python 3.12+, scikit-learn for trees, LightGBM for Phase 3, matplotlib for
  reports, duckdb/pandas for data access. Keep the dependency list short.
- One experiment = one config file in `experiments/`; the harness runs
  configs, code never hardcodes an experiment.
- Metrics of record: precision@K, PR-AUC, Brier, calibration plot. ROC-AUC
  may be logged but never headline (base rates are extreme in some label
  cells).
- Rule extraction output (human-readable tree rules) is a first-class
  artifact, checked into `reports/`.
- Every report cites `split_folds.parquet` (the frozen fold definition) and
  the number of configurations tried.

## Things Claude should proactively flag

- Any call to `train_test_split` or `KFold`: violates invariant 1.
- Training code that ignores the per-horizon `sample_weight_{H}y` column, or
  evaluation on `low`/`high` snapshot-kind rows (test sets are median-kind
  only, via the tags): both silently inflate results.
- Any filter dropping rows where `delisted_in_window_{H}` ≠ 'false':
  survivorship bias.
- Feature selection by column-name pattern instead of the manifest.
- Joins on `ticker`, or any join against raw Sharadar tables (the easy joins
  leak the future).
- Use of `entity_holdout`/`random_kfold` tags outside the registered
  leakage-gap experiment, or any read of `holdout` tags outside the
  final-eval script.
- Validation metrics dramatically above baseline: treat as suspected leakage
  first, breakthrough second. Check split application before celebrating.
- Any comparison across experiments using different dataset versions.
- Class-imbalance "fixes" (SMOTE, oversampling) that operate across time
  boundaries — synthetic samples must never mix eras.
- Backtest results reported without transaction costs or without the
  investability filter (there is no upstream liquidity floor; the filter is
  built here from `log_marketcap`, `dollar_volume_3m`, `amihud_12m`).

## Honest-evaluation checklist for any reported result

- [ ] Walk-forward, purged, embargoed (upstream tags applied correctly).
- [ ] Era-sliced table included (per-year metrics).
- [ ] Compared against the trivial baselines (majority class, single-factor
      rank, random).
- [ ] Number of configurations tried is stated.
- [ ] Calibration curve included if probabilities are used downstream.
- [ ] Effective sample size (Σ `sample_weight_{H}y`) reported, and
      `split_folds.parquet` cited.
