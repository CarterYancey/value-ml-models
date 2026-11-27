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
- **A column may be compared with a second label column** (from
  `dataset_v1.5`, whose full-path labels carry SPY's own path):
  `fwd_3y_path_avg_return > fwd_3y_spy_path_avg_return` is the
  endpoint-free "beat SPY" of data/labels.md, and
  `fwd_3y_max_drawdown_from_entry <= fwd_3y_spy_max_drawdown_from_entry`
  "fell no further than the market". Both columns must be numeric
  label columns; a NULL on either side is unobservable; the two
  spellings of one comparison (`a > b`, `b < a`) normalize to one
  cell. Arithmetic between columns (a ratio, a difference) is not
  offered: that target is an upstream label.
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

## Pick outcomes: a yardstick shared by every label

Lift over a cell's own base rate says a label is learnable. It cannot
compare two labels, and it does not say that picking by a label beats
the market. `vml-backtest` answers that (docs/backtesting.md) and is
the yardstick of record; `pick_outcomes` is the screen in front of it,
cheap enough to put on every run:

```toml
label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2"
top_k = [20, 50]
pick_outcomes = [
  "label_3y_beat_spy",               # binary: the picks' hit rate
  "fwd_3y_excess_cagr",              # continuous: mean and median
  "fwd_3y_max_drawdown_from_entry",
  "fwd_1y_cagr >= 0",                # a label expression: hit rate
]
```

For the top-K picks of each test year the report gains a "Pick
outcomes" section, one table per outcome and K, with the statistic over
the picks beside the same statistic over all test rows of the year, and
the number of distinct stocks among the picks (a stock has up to four
median rows per test year, so 20 picks can be fewer than 20 stocks).
The same numbers are logged per fold and pooled: `pick_mean_<o>_at_K`,
`pick_median_<o>_at_K`, `all_mean_<o>`, `all_median_<o>`,
`n_stocks_at_K`. Sweeps take the same key and show the first K's
columns after the metrics of record.

Rules:

- Outcomes are columns of the manifest's `labels` group or label
  expressions over them, at a horizon no longer than the run's (a
  shorter window lies inside the run's, so it is observable on the
  run's test rows; a longer one is refused).
- Report-only. They are never model inputs (an outcome whose source
  column is also a feature is refused), they do not change a fit, and
  the run is counted in the trial-ledger cell of its own label.
  `rank_metric` stays a metric of record unless a sweep names an
  outcome key on purpose, which makes the outcome a selection target
  and has to be said in the write-up.
- The picks are precision@K's picks: unweighted, one row one pick, same
  ordering and ties. The all-rows reference is unweighted too.
- NULL outcomes are left out of a statistic, never counted as misses.
- `pick_outcomes` is part of the config hash when set, like `top_k`;
  configs without it keep their hashes. An eval config may set it, so
  `vml-eval` adds outcomes to a saved bundle without refitting.
- It reads the picks with no costs, no investability filter, equal
  weights and one entry date per row. A label that looks good here has
  earned a backtest, nothing more.

### The portfolio screen

Top K rows a year count rows, not sectors and not quarters: on
2026-09-29 they showed a forest's picks level with SPY at a third of the
average drawdown, while the uncapped portfolio of the same picks was a
utilities and REIT portfolio with a deeper drawdown than SPY's. The
screen applies the backtest template's selection rule to the test rows:

```toml
[pick_screen]
per = "quarter"        # or "year"
top_k = 10             # picks per period, by score
max_per_group = 2      # optional: at most this many per group
group_column = "sector"
```

A backtest buys from the latest completed quarter's median snapshots,
and those are the test rows, so "top 10 per test quarter, at most 2 per
sector" picks very nearly what `vml-backtest` buys under the same rule.
The report gains a "Portfolio screen" section: per test year and
pooled, the picks, the distinct stocks, the largest group and its
share, the precision on the run's label and every pick outcome; then
each group's share of the picks beside its share of the test rows.
Logged per fold and pooled as `screen_n`, `screen_precision`,
`screen_n_stocks`, `screen_top_group_share`, `screen_mean_<o>`,
`screen_median_<o>`; sweep summaries lead their pick-outcome columns
with them. The group column must be a feature column of the manifest.
Report-only and part of the config hash when set, like
`pick_outcomes`; an eval config may set it for a saved bundle. Still a
screen: equal weights, no costs, entry at the snapshot, held to the
horizon.

**Where the picks come from.** A screen may name a region of
feature-column filters (the `[[universe]]` spelling) and the report
then carries the binary pick outcome `in_region`: the share of the
picks, of their peers and of the top K that sit inside it, for
instance the stocks 40% or more below their 5-year high with a long
record of positive operating cash flow:

```toml
[pick_screen]
per = "quarter"
top_k = 10
max_per_group = 2
peer_column = "log_marketcap_rank"
region = ["dist_5y_high <= -0.4", "ocf_positive_frac_20q >= 0.9"]
```

Logged as `screen_mean_in_region`, `screen_peer_mean_in_region` and the
top-K `mean_in_region` columns; the region's filters are ANDed, a NULL
counts as outside, the columns must be feature columns of the manifest
(a label can never be a region), and the region is part of the config
hash like the rest of the screen. It says where a selection comes
from, not what it earned: a model that is asked to emphasize a region
(`[emphasis]`) is read on whether its picks moved into it.

**Same-size peers.** The all-rows reference beside every pick outcome
is the average test row, and the average test row is a small company.
Against a capitalization-weighted benchmark small stocks trail by a
wide margin in every period (on `dataset_v1.4` the smaller half of the
investable stocks by 12 to 33 points a year over three years), so any
ranking that prefers large, calm companies "beats all rows" without
choosing well among them. Give the screen a peer column and it reports
what stocks of the picks' own size did:

```toml
[pick_screen]
per = "quarter"
top_k = 10
max_per_group = 2
peer_column = "log_marketcap_rank"   # a rank column of the manifest
peer_bins = 20                        # equal-width bands (default 20)
```

A pick's peers are the test rows of its own quarter (or year) in its
own band of the column. The screen table gains a `... peers` column
after the precision and after each outcome's mean, and the metrics
`screen_peer_precision` and `screen_peer_mean_<o>`: the peers'
statistic averaged over the picks, so `screen_mean_<o> -
screen_peer_mean_<o>` is the picks' mean lead over stocks of their own
size. **That difference, not the lead over all rows, is what reads a
selection.** The column is read from the test rows as of the snapshot
and need not be a model input; it must be in the manifest's `ranks` or
`sector_ranks` (the bands are cuts of a 0..1 rank). Part of the config
hash only when set. `vml-backtest` reports print the same reference
for the buys (docs/backtesting.md, `vs_peers`).

### Two models as one ranking (`blend`)

The backtest can rank on two bundles at once (`combine = "mean_rank"`);
an eval config can do the same on the test rows, so a two-model
candidate is read on the screen before a backtest is spent on it:

```toml
name = "screen_with_momentum"
blend = ["experiments/models/factor_mom_12_2_3y_97c0f095cf48"]
```

`vml-eval <bundle> <this file>` scores every fold's test rows with the
bundle's fold model and with each blended bundle's, ranks each model's
scores within the test quarter as a share of the quarter's rows, and
takes the mean share as the score (a row one model has no score for is
ranked on the others; ties share the better rank). The bundles must
share the dataset version and scheme and cover the evaluated bundle's
folds; the label, the universe and the test rows are the evaluated
bundle's. The result is a ranking, not a probability: no Brier and no
calibration. The blended bundles' config hashes are part of the
evaluation's own hash, so every blend tried is a configuration in the
cell's trial count.

`blend_combine = "worst_rank"` takes the lowest share instead of the
mean (ties broken by the mean): a row scores high only if every model
ranks it high, the backtest's `combine = "worst_rank"`. The mode is
part of the evaluation's hash; the default, `"mean_rank"`, leaves the
hashes of earlier blends unchanged.

### One model screened by another (`[[gate]]`)

An eval config can keep only the test rows another walk-forward
bundle scores in its top (or bottom) share of the test quarter, and
rank those by the evaluated bundle:

```toml
name = "huber_without_forest_bottom"
[[gate]]
bundle = "experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d"
keep = "top"      # or "bottom" (e.g. a downside model's least likely)
share = 0.5
```

Gated rows are moved below every kept row (in their own order), so
top-K, the screen and the threshold tables pick from the kept rows; the
report states the average share kept. Same checks as `blend` (dataset
version, scheme, folds); the gates (bundle hash, keep, share) are part
of the evaluation's hash. A ranking: no Brier, no calibration.

### Selection by score

With `score_thresholds` and `pick_outcomes` both set, the report gains
"Selection by score": for every threshold, per test year and pooled,
how many rows and distinct stocks scored at or above it, their
precision and what they went on to do (`thr_mean_<o>_at_<t>`,
`thr_median_<o>_at_<t>`, `thr_n_stocks_at_<t>`, `thr_years_at_<t>`). A
year with no row at the bar is a year in cash and keeps its row. The
mean is what an equal-weighted portfolio of those rows earns; the
median is shown beside it. Read the years before the pooled row, and a
threshold as a probability only on a calibrated run
(`calibration = "isotonic"`).

### Calibration across years (`mean_score`, `year_balance`)

Every probabilistic run reports `mean_score` (the weighted mean score
of a fold's test rows) beside `base_rate` in the era table, and in its
pooled metrics `year_calib_corr` (the correlation across test years of
the two) and `year_calib_mae` (their mean absolute gap). A threshold
rule ("every stock over X") buys fewer stocks in a bad year only if
`year_calib_corr` is well above zero; the ranks-only forests of cell C
are near −0.6 (docs/notes/2026-11-23-calibration-plan.md).

`year_balance = true` (a config field, hashed when set) reweights each
fold's training rows so that every snapshot year carries the pooled
positive share, each year keeping its total weight and the mandatory
sample weights staying inside it: the model cannot take particular
past years' market level as its prior. Binary labels only; applied in
walk-forward fits, backtest refits and deployment refits alike.

## Universe: the rows a model is trained and evaluated on

```toml
[[universe]]
column = "dollar_volume_3m"
op = ">="
value = 100000
# universe_scope = "test"   # train on every row, evaluate inside
```

A `[[universe]]` is a row filter on feature columns (the backtest's
`[[investability]]` spec: `column`, `op`, `value`; several entries are
ANDed; a NULL fails). By default it applies to train and test rows:
the model learns from, and is measured on, the stocks it would be
asked about. `universe_scope = "test"` trains on everything and
evaluates inside the universe: the reference arm for a training-time
floor, and what an eval config's `universe` does to a saved bundle
(`vml-eval`; refused for a bundle that has its own).

What it is and is not:

- **Not a split.** Upstream tags still decide which rows are train and
  which are test; the filter only leaves rows out, so the purge and
  embargo hold for the rows that remain (invariant 1).
- **Not a feature.** It reads a manifest feature column as of the
  snapshot and derives nothing (invariant 4). Labels and weights
  cannot be screened on.
- **Another population, so another cell.** Base rates, baselines and
  picks inside a universe are not comparable with a run over all rows.
  The run is logged under `label [universe: ...]`; its report states
  the configurations tried in that cell and against the label in any
  universe. Baselines have to be run inside the universe too. The
  sealed holdout is per label whatever the universe: a look inside a
  universe consumes the label's cell.
- **Part of the model, all the way to inference.** It is in the
  config hash and the bundle; `vml-train-deploy` refits inside it;
  `vml-predict` ranks only the inference rows inside it (a combined
  run, the rows inside every model's) and the sidecar says how many
  rows were left out; the backtest's year-end refits stay inside it,
  and a backtest refuses a bundle trained inside a universe unless
  its own `[[investability]]` or `[[filters]]` carry the same
  filters. The universe's columns must be in the inference data.
- **A rank floor is one line.** `dollar_volume_3m_rank >= 0.2` is as
  valid a filter as the dollar amount, era-neutral by construction
  (a within-quarter rank; pooled over the cross-section at
  inference), and needs nothing upstream.
- `sample_weight_{H}y` is the upstream uniqueness weight and is not
  recomputed for the rows left out.
- One universe per sweep file (top-level `[[universe]]`), so a sweep's
  runs are compared inside one population.

## Emphasis: a region of the training rows counted more

```toml
[emphasis]
factor = 3.0
region = ["dist_5y_high <= -0.4", "ocf_positive_frac_20q >= 0.9"]
```

An `[emphasis]` multiplies the mandatory sample weights of the training
rows inside a region by `factor`. The region is a list of filters over
feature columns, in the universe's spelling (`column op value` as one
string, or a `column`/`op`/`value` table), ANDed; a NULL fails, so a
row with a NULL in a region column is not emphasized. Introduced in
decision 78.6 for the rare region Carter described: stocks with a
strong record that have fallen hard. A forest given every row chooses
its splits where the gain is largest over the whole population, and
the columns that separate a small region never win a split; a
universe restricted to the region starves the fit in the early folds
(fold 2006 of the fallen universe has an effective size of 20).
Emphasis keeps every row and the common structure, and lets the region
decide more of the splits.

What it is and is not:

- **A weight, not a filter.** Every training row stays in the fit; no
  row's label or features change. The uniqueness weights keep their
  ratios inside and outside the region, and a `year_balance` is
  applied first. The effective sample size reported is Σ of the
  mandatory weights, unchanged; the report states the region's share
  of each fold's training weight before the factor
  (`emphasis_train_share`).
- **Training only.** Test rows are never reweighted, so every metric
  is measured exactly as without emphasis. A region may read feature
  columns the manifest declares, never a label or a weight (the same
  rule as a universe: the weight a row gets depends on what was known
  at the snapshot, never on its outcome).
- **Part of the model.** It is in the config hash and the bundle;
  `vml-train-deploy` and the backtest's year-end refits apply it. A
  factor of 1 is refused (drop the table instead).
- **Not a universe and not a cell.** The run is counted in its label's
  cell like any run over all rows, and its numbers are comparable with
  one; the same cell with `universe_scope = "all"` on the region is the
  starved version of the same idea.
- One emphasis per sweep file (top-level `[emphasis]`), like the
  universe; sweep over factors with one file per factor.

## Boolean feature columns

The upstream flags (`negative_equity`, `two_year_loss`, the nine
`piotroski_*` signals, ...) are nullable booleans. They are handed to
every model as floats, True 1.0 and False 0.0, NULL kept as NaN
("unknown" is not "failed": data/features.md). This changes how a
value is stored, not what it says, and reads no other row or column.
Date columns (`fund_datekey`, ...) are still not model inputs.

## `sector` as a model input

```toml
[features]
groups = ["ranks"]
columns = ["sector"]
```

`sector` is the one string column a model may take. It is handed to
every model as eleven 0/1 indicator columns, one per sector of the
upstream scheme (`sector=Technology`, ...), NULL kept as NULL in all
of them (`harness.dataset.CATEGORICAL_FEATURES`, `feature_matrix`).
The vocabulary is a fixed list in the code, not learned from a frame:
the train rows, every test fold, a backtest cross-section and an
inference frame get the same columns, and a value outside the list is
an error. Like the flags, a per-row recoding that reads no other row
or column (invariant 4). A bundle keeps the manifest name (`sector`);
importances and tree rules are indexed by the indicator columns.

Two things to keep in mind when reading a run that uses it:

- **It is a current-state column** (data/features.md,
  "Classification"): a reclassified company's whole history carries
  today's sector, and a delisted company's froze at delisting. The
  model sees a mild form of the future in it. The run's report says
  so. Compare against the same run without the column, on the screen
  and on the sector shares of the picks, before reading anything
  into a difference.
- The other classification columns are refused: `scalemarketcap` is
  today's size bucket stamped on a firm's whole history (it tells a
  2005 row how large the company became), and `industry` and
  `famaindustry` are current-state labels fine enough to name single
  companies.

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

**What ran is recorded with the results, not by reference.** A sweep
copies its TOML, as written, to
`reports/sweeps/<name>/<name>_config.toml` before the first run, and
every run (in a sweep or through `vml-run`) writes
`<run>_config.json` beside its report: the full config its hash is
taken over, and the feature columns its feature spec resolved to on
that dataset version. `vml-run` also copies its TOML there.
`vml-promote` carries the sweep copy along as `config_as_run.toml`.
To change a sweep that has run, copy it to a new file with a new
`name`: `vml-sweep` refuses a report directory that holds the copy of
a different sweep (a changed `note` is not a different sweep). Compare
runs on their resolved columns: one feature spec selects different
columns on different dataset versions.

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
