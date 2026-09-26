# value-ml-models

Model training, evaluation, and portfolio construction on top of the versioned
datasets produced by [`sharadar-dataset`](https://github.com/CarterYancey/sharadar-dataset).
This repo consumes a pinned `dataset_vX.Y/` directory and never touches raw
Sharadar data.

It trains **interpretable, calibrated** classifiers that predict, from
point-in-time fundamentals, whether a stock will meet return criteria over
1/2/3/5-year horizons (e.g. "≥ 5% CAGR over the next 3 years", "beats SPY over
the next year"), and turns ranked probabilities into portfolios — evaluated
honestly (walk-forward, purged, era-sliced). Status and roadmap:
[PLAN.md](PLAN.md), [TODO.md](TODO.md).

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

Data is git-ignored. Place (or symlink) a dataset directory from
`sharadar-dataset` under `data/datasets/`:

```
data/datasets/dataset_v1.0/
├── dataset.parquet       one row per snapshot: features, ranks, labels, weights
├── splits.parquet        role tags per (scheme, fold, horizon, snapshot)
├── split_folds.parquet   frozen fold manifest
└── manifest.json         provenance: version, params, counts, column layout
```

Never edit files inside a dataset directory; fixes are upstream changes that
produce a new version.

## Usage

One experiment = one TOML config in `experiments/`. Every run is logged to
`experiments/results.csv`; reports go to `reports/` (git-ignored until
promoted).

```sh
# train + evaluate one config (saves a model bundle)
uv run vml-run experiments/baseline_b2m_rank_3y_beat_spy.toml

# a sweep: one TOML expands into a grid of experiments, run and ranked
uv run vml-sweep experiments/sweeps/tree_precision_grid_3y.toml [--dry-run]

# re-evaluate a saved bundle with different metric parameters (no refit)
uv run vml-eval experiments/models/<bundle_dir> experiments/eval_thresholds.toml

# the full baseline grid
uv run python scripts/run_baselines.py dataset_v1.0

# browse past work; keep a result
uv run vml-experiments list --grep <something>
uv run vml-promote <experiment-name> --note "one-line conclusion"

# sealed holdout: once per cell, when you would act on the model
uv run python scripts/run_final_eval.py experiments/<selected>.toml

# deploy: refit on all labeled data, score today's stocks
uv run vml-train-deploy experiments/<selected>.toml
uv run vml-predict experiments/models/<name>_deployment_<run_id> data/datasets/<inference_dir>

# backtest a portfolio strategy over walk-forward bundles
uv run vml-backtest experiments/portfolios/allprob_top25_5models.toml

# registered diagnostics (era-identifiability probe)
uv run python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_3y.toml

# tests (miniature hand-built dataset; no real data needed)
uv run pytest
```

## Documentation

| file | contents |
|---|---|
| [docs/experiments.md](docs/experiments.md) | config format, feature selection, derived label expressions, models, sweeps |
| [docs/workflow.md](docs/workflow.md) | what is tracked, promotion, the experiment catalog, the sealed final eval |
| [docs/deployment.md](docs/deployment.md) | deployment refits and `vml-predict` |
| [docs/backtesting.md](docs/backtesting.md) | portfolio configs, strategies, the price panel |
| [docs/diagnostics.md](docs/diagnostics.md) | registered diagnostics (era probe) |
| [PLAN.md](PLAN.md) | architecture, design principles, phase roadmap, evaluation methodology |
| [TODO.md](TODO.md) | development tasks, in order |
| [CLAUDE.md](CLAUDE.md) | invariants and conventions for AI-assisted development |
| [data/manual.md](data/manual.md) | **the dataset contract** — read before touching modeling code |
| [data/dataset.md](data/dataset.md), [labels.md](data/labels.md), [splits.md](data/splits.md), [features.md](data/features.md) | dataset layout, label matrix, split schemes, feature registry (synced from upstream via `scripts/sync_data_docs.py`) |
| [data/versions.md](data/versions.md) | what each `dataset_vX.Y` provides; `min_dataset_version` |
