# Derived-label cells on dataset_v1.4, single seeds

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

## Derived-label cells (dataset_v1.4, single seeds)

| label | model | p@20 | base rate | note |
|---|---|---|---|---|
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` | lightgbm | 0.36 | 0.11 | 3.2× the base rate, the largest relative lift so far (promoted) |
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` | lightgbm | 0.40–0.42 | 0.21 | `lgbm_drawdown_rungs_3y` (promoted) |
| `… < 0.3` / `… < 0.4` / no drawdown clause | lightgbm | 0.35–0.42 | 0.25 / 0.28 / 0.34 | same sweep; p@20 stays ~0.4 while the base rate falls, so the lift grows as the rung tightens |
| `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` | decision_tree d3 | 0.49 | 0.39 | `tree_depth3_3y_survive_dd30` |
| `fwd_3y_excess_cagr >= 0.08` | xgboost ×120 | 0.22 mean (0.31 max) | 0.22 | **no skill** (promoted as a negative) |
| `fwd_3y_excess_cagr >= 0.08` | random_forest + isotonic | 0.12 | 0.22 | below the base rate |
| `fwd_1y_excess_cagr >= 0.5 \| fwd_1y_max_drawdown_from_entry < 0.1 & fwd_3y_excess_cagr > 0` | lightgbm | 0.20 | 0.22 | no skill |

*Correction, 2026-09-30.* The "random_forest + isotonic" row is not a
measurement of that forest's ranking. Its scores were calibrated with
an isotonic map, which until 2026-09-30 tied every score on the map's
top step (a top 20 over tied scores is the first 20 rows) and was
fitted on outcomes not yet observable at the test rows' dates
([process issues](process-issues.md), found 2026-09-30). The same
defects took a forest in another cell from p@20 0.79 uncalibrated to
0.65. "Below the base rate" is therefore unverified for the forest;
the xgboost row (120 uncalibrated configurations at the base rate) is
unaffected, and the conclusion below rests on it. The forest has not
been re-run.

- **Drawdown-constrained compounding looks learnable; large excess
  return does not.** Absolute "compound without a crash" targets beat
  their base rates by 1.5–3×, while "beat SPY by 8 points" sits at the
  base rate across 120 xgb configs and a forest. This is the most
  promising new direction. The rows of this table are one seed each
  and had no baseline in their cell when written. The first two
  cells have since been run on three seeds with baselines and held
  (2026-09-28, section above); the other rows are still single
  seeds.
- In `lgbm_drawdown_rungs_3y`, class_weight 0.25–0.5 beat 1.0 on one
  seed; over three seeds (section above) 0.25 and 0.5 are level. Its
  feature axis was a no-op: the `ranks` group already contains the
  `*_vs_5y_median_rank` columns, so `+ ranks/relvalue` added nothing
  (identical numbers in both arms; the column count was written here
  as 125, but `ranks` resolves to 112 columns on v1.4 and the
  sweep's per-run files are gone, so its count is unverified).
