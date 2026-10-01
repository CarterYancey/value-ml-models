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
- [x] Final-eval script for the sealed `holdout` fold: one look per cell,
      logs the result whether good or bad. Nothing else may read holdout
      tags. (`scripts/run_final_eval.py` — the only FINAL_EVAL entry
      point; a completed eval per cell is recorded in
      `reports/final_evals.csv`; repeating one needs a disclosed reason.)

### Registered diagnostics (from data/manual.md §7 — diagnostic only)
- [ ] Leakage-gap experiment: identical model under `random_kfold`,
      `entity_holdout`, and purged `walkforward`; report the score gaps.
- [x] Era-identifiability probe: predict calendar year from features alone,
      raw vs. rank sets. (`src/diagnostics/era_probe.py` + `era_metrics.py`
      + `probe_models.py` (multiclass tree / forest / LightGBM / XGBoost,
      weighted);
      `scripts/run_diagnostic.py era-probe <config>` is the only place
      that grants `REGISTERED_DIAGNOSTIC` access. Target = year of
      `snapshot_date` under `entity_holdout` (entity-disjoint, so firm
      memorisation can't help; `random_kfold` allowed as the leaky upper
      bound). Reports in `reports/diagnostics/`: headline vs. uniform /
      majority-year / train-prior baselines, per-year slice, post-burn-in
      slice, confusion heatmap, importances, tree rules naming which
      thresholds date a row. Exemplar configs in
      `experiments/diagnostics/era_probe_{raw,rank,raw_tree}_3y.toml` —
      the raw arm's non-numeric exclusion list is written from
      data/features.md and must be confirmed on the first real run.)
      **Findings** (`reports/promoted/era_probe_rank_fingerprints/`):
      on `dataset_v1.0` the rank arm dated rows at 0.954 accuracy
      (majority-year 0.09) because within-quarter percent ranks of
      integer composites and zero-inflated ratios are quarter-specific
      constants (four rank columns alone: 0.917; their raw values:
      0.148). Reported upstream; `dataset_v1.2` un-ranked the
      composites. On v1.2: all ranks 0.456, ranks minus technical/trend
      0.322, misses on adjacent years — the residual is regime
      recognition, tier nullity in 1997–2004, and secular drift, i.e.
      point-in-time economics, not a leak. Walk-forward/holdout results
      were never inflated by the fingerprint (unseen test quarters);
      `entity_holdout` retains regime hindsight and stays diagnostic-only.
- [ ] Boundary check on v1.2 zero-inflated rank columns (upstream brief
      §8, second query): does the first non-zero rank still equal the
      cell's zero share? A judgement call about a weak market-state
      signal, not a leak; record the answer in the brief §10.
- [ ] Further tests of the "entity_holdout learns the era, not the stock"
      concern, once the leakage-gap experiment exists (run it on v1.2 —
      on v1.0 its gap would mostly be the fingerprint): (a) global top-K
      vs. per-year top-K precision under `entity_holdout` — if pooled
      picks beat per-year picks, the model is timing eras, not selecting
      stocks; (b) share of an entity-holdout model's score variance
      explained by year (one-way ANOVA R²), a cheap add-on to the
      leakage-gap report.
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
- [ ] Historical analogues ("stocks that looked like this before"): pick
      one stock from an inference dataset, score it with several
      deployment bundles (e.g. the best 1y/3y/5y configs), and for each
      model show the labeled historical rows that **land in the same
      leaves as the stock**, and what actually happened to them.
      Explanation, not evaluation (PLAN §4 Phase 3, "Historical
      analogues"). Sketch:
      - **Primary method: leaf co-membership.** Every model in the zoo
        except the baselines is trees, so "similar" can mean similar *as
        the model sees it*: rows the model routes to the same leaves.
        This uses the model's own split thresholds and NULL routing (no
        distance metric to choose, no imputation, no feature scaling),
        and it needs no SHAP.
        - *Single tree*: the stock's leaf **is** a rule. Show the rule
          (reuse `src/explain/rules.py`) plus the training rows in that
          leaf: "stocks with P/B rank < X and … — here they are, and here
          is how each one turned out." Build this first.
        - *Forest*: proximity = share of trees in which a row shares the
          stock's leaf (sklearn `apply()`). Rank analogues by proximity.
        - *LightGBM / XGBoost*: leaf indices via `predict(pred_leaf=True)`.
          Boosted trees fit residuals, so plain leaf-sharing counts are
          weaker. Weight each tree by |leaf value| on the stock's path,
          and report both weighted and unweighted proximity until one
          proves more readable.
        - *Why these leaves*: list the split features on the stock's
          decision path(s), counted across trees for ensembles. That is
          a cheap "what drove it" without SHAP. When the SHAP /
          reason-code items land, show their signed contributions
          alongside.
        - *Scale*: rows × trees leaf matrices get big (≈1M rows × 500
          trees). Stream `apply` over row chunks and accumulate only the
          match counts against the query stock(s); never materialize the
          full matrix.
      - **Fallback: feature-space nearest neighbors**, only for models
        without leaves (baselines, a future logistic). Use the model's
        top-k features weighted by |contribution|, in `_rank` /
        `_secrank` form so eras compare (raw levels drift; inference
        ranks are pooled over one cross-section, so note that). A NULL
        matches a NULL and costs a fixed penalty against a value. No
        imputation.
      - **Candidate pool**: the labeled rows the bundle was trained on
        (same dataset version), all eras, delisted rows included — a
        delisted analogue is exactly the history this is for. Leaf
        statistics use the rows as the model saw them (all kinds,
        `sample_weight_{H}y`-weighted). The displayed list keeps one row
        per `permaticker` (highest proximity, median kind preferred), so
        one stock's overlapping quarters can't fill it. Show the era mix
        of the analogues. Exclude the query stock's own history by
        default (flag to include).
      - **Output** per model: score + rank in today's cross-section, the
        leaf rule (single tree) or top path features (ensembles), then N
        analogues with `ticker` (display only; match on `permaticker`),
        `snapshot_date`, proximity, the path features' values next to
        the query's, and realized `fwd_{H}_*` / `label_{H}_*` /
        `delisted_in_window_{H}` for every horizon. Summary: weighted
        positive rate and Σ weights of the analogues. CSV + markdown
        under `predictions/` with a `.meta.json` sidecar (bundles,
        dataset + inference versions, method, N, git SHA). CLI:
        `vml-analogues --ticker XYZ <bundles…>`, or
        `vml-predict --analogues XYZ`.
      - **Guardrails**: the deployment fit chose those leaves *from*
        these rows, so the leaf's outcome rate is in-sample by
        construction. For a single tree it is essentially the score
        itself. The output must say it is not an accuracy or probability
        estimate. An honest leaf hit-rate would need walk-forward fold
        models scored on their own test folds. That belongs on the
        evaluation side and is a separate item, not part of this tool.
        Refuse if the inference and training manifests differ in
        version/feature set. Proximities and analogue outcome rates must
        never become model features (invariant 4). A kNN *classifier* is
        a separate walk-forward experiment (PLAN §8, "Other classifier
        families").
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
- [x] Catalog answers "did it beat the baseline, and what did I learn?":
      headline shown against the best baseline in the same cell with a
      signed lift; listing grouped by cell and ranked by lift inside it
      (no cross-label sort); `note` column from the config; `final_eval`
      column from the sealed ledger; `★` for promoted; restricted
      schemes flagged; portfolio configs listed as their own kind.
- [x] Config hygiene: new `experiments/**/*.toml` are git-ignored; a
      config earns tracking through `vml-promote <name> --note "..."`,
      which snapshots the config into the promoted directory, writes the
      note into the config (outside the hash), stages both (`git add -f`)
      and regenerates the `reports/promoted/README.md` index.
- [x] Final eval without a copied `*_holdout.toml`:
      `scripts/run_final_eval.py` takes the selected walk-forward config
      and switches the scheme in memory. `--phase` is gone: the seal is
      per cell (label, horizon, holdout window from `split_folds.parquet`
      — not the dataset version, which re-used the same rows across
      v1.1–v1.4); a further look needs `--reopen "reason"` and is then
      counted in the report, the ledger and the catalog (`✓ look k/N`).
      Old `phase` ledgers migrate in place and their rows count as looks.
- [x] Cross-sweep digest: `vml-experiments sweeps` flattens every sweep
      summary CSV into one per-cell markdown (top runs across sweeps with
      lift, "what wins" per feature set / model / swept parameter,
      continuous axes quartile-binned). Fixed `runs` crashing on ledger
      rows without a horizon (backtest / deployment).
- [ ] Backfill notes on the tracked sample configs (what each one
      taught) so the catalog's `note` column is populated from day one.
- [x] Split the lab notebook (2026-09-28): `docs/logbook.md` (one
      short entry per sweep, `vml-logbook`), `docs/findings.md`
      (current state, under ~150 lines), `docs/notes/` (detail).
- [x] Unattended runs (2026-09-28, docs/agents.md): run queue
      (`vml-queue`, `experiments/queue.toml`), `vml-sweep --resume`
      from per-run result records, ledger shards
      (`experiments/ledger/`, `VML_RESULTS`, `VML_LEDGER_READ`),
      checkpoints on `claude/` branches, and
      `scripts/check_tracked_configs.py` with the `pr-hygiene`
      workflow for pull requests.
- [x] Forest runs needed ~18 GB: fitted fold models kept their
      training frame alive through the stored sample weights. Weights
      and targets are now copied (2026-09-28).
- [ ] Carter: machine user and token, branch rulesets, sandbox
      resources (docs/agents.md, "Setting up").
- [ ] First unattended session end to end in a sandbox: queue, stub,
      checkpoint, push from the machine account.
- [ ] Decide what to do with the unpromoted configs the branch
      carries (`python scripts/check_tracked_configs.py` lists 11):
      promote, name in `experiments/KEEP`, or untrack with `--fix`.
- [ ] `vml-experiments sweeps` ranks rows on different metrics (p@10 /
      p@20 / p@50) in one table — rank within one metric, or group by
      it.
- [x] Guard against editing a sweep TOML after it has run:
      `vml-sweep` copies the sweep file into `reports/sweeps/<name>/`
      and refuses to run when that directory holds the copy of a
      different sweep identity. Every run also writes
      `<run>_config.json` (full config, resolved feature columns)
      beside its report, `vml-run` copies its TOML there, and
      `vml-promote` carries the as-run copy (`config_as_run.toml`).
      `note` is now accepted in sweep files, so promoted sweep configs
      load again.
- [ ] `lgbm_candidate_sets_3y.toml` is pinned to dataset_v1.0 and never
      ran — re-pin to v1.4 or drop it.
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
- [x] Memory-bounded data access (the real cause of the vml-sweep OOM
      at ~29 GB RSS): `apply_split(columns=...)` merges a column
      projection instead of the full-width frame (string metadata
      columns dominated the old copies), the label-observability
      column is always force-included so validation can't be projected
      away, split tags load parquet-filtered per (scheme, horizon)
      instead of the whole tag table, manifest validation reads parquet
      metadata instead of materializing the frame, and deployment
      refits fit on a projection. Runner/eval pass exactly the columns
      a run touches; `dataset.data` stays full-width for the backtest
      cross-section. vml-sweep prints peak RSS per run so regressions
      are visible before the OOM killer finds them.
- [ ] `vml-experiments list` shows eval configs (`experiments/eval_*.toml`)
      and `experiments/queue.toml` as broken experiment configs ("lacks
      required fields"); recognize them as their own kinds.
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
      predictions of the earlier folds **whose outcomes were known
      before year Y** (fold f with f + H < Y for an H-year label), so
      no local split is constructed (invariant 1 intact).
      *Corrected 2026-09-30 (`claude/calibration-label-lag`):* until
      then every fold < Y was used, which handed fold Y's calibrator
      outcomes from up to H years in its future (docs/notes/
      process-issues.md). No fit, ranking or uncalibrated metric was
      affected; no calibrated run had been recorded before that day.
      Rows on one isotonic step now keep their raw order (they were
      tied, and a top-K over ties is a top-K in row order).
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
- [x] Boolean flags as model inputs (2026-09-30, same branch): the
      nullable boolean feature columns are handed to models as 0/1
      floats with NULL kept (`harness.dataset.feature_matrix`), route
      (b) below for the flags only. Strings and dates stay excluded.
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
- [x] Run the real searches against `dataset_v1.1`
      (`lgbm_random_search_3y`, `forest_random_search_3y`, plus the
      grid exemplars), commit the summaries, and pick Phase-3
      candidates for the sealed holdout. (Aug–Sep 2026: forest, xgb,
      lgbm and quantile-regressor searches on 3y beat_spy; conclusions
      in docs/findings.md, summaries promoted.)
- [x] Run the v1.4 baselines (`scripts/run_baselines.py dataset_v1.4`).
      (2026-09-26: 80 runs over the 20 stored-label cells. Derived-label
      cells are not covered by the script.)
- [x] Run the carry-forward sweeps on v1.4:
      `forest_candidate_sets_3y` and `xgb_candidate_sets_3y`.
      (2026-09-27: forests p@20 0.42 pooled, 0.22 in 2013–19 against a
      0.28 base rate; xgb 0.37 / 0.17. Lower than the same
      configurations on v1.1, on a column set that differs by 13
      added and 4 dropped columns; the cause is open, so the v1.1
      findings are unconfirmed, not refuted. No 3y beat_spy finalist;
      the 3y holdout stays unopened. docs/findings.md.)
- [x] Run `forest_v11_code_control_3y` (4 runs, needs
      `dataset_v1.1`). (2026-09-28: all 64 fold rows equal the August
      ledger rows; the code is not the cause.)
- [x] Run `forest_feature_ablation_3y`. (2026-09-28: 8 runs, one
      seed, not the 24 in its header. Arm fs0, the v1.1 column set,
      scored p@20 0.44 against the predicted 0.58: the 13 added
      columns are not the cause, though removing them raises PR-AUC
      by 0.01-0.02. The arms cannot be ranked. docs/findings.md.)
- [x] Do the 120 columns shared by the v1.1 and v1.4 feature sets
      hold identical values? (2026-09-28: no. 17 changed at v1.2,
      upstream decision 0016; 103 are equal. `data/versions.md`
      updated.)
- [x] Run `forest_v11_column_control_3y` and
      `forest_v14_unchanged_columns_3y`. (2026-09-28: the v1.1 edge
      is in the v1.1 values of the 17 columns decision 0016
      re-mapped: p@20 0.57-0.58 with them, 0.43-0.47 without. The
      four dropped columns change nothing, and v1.1 and v1.4 give
      identical fold rows on the other 103 columns.)
- [ ] Quarter identifier or stock information? Per-quarter picks on
      v1.1 (p@K within each test quarter, or the spread of the
      picks over a year's quarters) for the runs with and without
      the 17 columns. Needs per-quarter metrics or saved
      predictions. Then a note upstream: decision 0016 expects
      walk-forward not to be inflated by the keys. Low priority, it
      changes nothing about what to run on v1.4.
- [x] Run `baseline_lowvol_rank_3y`. (2026-09-28: best single
      factor is `conservative_score_rank`. From-entry cell: 0.39
      against forests 0.50 and LightGBM 0.39-0.40. Whole-path cell:
      0.34 against forests 0.37-0.39. 3y beat_spy: 0.49, level with
      the best forest arm on v1.4.)
- [x] Choose the primary cell. (2026-09-28, Carter: cagr >= 10% &
      drawdown from entry < 20%. The choice of label stays part of
      the experiments.)
- [x] Run `forest_feature_sets_dd_entry_3y`. (2026-09-29: no arm
      beats the 112 ranks; most of the signal is `vol_12m_rank`,
      `vol_36m_rank`, `conservative_score_rank`.
      docs/notes/2026-09-29-feature-sets-dd-entry.md)
- [x] Label screen: report-only outcomes of a run's top-K picks
      (`pick_outcomes`, `src/eval/picks.py`, docs/experiments.md;
      2026-09-28). Hit rate for binary outcomes, mean and median for
      continuous ones, beside the same over all test rows, plus the
      distinct stocks among the picks; in run reports, the ledger's
      per-fold metrics and sweep summaries; settable from an eval
      config for saved bundles.
- [x] Run `baseline_pick_outcomes_3y`. (2026-09-29: the bar is a
      beat-SPY hit rate of 0.49 and a median excess CAGR of about
      zero. docs/notes/2026-09-29-label-rungs-dd-entry.md)
- [x] Label-comparison backtest template. (2026-09-29, decision 6
      of docs/notes/2026-09-29-decisions.md: top 10 a month, equal
      weights, buy and hold, 35 bps, `dollar_volume_3m >= 100000`,
      buys 2005-2020, valued end of 2023; then a cap of 2 per
      sector, decision 7. `experiments/portfolios/bt_*.toml`.)
- [x] Run `forest_label_rungs_dd_entry_3y`. (2026-09-29: the
      thresholds move p@20 and PR-AUC and not what the picks go on
      to do; no rung passes the screen on every seed.)
- [x] Parameter search per family. (2026-09-30, in the candidate's
      cell C instead of the primary cell, 20 draws each: no draw of
      any family exceeds the reference forest's fold-mean PR-AUC
      0.585; boosted families pick worse at the same PR-AUC.
      docs/notes/2026-09-29-searches-nonloser.md)
- [x] Investability filter before any top-K number is acted on.
      (2026-09-29: every backtest applies `dollar_volume_3m >=
      100000`; the screen still does not, see the next section.)
- [x] Report the number of distinct `permaticker`s among the top-K
      picks per test year (`n_stocks_at_K`, part of `pick_outcomes`;
      2026-09-28). Runs without `pick_outcomes` do not carry it.
- [ ] A crash-window line in the era table for path labels: entry
      years whose window holds a market crash (2005-08, 2019 at 3y)
      are where the compounder models fall to the base rate.
- [ ] A config hash that leaves the sweep name out (the
      `identity_hash` exists for single configs), recorded in the
      ledger, so a re-run under another sweep name can be matched to
      the original by hash.
- [ ] `vml-experiments verify`: expand each config under
      `experiments/` and compare its config hashes with the ledger's,
      so a config that no longer matches its own runs is reported
      (today: `lgbm_random_search_3y`, `lgbm_cagr_quantile_3y`,
      `forest_random_search_3y`).
- [ ] `vml-experiments columns <run> <run>`: diff the resolved feature
      columns of two runs from their `*_config.json` records.
- [x] Multi-seed the drawdown-compounder labels on v1.4
      (`fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` and
      `… & fwd_3y_max_drawdown_from_entry < 0.2`). (2026-09-28: three
      baseline sweeps, `lgbm_drawdown_compounder_seeds_3y` and
      `forest_drawdown_compounder_seeds_3y`, 48 runs. Held over
      seeds and in 2013-20; forests p@20 0.50 against a 0.21 base
      rate and 0.37-0.39 against 0.11, ahead of LightGBM; no lift
      for entry years 2005-08 and 2019. docs/findings.md.)
- [ ] Baselines for derived-label cells: `scripts/run_baselines.py`
      takes stored labels only, so each derived cell needs hand-written
      baseline sweeps today. Give the script a `--label "<expression>"`
      option.
- [ ] Random-ranking baseline over several seeds in the standard grid:
      one seed scored p@20 0.39 on 3y beat_spy against a 0.35 base
      rate, and the catalog measures lift against it.
- [x] Ledger: an interrupted run's fold rows were logged `completed`.
      Fold rows are now held until every fold has finished and a
      stopped run leaves one `failed` row (`RunLog`,
      `src/harness/results.py`; runner, `vml-eval`, era probe).
- [ ] Ledger: a run whose process is killed outright (OOM,
      `kill -9`) leaves no row, so the trial goes uncounted. Log a
      row when a run starts, once ledger readers can ignore it.
- [x] `[[sets]]` axis: whole parameter dictionaries taken as units (the
      top candidates of a wide search), crossed with cells, feature sets,
      `[grid]`, `[random]` and seeds; a parameter lives in exactly one of
      `[model]`, `[grid]`, `[random]`, `[[sets]]`. Summary carries
      `param_set` / `set_params`.
      (exemplar: `experiments/sweeps/lgbm_candidate_sets_3y.toml`)
- [x] Multi-seed sweeps report per candidate: one seed-stability report
      each (mean / std / min / max / 95% t-interval across seeds, pooled
      and per test year), summary ranked by the mean with the spread
      beside it (`_summary_seeds.csv`), per-seed run reports under
      `seeds/`. (`src/harness/seed_report.py`)
- [x] Seed-stability pass on the sweep winner (multi-seed `[[sets]]`
      sweep over the top candidates; a config whose ranking collapses
      across seeds is noise, not signal). (v1.1: xgb spread ≤ 0.02 over
      3 seeds; forest top candidates over 2–4 seeds within noise of one
      another. The v1.4 re-run is the item above.)
- [x] GPU opt-in for LightGBM: `device = "cuda"` (or legacy-OpenCL
      `"gpu"`) on `lightgbm`/`lightgbm_regressor`, passed through as
      LightGBM's `device_type`. Requires a CUDA build of lightgbm (the
      PyPI wheel is CPU-only; the install command is in
      `models/gbm.py::LGBM_DEVICES`, and a cpu-only build asked for
      cuda fails with that command, not an opaque error). GPU histogram
      arithmetic differs slightly from CPU, so `device` is a model
      param: CPU and GPU runs hash as distinct configs and are never
      mixed in the trial ledger. Ruled out for the other families:
      sklearn trees/forests are CPU-only, and cuML's forest supports
      neither `sample_weight` (mandatory uniqueness weights) nor native
      NaN routing — incompatible with the contract, not just
      inconvenient.
- [x] XGBoost family (`xgboost` / `xgboost_regressor`, hist method) —
      the GPU path that needs no custom build: `device = "cuda"` works
      from the stock PyPI wheel. Harness protocol throughout (mandatory
      uniqueness weights, native NaN routing, no early stopping);
      numeric `class_weight` maps to `scale_pos_weight` with identical
      semantics to every other classifier ("balanced" computes
      Σw_neg/Σw_pos fold-internally); regressor mirrors the reframe
      (`eval_label`, `winsorize`, `quantile` objective via
      `quantile_alpha`); gain importances feed the standard artifact;
      prequential calibration applies. Guardrails: `device` is a model
      param (cuda and cpu runs hash as distinct configs), and because
      XGBoost silently falls back to CPU when no GPU is visible, the
      wrapper reads the fitted booster's own config after every
      non-cpu fit and refuses if the actual device differs — a CPU fit
      can never be logged under a cuda hash. (`src/models/xgb.py`;
      exemplar `experiments/sweeps/xgb_random_search_3y.toml`, same
      cell/axes/metrics as the LightGBM search for a fair
      family-vs-family read)
- [ ] Successive-halving style budgeting if random searches get slow:
      re-run the top decile of a cheap-budget search (low
      `n_estimators`) at full budget via a follow-up sweep file — no
      harness change needed, just two sweep configs.

### Next, from Carter's direction of 2026-10-01 (decision 36)

The working assumption is that 2021-26 is a bubble a value strategy
trails through; the candidate goes to paper trading as it is; the
search continues, wider. Each item below is laid out in
docs/notes/2026-10-01-research-plan.md (what the record already says,
what it needs, how it is read). New arms are judged on walk-forward
2005-2020 against same-size peers; 2021-26 is context.

Carter's:

- [ ] **Open and merge the pull request** from
      `claude/results-2026-10-01b` (the item in the section below; it
      now also carries docs/paper-trading.md, the research plan, the
      three queued sweeps and the Piotroski result).
- [ ] **Set up paper trading on the host**: docs/paper-trading.md.
      Three `vml-train-deploy` commands (the bundles built in the
      sandbox stay in the sandbox), an `inference_<date>` dataset
      from upstream each month, one `vml-predict` command. Two paper
      portfolios: buy and hold, and the rank sell discipline. The
      path was checked end to end on 2026-10-01 (9 of the backtest's
      10 picks for August 2026).
- [ ] **Two rules to accept or change** before a session on other
      model families (research plan, item 7): fold-internal median
      imputation with an is-missing indicator for models that cannot
      take NULLs; and "a learned transform (clusters, embeddings) is
      allowed when it is fitted on the fold's training rows and saved
      in the fold's bundle, never otherwise". And whether PyTorch may
      join the dependencies (scikit-learn's MLP needs nothing new).

Ready to run ("work the queue"; `vml-queue status`):

- [ ] `baseline_factors_crash_dd50`, `forest_crash_dd50`: the
      over-priced-stock model, "fell 50% from entry" within one and
      three years inside the liquid half. Read on precision at the
      top by year, on what the calls went on to do, and on whether
      the count of high-confidence calls rises before 2008 and 2020
      or after (the market-state question).
- [ ] `lgbm_regressor_growth_allrows_3y`: continuous models, LightGBM
      on 3y CAGR and excess CAGR, huber and three quantiles, read
      against same-size peers.

Small code, then a sweep (each on its own `claude/<topic>` branch):

- [ ] **`combine = "worst_rank"`** in `vml-backtest` and in
      `vml-eval`'s `blend`: rank by the worse of the models' ranks,
      which is "in every model's top N" for any N. Then the
      candidate's three legs by worst rank against by mean rank, on
      the screen with peers.
- [ ] **`vml-predict --holdings <file>`**: mark which held stocks the
      rank sell rule would sell this month, so portfolio B's sells do
      not have to be read off the CSV by hand.
- [ ] **A cash rule as a `Strategy`**, if `forest_crash_dd50` shows
      the count of high-confidence calls leading the market.
- [ ] A position cap (carried from below; low priority).

Sessions of their own (research plan, items 6 and 7):

- [ ] **Calibration and confidence-weighted sizing.** Start by
      measuring whether outcome rises with rank inside the forest's
      top 50 of a month at all; then the design of a target whose
      base rate does not move with the market (the peer-relative
      label, upstream).
- [ ] **Other model families**: a regularised logistic regression on
      the ranks, an MLP, a fold-internal clustering as an input; on
      the continuous and peer-relative targets first.
- [ ] **A short leg**, only if `forest_crash_dd50` reaches a
      precision that justifies it: borrow costs, recalls and
      unbounded loss are not in the engine.

Done under decision 36 on 2026-10-01:

- [x] The candidate's three models refit for deployment and the
      prediction path run end to end; docs/paper-trading.md; the two
      factor configs promoted.
- [x] The nine Piotroski signals against the composite F-score
      (`forest_piotroski_3y`): docs/logbook.md.
- [x] "Data before 1998": closed by Carter (Sharadar starts in 1998).

### Next, from the second session of 2026-10-01 (decisions 27-35)

Start with docs/findings.md, then docs/notes/2026-10-01-out-of-sample.md
and docs/notes/2026-10-01-large-caps.md. In one paragraph: traded to
the end of the price panel (2026-08-21) the candidate ends 10% behind
SPY (its sell-discipline variant level). The forest's precision held on
the holdout (0.65 at 20 picks a year, 0.73 at 50, base rate 0.38) and
it kept avoiding losers; but SPY outran equal-weighted stocks of every
size in 2021-26, and against stocks of their own size the candidate's
picks led by 5 to 6 points a year in 2005-2020 and by nothing after.
Inside large caps no model chooses better than return on capital
alone. Nothing more is run on 2021-26 and the search on these columns
is closed for now (decision 34).

Carter's, in order:

- [ ] **Open and merge the pull request** from
      `claude/results-2026-10-01b` into `Claude`
      (`gh pr create --base Claude --head claude/results-2026-10-01b --fill`).
      Five code changes (506 tests pass), the docs, the promoted
      results and the ledger shard; passes
      `scripts/check_tracked_configs.py`. The code, by branch (all
      contained in it; delete them after the merge):
      `claude/predict-selection` (`vml-predict --filter --pick
      --max-per-group`: the backtest's floor and sector cap on the
      ranking); `claude/backtest-calendar-years` (**a fix**: the
      reports' yearly table ran December to December);
      `claude/backtest-universe-outcomes` (every backtest report sets
      its buys beside all candidates and beside same-size peers);
      `claude/sector-feature` (`sector` as a model input);
      `claude/screen-size-peers` (`[pick_screen] peer_column`: the
      same-size reference on the sweep screen). docs/agents.md is
      rewritten in it, with your leave: read "Two ways of working".
- [x] **Decide what the portfolio is for, and its yardstick.**
      (Carter, 2026-10-01, decision 36: to beat the market over the
      long term; 2021-26 is taken as a bubble and waited out.) Against
      SPY the candidate is level over 21.6 years (11.3% to 12.0% a
      year against 10.9%) with three quarters of the worst drawdown,
      37% ahead at the end of 2020 and 10% behind now. Against stocks
      of its picks' own size it led until 2018 and has not since. If
      the aim is to beat SPY, the candidate is a starting point and
      the upside has to come from somewhere these columns do not
      reach; if the aim is market-like return with fewer losers, it is
      a result. Findings, "What this says about the thesis".
- [x] **Paper-trade the fixed candidate, or not.** (Yes: decision 36;
      carried to the section above.) (Your reading of
      2021-26 as a bubble the strategy sits out, decision 35, is a
      reason to: on 1999-2004 a stand-in for the candidate trailed in
      the last year of the run-up and led by 9 points a year for the
      buys of 2000-02. One precedent, and a different kind of
      run-up.) Mechanics as in
      docs/notes/2026-10-01-candidate.md ("Run it on today's stocks":
      `vml-train-deploy` the three configs, then `vml-predict ...
      --filter "dollar_volume_3m_rank >= 0.2" --pick 10
      --max-per-group 2`); needs an `inference_<date>` dataset from
      upstream. Buy and hold beside the sell discipline, both judged
      on `vs_peers` as well as on SPY. No other blend is proposed:
      choosing one now would be choosing it on 2021-26.
- [ ] **A baseline on the holdout rows of cell C**, if you want one:
      the look's report has none ("No baseline runs recorded for this
      cell"), so whether lowest volatility alone would have scored the
      forest's 0.65 there is not known. It is a further read of the
      holdout rows (`--reopen`, counted).

Upstream requests (a new dataset version; nothing is derived here).
The first three are new and come from decision 32:

- [ ] **An outcome and a label measured against same-size peers**:
      per horizon, `fwd_{H}y_cagr` minus the mean of the same quarter's
      stocks in the same band of market-capitalization rank, and its
      sign as a label. This is the target that asks a model to choose
      well rather than to prefer large companies. A cross-row label:
      it belongs upstream, beside the split machinery (a peer's window
      can outlive the row's embargo).
- [ ] **Size-neutral ranks** of the columns the models lean on
      (volatility, return on capital, momentum, the conservative
      score): ranked within a size band, like the sector ranks.
- [ ] **Information about upside that prices and statements do not
      carry**, if the raw tables have it: insider transactions
      (Sharadar SF2: net buying, clustered buys) and institutional
      holdings (SF3: changes in ownership), point-in-time by filing
      date. Inside large caps the 112 ranks rank risk and one quality
      factor and nothing else (docs/notes/2026-10-01-large-caps.md).
- [ ] **Market-state features** (PLAN 5.6): the thesis's condition
      (2), the era, is the whole of 2021-26, and a stock's own columns
      cannot say what era it is. Carried from the section below.
- [x] **Data before 1998, if it can be had** (closed by Carter the
      same day: Sharadar starts in 1998 and nothing comparable goes
      further back).
      The panel and the snapshots begin on 1997-12-31, so the first
      possible picks are January 1999: the test of decision 35 saw
      the last year of the dot-com run-up and its aftermath, not the
      years the bubble grew. Whether a low-risk, quality selection
      trails for years while a bubble inflates, the question 2021-26
      raises, needs 1990-1998. Check where the raw tables start; if
      the vendor's history starts there too, this needs another
      source for prices and statements.
- [ ] **An equal-weighted benchmark series in the price panel** (the
      investable universe, and its largest fifth), so a backtest can
      be set beside "the average large stock" as a portfolio, not
      only per buy.
- [ ] Delisting-aware outcomes and within-sector risk ranks: carried
      from the section below.

Proposed, not built (each on its own `claude/<topic>` branch):

- [ ] **"The index minus the predicted losers"**: a
      capitalization-weighted portfolio of large caps without the
      forest's worst quintile, the literal form of the thesis and the
      use the forest's ranking supports (among large caps it separates
      the worst quintile and nothing above it). Needs a "buy every
      candidate above a rank" strategy. Recorded with its two
      problems: it would have left out NVDA, TSLA and META in 2023
      (they rank in the forest's middle), and it is a 600-stock
      portfolio, not a screener for one person.
- [ ] **A position cap** in the strategy. Carried from below; low
      priority (the candidate's largest holding is 8%).
- [ ] `peer_column` in the sweep configs that are run from here on,
      and in `eval_screen_dv100k.toml`'s successors: a sweep without
      it is read against all rows, which is mostly size.

Settled in this session (details in docs/findings.md):

- [x] The holdout look in cell C read (decision 29); the candidate
      traded to 2026-08-21 (28); why it ended behind SPY (30, 32);
      `sector` as a model input: built, changes nothing (31); the
      floor and the sector cap in `vml-predict`; selection inside
      large caps: no arm passes (32, 34); docs/agents.md rewritten
      (27).

### Next, from the sessions of 2026-09-30 and 2026-10-01 (decisions 14-26)

Start with docs/findings.md and docs/notes/2026-10-01-candidate.md.
The candidate is cell C's forest, 12-month momentum and return on
capital by mean rank; 31 backtest configurations were tried on buys of
2005-2020 and no more are run on those years.

Carter's, in order:

- [x] **Open and merge the pull request** from
      `claude/results-2026-10-01` into `Claude`
      (`gh pr create --base Claude --head claude/results-2026-10-01 --fill`).
      It carries seven code changes (486 tests pass), the docs, 20
      promoted results and the sandbox's ledger shard, and passes
      `scripts/check_tracked_configs.py`. The code, by commit:
      `[[universe]]` row filters, `[pick_screen]`, selection by score
      and boolean flags as inputs; `blend` in vml-eval; **the
      calibration look-ahead fix**; `[sell] max_rank_pct`; per-buy
      outcomes in every backtest report; the universe applied in
      `vml-predict`; `weighting = "marketcap"`. The separate feature
      branches (`claude/universe-and-portfolio-screen`,
      `claude/eval-blend`, `claude/calibration-label-lag`,
      `claude/backtest-rank-sell`, `claude/backtest-buy-outcomes`,
      `claude/predict-universe`, `claude/backtest-marketcap-weighting`)
      are stacked and all contained in it; delete them after the merge.
- [x] **One holdout look** in cell C's 3y cell:
      `python scripts/run_final_eval.py experiments/forest_nonloser_dd30_3y.toml`.
      The forest is the only fitted part of the candidate. It says
      whether "not a loser" is still predicted on 2021+ snapshots
      (walk-forward: p@20 0.79, base 0.39); it does not test the
      blend. Read it beside the 2021-23 trading run (decision 26).
- [x] **Which liquidity floor to deploy with**: 100,000 a day (the
      template) or `dollar_volume_3m_rank >= 0.2` (era-neutral). The
      candidate is the same under either (12.24% and 12.15%). Carter's answer: era-neutral rank.
- [ ] **Deploy and paper-trade the candidate** beside its
      sell-discipline variant: carried to the section above, with
      what the run to 2026 showed.

Code worth building next (each on its own `claude/<topic>` branch):

- [x] **The floor and the sector cap in `vml-predict`**
      (2026-10-01: `--filter`, `--pick`, `--max-per-group` on
      `claude/predict-selection`.)
      (`--filter "dollar_volume_3m >= 100000"`, `--max-per-group 2`),
      so the deployed list is the backtest's selection and not a
      ranking to be filtered by hand.
- [ ] **A position cap** in the strategy (`Strategy` interface): stop
      adding to a holding above a share of the portfolio. The quality
      blend buys 94 stocks in sixteen years and two holdings are a
      third of it with the sell discipline; the candidate's largest
      is 8%.
- [x] **`sector` as a model input** (2026-10-01, second session:
      built on `claude/sector-feature` and run,
      `forest_sector_nonloser_3y`: the same picks, the same sectors,
      the same precision; decision 31.) (Carter, 2026-10-01: the cap is a
      bandage; the model might learn that a column means something
      different for REITs). One-hot of `sector` in
      `harness.dataset.feature_matrix`, a per-row recoding like the
      boolean flags, with the current-state caveat stated in every
      report. One sweep in cell C: ranks against ranks + sector, read
      on the screen and on sector shares.

Open questions, each with the experiment that would answer it (none
needs a backtest on 2005-2020):

- [ ] **Why the screen is about 0.02 a year harsher on blends with
      momentum than the backtests' own buys.** A third is the
      delisting convention; entry timing (the snapshot against the
      first trading days of the next quarter) is the untested rest.
- [ ] **A parameter search on the theory-led feature set** (fs2 of
      decision 18) before its verdict is final: it was run on a
      forest configuration tuned on the ranks. Low priority: 20 draws
      moved PR-AUC by 0.005 on the ranks.
- [ ] **Does the candidate's edge survive a longer wait between the
      snapshot and the buy?** The backtest buys one to six months
      after the snapshot; live trading on a fresh inference set buys
      sooner. Untested either way.

Upstream requests (new dataset version; nothing is derived here):

- [ ] **An outcome that treats a delisting as a portfolio does**:
      per horizon the delisting date and a return with the proceeds
      in the benchmark from the delisting to the horizon. Today an
      acquired stock is carried flat, which understates it in every
      `fwd_*` outcome and upside label (15% of the momentum blend's
      screen picks; docs/notes/2026-09-30-blends-and-calibration.md).
- [ ] **Within-sector ranks of the risk columns** (volatility,
      conservative score), for sector-neutral models.
- [ ] **Market-state features** (PLAN 5.6). Calibrated or not, score
      thresholds select years, not stocks: a confidence that means
      the same in 2008 and 2012 cannot come from a stock's own
      columns (docs/notes/2026-09-30-blends-and-calibration.md,
      2026-09-30-one-year-cell.md).

Settled in these sessions (details in docs/findings.md):

- [x] Training-time liquidity floor, theory-led feature sets, the
      1-year horizon, selection by calibrated confidence, a learned
      upside model, capitalization-weighted buys: none helps. A sell
      discipline helps the candidate and the quality blend, not
      forest + momentum. Trading 2021-23 was run with Carter's leave.

### Next, from the session of 2026-09-29/30 (Carter's notes, decision 13)

The candidate and its evidence: docs/findings.md, "State";
docs/notes/2026-09-29-decisions.md. Start a new session there.

- [x] **Carter:** one holdout look in cell C's 3y cell and the pull
      request for `claude/backtest-sector-cap`. (The sector cap
      reached `Claude` with PR #17; the holdout look is carried in
      the section above, with the same forest.)
- [x] **Sell discipline** for the candidate (2026-09-30: run as a
      rank criterion, `[sell] max_rank_pct = 0.2`, on the candidate
      and on the quality blend, decision 21; results in
      docs/notes/2026-09-30-backtests.md): one backtest with
      `strategy = "sell_below_criteria"`, criteria fixed before the
      run (the 14th backtest on 2005-2020). It works best with a
      calibrated model: buy on high confidence, sell or rebalance
      when it falls. Carter, 2026-09-30.
- [x] **Quick evaluation by confidence, not only by K.** (2026-09-30,
      `claude/universe-and-portfolio-screen`: with `score_thresholds`
      and `pick_outcomes` set, the report's "Selection by score"
      tables give, per year and pooled, the rows and stocks at or
      above each threshold, their precision and the mean and median
      of every outcome; years with no pick are shown.) The report's
      "High-confidence picks" table shows how many names clear a
      score and how precise they are; add the pick outcomes at those
      thresholds (mean excess CAGR, losers, big winners of every
      pick with `score >= p`, per year and pooled), so "mean excess
      CAGR at score > 0.7" can be read. Report **mean** beside median:
      an equal-weighted portfolio earns the mean, and the best picks
      may outweigh the worst. A median excess CAGR below zero is not
      a failure. Holding cash when nothing clears the bar is a valid
      strategy; the number of picks a year at a threshold is part of
      the result. Carter, 2026-09-30.
- [x] **Calibration** (2026-09-30: run on the candidate's forest
      after fixing a look-ahead in the calibrator; an honest
      calibrator for a 3-year label is four years behind and an
      absolute confidence bar would have held cash through the best
      entry years: docs/notes/2026-09-30-blends-and-calibration.md.
      A 1-year cell is the follow-up, decision 22.) Prequential,
      Phase 3 item above, before any
      rule that reads a score as confidence. Measured 2026-09-29 on
      the candidate's forest: top scores 0.81-0.85 for 2006-08 entries
      (precision 0.15-0.60) and 0.65-0.69 for 2011-13 (precision near
      1.0), so a fixed threshold picks the pre-crash years; a
      threshold relative to the year's scores, or calibrated
      probabilities, is what the confidence rule needs.
- [x] **Feature selection on theory, not only on the manifest
      groups.** (2026-09-30: five sets in cell C, on all rows and
      inside two liquidity floors, read on the portfolio screen. No
      set without the risk ranks matches the ranks: 0.013-0.034 a
      year less mean excess, more losers, and the same two sectors
      picked through operating-cash-flow stability. The floor at
      training changes nothing for the ranks forest.
      docs/notes/2026-09-30-features-and-floor.md. One seed, one
      forest configuration; a parameter search on the theory-led set
      is the untested rival.) Carter, 2026-09-30: the models lean on a few columns,
      the volatility and liquidity ranks among them; try excluding
      them, and prefer columns with a causal story in value investing
      (cash generation, balance-sheet strength, profitability,
      consistency). One August winner used
      `groups = ["ranks"]`, `exclude_families = ["ranks/technical",
      "ranks/trend"]`, `families = ["features/trend",
      "features/technical"]` (v1.1, 3y beat_spy;
      `forest_random_search_3y-2seeds2`). On v1.4 in cell A,
      fundamentals only scored 0.40-0.42 against 0.50 and its picks
      beat SPY 0.63 of the time before 2013 and 0.28 after
      (docs/notes/2026-09-29-pick-anatomy.md): the question is open
      in cell C and on pick outcomes and backtests, not on p@20.
- [x] **Training-time liquidity floor.** (2026-09-30, same branch:
      `[[universe]]` in configs and sweeps, `universe_scope = "test"`
      for the reference arm, a universe-qualified ledger cell, carried
      into bundles, deployment refits and backtest refits;
      docs/experiments.md "Universe".) Carter, 2026-09-30: drop
      rows below a dollar-volume threshold from training and test
      (the investability filter, applied to the dataset, not only to
      the backtest): less microcap noise, and the models need not
      learn the liquidity columns. A row filter on a manifest
      feature column, declared in the config, part of the hash and
      of the report; the label cell stays the same, so the trial
      count needs a "universe" qualifier. Not feature engineering
      (no new column); check data/manual.md before building it.
- [x] **Upstream request:** within-sector ranks of volatility and of
      the conservative score (carried in the section above).
- [x] **Sector cap in the pick-outcome screen** (`eval/picks.py`),
      so the screen sees what the backtest sees; and a sector table
      of the top-K picks in every run report. (2026-09-30, same
      branch: `[pick_screen]`, top K per test quarter with a cap per
      sector, and the picks' share by sector beside the test rows'.)
- [ ] Ranking metric for boosted-family searches: p@K over 2013-20
      of the worst seed, not PR-AUC (the two order LightGBM and
      XGBoost draws in opposite directions).
- [x] Whole shares at 100 a pick leave 55-108 of 192 months short of
      10 buys in the capped backtests; consider `fractional_shares`
      or a larger monthly deposit in the template, stated as a
      template change. (2026-09-30: the candidate re-run with
      fractional shares: 12.12% against 12.24% time-weighted,
      936,540 against 948,956. The template is unchanged.)
- [x] Why 134 delisting liquidations with momentum against 52
      without: takeover targets? Read the trades CSV of the promoted
      backtest. (2026-09-30: yes. Mean total return of the 134 is
      +79%, median +39%, 21% at a loss; 33 are within 10% of cost,
      bought a median three months before the delisting.
      docs/notes/2026-09-30-blends-and-calibration.md)

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
- [x] Derived labels: binary targets re-thresholded on the fly from the
      manifest's continuous outcomes — `label = "fwd_3y_cagr >= 0.1 &
      fwd_3y_max_drawdown_from_entry < 0.3"` — so new rungs never need
      a dataset rebuild. (`src/harness/derived_labels.py`, evaluated by
      `Dataset.frame`; row-wise only. A cross-sectional `cohort_pct`
      rank was built and removed: a cohort peer's label window can
      close up to a quarter after the row's own, eroding the embargo,
      and `beat_spy` / `excess_cagr` thresholds already give an
      era-neutral target. If ever wanted, it is an upstream label so
      the purge can see it.)
- [x] Recorded in data/versions.md: `dataset_v1.3` first ships
      `fwd_{H}_max_drawdown{,_from_entry}` (upstream decision 0017);
      drawdown-label configs set `min_dataset_version = "1.3"`.
- [ ] Once drawdown configs exist: consider asking upstream to drop the
      stored `label_{H}_cagr_ge_*` / `excess_ge_*` rungs (each is a
      one-line expression now — `fwd_{H}_cagr >= 0.1` reproduces
      `label_{H}_cagr_ge_10` exactly, tested). Existing configs name the
      stored columns, so this is a breaking version: migrate their
      labels to expressions first (the ledger cell name changes with it).
- [ ] Two-stage survival gating: stage-1 survival model (target e.g.
      `fwd_{H}_max_drawdown_from_entry < 0.3`, a derived label, now that
      upstream ships the continuous drawdowns), stage-2 return model
      ranks survivors only; evaluate the gate's precision cost outside
      crashes.
- [ ] Upstream requests to file: point-in-time market-state context
      features (drawdown-from-high, index vol) if regime-conditional
      models ever need them. (~~max-drawdown label~~ — shipped upstream
      as continuous `fwd_{H}_max_drawdown{,_from_entry}`, decision 0017;
      binaries are derived labels here.)

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
- [x] Run the regression-reframe spike against `dataset_v1.1`
      (`lgbm_cagr_quantile_3y`) and compare its summary against the
      classification sweeps on the same eval cells before going further.
      (Did not beat the classifiers: 0.44 pooled vs 0.47–0.55;
      docs/findings.md.)
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
- [x] Per-buy outcomes in every backtest report (2026-09-30,
      `claude/backtest-buy-outcomes`): each buy over the 1 and 3
      years after its trade date against the benchmark, by buy year
      and pooled, delisting proceeds riding the benchmark.
- [x] Rank-based sell criterion (2026-09-30,
      `claude/backtest-rank-sell`): `[sell] max_rank_pct`, a holding
      is kept while it is among that top share of the month's buy
      candidates; for `mean_rank` combinations and for models whose
      score level moves between years.
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
