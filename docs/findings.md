# Findings

What is known now, by cell, and what is planned. Kept short on purpose:
**this file is rewritten, not appended to**, and stays under about 150
lines.

- What was done, in order, one entry per sweep: [logbook.md](logbook.md).
  Read that first.
- Tables, checks and reasoning behind a conclusion: the note it links
  to, in [notes/](notes/).
- How an unattended session works: [agents.md](agents.md).

Numbers are walk-forward fold means over test years 2005–2020 (16
folds, `split_folds.parquet` of the named dataset version), `p@20`
picks the top 20 per test year, and they are **selection-biased** by
the trial counts given. They rank candidates; none is a result of
record. Results are never compared across dataset versions.

## State (2026-09-29)

| cell (3y, `dataset_v1.4`) | trials | best so far, p@20 | bar | status |
|---|---|---|---|---|
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` ("from entry", **primary**) | 64 | forests 0.48–0.50 (2013–20: 0.53–0.54), fold-mean PR-AUC 0.327, on the 112 rank columns | single factor 0.39, base rate 0.21 | feature set chosen; label rungs and parameter searches queued |
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` ("whole path") | 29 | forests 0.37–0.39 | single factor 0.34, base rate 0.11 | close to a screen; second choice |
| `label_3y_beat_spy` | 47 (725 on v1.1) | forests 0.40–0.54, not separable | single factor 0.49, base rate 0.35 | parked |

- **Sealed holdout:** 19 looks, all at 1y/2y/5y (below). Every 3y cell
  is unopened.
- **Ledger:** 1,929 runs by run id on the host at the last count
  (2026-09-29), before the sandbox's shard.

## Conclusions that stand

Each with the note that carries its evidence.

1. **Drawdown-constrained compounding is learnable and the lift holds
   after 2013.** Three seeds, seed std at most 0.03, every candidate
   higher in 2013–20 than in 2005–12.
   [note](notes/2026-09-28-drawdown-compounder-cells.md)
2. **Those models fall to the base rate for entry years whose window
   holds a crash** (2005–08, 2019), and so does every single factor.
   Same note.
3. **Much of that lift is one column.** `conservative_score_rank`
   alone scores 0.39 in the primary cell: about 60% of the forests'
   lift over the base rate. LightGBM as configured adds nothing to it;
   forests add 0.11. Same note.
4. **Forests are ahead of LightGBM in both compounder cells**, on p@20
   and PR-AUC, comparing two configurations, not two tuned families.
   Same note.
5. **The v1.1 forest edge on 3y beat_spy sat in the v1.1 form of 17
   rank columns** that upstream decision 0016 re-mapped at v1.2.
   Code, added columns and dropped columns are each ruled out by a
   run; v1.1 and v1.4 give identical fold rows on the other 103
   columns. Open: whether that form carried a quarter identifier or
   stock information. [note](notes/2026-09-beat-spy-v11-to-v14.md)
6. **On v1.4, no forest is clearly better than a single factor on 3y
   beat_spy**, and its lift over the base rate is a 2005–12 lift.
   Same note.
7. **The columns v1.4 added lower forest PR-AUC by 0.01–0.02 on 3y
   beat_spy** (15 of 16 years). Same note.
8. **Large excess return (`fwd_3y_excess_cagr >= 0.08`) showed no
   skill** across 120 xgboost configurations and a forest.
   [note](notes/2026-09-derived-label-cells.md)
9. **The universe loses to SPY:** over walk-forward test rows the mean
   `fwd_3y_excess_cagr` is −0.11 and 36% beat SPY (unweighted; smoke
   test, scratch ledger). An excess return of picks is read against
   zero, not against the average row.
10. **Scores are not probabilities.** Forest Brier beats the no-skill
    reference in 5–10 of 16 years in the compounder cells.
11. **In the primary cell no feature set beats the 112 rank columns,
    and most of the signal is three of them.** Sector ranks add
    nothing; the 15 technical ranks alone come within 0.005 PR-AUC;
    without `vol_12m_rank`, `vol_36m_rank` and
    `conservative_score_rank` forests fall to the single factor's
    p@20 (0.39); 60 raw technical and trend columns lower PR-AUC by
    0.011–0.015. Every arm is at the base rate for 2019 entries.
    [note](notes/2026-09-29-feature-sets-dd-entry.md)
12. **Hyperparameters barely matter inside a family; p@20 differences
    under 0.03 are noise** (standard error of a pooled p@20 over 320
    picks). Rank on PR-AUC and the 2013–20 half.
    [note](notes/2026-08-beat-spy-v11-families.md)

Found on v1.0/v1.1 and not re-run since:
[earlier work](notes/2026-08-earlier-work.md),
[v1.1 model families](notes/2026-08-beat-spy-v11-families.md).

## Open questions

- Which label serves best for beating the market? Lift over a cell's
  own base rate cannot say. `pick_outcomes` is the screen,
  `vml-backtest` the yardstick of record.
- Do the volatility ranks measure calmness itself or stand in for
  something the fundamentals measure worse? And which of the raw
  technical and raw trend columns lowers PR-AUC? Neither changes the
  feature set; the second has a proposed two-arm sweep (note of
  2026-09-29).
- Are 20 picks 20 stocks? About 15, for the one baseline measured.
- Quarter identifier or stock information in the v1.1 ranks (5 above)?
  Low priority: it changes nothing about what runs on v1.4.

## Plan

In full, with the reasoning: [notes/2026-09-28-plan.md](notes/2026-09-28-plan.md).
The queue an agent works from is `experiments/queue.toml`.

1. Done 2026-09-29: the feature set for the primary cell is the
   `ranks` group (112 columns).
2. `baseline_pick_outcomes_3y`, then `forest_label_rungs_dd_entry_3y`:
   the single-factor bar and nine label rungs, read on pick outcomes.
3. Parameter search per family in the primary cell, equal budgets,
   ranked on fold-mean PR-AUC (a sweep summary's `pr_auc` is pooled
   and reads about 0.05 lower) and worst-seed 2013–20 p@20. Queued:
   `{forest,lgbm,xgb}_random_search_dd_entry_3y`, 40 draws each, one
   seed; then the top five of each on three seeds.
4. One candidate per surviving label: a regular config through
   `vml-run` (saves the fold bundle), `vml-promote`, `vml-backtest`
   with one portfolio template and buys ending 2020-12-31, then one
   final eval, then `vml-train-deploy`.
5. Calibration for the family that wins, before the final eval.

Decisions waiting for Carter: `cost_bps` and the investability filter
for the backtest template.

## Sealed holdout record

From `reports/final_evals.csv` (19 looks; the counts are part of every
holdout number). PR-AUC against the base rate, holdout test year in
brackets:

| cell | looks | what the looks showed |
|---|---|---|
| 2y cagr_ge_0 (v1.0 [2022], v1.1 [2022]) | 3 + 2 | PR-AUC 0.62–0.68 vs base 0.51 |
| 1y cagr_ge_0 (v1.1 [2023]) | 3 | PR-AUC 0.59–0.65 vs 0.51 |
| 1y beat_spy (v1.1 [2023]) | 3 | 0.29–0.31 vs 0.27, barely any skill |
| 2y beat_spy (v1.0, v1.1 [2022]) | 1 + 2 | technicals 0.20 vs 0.21 (**none**); valuation 0.26 |
| 5y beat_spy (v1.1 [2019]) | 2 | technicals 0.18 vs 0.17 (**none**); valuation 0.24 |
| 5y cagr_ge_0 (v1.1 [2019]) | 2 | 0.66–0.68 vs 0.50 |
| 2y cagr_ge_8 (v1.0) | 1 | p@20 0.35 vs 0.30 |

The Aug 24 batch opened 12 looks in ~50 minutes, comparing
technicals-vs-valuation pairs on the holdout. That is the pattern the
one-look-per-cell rule now prevents. Read those cells as consumed. The
one consistent signal: **technical-rank models had no holdout skill on
the relative (beat_spy) labels, and valuation/trend models kept some.**

## Process

Rules learned the hard way are in CLAUDE.md ("Before writing a
conclusion"); the incidents behind them are in
[notes/process-issues.md](notes/process-issues.md). The session log
up to the split is in
[notes/session-log-2026-09.md](notes/session-log-2026-09.md).
