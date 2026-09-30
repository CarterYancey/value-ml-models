# Earlier work, dataset_v1.0 and v1.1

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

## Earlier work (dataset_v1.0 / v1.1, July – August)

- 1y/2y/5y beat_spy and cagr_ge_0 LightGBM feature-set sweeps
  (`lightgbm_sweep_4fs_*`, `lgbm_spy_*`): rank features beat raw
  features at 1y/2y/5y beat_spy on v1.0 (p@10 ~0.73–0.83 against
  ~0.37–0.53). Metrics were p@10/p@50 on few seeds, so treat these as
  directional only.
- `lgbm_precision_grid_1-2y_absFeatures` (v1.0): 1y cagr_ge_0 p@50
  0.72 mean against a random baseline of 0.53. **2y cagr_ge_0 and 2y
  cagr_ge_10 were below the random baseline** (0.31 against 0.54, 0.11
  against 0.39), which is worth remembering before running raw-feature
  models on 2y absolute labels.
- Depth-limited trees (experiments 4–14, `tree_depth*`): interpretable
  but weak off 2y cagr_ge_0; `tree_depth3_2y_cagr_ge_0` is promoted with
  its rules.
