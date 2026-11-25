# Registered diagnostics: what the purging discipline is buying

The dataset manual, data/manual.md section 7, defers a few diagnostics to this repo. They are
**diagnostic only**. They are never model selection and never reported
performance. They are the only sanctioned readers of the `entity_holdout`
and `random_kfold` tags. `scripts/run_diagnostic.py` is the single entry
point that opens those schemes. The ordinary runner keeps refusing them.

**The era-identifiability probe asks whether the features alone can tell
what year a snapshot comes from.** Under entity holdout, train and test
share the same years but hold different firms. A return model fitted that
way can score by learning *which eras were good* rather than *which
stocks*. The probe measures how identifiable the era is. It trains a
multiclass classifier on `year(snapshot_date)` under `entity_holdout`, so
memorising firms cannot help. It weights rows by the horizon's
`sample_weight_{H}y`, exactly like any experiment. It reports the result
against three trivial baselines: uniform chance, majority year and the
train prior. Snapshot counts grow over time, so majority year is the
baseline that matters. The report slices the result per year and also reports a
post-burn-in slice, because early years are identifiable from nullity
alone.

The probe has two arms:

- The raw `features` group. Its nominal levels drift with the market.
- The `ranks` group. Ranks are uniform per quarter by construction. If
  *that* group still dates a row, the joint structure encodes the era,
  and rank-fed models can time eras too.

```sh
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_3y.toml
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_rank_3y.toml
# depth-limited tree: the rules artifact names which thresholds date a row
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_tree_3y.toml
```

A probe config is an experiment config with `diagnostic = "era_probe"`
and these differences:

- It has no `label`. The target is always the snapshot year.
- `horizon_years` is mandatory. It selects the tag set and the weight
  column.
- It uses the same `[features]` selection machinery, so the probe can
  take any experiment's feature set verbatim. The config must exclude
  non-numeric columns explicitly. The probe refuses them by name.
- Its `[model]` table names `decision_tree`, `random_forest`, `lightgbm`
  or `xgboost`. The model is multiclass, with the same params and the
  same `device` knob as the binary registry.
- `report_min_year` is optional and sets the post-burn-in slice.

The probe accepts `scheme = "random_kfold"` as the deliberately leaky
upper bound.

Leave `name` out. The runner names the run `<config file stem>_<content
hash>`, so two config files can never share a report path. Editing a file
then moves its artifacts instead of overwriting them. The runner refuses
an explicit `name` that would overwrite a report written by a different
config. Reports go to `reports/diagnostics/<name>.md` with the confusion
heatmap and the importances alongside. The tree arm also writes its rules
alongside. Promote one with `vml-promote reports/diagnostics/<name>.md`.
The runner logs runs to `experiments/results.csv` under their diagnostic
scheme and the pseudo-label `snapshot_year`, apart from walk-forward trial
accounting.
