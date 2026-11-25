# TODO

This file lists the concrete development tasks, roughly in order. The
architecture and the rationale are in [PLAN.md](PLAN.md). Check items
off as work proceeds, and add new ones as they appear.

## 1 — Phase 1: harness + baseline trees

### Dataset loading
- [x] The loader reads a versioned dataset directory (`src/harness/dataset.py`).
      It reads `manifest.json` and exposes the column groups: `key_meta`,
      `features`, `ranks`, `sector_ranks`, `labels` and `sample_weights`.
      Column selection is manifest-driven and never matches column names
      by pattern.
- [x] The loader validates on load. It compares the manifest row counts
      with the parquet, checks that the required files are present, and
      checks that the requested horizon exists in `horizons_years`.
- [x] Split application takes a scheme, a fold and a horizon, joins
      `splits.parquet` and returns train and test frames. The code
      enforces two rules. Training rows are `role='train'` rows only.
      Test rows come only from the tags, which already restrict them to
      median-kind, label-observable rows, and the code re-verifies this
      on apply.
- [x] The guardrails are errors rather than conventions. The loader refuses the
      `holdout` scheme outside the dedicated final-eval script. It
      refuses the diagnostic schemes `entity_holdout` and `random_kfold`
      outside the registered-experiment runner. It refuses to fit without
      the horizon's `sample_weight_{H}y`. The mechanism is `SplitAccess`
      in `src/harness/dataset.py`, and the ordinary runner only ever
      grants STANDARD access. The final-eval and registered-diagnostic
      entry points themselves are Phase 2 work.

### Experiment harness
- [x] The config schema is one TOML file per experiment in
      `experiments/` (`src/harness/config.py`). A config names the
      dataset version, the scheme, the folds, the horizon and the label
      column. It also names a feature-set selector by manifest group,
      the model and its parameters, and the seed.
- [x] The runner executes a config and logs it to an append-only
      results store, `experiments/results.csv`. The row carries the
      dataset version, the config hash, the git SHA, the seed and the
      metrics. The runner logs abandoned and failed runs too. The code is in
      `src/harness/runner.py` and `src/harness/results.py`, and the CLI
      is `vml-run`.
- [x] Every report cites `split_folds.parquet` with the fold boundaries
      and counts (`src/harness/report.py`). It also cites the effective
      sample size, the sum of `sample_weight_{H}y`, cross-checked
      against `manifest.json["effective_rows"]`.
- [x] Training and evaluation are separate steps. The runner saves the fitted
      per-fold models as a bundle (`src/harness/model_store.py`),
      git-ignored under `experiments/models/`. `vml-eval` re-scores a
      saved bundle under an eval config without refitting
      (`src/harness/evaluate.py`). An eval config may change the top-K
      and the score thresholds only. Everything else stays pinned by the
      bundle. The tool logs each evaluation to the results store under its
      own config hash.

### Baselines (before any tree is trained)
- [x] A majority-class baseline exists per horizon and threshold cell.
      `scripts/run_baselines.py` runs the full grid, and exemplar
      configs are in `experiments/`. Real reports need a real
      `dataset_v1.0` locally. I verified the script end to end on the
      test fixture.
- [x] Single-factor rank baselines take the top K by
      `book_to_market_rank` and by `earnings_yield_rank`
      (`src/models/baselines.py`).
- [x] The random-ranking baseline is seeded.

### Models
- [x] A single scikit-learn decision tree, depth-limited, is fitted with
      `sample_weight_{H}y` (`src/models/tree.py`). Class weighting is
      available where a cell is heavily imbalanced. `max_depth` is
      mandatory. NaNs are handled natively, so there is no imputation.
      Exemplar configs are in `experiments/tree_*.toml`. Real reports
      need a real `dataset_v1.0` locally. I verified the path end to
      end on the test fixture.
- [x] Rule extraction writes human-readable rules per trained tree to
      `reports/` and checks them in (`src/explain/rules.py`). The runner
      writes `reports/<experiment>_rules.md` with one section per fold,
      and every condition states its NaN routing.
- [x] The runner renders the tree diagram with matplotlib into the same report.
      The file is `reports/<experiment>_tree.png`, linked from the
      report. It shows the last fold's tree, which has the widest
      training window.

### Tests
- [x] Unit tests cover split application against a hand-built miniature
      splits.parquet (`tests/test_split_application.py`). They cover the
      roles, the rule that absence means out of fold, and median-kind
      test rows. `tests/conftest.py` builds the fixture.
- [x] A test checks that the guardrails raise on holdout access, on the
      diagnostic schemes and on a missing sample weight
      (`tests/test_guardrails.py`).

## 2 — Phase 2: evaluation done right

- [x] The metrics module provides precision@K, recall@K, PR-AUC, Brier
      and the calibration curve (`src/eval/metrics.py`). ROC-AUC may be
      logged and is never the headline. `calibration_table` is in the
      same module. `src/eval/plots.py` draws the reliability-curve PNG,
      embedded in every probabilistic report.
- [x] `render_pr_curve` and `render_roc_curve` in `src/eval/plots.py`
      graph the PR-AUC and ROC-AUC curves. Both curves pool the folds
      and use the weights. The PR curve has the base-rate no-skill line
      as its reference and the ROC curve has the chance diagonal. The
      report draws them for every model, not only the probabilistic
      ones, in a new "Discrimination curves" section.
- [x] Re-evaluation of a saved model does not redraw the score-only
      figures, which are calibration, PR and ROC. The scores are
      unchanged, so the values are identical to the training run's.
      `finalize_run(render_score_figures=)` controls this. `vml-eval`
      passes False, and the eval report points back to the training
      run's figures.
- [x] Era slicing reports every metric per test year, and no report
      presents pooled numbers alone (`src/eval/era.py`). The slices
      follow the year of `snapshot_date`, and the pooled row carries a
      clear "context only" mark.
- [x] The crash-era report breaks out 2000–02, 2008–09, 2020 and 2022
      separately, with uncertainty, as PLAN §4 Phase 2 asks.
      `crash_era_table` gives a Wilson 95% CI on precision@K. The table
      flags the CI as optimistic because same-year picks are correlated.
      Reports state explicitly when no crash era falls in the test
      years.
- [x] The walk-forward driver loops over the upstream `walkforward`
      folds, retrains per fold and aggregates the era table.
      `src/harness/runner.py` collects the per-row test predictions
      across folds and aggregates them.
- [x] Every report includes a baseline-comparison table and states the
      number of configurations tried
      (`ResultsStore.model_comparison`). A report with no recorded
      baselines for the cell says so and is not reportable.
- [x] The final-eval script for the sealed `holdout` fold takes one look
      per cell and logs the result whether good or bad
      (`scripts/run_final_eval.py`). Nothing else may read holdout tags.
      It is the only FINAL_EVAL entry point. `reports/final_evals.csv`
      records each completed eval per cell, and repeating one needs a
      disclosed reason.

### Registered diagnostics (from data/manual.md §7 — diagnostic only)
- [ ] Build the leakage-gap experiment: run an identical model under
      `random_kfold`, `entity_holdout` and purged `walkforward`, and
      report the score gaps.
- [x] The era-identifiability probe predicts the calendar year from
      features alone, on raw and on rank sets. The code is
      `src/diagnostics/era_probe.py`, `era_metrics.py` and
      `probe_models.py`. The probe models are a weighted multiclass tree,
      forest, LightGBM and XGBoost.
      `scripts/run_diagnostic.py era-probe <config>` is the only place
      that grants `REGISTERED_DIAGNOSTIC` access. The target is the year
      of `snapshot_date` under `entity_holdout`. That scheme is
      entity-disjoint, so firm memorisation cannot help. `random_kfold`
      is allowed as the leaky upper bound. Reports go to
      `reports/diagnostics/`. Each report has the headline against the
      uniform, majority-year and train-prior baselines. It also has a
      per-year slice, a post-burn-in slice, a confusion heatmap and the
      importances. Its tree rules name which thresholds date a row.
      Exemplar configs
      are `experiments/diagnostics/era_probe_{raw,rank,raw_tree}_3y.toml`.
      I wrote the raw arm's non-numeric exclusion list from
      data/features.md, and the first real run must confirm it.
      **The findings are in `reports/promoted/era_probe_rank_fingerprints/`.**
      On `dataset_v1.0` the rank arm dated rows at 0.954 accuracy, where
      the majority-year baseline scored 0.09. The cause was that
      within-quarter percent ranks of integer composites and
      zero-inflated ratios are quarter-specific constants. Four rank
      columns alone scored 0.917, and their raw values scored 0.148. I
      reported this upstream, and `dataset_v1.2` un-ranked the
      composites. The v1.2 results were these:

      | arm on `dataset_v1.2` | accuracy |
      |---|---|
      | all ranks | 0.456 |
      | ranks minus technical and trend | 0.322 |

      The misses are on adjacent years. The residual is regime
      recognition, tier nullity in 1997–2004 and secular drift. That is
      point-in-time economics rather than a leak. The fingerprint never inflated the walk-forward or holdout
      results, because their test quarters are unseen. `entity_holdout` retains regime
      hindsight and stays diagnostic-only.
- [ ] Run the boundary check on the v1.2 zero-inflated rank columns.
      It is the second query in the upstream brief §8. Does the first non-zero rank
      still equal the cell's zero share? This is a judgement call about
      a weak market-state signal rather than a leak. Record the answer
      in the brief §10.
- [ ] Test the concern that `entity_holdout` learns the era rather than
      the stock, once the leakage-gap experiment exists. Run it on v1.2,
      because on v1.0 its gap would mostly be the fingerprint. The plan
      has two tests:
      - Compare global top-K precision with per-year top-K precision
        under `entity_holdout`. If pooled picks beat per-year picks, the
        model is timing eras rather than selecting stocks.
      - Measure the share of an entity-holdout model's score variance
        that year explains, as a one-way ANOVA R². This is a cheap
        add-on to the leakage-gap report.
- [ ] Run the restated-variant ablation. It needs a restated-dimension
      dataset variant from upstream, so coordinate before starting.

## Deployment (cross-phase: ship whatever the current phase selected)

- [x] Deployment training refits a selected config's model on **all**
      labeled rows and saves a single-model deployment bundle. The
      refit includes all snapshot kinds and delistings, and it does no
      split filtering. This follows data/manual.md §4 rule 7, and the refit
      never reads split tags. The runs go to the results store under
      scheme `deployment`, apart from walk-forward trial accounting. The
      code is `src/harness/deploy.py` and `DeploymentBundle` in
      `src/harness/model_store.py`, and the CLI is `vml-train-deploy`.
- [x] Inference on today's stocks scores a
      `data/datasets/inference_{date}/` dataset with a deployment bundle.
      The CLI is `vml-predict`. The inference dataset has feature
      columns and no labels. The full ranking goes to `predictions/*.csv`
      with a provenance sidecar `.meta.json`, and the top 50 are printed.
      A deployment fit has no walk-forward folds and no holdout, so its
      scores are rankings and never reported performance.
- [x] Multi-model inference: `vml-predict` accepts several deployment
      bundles and writes one combined CSV for side-by-side model
      comparison. The CSV has a `rank_<model>` and `score_<model>` pair
      per bundle, ordered by mean rank. Each model gets one logged
      inference run.
- [x] `vml-predict --trends` carries the long-horizon trend context
      columns verbatim from the inference data into the output CSV, in
      single and multi-bundle mode. The columns are `revenue_trend_20q`,
      `tangibles_trend_20q`, `ocf_trend_20q`, `div_years_paid_10y` and
      `div_cuts_10y`. A missing column is an error, and the sidecar
      records `extra_columns`.
- [x] Historical analogues answer "which stocks looked like this
      before". I built this on 2026-10-01 as `vml-analogues` on
      `claude/analogues` (decision 37). It takes the picks or named
      tickers and reads the blend as one. Forests match by shared
      leaves and rank factors by closeness on their column. docs/deployment.md documents it. I did not build two parts: boosted
      trees weighted by leaf value, and a per-model report.
      The original design follows. Pick one stock from an inference
      dataset and score it with several deployment bundles, such as the
      best 1y, 3y and 5y configs. For each model show the labeled
      historical rows that **land in the same leaves as the stock**, and
      what happened to them. This is explanation rather than
      evaluation, as PLAN §4 Phase 3 says under "Historical analogues".
      The sketch has these parts:
      - **The primary method is leaf co-membership.** Every model in the
        zoo except the baselines is trees. So "similar" can mean similar
        *as the model sees it*, which is the rows the model routes to
        the same leaves. This uses the model's own split thresholds and NULL
        routing. There is no distance metric to choose, no imputation
        and no feature scaling, and it needs no SHAP.
        - *Single tree*: the stock's leaf **is** a rule. Show the rule,
          reusing `src/explain/rules.py`, plus the training rows in that
          leaf. The reading is "stocks with P/B rank below X and so on,
          here they are". Then show how each one turned out. Build this
          first.
        - *Forest*: proximity is the share of trees in which a row shares
          the stock's leaf, from sklearn's `apply()`. Rank analogues by
          proximity.
        - *LightGBM and XGBoost*: leaf indices come from
          `predict(pred_leaf=True)`. Boosted trees fit residuals, so
          plain leaf-sharing counts are weaker. Weight each tree by the
          absolute leaf value on the stock's path, and report both
          weighted and unweighted proximity until one proves more
          readable.
        - *Why these leaves*: list the split features on the stock's
          decision paths, counted across trees for ensembles. That is a
          cheap "what drove it" without SHAP. When the SHAP and
          reason-code items land, show their signed contributions
          alongside.
        - *Scale*: a rows-by-trees leaf matrix gets big, at about 1M rows
          by 500 trees. Stream `apply` over row chunks and accumulate
          only the match counts against the query stocks. Never
          materialize the full matrix.
      - **The fallback is feature-space nearest neighbors**, only for
        models without leaves, which are the baselines and a future
        logistic. Use the model's top-k features weighted by absolute
        contribution, in `_rank` or `_secrank` form so that eras
        compare. Raw levels drift, and inference ranks are pooled over
        one cross-section, so note that. A NULL matches a NULL and costs
        a fixed penalty against a value. There is no imputation.
      - **The candidate pool** is the labeled rows the bundle was trained
        on, from the same dataset version, over all eras, delisted rows
        included. A delisted analogue is exactly the history this is
        for. Leaf statistics use the rows as the model saw them, all
        kinds, weighted by `sample_weight_{H}y`. The displayed list keeps
        one row per `permaticker`, the highest proximity with the median
        kind preferred, so one stock's overlapping quarters cannot fill
        it. Show the era mix of the analogues. Exclude the query stock's
        own history by default, with a flag to include it.
      - **The output per model** starts with the score and rank in
        today's cross-section. Then comes the leaf rule for a single
        tree, or the top path features for an ensemble. Then come N
        analogues. Each analogue
        shows `ticker` for display only, with matching on `permaticker`.
        It also shows `snapshot_date`, the proximity, the path features'
        values next to the query's, and the realized `fwd_{H}_*`,
        `label_{H}_*` and `delisted_in_window_{H}` for every horizon.
        The summary gives the weighted positive rate and the sum of
        weights of the analogues. The CSV and markdown go under
        `predictions/` with a `.meta.json` sidecar. The sidecar names the
        bundles, the dataset and inference versions, the method, N and
        the git SHA. The CLI is `vml-analogues --ticker XYZ <bundles…>`, or
        `vml-predict --analogues XYZ`.
      - **The guardrails**: the deployment fit chose those leaves *from*
        these rows, so the leaf's outcome rate is in-sample by
        construction. For a single tree it is essentially the score
        itself. The output must say it is not an accuracy or probability
        estimate. An honest leaf hit-rate would need walk-forward fold
        models scored on their own test folds. That belongs on the
        evaluation side and is a separate item rather than part of this
        tool. Refuse if the inference and training manifests differ in
        version or feature set. Proximities and analogue outcome rates
        must never become model features (invariant 4). A kNN
        *classifier* is a separate walk-forward experiment, listed in
        PLAN §8 under "Other classifier families".
- [ ] Apply the investability filter from Phase 4 to deployment rankings
      before acting on them. Microcaps dominate the universe and there
      is no upstream liquidity floor.

## Workflow & tooling (cross-phase)

- [x] Artifact hygiene (`harness/promote.py`): generated `reports/`
      output is git-ignored. `vml-promote` copies a report and its
      artifacts into the tracked `reports/promoted/<name>/`, sweep
      summaries included. The sealed final-eval record stays tracked
      unconditionally. The results ledger `experiments/results.csv` is
      local.
- [x] The experiment catalog `vml-experiments` joins
      `experiments/*.toml` with the results ledger
      (`harness/catalog.py`). Its subcommands are `list`, `runs` and
      `show`. It answers three questions without grepping: have I run
      this, what is closest to edit from, and what did it score.
- [x] The catalog answers "did it beat the baseline, and what did I
      learn?". It shows the headline against the best baseline in the
      same cell with a signed lift. The listing is grouped by cell and
      ranked by lift inside it, with no cross-label sort. It shows the
      `note` column from the config and the `final_eval` column from the
      sealed ledger. A `★` marks a promoted config, restricted schemes
      are flagged, and portfolio configs are listed as their own kind.
- [x] Config hygiene: new `experiments/**/*.toml` files are git-ignored.
      A config earns tracking through `vml-promote <name> --note "..."`.
      That command snapshots the config into the promoted directory and
      writes the note into the config outside the hash. It then stages
      both with `git add -f` and regenerates the
      `reports/promoted/README.md` index.
- [x] Final eval needs no copied `*_holdout.toml`.
      `scripts/run_final_eval.py` takes the selected walk-forward config
      and switches the scheme in memory. `--phase` is gone. The seal is
      per cell, which is the label, the horizon and the holdout window
      from `split_folds.parquet`. The dataset version is not part of
      the cell, because v1.1 to v1.4 re-used the same rows. A further
      look needs `--reopen "reason"` and is then counted in the report,
      the ledger and the catalog as `✓ look k/N`. Old `phase` ledgers
      migrate in place and their rows count as looks.
- [x] The cross-sweep digest `vml-experiments sweeps` flattens every
      sweep summary CSV into one per-cell markdown. It lists the top
      runs across sweeps with lift and "what wins" per feature set,
      model and swept parameter, with continuous axes quartile-binned.
      I also fixed `runs` crashing on ledger rows without a horizon,
      which backtest and deployment rows are.
- [ ] Backfill notes on the tracked sample configs, saying what each one
      taught, so that the catalog's `note` column is populated from day
      one.
- [x] I split the lab notebook on 2026-09-28 into three places.
      `docs/logbook.md` holds one short entry per sweep, written with
      `vml-logbook`. `docs/findings.md` holds the current state, under
      about 150 lines. `docs/notes/` holds the detail.
- [x] I set up unattended runs on 2026-09-28 (docs/agents.md). The
      pieces are the run queue in `vml-queue` and
      `experiments/queue.toml`, `vml-sweep --resume` from per-run result
      records, and the ledger shards under `experiments/ledger/` with
      `VML_RESULTS` and `VML_LEDGER_READ`. Checkpoints go on `claude/`
      branches, and `scripts/check_tracked_configs.py` runs with the
      `pr-hygiene` workflow for pull requests.
- [x] Forest runs needed about 18 GB. The fitted fold models kept their
      training frame alive through the stored sample weights. The
      runner now copies the weights and targets (2026-09-28).
- [ ] Carter sets up the machine user and token, the branch rulesets and
      the sandbox resources, as docs/agents.md describes under "Setting
      up".
- [ ] Run the first unattended session end to end in a sandbox: queue,
      stub, checkpoint, and push from the machine account.
- [ ] Decide what to do with the unpromoted configs the branch carries.
      `python scripts/check_tracked_configs.py` lists 11 of them. The options
      are to promote them, name them in `experiments/KEEP`, or untrack
      them with `--fix`.
- [ ] `vml-experiments sweeps` ranks rows on different metrics in one
      table, where the metrics are p@10, p@20 and p@50. Rank within one
      metric, or group by it.
- [x] A guard stops a sweep TOML from being edited after it has run.
      `vml-sweep` copies the sweep file into `reports/sweeps/<name>/`
      and refuses to run when that directory holds the copy of a
      different sweep identity. Every run also writes
      `<run>_config.json` beside its report, with the full config and
      the resolved feature columns. `vml-run` copies its TOML there,
      and `vml-promote` carries the as-run copy as
      `config_as_run.toml`. Sweep files now accept `note`, so promoted
      sweep configs load again.
- [ ] `lgbm_candidate_sets_3y.toml` is pinned to dataset_v1.0 and never
      ran. Re-pin it to v1.4 or drop it.
- [x] Upstream doc sync: `scripts/sync_data_docs.py` copies the dataset
      docs from the local `radarash-dataset` checkout and records the
      upstream commit and file hashes in `data/upstream.json`. Its
      `--check` flag detects drift. `data/versions.md` is maintained
      here and maps dataset versions to features. Configs declare
      `min_dataset_version`, and the harness enforces it against the
      loaded manifest.
- [x] I overhauled the report. The era table now leads, with crash years tagged
      inline and a pooled row that picks per year. A global top-K over
      pooled per-fold scores was wrong, because it returned the hottest
      fold's picks. A new high-confidence-picks profile shows top-N per
      year tiers and `score >= p` counts, so no pre-chosen threshold is
      needed. I added `conf_at_K`, the mean score of the picks, and
      `base_rate_brier`, the no-skill Brier reference. The
      fold definition, the effective sample size and the crash-era CI
      table moved to a provenance appendix. Markdown tables are
      width-padded. PR and ROC curves are opt-in with `vml-run
      --curves`, and the calibration plot is always drawn.
- [x] Memory-bounded data access fixed the real cause of the vml-sweep
      OOM at about 29 GB RSS. `apply_split(columns=...)` merges a column
      projection instead of the full-width frame, because string
      metadata columns dominated the old copies. The
      label-observability column is always force-included, so
      validation cannot be projected away. Split tags load
      parquet-filtered per scheme and horizon instead of the whole tag
      table. Manifest validation reads parquet metadata instead of
      materializing the frame, and deployment refits fit on a
      projection. The runner and eval pass exactly the columns a run
      touches, while `dataset.data` stays full-width for the backtest
      cross-section. vml-sweep prints the peak RSS per run, so a
      regression is visible before the OOM killer finds it.
- [ ] `vml-experiments list` shows eval configs
      (`experiments/eval_*.toml`) and `experiments/queue.toml` as broken
      experiment configs that "lack required fields". Recognize them as
      their own kinds.
- [ ] Add two conveniences to `vml-experiments`: a `--cell` filter on
      horizon and label, and a `similar <config>` subcommand that ranks
      configs by shared cell, model and features.
- [ ] Wire `scripts/sync_data_docs.py --check` into the test session or
      a pre-commit hook on machines that have the upstream checkout.

## 3 — Phase 3: better models, kept interpretable

### Models & precision-first tuning
- [x] The LightGBM wrapper handles NaN natively, passes the weights
      through and has no early stopping (`src/models/gbm.py`). A local
      validation split would violate invariant 1, so the boosting rounds
      are tuned across walk-forward folds instead. The exemplar sweep is
      `experiments/sweeps/lgbm_precision_grid_3y.toml`.
- [x] The random-forest wrapper is scikit-learn's forest, NaN-native,
      with mandatory weights (`src/models/forest.py`). The exemplar
      config is `experiments/forest_3y_beat_spy.toml`.
- [x] The Phase-1 tree exposes its full hyperparameter surface. The
      parameters are `min_samples_leaf`, `min_samples_split`,
      `max_leaf_nodes`, `max_features`, `min_impurity_decrease`,
      `ccp_alpha` and `splitter`. `max_depth` remains a mandatory
      parameter.
- [x] Precision-over-recall knobs follow PLAN §2. Every classifier takes
      a numeric `class_weight`, where `w < 1` penalizes false positives
      and so gives purer positive calls. Any config may set
      `precision_targets` and then reports `recall_at_prec_*`,
      `thr_for_prec_*` and `n_at_prec_*`. These give the best recall
      subject to a precision floor, per fold, per era and pooled. The
      code is in `models/common.py` and `eval/metrics.recall_at_precision`.
- [x] Post-hoc calibration, isotonic or Platt, runs prequentially. A
      config or sweep sets `calibration = "isotonic"|"platt"`. Fold Y's
      raw scores are then calibrated on the pooled out-of-sample test
      predictions of the earlier folds **whose outcomes were known before
      year Y**. For an H-year label those are the folds f with f + H < Y.
      The harness constructs no local split, so invariant 1 holds.
      *I corrected this on 2026-09-30 on `claude/calibration-label-lag`.*
      Until then every fold below Y was used. That handed fold Y's
      calibrator outcomes from up to H years in its future
      (docs/notes/process-issues.md). No fit, ranking or uncalibrated
      metric was affected, and no calibrated run had been recorded before
      that day. Rows on one isotonic step now keep their raw order. They
      were tied, and a top-K over ties is a top-K in row order.
      Folds with less history than `calibration_min_rows`, by default
      1000 rows, stay raw and are flagged in the report. The report
      draws the calibrated and raw reliability curves side by side and
      states the across-refit score-stability assumption. Monotone maps
      leave the rankings unchanged. The gain is that `thr_for_prec_*`
      and the `score >= p` confidence tiers become real probabilities.
      `vml-eval` re-derives identical calibrated scores from a bundle of
      raw models, so nothing new is persisted. This applies to
      probabilistic classifiers only. The code is
      `harness/calibration.py`, and the exemplar is
      `experiments/lgbm_isotonic_3y_beat_spy.toml`.
- [ ] Build deployment-time calibration. A deployment refit has no
      out-of-sample history, so `vml-train-deploy` refuses calibrated
      configs today. The design is to fit the final calibrator on the
      *full* walk-forward OOS history of the same config. The DeploymentBundle then stores the calibrator, which needs a
      format bump. Then `vml-predict`
      scores read as probabilities. Until then deployment rankings are
      identical to the uncalibrated config's.
- [ ] Add SHAP, with global importance and per-prediction explanations,
      and compare it against the Phase-1 tree rules.
- [x] Native feature importances are a standard artifact
      (`harness/runner.py::_write_importances_file`). Every model that
      exposes `feature_importances()` gets a per-fold
      `reports/<run>_importances.csv`, with the cross-fold mean sorted,
      plus a top-10 table in the report's Interpretability section. The
      models are the tree and forest by impurity and LightGBM by gain,
      classifier and regressor. The artifact flags itself as a *triage
      list* for importance-guided feature subsets, which count as
      configurations tried, and not as an explanation.
- [ ] Add explainability for forests and LightGBM beyond impurity and
      gain. One part is permutation importance, weighted, on the
      training folds. The other is per-prediction reason codes, the top
      signed contributions, as optional columns in `vml-predict` output,
      so that a ranking is auditable stock by stock.
- [ ] Run the ablations: raw against rank against sector-rank features,
      with and without technicals, and with and without the
      classification columns under their current-state caveat. The sweep
      harness's `[[feature_sets]]` axis is the mechanism.
- [x] A feature blacklist exists: `exclude_feature_columns` in any
      config, and per `[[feature_sets]]` entry or at top level in sweeps.
      It means "the whole manifest group minus these", applied after any
      `feature_columns` whitelist. Excluding an absent column is an
      error, so a typo cannot silently keep a column in. This is needed
      because the `features` group contains non-numeric columns that no
      tree model can consume.
- [x] Three config conveniences exist. The default `name` is derived as
      `{model}_{features}_{label}_{content-hash}`, so a copied config
      with edited values cannot overwrite the original's artifacts.
      `horizon_years` is inferred from the label's `{H}y` token. Feature
      selection is hierarchical through a `[features]` table, where
      groups contain families and families contain columns. Family
      membership mirrors data/features.md in `src/harness/families.py`.
      Blacklisting a child whose parent was never selected is an error.
      Legacy top-level feature keys keep working and keep their config
      hashes. The code is in `src/harness/config.py`,
      `src/harness/families.py` and `Dataset.select_features`, and the
      example is `experiments/tree_depth3_families_example.toml`.
      Sweeps take the same `[features]` table, or a `[[features]]` array
      as the feature axis. They infer cell horizons from labels and
      derive a default `name` too, as
      `{model}_sweep_{features}_{labels}_{hash}`.
- [x] Boolean flags are model inputs since 2026-09-30, on the same
      branch. `harness.dataset.feature_matrix` hands the nullable boolean
      feature columns to models as 0/1 floats with NULL kept. This is
      route b below, for the flags only. Strings and dates stay excluded.
- [ ] Encode the categorical and non-numeric `features` columns so that
      they become usable as model features. These are `sector`,
      `industry`, `famaindustry`, `scalemarketcap`, the `Y`/`N`
      condition flags such as `negative_equity`, and the `fund_datekey`
      and `fund_reportperiod` date fields. Today they must be excluded
      with `exclude_feature_columns`. Decide the route first, because
      invariant 4 is in tension with doing it locally. There are two
      routes:
      - Route a, preferred: upstream encodes them, as one-hot, ordinal or
        a native categorical dtype, in a new dataset version.
      - Route b, acceptable if argued: a disclosed, deterministic per-row
        *recoding* in the harness, as one-hot or through sklearn's and
        LightGBM's native categorical support. That is representation
        rather than derivation. No cross-row statistics are allowed
        under any circumstances, because target or frequency encoding
        fitted on the data is leakage.
      Either way, mind the classification columns' current-state caveat
      in data/features.md. `sector` and `industry` are today's values
      rather than point-in-time, so a model using them sees a hint of
      the future.

### Sweep harness (ranges instead of one-config-at-a-time)
- [x] The sweep config lives in `experiments/sweeps/*.toml`
      (`src/harness/sweep.py`). It has `[[cells]]` for several
      horizon-and-label cells in one file, `[grid]` for the cartesian
      product of model parameters, and optional `[[feature_sets]]` and
      `seeds`. `max_runs` caps the expansion, at 200 by default.
- [x] The `vml-sweep` CLI has a `--dry-run` flag that prints the
      expansion. Every expanded run goes through the standard runner and
      is logged to the results store, failures included, because they
      still count as trials. Runs get STANDARD split access only, and
      each writes one report under `reports/sweeps/<name>/`.
- [x] The ranked sweep summary is `_summary.md` plus a full-metrics
      `_summary.csv`. It ranks by the pooled `rank_metric`, by default
      recall at the first precision floor. It gives the per-cell all-time
      counts of configurations tried and an explicit selection-bias
      warning.
- [x] Random search runs alongside the grid. A `[random]` table holds
      distribution specs of the form `{low, high[, log][, int]}` or
      `{choices}`, plus `n_samples` and `search_seed`. Sampling is
      deterministic, a pure function of the sweep content, so
      `--dry-run` shows exactly what will run. The draws are crossed
      with the grid and every other axis. `max_runs` still caps the
      total, and every draw hits the trial ledger. Sampled values land
      in the summary's `sampled_params` column. The code is
      `harness/sweep.py`. Curated search spaces with range rationale are
      in `experiments/sweeps/lgbm_random_search_3y.toml` and
      `experiments/sweeps/forest_random_search_3y.toml`. Both have a
      `[[features]]` axis, so the feature set is searched rather than
      hand-picked.
- [x] I ran the real searches against `dataset_v1.1`, which were
      `lgbm_random_search_3y`, `forest_random_search_3y` and the grid
      exemplars. I committed the summaries and picked Phase-3 candidates
      for the sealed holdout. In August and September 2026 I ran forest,
      xgb, lgbm and quantile-regressor searches on 3y beat_spy. The conclusions are in docs/findings.md, and I promoted the
      summaries.
- [x] I ran the v1.4 baselines with `scripts/run_baselines.py
      dataset_v1.4` on 2026-09-26. That was 80 runs over the 20
      stored-label cells. The script does not cover derived-label cells.
- [x] I ran the carry-forward sweeps `forest_candidate_sets_3y` and
      `xgb_candidate_sets_3y` on v1.4 on 2026-09-27. The base rate was
      0.28. The p@20 results were these:

      | family on v1.4 | pooled | 2013–19 |
      |---|---|---|
      | forests | 0.42 | 0.22 |
      | xgb | 0.37 | 0.17 |

      These are lower than the same configurations on v1.1, on a column
      set that differs by 13 added and 4 dropped columns. The cause is
      open, so the v1.1 findings are unconfirmed rather than refuted.
      There is no 3y beat_spy finalist, and the 3y holdout stays
      unopened. The detail is in docs/findings.md.
- [x] I ran `forest_v11_code_control_3y`, 4 runs that need
      `dataset_v1.1`, on 2026-09-28. All 64 fold rows equal the August
      ledger rows, so the code is not the cause.
- [x] I ran `forest_feature_ablation_3y` on 2026-09-28. It was 8 runs on
      one seed, not the 24 in its header. Arm fs0, the v1.1 column set,
      scored p@20 0.44 against the predicted 0.58. So the 13 added
      columns are not the cause, though removing them raises PR-AUC by
      0.01-0.02. The arms cannot be ranked. The detail is in
      docs/findings.md.
- [x] Do the 120 columns shared by the v1.1 and v1.4 feature sets hold
      identical values? On 2026-09-28 the answer was no. 17 changed at
      v1.2 under upstream decision 0016, and 103 are equal. I updated
      `data/versions.md`.
- [x] I ran `forest_v11_column_control_3y` and
      `forest_v14_unchanged_columns_3y` on 2026-09-28. The v1.1 edge is
      in the v1.1 values of the 17 columns that decision 0016 re-mapped:

      | arm | p@20 |
      |---|---|
      | with the 17 columns' v1.1 values | 0.57-0.58 |
      | without them | 0.43-0.47 |

      The four dropped columns change nothing, and v1.1 and v1.4 give
      identical fold rows on the other 103 columns.
- [ ] Is it a quarter identifier or stock information? Compute per-quarter
      picks on v1.1 for the runs with and without the 17 columns. The
      measure is either p@K within each test quarter or the spread of
      the picks over a year's quarters. This needs per-quarter metrics or saved
      predictions. Then send a note upstream, because decision 0016
      expects walk-forward not to be inflated by the keys. This is low
      priority, because it changes nothing about what to run on v1.4.
- [x] I ran `baseline_lowvol_rank_3y` on 2026-09-28. The best single
      factor is `conservative_score_rank`. Its p@20 against the model
      families was this:

      | cell | `conservative_score_rank` | forests | LightGBM |
      |---|---|---|---|
      | from-entry cell | 0.39 | 0.50 | 0.39-0.40 |
      | whole-path cell | 0.34 | 0.37-0.39 | |
      | 3y beat_spy | 0.49 | level with the best forest arm on v1.4 | |

- [x] Carter chose the primary cell on 2026-09-28: cagr >= 10% and
      drawdown from entry < 20%. The choice of label stays part of the
      experiments.
- [x] I ran `forest_feature_sets_dd_entry_3y` on 2026-09-29. No arm beats
      the 112 ranks. Most of the signal is in `vol_12m_rank`,
      `vol_36m_rank` and `conservative_score_rank`. The note is
      docs/notes/2026-09-29-feature-sets-dd-entry.md.
- [x] The label screen reports the outcomes of a run's top-K picks,
      report-only, through `pick_outcomes` in `src/eval/picks.py`, built
      on 2026-09-28 and documented in docs/experiments.md. For a binary outcome it gives the share of picks with the outcome
      true, and for a continuous one the mean and median. It gives the
      same over all test rows beside them, plus the distinct stocks among
      the picks. It appears in run reports, in the ledger's
      per-fold metrics and in sweep summaries, and an eval config can set
      it for saved bundles.
- [x] I ran `baseline_pick_outcomes_3y` on 2026-09-29. The bar is that
      0.49 of the picks beat SPY, with a median excess CAGR of about
      zero.
      The note is docs/notes/2026-09-29-label-rungs-dd-entry.md.
- [x] Decision 6 of docs/notes/2026-09-29-decisions.md fixed the
      label-comparison backtest template on 2026-09-29. It buys the top
      10 a month at equal weights, buy and hold, at 35 bps a side, inside
      `dollar_volume_3m >= 100000`. The buys run 2005-2020 and are valued
      at the end of 2023. Decision 7 then added a cap of 2 per sector.
      The configs are `experiments/portfolios/bt_*.toml`.
- [x] I ran `forest_label_rungs_dd_entry_3y` on 2026-09-29. The
      thresholds move p@20 and PR-AUC but not what the picks go on to do.
      No rung passes the screen on every seed.
- [x] I ran a parameter search per family on 2026-09-30, in the
      candidate's cell C instead of the primary cell, with 20 draws
      each. No draw of any family exceeds the reference forest's
      fold-mean PR-AUC of 0.585. The boosted families pick worse at the
      same PR-AUC. The note is docs/notes/2026-09-29-searches-nonloser.md.
- [x] An investability filter runs before any top-K number is acted on.
      Since 2026-09-29 every backtest applies `dollar_volume_3m >=
      100000`. The screen still does not, which the next section covers.
- [x] Reports give the number of distinct `permaticker`s among the top-K
      picks per test year, as `n_stocks_at_K`, part of `pick_outcomes`
      since 2026-09-28. Runs without `pick_outcomes` do not carry it.
- [ ] Add a crash-window line to the era table for path labels. The
      entry years whose window holds a market crash are 2005-08 and 2019
      at 3y. Those are the years where the compounder models fall to the
      base rate.
- [ ] Add a config hash that leaves the sweep name out, and record it
      in the ledger. Then a re-run under another sweep name can be
      matched to the original by hash. The `identity_hash` exists for
      single configs.
- [ ] Add `vml-experiments verify`. It expands each config under
      `experiments/` and compares its config hashes with the ledger's.
      It then reports any config that no longer matches its own runs.
      Today those are `lgbm_random_search_3y`, `lgbm_cagr_quantile_3y`
      and `forest_random_search_3y`.
- [ ] Add `vml-experiments columns <run> <run>` to diff the resolved
      feature columns of two runs from their `*_config.json` records.
- [x] I multi-seeded the drawdown-compounder labels on v1.4 on
      2026-09-28. The labels are `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown
      < 0.3` and the same with `fwd_3y_max_drawdown_from_entry < 0.2`.
      The sweeps were three baseline sweeps,
      `lgbm_drawdown_compounder_seeds_3y` and
      `forest_drawdown_compounder_seeds_3y`, 48 runs in all. The result
      held over seeds and in 2013-20, and the forests are ahead of
      LightGBM:

      | label | forest p@20 | base rate |
      |---|---|---|
      | whole-path drawdown < 0.3 | 0.50 | 0.21 |
      | drawdown from entry < 0.2 | 0.37-0.39 | 0.11 |

      There is no lift for the entry years 2005-08 and 2019. The detail
      is in docs/findings.md.
- [ ] Add baselines for derived-label cells. `scripts/run_baselines.py`
      takes stored labels only, so each derived cell needs hand-written
      baseline sweeps today. Give the script a `--label "<expression>"`
      option.
- [ ] Run the random-ranking baseline over several seeds in the standard
      grid. One seed scored p@20 0.39 on 3y beat_spy against a 0.35 base
      rate, and the catalog measures lift against it.
- [x] Ledger fix: an interrupted run's fold rows were logged `completed`.
      Fold rows are now held until every fold has finished, and a
      stopped run leaves one `failed` row. The code is `RunLog` in
      `src/harness/results.py`, used by the runner, `vml-eval` and the
      era probe.
- [ ] Ledger gap: a run whose process is killed outright, by OOM or
      `kill -9`, leaves no row, so the trial goes uncounted. Log a row
      when a run starts, once ledger readers can ignore it.
- [x] The `[[sets]]` axis takes whole parameter dictionaries as units,
      such as the top candidates of a wide search. It is crossed with
      cells, feature sets, `[grid]`, `[random]` and seeds. A parameter
      lives in exactly one of `[model]`, `[grid]`, `[random]` and
      `[[sets]]`. The summary carries `param_set` and `set_params`. The
      exemplar is `experiments/sweeps/lgbm_candidate_sets_3y.toml`.
- [x] Multi-seed sweeps report per candidate (`src/harness/seed_report.py`).
      Each candidate gets one seed-stability report with the mean,
      standard deviation, minimum, maximum and 95% t-interval across
      seeds, pooled and per test year. The summary
      `_summary_seeds.csv` is ranked by the mean with the spread beside
      it, and the per-seed run reports go under `seeds/`.
- [x] I ran a seed-stability pass on the sweep winner: a multi-seed
      `[[sets]]` sweep over the top candidates. A config whose ranking
      collapses across seeds is noise rather than signal. On v1.1 the
      xgb spread was at most 0.02 over three seeds. The forest top
      candidates were within noise of one another over two to four
      seeds. The v1.4 re-run is the item above.
- [x] LightGBM has a GPU opt-in: `device = "cuda"`, or the legacy OpenCL
      `"gpu"`, on `lightgbm` and `lightgbm_regressor`, passed through as
      LightGBM's `device_type`. It requires a CUDA build of lightgbm,
      because the PyPI wheel is CPU-only. The install command is in
      `models/gbm.py::LGBM_DEVICES`, and a CPU-only build asked for cuda
      fails with that command rather than an opaque error. GPU histogram
      arithmetic differs slightly from CPU, so `device` is a model
      param. CPU and GPU runs hash as distinct configs and are never
      mixed in the trial ledger. I ruled this out for the other
      families. The sklearn trees and forests are CPU-only. cuML's forest
      supports neither `sample_weight`, which the mandatory uniqueness
      weights need, nor native NaN routing. So it is incompatible with
      the contract rather than merely inconvenient.
- [x] The XGBoost family is `xgboost` and `xgboost_regressor` with the
      hist method (`src/models/xgb.py`). It is the GPU path that needs no
      custom build, because `device = "cuda"` works from the stock PyPI
      wheel. It follows the harness protocol throughout, with mandatory uniqueness
      weights, native NaN routing and no early stopping. A numeric
      `class_weight` maps to `scale_pos_weight` with the same semantics
      as every other classifier. "Balanced" computes the weight sum ratio
      of negatives to positives fold-internally. The regressor
      mirrors the reframe with `eval_label`, `winsorize` and the
      `quantile` objective through `quantile_alpha`. Gain importances
      feed the standard artifact, and prequential calibration applies.
      Two guardrails apply. `device` is a model param, so cuda and cpu
      runs hash as distinct configs. XGBoost silently falls back to CPU
      when no GPU is visible. So the wrapper reads the fitted booster's
      own config after every non-cpu fit, and it refuses if the actual
      device differs. A CPU fit can never be logged under a cuda hash. The
      exemplar is `experiments/sweeps/xgb_random_search_3y.toml`, with
      the same cell, axes and metrics as the LightGBM search, for a fair
      family-against-family read.
- [ ] Add successive-halving style budgeting if random searches get
      slow. Re-run the top decile of a cheap-budget search, one with low
      `n_estimators`, at full budget through a follow-up sweep file. No
      harness change is needed, only two sweep configs.

### Next, after 2026-11-24 (decisions 55-58)

The dataset of record is `dataset_v1.4.1` (upstream decision 0021).
Every run row now carries `dataset_sha256`. I reran the candidate's legs,
screens and backtests on it. The results are in
docs/notes/2026-11-24-v141-and-size-band.md and findings.md. I produced
the November 2026 list from the v1.4.1 deployment bundles. I added the
`writing` skill and the check `vml-writing` the same day, on
`claude/writing-check` (decision 59).

- [ ] **Carter merges `claude/writing-check`.** It includes
      `claude/results-2026-11-24`, which includes
      `claude/results-2026-11-23` (pull request 20) and
      `claude/plain-writing`. Pull request 20 can then be closed.
- [ ] **Carter decides on the November 2026 list.** It is in docs/paper-trading.md
      under "Checked end to end (2026-11-24)": RPRX, KO, EBAY, CHD,
      SAIC, V, HAS, NDSN, WAB and PSX. Carter decides what is bought.
- [ ] **Carter decides on the larger-half filter (decision 58).** Adding
      `log_marketcap_rank >= 0.5` to the candidate's investability
      filter earned more on all three seeds. The gap in TWR was 0.32
      to 0.75 points a year. Its mean was 0.59 against a candidate
      seed spread of 0.42. The drawdown was 1.5 to 1.9 points
      shallower. To 2026 the filter ends 6% behind SPY where the
      candidate ends 13% behind. Carter confirms or declines. If
      confirmed, the next steps are the backtest
      `bt_..._rankfloor_largehalf_sell20_to2026` and a second
      `--filter` in the runbook.
- [ ] Large caps (`log_marketcap_rank >= 0.8`) earned the same final
      value as the candidate. Four points fewer of its buys lost money,
      and its lead over same-size peers was 1.5 points larger. Both
      gaps are beyond two standard errors (decision 57). I did not
      carry it forward because the final value did not improve. It is
      worth a look if the goal is ever restated as fewer losers at the
      same return.
- [ ] The ledger holds seven failed runs from 2026-11-24, caused by one
      chain-script error, a copy that overwrote the `[model]` name. An earlier
      error, a wrong config path, failed four backtests before they
      reached the ledger. The seven count as trials in their cells
      under the ledger's rule, and this note says why the counts are
      higher.
- [ ] Re-read `year_balance` against plain ranks on the screen under
      decision 50. Both forests need refitting on v1.4.1. This is low
      priority.
- [ ] Upstream requests stand. They are market-state columns per
      snapshot date and the peer-relative label, listed under "Upstream
      request" in docs/notes/2026-11-23-calibration-plan.md. Upstream
      has done patch versions and the provenance block (decision 0021).

### Next, after the third round of 2026-11-23 (decisions 50-51)

Decision 50 says how results are judged. I read picks against
same-size peers, crash years included. I carry an arm forward on
paired per-year gains beyond noise. Beyond noise means about 2 se. It
also means ahead in 10 or more of the 16 years. Then come seeds, then a backtest. A bar set
beforehand is a prediction rather than a gate.

- [x] Trace why `bt_nonloser_mom_roc_top10_cap2_rankfloor`, config
      `6005c9c0a2869bc9`, gives different numbers at two git SHAs. Until
      then, compare backtests only at one git SHA. The answer is the
      dataset_v1.4 rebuild of 2026-11-23 (decision 54). The two runs
      were these:

      | git SHA | TWR | buys |
      |---|---|---|
      | `cfa451c` | 11.90% | 1,742 |
      | `f96037d` | 12.15% | 1,747 |

- [x] Test `label_3y_cagr_ge_0`, open under decision 51, if Carter
      agrees it fits the thesis. The plan was forest seeds 232 and 1776,
      paired in the mean-rank blend. If the gain held, a backtest beside
      the candidate at the same SHA would follow. The result is that it is an
      equivalent rather than a replacement (decision 53).
- [x] Rerun the candidate's to-2026 backtests, `*_rankfloor_to2026` and
      `*_rankfloor_sell20_to2026`, on the rebuilt v1.4. Then the
      findings' table and new runs share a dataset build (decision 54).
      I did this on `dataset_v1.4.1` instead (decision 55).
- [x] Ask upstream for a content hash of dataset.parquet in the
      manifest, or a new version number for any rebuild (decision 54).
      Upstream did both on 2026-11-24 (upstream decision 0021), and
      downstream logs `dataset_sha256` (decision 55).
- [ ] Find why worst rank selects better and earns less. Decision 51's
      hypotheses are smaller stocks, holding past 3 years, or the 2008
      fall. This is low priority.
- [x] Re-read the earlier arms that a fixed bar closed under decision
      50's rule, which is paired, with noise. The candidates were
      decision 41's top-5 and score weights, and `year_balance` against
      plain ranks on the screen. I re-read the top 5 and the score
      weights, and decision 42 stands (decision 56). `year_balance` is
      left, see the 2026-11-24 section.

### Next, after the second round of 2026-11-23 (decisions 43-49)

I followed Carter's three directions (decision 43) to the end of what
the data on disk can answer. I carried nothing forward, and the
candidate is unchanged. The results are in
docs/notes/2026-11-23-downside-gates-calibration.md and
docs/notes/2026-11-23-calibration-plan.md.

- [ ] **Carter forwards the upstream request** in the calibration plan,
      under "Upstream request". It asks for market-state columns per
      snapshot date and the peer-relative label. Then rerun calibration
      step 3 with the market-state columns under decision 44's rule.
- [ ] **Carter merges `claude/results-2026-11-23`.** It now also carries
      `year_balance`, `mean_score` and `year_calib_*`, and `[[gate]]`.
- [ ] This item is open in case a hedge or short leg is ever built. The
      huber regressor's within-band selection among small stocks led
      same-size candidates by +6.5 to +6.8 points a year (decision 49).
- [ ] Add `[[gate]]` to `vml-backtest`, where only `vml-eval` has it, if
      a gated selection ever passes a screen.
- [ ] Find why two forests with the same parameters screen differently.
      They are this run's plain-ranks forest and the candidate's forest
      bundle. Expand both
      configs and compare hashes and fields before using either as a
      bar again. The screen numbers were these:

      | forest | screen |
      |---|---|
      | `calib_levels_nonloser_plain_3y` fs0 | +0.036 / +0.024 |
      | the candidate forest bundle | +0.030 / +0.027 |

### Earlier: after the first round of 2026-11-23 (decisions 38-42)

The session of 2026-11-23 ran the queue, which held the over-priced
stocks and the continuous growth models. It built `worst_rank`, blended
the forest with the huber regressor, and measured the forest's
confidence inside its top 200, with two backtests from it. I carried nothing
forward, and the candidate is unchanged. The results are in
docs/notes/2026-11-23-crash-growth-worst-rank.md. What is left belongs
to Carter or to upstream:

- [ ] **Carter merges `claude/results-2026-11-23`.** It carries the
      `worst_rank` code with tests, decisions 38-42, the note, the
      logbook, the findings and the ledger shard.
- [ ] **Upstream builds the peer-relative label**, "beat stocks of the
      same size band over 3 years". It is the one target whose base rate
      does not move with the market. It reopens calibration and
      confidence sizing, which decision 42 closed for the forest. It is
      the most promising new cell, because the screen already shows that
      the forest's lead is a lead over same-size peers.
- [ ] **Carter sets the three rules for other model families**, listed
      below and unchanged. Then come a logistic regression and an MLP on
      the ranks.
- [ ] Optional and cheap: run seeds 232 and 1776 of the huber regressors
      on CAGR and on excess CAGR. The test is whether their large
      difference is chance (decision 39's open question). This is not a
      candidate,
      because they fail on losers whatever the answer.
- [ ] Upstream, after the label, adds market-state features, which is
      research plan item 8. The count of a crash model's confident calls
      is not one (decision 39).

### Earlier: from Carter's direction of 2026-10-01 (decision 36)

The working assumption is that 2021-26 is a bubble that a value
strategy trails through. The candidate goes to paper trading as it is,
and the search continues, wider. Each item below is laid out in
docs/notes/2026-10-01-research-plan.md. That note says what the record
already says, what each item needs and how it is read. I judge new arms
on walk-forward 2005-2020 against same-size peers, and 2021-26 is
context.

These items are Carter's:

- [ ] **Open and merge the pull request** from
      `claude/results-2026-10-01b`. This is the item in the section
      below. The branch now also carries docs/paper-trading.md, the
      research plan, the three queued sweeps and the Piotroski result.
- [ ] **Set up paper trading on the host**, following
      docs/paper-trading.md. It takes three `vml-train-deploy` commands,
      because the bundles built in the sandbox stay in the sandbox. It
      also takes an `inference_<date>` dataset from upstream each month,
      and one `vml-predict` command. There are two paper portfolios: buy and
      hold, and the rank sell discipline. I checked the path end to end
      on 2026-10-01, and it gave 9 of the backtest's 10 picks for August
      2026.
- [ ] **Accept or change two rules** before a session on other model
      families, which is research plan item 7. The first rule is
      fold-internal median imputation with an is-missing indicator for
      models that cannot take NULLs. The second concerns a learned
      transform, such as clusters or embeddings. It is allowed when it is
      fitted on the fold's training rows and saved in the fold's bundle,
      and never otherwise. Also decide whether PyTorch may join the
      dependencies. Scikit-learn's MLP needs nothing new.

These items are ready to run, which means "work the queue" with
`vml-queue status`:

- [x] `baseline_factors_crash_dd50` and `forest_crash_dd50` are the
      over-priced-stock model: "fell 50% from entry" within one and
      three years inside the liquid half. I ran them on 2026-11-23
      and closed them (decision 39). I read them on precision at the top by
      year and on what the calls went on to do. They are also read on the
      market-state question: does the count of high-confidence calls rise
      before 2008 and 2020, or after?
- [x] `lgbm_regressor_growth_allrows_3y` holds the continuous models:
      LightGBM on 3y CAGR and excess CAGR, huber and three quantiles,
      read against same-size peers. I ran it on 2026-11-23, and carried no arm
      forward (decisions 39-40).

These items are small code changes followed by a sweep, each on its
own `claude/<topic>` branch:

- [x] **`combine = "worst_rank"`** in `vml-backtest` and in `vml-eval`'s
      `blend` ranks by the worse of the models' ranks. That means "in
      every model's top N" for any value of N at all. Then the
      candidate's three legs by worst rank were to be read against mean
      rank, on the screen with peers. I built it on 2026-11-23 on `claude/worst-rank`, and the
      screen fell short (decision 39).
- [ ] **`vml-predict --holdings <file>`** marks which held stocks the
      rank sell rule would sell this month. Then portfolio B's sells do
      not have to be read off the CSV by hand.
- [x] ~~**A cash rule as a `Strategy`**~~ was conditional on
      `forest_crash_dd50` showing the count of high-confidence calls
      leading the market. I did not build it, because the count did not
      lead (decision 39).
- [ ] A position cap, carried from below, is low priority.

Sessions of their own, research plan items 6 and 7:

- [x] **Calibration and confidence-weighted sizing.** The plan was to
      start by measuring whether outcome rises with rank inside the
      forest's top 50 of a month at all. Then came the design of a
      target whose base rate does not move with the market, which is
      the peer-relative label, upstream. I did the first step on
      2026-11-23: the top 10 is purer, and the top 5 and score weights
      do not help. This is closed for the forest (decision 42).
- [ ] **Other model families** are a regularised logistic regression on
      the ranks, an MLP, and a fold-internal clustering as an input. They
      run on the continuous and peer-relative targets first.
- [x] ~~**A short leg**~~ was conditional on `forest_crash_dd50`
      reaching a precision that justifies it. Borrow costs, recalls and
      unbounded loss are not in the engine. It is closed (decision 39).

These items were done under decision 36 on 2026-10-01:

- [x] I refit the candidate's three models for deployment and ran the
      prediction path end to end. I wrote docs/paper-trading.md and
      promoted the two factor configs.
- [x] I ran the nine Piotroski signals against the composite F-score
      as `forest_piotroski_3y`. The entry is in docs/logbook.md.
- [x] Carter closed "Data before 1998", because Sharadar starts in
      1998.
- [x] `vml-analogues` gives the historical stocks today's picks
      resemble, and what they went on to do (decision 37). It is in
      docs/deployment.md and in docs/paper-trading.md step 5.

### Next, from the second session of 2026-10-01 (decisions 27-35)

Start with docs/findings.md, then docs/notes/2026-10-01-out-of-sample.md
and docs/notes/2026-10-01-large-caps.md. The summary is this. Traded to
the end of the price panel on 2026-08-21, the candidate ends 10% behind
SPY, and its sell-discipline variant ends level with it. The forest's
precision held on the holdout, and it kept avoiding losers:

| picks a year | precision on the holdout |
|---|---|
| 20 | 0.65 |
| 50 | 0.73 |
| base rate | 0.38 |

But in 2021-26 SPY beat equal-weighted stocks of every size. Against
stocks of their own size the candidate's picks were ahead by 5 to 6
points a year in 2005-2020, and by nothing after. Inside large caps no model
chooses better than return on capital alone. Nothing more is run on
2021-26, and the search on these columns is closed for now (decision 34).

These items are Carter's, in order:

- [ ] **Open and merge the pull request** from
      `claude/results-2026-10-01b` into `Claude` with
      `gh pr create --base Claude --head claude/results-2026-10-01b --fill`.
      It carries six code changes, the docs, the promoted results and
      the ledger shard. 510 tests pass, and it passes
      `scripts/check_tracked_configs.py`. The sixth code change is
      `claude/analogues`, which is `vml-analogues`. docs/agents.md is
      rewritten in it, with your leave, so read "Two ways of working".
      The branches are all contained in it, so delete them after the
      merge. The code, by branch:
      - `claude/predict-selection` adds `vml-predict --filter --pick
        --max-per-group`, the backtest's floor and sector cap on the
        ranking.
      - `claude/backtest-calendar-years` is **a fix**: the reports' yearly
        table ran December to December.
      - `claude/backtest-universe-outcomes` makes every backtest report
        set its buys beside all candidates and beside same-size peers.
      - `claude/sector-feature` adds `sector` as a model input.
      - `claude/screen-size-peers` adds `[pick_screen] peer_column`, the
        same-size reference on the sweep screen.
- [x] **Decide what the portfolio is for, and its yardstick.** Carter
      decided on 2026-10-01 (decision 36). The aim is to beat the market
      over the long term. 2021-26 is taken as a bubble and waited out. Against SPY the candidate is level over 21.6 years, with
      three quarters of the worst drawdown:

      | | CAGR a year |
      |---|---|
      | the candidate | 11.3% to 12.0% |
      | SPY | 10.9% |

      It was 37% ahead at the end of 2020 and is 10% behind now. Against
      stocks of its picks' own size it led until 2018 and has not since.
      If the aim is to beat SPY, the candidate is a starting point. The
      upside then has to come from somewhere these columns do not reach.
      If the aim is market-like return with fewer losers, it is a result.
      See findings, "What this says about the thesis".
- [x] **Paper-trade the fixed candidate, or not.** The answer was yes
      (decision 36), and the item is carried to the section above. Your
      reading of 2021-26 as a bubble the strategy sits out (decision 35)
      is a reason to. On 1999-2004 a stand-in for the candidate trailed
      in the last year of the run-up. It led by 9 points a year for the
      buys of 2000-02. That is one precedent, and a different kind of
      run-up. The mechanics are in docs/notes/2026-10-01-candidate.md
      under "Run it on today's stocks". Run `vml-train-deploy` on the
      three configs, then `vml-predict ... --filter "dollar_volume_3m_rank
      >= 0.2" --pick 10 --max-per-group 2`. It needs an
      `inference_<date>` dataset from upstream. Buy and hold runs beside
      the sell discipline, and both are judged on `vs_peers` as well as
      on SPY. No other blend is proposed, because choosing one now would
      be choosing it on 2021-26.
- [ ] **A baseline on the holdout rows of cell C**, if you want one. The
      look's report has none and says "No baseline runs recorded for
      this cell". So it is not known whether lowest volatility alone
      would have scored the forest's 0.65 there. It is a further read of
      the holdout rows with `--reopen`, and it is counted.

These are upstream requests for a new dataset version, and nothing is
derived here. The first three are new and come from decision 32:

- [ ] **An outcome and a label measured against same-size peers.** Per
      horizon, the outcome is `fwd_{H}y_cagr` minus the mean of the same
      quarter's stocks in the same band of market-capitalization rank.
      The label is its sign. This is the target that asks a model to choose
      well rather than to prefer large companies. It is a cross-row
      label, so it belongs upstream, beside the split machinery, because
      a peer's window can outlive the row's embargo.
- [ ] **Size-neutral ranks** of the columns the models lean on, ranked
      within a size band like the sector ranks. Those columns are
      volatility, return on capital, momentum and the conservative
      score.
- [ ] **Information about upside that prices and statements do not
      carry**, if the raw tables have it. That means insider
      transactions from Sharadar SF2, as net buying and clustered buys.
      It also means institutional holdings from SF3, as changes in
      ownership. Both would be point-in-time by filing date. Inside large caps the 112 ranks rank
      risk and one quality factor and nothing else
      (docs/notes/2026-10-01-large-caps.md).
- [ ] **Market-state features**, from PLAN §5.6. The thesis's condition 2, the
      era, is the whole of 2021-26, and a stock's own columns cannot say
      what era it is. This is carried from the section below.
- [x] **Data before 1998, if it can be had.** Carter closed this the same
      day: Sharadar starts in 1998 and nothing comparable goes further
      back. The panel and the snapshots begin on 1997-12-31, so the first
      possible picks are January 1999. The test of decision 35 therefore
      saw the last year of the dot-com run-up and its aftermath, and not
      the years the bubble grew. The question 2021-26 raises is whether
      a low-risk, quality selection trails for years while a bubble
      inflates, and that needs 1990-1998. Check where the raw tables
      start. If the vendor's history starts there too, this needs
      another source for prices and statements.
- [ ] **An equal-weighted benchmark series in the price panel**, for the
      investable universe and for its largest fifth. Then a backtest can
      be set beside "the average large stock" as a portfolio, and not
      only per buy.
- [ ] Delisting-aware outcomes and within-sector risk ranks are carried
      from the section below.

These are proposed and not built, each on its own `claude/<topic>`
branch:

- [ ] **"The index minus the predicted losers"** is a
      capitalization-weighted portfolio of large caps without the
      forest's worst quintile. It is the literal form of the thesis and
      the use the forest's ranking supports. Among large caps the forest
      separates the worst quintile and nothing above it. It needs a "buy
      every candidate above a rank" strategy. It is recorded with its
      two problems. It would have left out NVDA, TSLA and META in 2023,
      because they rank in the forest's middle. And it is a 600-stock
      portfolio rather than a screener for one person.
- [ ] **A position cap** in the strategy is carried from below and is
      low priority, because the candidate's largest holding is 8%.
- [ ] Add `peer_column` to the sweep configs that are run from here on,
      and to `eval_screen_dv100k.toml`'s successors. A sweep without it
      is read against all rows, which is mostly size.

These questions were settled in this session, with the details in docs/findings.md:

- [x] I read the holdout look in cell C (decision 29). I traded the
      candidate to 2026-08-21 (decision 28). I answered why it ended
      behind SPY (decisions 30 and 32). I built `sector` as a model
      input, and it changes nothing (decision 31). The floor and the
      sector cap went into `vml-predict`. On selection inside large caps,
      no arm passes (decisions 32 and 34). I rewrote docs/agents.md
      (decision 27).

### Next, from the sessions of 2026-09-30 and 2026-10-01 (decisions 14-26)

Start with docs/findings.md and docs/notes/2026-10-01-candidate.md.
The candidate is cell C's forest, 12-month momentum and return on
capital by mean rank. I tried 31 backtest configurations on buys of
2005-2020, and I run no more on those years.

These items are Carter's, in order:

- [x] **Open and merge the pull request** from
      `claude/results-2026-10-01` into `Claude` with
      `gh pr create --base Claude --head claude/results-2026-10-01 --fill`.
      It carries seven code changes, the docs, 20 promoted results and
      the sandbox's ledger shard. 486 tests pass, and it passes
      `scripts/check_tracked_configs.py`. The separate feature branches
      are stacked and all contained in it, so delete them after the
      merge. They are `claude/universe-and-portfolio-screen`,
      `claude/eval-blend`, `claude/calibration-label-lag`,
      `claude/backtest-rank-sell`, `claude/backtest-buy-outcomes`,
      `claude/predict-universe` and
      `claude/backtest-marketcap-weighting`. The code, by commit:
      - `[[universe]]` row filters, `[pick_screen]`, selection by score,
        and boolean flags as inputs.
      - `blend` in vml-eval.
      - **The calibration look-ahead fix.**
      - `[sell] max_rank_pct`.
      - Per-buy outcomes in every backtest report.
      - The universe applied in `vml-predict`.
      - `weighting = "marketcap"`.
- [x] **One holdout look** in cell C's 3y cell, with
      `python scripts/run_final_eval.py experiments/forest_nonloser_dd30_3y.toml`.
      The forest is the only fitted part of the candidate. The look says
      whether "not a loser" is still predicted on 2021+ snapshots. The
      walk-forward numbers were p@20 0.79 against a base rate of 0.39.
      It does not test the blend. Read it beside the 2021-23 trading run
      (decision 26).
- [x] **Which liquidity floor to deploy with**: 100,000 a day, which is
      the template, or `dollar_volume_3m_rank >= 0.2`, which is
      era-neutral. The candidate is the same under either, at 12.24% and
      12.15%. Carter's answer is the era-neutral rank.
- [ ] **Deploy and paper-trade the candidate** beside its
      sell-discipline variant. This is carried to the section above,
      with what the run to 2026 showed.

This code is worth building next, each item on its own `claude/<topic>` branch:

- [x] **The floor and the sector cap in `vml-predict`**: I built them on
      2026-10-01 as `--filter`, `--pick` and `--max-per-group` on
      `claude/predict-selection`. The call is `--filter "dollar_volume_3m
      >= 100000"` with `--max-per-group 2`. The deployed list is then
      the backtest's selection and not a ranking to be filtered by hand.
- [ ] **A position cap** in the strategy, on the `Strategy` interface,
      stops adding to a holding above a share of the portfolio. The
      quality blend buys 94 stocks in sixteen years, and two holdings are
      a third of it with the sell discipline. The candidate's largest
      holding is 8%.
- [x] **`sector` as a model input**: I built it on `claude/sector-feature`
      and ran it in the second session of 2026-10-01 as
      `forest_sector_nonloser_3y`. It gave the same picks, the same
      sectors and the same precision (decision 31). Carter said on
      2026-10-01 that the cap is a bandage, and that the model might
      learn that a column means something different for REITs. The
      design was a one-hot of `sector` in
      `harness.dataset.feature_matrix`, a per-row recoding like the
      boolean flags, with the current-state caveat stated in every
      report. One sweep in cell C compared ranks with ranks plus sector,
      read on the screen and on sector shares.

These are open questions, each with the experiment that would answer it.
None needs a backtest on 2005-2020:

- [ ] **Why is the screen about 0.02 a year harsher on blends with
      momentum than the backtests' own buys?** A third of it is the
      delisting convention. Entry timing, the snapshot against the first
      trading days of the next quarter, is the untested rest.
- [ ] **Run a parameter search on the theory-led feature set**, fs2 of
      decision 18, before its verdict is final. It was run on a forest
      configuration tuned on the ranks. This is low priority, because 20
      draws moved PR-AUC by 0.005 on the ranks.
- [ ] **Does the candidate's lead survive a longer wait between the
      snapshot and the buy?** The backtest buys one to six months after
      the snapshot, and live trading on a fresh inference set buys
      sooner. It is untested either way.

These are upstream requests for a new dataset version, and nothing is
derived here:

- [ ] **An outcome that treats a delisting as a portfolio does.** Per
      horizon it gives the delisting date and a return with the proceeds
      in the benchmark from the delisting to the horizon. Today an
      acquired stock is carried flat, which understates it in every
      `fwd_*` outcome and upside label. Such stocks are 15% of the
      momentum blend's screen picks
      (docs/notes/2026-09-30-blends-and-calibration.md).
- [ ] **Within-sector ranks of the risk columns**, volatility and the
      conservative score, for sector-neutral models.
- [ ] **Market-state features**, from PLAN §5.6. Calibrated or not, score
      thresholds select years rather than stocks. A confidence that
      means the same in 2008 and 2012 cannot come from a stock's own
      columns (see docs/notes/2026-09-30-blends-and-calibration.md and
      2026-09-30-one-year-cell.md).

These questions were settled in these sessions, with the details in docs/findings.md:

- [x] None of these helps: a training-time liquidity floor, theory-led
      feature sets, the 1-year horizon, selection by calibrated
      confidence, a learned upside model, and capitalization-weighted
      buys. A sell discipline helps the candidate and the quality blend,
      and does not help forest plus momentum. I ran the 2021-23 trading
      with Carter's leave.

### Next, from the session of 2026-09-29/30 (Carter's notes, decision 13)

The candidate and its evidence are in docs/findings.md under "State"
and in docs/notes/2026-09-29-decisions.md. Start a new session there.

- [x] **Carter** takes one holdout look in cell C's 3y cell and opens the
      pull request for `claude/backtest-sector-cap`. The sector cap
      reached `Claude` with PR #17. The holdout look is carried in the
      section above, with the same forest.
- [x] **Sell discipline** for the candidate. Carter asked for it on
      2026-09-30: one backtest with `strategy = "sell_below_criteria"`,
      with the criteria fixed before the run, as the 14th backtest on
      2005-2020. It works best with a calibrated model, which buys on
      high confidence and sells or rebalances when it falls. I ran it on
      2026-09-30 as a rank criterion, `[sell] max_rank_pct = 0.2`, on the
      candidate and on the quality blend (decision 21). The results are
      in docs/notes/2026-09-30-backtests.md.
- [x] **Quick evaluation by confidence, and not only by K.** Carter asked
      for this on 2026-09-30. The report's "High-confidence picks" table
      shows how many names clear a score and how precise they are. The
      request was to add the pick outcomes at those thresholds, per year
      and pooled. Then "mean excess CAGR at score > 0.7" can be read.
      Those outcomes are the mean excess CAGR, the losers and the big
      winners of every pick with `score >= p`. Report the **mean** beside
      the median, because an equal-weighted portfolio earns the mean, and
      the best picks may outweigh the worst. A median excess CAGR below
      zero is not a failure. Holding cash when nothing clears the bar is
      a valid strategy. The number of picks a year at a threshold is part
      of the result. I built it on 2026-09-30 on
      `claude/universe-and-portfolio-screen`. With `score_thresholds` and
      `pick_outcomes` set, the report's "Selection by score" tables give
      the rows and stocks at or above each threshold, per year and
      pooled. They give their precision and the mean and median of every
      outcome, and years with no pick are shown.
- [x] **Calibration.** This is the prequential Phase 3 item above, and it
      comes before any rule that reads a score as confidence. I measured
      the candidate's forest on 2026-09-29. The top scores were these:

      | entry years | top scores | precision |
      |---|---|---|
      | 2006-08 | 0.81-0.85 | 0.15-0.60 |
      | 2011-13 | 0.65-0.69 | near 1.0 |

      So a fixed threshold picks the pre-crash years. The confidence rule
      needs a threshold relative to the year's scores, or calibrated
      probabilities. On 2026-09-30 I ran it on the candidate's forest
      after fixing a look-ahead in the calibrator. An honest calibrator
      for a 3-year label is four years behind, and an absolute confidence
      bar would have held cash through the best entry years. The note is
      docs/notes/2026-09-30-blends-and-calibration.md. A 1-year cell is
      the follow-up (decision 22).
- [x] **Features are selected on theory, and not only on the manifest
      groups.** Carter said on 2026-09-30 that the models lean on a few
      columns, the volatility and liquidity ranks among them. Try
      excluding them, and prefer columns with a causal story in value
      investing: cash generation, balance-sheet strength, profitability
      and consistency. One August winner,
      `forest_random_search_3y-2seeds2` on v1.1 and 3y beat_spy, used
      `groups = ["ranks"]`, `exclude_families = ["ranks/technical",
      "ranks/trend"]` and `families = ["features/trend",
      "features/technical"]`. On v1.4 in cell A, fundamentals only scored
      0.40-0.42 against 0.50. Its picks beat SPY 0.63 of the time before
      2013 and 0.28 after (docs/notes/2026-09-29-pick-anatomy.md). So the
      question is open in cell C and on pick outcomes and backtests, and
      not on p@20. On 2026-09-30 I ran five sets in cell C, on all rows
      and inside two liquidity floors, read on the portfolio screen. No
      set without the risk ranks matches the ranks. They earn 0.013-0.034
      a year less mean excess, have more losers, and pick the same two
      sectors through operating-cash-flow stability. The floor at
      training changes nothing for the ranks forest. The note is
      docs/notes/2026-09-30-features-and-floor.md. That was one seed and
      one forest configuration, and a parameter search on the theory-led
      set is the untested rival.
- [x] **The liquidity floor applies at training time.** Carter asked on 2026-09-30 to
      drop rows below a dollar-volume threshold from training and test.
      That is the investability filter applied to the dataset, and not
      only to the backtest. It gives less microcap noise, and the models
      need not learn the liquidity columns. The design is a row filter on
      a manifest feature column, declared in the config, part of the hash
      and of the report. The label cell stays the same, so the trial
      count needs a "universe" qualifier. It is not feature engineering,
      because there is no new column, and I checked data/manual.md
      before building it. I built it on 2026-09-30 on the same branch as
      `[[universe]]` in configs and sweeps, with `universe_scope =
      "test"` for the reference arm. It gives a universe-qualified ledger
      cell and is carried into bundles, deployment refits and backtest
      refits. The "Universe" section of docs/experiments.md describes it.
- [x] **Upstream request:** within-sector ranks of volatility and of the
      conservative score. This is carried in the section above.
- [x] **The pick-outcome screen has a sector cap** (`eval/picks.py`), so
      that the screen sees what the backtest sees. Every run report also
      has a sector table of the top-K picks. I built it on 2026-09-30 on
      the same branch as `[pick_screen]`. It takes the top K per test
      quarter with a cap per sector, and shows the picks' share by sector
      beside the test rows'.
- [ ] Change the ranking metric for boosted-family searches to p@K over
      2013-20 of the worst seed, instead of PR-AUC. The two metrics order
      LightGBM and XGBoost draws in opposite directions.
- [x] Whole shares at 100 a pick leave many months short of 10 buys in
      the capped backtests. Between 55 and 108 of the 192 months fall
      short. The item was to consider
      `fractional_shares` or a larger monthly deposit in the template,
      stated as a template change. On 2026-09-30 I re-ran the candidate
      with fractional shares. The template is unchanged:

      | candidate | TWR | final value |
      |---|---|---|
      | whole shares | 12.24% | 948,956 |
      | fractional shares | 12.12% | 936,540 |

- [x] Why were there 134 delisting liquidations with momentum against 52
      without? Were they takeover targets? The item was to read the
      trades CSV of the promoted backtest. On 2026-09-30 the answer was
      yes. Of the 134, 21% were at a loss. 33 were within 10% of cost,
      bought a median three months before the delisting. Their total
      returns were these:

      | the 134 delisted buys | total return |
      |---|---|
      | mean | +79% |
      | median | +39% |

      The note is docs/notes/2026-09-30-blends-and-calibration.md.

## 3.5 — Downturn specialization (PLAN §4 Phase 3.5)

Make crash performance a training and selection objective, and not only
a report slice. Everything stays within the invariants: no local splits
and no derived features.

- [ ] Add regime-emphasis training weights: a config-declared multiplier
      on `sample_weight_{H}y` for training rows whose label windows
      overlap drawdown eras, disclosed, hashed and reported. Report the
      effective sample size under emphasis, so that the shrinkage is
      visible.
- [ ] Add a crash-aware `rank_metric` for sweeps. It ranks candidates by
      precision or recall-at-precision restricted to crash-era test
      years, with the Wilson-interval caveat stated in the summary.
- [ ] Write the specialist configs. Relative labels, `beat_spy`, are the
      default cell for downturn models. Sweep tree, forest and lgbm under
      regime emphasis and compare them against the unemphasized winners
      on the crash-era table.
- [x] Derived labels are binary targets re-thresholded on the fly from
      the manifest's continuous outcomes, so that new rungs never need a
      dataset rebuild. An example is `label = "fwd_3y_cagr >= 0.1 &
      fwd_3y_max_drawdown_from_entry < 0.3"`. The code is
      `src/harness/derived_labels.py`, evaluated by `Dataset.frame`, and
      it is row-wise only. I built a cross-sectional `cohort_pct` rank
      and removed it. A cohort peer's label window can close up to a quarter
      after the row's own, which erodes the embargo. Also, the `beat_spy`
      and `excess_cagr` thresholds already give an era-neutral target. If
      it is ever wanted, it is an upstream label, so that the purge can
      see it.
- [x] data/versions.md records that `dataset_v1.3` first ships
      `fwd_{H}_max_drawdown{,_from_entry}` (upstream decision 0017).
      Drawdown-label configs set `min_dataset_version = "1.3"`.
- [ ] Once drawdown configs exist, consider asking upstream to drop the
      stored `label_{H}_cagr_ge_*` and `excess_ge_*` rungs. Each is a
      one-line expression now, and `fwd_{H}_cagr >= 0.1` reproduces
      `label_{H}_cagr_ge_10` exactly, which is tested. Existing configs
      name the stored columns, so this is a breaking version. Migrate
      their labels to expressions first, and note that the ledger cell
      name changes with it.
- [ ] Build two-stage survival gating. A stage-1 survival model has a
      target such as `fwd_{H}_max_drawdown_from_entry < 0.3`, a derived
      label now that upstream ships the continuous drawdowns. A stage-2
      return model ranks survivors only. Evaluate the gate's precision
      cost outside crashes.
- [ ] File upstream requests for point-in-time market-state context
      features, such as drawdown from high and index volatility, if
      regime-conditional models ever need them. The ~~max-drawdown
      label~~ shipped upstream as the continuous
      `fwd_{H}_max_drawdown{,_from_entry}` (decision 0017), and the
      binaries are derived labels here.

## Model families to explore (PLAN §8)

- [ ] Build a weighted, calibrated logistic regression on the rank
      feature set. It is the cheapest new family, has interpretable
      coefficients and doubles as a stronger baseline. Imputation is
      fold-internal only, and disclosed.
- [ ] Run KNN and SVM comparison runs, registered as experiments like
      any other. They use rank features only, which are already scaled,
      fold-internal imputation, and a subsampling strategy that respects
      the uniqueness weights. Keep them unless they beat trees on the
      precision-floor metrics.
- [x] The regression reframe mechanism: `lightgbm_regressor` trains on
      the continuous `fwd_{H}y_cagr` and `fwd_{H}y_excess_cagr` columns.
      The objectives are `regression`, `regression_l1`, `huber` and
      `quantile`. Quantile with a low `alpha` value ranks by a pessimistic return
      estimate, the regression analogue of the precision knob.
      `winsorize = q` clips the training target fold-internally, under
      the extreme-return caveat. Configs set `eval_label` to a binary
      cell, and every metric, report and eval stays in the precision@K
      frame. The trial ledger and the baseline comparison charge the run
      to the eval cell. The guardrail is that continuous columns refuse
      `astype(bool)` coercion under classifiers, and the reverse holds
      too. The code is in `models/gbm.py` and
      `harness/dataset.py::_target_array`. The exemplars are
      `experiments/lgbm_regressor_3y_cagr_ge_10.toml` and
      `experiments/sweeps/lgbm_cagr_quantile_3y.toml`.
- [x] Regression runs have diagnostics beyond the binary frame (see
      `eval/metrics.regression_diagnostics` and `eval/era.py`). Continuous
      runs carry the realized outcome through the prediction frames. So
      the era table and the pooled block report `fwd_at_K`, the mean
      realized CAGR of the top-K picks, picked per year. Sweeps can rank
      on it with `rank_metric = "fwd_at_20"`. They also report
      `spearman_ic`, the rank IC, whose pooled row is the mean of the
      per-year ICs, because per-fold scores are not comparable. Weighted
      MAE and R² go to the results store as fit diagnostics only. An R²
      near zero on stock returns is normal and says nothing about the
      top of the ranking, so neither is ever the headline.
- [x] I ran the regression-reframe spike `lgbm_cagr_quantile_3y` against
      `dataset_v1.1` and compared its summary against the classification
      sweeps on the same eval cells. It did not beat the classifiers,
      scoring 0.44 pooled against 0.47–0.55. The detail is in
      docs/findings.md.
- [ ] Deep learning goes through upstream first. A sequence-shaped
      dataset variant, with per-quarter point-in-time history per stock,
      is a prerequisite, and history must not be flattened locally
      (invariant 4). Then comes a small TCN or transformer with embedded
      categoricals, on the same splits and weights, with era-sliced
      reporting.

## 4 — Phase 4: portfolio construction & backtest

- [x] The backtest harness is `src/portfolio/` with the CLI
      `vml-backtest`, one TOML per strategy in `experiments/portfolios/`,
      and the design in PLAN §4. Walk-forward fold bundles score each
      trade year. Deployment bundles are refused, and buys are
      structurally confined to fold years. The monthly point-in-time
      cross-sections come from `dataset.parquet`: the latest
      completed-quarter median snapshot, staleness-capped, with no label
      columns. The score combination is declared as `product`, `mean`,
      `min` or `mean_rank`, with a per-model floor and validated column
      filters. A buy-and-hold top-K strategy sits behind a pluggable
      `Strategy` interface. The benchmark leg runs through the same
      engine under identical deposits. The report has XIRR, TWR,
      drawdown, a per-year era table and the defensive-hypothesis check.
      Every run goes to the ledger under scheme `backtest`. The exemplar config is
      `experiments/portfolios/allprob_top25_5models.toml`, the live
      five-model AllProb screen.
      Deposits keep rolling past a bundle's last fold year, and the
      `model_update` policy serves those years. `refit` means simulated
      point-in-time year-end deployment refits under manual.md §4 rule 7,
      and `frozen` means the last fold model. Every report flags the
      holdout-era overlap as selection-toxic. Refits are disk-cached
      across runs under `experiments/models/refits/`, keyed by the train
      config hash, the dataset version, the year and the lag. The sidecar
      is validated before a pickle is trusted. Per-model floors
      go through `[signal.min_scores]`. Execution is in whole shares,
      with the realized profit per ticker in the trade log. The
      artifacts go under `reports/backtest/<name>_<config-hash>.*`.
- [x] The investability filter mechanism: `[[investability]]` column
      screens are a mandatory config field. An explicit `investability =
      "none"` opts out and is flagged in the report. Choosing honest
      thresholds from `log_marketcap`, `dollar_volume_3m` and
      `amihud_12m` is still open, below.
- [x] The transaction-cost mechanism is a flat per-side `cost_bps`,
      required in every config with no default, and the costs are paid
      inside TWR. Microcap fidelity, with spread and impact models, is an
      open question in PLAN §8.
- [x] The SPY benchmark runs under identical cash flows. Every report has
      drawdowns and per-year era slices with crash tagging.
- [x] The defensive-hypothesis check breaks out the benchmark's
      down-years in the report. It is not testable when the window has
      none, and the report says so.
- [x] The versioned price panel lives at `data/datasets/prices_vX.Y/`.
      The consumer contract is in `src/portfolio/prices.py` and the
      builder is `scripts/build_price_panel.py`. It is extracted from the
      raw `SEP.closeadj` and `SFP` tables, the labels' own price source,
      through the `TICKERS` ticker-to-permaticker mapping. It is
      restricted to a pinned dataset's universe, and the manifest holds
      the mapping, cleaning and coverage statistics and the raw-pull
      provenance. This is the one sanctioned raw-table read in this
      repo: outcome price paths only, never features. Build it locally
      with the upstream raw directory symlinked, such as `data/raw ->
      ~/radarash-dataset/data/raw`, then run
      `python scripts/build_price_panel.py data/raw dataset_v1.1
      --out-version prices_v1.0`.
- [ ] Run the real backtest of the live five-model screen once the panel
      is built and the five walk-forward bundles exist. Run `vml-run` on
      each model config, fill in the bundle run ids, then run
      `vml-backtest experiments/portfolios/allprob_top25_5models.toml`
      and promote the report.
- [ ] Pick and justify the investability thresholds. Microcaps dominate,
      so report the sensitivity of the headline result to the floor.
- [ ] Add an equal-weight-universe benchmark as a second comparison leg.
- [x] The sell discipline is the `sell_below_criteria` strategy. Held
      positions that fail the sell criteria are sold at rebalance, and
      dropping out of the top K alone is never a sell. An optional
      `[sell]` section gives a separate criteria band for hysteresis, and
      otherwise the sell criteria are inherited from the buy criteria.
      The trade log records each sell with its cause.
- [x] Every backtest report has per-buy outcomes since 2026-09-30, from
      `claude/backtest-buy-outcomes`. Each buy is read over the 1 and 3
      years after its trade date against the benchmark, by buy year and
      pooled. Delisting proceeds ride the benchmark.
- [x] I built the rank-based sell criterion `[sell] max_rank_pct` on
      2026-09-30 on `claude/backtest-rank-sell`. A holding is kept while
      it is among that top share of the month's buy candidates. It is for
      `mean_rank` combinations and for models whose score level moves
      between years.
- [ ] Add richer strategies behind the `Strategy` interface: periodic
      full rebalance, stop-loss and trailing-stop sells, position caps,
      and partial trimming. Partial trimming sells down to weight instead
      of all or nothing.
- [ ] Cross-section rank freshness: the ranks in a backtest
      cross-section are relative to each snapshot's own quarter. Consider
      an upstream "as-of re-rank" artifact if this approximation ever
      drives results.

## Upstream coordination / watch list

- [ ] The earliest-trustworthy-year verification, which is the
      survivorship-depth check, is still open upstream. Until it is
      resolved, treat pre-2000 cross-sections with suspicion (see PLAN §8).
- [ ] The restated-dimension dataset variant (decision 0009) is needed
      for the restated ablation.
- [x] ~~A versioned price panel for Phase-4 backtests~~: I resolved this
      locally. `scripts/build_price_panel.py` extracts it from the raw
      SEP, SFP and TICKERS tables, as §4 above says, so no upstream build
      stage is needed. Upstream only needs to keep shipping `data/raw/`.
- [ ] An inner-validation role is needed only if early stopping ever
      becomes worth it. Invariant 1 stays absolute. There is no local
      split carving, however "temporal and careful" it looks. The purge
      and embargo machinery lives upstream, and a second local
      implementation would drift silently. LightGBM early stopping is the
      only use case so far that needs rows held out inside the training
      window. Calibration is served prequentially without them. If one is
      genuinely needed, the sanctioned path is an upstream request. That
      request is an additional `inner_val` role inside each walkforward
      fold's training window, shipped as extra rows in `splits.parquet`.
      It would be the last pre-purge year, purged and embargoed against
      the rest of train with the same discipline as test. It is additive
      and opt-in. Configs that ignore the role are byte-identical in
      behavior, so there is no "third split always" burden. The role is
      frozen and citable like every other fold definition. Weigh it
      against the cheap alternative first: the random search already
      tunes the boosting rounds across folds.
- [ ] File any feature request discovered during modeling upstream, as a
      new dataset version. Nothing is engineered here.
