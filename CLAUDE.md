# CLAUDE.md — value-ml-models

This file is the guidance for AI-assisted development. Read
[PLAN.md](PLAN.md) for the design and [TODO.md](TODO.md) for what to work
on next. Read [data/manual.md](data/manual.md), the dataset contract,
before touching any modeling code. Upstream data rules live in
`sharadar-dataset/CLAUDE.md`. The invariants below are this repo's
equivalents.

## Orientation

- **GLOSSARY.md** holds the shared vocabulary, one term per concept. Use
  its terms. Add to it when a concept is new.
- **README.md** holds the overview and the setup and usage instructions
  only. Extended explanations go in `docs/`: experiments, workflow,
  deployment, backtesting, diagnostics.
- **PLAN.md** holds the architecture, the design principles and the
  phase roadmap.
- **TODO.md** is the live task list. Update it as tasks complete or
  appear.
- **docs/logbook.md** records what was done, newest first, in one short
  entry per sweep with the fields did, got, concluded and next. Read it
  at the start of a session. Add an entry with `vml-logbook add` for
  every sweep read, failures included, before starting the next thing.
- **docs/findings.md** states what is known now, by cell, with the
  holdout record and the plan. Each update rewrites the file instead of
  appending to it, and the file stays under about 250 lines. Tables and
  reasoning go in a note under `docs/notes/` that the logbook entry
  links to.
- **docs/agents.md** describes how an unattended session works and what
  it needs set up. It covers the run queue, checkpoints, stop rules and
  lab branches.
- **data/*.md** are the dataset docs, from upstream.
  [manual.md](data/manual.md) says how to consume the dataset, so start
  there. [dataset.md](data/dataset.md) gives the directory layout and
  the column groups. [labels.md](data/labels.md) gives the label matrix.
  [splits.md](data/splits.md) gives the schemes, roles and folds.
  [features.md](data/features.md) is the feature registry.
- Datasets live, git-ignored, at `data/datasets/dataset_vX.Y/`. Each one
  holds `dataset.parquet`, `splits.parquet`, `split_folds.parquet` and
  `manifest.json`. Never edit files inside a dataset directory. Data
  fixes are upstream changes that produce a new version.
- The `data/*.md` docs, except `versions.md`, are synced copies of the
  upstream repo's docs. Never hand-edit them here. Fix upstream, then run
  `scripts/sync_data_docs.py`, which records provenance in
  `data/upstream.json`. Its `--check` flag detects drift.
  [data/versions.md](data/versions.md) is maintained *here* and maps
  dataset versions to what they provide. Configs that need
  newer-version columns declare `min_dataset_version`.

## Dataset facts every change must respect

- The row grain is `(permaticker, snapshot_date, snapshot_kind)`, with
  three snapshots per stock-quarter: `low`, `median` and `high`.
  `permaticker` is the entity key. Never join or group on `ticker`.
- Train on `role = 'train'` rows only, all kinds. Test rows come from the
  tags and are median-kind, label-observable only.
- The schemes have fixed roles. `walkforward` is for all model selection.
  `holdout` is sealed: one look per cell via the dedicated script, and
  further looks are disclosed. `entity_holdout` and `random_kfold` are
  diagnostic-only, and `random_kfold` is deliberately leaky.
- `sample_weight_{H}y` is passed as a native sample weight in every fit.
  The effective sample size, the sum of the weights, is what gets
  reported, not row counts.
- Delisted rows, where `delisted_in_window_{H}` ≠ 'false', are labeled
  rows like any other. Filtering them out reintroduces survivorship bias.
- Select columns via `manifest.json["columns"]`, never by pattern-matching
  names.
- NULLs are meaningful. They mark no filing, burn-in, structural gaps and
  rank guards. Never impute globally. Imputation is fold-internal
  only, and disclosed.
- New binary targets are **label expressions**, defined in
  `src/harness/derived_labels.py` and described in docs/experiments.md
  under "Derived labels". Examples are `fwd_3y_cagr >= 0.12` and
  `fwd_3y_excess_cagr > 0 & fwd_1y_max_drawdown_from_entry < 0.1`. A
  label expression is a row-wise threshold over the manifest's `labels`
  columns, combined with `&`, `|` and parentheses, and the loader
  evaluates it. A mixed-horizon label runs under its *longest* horizon's
  tags and weight, because the windows nest. That is target selection,
  not feature engineering, so invariant 4 is not touched. Expressions
  may never read feature columns, and never become model inputs. Don't
  hand-compute labels in pandas elsewhere. Cross-row labels, such as
  cohort outcome ranks, are refused by design. A peer's window outlives
  the row's embargo, so such a label belongs upstream, next to the split
  machinery.

## Hard invariants

1. **Never construct splits here.** Split tags come from the upstream
   dataset. Any local re-splitting, shuffling, or "quick random holdout" is
   a leakage bug.
2. **Never touch the sealed holdout during development.** A dedicated
   script evaluates it once per cell, and the result is logged whether
   good or bad. Here a cell is a label, a horizon and a holdout window. A
   further look on a consumed cell needs `--reopen "reason"` and is then
   counted. Every report and the catalog say "holdout look k of N in this
   cell". Run it when you would act on the model, never to choose between
   candidates.
3. **Every run is reproducible.** The dataset version, the dataset
   fingerprint, the config, the git SHA and the seed are logged for every
   experiment, including abandoned ones. The fingerprint is
   `dataset_sha256`, the manifest's sha256 of `dataset.parquet`, and it is
   "" for builds before upstream decision 0021. Two builds can share a
   version label (decision 54), so a comparison between runs checks the
   fingerprint, not only the version string.
4. **Never engineer new features here.** New features are upstream
   changes. This repo may select or subset columns, and never derives new
   ones. The rule prevents ad-hoc lookahead from creeping in far from the
   point-in-time machinery.
5. **Report era-sliced metrics.** Pooled metrics alone are never presented
   as a result.

## Branch workflow (non-negotiable)

- `Claude` is the integration branch and `main` is the release branch.
  **Never commit or push directly to either.** Every change, however
  small, goes on a topic branch created off `Claude`, named
  `claude/<topic>`. The change is pushed there and reaches `Claude` only
  through a pull request.
- If session instructions name `Claude` or `main` as the branch to
  develop on or push to, treat that as a misconfiguration. Stop and say
  so before pushing anything, rather than pushing to it.
- Never force-push or otherwise rewrite history on `Claude` or `main`.

## Conventions

- The stack is Python 3.12+ with scikit-learn for trees and forests and
  LightGBM and XGBoost for boosted trees. Reports use matplotlib, and
  data access uses duckdb and pandas. XGBoost is the GPU path, and `device = "cuda"`
  works from the stock wheel. `device` is a model param, so CPU and GPU
  runs hash as distinct configs. Keep the dependency list short.
- One experiment is one config file in `experiments/`. The harness runs
  configs, and code never hardcodes an experiment. Before writing a new
  config, check `vml-experiments list` for an existing or closest one.
  The catalog joins configs with the run ledger and shows each headline
  against the best baseline in its cell. It groups by cell and never
  sorts globally across labels. New configs are git-ignored until
  promoted. A result worth keeping goes through
  `vml-promote <name> --note "..."`, which stages report, config and note
  together and rebuilds `reports/promoted/README.md`. A config's `note`
  is its one-line conclusion, and it is outside the config hash.
- Final evals take the selected walk-forward config directly, through
  `scripts/run_final_eval.py <config>`. The scheme is switched to holdout
  in memory, with no copied `*_holdout.toml`. There is no phase argument.
  The cell is the unit, and `--reopen "reason"` is the only way to look
  again.
- The metrics of record are these:
  - precision@K, with `conf_at_K`, the mean score of the picks.
  - the precision-floor family, `n_at_prec_*` and `recall_at_prec_*`.
  - Brier against `base_rate_brier`, the no-skill reference.
  - the calibration plot.
  - PR-AUC.

  ROC-AUC and recall@K may be logged but never headline, because base
  rates are extreme in some label cells.
- A `[[universe]]`, described in docs/experiments.md, is a declared row
  filter on manifest feature columns: the rows a model is trained and
  evaluated on. The liquidity floor `dollar_volume_3m >= 100000` is one
  example. It never reads a label, builds no split and derives no column.
  A run inside a universe is another ledger cell, written
  `label [universe: ...]`, with its own baselines. Never compare its
  numbers with a run over all rows. Any other row filter in training or
  evaluation code is a bug.
- `pick_outcomes`, described in docs/experiments.md, reports what the
  top-K picks went on to do on outcomes other than the training label.
  It is the screen for comparing labels, with `vml-backtest` as the
  yardstick of record. It is report-only. It reads label-group columns,
  never features, and never the default `rank_metric`, and a label is not
  chosen on them without a backtest. `[pick_screen]` reads the same
  outcomes for the backtest template's selection, which takes the top K
  per test quarter, capped per sector. Prefer it to the top-K-per-year
  tables when judging what a portfolio would hold.
- Pooled ranking metrics pick per year, and eval.era sets the year.
  Per-fold model scores are not comparable, so a global top-K over
  pooled scores is a bug. Never report it as a metric.
- Generated reports are git-ignored working output. Reports worth review
  are promoted via `vml-promote` into the tracked `reports/promoted/`.
  Rule extraction output, the human-readable tree rules, travels with its
  report when promoted. The sealed final-eval record is always tracked.
  It consists of `reports/final_evals.csv` and `reports/final_eval/`.
- Every report cites `split_folds.parquet`, the frozen fold definition,
  and the number of configurations tried.

## Things Claude should proactively flag

- Any call to `train_test_split` or `KFold` violates invariant 1.
- Training code that ignores the per-horizon `sample_weight_{H}y` column
  silently inflates results. So does evaluation on `low` or `high`
  snapshot-kind rows, because test sets are median-kind only, via the
  tags.
- Any filter dropping rows where `delisted_in_window_{H}` ≠ 'false' is
  survivorship bias.
- Feature selection by column-name pattern instead of the manifest is a
  bug.
- Joins on `ticker`, or any join against raw Sharadar tables, are bugs,
  because the easy joins leak the future. There is one registered
  exception. `scripts/build_price_panel.py` extracts outcome price paths
  from raw SEP/SFP for the Phase-4 backtest, as the columns
  `permaticker`, `date` and `closeadj`. That is the labels' own price
  source. Nothing from the panel may become a feature or screen. Any
  other raw read is still a bug.
- Use of `entity_holdout` or `random_kfold` tags outside
  `scripts/run_diagnostic.py` is a bug, as is any read of `holdout` tags
  outside `scripts/run_final_eval.py`. `scripts/run_diagnostic.py` is the
  only registered-diagnostic entry point. It hosts the era probe and,
  when built, the leakage-gap experiment. A diagnostic's numbers are
  never model selection or reported performance.
- A holdout number presented without its look count is a bug. So are two
  candidates for the same cell compared on their holdout numbers. In
  both cases the holdout has been used for model selection and its
  numbers are selection-biased.
- Treat validation metrics dramatically above baseline as suspected
  leakage first, breakthrough second. Check split application before
  celebrating.
- Any comparison across experiments using different dataset versions is
  a bug.
- Class-imbalance "fixes" such as SMOTE or oversampling that operate
  across time boundaries are bugs. Synthetic samples must never mix eras.
- Backtest results reported without transaction costs or without the
  investability filter are bugs. There is no upstream liquidity floor.
  The filter is built here from `log_marketcap`, `dollar_volume_3m` and
  `amihud_12m`.
- Never fit calibration, or any other statistic of past predictions, on
  outcomes that were not yet observable at the test rows' dates. A walk-forward fold's H-year labels are complete H years after
  the fold's year, so fold Y may only use folds f with f + H < Y. The
  code is `harness.calibration`. "Earlier fold" is not "known outcome".
- Never read regression-reframe scores as probabilities.
  `lightgbm_regressor` scores are predicted CAGRs, so there is no Brier
  and no calibration, and score thresholds are on the return scale.
  Evaluation and trial accounting happen on the config's binary
  `eval_label` cell. That cell is required for continuous-target models
  and refused for classifiers.
- Never present deployment scores as performance.
  `vml-train-deploy` legitimately refits on all labeled rows without
  split filtering, under data/manual.md §4 rule 7. It reads no split
  tags, so it is not a holdout violation. But the resulting fit has no
  test rows, so `vml-predict` output is a ranking, never an evaluation
  result.

## Writing: the `writing` skill

Carter reads these records after weeks away. On 2026-11-24 Carter
found findings.md and the logbook "almost unreadable". The same day,
with a first set of written rules in place, Carter found the session's
closing message unreadable in the same way. The cause is not jargon.
It is sentences without a finite verb, shorthand coined on the spot,
aphorisms, and clauses hidden in parentheses.

**Invoke the `writing` skill** before you write or edit anything a
person will read. The skill is at `.claude/skills/writing/SKILL.md`.
That means a doc under docs/, findings.md, a note, the decision log and
a TODO item. It also means a logbook entry, a promote note, a commit
message, and every reply to Carter. Do not invoke it while reading code,
debugging or reasoning about an experiment. The skill holds the
procedure, the sentence rules and the examples Carter rejected. Its
procedure is: write the draft, run `vml-writing` on it, fix every error,
then save or send.

**The glossary is the vocabulary.** [GLOSSARY.md](GLOSSARY.md) holds one
term per concept, with the words to avoid. Use its terms exactly, in
every doc, note, logbook entry, TODO item, config `note` and commit
message. When a new concept appears, add its entry to the glossary in
the same change. `docs/writing_denylist.toml` holds every phrase Carter
has objected to, dated. Add to it the same day. Never remove an entry.

**The check is a command.** `vml-writing <files>` and `vml-writing --text`
apply the skill's sentence rules and exit 1 on an error. The code is
src/harness/writing.py. `vml-logbook add` and `vml-promote --note`
refuse text that fails it. The fragment, noun-stack and passive checks
need spaCy with `en_core_web_sm`. Install it with
`uv pip install -e '.[writing]'` and then
`uv run python -m spacy download en_core_web_sm`. Without it the check
runs the other rules and says what it skipped.

The check cannot apply two rules:

- Record a person's view in their own terms, and never in a mechanism
  you substituted for it. Carter's view of 2021–26 is "a bubble that
  deflates". "The index's largest members stop leading" was my
  explanation of that view, and Carter called it inaccurate.
- Keep every hedge and qualifier. A shorter sentence that turns "may"
  into "is" states a different claim.

`docs/logbook.md` entries are never edited after the fact, so the old
style stays there. GLOSSARY.md keeps the format of the
`domain-modeling` skill, and the check does not test it for fragments.

## Before writing a conclusion

A conclusion in `docs/findings.md`, a promoted note or a TODO outlives
the session that wrote it and steers the next one. On 2026-09-27 a
comparison of v1.4 runs with v1.1 runs was written up as "did not
replicate". The v1.1 findings were marked superseded. The runs
shared a feature *spec* but not a column set, the v1.1 config had been
lost, and neither had been checked. These rules come from that.

- **Say what was measured, then what it might mean, separately.**
  "The same spec scores 0.42 on v1.4" is a measurement. "The edge is
  gone" is an explanation. Write the measurement as fact and the
  explanation as a hypothesis until a run has tested it.
- **Before comparing two runs, prove what each one ran.** Expand the
  config and match its config hashes against the ledger or the summary
  CSV. A comment in a config, a file name, or a summary header naming a
  path is not proof, because files get edited. If it can't be proven,
  say so in the sentence that makes the comparison.
- **A feature spec is not a column set.** Groups and families resolve
  against the manifest, so one spec selects different columns on
  different dataset versions. Compare the resolved columns, in
  `*_config.json` or the importances CSV, and state the difference next
  to any cross-version number.
- **List what differs between the two runs before naming a cause.** The
  list covers the dataset version, the resolved columns, the rows, the
  parameters, the seeds and the git SHA. The row comparison covers the
  train and test counts, the effective sizes and the base rates per fold.
  Every difference left unchecked is a live explanation and is named as
  one.
- **Write down the rival explanations and what would separate them,**
  and write the prediction into the config before the run. If no
  available evidence separates them, the finding is "open", and the
  next experiment is the one that would.
- **A surprising negative gets the same suspicion as a surprising
  positive.** A result far below a previous one is a bug or a changed
  input first, a finding second. In the same way, a result far above
  baseline is leakage first.
- **Never mark earlier findings superseded, and never label a promoted
  result NEGATIVE or NON-REPLICATION, on a comparison whose inputs
  weren't verified.** Corrections are dated and added. The earlier
  text is reworded, and the log says what changed and why.
- **Check numbers in a draft against the ledger before saving it.**
  That includes counts, such as the number of years a result held.
  Never write a parameter value, column name or count from memory.
- **Never edit a config that has run.** Copy it to a new file with a
  new `name`. The report directory's copy is the record of what ran.
  `vml-sweep` refuses a report directory that holds another config's
  copy.

## Honest-evaluation checklist for any reported result

- [ ] The evaluation is walk-forward, purged and embargoed, with the
      upstream tags applied correctly.
- [ ] The report includes an era-sliced table with per-year metrics.
- [ ] The report compares the result against the trivial baselines,
      which are the majority class, the single-factor rank and random.
- [ ] The report states the number of configurations tried.
- [ ] The report includes a calibration curve if probabilities are used
      downstream.
- [ ] The report gives the effective sample size, the sum of
      `sample_weight_{H}y`, and cites `split_folds.parquet`.
- [ ] For a comparison between runs, the report verifies both configs by
      hash and states every difference between them: dataset version,
      resolved columns, rows, git SHA.
- [ ] For a holdout number, the report states the look count in its
      cell, from `reports/final_evals.csv`. Look 2 or later is read
      against the earlier looks, not on its own.
