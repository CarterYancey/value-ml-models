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

Found on 2026-09-30, from the first calibrated run on a 3-year label
(`forest_nonloser_dd30_isotonic_3y`):

- **Prequential calibration used outcomes from the future.** Fold Y's
  calibrator was fitted on the test predictions *and outcomes* of
  every fold before Y. A 3-year label of a 2007 snapshot is not known
  until 2010, so the calibrator for the 2008 entries had seen what the
  2005–07 entries went on to do in the crash. It showed as a
  calibrated run in which no 2008 or 2009 row scored 0.5 or more,
  while the uncalibrated scores for those years were the highest of
  the sample. The module's docstring said the history was "strictly
  earlier"; the test years were, the outcomes were not. **"Earlier
  fold" is not "known outcome": anything fitted on past predictions
  may use fold f for fold Y only when f + H < Y.** Fixed on
  `claude/calibration-label-lag`. Blast radius, checked: the fit, the
  ranking and every uncalibrated metric were never affected. Three
  configs set `calibration` (searched in `experiments/` here and on
  the host): `lgbm_isotonic_3y_beat_spy` has no ledger rows;
  `forest_isotonic_3y_excess8_relvalue` ran once on the host
  (2026-09-25, run `0bdb9eb4fef8`, logged under the derived name
  `random_forest_ranks-relvalue_3y_excess_cagr_ge_0p08_b8251f37`) and
  is the "random_forest + isotonic" row of
  [derived-label cells](2026-09-derived-label-cells.md), corrected
  there; `forest_nonloser_dd30_isotonic_3y`, the run that found it,
  is not to be read. No final eval used calibration (a holdout run is
  one fold and has no history to calibrate on). A first search by
  experiment name found nothing: the host run has a derived name, and
  it was found by config path. **Search a ledger by config path as
  well as by name.**
- **Isotonic calibration tied the top of the ranking.** The same run
  had p@20 0.65 against the uncalibrated 0.79: an isotonic map is a
  step function, all scores on its top step became one value, and the
  top 20 of tied scores are the first 20 rows. The docstring said
  precision@K was "essentially untouched". Rows on a step now keep
  their raw order. **A prediction written in the config ("p@20 as in
  the uncalibrated run") is what caught both.**

Found on 2026-10-01:

- **The backtest reports' yearly table was a month off.** The
  portfolio is valued on the first trading day of each month, a row
  of the equity curve carries the return since the previous valuation,
  and `yearly_table` grouped rows by the year of their own date: the
  January row, December's return, went into the new year. Every
  "year" in every backtest report ran from the first trading day of
  one December to the first of the next. SPY's "2022" read −8.2% (the
  calendar year: −19.0%), its "2019" +13.8% (+32.3%), its "2018" +7.5%
  (−5.1%). It showed when a run to 2026 printed 14.5% for a "2023"
  that the run to 2023 had printed as 19.0%. Blast radius, checked:
  both legs of a report share the window, so every excess over SPY is
  a true difference over a mislabelled twelve months, and no ordering
  of portfolios changes; the headline figures (final value, time- and
  money-weighted return, drawdown) and the per-buy tables do not use
  the table. What was wrong is every sentence that names a year
  ("ahead in 2008 by 9.5 points", "−9.6 / +4.3 / −2.2 in 2021–23"):
  the candidate's years are restated on calendar years in
  [the out-of-sample note](2026-10-01-out-of-sample.md) (2008: +11.4;
  2021–23: −8.6 / +3.2 / −2.9), and the yearly tables of the earlier
  backtest notes are left as written, with this entry as their
  correction. Fixed on `claude/backtest-calendar-years`. **A table
  whose label is a calendar unit needs one test against a date that
  straddles it.**
- **Every backtest stopped its valuation at 2023-12-29 while the
  price panel and the dataset's snapshots ran to 2026-08-21.** The
  date was the template's (decision 6) and was copied into 33 configs
  over four sessions. Findings said, correctly, that the candidate
  "has not been shown to hold outside 2005–2023"; thirty-two months
  that could show it were on disk. Traded to the end of the panel the
  candidate ends 10% behind SPY. **Before writing "only time can
  say", check the last date in the data.**
- **"Beats the average stock" was read as selection skill.** Pick
  outcomes, the screen and the per-buy tables all set picks beside
  all test rows or beside SPY. Size decides both comparisons: the
  smaller half of the investable stocks trailed SPY by 12 to 33
  points a year in every period, so any ranking that prefers large,
  calm companies beats the average row. Against stocks of their own
  size the candidate's lead was half what the all-rows comparison
  showed in 2005–2020 and nothing for the buys of 2021–23.
  `claude/backtest-universe-outcomes` adds the same-size reference to
  every backtest report. **A reference population has to share the
  picks' size before a difference is called selection.**
