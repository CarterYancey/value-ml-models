# Registered diagnostics: what the purging discipline is buying

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
