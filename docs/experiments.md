# Experiments: configs, labels, models, sweeps

This document says how to write what the harness runs. The commands are
in the [README](../README.md). The dataset contract is in
[data/manual.md](../data/manual.md).

## Configs

- One experiment is one TOML config file in `experiments/`. The file
  names the dataset version, the scheme and folds, the label column,
  the feature selection, the model with its params, and the seed.
- The harness derives two fields when a config omits them. `horizon_years` comes
  from the label's `{H}y` token, so `label_3y_beat_spy` gives 3. If a
  config states both, they must agree. The default `name` is
  `{model}_{features}_{label}_{content-hash}`. A copied config with
  edited values therefore cannot overwrite the original's reports and
  bundles through a forgotten name.
- A config selects features hierarchically with a `[features]` table.
  The table has three keys. `groups` names manifest groups. `families`
  names registry families from data/features.md. A bare `"valuation"`
  takes every group's variant and `"ranks/valuation"` takes only that
  group's. Under `columns` a config lists individual columns. Naming a column
  implies its group and family. The selection is the union of the three, minus
  `exclude_columns` and `exclude_families`.
- Every exclusion must remove something the selection includes.
  Excluding a child whose parent is not in the selection is an error. Naming a column the
  manifest does not declare is an error too. A typo therefore cannot
  keep or drop a feature without notice.
- Sweep configs take the same table. One `[features]` applies to every
  run, or a `[[features]]` array becomes the sweep's feature axis. The
  sweep's `[[cells]]` entries infer `horizon_years` from the label the
  same way. A sweep's `name` defaults to
  `{model}_sweep_{features}_{labels}_{content-hash}`, so a copied sweep
  file with edited values gets fresh run names and a fresh
  `reports/sweeps/` directory too.
- The legacy top-level keys still work: `feature_groups`, the
  `feature_columns` whitelist and `exclude_feature_columns`. They also
  work in sweep configs, at the top level or per `[[feature_sets]]`
  entry as `exclude`. A config cannot mix them with `[features]`.
- The harness runs configs. Code never hardcodes an experiment. Every
  run appends the dataset version, the config hash, the git SHA, the
  seed and the metrics to `experiments/results.csv`. It appends failed
  and abandoned runs too.
- The harness writes evaluation reports to `reports/`. A report holds the
  era-sliced metrics, the high-confidence-picks profile and the
  calibration. Its appendix cites `split_folds.parquet` and gives the
  effective sample sizes. Generated reports are **git-ignored working
  output**. Promote the ones worth keeping, as [workflow.md](workflow.md)
  describes.
- Training and evaluation are distinct tasks. `vml-run` saves the
  fitted per-fold models as a bundle under `experiments/models/`, which
  is git-ignored. `vml-eval` re-scores a saved bundle under an eval
  config. An eval config holds metric parameters only, such as `top_k`
  and `score_thresholds`. The dataset version, scheme, folds, label and
  features stay pinned by the bundle. `vml-eval` logs each evaluation to
  `experiments/results.csv` under its own config hash, so trying many
  evaluation criteria still counts in the trial ledger.

## Derived labels

Anywhere a config names a label it may instead give a **label
expression** over the manifest's `labels` columns. The places are
`label`, `eval_label` and a sweep's `[[cells]]`. The loader evaluates
the expression on the fly, so a new threshold never needs a dataset
rebuild. The rule is in data/manual.md §3. Some examples follow:

```toml
label = "fwd_3y_cagr >= 0.12"                              # a custom rung
label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"   # compounded without a crash
label = "fwd_3y_max_drawdown_from_entry < 0.2"             # never down >20% from entry
label = "fwd_3y_excess_cagr >= 0.08"                       # beat SPY by 8 pts
label = "label_3y_beat_spy == true & fwd_3y_cagr >= 0"     # stored binaries combine too
label = "fwd_3y_excess_cagr > 0 & fwd_1y_max_drawdown_from_entry < 0.1"   # mixed horizons
label = "(fwd_3y_cagr >= 0.15 | fwd_3y_excess_cagr >= 0.05) & fwd_3y_max_drawdown < 0.4"
```

- The grammar is this. A condition is `column OP literal`, where `OP`
  is one of `>= > <= < == !=`. `&` and `|` join conditions. `&` binds
  tighter, and parentheses group. A literal is a number, or `true` or
  `false` for a boolean column. The loader parses the expression and
  never passes it to `eval`.
- Columns must be in the manifest `labels` group. They are outcomes,
  never features.
- **Mixed horizons are allowed and the longest governs.** Every window
  starts at the snapshot, so a `1y & 3y` label's window *is* the 3y
  window. The loader infers `horizon_years` as 3. The 3y split tags,
  `sample_weight_3y` and the 3y fold calendar apply to the whole label.
  The purge and embargo for the 1y part follow a fortiori. The report
  says so when a label mixes horizons.
- Drawdown columns exist from `dataset_v1.3`. Set
  `min_dataset_version = "1.3"` for them (data/versions.md). A sweep
  states `min_dataset_version` once and every expanded run carries it.
  The exemplars are `experiments/tree_depth3_3y_survive_dd30.toml`,
  `experiments/lgbm_3y_compounder_no_crash.toml` and
  `experiments/sweeps/lgbm_drawdown_rungs_3y.toml`.
- NULL propagates, under `|` too. A row with any referenced column NULL
  has a NULL label, which means unobservable, and never False. Within a
  horizon all columns are NULL together, so the rows where a
  three-valued `OR` would differ are outside the label's window anyway.
- Every label is a function of its own row, so the upstream purge and
  embargo cover it exactly as they cover a stored label. The harness
  deliberately does not offer cross-sectional outcome ranks, such as
  "top decile of the cohort". A peer's window can close up to a quarter later than the
  row's own and would erode the embargo. Such a label belongs upstream.
  The era-neutral targets are `beat_spy` and the `fwd_{H}_excess_cagr`
  thresholds.
- The loader normalizes expressions to a sorted sum of products with
  canonical literals, and drops duplicate conditions and clauses. One
  target is
  therefore one results-ledger cell, whatever spelling or bracketing a
  config used. `fwd_3y_cagr >= 0.1` reproduces `label_3y_cagr_ge_10`
  exactly, since thresholds are inclusive. It is still a separate
  ledger cell, because the cell is the label string.

## Pick outcomes: a yardstick shared by every label

Lift over a cell's own base rate says a label is learnable. It cannot
compare two labels, and it does not say that picking by a label beats
the market. `vml-backtest` answers that question (docs/backtesting.md)
and is the yardstick of record. `pick_outcomes` is the screen in front
of it, and it is cheap enough to put on every run:

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
outcomes" section, with one table per outcome and K value. Each table
shows the statistic over the picks beside the same statistic over all
test rows of the year. It also shows the number of distinct stocks
among the picks. A
stock has up to four median rows per test year, so 20 picks can be
fewer than 20 stocks. The harness logs the same numbers per fold and
pooled as `pick_mean_<o>_at_K`, `pick_median_<o>_at_K`, `all_mean_<o>`,
`all_median_<o>` and `n_stocks_at_K`. Sweeps take the same key and show
the first K's columns after the metrics of record.

The rules are these:

- Outcomes are columns of the manifest's `labels` group, or label
  expressions over them, at a horizon no longer than the run's. A
  shorter window lies inside the run's, so it is observable on the
  run's test rows. The harness refuses a longer one.
- Pick outcomes are report-only. They are never model inputs, and the
  harness refuses an outcome whose source column is also a feature. They
  do not change a fit, and the ledger counts the run in the cell of its
  own label. `rank_metric` stays a metric of record unless a sweep names
  an outcome key on purpose. That makes the outcome a selection target,
  and the write-up has to say so.
- The picks are precision@K's picks: unweighted, one row one pick, with
  the same ordering and ties. The all-rows reference is unweighted too.
- A statistic leaves NULL outcomes out and never counts them as
  misses.
- `pick_outcomes` is part of the config hash when it is set, like
  `top_k`. Configs without it keep their hashes. An eval config may set
  it, so `vml-eval` adds outcomes to a saved bundle without refitting.
- The screen reads the picks with no costs, no investability filter,
  equal weights and one entry date per row. A label that looks good
  here has earned a backtest, nothing more.

### The portfolio screen

Top K rows a year count rows, not sectors and not quarters. On
2026-09-29 they showed a forest's picks level with SPY at a third of
the average drawdown. The uncapped portfolio of the same picks was a
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
and those are the test rows. "Top 10 per test quarter, at most 2 per
sector" therefore picks very nearly what `vml-backtest` buys under the
same rule. The report gains a "Portfolio screen" section. Per test year
and pooled, it lists the picks, the distinct stocks, and the largest
group with its share. It also lists the precision on the run's label
and every pick outcome. After that it lists each group's share of the
picks beside its share of the test rows. The harness logs the metrics per fold and pooled as
`screen_n`, `screen_precision`, `screen_n_stocks`,
`screen_top_group_share`, `screen_mean_<o>` and `screen_median_<o>`.
Sweep summaries lead their pick-outcome columns with them. The group
column must be a feature column of the manifest. The screen is
report-only and is part of the config hash when it is set, like
`pick_outcomes`. An eval config may set it for a saved bundle. It is
still a screen: equal weights, no costs, entry at the snapshot, held to
the horizon.

**Same-size peers put the all-rows reference in context.** The
all-rows reference beside every pick outcome is the average test row,
and the average test row is a small company. Against a
capitalization-weighted benchmark small stocks lag by a wide margin
in every period. On `dataset_v1.4` the smaller half of the investable
stocks was 12 to 33 points a year behind over three years. Any ranking
that prefers large, calm companies therefore "beats all rows" without
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

A pick's peers are the test rows of its own quarter or year in its own
band of the column. The screen table gains a `... peers` column after
the precision and after each outcome's mean. The metrics
`screen_peer_precision` and `screen_peer_mean_<o>` are the peers'
statistic averaged over the picks. `screen_mean_<o> -
screen_peer_mean_<o>` is therefore the picks' mean lead over stocks of
their own size. **That difference, and not the lead over all rows, is
what reads a selection.** The screen reads the column from the test
rows as of the snapshot, and the column need not be a model input. It must be in the
manifest's `ranks` or `sector_ranks`, because the bands are cuts of a
0..1 rank. It is part of the config hash only when it is set.
`vml-backtest` reports print the same reference for the buys, as
`vs_peers` in docs/backtesting.md.

### Two models as one ranking (`blend`)

The backtest can rank on two bundles at once with
`combine = "mean_rank"`. An eval config can do the same on the test
rows. A two-model candidate is therefore read on the screen before a
backtest is spent on it:

```toml
name = "screen_with_momentum"
blend = ["experiments/models/factor_mom_12_2_3y_97c0f095cf48"]
```

`vml-eval <bundle> <this file>` scores every fold's test rows with the
bundle's fold model and with each blended bundle's fold model. It ranks
each model's scores within the test quarter as a share of the quarter's
rows, and takes the mean share as the score. A row that one model has
no score for takes its rank from the others. Ties share the better rank. The
bundles must share the dataset version and scheme and cover the
evaluated bundle's folds. The label, the universe and the test rows are
the evaluated bundle's. The blended score is a ranking and not a
probability, so the report has no Brier score and no calibration. The
blended bundles' config
hashes are part of the evaluation's own hash, so every blend tried is a
configuration in the cell's trial count.

`blend_combine = "worst_rank"` takes the lowest share instead of the
mean, with ties broken by the mean. A row then scores high only if
every model ranks it high. This is the backtest's
`combine = "worst_rank"`. The mode is part of the evaluation's hash.
The default, `"mean_rank"`, leaves the hashes of earlier blends
unchanged.

### One model screened by another (`[[gate]]`)

An eval config can keep only the test rows that another walk-forward
bundle scores in its top or bottom share of the test quarter. It then
ranks those rows by the evaluated bundle:

```toml
name = "huber_without_forest_bottom"
[[gate]]
bundle = "experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d"
keep = "top"      # or "bottom" (e.g. a downside model's least likely)
share = 0.5
```

The gate puts gated rows below every kept row, in their own order.
Top-K,
the screen and the threshold tables therefore pick from the kept rows.
The report states the average share kept. The checks are the same as
for `blend`: dataset version, scheme and folds. The gates are part of
the evaluation's hash, through the bundle hash, `keep` and `share`. The
result is a ranking, so there is no Brier and no calibration.

### Selection by score

With `score_thresholds` and `pick_outcomes` both set, the report gains
a "Selection by score" section. For every threshold, per test year and
pooled, it gives how many rows and distinct stocks scored at or above
the threshold. It gives their precision and what they went on to do. The
metrics
are `thr_mean_<o>_at_<t>`, `thr_median_<o>_at_<t>`,
`thr_n_stocks_at_<t>` and `thr_years_at_<t>`. A year with no row at the
bar is a year in cash and keeps its row. The mean is what an
equal-weighted portfolio of those rows earns, and the report shows the
median beside it. Read the years before the pooled row. Read a threshold as a
probability only on a calibrated run, which means
`calibration = "isotonic"`.

### Calibration across years (`mean_score`, `year_balance`)

Every probabilistic run reports `mean_score` beside `base_rate` in the
era table. `mean_score` is the weighted mean score of a fold's test
rows. The pooled metrics add `year_calib_corr`, the correlation of the
two across test years, and `year_calib_mae`, their mean absolute gap. A
threshold rule such as "every stock over X" buys fewer stocks in a bad
year only if `year_calib_corr` is well above zero. The ranks-only
forests of cell C are near −0.6
(docs/notes/2026-11-23-calibration-plan.md).

`year_balance = true` is a config field, hashed when it is set. It
reweights each fold's training rows so that every snapshot year carries
the pooled positive share. Each year keeps its total weight, and the
mandatory sample weights stay inside it. The model therefore cannot
take particular past years' market level as its prior. It applies to
binary labels only. The harness applies it in walk-forward fits,
backtest refits and deployment refits alike.

## Universe: the rows a model is trained and evaluated on

```toml
[[universe]]
column = "dollar_volume_3m"
op = ">="
value = 100000
# universe_scope = "test"   # train on every row, evaluate inside
```

A `[[universe]]` is a row filter on feature columns. It uses the
backtest's `[[investability]]` spec: `column`, `op` and `value`.
Several entries are ANDed, and a NULL fails. By default the universe
applies to train and test rows. The model then learns from, and is
measured on, the stocks it would be asked about.
`universe_scope = "test"` trains on everything and evaluates inside the
universe. That is the reference arm for a training-time floor. It is
also what an eval config's `universe` does to a saved bundle through
`vml-eval`. `vml-eval` refuses it for a bundle that has its own
universe.

What a universe is and is not:

- **A universe is not a split.** Upstream tags still decide which rows
  are train and which are test. The filter only leaves rows out, so the
  purge and embargo hold for the rows that remain (invariant 1).
- **A universe is not a feature.** It reads a manifest feature column
  as of the snapshot and derives nothing (invariant 4). Labels and
  weights cannot be screened on.
- **A universe is another population, so it is another cell.** Base
  rates, baselines and picks inside a universe are not comparable with
  a run over all rows. The ledger lists the run under
  `label [universe: ...]`. Its report states the configurations tried
  in that cell and against the label in any universe. You have to run
  the baselines inside the universe too. The sealed holdout is per label whatever the universe,
  so a look inside a universe consumes the label's cell.
- **A universe is part of the model, all the way to inference.** It is
  in the config hash and the bundle. `vml-train-deploy` refits inside
  it. `vml-predict` ranks only the inference rows inside it, and a
  combined run ranks the rows inside every model's universe. The
  sidecar says how many rows were left out. The backtest's year-end
  refits stay inside it. A backtest refuses a bundle trained inside a
  universe unless its own `[[investability]]` or `[[filters]]` carry
  the same filters. The universe's columns must be in the inference
  data.
- **A rank floor is one line.** `dollar_volume_3m_rank >= 0.2` is as
  valid a filter as the dollar amount, and it needs nothing upstream.
  It is era-neutral by construction, because it is a within-quarter
  rank, pooled over the cross-section at inference.
- `sample_weight_{H}y` is the upstream uniqueness weight, and the
  harness does not recompute it for the rows left out.
- A sweep file takes one universe, as a top-level `[[universe]]`, so a
  sweep's runs are compared inside one population.

## Boolean feature columns

The upstream flags are nullable booleans. They include
`negative_equity`, `two_year_loss` and the nine `piotroski_*` signals.
The harness hands them to every model as floats, with True as 1.0 and
False as 0.0. It keeps NULL as NaN, because an unknown value is not a
failed one (data/features.md). The recoding changes only how a value
is stored, and it reads no other row or column. Date columns such as
`fund_datekey` are still not model inputs.

## `sector` as a model input

```toml
[features]
groups = ["ranks"]
columns = ["sector"]
```

`sector` is the one string column a model may take. The harness hands
it to every model as eleven 0/1 indicator columns, one per sector of
the upstream scheme, such as `sector=Technology`. It keeps NULL as NULL
in all of them. The code is `harness.dataset.CATEGORICAL_FEATURES` and
`feature_matrix`. The vocabulary is a fixed list in the code and is not
learned from a frame. The train rows, every test fold, a backtest
cross-section and an inference frame therefore get the same columns. A
value outside the list is an error. Like the flags, this is a per-row
recoding that reads
no other row or column (invariant 4). A bundle keeps the manifest name
`sector`. Importances and tree rules use the indicator columns as
their index.

Keep two things in mind when you read a run that uses it:

- **`sector` is a current-state column.** The "Classification"
  section of data/features.md explains this. A reclassified company's
  whole history carries today's sector, and a delisted company's sector
  froze at delisting. The model sees a mild form of the future in it.
  The run's report says so. Before you read anything into a difference,
  compare against the same run without the column. Compare on the
  screen and on the sector shares of the picks.
- The harness refuses the other classification columns. `scalemarketcap` is
  today's size bucket stamped on a firm's whole history, so it tells a
  2005 row how large the company became. `industry` and `famaindustry`
  are current-state labels fine enough to name single companies.

## Models

A config's `model.name` selects a model from the registry. The registry holds
the baselines `majority_class`, `rank_factor` and `random_ranking`, the
Phase-1 `decision_tree`, and the Phase-3 `random_forest` and
`lightgbm`. The decision tree exposes the full sklearn regularization
surface, including `max_depth`, `min_samples_leaf`, `max_leaf_nodes`
and `ccp_alpha`. All models fit with the horizon's mandatory
`sample_weight_{H}y` and handle NULLs natively. There is no imputation
anywhere.

**Precision-first tuning is the core strategy**: extremely high
precision, even at low recall. Three mechanisms serve it:

- Every classifier takes `class_weight`. `"balanced"` is
  recall-friendly. A positive float `w` weights positives `w` against 1
  for negatives. With `w < 1` false positives become expensive, so
  models only call very pure regions positive.
- `precision_targets = [0.75, 0.9]` in any config records
  `recall_at_prec_*`, `thr_for_prec_*` and `n_at_prec_*`. These are the
  best recall subject to each precision floor, with the score threshold
  and pick count that achieve it. The report gives them per fold, per
  era and pooled.
- A sweep's summary ranks by `rank_metric`, whose default is recall at
  the first precision floor. The question "which config recalls most at
  90% precision or better?" is therefore answered directly.

## Sweeps

`experiments/sweeps/*.toml` declare grids instead of single runs. A
sweep file has these parts. `[[cells]]` lists horizon and label pairs,
so one file can hold several label columns. `[grid]` gives model-param
ranges and expands to their cartesian product. `[[sets]]` gives whole
model-param dictionaries, each taken as a unit. `[[feature_sets]]` and
`seeds` are optional.

`vml-sweep` trains exactly as `vml-run` does. Each expanded config goes
through the same runner, which fits fresh per-fold models and evaluates
them on that fold's test year. A 32-point sweep is therefore 32 full
training runs. `vml-sweep` logs every run to `experiments/results.csv`,
failures included, because failures count as trials. The sweep uses
STANDARD split access only. Per-run reports go under
`reports/sweeps/<name>/` with a ranked summary in `_summary.md` and
`_summary.csv`. The one difference from `vml-run` is that `vml-sweep`
discards fitted models after scoring rather than saving them as
bundles. Pass
`--save-models` to keep them. The intended flow is to run the sweep,
read the summary, and re-run the winning config through `vml-run` for
its bundle. `max_runs`, whose default is 200, caps the expansion, so
trial-count inflation is always an explicit decision. The summary's
ranking is model selection on walk-forward folds. It yields candidates
for the sealed holdout, never final results.

**The record of what ran travels with the results, not as a
reference.** A sweep
copies its TOML, as written, to
`reports/sweeps/<name>/<name>_config.toml` before the first run. Every
run, in a sweep or through `vml-run`, writes `<run>_config.json` beside
its report. That file holds the full config its hash is taken over, and
the feature columns its feature spec resolved to on that dataset
version. `vml-run` also copies its TOML there. `vml-promote` carries
the sweep copy along as `config_as_run.toml`. To change a sweep that
has run, copy it to a new file with a new `name`. `vml-sweep` refuses a
report directory that holds the copy of a different sweep, and a
changed `note` is not a different sweep. Compare runs on their resolved
columns, because one feature spec selects different columns on
different dataset versions.

`[[sets]]` is the follow-up to a wide `[grid]` search. Paste its top
candidates in as whole parameter dictionaries and re-run them across
seeds, feature sets or label cells. You can also re-run them across a
further `[grid]` or `[random]` over the parameters the sets leave open.
Sets cross with every other axis. Either TOML spelling works, one inline table per line or an array
of tables:

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

A parameter may appear in only one of `[model]`, `[grid]`, `[random]`
and `[[sets]]`. A collision is a config error, not a silent override.
The sweep names runs `set<i>` by position. The summary CSV carries the full
dictionary in its `set_params` column, and the markdown header lists
every set. The exemplar is
`experiments/sweeps/lgbm_candidate_sets_3y.toml`, which crosses the
candidate sets with a `class_weight` grid and three seeds.

**Several seeds give one report per candidate.** When `seeds` lists
more than one value, the sweep reports per *candidate* rather than per
run. A candidate is a cell, a feature set, a parameter set, a grid point
and a random draw, which is everything but the seed. For each candidate
`reports/sweeps/<name>/<candidate>.md` gives, for every pooled metric
and for each test year, these statistics across seeds, plus the
per-seed values:

| statistic | meaning |
|---|---|
| `n` | the number of seeds |
| `mean`, `std` | the mean and standard deviation across seeds |
| `min`, `max` | the worst and best seed |
| 95% t-interval | the confidence interval for the mean |

The summary ranks candidates by the **mean** of `rank_metric` across
seeds, with its std, min and 95%-CI lower bound beside it.
`_summary_seeds.csv` has every metric's statistics, and `_summary.csv`
still lists every run. The per-seed run reports move to
`reports/sweeps/<name>/seeds/`. A candidate is only as good as its
worst seed, so read `_min` before `_mean`. With two or three seeds the
interval is wide by construction, and that is the honest width.
