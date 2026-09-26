# Experiments: configs, labels, models, sweeps

How to write what the harness runs. For the commands see the
[README](../README.md); for the dataset contract see
[data/manual.md](../data/manual.md).

## Configs

- One experiment = one TOML config file in `experiments/`, naming the
  dataset version, scheme/fold(s), label column, feature selection,
  model + params, and seed. Two fields are derived when omitted:
  `horizon_years` comes from the label's `{H}y` token
  (`label_3y_beat_spy` → 3; stating both requires agreement), and `name`
  defaults to `{model}_{features}_{label}_{content-hash}` — so a copied
  config with edited values can't silently overwrite the original's
  reports and bundles through a forgotten name.
- Features are selected hierarchically with a `[features]` table:
  `groups` (manifest groups), `families` (registry families from
  data/features.md — bare `"valuation"` takes every group's variant,
  `"ranks/valuation"` just that group's), and `columns` (individual
  columns; group/family membership is implied). The selection is their
  union, minus `exclude_columns` / `exclude_families`. Every exclusion
  must remove something actually selected — blacklisting a child whose
  parent was never selected is an error, as is naming a column the
  manifest doesn't declare, so typos can't silently keep or drop a
  feature. Sweep configs take the same table (one `[features]` for every
  run, or a `[[features]]` array as the sweep's feature axis), their
  `[[cells]]` entries infer `horizon_years` from the label the same way,
  and a sweep's `name` defaults to
  `{model}_sweep_{features}_{labels}_{content-hash}` — a copied sweep
  file with edited values gets fresh run names and a fresh
  `reports/sweeps/` directory too.
  The legacy top-level keys (`feature_groups`,
  `feature_columns` whitelist, `exclude_feature_columns`) keep working —
  also in sweep configs (top-level or per `[[feature_sets]]` entry, as
  `exclude`) — but can't be mixed with `[features]` in one config.
- The harness runs configs; code never hardcodes an experiment. Every run
  appends dataset version + config hash + git SHA + seed + metrics to
  `experiments/results.csv`, including failed/abandoned runs.
- Evaluation reports (era-sliced metrics, high-confidence-picks profile,
  calibration; `split_folds.parquet` citation and effective sample sizes
  in the appendix) are written to `reports/`. Generated reports are
  **git-ignored working output** — promote the ones worth keeping (see
  [workflow.md](workflow.md)).

- Training and evaluation are distinct tasks: `vml-run` saves the fitted
  per-fold models as a bundle under `experiments/models/` (git-ignored),
  and `vml-eval` re-scores a saved bundle under an eval config — metric
  parameters only (`top_k`, `score_thresholds`); the dataset version,
  scheme, folds, label, and features stay pinned by the bundle. Each
  evaluation is logged to `experiments/results.csv` under its own config
  hash, so trying many evaluation criteria still counts in the trial
  ledger.

## Derived labels

Anywhere a config names a label (`label`, `eval_label`, a sweep's
`[[cells]]`) it may instead give a **label expression** over the
manifest's `labels` columns, evaluated on the fly — so a new threshold
never needs a dataset rebuild (data/manual.md §3):

```toml
label = "fwd_3y_cagr >= 0.12"                              # a custom rung
label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"   # compounded without a crash
label = "fwd_3y_max_drawdown_from_entry < 0.2"             # never down >20% from entry
label = "fwd_3y_excess_cagr >= 0.08"                       # beat SPY by 8 pts
label = "label_3y_beat_spy == true & fwd_3y_cagr >= 0"     # stored binaries combine too
label = "fwd_3y_excess_cagr > 0 & fwd_1y_max_drawdown_from_entry < 0.1"   # mixed horizons
label = "(fwd_3y_cagr >= 0.15 | fwd_3y_excess_cagr >= 0.05) & fwd_3y_max_drawdown < 0.4"
```

- Grammar: conditions `column OP literal`, `OP` ∈ `>= > <= < == !=`,
  joined by `&` and `|` (`&` binds tighter; parentheses group);
  literals are numbers, or `true`/`false` for boolean columns. Parsed,
  never `eval`'d.
- Columns must be in the manifest `labels` group (outcomes, never
  features). **Mixed horizons are allowed and the longest governs**:
  every window starts at the snapshot, so a `1y & 3y` label's window
  *is* the 3y window — `horizon_years` is inferred as 3, and the 3y
  split tags, `sample_weight_3y` and fold calendar apply to the whole
  label (purge/embargo for the 1y part follow a fortiori). The report
  says so when a label mixes horizons. Drawdown columns exist from `dataset_v1.3` — set
  `min_dataset_version = "1.3"` (data/versions.md); a sweep states
  `min_dataset_version` once and every expanded run carries it.
  Exemplars: `experiments/tree_depth3_3y_survive_dd30.toml`,
  `experiments/lgbm_3y_compounder_no_crash.toml`,
  `experiments/sweeps/lgbm_drawdown_rungs_3y.toml`.
- NULL propagates, under `|` too: a row with any referenced column
  NULL has a NULL (unobservable) label, never False (within a horizon
  all columns are NULL together, so the rows where three-valued `OR`
  would differ are outside the label's window anyway).
- Every label is a function of its own row, so the upstream purge and
  embargo cover it exactly as they cover a stored label. Cross-sectional
  outcome ranks ("top decile of the cohort") are deliberately not
  offered: a peer's window can close up to a quarter later than the
  row's own, eroding the embargo — that would be an upstream label.
  `beat_spy` / `fwd_{H}_excess_cagr` thresholds are the era-neutral
  targets.
- Expressions are normalized to a sorted sum of products (canonical
  literals, duplicate conditions/clauses dropped), so one target is one
  results-ledger cell whatever spelling or bracketing a config used;
  `fwd_3y_cagr >= 0.1` reproduces `label_3y_cagr_ge_10` exactly (inclusive
  thresholds) but is a separate ledger cell, since the cell is the label
  string.

## Models

`model.name` in a config selects from the registry: the baselines
(`majority_class`, `rank_factor`, `random_ranking`), the Phase-1
`decision_tree` (full sklearn regularization surface: `max_depth`,
`min_samples_leaf`, `max_leaf_nodes`, `ccp_alpha`, …), and the Phase-3
`random_forest` and `lightgbm`. All fit with the horizon's mandatory
`sample_weight_{H}y` and handle NULLs natively — no imputation anywhere.

**Precision-first tuning** (the core strategy: extremely high precision,
even at low recall):

- every classifier takes `class_weight`: `"balanced"` (recall-friendly)
  or a positive float `w` → positives weighted `w` vs. 1 for negatives —
  `w < 1` makes false positives expensive, so models only call very pure
  regions positive;
- `precision_targets = [0.75, 0.9]` in any config records
  `recall_at_prec_*` / `thr_for_prec_*` / `n_at_prec_*`: the best recall
  (and the score threshold and pick count achieving it) subject to each
  precision floor, per fold, per era, and pooled;
- a sweep's summary ranks by `rank_metric` (default: recall at the first
  precision floor), so "which config recalls most at ≥ 90% precision?"
  is answered directly.

## Sweeps

`experiments/sweeps/*.toml` declare grids instead of single runs:
`[[cells]]` (horizon + label pairs — multiple label columns in one file),
`[grid]` (model-param ranges, cartesian product), `[[sets]]` (whole
model-param dictionaries, each taken as a unit), optional
`[[feature_sets]]` and `seeds`. `vml-sweep` trains exactly like
`vml-run` does — each expanded config goes through the same runner,
fitting fresh per-fold models and evaluating them on that fold's test
year — so a 32-point sweep is 32 full training runs, logged to
`experiments/results.csv` (failures included, they count as trials),
STANDARD split access only, with per-run reports under
`reports/sweeps/<name>/` plus a ranked summary (`_summary.md` / `.csv`).
The one difference from `vml-run`: fitted models are discarded after
scoring rather than saved as bundles (pass `--save-models` to keep
them) — the intended flow is sweep → read the summary → re-run the
winning config through `vml-run` for its bundle.
Expansion is capped by `max_runs` (default 200) so trial-count inflation
is always an explicit decision. The summary's ranking is model selection
on walk-forward folds — candidates for the sealed holdout, never final
results.

`[[sets]]` is the follow-up to a wide `[grid]` search: paste its top
candidates in as whole parameter dictionaries and re-run them across
seeds, feature sets, label cells, or a further `[grid]` / `[random]`
over the parameters the sets leave open (sets cross with every other
axis). Either
TOML spelling works — one inline table per line, or an array of tables:

```toml
sets = [
  {n_estimators = 300, num_leaves = 7,  learning_rate = 0.05, reg_lambda = 1.0},
  {n_estimators = 100, num_leaves = 15, learning_rate = 0.05, reg_lambda = 5.0},
]

[[sets]]            # equivalent
n_estimators = 300
num_leaves = 7
learning_rate = 0.05
reg_lambda = 1.0
```

A parameter may appear in only one of `[model]`, `[grid]`, `[random]`,
`[[sets]]` (a collision is a config error, not a silent override). Runs
are named `set<i>` by position; the summary CSV carries the full
dictionary in its `set_params` column and the markdown header lists
every set. Exemplar:
`experiments/sweeps/lgbm_candidate_sets_3y.toml` (candidate sets × a
`class_weight` grid × three seeds).

**Several seeds → one report per candidate.** When `seeds` lists more
than one value, the sweep reports per *candidate* (cell × feature set ×
parameter set × grid point × random draw — everything but the seed)
rather than per run: `reports/sweeps/<name>/<candidate>.md` gives, for
every pooled metric and for each test year, the `n` / `mean` / `std` /
`min` / `max` / 95% t-interval across seeds, plus the per-seed values.
The summary ranks candidates by the **mean** of `rank_metric` across
seeds with its std / min / 95%-CI lower bound beside it
(`_summary_seeds.csv` has every metric's statistics; `_summary.csv`
still lists every run), and the per-seed run reports move to
`reports/sweeps/<name>/seeds/`. A candidate is only as good as its
worst seed — read `_min` before `_mean`; with two or three seeds the
interval is wide by construction, which is the honest width.
