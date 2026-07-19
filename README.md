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

Status: **v1 dataset delivered, modeling not yet started.** The upstream
dataset (v1.0) is complete and documented; the experiment harness is the
first thing to build. See [TODO.md](TODO.md).

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

Planned workflow (the harness is not yet implemented — see
[TODO.md](TODO.md)):

- One experiment = one config file in `experiments/`, naming the dataset
  version, scheme/fold/horizon, label column, model, and seed.
- The harness runs configs; code never hardcodes an experiment. Every run
  logs dataset version + config + git SHA + seed, including abandoned runs.
- Evaluation reports (era-sliced metrics, calibration curves, extracted tree
  rules) are written to `reports/` and checked in.

Before writing or reviewing any modeling code, read
[data/manual.md](data/manual.md) — it is the contract that keeps validation
metrics honest — and the invariants in [CLAUDE.md](CLAUDE.md).
