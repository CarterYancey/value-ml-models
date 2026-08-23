# Dataset version compatibility

Maintained in **this** repo (not synced from upstream): which upstream
`dataset_vX.Y` a feature of this project needs, so configs and code can
declare requirements instead of relying on memory.

Two mechanisms enforce this:

1. **`min_dataset_version` in an experiment config** — the harness
   refuses to run the config against an older dataset (checked at config
   parse and again against the loaded `manifest.json`). Declare it
   whenever a config uses columns that newer versions introduced.
2. **The manifest itself** — selecting a column the manifest doesn't
   declare is always an error, so a missing feature fails loudly either
   way; `min_dataset_version` just fails with the *reason*.

## Version history (downstream view)

| dataset version | provides | notes |
|---|---|---|
| `dataset_v1.0` | base feature set: fundamentals, ranks, sector ranks, labels (1/2/3/5y), walk-forward + holdout + diagnostic splits, uniqueness weights | no trend features |
| `dataset_v1.1` | adds long-horizon trend/consistency columns (`revenue_trend_20q`, `tangibles_trend_20q`, `ocf_trend_20q`, `div_years_paid_10y`, `div_cuts_10y`; upstream decision 0015) | configs using trend columns need `min_dataset_version = "1.1"` |

When upstream ships a new version: add a row here, note what it adds or
changes, and set `min_dataset_version` in any new config that depends on
it. Results across different dataset versions are never compared
(CLAUDE.md), so the pinned `dataset_version` in each config remains the
version actually trained on — `min_dataset_version` only states the
floor the config is meaningful for.

## Doc provenance

The other `.md` files in `data/` are copies of the upstream
`radarash-dataset` docs, synced by `scripts/sync_data_docs.py`, which
records the upstream commit and per-file hashes in `data/upstream.json`.
Run `scripts/sync_data_docs.py --check` at the start of a modeling
session (needs the local upstream checkout) to catch drift; run it
without `--check` to sync and refresh the provenance record.
