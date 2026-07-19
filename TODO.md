# TODO

Concrete development tasks, roughly in order. Architecture and rationale live
in [PLAN.md](PLAN.md); check items off (and add new ones) as work proceeds.

## 0 — Project scaffolding

- [ ] Fill in `pyproject.toml`: real description, dependencies
      (`pandas`, `pyarrow`, `duckdb`, `scikit-learn`, `matplotlib`;
      `lightgbm` can wait for Phase 3), dev deps (`pytest`, `ruff`).
- [ ] Create the source skeleton from PLAN §6 (`src/harness`, `src/models`,
      `src/eval`, `src/explain`, `src/portfolio`, `experiments/`, `reports/`,
      `tests/`).
- [ ] Obtain `dataset_v1.0` from `sharadar-dataset` and place it under
      `data/datasets/dataset_v1.0/` (git-ignored).

## 1 — Phase 1: harness + baseline trees

### Dataset loading
- [ ] Loader for a versioned dataset directory: reads `manifest.json`,
      exposes column groups (`key_meta`, `features`, `ranks`,
      `sector_ranks`, `labels`, `sample_weights`) — column selection is
      manifest-driven, never name-pattern-matched.
- [ ] Validate on load: manifest row counts vs. parquet, required files
      present, requested horizon exists in `horizons_years`.
- [ ] Split application: given (scheme, fold, horizon), join
      `splits.parquet` and return train/test frames. Enforce in code:
      train = `role='train'` only; test rows come only from the tags (which
      already restrict to median-kind, label-observable).
- [ ] Guardrails as errors, not conventions: refuse `holdout` scheme outside
      the dedicated final-eval script; refuse diagnostic schemes
      (`entity_holdout`, `random_kfold`) outside the registered-experiment
      runner; refuse fitting without the horizon's `sample_weight_{H}y`.

### Experiment harness
- [ ] Config schema (one file per experiment in `experiments/`): dataset
      version, scheme/fold(s)/horizon, label column, feature-set selector
      (by manifest group), model + params, seed.
- [ ] Runner: executes a config, logs dataset version + config hash +
      git SHA + seed + metrics to an append-only results store (plain
      parquet/CSV table is fine to start). Abandoned/failed runs are logged
      too.
- [ ] Every report cites `split_folds.parquet` (fold boundaries + counts)
      and the effective sample size (Σ `sample_weight_{H}y`, cross-checked
      against `manifest.json["effective_rows"]`).

### Baselines (before any tree is trained)
- [ ] Majority-class baseline per (horizon, threshold) cell.
- [ ] Single-factor rank baselines: top-K by `book_to_market_rank` and
      `earnings_yield_rank`.
- [ ] Random-ranking baseline (seeded).

### Models
- [ ] Single decision tree (sklearn), depth-limited, fitted with
      `sample_weight_{H}y`; class weighting where a cell is heavily
      imbalanced.
- [ ] Rule extraction: human-readable rules per trained tree, written to
      `reports/` and checked in.
- [ ] Tree diagram rendering (matplotlib) into the same report.

### Tests
- [ ] Unit tests for split application against a hand-built miniature
      splits.parquet (roles, absence-means-out-of-fold, median-kind test
      rows).
- [ ] Test that the guardrails actually raise (holdout access, diagnostic
      schemes, missing sample weight).

## 2 — Phase 2: evaluation done right

- [ ] Metrics module: precision@K, recall@K, PR-AUC, Brier, calibration
      curve. ROC-AUC may be logged, never headlined.
- [ ] Era slicing: every metric per test year; pooled numbers are never
      presented alone.
- [ ] Crash-era report: 2000–02, 2008–09, 2020, 2022 broken out separately,
      with uncertainty (correlated-picks caveat, PLAN §4 Phase 2).
- [ ] Walk-forward driver: loop the upstream `walkforward` folds, retrain
      per fold, aggregate the era table.
- [ ] Baseline-comparison table auto-included in every report; state the
      number of configurations tried.
- [ ] Final-eval script for the sealed `holdout` fold: runs once per phase,
      logs the result whether good or bad. Nothing else may read holdout
      tags.

### Registered diagnostics (from data/manual.md §7 — diagnostic only)
- [ ] Leakage-gap experiment: identical model under `random_kfold`,
      `entity_holdout`, and purged `walkforward`; report the score gaps.
- [ ] Era-identifiability probe: predict calendar year from features alone,
      raw vs. rank sets.
- [ ] Restated-variant ablation (needs a restated-dimension dataset variant
      from upstream; coordinate before starting).

## 3 — Phase 3: better models, kept interpretable

- [ ] LightGBM wrapper (native NaN handling; weights passed through).
- [ ] Post-hoc calibration (isotonic / Platt) on a purged validation fold.
- [ ] SHAP: global importance + per-prediction explanations; compare against
      Phase-1 tree rules.
- [ ] Ablations: raw vs. rank vs. sector-rank features; ± technicals;
      ± classification columns (current-state caveat).

## 4 — Phase 4: portfolio construction & backtest

- [ ] Ranking → quarterly-rebalanced top-K portfolio.
- [ ] Investability filter from `log_marketcap`, `dollar_volume_3m`,
      `amihud_12m`; filter definition reported with the model.
- [ ] Transaction-cost model (microcap fidelity is an open question,
      PLAN §8).
- [ ] Benchmarks: SPY and equal-weight universe; drawdowns and era-sliced
      results, not just CAGR.
- [ ] Defensive-hypothesis test: in market-down years, do selected stocks
      lose less?

## Upstream coordination / watch list

- [ ] Earliest-trustworthy-year (survivorship-depth) verification is still
      open upstream; until resolved, treat pre-2000 cross-sections with
      suspicion (PLAN §8).
- [ ] Restated-dimension dataset variant (decision 0009) needed for the
      restated ablation.
- [ ] Any feature request discovered during modeling → file upstream, new
      dataset version (never engineered here).
