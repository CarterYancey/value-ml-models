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

### 77. The counts lose money in both arrangements: the v1.5.1 program closes

*What happened (2026-11-26):* the four backtests of decision 76 ran
(2.3 minutes each; **peak RSS 12.4 to 13.8 GB of the sandbox's 14**,
the widest dataset yet). Seed 23, buys 2005–2020 on 192,000 of
deposits, valued 2023-12-29, SPY on the same deposits 732,110 (TWR
9.58%).

| arrangement | forest | final value | CAGR | TWR | worst drawdown | buys | lost money over 3y | lead over same-size peers, 3y |
|---|---|---|---|---|---|---|---|---|
| forest alone | fs0 (112 ranks) | 602,079 | 9.97% | 9.38% | −48.3% | 1,850 | 0.185 | +2.6 points |
| forest alone | fs5 (+ 8-K counts) | 571,211 | 9.52% | 9.17% | −45.8% | 1,858 | 0.197 | +3.6 points |
| blend (candidate's rule) | fs0 | 932,471 | 13.65% | 11.76% | −41.0% | 1,741 | 0.215 | +5.2 points |
| blend | fs5 | 851,928 | 12.89% | 11.24% | −40.2% | 1,760 | 0.212 | +5.2 points |

The fs5 forest alone ends with 5.1% less money than fs0, the fs5 blend
with 8.6% less. The equity curves say when: the forest-alone fs5
portfolio was 7% ahead at the end of 2015 (271,229 against 253,112),
level at the end of 2018 and 4% behind at the end of 2020 (474,028
against 493,540); the blend with fs5 was behind from 2015 on (290,907
against 299,156; 677,472 against 728,211 at the end of 2020). The
buys' lead over same-size peers is a point higher with the counts in
the forest-alone pair, as the screen said, and the same in the blend.

The fs0 blend on `dataset_v1.5.1` ends with exactly the v1.4.1
candidate's final value (932,471; 728,211 at the end of 2020). That
is a measurement, not a comparison for a conclusion: the builds share
the snapshot and the 112 rank columns' values (data/versions.md), so
the same seed gives the same forest and the same trades. It says the
v1.5.1 control is the candidate.

*Predictions of 76.3.* Both contradicted, downward: the forest-alone
pair is 5.1% apart, not within 3%, and the blend pair 8.6%, not within
2%. The rival (fs5 5% or more above) is rejected. The pattern of
decision 51 holds a third time, and more strongly: a lead over
same-size peers on the screen, +1.1 points a year at three seeds, and
a point more on the backtest's own buys, became less money. The lead
was earned in 2011–2015, when the account was small; the holdings of
2016–2020, when it was large, did worse. Why the counts' picks did
worse then is open and not pursued: the counts are not carried.

*Decided:*

1. **The 8-K counts are not carried** into the candidate's forest, by
   decision 74.6 (losers) and by the money (this decision). The arm is
   closed; the record is the three-seed screen and these four runs.
2. **The v1.5.1 program is closed.** On this build, in cell C: no new
   column set, no new label and no booster improves on the candidate's
   forest on the 112 old ranks. The path-average twin of cell C is an
   equivalent label. The market-relative labels are not learnable by
   the forest here (below a trivial bar). The dataset of record for new
   work is `dataset_v1.5.1`, and the candidate's record on it is the
   v1.4.1 record to the dollar; the candidate's legs are not refit.
3. **Nothing is promoted as a candidate change.** Promoted for the
   record: the feature sweep, the seeds sweep, the label sweep, the
   tuned-LightGBM sweep and the four backtests.
4. **A backtest on v1.5.1 peaks at 13.8 GB.** No backtest runs on this
   build with anything else in memory, and no chain of them runs
   unattended until the backtest's memory is cut (TODO). The runs
   finished; a wider build would not.
5. **What goes to Carter.** Nothing needs a decision from this program.
   The open decisions of 2026-11-25 stand (the larger-half filter, the
   training cutoff, the F50 portfolio, the price floor, the Foamex
   request). One observation for the upstream list: the two counts the
   forest used were earnings releases and officer changes in the
   trailing year; the other twelve were idle.

### 78. Carter's second request of 2026-11-26: run-up labels, fundamentals without price, and a plan for the rare region

*What happened (2026-11-26):* Carter read the close of the v1.5.1
program and asked for more. Three labels to start from
(`fwd_3y_max_runup >= 0.5 & fwd_3y_max_drawdown_from_entry < 0.3`,
`fwd_3y_max_runup >= 0.75`, `fwd_3y_cagr >= 0.2 |
fwd_3y_max_drawdown_from_entry <= fwd_3y_spy_max_drawdown_from_entry`)
with other values and horizons; new feature sets that lean less on the
rank group and leave out volume and momentum, so that the models work
from fundamentals, and in particular from the fundamental-history
columns (`roe_5y_z`, `revenue_vs_5y_peak`, …) beside other
fundamentals. His concern: a model given every column up front picks
the dominating ones (momentum, size, volatility) and never finds the
columns that separate the rare region, stocks with a strong record that
have fallen hard and recover within a few years. If features and cells
are not enough, build a plan for training a model to find that region
and start on it.

*What was checked first.* The first of his labels was cell L3 of
decision 74 (p@20 0.466 against a size bar's 0.528; lead +0.035, six
thousandths over cell C at 11 of 16 years; 2.5 points more losers).
That reading was on all 149 ranks; nothing of his second request has
run. Base rates among the liquid median-kind test rows of 2005–20
(200,472 rows): `max_runup >= 0.75` 0.371, `>= 1.0` 0.270,
`>= 1.0 & dd < 0.4` 0.193, his union label 0.318 (it is "did not fall
further than SPY" in 2006–08, where that clause alone is 0.31–0.35 and
`cagr >= 0.2` is 0.05, and "earned 20%" from 2009 on), `cagr >= 0.15 &
dd < 0.3` 0.213. At 5 years (folds 2007–18, 147,510 rows): cell C's
twin 0.403, `max_runup >= 1.0 & dd < 0.4` 0.281, `cagr >= 0.15 & dd <
0.3` 0.181. `revenue_vs_5y_peak` is `revenue / own 20q peak − 1` on
[−1, 0], not a ratio; `price_vs_5y_avg` is `price / own 5y average − 1`.
The region Carter describes exists and is small: inside the 100k floor,
stocks 40% or more below their 5-year high with operating cash flow
positive in 18 of the last 20 quarters are 32,052 test rows (16% of the
liquid rows), mean 3y CAGR +0.034 against −0.032 for all fallen stocks
and +0.004 for all liquid rows; 35% double within three years and 38%
lose half (all liquid: 27% and 38%). Add "net income positive in 7 of
the last 10 fiscal years" and the mean CAGR is +0.056 with 35% losing
half; but `ni_positive_years_10y` needs ten years of fundamentals and
the data start in 1998, so 89% of the 2005 rows have fewer than ten
years of history and the count is an era marker before 2008.
`ocf_positive_frac_20q` is stable across years (52–63% of rows at or
above 0.9). Training rows inside "F40 with a strong record" are thin
early: fold 2006 has 705 rows (effective size 20), fold 2012 18,052
(520). A model trained only there starves before 2013, which is what
the fallen-stock program found (decision 62). sklearn's forest routes
NULLs natively, so raw feature columns need no imputation.

*Decided:*

1. **The judging rule is unchanged** (decision 74.4): the screen's lead
   over same-size peers on the horizon's CAGR and the share of losers,
   paired by test year with the control in the same sweep, both halves;
   carry to seeds on the 74.4 rule, then a backtest. The control is the
   candidate's forest on cell C with the 112 old ranks (fs0), seed 23,
   `universe_scope = "test"` inside the 100k floor, rerun inside every
   sweep so each pairing is within one file. A label arm is read on the
   same two outcomes and on what its picks did on cell C, never on its
   own precision; p@20 against its cell's bars says only whether the
   label is learnable at all.
2. **Sweep A, `forest_fund_labels_3y`**: six cells × five feature sets,
   the candidate's forest, seed 23, 30 runs. Cells: C (control); Carter's
   three; `max_runup >= 1.0 & dd < 0.4` ("doubled without a crash");
   `cagr >= 0.15 & dd < 0.3` (the and-form of his third idea: a real
   gain without a crash; the or-form mixes two populations). Feature
   sets: fs0 the 112 old ranks; fs1 every raw fundamental column, no
   technical, events, classification or meta family (193 columns: the
   stock's own ratios, growth, trend, history, solvency and quality
   scores, no price, size, volume or volatility); fs2 the rank group
   without the 15 technical ranks plus the 28 unranked history columns
   (162); fs3 a compact own-history set of 74 raw columns, the
   fundamental-history and relative-value families with the dividend
   record, the loss and cash-flow histories and 24 core ratios
   (valuation, profitability, solvency, size by assets); fs4 fs3 plus
   the three columns that place the price against the stock's own past
   (`dist_5y_high`, `dist_52w_high`, `price_vs_5y_avg`), 77: the fall
   itself, with no momentum, volume or volatility column.
3. **Sweep B, `baseline_fund_labels_3y`**: the bars in the four cells
   that have none (ten single-factor rank bars, the eight of decision 74
   plus the least-fallen and the own-history return on equity), 40 runs.
4. **Sweep C, `forest_fund_labels_5y`**: the 5-year horizon on folds
   2007–18, four cells (C's twin, `max_runup >= 1.0 & dd < 0.4`, `cagr
   >= 0.15 & dd < 0.3`, `max_runup >= 1.0`) × fs0, fs1, fs4, 12 runs,
   read on the 5-year CAGR lead and 5-year losers with the 3-year
   outcomes reported beside them; halves 2007–12 and 2013–18.
5. **Predictions, written before the runs.** (a) fs1 in cell C is
   0.08–0.12 below fs0 on p@20 (the theory-led sets of 2026-09-30 were
   0.09–0.15 below), its lead within 0.02 of fs0's and its losers 3–6
   points higher, with utilities and REITs over-represented: without
   price columns the forest learns balance-sheet calm. Rival: with the
   history z-scores and the relative yields that the 2026-09 sets
   lacked, fs1 matches fs0's lead with no more losers; then what the
   earlier sets missed was the history, not the price. (b) fs3 and fs4
   are no better than fs1 on p@20 (a forest at a fifth of the columns
   per split loses, not gains, from fewer columns); fs4 leads fs3 in
   2009–12 (the fall columns find the post-crash bounces) and has more
   losers over all 16 years. (c) `max_runup >= 0.75` is learned as
   volatility: its picks' realized volatility is above their peers',
   their CAGR lead is within 0.01 of zero or negative and their losers
   are above the peers'. The `>= 1.0 & dd < 0.4` cell's picks look like
   cell C's (cell C rate within 0.05) because the no-crash clause is
   what the forest can learn. (d) Carter's union label has a p@20 lift
   over its base rate of 0.10 or less, a lead within 0.01 of cell C's
   and no fewer losers. (e) At 5 years the cells order as at 3 years;
   the leads are larger in points and no larger against their noise.
   (f) No fundamentals-only arm passes 74.4 against the control on
   both outcomes. Rival: one does; then the history columns are what
   the forest lacked and it goes to seeds and a backtest.
6. **The plan for the rare region, started after sweeps A–C are read**,
   whatever they show, because Carter asked for it and the sweeps test
   features and cells only. The region is defined on feature columns
   (so a universe or a weight can name it; a label cannot): 40% or more
   below the 5-year high, operating cash flow positive in 18 of the
   last 20 quarters, inside the 100k floor. (i) *Emphasis weights*: a
   harness field that multiplies the mandatory sample weights of the
   training rows inside a declared region by a factor (3 and 10 to
   start), hashed, disclosed in the report, test rows untouched. The
   model sees every row and keeps the common structure, but the splits
   are chosen as if the region were a third or a half of the data, so
   a column that separates recoveries inside it can win a split it
   never wins over all rows. Code on `claude/emphasis-weights` with
   tests; nothing else in the harness changes. (ii) *Universe arms*
   with `universe_scope = "all"` on the region, fs1 and fs4, cells C
   and "doubled without a crash", folds 2008–20 (fold 2007 has 2,148
   training rows inside the region): the starved version of the same
   idea, run so the two can be compared. (iii) *Random-subspace
   forests*: `max_features` 0.05 and depth 8 on fs1 and fs4, so that a
   split sees four to ten columns and cannot always take the dominant
   one; and LightGBM at `colsample_bytree = 0.1`. (iv) *The upper
   tail as a regression*: `lightgbm_regressor` with the quantile
   objective at 0.8 and 0.9 on `fwd_3y_cagr`, fs4, measured on `cagr
   >= 0.2`: the model is asked where the large gains are, not where
   the average is. (v) `year_balance = true` on the best arm of (i),
   so the market level of past years is not the prior. Each piece gets
   its own decision with predictions before it runs. What is not done:
   no label or weight read from a label column at training time beyond
   the target itself, no local ranking of features (invariant 4), no
   holdout look, no deployment change.
7. **Records.** Runs on `claude/lab-2026-11-26` (the same session); the
   results branch gets a second commit unless Carter has merged it by
   then, in which case a new results branch is cut off `Claude`.

### 79. The rare-region program: emphasis weights, the region as a universe, subspace forests, the upper tail as a regression

*What happened (2026-11-26, after sweep A of decision 78 was read).*
Sweep A (`forest_fund_labels_3y`, 30 runs; tables in
`docs/notes/2026-11-26-rare-region.md`) answered the feature-set half of
Carter's request. No fundamentals-only arm passes rule 74.4 against the
control (cell C × the 112 old ranks: lead +0.029 a year, losers 0.167).
The raw fundamentals without any price column (fs1, 193) lose 0.091 of
p@20, hold the lead within noise (−0.004, 7 of 16 years ahead) and take
6.7 points more losers; the forest builds itself on operating cash flow
instead of on the volatility ranks. The rank group without the technical
family plus the 28 unranked history columns (fs2, 162) matches the
control's lead exactly in cell C with 5.6 points more losers, and on the
three harder cells it is the only set ahead of its fs0 twin. The compact
own-history sets (fs3, fs4) are behind fs1 everywhere; the three fall
columns add nothing. The run-up label with a 40% drawdown cap (`fwd_3y_max_runup
>= 1.0 & fwd_3y_max_drawdown_from_entry < 0.4`) on fs0 is a one-month
reversal forest with a lead of +0.081 a year over the control (t 5.3, 15
of 16 years, both halves) and 38% losers against 17%; its picks' same-size
peers lose money a third to a half of the time in every year after 2008,
so the lead is over a bad neighbourhood, and it fails 74.4 on losers.

Sweep A also sharpens Carter's concern: the dominating columns are the
volatility ranks (a third of the importance in the control), and removing
them costs losers, not lead. A model that finds the rare region has to
keep the common structure (calm is good) and still split on what
separates recoveries inside the region. That is what the pieces below
try, in the order decision 78.6 set.

*The region* is the same in every piece: training rows inside the 100k
floor, 40% or more below their 5-year high (`dist_5y_high <= -0.4`), with
operating cash flow positive in 18 of the last 20 quarters
(`ocf_positive_frac_20q >= 0.9`). It is 16% of the liquid test rows
(32,052), mean 3-year CAGR +0.034 against −0.032 for all fallen liquid
rows and +0.004 for all liquid rows; 35% of its rows double, 38% lose
half. Training rows inside it are thin early (fold 2006: 705 rows,
effective size 20; fold 2012: 18,052 rows, effective size 520).

*What was added to measure the predictions.* The harness did not say
where a screen's picks come from, so `[pick_screen] region` was added
on `claude/emphasis-weights`: a region of feature-column filters whose
share among the picks, their peers and the top K the report carries as
the binary pick outcome `in_region` (`screen_mean_in_region`,
`screen_peer_mean_in_region`); a NULL counts as outside, a label can
never be a region, the field is part of the config hash like the rest
of the screen. Every sweep below declares the region there, and
`forest_fund_control_region_3y` (1 run) re-runs the control with it so
the control's share is known; its model-side numbers must reproduce
sweep A's run to the digit, which is a reproducibility check for free.

*The pieces, and what each one runs.* Each sweep uses the candidate's
forest configuration (decision 24) unless it says otherwise, seed 23, the
same 22 pick outcomes as sweep A, and is read inside the 100k floor on
the same-size screen. Feature sets in each: fs0 the 112 old ranks (the
control set), fs1 = sweep A's fs2 (162, ranks without the technical
family plus the unranked history columns; replaces the raw set, which
sweep A placed last), fs2 = sweep A's fs4 (77, the compact own-history
set plus the price against its own past). The control for every arm is
cell C × fs0 of sweep A, paired by test year; each arm is also read
against the same cell × set without the piece's change (sweep A's run).

1. **Emphasis weights** (`forest_emph3_fund_3y`, `forest_emph10_fund_3y`,
   9 runs each): `[emphasis] factor = 3 | 10` on the region, cells C,
   'doubled without a crash' (run-up ≥ 1.0 & dd < 0.4) and 'a real gain
   without a crash' (cagr ≥ 0.15 & dd < 0.3). The code is on
   `claude/emphasis-weights` (commit 340ded7, 19 tests, 564 in all): the
   factor multiplies the mandatory sample weight of the training rows
   inside the region after `year_balance`, test rows untouched, the
   region's share of each fold's training weight disclosed in the
   report, the field in the config hash and in bundles, so a deployment
   refit carries it.
2. **The region as a universe** (`forest_region_universe_3y`, 6 runs):
   `universe_scope = "all"` on the region, folds 2008–20, cells C and
   'doubled without a crash'. The starved version of piece 1: the model
   never sees a row outside the region, and its peers are the same-size
   rows inside it, so its lead is not comparable with the control's and
   is read against the region's own base rates (cell C's inside the
   region is reported per fold by the run).
3. **Random-subspace forests** (`forest_subspace_fund_3y`, 12 runs):
   `max_features = 0.05` (5–8 columns a split) at depth 8 with leaf 30,
   and at the candidate's depth 4 with leaf 72; cells C and 'doubled
   without a crash'. **LightGBM at `colsample_bytree = 0.1`**
   (`lgbm_colsample_fund_3y`, 6 runs; the r13 parameters otherwise,
   class weight 0.25).
4. **The upper tail as a regression** (`lgbm_quantile_fund_3y`, 6 runs):
   `lightgbm_regressor`, quantile objective at alpha 0.8 and 0.9 on
   `fwd_3y_cagr`, evaluated on the cell `fwd_3y_cagr >= 0.2`, fs0, fs1,
   fs2. The score is a predicted CAGR, not a probability: no Brier, no
   calibration.
5. `year_balance = true` on the best arm of piece 1, in its own decision,
   if piece 1 produces an arm worth it.

*Predictions, written before any of it runs.*

- (a) Emphasis ×3 in cell C on fs0: lead within 0.01 of the control's,
  losers within 2 points, and the share of its picks inside the region
  (`screen_mean_in_region`) no more than 10 points above the control's
  (the control's share is measured by `forest_fund_control_region_3y`
  and is predicted below 0.15: the control buys calm stocks near their
  highs). The rival, which is Carter's hypothesis: the region's columns
  win splits they never won, the picks inside the region rise 10 points
  or more above the control's share, and the lead is 0.01 or more above
  the control's in both halves at the same losers. ×10 moves further in the
  same direction as ×3 and costs losers (3 points or more), because at
  ×10 the region is near half the training weight in the late folds and
  the forest's prior becomes "fallen".
- (b) On fs1 and fs2, emphasis changes the lead by less than its noise
  (se ≈ 0.01) in cell C; in 'doubled without a crash' it lowers the
  lead, because the reversal columns that carry that cell on fs0 are not
  in those sets and the region adds fallen rows that do not recover.
- (c) The universe arms: lead over in-region peers positive in 10 or
  more of 13 years for cell C on fs0 (the fallen-stocks finding of
  decision 63 on a different region), losers 0.30 or more, and nothing
  on fs1 or fs2 ahead of fs0 inside the region. The emphasis arm of
  the same cell has fewer losers than the universe arm in every year
  they share.
- (d) Subspace forests: p@20 falls 0.03–0.06 below the candidate's forest
  on fs0 (the forced splits on weak columns dilute the volatility
  signal); the lead is within noise of the control's and losers 2–4
  points higher. Depth 8 beats depth 4 on p@20 and not on the screen.
  Rival: the subspace forest finds the region's columns and its picks'
  share inside the region is 10 points or more above the control's at
  the same losers. LightGBM at colsample 0.1 behaves like
  the subspace forests.
- (e) Quantile regression at 0.8 and 0.9: screened on `cagr >= 0.2`, the
  picks are high-volatility small stocks (realized volatility 0.5 or
  more, like the run-up cell's), losers 0.35 or more, and the lead
  over same-size peers is positive but no more than the run-up cell's;
  alpha 0.9 is more extreme than 0.8 on every one of those. Not a
  candidate for a portfolio; the question it answers is whether asking
  for the tail finds different stocks than asking for calm, and the
  prediction is yes.
- (f) Over the whole program: no arm passes rule 74.4 against the
  control on both outcomes. The arm most likely to come closest is
  emphasis ×3 on fs0 in cell C. If an arm does pass, three seeds and a
  backtest follow in a new decision; if none does, the program's
  finding is that the rare region does not carry a 3-year edge that
  the harness can find with weights, universes or subspaces, and the
  next step belongs to the label (a recovery label measured inside the
  region, decision 63's open question) or to upstream data.

*Records.* `claude/emphasis-weights` is merged into the lab branch
between chains (the main checkout's code is not changed while a sweep
runs); the six configs and this decision are checkpointed before the
chain starts; sweeps B and C of decision 78 are read when they finish
and do not change this plan. What is not done: no label or weight read
from a label column at training time beyond the target, no local feature
derivation, no holdout look, no deployment change.

### 80. The rare-region program's verdict: the region is the market's recovery, and every model that buys it loses

*2026-11-27.* Chain 2 of decision 79 finished at 04:30 UTC: 49 runs in
seven sweeps, read against the control (cell C × the 112 old ranks,
the candidate's forest at seed 23: lead over same-size peers +.029 a
year, losers .167, p@20 .747) and, where a twin exists, against the
unemphasized arm of sweep A. Tables and per-sweep readings are in
[the rare-region note](2026-11-26-rare-region.md).

*Predictions of 79.* (a) held and Carter's rival failed: emphasis ×3 in
cell C on fs0 moves the lead −.002, losers −0.2 points and the picks'
share inside the region not at all (.006, the control's). The ×10
clause was half right: the lead fell further (−.006) but losers fell
0.6 points instead of rising 3; with the region near half the late
folds' training weight the forest put `dist_5y_high_rank` and
`price_vs_5y_avg_rank` third and fourth and used them to avoid the
region. (b) held in cell C (every change inside noise) and was right
for the wrong reason in 'doubled without a crash': the lead fell on
fs0 (−.046 and −.079, t −5.6 and −5.8), the set with the reversal
columns, not on fs1 or fs2. (c) held on every count but a tie: inside
the region the forest leads in-region peers in 10 of 13 years, losers
.331, fs1 and fs2 not ahead of fs0, and the emphasis arm has fewer
losers than the universe arm in 12 of 13 shared years (equal in 2020).
(d) held in substance: subspace forests keep the lead inside noise and
add 2–3 points of losers; depth 8 beats depth 4 on p@20 only (depth 8
lost .025 of p@20, under the predicted .03–.06; depth 4 lost .113,
over it); LightGBM at colsample 0.1 behaved alike on fs1 and fs2 and
not on fs0 (−.022). The rival failed everywhere: no arm's share inside
the region rose 10 points at the control's losers. (e) held on
volatility (.71–1.03), losers (.48–.61) and the comparison with the
run-up cells, and failed on the sign of the lead (−.068 to +.025, five
of six at or below zero). (f) held: no arm passes rule 74.4.

1. **The verdict.** No arm of the program passes rule 74.4 against the
   control on both outcomes, so no seeds and no backtest follow. The
   program's finding, as 79(f) framed it: the rare region — liquid,
   40% or more below its 5-year high, cash flow positive in 18 of 20
   quarters, 16% of the liquid rows — does not carry a 3-year edge
   that the harness can find with training weights, a universe,
   subspace forests, column sub-sampling or an upper-tail regression.
2. **What the region is** (measured on every test row 2008–2020, the
   folds where its columns exist). Its rows earn a mean 3-year CAGR of
   .019 against .034 for all liquid rows, with 41% losers against 37%,
   40% halvings against 34%, and 18.5% doublers against 15.9%: wider
   tails, lower mean. By year it earns .09–.18 in 2008–2012 and .15 in
   2020 and loses in every year from 2013 to 2018 (−.02 to −.19). The
   region pays when the market recovers from a crash and loses through
   a long rise. "Strong history, steep fall, recovers" describes the
   region's good years; the recovery is the market's, and the thing
   that separates 2009 from 2014 inside the region is not in the row.
3. **Every selection that buys the region loses, and every selection
   that leads avoids it.** The picks' share inside the region and
   their share of losers rise together in all 49 runs: .006 and 17%
   (the control), .05–.07 and 19–21% (the fs1 arms), .27–.34 and
   36–41% (the reversal forests), .47–.86 and 44–61% (the compact-set,
   universe and quantile arms). Inside the region the forest does what
   it did inside F50 (decision 63): it finds the fallen stocks that
   fall least (`dist_5y_high_rank`, `price_vs_5y_avg_rank`, the
   volatility ranks), leads in-region peers by 4 points a year, and
   its picks earn .062 against the control's picks' .121 with three
   times the losers; they double less often than their peers (.117
   against .145).
4. **Given the region's columns and more of its weight, the forest
   learns to avoid it.** This is the answer to Carter's concern that
   dominant columns hide the region's columns. At emphasis ×10 the
   region's own columns rose to third and fourth importance in cell C
   and the picks' share inside the region stayed at .006; with the
   volatility ranks absent from 19 of 20 splits (subspace) no column
   emerged that discriminates inside the region, and the same columns
   led at a third of the weight. The forest was never failing to see
   the region; the region's label rate for 'not a loser' is below the
   rest of the data's, and the forest reads it correctly.
5. **The own-history valuation columns are real and are not a
   selection.** `sales_yield_vs_5y_median_rank`,
   `tangible_book_to_market_vs_5y_median_rank`,
   `earnings_yield_5y_peak_rank`, `book_to_market_5y_pctile` and
   `earnings_yield_5y_avg_rank` are the top splits wherever the
   price-based columns are absent or the question is the upper tail
   (the universe on fs1, LightGBM at colsample 0.1 on fs1, the quantile
   model on fs1). In every such arm the lead is at best the control's
   (+.027 to +.044) with 2 to 31 points more losers. They say where the
   upside is scattered; they do not pick it out at 3 years.
6. **What is not run.** Piece 5 of decision 79 (`year_balance`) was
   conditional on piece 1 yielding an arm; it did not, so it is not
   built. Three seeds and a backtest are not run for any arm. The
   reversal forest ('doubled without a crash' on the 112 ranks,
   +.081 a year over the control, 38% losers, peers losing money in
   half the years after 2008) is recorded as a bad-neighbourhood arm,
   not followed.
7. **What follows.** The program is closed on the 3-year horizon. The
   evidence points upstream, not at the model: the region's good and
   bad years are the market's, so the column that would separate them
   is a market-state column per snapshot date (already on the upstream
   list, decision 73 and findings plan item 3), and the label that
   would name a recovery is a peer- or market-relative one measured
   inside the region (decision 63's open question, also upstream). A
   recovery label at 5 years inside the region is the one local
   experiment left; it is not run here because the region's rows
   before 2013 are too few to train on alone (effective size 588–1,231)
   and the 5-year folds end in 2018.

*Records.* Logbook entries for all seven sweeps; the rare-region note
holds every table; `forest_fund_labels_3y` (sweep A),
`forest_region_universe_3y` and `forest_emph3_fund_3y` are promoted as
the program's records (the sets, the region's own numbers, the
emphasis negative); the other configs of decisions 78 and 79 go into
`experiments/KEEP`. findings.md is rewritten; TODO.md gets a "Next,
after 2026-11-27" section. The results branch
`claude/results-2026-11-26` receives a second commit with the
emphasis and region code (`claude/emphasis-weights`), decisions 78 to
80, the notes and the records; Carter opens the pull request. What is
not done: no holdout look, no deployment change, no edit to a config
that has run.
