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
| `dataset_v1.2` | removes the rank columns of integer-valued composites (verified absent: `piotroski_f_rank`, `mohanram_g7_rank`; the raw scores remain) after the era-identifiability probe showed within-quarter ranks of discrete columns encode the calendar quarter — see `reports/promoted/era_probe_rank_fingerprints/upstream_brief.md` | breaking for configs naming those rank columns; rank-fed results are not comparable across the v1.1/v1.2 boundary; fill in the full upstream change list from its changelog |
| `dataset_v1.3` | adds the continuous path labels `fwd_{H}_max_drawdown` and `fwd_{H}_max_drawdown_from_entry` (upstream decision 0017); stored continuous only — binary drawdown targets are label expressions here (README "Derived labels") | configs whose label expression reads a drawdown column need `min_dataset_version = "1.3"` |
| `dataset_v1.4` | additive, no existing column changes: the **relative-value** family (upstream decision 0018 — the six marketcap yields against the stock's own 20-quarter history: `*_vs_5y_median`, ranked; `*_5y_pctile`, raw only), long-window **price** features (decision 0019: `mom_36_12`, `max_ret_21d`, `beta_12m`, `dist_5y_high`, `price_vs_5y_avg`), and **standard scores** (decision 0020: `ohlson_o`, the assembly-stage `magic_formula_score`, the nine `piotroski_*` signal flags). Registry copy updated: `harness.families` gains the `relvalue` family and the new columns in `valuation` / `solvency` / `quality` / `technical` | configs selecting any of these (by column, or the `relvalue` family) need `min_dataset_version = "1.4"`; a `relvalue` family reference on an older dataset fails at feature resolution ("no columns in the manifest"). New relative/long-window columns are NULL without ~3–4 years of history — keep the NULLs. Note: the synced `data/dataset.md` labels `magic_formula_score` and the `sales_yield_vs_5y_median` / `max_ret_21d` / `dist_5y_high` rank pins "v1.3", while `features.md` and `manual.md` say v1.4 — v1.4 is taken as authoritative here (fix the wording upstream, then re-sync) |

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
