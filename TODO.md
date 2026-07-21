# TODO

Concrete development tasks, roughly in order. Architecture and rationale live
in [PLAN.md](PLAN.md); check items off (and add new ones) as work proceeds.

## 1 — Phase 1: harness + baseline trees

### Dataset loading
- [x] Loader for a versioned dataset directory: reads `manifest.json`,
      exposes column groups (`key_meta`, `features`, `ranks`,
      `sector_ranks`, `labels`, `sample_weights`) — column selection is
      manifest-driven, never name-pattern-matched. (`src/harness/dataset.py`)
- [x] Validate on load: manifest row counts vs. parquet, required files
      present, requested horizon exists in `horizons_years`.
- [x] Split application: given (scheme, fold, horizon), join
      `splits.parquet` and return train/test frames. Enforce in code:
      train = `role='train'` only; test rows come only from the tags (which
      already restrict to median-kind, label-observable — re-verified
      defensively on apply).
- [x] Guardrails as errors, not conventions: refuse `holdout` scheme outside
      the dedicated final-eval script; refuse diagnostic schemes
      (`entity_holdout`, `random_kfold`) outside the registered-experiment
      runner; refuse fitting without the horizon's `sample_weight_{H}y`.
      (`SplitAccess` in `src/harness/dataset.py`; the ordinary runner only
      ever grants STANDARD access. The final-eval and registered-diagnostic
      entry points themselves are Phase 2.)

### Experiment harness
- [x] Config schema (one TOML file per experiment in `experiments/`):
      dataset version, scheme/fold(s)/horizon, label column, feature-set
      selector (by manifest group), model + params, seed.
      (`src/harness/config.py`)
- [x] Runner: executes a config, logs dataset version + config hash +
      git SHA + seed + metrics to an append-only results store
      (`experiments/results.csv`). Abandoned/failed runs are logged too.
      (`src/harness/runner.py`, `src/harness/results.py`; CLI: `vml-run`)
- [x] Every report cites `split_folds.parquet` (fold boundaries + counts)
      and the effective sample size (Σ `sample_weight_{H}y`, cross-checked
      against `manifest.json["effective_rows"]`). (`src/harness/report.py`)
- [x] Train/eval split: the runner saves fitted per-fold models as a
      bundle (`src/harness/model_store.py`, git-ignored under
      `experiments/models/`); `vml-eval` re-scores a saved bundle under an
      eval config (top-K, score thresholds only — everything else stays
      pinned by the bundle) without refitting, logging each evaluation to
      the results store under its own config hash.
      (`src/harness/evaluate.py`)

### Baselines (before any tree is trained)
- [x] Majority-class baseline per (horizon, threshold) cell.
      (`scripts/run_baselines.py` runs the full grid; exemplar configs in
      `experiments/`. Needs a real `dataset_v1.0` locally to produce
      reports — verified end-to-end on the test fixture.)
- [x] Single-factor rank baselines: top-K by `book_to_market_rank` and
      `earnings_yield_rank`. (`src/models/baselines.py`)
- [x] Random-ranking baseline (seeded).

### Models
- [x] Single decision tree (sklearn), depth-limited, fitted with
      `sample_weight_{H}y`; class weighting where a cell is heavily
      imbalanced. (`src/models/tree.py`; `max_depth` is mandatory, NaNs
      handled natively — no imputation. Exemplar configs in
      `experiments/tree_*.toml`; needs a real `dataset_v1.0` locally for
      real reports — verified end-to-end on the test fixture.)
- [x] Rule extraction: human-readable rules per trained tree, written to
      `reports/` and checked in. (`src/explain/rules.py`; the runner
      writes `reports/<experiment>_rules.md`, one section per fold, with
      NaN-routing stated in every condition.)
- [x] Tree diagram rendering (matplotlib) into the same report.
      (`reports/<experiment>_tree.png`, the last fold's tree — the widest
      training window — linked from the report.)

### Tests
- [x] Unit tests for split application against a hand-built miniature
      splits.parquet (roles, absence-means-out-of-fold, median-kind test
      rows). (`tests/conftest.py` builds the fixture;
      `tests/test_split_application.py`)
- [x] Test that the guardrails actually raise (holdout access, diagnostic
      schemes, missing sample weight). (`tests/test_guardrails.py`)

## 2 — Phase 2: evaluation done right

- [x] Metrics module: precision@K, recall@K, PR-AUC, Brier, calibration
      curve. ROC-AUC may be logged, never headlined. (`src/eval/metrics.py`
      incl. `calibration_table`; reliability-curve PNG via
      `src/eval/plots.py`, embedded in every probabilistic report.)
- [x] Era slicing: every metric per test year; pooled numbers are never
      presented alone. (`src/eval/era.py`; sliced on `snapshot_date` year,
      pooled row clearly marked as context only.)
- [x] Crash-era report: 2000–02, 2008–09, 2020, 2022 broken out separately,
      with uncertainty (correlated-picks caveat, PLAN §4 Phase 2).
      (`crash_era_table` — Wilson 95% CI on precision@K, flagged as
      optimistic because same-year picks are correlated; reports state
      explicitly when no crash era falls in the test years.)
- [x] Walk-forward driver: loop the upstream `walkforward` folds, retrain
      per fold, aggregate the era table. (`src/harness/runner.py` collects
      per-row test predictions across folds and aggregates.)
- [x] Baseline-comparison table auto-included in every report; state the
      number of configurations tried. (`ResultsStore.model_comparison`;
      a report with no recorded baselines for the cell says so and is not
      reportable.)
- [x] Final-eval script for the sealed `holdout` fold: runs once per phase,
      logs the result whether good or bad. Nothing else may read holdout
      tags. (`scripts/run_final_eval.py` — the only FINAL_EVAL entry
      point; a completed eval per (phase, cell) is recorded in
      `reports/final_evals.csv` and cannot be repeated.)

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
