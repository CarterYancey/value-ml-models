# Decision log, continued from 2026-11-26

This file continues [the decision log begun on 2026-09-29](2026-09-29-decisions.md).
Carter closed that file on 2026-11-26 and asked that nothing more be
added to it. The numbering continues here, and the rules in that
file's header still hold: one numbered entry per decision, newest
last, with the reason and what it rests on. Results are in the
[logbook](../logbook.md) and the notes it links to.

### 73. The Foamex move is not accepted as real; upstream is asked to investigate; the first decision log is closed

*What happened (2026-11-26):* Carter read decision 72 and rejected its
conclusion. A 400-fold return in five months is not something that
happens, whatever the vendor's own record says. He asked for a note
for upstream to investigate further, and that no more entries be added
to the decision log of 2026-09-29.

*What decision 72 rested on, and what it did not.* The check behind
"the move is real" used Sharadar's price table, Sharadar's daily
market value and Sharadar's corporate-action table, which are three
views of one vendor's data, and the public record of the
reorganization, which says the equity survived but not what it traded
at in January 2006. No quote from an independent source was checked.
A 451-fold move from an adjusted close of 4 cents on 2006-01-03 to
18.04 dollars on 2006-05-01, from a price the vendor records to the
nearest cent, is the kind of result that is a data question first and
a finding second (CLAUDE.md, "a surprising positive").

*Decided (Carter):*

1. **The Foamex price path is an open data question for upstream.**
   The sentence "the move is real" in decision 72 is withdrawn. The
   move is recorded as unverified, and the note
   [upstream request: the Foamex price path](2026-11-26-upstream-foamex-price-check.md)
   says what was seen, what was checked here and what upstream is
   asked to check. Until upstream answers, the W70 run of round 6
   rests on an unverified price and every record that cites it says
   so. Nothing in this repo may correct the price (invariant 4 and
   the dataset rule: data fixes are upstream changes).
2. **Decisions are logged in this file from now on.** The log of
   2026-09-29 is closed at decision 72 and is not edited again, not
   even for a pointer; agents.md, GLOSSARY.md and findings.md point
   here instead.
3. **What does not change.** The CAGR stays the metric of record for
   a backtest (decision 72, items 1 and 2). The price-floor question
   (decision 71.3) stands, with one more reason behind it: whether or
   not the Foamex path is right, a filter that admits a 1-cent stock
   admits the one kind of row most likely to carry a data error.

### 74. dataset_v1.5.1: the program for the new features and labels, and how its arms are judged

*What happened (2026-11-26):* Upstream shipped `dataset_v1.5.1` (v1.5
code on the 2026-11-21 snapshot). It adds 69 feature columns in three
places (the fundamental-history family, book-value and share-count
trends with the loss history in the trend family, fourteen 8-K event
counts), 37 rank columns for the continuous ones, and 36 full-path
label columns (max run-up, days to the high and the low, the
path-average return, realized volatility, and SPY's own path over the
same window). data/versions.md has the row. Carter asked for several
experiments with the new features and labels, across models.

*What was checked first.* The 8-K counts are an era marker: item
numbering changed in August 2004, and on this build the officer-change
count averages 0.01 a row in 1997–2003 and 2.2 from 2005 on
(`events_8k_days_12m` 5 against 15). A tree given them can read the
training era off the count. The 5y history statistics are mostly NULL
before 2001. The base rate of "path-average return beat SPY's" runs
within 0.05 of `label_3y_beat_spy` in every year.

*Decided:*

1. **Every run of the program is on `dataset_v1.5.1`, and the control
   is rerun there.** The control is the candidate's forest
   configuration (decision 24: entropy, depth 4, 490 trees, leaf 72,
   seed 23) on the 112 rank columns v1.4.1 had, trained on all rows
   and read inside the 100k floor on the same-size screen (top 10 a
   quarter, 2 per sector, peers in 5% bands of `log_marketcap_rank`;
   `universe_scope = "test"`, the arrangement of the candidate's
   screens). No v1.4.1 number is compared with a v1.5.1 number
   (decisions 54, 55).
2. **Feature arms, cell C**, the candidate's forest, one seed, then
   LightGBM (the two sets of 2026-11-25) and XGBoost (set1 of the
   2026-09 search, on CPU) on the first three: fs0 the 112 old ranks;
   fs1 all 149 ranks; fs2 fs1 plus the 18 new columns upstream ships
   unranked (quarters since the own peaks, `revenue_vs_5y_peak`, the
   ten-year loss record, the share-count and book-value up-shares, the
   loss history); fs3 fs0 plus the fundamental-history ranks alone;
   fs4 fs1 plus the fourteen 8-K counts; fs5 fs0 plus the 8-K counts
   alone.
3. **Label arms**, the forest on fs1, one seed, the same screen, with
   the path outcomes reported for every pick: the endpoint-free "beat
   SPY" `fwd_3y_path_avg_return > fwd_3y_spy_path_avg_return` (needs
   the column-vs-column condition added to the label grammar on
   `claude/v151-support`); the path-positive "not a loser"
   (`fwd_3y_path_avg_return >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`);
   "upside without a crash" (`fwd_3y_max_runup >= 0.5 & ...< 0.3`);
   the market-relative "not a loser" (`fwd_3y_cagr >= 0 &
   fwd_3y_max_drawdown_from_entry <= fwd_3y_spy_max_drawdown_from_entry`);
   "beat SPY on the path without a crash"; and cell C beside them.
   Single-factor bars, majority and random baselines are run in every
   new cell before any of its numbers is read.
4. **How an arm is judged** (decision 50, unchanged): the screen's
   lead over same-size peers on the 3-year CAGR and the share of
   losers, paired by test year with the control, in both halves
   (2005–12, 2013–20). An arm is carried to three seeds when its mean
   yearly gain in lead is positive at about two standard errors and
   it is ahead in 10 or more of 16 years, with no half worse by more
   than its noise; a label arm is read on the same two outcomes, not
   on its own precision. The next step after seeds is a backtest
   (decision 51: a screen gain is not a money gain). p@20 and PR-AUC
   rank the arms as predictors of their label and nothing more.
5. **Predictions, written before the runs.** (a) fs1 within 0.02 of
   fs0 on p@20 and within 0.01 on the screen lead: the forest at depth
   4 with a fifth of the columns per split already has the level
   ranks that the history ranks restate. Rival: the own-history
   z-scores and the normalized yields are what a value investor reads
   and the forest has not had them; then fs1 and fs3 lead fs0 by 0.01
   or more in both halves. (b) fs4 and fs5 are no better than their
   parents on the screen and have a lower lead in 2005–08, where the
   training rows before 2005 carry the near-zero counts: the counts
   buy era, not quality. (c) LightGBM matches the forest within 0.01
   of p@20 on each set, as it did inside F50; XGBoost below both in
   2013–20 as in 2026-09. (d) The path-average labels have the same
   picks as their endpoint twins (screen precision within 0.03 and the
   same lead within 0.01): the path average and the endpoint agree on
   most stocks over three years, so the label buys little. Rival: the
   endpoint's noise is what the forest cannot learn, and the path
   label's p@20 lift over its base rate is 0.03 or more above cell C's.
   (e) "Upside without a crash" is learned as calm (picks with a low
   realized volatility) and its picks earn no more than cell C's.
6. **What is not run.** No holdout look, no deployment change, no
   backtest before an arm has passed item 4 at three seeds. Nothing
   with the 8-K counts is carried forward unless it passes item 4 with
   its 2005–08 lead no lower than its parent's.
