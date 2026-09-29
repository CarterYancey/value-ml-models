# Sweep summary — baseline_pick_outcomes_3y

- sweep config: `experiments/sweeps/baseline_pick_outcomes_3y.toml` — copied as run to [baseline_pick_outcomes_3y_config.toml](baseline_pick_outcomes_3y_config.toml) (sweep identity `d0a25084`); the copy, not the file under `experiments/`, is the record
- dataset version: `dataset_v1.4` (pinned, immutable)
- scheme: `walkforward`, folds: `all`, git `c03a32228ae809267f9b59b8278e64e1735e221b`
- model family: `rank_factor`, fixed params `{}`
- grid: `{}`
- parameter sets (2, each taken as a unit):
  - `set0`: `{"higher_is_better": true, "rank_column": "conservative_score_rank"}`
  - `set1`: `{"higher_is_better": false, "rank_column": "vol_36m_rank"}`
- expanded runs: 2 (0 failed), seeds [7]
- ranked by pooled `precision_at_20` (higher is better)

**This ranking is model selection on walk-forward folds.** The winner's numbers are selection-biased by every configuration tried below (and before); they are candidates for the sealed holdout, never final results. Pooled numbers here are for ranking only — the per-run reports in this directory carry the era-sliced tables that an honest read requires.

## Trial ledger

- `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` (3y): 66 configurations ever tried against this cell (append-only ledger, failures included)

## Ranked runs (pooled over folds)

| run                                                                                         | status    | label                                                     | seed | param_set | grid_params | precision_at_20 | recall_at_20 | pr_auc | base_rate | n_stocks_at_20 | pick_mean_label_3y_beat_spy_at_20 | pick_mean_fwd_3y_excess_cagr_at_20 | pick_median_fwd_3y_excess_cagr_at_20 | pick_mean_fwd_3y_cagr_at_20 | pick_median_fwd_3y_cagr_at_20 | pick_mean_fwd_3y_max_drawdown_from_entry_at_20 | pick_median_fwd_3y_max_drawdown_from_entry_at_20 | all_mean_label_3y_beat_spy | all_mean_fwd_3y_excess_cagr | all_median_fwd_3y_excess_cagr | all_mean_fwd_3y_cagr | all_median_fwd_3y_cagr | all_mean_fwd_3y_max_drawdown_from_entry | all_median_fwd_3y_max_drawdown_from_entry |
| ------------------------------------------------------------------------------------------- | --------- | --------------------------------------------------------- | ---- | --------- | ----------- | --------------- | ------------ | ------ | --------- | -------------- | --------------------------------- | ---------------------------------- | ------------------------------------ | --------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------------------------ | -------------------------- | --------------------------- | ----------------------------- | -------------------- | ---------------------- | --------------------------------------- | ----------------------------------------- |
| baseline_pick_outcomes_3y__label_3y_cagr_ge_0p1_and_3y_max_drawdown_from_entry_lt_0p2__set0 | completed | fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2 | 7    | 0         | {}          | 0.3875          | 0.0023       | 0.2940 | 0.2034    | 15.3750        | 0.4906                            | -0.0207                            | -0.0023                              | 0.0742                      | 0.0928                        | 0.2810                                         | 0.1859                                           | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    |
| baseline_pick_outcomes_3y__label_3y_cagr_ge_0p1_and_3y_max_drawdown_from_entry_lt_0p2__set1 | completed | fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2 | 7    | 1         | {}          | 0.3250          | 0.0019       | 0.3090 | 0.2034    | 8.5625         | 0.3781                            | -0.0805                            | -0.0262                              | 0.0145                      | 0.0740                        | 0.2452                                         | 0.0933                                           | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    |

Full pooled metrics for every run: `baseline_pick_outcomes_3y_summary.csv`. Per-run reports (era slices, crash eras, calibration, baselines): `<run name>.md` in this directory.
