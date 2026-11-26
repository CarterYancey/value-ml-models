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
| `dataset_v1.2` | removes the rank columns of integer-valued composites (verified absent: `piotroski_f_rank`, `mohanram_g7_rank`; the raw scores remain) after the era-identifiability probe showed within-quarter ranks of discrete columns encode the calendar quarter — see `reports/promoted/era_probe_rank_fingerprints/upstream_brief.md` | breaking for configs naming those rank columns; rank-fed results are not comparable across the v1.1/v1.2 boundary. **Values of existing columns change too** (upstream decision 0016, `pinned` rank policy): the ranks of features with a mass point are re-mapped around a fixed pin. Verified 2026-09-28 on the parquet files, among the columns of the 3y forest feature set: 16 rank columns and raw `conservative_score` differ between v1.1 and v1.2 in 84–100% of rows (listed in docs/findings.md, "Results of the two tests"); none of them differs between v1.2 and v1.4. Decision 0016 names 18 pinned features and 25 removed rank columns in all |
| `dataset_v1.3` | adds the continuous path labels `fwd_{H}_max_drawdown` and `fwd_{H}_max_drawdown_from_entry` (upstream decision 0017); stored continuous only — binary drawdown targets are label expressions here (docs/experiments.md "Derived labels") | configs whose label expression reads a drawdown column need `min_dataset_version = "1.3"` |
| `dataset_v1.4` | additive, no existing column changes: the **relative-value** family (upstream decision 0018 — the six marketcap yields against the stock's own 20-quarter history: `*_vs_5y_median`, ranked; `*_5y_pctile`, raw only), long-window **price** features (decision 0019: `mom_36_12`, `max_ret_21d`, `beta_12m`, `dist_5y_high`, `price_vs_5y_avg`), and **standard scores** (decision 0020: `ohlson_o`, the assembly-stage `magic_formula_score`, the nine `piotroski_*` signal flags). Registry copy updated: `harness.families` gains the `relvalue` family and the new columns in `valuation` / `solvency` / `quality` / `technical` | configs selecting any of these (by column, or the `relvalue` family) need `min_dataset_version = "1.4"`; a `relvalue` family reference on an older dataset fails at feature resolution ("no columns in the manifest"). New relative/long-window columns are NULL without ~3–4 years of history — keep the NULLs. Note: the synced `data/dataset.md` labels `magic_formula_score` and the `sales_yield_vs_5y_median` / `max_ret_21d` / `dist_5y_high` rank pins "v1.3", while `features.md` and `manual.md` say v1.4 — v1.4 is taken as authoritative here (fix the wording upstream, then re-sync) |
| `dataset_v1.4.1` | the first **patch** build (upstream decision 0021): the v1.4 code rebuilt from the 2026-11-21 Sharadar snapshot, same column layout as v1.4, same row count (1,537,293) and effective sizes. The manifest carries a `provenance` block: raw snapshot times and hashes, the code commit, and a sha256 of every output file. Built from the same interim files as the rebuilt `dataset_v1.4` of 2026-11-23 (which has no provenance block); upstream calls the two equivalent up to floating-point noise in `sample_weight_{H}y` (relative 1e-14) | a patch is a different dataset for comparison (never compare v1.4 and v1.4.1 numbers; rerun instead, decisions 54 and 55). Every run row, result record and report now logs `dataset_sha256`, the fingerprint of `dataset.parquet`, "" for a manifest without provenance. `min_dataset_version = "1.4"` accepts it (versions parse as integer tuples) |
| `dataset_v1.5.1` | additive, no existing column changes (the v1.5 code built on the 2026-11-21 Sharadar snapshot; 1,537,293 rows, the same split files as v1.4.1 by row count): the **fundamental history** family (upstream decision 0023: the stock's own 20-quarter record of ROA, ROE and margins as `*_5y_median` / `*_5y_std` / `*_5y_z`; normalized earnings power `earnings_yield_5y_avg`, `_10y_avg`, `_5y_peak`, `_at_5y_median_margin` and the OCF/FCF 5y averages; distance from the own peak `{revenue,netinc,bvps}_vs_5y_peak` with `_quarters_since_5y_peak`; `netinc_sue_8q`, `revenue_sue_8q`; the ten-year record `ni_positive_years_10y`, `ni_history_years_10y`, `{revenue,bvps,shares}_cagr_10y`), the **trend** family widened by book value per share (`bvps_{trend,consistency,up_frac}_{w}q`), the share count (`shares_{trend,up_frac}_{w}q`) and the loss history `ni_positive_frac_{w}q`, and the **corporate events** family (decision 0024: fourteen trailing-year 8-K item counts `events_*_12m`, raw counts only). 69 new feature columns, 37 new rank columns (235 features, 149 ranks, 13 sector ranks). Labels gain the **full-path** columns per horizon (decision 0022): `fwd_{H}_max_runup`, `_days_to_max`, `_days_to_min`, `_path_avg_return`, `_realized_vol`, and SPY's own `fwd_{H}_spy_max_runup`, `_spy_max_drawdown`, `_spy_max_drawdown_from_entry`, `_spy_path_avg_return` (36 new label columns, 124 in all). Registry copy updated: `harness.families` gains `fundhist` and `events` and the trend additions. Label expressions may compare two label columns (`fwd_3y_path_avg_return > fwd_3y_spy_path_avg_return`, docs/experiments.md "Derived labels") | configs selecting any new column or family, or whose label reads a full-path column, need `min_dataset_version = "1.5"`. **The 8-K counts are an era marker before 2005**: 8-K item numbering changed in August 2004, and on this build `events_officer_change_12m` averages 0.01 per row in 1997–2003 and 2.2 from 2005 on (`events_8k_days_12m` 5 against 15); a model given them can tell the training era from the count alone (data/manual.md, TODO V8). The 5y history statistics are mostly NULL before 2001 (`roa_5y_z` NULL in 73% of 2000 rows, 16% from 2003) and the 10-year averages before 2004. A new dataset for comparison purposes: no v1.4.1 number is compared with a v1.5.1 number, the control run is rerun on v1.5.1 (decisions 54, 55) |

When upstream ships a new version or patch: add a row here, note what it
adds or changes, and set `min_dataset_version` in any new config that depends on
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
