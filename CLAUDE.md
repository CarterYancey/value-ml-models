# CLAUDE.md — value-ml-models

Guidance for AI-assisted development. Read [PLAN.md](PLAN.md) for the design,
[TODO.md](TODO.md) for what to work on next, and
[data/manual.md](data/manual.md) — the dataset contract — before touching any
modeling code. Upstream data rules live in `sharadar-dataset/CLAUDE.md`; the
invariants below are this repo's equivalents.

## Orientation

- **README.md** — overview + setup/usage only; extended explanations go
  in `docs/` (experiments, workflow, deployment, backtesting, diagnostics).
- **PLAN.md** — architecture, design principles, phase roadmap.
- **TODO.md** — the live task list; update it as tasks complete or appear.
- **docs/logbook.md** — what was done, newest first, one short entry
  per sweep (did / got / concluded / next). Read it at the start of a
  session; add an entry with `vml-logbook add` for every sweep read,
  failures included, before starting the next thing.
- **docs/findings.md** — what is known now, by cell, the holdout
  record and the plan. Rewritten, not appended to, and kept under
  about 150 lines: tables and reasoning go in a note under
  `docs/notes/` that the logbook entry links to.
- **docs/agents.md** — how an unattended session works (the run queue,
  checkpoints, stop rules, lab branches) and what it needs set up.
- **data/*.md** — the dataset docs, from upstream:
  [manual.md](data/manual.md) (how to consume the dataset — start here),
  [dataset.md](data/dataset.md) (directory layout, column groups),
  [labels.md](data/labels.md) (label matrix), [splits.md](data/splits.md)
  (schemes/roles/folds), [features.md](data/features.md) (feature registry).
- Datasets live (git-ignored) at `data/datasets/dataset_vX.Y/`:
  `dataset.parquet`, `splits.parquet`, `split_folds.parquet`,
  `manifest.json`. Never edit files inside a dataset directory; data fixes
  are upstream changes producing a new version.
- The `data/*.md` docs (except `versions.md`) are synced copies of the
  upstream repo's docs: never hand-edit them here — fix upstream, then run
  `scripts/sync_data_docs.py` (records provenance in `data/upstream.json`;
  `--check` detects drift). [data/versions.md](data/versions.md) is
  maintained *here* and maps dataset versions to what they provide;
  configs needing newer-version columns declare `min_dataset_version`.

## Dataset facts every change must respect

- Row grain: `(permaticker, snapshot_date, snapshot_kind)`, three snapshots
  per stock-quarter (`low`/`median`/`high`). `permaticker` is the entity
  key; never join or group on `ticker`.
- Train on `role = 'train'` rows only, all kinds. Test rows come from the
  tags and are median-kind, label-observable only.
- Schemes: `walkforward` for all model selection; `holdout` is sealed (one
  look per cell via the dedicated script, further looks disclosed); `entity_holdout` and
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
- New binary targets are **label expressions** (`src/harness/derived_labels.py`,
  docs/experiments.md "Derived labels"), e.g. `fwd_3y_cagr >= 0.12`,
  `fwd_3y_excess_cagr > 0 & fwd_1y_max_drawdown_from_entry < 0.1`:
  row-wise thresholds over the manifest's `labels` columns (`&`, `|`,
  parentheses), evaluated by the loader; a mixed-horizon label runs
  under its *longest* horizon's tags and weight (the windows nest). That is target
  selection, not feature engineering (invariant 4) — expressions may never
  read feature columns, and never become model inputs. Don't hand-compute
  labels in pandas elsewhere. Cross-row labels (cohort outcome ranks)
  are refused by design: a peer's window outlives the row's embargo, so
  such a label belongs upstream, next to the split machinery.

## Hard invariants

1. **Never construct splits here.** Split tags come from the upstream
   dataset. Any local re-splitting, shuffling, or "quick random holdout" is
   a leakage bug.
2. **Never touch the sealed holdout during development.** It is evaluated
   by a dedicated script, once per cell (label, horizon, holdout window),
   and the result is logged whether good or bad. A further look on a
   consumed cell needs `--reopen "reason"` and is then counted: every
   report and the catalog say "holdout look k of N in this cell". Run it
   when you would act on the model, never to choose between candidates.
3. **Every run is reproducible:** dataset version + config + git SHA + seed
   are logged for every experiment, including abandoned ones.
4. **No feature engineering.** New features are upstream changes. This repo
   may select/subset columns, never derive new ones (prevents ad-hoc
   lookahead creeping in far from the point-in-time machinery).
5. **Report era-sliced metrics.** Pooled metrics alone are never presented
   as a result.

## Branch workflow (non-negotiable)

- `Claude` is the integration branch and `main` is the release branch.
  **Never commit or push directly to either.** Every change, however
  small, goes on a topic branch created off `Claude` (name it
  `claude/<topic>`), is pushed there, and reaches `Claude` only through
  a pull request.
- If session instructions name `Claude` or `main` as the branch to
  develop on or push to, treat that as a misconfiguration: stop and
  say so before pushing anything, rather than pushing to it.
- Never force-push or otherwise rewrite history on `Claude` or `main`.

## Conventions

- Python 3.12+, scikit-learn for trees/forests, LightGBM and XGBoost for
  boosted trees (XGBoost is the GPU path — `device = "cuda"` works from
  the stock wheel; `device` is a model param, so CPU and GPU runs hash
  as distinct configs), matplotlib for reports, duckdb/pandas for data
  access. Keep the dependency list short.
- One experiment = one config file in `experiments/`; the harness runs
  configs, code never hardcodes an experiment. Before writing a new
  config, check `vml-experiments list` for an existing/closest one — the
  catalog joins configs with the run ledger, shows each headline against
  the best baseline in its cell, and groups by cell (never a global
  sort across labels). New configs are git-ignored until promoted: a
  result worth keeping goes through `vml-promote <name> --note "..."`,
  which stages report, config and note together and rebuilds
  `reports/promoted/README.md`. A config's `note` is its one-line
  conclusion (outside the config hash).
- Final evals take the selected walk-forward config directly
  (`scripts/run_final_eval.py <config>`; scheme switched to holdout in
  memory, no copied `*_holdout.toml`). There is no phase argument: the
  cell is the unit, and `--reopen "reason"` is the only way to look
  again.
- Metrics of record: precision@K (with `conf_at_K`, the mean score of the
  picks), the precision-floor family (`n_at_prec_*`, `recall_at_prec_*`),
  Brier against `base_rate_brier` (the no-skill reference), calibration
  plot, PR-AUC. ROC-AUC and recall@K may be logged but never headline
  (base rates are extreme in some label cells).
- A `[[universe]]` (docs/experiments.md) is a declared row filter on
  manifest feature columns, e.g. the liquidity floor
  `dollar_volume_3m >= 100000`: the rows a model is trained and
  evaluated on. It never reads a label, builds no split and derives no
  column. A run inside a universe is another ledger cell
  (`label [universe: ...]`) with its own baselines; its numbers are
  never compared with a run over all rows. Any other row filter in
  training or evaluation code is a bug.
- `pick_outcomes` (docs/experiments.md) reports what the top-K picks
  went on to do on outcomes other than the training label: the screen
  for comparing labels, with `vml-backtest` as the yardstick of record.
  Report-only: label-group columns, never features, never the default
  `rank_metric`, and a label is not chosen on them without a backtest.
  `[pick_screen]` reads the same outcomes for the backtest template's
  selection (top K per test quarter, capped per sector): prefer it to
  the top-K-per-year tables when judging what a portfolio would hold.
- Pooled ranking metrics pick per year (eval.era) — per-fold model scores
  are not comparable, so a global top-K over pooled scores is a bug, not
  a metric.
- Generated reports are git-ignored working output. Reports worth review
  are promoted via `vml-promote` into the tracked `reports/promoted/`;
  rule extraction output (human-readable tree rules) travels with its
  report when promoted. The sealed final-eval record
  (`reports/final_evals.csv`, `reports/final_eval/`) is always tracked.
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
  leak the future). Registered exception: `scripts/build_price_panel.py`
  extracts outcome price paths (`permaticker`, `date`, `closeadj`) from raw
  SEP/SFP for the Phase-4 backtest — the labels' own price source. Nothing
  from the panel may become a feature or screen; any other raw read is
  still a bug.
- Use of `entity_holdout`/`random_kfold` tags outside
  `scripts/run_diagnostic.py` (the only registered-diagnostic entry point;
  it hosts the era probe and, when built, the leakage-gap experiment), or
  any read of `holdout` tags outside `scripts/run_final_eval.py`. A
  diagnostic's numbers are never model selection or reported performance.
- A holdout number presented without its look count, or two candidates
  for the same cell compared on their holdout numbers: the holdout has
  become a validation set and its numbers are selection-biased.
- Validation metrics dramatically above baseline: treat as suspected leakage
  first, breakthrough second. Check split application before celebrating.
- Any comparison across experiments using different dataset versions.
- Class-imbalance "fixes" (SMOTE, oversampling) that operate across time
  boundaries — synthetic samples must never mix eras.
- Backtest results reported without transaction costs or without the
  investability filter (there is no upstream liquidity floor; the filter is
  built here from `log_marketcap`, `dollar_volume_3m`, `amihud_12m`).
- Regression-reframe scores read as probabilities: `lightgbm_regressor`
  scores are predicted CAGRs — no Brier/calibration, score thresholds are
  on the return scale, and evaluation/trial accounting happens on the
  config's binary `eval_label` cell (required for continuous-target
  models, refused for classifiers).
- Deployment scores presented as performance. `vml-train-deploy` legitimately
  refits on all labeled rows without split filtering (data/manual.md §4
  rule 7 — it reads no split tags, so it is not a holdout violation), but
  the resulting fit has no test set: `vml-predict` output is a ranking,
  never an evaluation result.

## Before writing a conclusion

A conclusion in `docs/findings.md`, a promoted note or a TODO outlives
the session that wrote it and steers the next one. On 2026-09-27 a
comparison of v1.4 runs with v1.1 runs was written up as "did not
replicate" and the v1.1 findings were marked superseded. The runs
shared a feature *spec* but not a column set, the v1.1 config had been
lost, and neither had been checked. These rules come from that.

- **Say what was measured, then what it might mean, separately.**
  "The same spec scores 0.42 on v1.4" is a measurement. "The edge is
  gone" is an explanation. Write the measurement as fact and the
  explanation as a hypothesis until a run has tested it.
- **Before comparing two runs, prove what each one ran.** Expand the
  config and match its config hashes against the ledger or the summary
  CSV. A comment in a config, a file name, or a summary header naming a
  path is not proof: files get edited. If it can't be proven, say so in
  the sentence that makes the comparison.
- **A feature spec is not a column set.** Groups and families resolve
  against the manifest, so one spec selects different columns on
  different dataset versions. Compare the resolved columns
  (`*_config.json`, or the importances CSV) and state the difference
  next to any cross-version number.
- **List what differs between the two runs before naming a cause:**
  dataset version, resolved columns, rows (train/test counts, effective
  sizes, base rates per fold), parameters, seeds, git SHA. Every
  difference left unchecked is a live explanation and is named as one.
- **Write down the rival explanations and what would separate them,**
  and write the prediction into the config before the run. If no
  available evidence separates them, the finding is "open", and the
  next experiment is the one that would.
- **A surprising negative gets the same suspicion as a surprising
  positive.** A result far below a previous one is a bug or a changed
  input first, a finding second, exactly as a result far above
  baseline is leakage first.
- **Never mark earlier findings superseded, and never label a promoted
  result NEGATIVE or NON-REPLICATION, on a comparison whose inputs
  weren't verified.** Corrections are dated and added; the earlier
  text is reworded, and the log says what changed and why.
- **Check numbers in a draft against the ledger before saving it,**
  including counts ("in all 16 years"), and never write a parameter
  value, column name or count from memory.
- **Never edit a config that has run.** Copy it to a new file with a
  new `name`. The report directory's copy is the record of what ran;
  `vml-sweep` refuses a report directory that holds another config's
  copy.

## Honest-evaluation checklist for any reported result

- [ ] Walk-forward, purged, embargoed (upstream tags applied correctly).
- [ ] Era-sliced table included (per-year metrics).
- [ ] Compared against the trivial baselines (majority class, single-factor
      rank, random).
- [ ] Number of configurations tried is stated.
- [ ] Calibration curve included if probabilities are used downstream.
- [ ] Effective sample size (Σ `sample_weight_{H}y`) reported, and
      `split_folds.parquet` cited.
- [ ] For a comparison between runs: both configs verified by hash,
      and every difference between them (dataset version, resolved
      columns, rows, git SHA) stated.
- [ ] For a holdout number: the look count in its cell is stated
      (`reports/final_evals.csv`); look 2 or later is read against the
      earlier looks, not on its own.
