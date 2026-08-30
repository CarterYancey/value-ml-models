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
- [x] Graph the PR-AUC and ROC-AUC curves. (`render_pr_curve` /
      `render_roc_curve` in `src/eval/plots.py` — pooled over folds,
      weighted; PR drawn against the base-rate no-skill line, ROC against
      the chance diagonal; drawn for every model, not just probabilistic
      ones. New "Discrimination curves" report section.)
- [x] On re-evaluation of a saved model, don't redraw score-only figures
      (calibration, PR, ROC): the scores are unchanged, so the values are
      identical to the training run. (`finalize_run(render_score_figures=)`
      — `vml-eval` passes False; the eval report points back to the
      training run's figures instead.)
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

## Deployment (cross-phase: ship whatever the current phase selected)

- [x] Deployment training: refit a selected config's model on **all**
      labeled rows (all snapshot kinds, delistings included, no split
      filtering — data/manual.md §4 rule 7; split tags are never read) and
      save a single-model deployment bundle. Runs are logged to the
      results store under scheme `deployment`, apart from walk-forward
      trial accounting. (`src/harness/deploy.py`,
      `DeploymentBundle` in `src/harness/model_store.py`;
      CLI: `vml-train-deploy`)
- [x] Inference on today's stocks: score a
      `data/datasets/inference_{date}/` dataset (feature columns, no
      labels) with a deployment bundle; full ranking written to
      `predictions/*.csv` with a provenance sidecar `.meta.json`, top 50
      printed. Deployment fits have no test set — scores are rankings,
      never reported performance. (CLI: `vml-predict`)
- [x] Multi-model inference: `vml-predict` accepts several deployment
      bundles and writes one combined CSV (`rank_<model>`/`score_<model>`
      pair per bundle, ordered by mean rank) for side-by-side model
      comparison; one logged inference run per model.
- [x] `vml-predict --trends`: carry the long-horizon trend context
      columns (`revenue_trend_20q`, `tangibles_trend_20q`,
      `ocf_trend_20q`, `div_years_paid_10y`, `div_cuts_10y`) verbatim
      from the inference data into the output CSV (single and
      multi-bundle; missing columns are an error, and the sidecar
      records `extra_columns`).
- [ ] Apply the investability filter (Phase 4) to deployment rankings
      before acting on them — microcaps dominate the universe and there is
      no upstream liquidity floor.

## Workflow & tooling (cross-phase)

- [x] Artifact hygiene: generated `reports/` output is git-ignored;
      `vml-promote` copies a report + its artifacts into the tracked
      `reports/promoted/<name>/` (sweep summaries too); the sealed
      final-eval record stays tracked unconditionally; the results
      ledger `experiments/results.csv` is local. (`harness/promote.py`)
- [x] Experiment catalog: `vml-experiments` (`list`/`runs`/`show`) joins
      `experiments/*.toml` with the results ledger — answers "have I run
      this?", "what's closest to edit from?", "what did it score?"
      without grepping. (`harness/catalog.py`)
- [x] Upstream doc sync: `scripts/sync_data_docs.py` copies the dataset
      docs from the local `radarash-dataset` checkout, records upstream
      commit + file hashes in `data/upstream.json`; `--check` detects
      drift. `data/versions.md` (maintained here) maps dataset versions
      to features; configs declare `min_dataset_version` and the harness
      enforces it against the loaded manifest.
- [x] Report overhaul: era table leads with crash years tagged inline and
      per-year-pick pooled row (global top-K over pooled per-fold scores
      was wrong — it returned the hottest fold's picks); new
      high-confidence-picks profile (top-N/yr tiers + `score >= p` counts,
      no pre-chosen threshold needed); `conf_at_K` (mean score of picks)
      and `base_rate_brier` (no-skill Brier reference) added; fold
      definition, effective sample size, and the crash-era CI table moved
      to a provenance appendix; markdown tables width-padded; PR/ROC
      curves opt-in (`vml-run --curves`), calibration always drawn.
- [ ] `vml-experiments` quality-of-life: `--cell` filter (horizon+label),
      and a `similar <config>` subcommand ranking configs by shared
      cell/model/features.
- [ ] Wire `scripts/sync_data_docs.py --check` into the test session or a
      pre-commit hook on machines that have the upstream checkout.

## 3 — Phase 3: better models, kept interpretable

### Models & precision-first tuning
- [x] LightGBM wrapper (native NaN handling; weights passed through; no
      early stopping — a local validation split would violate invariant 1;
      boosting rounds are tuned across walk-forward folds instead).
      (`src/models/gbm.py`; exemplar sweep in
      `experiments/sweeps/lgbm_precision_grid_3y.toml`)
- [x] Random-forest wrapper (sklearn, NaN-native, weights mandatory).
      (`src/models/forest.py`; exemplar config
      `experiments/forest_3y_beat_spy.toml`)
- [x] Full hyperparameter surface on the Phase-1 tree: `min_samples_leaf`,
      `min_samples_split`, `max_leaf_nodes`, `max_features`,
      `min_impurity_decrease`, `ccp_alpha`, `splitter` (`max_depth` stays
      mandatory).
- [x] Precision-over-recall knobs (PLAN §2): numeric `class_weight` on
      every classifier (`w < 1` penalizes false positives → purer positive
      calls), and `precision_targets` in any config reporting
      `recall_at_prec_*` / `thr_for_prec_*` / `n_at_prec_*` — best recall
      subject to a precision floor — per fold, per era, and pooled.
      (`models/common.py`, `eval/metrics.recall_at_precision`)
- [x] Post-hoc calibration (isotonic / Platt), prequentially: with
      `calibration = "isotonic"|"platt"` in a config (or sweep), fold
      Y's raw scores are calibrated on the pooled out-of-sample test
      predictions of folds < Y — already purged/embargoed and strictly
      earlier, so no local split is constructed (invariant 1 intact).
      Folds below `calibration_min_rows` of history (default 1000) stay
      raw and are flagged in the report; the report draws the calibrated
      and raw reliability curves side by side and states the
      across-refit score-stability assumption. Monotone maps leave the
      rankings unchanged — the win is that `thr_for_prec_*` and the
      `score >= p` confidence tiers become real probabilities. `vml-eval`
      re-derives identical calibrated scores from a bundle of raw
      models (nothing new persisted); probabilistic classifiers only.
      (`harness/calibration.py`; exemplar
      `experiments/lgbm_isotonic_3y_beat_spy.toml`)
- [ ] Deployment-time calibration: a deployment refit has no
      out-of-sample history, so `vml-train-deploy` refuses calibrated
      configs today. Design: fit the final calibrator on the *full*
      walk-forward OOS history of the same config and store it in the
      DeploymentBundle (format bump), so `vml-predict` scores read as
      probabilities; until then deployment rankings are identical to
      the uncalibrated config's.
- [ ] SHAP: global importance + per-prediction explanations; compare against
      Phase-1 tree rules.
- [x] Native feature importances as a standard artifact: every model
      exposing `feature_importances()` (tree impurity, forest impurity,
      LightGBM gain — classifier and regressor) gets a per-fold
      `reports/<run>_importances.csv` (cross-fold mean, sorted) plus a
      top-10 table in the report's Interpretability section. Flagged in
      the artifact itself as a *triage list* for importance-guided
      feature subsets (which count as configurations tried), not an
      explanation. (`harness/runner.py::_write_importances_file`)
- [ ] Explainability for forests/LightGBM beyond impurity/gain:
      permutation importance (weighted, on training folds); per-prediction
      reason codes (top signed contributions) as optional columns in
      `vml-predict` output so a ranking is auditable stock by stock.
- [ ] Ablations: raw vs. rank vs. sector-rank features; ± technicals;
      ± classification columns (current-state caveat). The sweep harness's
      `[[feature_sets]]` axis is the mechanism.
- [x] Feature blacklist: `exclude_feature_columns` in any config (and per
      `[[feature_sets]]` entry / top-level in sweeps) — "the whole
      manifest group minus these", applied after any `feature_columns`
      whitelist; excluding an absent column is an error so typos can't
      silently keep a column in. Needed because the `features` group
      contains non-numeric columns no tree model can consume.
- [x] Config ergonomics: default `name` derivation
      (`{model}_{features}_{label}_{content-hash}` — a copied config with
      edited values can't overwrite the original's artifacts), inferred
      `horizon_years` from the label's `{H}y` token, and hierarchical
      feature selection (`[features]` table: groups ⊃ families ⊃ columns,
      family membership mirrored from data/features.md in
      `src/harness/families.py`; blacklisting a child whose parent was
      never selected is an error). Legacy top-level feature keys keep
      working and keep their config hashes.
      (`src/harness/config.py`, `src/harness/families.py`,
      `Dataset.select_features`; example in
      `experiments/tree_depth3_families_example.toml`)
      Sweeps take the same `[features]` table (or a `[[features]]` array
      as the feature axis), infer cell horizons from labels, and derive
      a default `name` (`{model}_sweep_{features}_{labels}_{hash}`) too.
- [ ] Encode the categorical/non-numeric `features` columns (`sector`,
      `industry`, `famaindustry`, `scalemarketcap`, the `Y`/`N` condition
      flags like `negative_equity`, and the `fund_datekey` /
      `fund_reportperiod` date fields) so they become usable as model
      features — today they must be excluded via
      `exclude_feature_columns`. Decide the route first, because
      invariant 4 (no feature engineering here) is in tension with doing
      it locally:
      (a) preferred: upstream encodes them (one-hot / ordinal / native
      categorical dtype) in a new dataset version;
      (b) acceptable if argued: a disclosed, deterministic per-row
      *recoding* in the harness (one-hot, or sklearn/LightGBM native
      categorical support) — representation, not derivation. No
      cross-row statistics under any circumstances: target/frequency
      encoding fitted on the data is leakage.
      Either way, mind the classification columns' current-state caveat
      (data/features.md): `sector`/`industry` are today's values, not
      point-in-time, so a model using them sees a hint of the future.

### Sweep harness (ranges instead of one-config-at-a-time)
- [x] Sweep config (`experiments/sweeps/*.toml`): `[[cells]]` (several
      horizon+label cells in one file), `[grid]` (model-param cartesian
      product), optional `[[feature_sets]]` and `seeds`; expansion capped
      by `max_runs` (default 200). (`src/harness/sweep.py`)
- [x] `vml-sweep` CLI (+ `--dry-run` to print the expansion): every
      expanded run goes through the standard runner — logged to the
      results store (failures included, they still count as trials),
      STANDARD split access only, one report per run under
      `reports/sweeps/<name>/`.
- [x] Ranked sweep summary (`_summary.md` + full-metrics `_summary.csv`):
      pooled `rank_metric` (default: recall at the first precision floor),
      per-cell all-time configurations-tried counts, explicit
      selection-bias warning.
- [x] Random search alongside the grid: a `[random]` table of
      distribution specs (`{low, high[, log][, int]}` or `{choices}`)
      plus `n_samples`/`search_seed`, sampled deterministically (a pure
      function of the sweep content, so `--dry-run` shows exactly what
      will run) and crossed with the grid and every other axis;
      `max_runs` still caps the total and every draw hits the trial
      ledger. Sampled values land in the summary's `sampled_params`
      column. (`harness/sweep.py`; curated search spaces with range
      rationale in `experiments/sweeps/lgbm_random_search_3y.toml` and
      `experiments/sweeps/forest_random_search_3y.toml`, both with a
      `[[features]]` axis so the feature set is searched, not
      hand-picked)
- [ ] Run the real searches against `dataset_v1.1`
      (`lgbm_random_search_3y`, `forest_random_search_3y`, plus the
      grid exemplars), commit the summaries, and pick Phase-3
      candidates for the sealed holdout.
- [ ] Seed-stability pass on the sweep winner (multi-seed sweep; a config
      whose ranking collapses across seeds is noise, not signal).
- [ ] Successive-halving style budgeting if random searches get slow:
      re-run the top decile of a cheap-budget search (low
      `n_estimators`) at full budget via a follow-up sweep file — no
      harness change needed, just two sweep configs.

## 3.5 — Downturn specialization (PLAN §4 Phase 3.5)

Make crash performance a training/selection objective, not just a report
slice. All within the invariants: no local splits, no derived features.

- [ ] Regime-emphasis training weights: config-declared multiplier on
      `sample_weight_{H}y` for training rows whose label windows overlap
      drawdown eras (disclosed, hashed, reported); report the effective
      sample size under emphasis so the shrinkage is visible.
- [ ] Crash-aware `rank_metric` for sweeps: rank candidates by
      precision/recall-at-precision restricted to crash-era test years
      (with the Wilson-interval caveat stated in the summary).
- [ ] Specialist configs: relative (`beat_spy`) labels as the default
      cell for downturn models; sweep tree/forest/lgbm under regime
      emphasis and compare against the unemphasized winners on the
      crash-era table.
- [ ] Two-stage survival gating: stage-1 survival model
      (interim target: `label_{H}_cagr_ge_0` until upstream ships a
      max-drawdown/catastrophe label), stage-2 return model ranks
      survivors only; evaluate the gate's precision cost outside crashes.
- [ ] Upstream requests to file: catastrophe/max-drawdown label
      (`label_{H}_max_drawdown_le_X` or similar); point-in-time
      market-state context features (drawdown-from-high, index vol) if
      regime-conditional models ever need them.

## Model families to explore (PLAN §8)

- [ ] Weighted, calibrated logistic regression on the rank feature set —
      cheapest new family, interpretable coefficients, doubles as a
      stronger baseline. Fold-internal imputation only, disclosed.
- [ ] KNN and SVM comparison runs (registered as experiments like any
      other): rank features only (already scaled), fold-internal
      imputation, subsampling strategy that respects uniqueness weights;
      keep unless they beat trees on the precision-floor metrics.
- [x] Regression reframe mechanism: `lightgbm_regressor` trains on the
      continuous `fwd_{H}y_cagr` / `fwd_{H}y_excess_cagr` columns
      (objectives `regression`/`regression_l1`/`huber`/`quantile` —
      quantile with low alpha ranks by a pessimistic return estimate,
      the regression analogue of the precision knob; `winsorize = q`
      clips the training target fold-internally per the extreme-return
      caveat). Configs set `eval_label` to a binary cell and every
      metric/report/eval stays in the precision@K frame; the trial
      ledger and baseline comparison charge the run to the eval cell.
      Guardrails: continuous columns refuse `astype(bool)` coercion
      under classifiers and vice versa. (`models/gbm.py`,
      `harness/dataset.py::_target_array`; exemplars
      `experiments/lgbm_regressor_3y_cagr_ge_10.toml`,
      `experiments/sweeps/lgbm_cagr_quantile_3y.toml`)
- [x] Regression-run diagnostics beyond the binary frame: continuous
      runs carry the realized outcome through the prediction frames, so
      the era table and pooled block report `fwd_at_K` (mean realized
      CAGR of the top-K picks, picked per year — sweep-rankable via
      `rank_metric = "fwd_at_20"`) and `spearman_ic` (rank IC; pooled
      row is the mean of per-year ICs since per-fold scores aren't
      comparable). Weighted MAE/R² are logged in the results store as
      fit diagnostics only — R²≈0 on stock returns is normal and says
      nothing about the top of the ranking, so neither is ever
      headlined. (`eval/metrics.regression_diagnostics`, `eval/era.py`)
- [ ] Run the regression-reframe spike against `dataset_v1.1`
      (`lgbm_cagr_quantile_3y`) and compare its summary against the
      classification sweeps on the same eval cells before going further.
- [ ] Deep learning goes through upstream first: sequence-shaped dataset
      variant (per-quarter point-in-time history per stock) is a
      prerequisite; do not flatten history locally (invariant 4). Then a
      small TCN/transformer with embedded categoricals, same splits,
      weights, and era-sliced reporting.

## 4 — Phase 4: portfolio construction & backtest

- [x] Backtest harness (`src/portfolio/`, CLI `vml-backtest`, one TOML
      per strategy in `experiments/portfolios/`; design in PLAN §4):
      walk-forward fold bundles score each trade year (deployment
      bundles refused; buys structurally confined to fold years),
      monthly point-in-time cross-sections from `dataset.parquet`
      (latest completed-quarter median snapshot, staleness-capped, no
      label columns), declared score combination
      (`product`/`mean`/`min`/`mean_rank`) + per-model floor + validated
      column filters, buy-and-hold top-K strategy behind a pluggable
      `Strategy` interface, benchmark leg through the same engine under
      identical deposits, XIRR/TWR/drawdown/per-year-era report with
      defensive-hypothesis check, every run logged under scheme
      `backtest`. Exemplar config:
      `experiments/portfolios/allprob_top25_5models.toml` (the live
      five-model AllProb screen).
      Deposits keep rolling past a bundle's last fold year: the
      `model_update` policy serves those years (`refit` = simulated
      point-in-time year-end deployment refits, manual.md §4 rule 7;
      `frozen` = last fold model), with the holdout-era overlap flagged
      as selection-toxic in every report. Refits are disk-cached
      across runs (`experiments/models/refits/`, keyed by train config
      hash + dataset version + year + lag; sidecar-validated before a
      pickle is trusted). Per-model floors via
      `[signal.min_scores]`; whole-share execution with realized
      profit/ticker in the trade log; artifacts under
      `reports/backtest/<name>_<config-hash>.*`.
- [x] Investability filter mechanism: `[[investability]]` column screens
      are a mandatory config field (explicit `investability = "none"`
      opts out and is flagged in the report). Choosing honest thresholds
      from `log_marketcap` / `dollar_volume_3m` / `amihud_12m` is still
      open (below).
- [x] Transaction-cost mechanism: flat per-side `cost_bps`, required in
      every config (no default); costs paid inside TWR. Microcap
      fidelity (spread/impact models) is an open question, PLAN §8.
- [x] SPY benchmark under identical cash flows; drawdowns and per-year
      era slices with crash tagging in every report.
- [x] Defensive-hypothesis check: benchmark down-years broken out in the
      report (not testable when the window has none — the report says
      so).
- [x] Versioned price panel `data/datasets/prices_vX.Y/` (consumer
      contract in `src/portfolio/prices.py`; builder
      `scripts/build_price_panel.py`): extracted from the raw
      `SEP.closeadj` / `SFP` tables — the labels' own price source —
      via the `TICKERS` ticker→permaticker mapping, restricted to a
      pinned dataset's universe, with mapping/cleaning/coverage stats
      and raw-pull provenance in the manifest. The one sanctioned
      raw-table read in this repo: outcome price paths only, never
      features. Build it locally with the upstream raw dir symlinked
      (e.g. `data/raw -> ~/radarash-dataset/data/raw`):
      `python scripts/build_price_panel.py data/raw dataset_v1.1
      --out-version prices_v1.0`.
- [ ] Run the real backtest of the live five-model screen once the
      panel is built and the five walk-forward bundles exist
      (`vml-run` each model config, fill in the bundle run ids, then
      `vml-backtest experiments/portfolios/allprob_top25_5models.toml`);
      promote the report.
- [ ] Pick and justify investability thresholds (microcaps dominate;
      report sensitivity of the headline result to the floor).
- [ ] Equal-weight-universe benchmark as a second comparison leg.
- [x] Sell discipline: `sell_below_criteria` strategy — held positions
      failing the sell criteria are sold at rebalance (top-K drop-out
      alone is never a sell); optional `[sell]` section for a separate
      criteria band (hysteresis), inherited from the buy criteria
      otherwise; sells logged with per-cause reasons.
- [ ] Richer strategies behind the `Strategy` interface: periodic full
      rebalance, stop-loss / trailing-stop sells, position caps,
      partial trimming (sell down to weight instead of all-or-nothing).
- [ ] Cross-section rank freshness: ranks in a backtest cross-section are
      relative to each snapshot's own quarter. Consider an upstream
      "as-of re-rank" artifact if this approximation ever drives results.

## Upstream coordination / watch list

- [ ] Earliest-trustworthy-year (survivorship-depth) verification is still
      open upstream; until resolved, treat pre-2000 cross-sections with
      suspicion (PLAN §8).
- [ ] Restated-dimension dataset variant (decision 0009) needed for the
      restated ablation.
- [x] ~~Versioned price panel for Phase-4 backtests~~ — resolved locally:
      `scripts/build_price_panel.py` extracts it from the raw
      SEP/SFP/TICKERS tables (see §4 above), so no upstream build stage
      is needed. Upstream only needs to keep shipping `data/raw/`.
- [ ] Inner-validation role (only if early stopping ever becomes worth
      it): invariant 1 stays absolute — no local split carving, however
      "temporal and careful" it looks, because the purge/embargo
      machinery lives upstream and a second local implementation would
      drift silently. If a use case genuinely needs a within-train
      validation set (LightGBM early stopping is the only candidate so
      far; calibration is served prequentially without one), the
      sanctioned path is an upstream request: an additional
      `inner_val` role inside each walkforward fold's training window
      (last pre-purge year, purged/embargoed against the rest of train
      with the same discipline as test), shipped as extra rows in
      `splits.parquet`. Additive and opt-in — configs that ignore the
      role are byte-identical in behavior, so no "third split always"
      burden — and frozen/citable like every other fold definition.
      Weigh against the cheap alternative first: boosting rounds are
      already tuned across folds by the random search.
- [ ] Any feature request discovered during modeling → file upstream, new
      dataset version (never engineered here).
