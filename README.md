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

Status: **Phases 1–2 built; Phase 3 (better models) in progress.** The
experiment harness, split application with guardrails, trivial baselines,
depth-limited decision trees with rule extraction, era-sliced evaluation,
and the deployment path are implemented. Phase 3 adds random forests and
LightGBM, precision-first tuning knobs, and a sweep harness that expands
one config into a whole grid of experiments. See [TODO.md](TODO.md).

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
`experiments/models/`, predictions under `predictions/`, and the local
trial ledger `experiments/results.csv`. Only two kinds of evaluation
output are tracked:

- **Promoted reports** — a result worth review or a good example:
  `uv run vml-promote <experiment-name>` copies the report and all its
  artifacts (rules, figures) into `reports/promoted/<name>/`, which is
  tracked; commit that directory. Sweep summaries promote too
  (`vml-promote reports/sweeps/<name>/_summary.md`). Everything else can
  be deleted whenever it stops being useful — the results ledger keeps
  the trial accounting either way.
- **The sealed final-eval record** (`reports/final_evals.csv` and
  `reports/final_eval/`) — always tracked, never optional.

To find your way around past work instead of grepping TOML files:

```sh
uv run vml-experiments                 # every config + run status/date/headline
uv run vml-experiments list --model lightgbm --label beat_spy
uv run vml-experiments runs            # ledger view: everything ever run
uv run vml-experiments show <config-or-name>   # one config + its run history
```

Before writing a new config, `vml-experiments list --grep <something>`
answers "have I done this already, and what's closest to edit from?".

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
`[grid]` (model-param ranges, cartesian product), optional
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

The sealed `holdout` scheme and the diagnostic schemes (`entity_holdout`,
`random_kfold`) are refused by the runner — they raise errors unless
requested via the dedicated final-eval / registered-diagnostic entry points
(Phase 2).

Before writing or reviewing any modeling code, read
[data/manual.md](data/manual.md) — it is the contract that keeps validation
metrics honest — and the invariants in [CLAUDE.md](CLAUDE.md).
