# Process issues

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

## Process issues found in this review

- Sweep TOMLs were edited in place between runs.
  `forest_random_search_3y.toml` no longer matches its own summary, and
  `-2seeds` ran from an edit that was not kept. **Copy a sweep to a
  new file before changing it.** (2026-09-28: the `-2seeds` config was
  rebuilt and hash-verified. Every sweep now copies its config into
  its report directory, every run writes its full config and resolved
  feature columns beside its report, and a sweep whose file was edited
  is refused its old report directory.)
- The tracked `lgbm_random_search_3y.toml` and
  `lgbm_cagr_quantile_3y.toml` do not reproduce the config hashes of
  their ledger runs (0 of 57 and 0 of 144), so they are not the files
  that ran either. Their results have no verified config.
- Promoted sweep configs could not be loaded: `vml-promote --note`
  writes `note` into the file and the sweep parser rejected the key.
  Fixed 2026-09-28; `note` is outside the sweep identity and the run
  hashes.
- `forest_random_search_3y-2seeds2` finished its runs but never wrote a
  summary (interrupted before the summary step?). Its runs are in the
  ledger only.
- `vml-experiments sweeps` ranks rows that use different metrics (p@10,
  p@20, p@50) in one table. Read a row's metric before comparing it.
- `reports/final_evals.csv` and `reports/final_eval/` were untracked
  despite being "always tracked". Now committed.
- `lgbm_candidate_sets_3y.toml` is pinned to `dataset_v1.0` and was never
  run.

Found on 2026-09-27:

- An interrupted run was logged as `completed`: fold rows were written
  as each fold finished, so the first attempt at forest set0 seed 23
  (run `9f357ea6b798`, stopped after 5 of 16 folds) looks like a short
  finished run. **Fixed 2026-09-28**: fold rows are now written only
  once every fold has finished, and a stopped run (Ctrl-C included)
  leaves a single `failed` row. That one old run stays in the ledger
  (rows are never rewritten); the sweep summary used the full re-run,
  but a ledger query that averages by experiment name should skip it.
- The majority-class baseline's p@K is a tie-break over constant
  scores (0.00 to 0.50 by year). Only its Brier means anything.
- Forest set4 took about 78 minutes per run against 2–15 for the
  other sets, for no gain. Check the cost of a set before giving it
  three seeds.

Found on 2026-09-28 (evening):

- `forest_feature_ablation_3y` ran 8 runs on one seed where its
  header comment describes 24 on three. The cut was deliberate
  (Carter: one seed answers the v1.1 comparison), and this file
  first reported it as a mismatch. **The `expanded runs` line of a
  summary, not a config's header comment, says what ran.**
- The two ledger hashes of a re-run differ from the original's when
  the sweep name differs, because the name is inside the config
  hash. "Same configuration" across sweeps has to be shown on the
  parameters and the per-fold numbers (as done for the code control),
  or on a hash that leaves the name out.
- `data/versions.md` described v1.2 by its removed columns only. The
  changed values of the pinned rank columns are now in its v1.2 row.
- The compounder cells had only baselines that cannot win (value
  ranks, random). **A cell's baselines should include the single
  factor the label is closest to**, here volatility.
- This session worked in a clone of the repository: the ledger, the
  reports and the untracked configs were read from the host copy,
  and the three new configs are committed with `git add -f` so that
  they travel with the branch.

Found on 2026-09-28 (night), from the first pick-outcome table:

- **The all-rows mean of `fwd_3y_excess_cagr` is −0.11 and its median
  −0.07** over the walk-forward test rows (unweighted; 36% of rows
  beat SPY). The universe a top-K is drawn from loses to SPY by a
  wide margin on average, so "better than the average test row" is a
  low bar, and an excess-return number for picks is read against
  zero, not against the universe. Smoke-test numbers, scratch
  ledger.
