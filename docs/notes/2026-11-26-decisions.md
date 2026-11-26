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

### 75. The first reading of decision 74's sweeps, and two follow-ups before the records are written

*What happened (2026-11-26):* the five sweeps of decision 74 ran (68
runs, 101 minutes, peak 10.3 GB). Read from the ledger per test year,
2005–2020, paired with the control (fs0: the candidate's forest on the
112 old ranks, on `dataset_v1.5.1`, inside the 100k floor on the
same-size screen). The control: p@20 0.747, screen lead over same-size
peers +0.029 a year, losers 0.167 against the peers' 0.300.

*Feature arms (the forest, seed 23).* Mean yearly gain over fs0 in
lead / in losers (a negative loser figure is more losers), with the
standard error and the years ahead: fs1 +0.000 (0.004) 6/16 / −0.023
(0.012) 2/16; fs2 −0.001 (0.005) 6/16 / −0.022 (0.011) 3/16; fs3
+0.001 (0.004) 8/16 / −0.019 (0.011) 4/16; fs4 −0.005 (0.006) 4/16 /
−0.030 (0.015) 5/16; fs5 +0.010 (0.005, t 1.9) 10/16, positive in both
halves (+0.014, +0.007) / −0.017 (0.009) 3/16. Every arm that adds new
columns has 1.7 to 3.0 points more losers than the control and holds
fewer distinct stocks a year (21 to 23 against 25). In fs5 the forest
used two of the fourteen counts (`events_earnings_release_12m` 20th of
126 columns by importance, `events_officer_change_12m` 31st); nine of
the fourteen have an importance under 1e-4.

*Label arms (the forest on all 149 ranks).* Paired with cell C on the
same screen: the path-positive "not a loser" is the same arm (lead
+0.001 (0.003), losers +0.009 (0.012)); "upside without a crash" lead
+0.006 (0.007) 11/16, losers −0.025 (0.027), its picks' realized
volatility 0.317 against cell C's 0.254 and the peers' 0.401; the
endpoint-free "beat SPY" lead +0.002 (0.008), losers −0.052 (0.034),
2013–20 losers 0.284 against cell C's 0.156; the market-relative "not
a loser" (drawdown no deeper than SPY's) lead −0.004 (0.006), losers
−0.025 (0.020); "beat SPY on the path without a crash" lead −0.004
(0.006), losers −0.067 (0.027, t −2.5), 2013–20 losers 0.294. On
precision the four relative or run-up cells are below a single-factor
bar: path-beat 0.522 against the `log_marketcap` bar's 0.566 (base
0.410); run-up 0.466 against 0.528 (0.305); path-beat without a crash
0.409 against 0.503 (0.301); drawdown no deeper than SPY's 0.353
against the `vol_36m` bar's 0.475 (0.176). Cell C 0.753 and the
path-positive cell 0.772 are above every bar (0.741, 0.747).

*Boosters.* LightGBM with the two F50 sets: p@20 0.634–0.659, lead
+0.001 to +0.014, losers 0.184–0.220; XGBoost set1: 0.681 (fs0) and
0.650 (fs1), lead 0.014 and 0.011, losers 0.206 and 0.220.

*Predictions of 74.5.* (a) held: fs1 is within 0.006 on p@20 and
within 0.001 on the lead; the rival (fs1 and fs3 ahead by 0.01 in both
halves) is rejected. (b) held for fs4; contradicted for fs5 on the
lead, which is higher and higher in 2005–08 too (0.045 against 0.037 a
year); fs5's losers are worse, so it fails 74.4 all the same. (c)
contradicted: LightGBM is 0.09 to 0.11 below the forest on p@20, not
within 0.01. The F50 match did not carry to the full universe; the
2026-09 random search on v1.4 is the precedent (its best draws matched
the forest's p@20 and their picks were worse on every outcome), and
the F50 sets are small (7 leaves) where the 2026-09 draws were not.
XGBoost is below the forest in 2013–20 as predicted, but not below
LightGBM. (d) held: the path-average twin of cell C has the same picks
within 0.015 on screen precision and 0.001 on lead; the rival (a lift
over base 0.03 above cell C's) is rejected (0.330 against 0.325). (e)
half held: the run-up label's picks are calmer than peers and earn no
more than cell C's, but they are not calmer than cell C's picks.

*Decided:*

1. **No arm is carried under 74.4.** None is ahead of the control on
   both outcomes. The new columns bought nothing in cell C at seed 23,
   and every market-relative label is behind cell C on losers and
   below a trivial bar on precision: the forest on these columns learns
   an absolute floor (a positive endpoint without a 30% drawdown), not
   a comparison with SPY. That reading is a hypothesis until the seeds
   below are read.
2. **Two cheap follow-ups run before the records are written** (36 and
   12 minutes). (a) `forest_v151_features_seeds_3y`: fs0, fs1 and fs5
   at seeds 232 and 1776, to separate seed noise from the two
   patterns of seed 23 — fs5's lead and the loser penalty of the new
   columns. Prediction: fs5's three-seed mean gain in lead is under
   +0.005 and its losers stay above fs0's; fs1's loser penalty stays at
   0.01 or more. Rival: fs5's gain holds at +0.008 or more with its
   2005–08 lead no lower than fs0's; then the two counts carry
   information and the arm goes to Carter as a backtest question (an
   off-thesis trade: more return with more losers; 74.6 still bars a
   carry while its losers are worse). (b) `lgbm_v151_tuned_nonloser_3y`:
   LightGBM with r13 and r19 of the 2026-09 search (about 60 leaves,
   class weight 0.25) on fs0 and fs1. Prediction: p@20 within 0.02 of
   the forest's, the screen lead 0.01 or more below the forest's and
   more losers, as in 2026-09. Rival: a booster of this size matches
   the forest on the screen; then the model family is not what sets
   the picks.
3. **The control at three seeds is the v1.5.1 reference** for any later
   arm in cell C inside the floor (the candidate's own numbers are a
   v1.4.1 record and are not compared).

### 76. The 8-K counts hold at three seeds: the backtest that decision 75 said would follow

*What happened (2026-11-26):* `forest_v151_features_seeds_3y` ran fs0,
fs1 and fs5 at seeds 232 and 1776 (6 runs, 29 minutes). Three-seed
means, paired by test year with the control's three-seed mean: fs5's
gain in lead is +0.011 a year (se 0.005, t 2.4), ahead in 13 of 16
years, +0.013 in 2005–12 and +0.009 in 2013–20, and its 2005–08 lead
is not lower (0.040 against 0.034). The gain is +0.010, +0.011 and
+0.012 at the three seeds alone. Its losers are 0.187 against the
control's 0.173 (gain −0.014, se 0.010, t −1.5; −0.021 in 2005–12,
−0.007 in 2013–20). fs1: lead +0.002 (se 0.003), losers −0.015 (se
0.012), the first half carrying the penalty (−0.028, se 0.018). p@20
at three seeds: fs0 0.762, fs1 0.755, fs5 0.754.

`lgbm_v151_tuned_nonloser_3y` (4 runs, 33 minutes): r13 and r19 on
fs0 and fs1 reach p@20 0.719–0.747 (the forest's 0.747–0.753), with
the forest's PR-AUC, and a screen lead of −0.003 to +0.006 a year
against the forest's +0.029; losers 0.178–0.208 against 0.167–0.191;
their picks' mean path return 0.11–0.13 against the peers' 0.17.

*Predictions of 75.2.* (a) contradicted for fs5: the gain in lead did
not shrink below +0.005, it held at +0.011 at every seed with the
2005–08 lead no lower than the control's. The rival stands: the two
counts the forest used (earnings releases and officer changes in the
trailing year) carry information the 112 ranks do not. The loser
penalty of the new columns held for fs1 in the first half only, at
1.6 standard errors over all 16 years; it is noise or small. (b) held
and its rival rejected: a LightGBM of the 2026-09 size matches the
forest's p@20 and its picks have no lead over their peers. The model
family sets the picks, not the top-20 precision.

*Decided:*

1. **fs5 is not carried into the candidate** (74.4 needs both
   outcomes; 74.6 bars a carry of the counts while losers are worse).
   The question 75.2a reserved for Carter is answered with a
   measurement instead of a screen number: **the backtest runs now**,
   on the arrangement of record, because the gain in lead is beyond
   noise at three seeds, the era-marker prediction that was the reason
   for 74.6's bar failed, and a screen gain is not a money gain
   (decision 51). Nothing is promoted on the screen alone.
2. **Four backtests, seed 23, `dataset_v1.5.1`, buys 2005–2020 valued
   2023-12-29, Carter's rank floor, top 10 a month, 2 per sector, 35
   bps:** the candidate's blend (forest, momentum, return on capital by
   mean rank) with the fs0 forest and with the fs5 forest; and the
   forest alone, fs0 and fs5, under the same rule. The v1.4.1 record
   is not compared; the fs0 pair is the v1.5.1 control.
3. **Predictions.** The forest-alone fs5 portfolio ends within 3% of
   the fs0 portfolio on money, with a drawdown within 2 points: the
   screen's +1.1 points a year on the picks' 3-year CAGR does not carry
   into a monthly portfolio with costs (decision 51's pattern). Rival:
   it ends 5% or more above with the drawdown within 2 points; then the
   counts go to Carter as a change to the candidate's forest, with the
   blend's own pair saying how much of it survives the two factors.
   The blend pair is predicted to be within 2% of each other on money.
4. **Bundles** come from `vml-run` of four configs on v1.5.1: the two
   forests (`forest_nonloser_dd30_3y_v151`, `forest_nonloser_dd30_3y_events_v151`)
   and the two factor legs (`factor_mom_12_2_3y_v151`, `factor_roc_greenblatt_3y_v151`).
