# value-ml-models

Model training, evaluation, and portfolio construction on top of the versioned
datasets produced by [`sharadar-dataset`](https://github.com/CarterYancey/sharadar-dataset).
This repo begins where that one ends: it consumes a pinned `dataset_vX.Y/`
directory and never touches raw Sharadar data.

The goal: train **interpretable, calibrated** classifiers that predict, from
point-in-time fundamentals, whether a stock will meet return criteria over
1/2/3/5-year horizons (e.g. "≥ 5% CAGR over the next 3 years", "beats SPY over
the next year"), and turn ranked probabilities into portfolios — evaluated
honestly (walk-forward, purged, era-sliced).

Status: **Phases 1–2 built; Phase 3 (better models) in progress; the
Phase 4 backtest harness is built** (awaiting the upstream price panel).
The experiment harness, split application with guardrails, trivial
baselines, depth-limited decision trees with rule extraction, era-sliced
evaluation, and the deployment path are implemented. Phase 3 adds random
forests and LightGBM, precision-first tuning knobs, and a sweep harness
that expands one config into a whole grid of experiments. Phase 4 adds
`vml-backtest`: config-driven portfolio simulation over walk-forward fold
models against a benchmark under identical cash flows. See
[TODO.md](TODO.md).

## Documentation map

| file | contents |
|---|---|
| [PLAN.md](PLAN.md) | architecture, design principles, phase roadmap, evaluation methodology |
| [TODO.md](TODO.md) | concrete development tasks, in order |
| [CLAUDE.md](CLAUDE.md) | guidance for AI-assisted development (invariants, conventions) |
| [data/manual.md](data/manual.md) | **the dataset user manual** — how to consume `dataset_vX.Y/` honestly |
| [data/dataset.md](data/dataset.md) | dataset directory layout and column groups |
| [data/labels.md](data/labels.md) | label matrix definitions (horizons, thresholds, delisting convention) |
| [data/splits.md](data/splits.md) | split-tag schemes, roles, fold calendar |
| [data/features.md](data/features.md) | the canonical feature registry |
| [data/versions.md](data/versions.md) | dataset version compatibility (what each `dataset_vX.Y` provides; `min_dataset_version`) |

The `data/*.md` docs (except `versions.md`) are synced copies of the
upstream `radarash-dataset` docs — `scripts/sync_data_docs.py` copies
them from the local upstream checkout and records the upstream commit in
`data/upstream.json`; `--check` detects drift without copying.

## Setup

Requires Python 3.12+. Dependencies are managed in `pyproject.toml`
([uv](https://docs.astral.sh/uv/) recommended):

```sh
uv sync
```

### Getting the data

Data files are git-ignored; only docs are committed. Place (or symlink) a
versioned dataset directory produced by `sharadar-dataset` under
`data/datasets/`:

```
data/datasets/dataset_v1.0/
├── dataset.parquet       one row per snapshot: features, ranks, labels, weights
├── splits.parquet        role tags per (scheme, fold, horizon, snapshot)
├── split_folds.parquet   frozen fold manifest
└── manifest.json         provenance: version, params, counts, column layout
```

Never edit files inside a dataset directory. If something is wrong upstream,
file it against `sharadar-dataset` and consume the next version.

## Usage

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
  "Workflow & housekeeping" below).

- Training and evaluation are distinct tasks: `vml-run` saves the fitted
  per-fold models as a bundle under `experiments/models/` (git-ignored),
  and `vml-eval` re-scores a saved bundle under an eval config — metric
  parameters only (`top_k`, `score_thresholds`); the dataset version,
  scheme, folds, label, and features stay pinned by the bundle. Each
  evaluation is logged to `experiments/results.csv` under its own config
  hash, so trying many evaluation criteria still counts in the trial
  ledger.

```sh
# one experiment (trains, evaluates, and saves the model bundle)
uv run vml-run experiments/baseline_b2m_rank_3y_beat_spy.toml

# a sweep: one TOML declaring ranges (label cells x param grid x feature
# sets x seeds) expands into ordinary experiments, all run and ranked
uv run vml-sweep experiments/sweeps/tree_precision_grid_3y.toml
uv run vml-sweep experiments/sweeps/tree_precision_grid_3y.toml --dry-run  # names only

# re-evaluate a saved bundle with different metric parameters (no refit)
uv run vml-eval experiments/models/<bundle_dir> experiments/eval_thresholds.toml

# the full baseline grid (every horizon × label cell × baseline)
uv run python scripts/run_baselines.py dataset_v1.0

# tests (run against a hand-built miniature dataset; no real data needed)
uv run pytest
```

### Workflow & housekeeping

Everything a run generates is working output, git-ignored by default:
reports and figures under `reports/`, model bundles under
`experiments/models/`, predictions under `predictions/`, the local trial
ledger `experiments/results.csv` — **and every new config under
`experiments/`**. Most configs get written, run once and forgotten, so an
untracked one is never a decision to make. A config becomes tracked when
its result is promoted (or, for a sample worth keeping without a
report, `git add -f experiments/<config>.toml`; configs already tracked
stay tracked). Only two kinds of evaluation output are tracked:

- **Promoted results** — a result worth review or a good example:

  ```sh
  uv run vml-promote <experiment-name> --note "one-line conclusion"
  git commit
  ```

  copies the report and all its artifacts (rules, figures) into
  `reports/promoted/<name>/` together with a `config.toml` snapshot and a
  `promoted.json` provenance record (run id, config hash, cell, headline
  vs. best baseline), writes the note into the config (`note = "..."`,
  outside the config hash), stages the config (`git add -f`) and the
  promoted directory, and regenerates `reports/promoted/README.md` — the
  index of everything promoted, with cell, headline vs. baseline and
  note per row. Sweeps promote too, by name
  (`vml-promote <sweep-name>` takes the summary and its CSVs, not the
  per-run reports — a candidate worth keeping is promoted by its own
  report path, `vml-promote reports/sweeps/<sweep>/<run>.md`); `vml-promote --list`
  shows what could be promoted, `--index` rebuilds the index. Everything
  else can be deleted whenever it stops being useful — the results ledger
  keeps the trial accounting either way.
- **The sealed final-eval record** (`reports/final_evals.csv` and
  `reports/final_eval/`) — always tracked, never optional.

To find your way around past work instead of grepping TOML files:

```sh
uv run vml-experiments                 # every config, grouped by cell, ranked by lift
uv run vml-experiments list --model lightgbm --label beat_spy
uv run vml-experiments list --sort path   # the flat, path-ordered view
uv run vml-experiments runs            # ledger view: everything ever run
uv run vml-experiments show <config-or-name>   # one config, its runs, its cell's baselines
uv run vml-experiments sweeps --out reports/sweep_digest.md   # every sweep, digested
```

`sweeps` reads every `reports/sweeps/*/*_summary.csv` and writes one
markdown digest: per cell, the top runs across *all* sweeps (sweep,
model, feature set as the sweep config describes it, swept params,
metric, lift over the cell's best baseline) and a "what wins" list —
the mean metric by value for the feature set, the model and each swept
parameter (continuous random-search axes are binned into quartiles).
It is pooled and selection-biased, so it ranks candidates and settles
hyperparameters; it never reports a result. `--metric` picks the pooled
metric (default `precision_at_20`, falling back to the row's headline),
`--label` filters cells. Reading the digest beats reading thirty
summaries, for you and for anyone you paste it to.

The listing groups configs by *cell* (label · horizon · scheme · dataset
version) — numbers across cells are not comparable, so there is no global
sort — and inside a cell ranks them by **lift**: the headline metric
(`p@K`, else `recall@p…`, fold mean of the latest completed run) minus the
best baseline on that same metric in the same cell, taken from the
ledger's latest baseline runs (`scripts/run_baselines.py`; a cell without
baselines reads `none run`). Each row also shows the config's `note`,
whether the sealed holdout has been consumed for it (`final_eval`:
`phase3 ✓`), and `★` when promoted. Restricted schemes are flagged in the
group header (`holdout ⚠ final eval only`).

Before writing a new config, `vml-experiments list --grep <something>`
answers "have I done this already, and what's closest to edit from?" —
notes are searched too.

### Derived labels

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

### Models

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

### Sweeps

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

### Deployment: train on everything, score today's stocks

Development measures with purged walk-forward splits; the model that
*ships* is refit on **all** labeled rows — every snapshot kind, delistings
included, no split filtering (data/manual.md §4 rule 7: the holdout/purge
discipline constrains measurement, not what the deployed model may learn
from). Deployment fits have no test set, so their scores are rankings,
never performance numbers.

```sh
# refit an already-selected config's model on all labeled data
# (the config's scheme/folds are ignored; saves a deployment bundle)
uv run vml-train-deploy experiments/tree_depth3_3y_beat_spy.toml

# score today's stocks: an inference dataset directory containing a
# dataset.parquet with the feature columns (no labels needed)
uv run vml-predict \
    experiments/models/<name>_deployment_<run_id> \
    data/datasets/inference_2026-07-22

# or several bundles at once: one combined CSV with a
# rank_<model>/score_<model> column pair per bundle, ordered by
# mean rank across the models
uv run vml-predict \
    experiments/models/<name_a>_deployment_<run_id> \
    experiments/models/<name_b>_deployment_<run_id> \
    data/datasets/inference_2026-07-22
```

`vml-predict` writes the full score-descending ranking to
`predictions/<inference>__<bundle>.csv` (override with `--output`), writes
a provenance sidecar `.meta.json` (bundle, git SHA, config hash, row
count), and prints the top 50 (`--top` to change). With several bundles
the combined CSV goes to `predictions/<inference>__multi__<names>.csv`,
each model still gets its own logged inference run, and the sidecar lists
every bundle; each model's score is its own probability/margin scale, so
cross-model comparison uses the `rank_*` columns. `--trends` carries the
long-horizon trend context columns (`revenue_trend_20q`,
`tangibles_trend_20q`, `ocf_trend_20q`, `div_years_paid_10y`,
`div_cuts_10y`) verbatim from the inference data into either CSV, after
the score columns. Both deployment
training and inference runs are logged to `experiments/results.csv` under
their own schemes (`deployment` / `inference`), so they never mix with
walk-forward trial accounting.

### Registered diagnostics: what the purging discipline is buying

data/manual.md §7 defers a few diagnostics to this repo. They are
**diagnostic only** — never model selection, never reported performance —
and they are the only sanctioned readers of the `entity_holdout` /
`random_kfold` tags. `scripts/run_diagnostic.py` is the single entry
point that opens those schemes; the ordinary runner keeps refusing them.

**Era-identifiability probe** — can the features alone tell what year a
snapshot comes from? An entity-holdout return model (train and test share
the same years, different firms) can score by learning *which eras were
good* rather than *which stocks*; the probe measures how identifiable the
era is. It trains a multiclass classifier on `year(snapshot_date)` under
`entity_holdout` (so memorising firms can't help), weighted by the
horizon's `sample_weight_{H}y` exactly like any experiment, and reports
it against the trivial baselines (uniform chance, majority year, train
prior — snapshot counts grow over time, so majority-year is the one that
matters), per year, and for a post-burn-in slice (early years are
identifiable from nullity alone). Two arms: the raw `features` group
(nominal levels drift with the market) and the `ranks` group (uniform per
quarter by construction — if *that* still dates a row, the era is
encoded in joint structure and rank-fed models can time eras too).

```sh
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_3y.toml
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_rank_3y.toml
# depth-limited tree: the rules artifact names which thresholds date a row
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_tree_3y.toml
```

A probe config is an experiment config with `diagnostic = "era_probe"`,
no `label` (the target is always the snapshot year), a mandatory
`horizon_years` (it selects the tag set and the weight column), the same
`[features]` selection machinery (so any experiment's feature set can be
probed verbatim — non-numeric columns must be excluded explicitly; the
probe refuses them by name), a `[model]` table (`decision_tree`,
`random_forest`, `lightgbm`, `xgboost` — multiclass, same params and
`device` knob as the binary registry), and an optional
`report_min_year` for the post-burn-in slice. `scheme = "random_kfold"`
is accepted as the deliberately leaky upper bound. Leave `name` out: the
run is named `<config file stem>_<content hash>`, so two config files can
never share a report path, and editing a file moves its artifacts instead
of overwriting them; an explicit `name` that would overwrite a report
written by a different config is refused. Reports go to
`reports/diagnostics/<name>.md` with the confusion heatmap, importances,
and (tree arm) rules alongside; promote one with
`vml-promote reports/diagnostics/<name>.md`. Runs are logged to
`experiments/results.csv` under their diagnostic scheme and the
pseudo-label `snapshot_year`, apart from walk-forward trial accounting.

### Backtesting: simulate the strategy without the deployed models

A deployment bundle is refit on all labeled history, so backtesting it
would score the past with a model that has seen it. `vml-backtest`
instead consumes the **walk-forward fold bundles** `vml-run` saves: a
trade in year Y is scored by the fold-Y models — trained, purged, and
embargoed on years before Y — which is exactly "update the models at the
end of each calendar year". One TOML in `experiments/portfolios/`
declares the whole strategy (see
`experiments/portfolios/allprob_top25_5models.toml` for the live
five-model AllProb screen):

- the model bundles and how their scores combine (`product` = AllProb,
  `mean`, `min`, `mean_rank`) plus an optional per-model `min_score`;
- declared column filters (e.g. `revenue_trend_20q > 0`) — validated
  against the manifest's feature/rank groups, so a screen can never
  reference a label;
- a **mandatory investability statement**: `[[investability]]` filters or
  the explicit `investability = "none"` (reported with a warning);
- per-model floors via `[signal.min_scores]` (bundle name → floor,
  overriding the scalar `min_score`);
- the strategy and **mandatory `cost_bps`**: `buy_and_hold` (monthly
  deposit, buy top-K by combined score, score- or equal-weighted, whole
  shares — the budget remainder stays in cash — never sell) or
  `sell_below_criteria` (same buying, plus: any held position failing
  the *sell criteria* at a rebalance is sold entirely, proceeds funding
  that month's buys — falling out of the top-K alone is never a sell,
  and a holding whose snapshot aged out of the cross-section fails).
  The sell criteria default to the buy criteria; an optional `[sell]`
  section (own `min_score`/`min_scores`/`filters`) states a hysteresis
  band explicitly (buy > 0.7, sell < 0.5). New portfolio-management
  ideas plug in as new `Strategy` classes without touching the engine;
- the `model_update` policy for trade years past a bundle's last fold
  (the fold calendar stops where test labels stop being observable, but
  a live portfolio keeps trading): `"refit"` (default) simulates the
  real year-end procedure — the bundle's config refit on every row
  whose label window was observable by Jan 1 of the trade year
  (manual.md §4 rule 7 applied point-in-time; no split tags read, no
  test set) — while `"frozen"` keeps the last fold's model. Refits are
  cached on disk (`experiments/models/refits/`, git-ignored) keyed by
  (train config hash, dataset version, trade year, label lag), so
  re-running with different strategy parameters reuses the identical
  models — the report's refit appendix marks each row `fit` or `cache`
  (`--refit-cache DIR` moves the cache, `--no-refit-cache` bypasses
  it). Reports flag that these years overlap the sealed holdout era:
  context, never a selection signal;
- the simulation window (defaults: buys start at the latest first-fold
  year across the bundles and continue, deposits included, to the price
  panel's end; `[window] start` trims the early thin years).

Monthly point-in-time cross-sections come from `dataset.parquet` itself
(latest completed-quarter median-kind snapshot per stock, staleness-
capped) — **not** from historical inference directories, which are
survivor-only by construction. The benchmark leg (SPY) runs through the
same engine with identical deposits and accounting. Reports land in
`reports/backtest/<name>_<config-hash>.*` (report, equity/trades/
rebalances CSVs — trades carry tickers, per-model scores, and realized
profit on sells — and the equity plot), lead with money- and
time-weighted results, the per-year era slice with crash years tagged,
and the defensive-hypothesis check; runs are logged to
`experiments/results.csv` under scheme `backtest`.

```sh
# 1. train walk-forward bundles for the models the strategy uses
uv run vml-run experiments/<model-config>.toml
# 2. point the portfolio config's `bundles` at those directories, then
uv run vml-backtest experiments/portfolios/allprob_top25_5models.toml
```

Backtests additionally require a versioned **price panel**
`data/datasets/prices_vX.Y/` (`prices.parquet` — daily total-return
adjusted closes per permaticker, survivorship-free through each stock's
final print; `benchmark.parquet` — SPY, whose dates define the trading
calendar; `manifest.json`). Build it from the upstream repo's raw
Sharadar tables — the same `SEP.closeadj` / `SFP` source the labels are
computed from — with the raw directory symlinked like the datasets:

```sh
ln -s ~/radarash-dataset/data/raw data/raw
uv run python scripts/build_price_panel.py data/raw dataset_v1.1 --out-version prices_v1.0
```

This is the one sanctioned read of raw Sharadar tables in this repo:
the panel carries `(permaticker, date, closeadj)` outcome paths only —
never features — and the consumer contract in `src/portfolio/prices.py`
validates it on load.

The sealed `holdout` scheme and the diagnostic schemes (`entity_holdout`,
`random_kfold`) are refused by the runner — they raise errors unless
requested via the dedicated entry points: `scripts/run_final_eval.py`
(holdout, one look per cell) and `scripts/run_diagnostic.py` (the registered
diagnostics, see above).

The final eval takes the config you selected on walk-forward as it is —
no copied `*_holdout.toml`:

```sh
uv run python scripts/run_final_eval.py experiments/<selected>.toml
```

The scheme is switched to `holdout` in memory; the run keeps the
experiment's name (the report lands in `reports/final_eval/`, the row in
`reports/final_evals.csv`, and `vml-experiments` shows `✓ look 1/1` next
to the config). The holdout is the one number nobody selected on, and it
stays that only while it is looked at **once per cell** — label, horizon
and holdout window (the fold's test years from `split_folds.parquet`; a
feature-only dataset bump re-uses the same rows and does not re-seal
them). Run it when you would act on the model; choosing between
candidates is walk-forward's job. A second evaluation in a consumed cell
is refused unless you say why:

```sh
uv run python scripts/run_final_eval.py experiments/<other>.toml \
    --reopen "new model family after the v1.4 relvalue features"
```

It then runs as look 2, the reason is logged, and the report, the ledger
and the catalog (`✓ look 2/2`) all carry the count — N looks inflate the
best number by roughly the top order statistic of N draws, so the count
is part of the result, never hidden. Ledgers written under the older
`phase` column are migrated in place; their rows count as looks in
their cell.

Before writing or reviewing any modeling code, read
[data/manual.md](data/manual.md) — it is the contract that keeps validation
metrics honest — and the invariants in [CLAUDE.md](CLAUDE.md).
