# Session log, September 2026

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

## Log

Newest first. One entry per working session: what ran, what it showed,
what's next. Record trial counts, not just winners.

### 2026-09-28 (late): pick outcomes built

- Code: `pick_outcomes` in experiment, sweep and eval configs;
  `src/eval/picks.py`; a "Pick outcomes" section in run reports and
  the columns in sweep summaries. 17 new tests, 423 pass. Configs
  without the key keep their hashes (the key is in the hash when
  set, like `top_k`).
- Smoke test on `dataset_v1.4`, scratch ledger, not a logged trial:
  highest `conservative_score_rank` in the primary cell. p@20 0.3875,
  equal to the ledger's run of the same baseline; the picks' hit
  rate on `label_3y_beat_spy` 0.4906, equal to the same factor's
  p@20 in the beat_spy cell (0.491, a separate run). Two independent
  runs agreeing is the check that the outcomes describe the right
  rows. The picks: median excess CAGR −0.002, mean −0.021, median
  drawdown from entry 0.19, 15.4 distinct stocks per 20 picks.
- Decided (Carter): the label comparison of record is
  `vml-backtest`; sweeps do not save models; a candidate goes sweep →
  `vml-run` → promote → backtest → final eval → `vml-train-deploy`.
- Wrote `baseline_pick_outcomes_3y` (2 runs) and
  `forest_label_rungs_dd_entry_3y` (27 runs), dry-run clean, not
  run. `forest_feature_sets_dd_entry_3y` was started by Carter at
  14:48 and carries no pick outcomes (written before they existed,
  and a config that has run is not edited).
- Next: the two new sweeps; read the feature-set sweep when it
  finishes; then the backtest template.

### 2026-09-28 (night): column controls and low-risk baselines; primary cell chosen

- Ran (by Carter, git `3f2bfdf`), 24 runs, no failures:
  `baseline_lowvol_rank_3y` (12), `forest_v11_column_control_3y` (8,
  `dataset_v1.1`), `forest_v14_unchanged_columns_3y` (4). All three
  report directories hold the configs as committed. Trial counts:
  3y beat_spy 47 on v1.4 and 725 on v1.1; cell A 29; cell B 34.
- Showed: (1) the v1.1 forest edge on 3y beat_spy is in the v1.1
  values of the 17 columns decision 0016 re-mapped (0.57–0.58 with
  them, 0.43–0.47 without; the four dropped columns change nothing;
  v1.1 and v1.4 are identical on the other 103); (2) on v1.4,
  `conservative_score_rank` alone matches the forests on beat_spy;
  (3) in cell B forests are 0.11 above the best single factor and
  LightGBM is level with it; in cell A the forests are within 0.05
  of it.
- Decided (Carter): the from-entry cell is the primary cell, for its
  precision and because the label is the more intuitive one. The
  choice of label stays part of the experiments.
- Corrected: the ablation's single seed was deliberate, not a
  mismatch.
- Wrote `forest_feature_sets_dd_entry_3y` (30 runs), dry-run clean,
  resolved columns 97 / 15 / 109 / 125 / 172, not run.
- Nothing promoted, no holdout look.
- Next: run that sweep; build the report-only secondary outcomes
  (plan, step 3) before comparing labels.

### 2026-09-28 (evening): seven sweeps reviewed; code and added columns ruled out; compounder cells hold

- Ran (by Carter, 2026-09-27/28, git `86ef0c4`), 60 runs:
  `forest_feature_ablation_3y` (8 runs, one seed),
  `baseline_majority_` / `_random_` / `_rank_factor_drawdown_compounder_3y`
  (2 + 6 + 4), `forest_drawdown_compounder_seeds_3y` (24),
  `lgbm_drawdown_compounder_seeds_3y` (12),
  `forest_v11_code_control_3y` (4, on `dataset_v1.1`). No failures.
  Trial counts now: 3y beat_spy 39 on v1.4 and 717 on v1.1;
  compounder cell A 25, cell B 30.
- Showed: (1) today's code reproduces the August v1.1 fold rows
  exactly; (2) the v1.1 column set on v1.4 scores p@20 0.44, not the
  0.58 predicted if the added columns were the cause, though
  removing them raises PR-AUC by 0.01–0.02; (3) no ablation arm can
  be told from another; (4) the compounder cells hold over three
  seeds and after 2013, forests ahead of LightGBM, no lift in the
  crash-window entry years.
- Checked on the parquet files (no harness run): 17 of the 120
  shared columns changed values at v1.2 (decision 0016).
- Wrote three configs, dry-run clean, resolved columns checked
  against both manifests (120 / 103 / 103), none run:
  `baseline_lowvol_rank_3y` (12 runs),
  `forest_v11_column_control_3y` (8),
  `forest_v14_unchanged_columns_3y` (4).
- Nothing promoted, no holdout look.
- Next (as planned that evening; both have since run): the
  low-volatility baseline, then the column controls.

### 2026-09-28: the non-replication claim withdrawn; configs now travel with reports

- Carter questioned the 2026-09-27 conclusion: the v1.1 sweep's
  config was lost, so what the v1.4 runs were being compared with was
  not known. Checked it. The config was recoverable (100 of 100
  hashes), the spec and parameters were the right ones, the rows are
  identical, and the columns are not: 13 added, 4 dropped. The claim
  "did not replicate" is withdrawn; "scores lower on a different
  column set, cause open" replaces it. Promoted notes reworded.
- What went wrong in the reasoning is written up in CLAUDE.md,
  "Before writing a conclusion".
- Wrote `forest_v11_code_control_3y` (4 runs); it and the ablation
  now come before the drawdown-compounder sweeps.
- Code: config copies in report directories, `note` accepted in sweep
  files (above, under process issues). No experiments run.

### 2026-09-28: interrupted runs no longer log as completed

- Code only, no experiments run. `RunLog` in `src/harness/results.py`
  holds a run's fold rows until the last fold finishes; used by
  `vml-run` / `vml-sweep`, `vml-eval` and the era probe. Regression
  test in `tests/test_runner.py`. A process that is killed outright
  (OOM, `kill -9`) still leaves no row at all.

### 2026-09-27: v1.4 carry-forward sweeps reviewed

- Ran (by Carter, 2026-09-26/27, git `b649c58`): the v1.4 baseline
  grid (80 runs), `forest_candidate_sets_3y` (18 runs, plus one
  interrupted) and `xgb_candidate_sets_3y` (9 runs). 31 configurations
  in the 3y beat_spy cell on v1.4.
- Showed (as read that day; see the 2026-09-28 entry for the
  correction): neither family replicates. Forests p@20 0.42 pooled, 0.59
  in 2005–12, 0.22 in 2013–19 (base 0.28); xgb 0.37 / 0.54 / 0.17.
  PR-AUC stays above the base rate every year. Details in "3y beat_spy
  on dataset_v1.4".
- Promoted 3 (two sweep summaries as negatives, one era report). No
  holdout look.
- Wrote six sweep configs (git-ignored until promoted), all dry-run
  clean, none run: `forest_feature_ablation_3y` (24 runs),
  `lgbm_drawdown_compounder_seeds_3y` (12),
  `forest_drawdown_compounder_seeds_3y` (24), and the random /
  rank-factor / majority baselines for the two drawdown-compounder
  cells (6 + 4 + 2).
- Next: run the three baseline sweeps, then the two compounder
  sweeps, then the ablation. Read each era table before the pooled
  number. If the compounder lift also sits in 2005–12 only, the
  problem is the post-2013 regime and not the label.

### 2026-09-26: review after the August/September hiatus

- Reviewed the ledger, every sweep summary and the holdout record. Wrote
  this file.
- Promoted 7 results (see `reports/promoted/README.md`), including 2
  negatives.
- Wrote `forest_candidate_sets_3y` / `xgb_candidate_sets_3y` (v1.4).
- Cleared the working tree (archived outside the repo first): 87
  untracked configs, unpromoted reports, walk-forward bundles and cached
  refits. Kept: the ledger, the holdout record, promoted reports, tracked
  configs, and the 16 deployment bundles.
- Next: v1.4 baselines → both carry-forward sweeps → compare the family
  era slices → multi-seed the drawdown-compounder label with a v1.4
  baseline.
