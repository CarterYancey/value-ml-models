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

*Rewritten for readability on 2026-11-27; the substance is unchanged.*

*What happened (2026-11-26).* Carter read the close of the v1.5.1
program and asked for more. He named three labels to start from: a
run-up of 50% with no drawdown of 30% or more
(`fwd_3y_max_runup >= 0.5 & fwd_3y_max_drawdown_from_entry < 0.3`), a
run-up of 75% (`fwd_3y_max_runup >= 0.75`), and a CAGR of 20% or more
or a drawdown no deeper than the S&P 500's
(`fwd_3y_cagr >= 0.2 | fwd_3y_max_drawdown_from_entry <= fwd_3y_spy_max_drawdown_from_entry`).
He asked for other values and horizons too. He asked for feature sets
that lean less on the rank group and leave out volume and momentum, so
that the models work from fundamentals, and in particular from the new
columns that describe a stock's own history (`roe_5y_z`,
`revenue_vs_5y_peak` and the like) beside other fundamentals. His
concern was this: a model given every column up front picks the
dominant ones (momentum, size, volatility) and never finds the columns
that separate the rare region, meaning stocks with a strong record that
have fallen hard and recover within a few years. If features and labels
were not enough, he wanted a plan for training a model to find that
region, and work on it started.

*What was checked first.* The first of his labels was cell L3 of
decision 74. There it had a p@20 of 0.466 against 0.528 for a ranking
on size alone, a lead of +0.035 (six thousandths above cell C, ahead in
11 of 16 years) and 2.5 points more losers. That reading used all 149
rank columns, and nothing of his second request had run. The base rates
among the liquid, median-kind test rows of 2005 to 2020 (200,472 rows)
are: a run-up of 75%, 0.371; a run-up of 100%, 0.270; a run-up of 100%
with a drawdown under 40%, 0.193; his union label, 0.318; and a CAGR of
15% with a drawdown under 30%, 0.213. The union label changes meaning
with the market. In 2006 to 2008 it mostly says "did not fall further
than SPY", because that clause alone is 0.31 to 0.35 and "earned 20%" is
0.05; from 2009 on it mostly says "earned 20%". At five years (folds
2007 to 2018, 147,510 rows) cell C's twin is 0.403, the capped run-up
0.281 and the 15% CAGR with a drawdown cap 0.181. Two column definitions
matter: `revenue_vs_5y_peak` is revenue divided by its own 20-quarter
peak, minus one, so it lies in [−1, 0]; `price_vs_5y_avg` is the price
divided by its own five-year average, minus one.

The region Carter described exists and is small. Inside the 100k floor,
stocks 40% or more below their five-year high with operating cash flow
positive in 18 of the last 20 quarters make up 32,052 test rows, 16% of
the liquid rows. Their mean three-year CAGR is +0.034, against −0.032 for
all fallen stocks and +0.004 for all liquid rows. 35% of them double
within three years and 38% lose half (all liquid rows: 27% and 38%).
Adding "net income positive in 7 of the last 10 fiscal years" raises the
mean CAGR to +0.056 with 35% losing half. But that count needs ten years
of fundamentals, the data start in 1998, and 89% of the 2005 rows have
fewer than ten years of history, so the count marks the era before
2008. The cash-flow fraction is stable across years, with 52% to 63% of
rows at or above 0.9. Training rows inside the region are thin early:
fold 2006 has 705 rows with an effective size of 20, and fold 2012 has
18,052 rows with an effective size of 520. A model trained only there
starves before 2013, which is what the fallen-stock program found
(decision 62). The scikit-learn forest routes NULLs natively, so raw
feature columns need no imputation.

*Decided:*

1. **The judging rule is unchanged** (decision 74.4). An arm is judged
   on its picks' lead over same-size peers on the horizon's CAGR and on
   its share of losers, paired by test year with the control in the same
   sweep, in both halves of the period. An arm that passes goes to
   seeds, then to a backtest. The control is the candidate's forest on
   cell C with the 112 old ranks (fs0), seed 23, trained on all rows and
   read inside the 100k floor (`universe_scope = "test"`). It is rerun
   inside every sweep so that each pairing is within one file. A new
   label is read on the same two outcomes and on what its picks did on
   cell C, never on its own precision. Its p@20 against single-column
   rankings says only whether the label is learnable at all.
2. **Sweep A, `forest_fund_labels_3y`**: six labels, five feature sets,
   the candidate's forest at seed 23, 30 runs. The labels are cell C
   (the control), Carter's three, "doubled without a crash" (a run-up of
   100% with no drawdown of 40%) and "a real gain without a crash" (a
   CAGR of 15% with no drawdown of 30%, the and-form of his third idea;
   the or-form mixes two populations). The feature sets are: fs0, the
   112 old ranks; fs1, every raw fundamental column with no technical,
   event, classification or metadata family (193 columns: the stock's
   own ratios, growth, trend, history, solvency and quality scores, and
   nothing about price, size, volume or volatility); fs2, the rank group
   without the 15 technical ranks plus the 28 unranked history columns
   (162); fs3, a compact own-history set of 74 raw columns, being the
   fundamental-history and relative-value families with the dividend
   record, the loss and cash-flow histories and 24 core ratios; and fs4,
   fs3 plus the three columns that place the price against the stock's
   own past (`dist_5y_high`, `dist_52w_high`, `price_vs_5y_avg`), 77
   columns. fs4 sees the fall itself, with no momentum, volume or
   volatility column.
3. **Sweep B, `baseline_fund_labels_3y`**: single-column rankings on the
   four labels that have none. Ten rankings, the eight of decision 74
   plus the least-fallen stocks and the own-history return on equity.
   40 runs.
4. **Sweep C, `forest_fund_labels_5y`**: the five-year horizon on folds
   2007 to 2018. Four labels (cell C's twin, the capped run-up of 100%,
   the 15% CAGR with a drawdown cap, and the uncapped run-up of 100%) on
   fs0, fs1 and fs4, 12 runs. Read on the five-year lead and five-year
   losers with the three-year outcomes reported beside them. The halves
   are 2007 to 2012 and 2013 to 2018.
5. **Predictions, written before the runs.**
   (a) fs1 in cell C scores 0.08 to 0.12 below fs0 on p@20 (the
   theory-led sets of 2026-09-30 were 0.09 to 0.15 below). Its lead is
   within 0.02 of fs0's and its losers 3 to 6 points higher, with
   utilities and REITs over-represented, because without price columns
   the forest learns balance-sheet calm. The rival: with the history
   z-scores and relative yields that the 2026-09 sets lacked, fs1
   matches fs0's lead with no more losers, which would mean the earlier
   sets missed the history and not the price.
   (b) fs3 and fs4 are no better than fs1 on p@20, because a forest
   that already considers a fifth of the columns per split loses rather
   than gains from fewer columns. fs4 leads fs3 in 2009 to 2012, when
   the fall columns find the post-crash rebounds, and has more losers
   over all 16 years.
   (c) The 75% run-up label is learned as volatility: its picks'
   realized volatility is above their peers', their lead is within 0.01
   of zero or negative, and their losers are above the peers'. The
   capped 100% run-up label picks stocks like cell C's (a cell C rate
   within 0.05 of the control's), because the no-crash clause is what
   the forest can learn.
   (d) Carter's union label has a p@20 at most 0.10 above its base
   rate, a lead within 0.01 of cell C's and no fewer losers.
   (e) At five years the labels and sets order as at three years. The
   leads are larger in points and no larger against their noise.
   (f) No fundamentals-only arm passes the screen rule against the
   control on both outcomes. The rival: one does, which would mean the
   history columns were what the forest lacked, and that arm goes to
   seeds and a backtest.
6. **The plan for the rare region**, started after sweeps A to C are
   read, whatever they show, because Carter asked for it and the sweeps
   test only features and labels. The region is defined on feature
   columns, so that a universe or a weight can name it (a label
   cannot): 40% or more below the five-year high, operating cash flow
   positive in 18 of the last 20 quarters, inside the 100k floor. Five
   pieces, each with its own decision and predictions before it runs:
   (i) *Emphasis weights.* A new harness field multiplies the sample
   weights of the training rows inside a declared region by a factor
   (3 and 10 to start). The factor is in the config hash and disclosed
   in the report, and test rows are untouched. The model still sees
   every row and keeps the common structure, but its splits are chosen
   as if the region were a third or a half of the data, so a column that
   separates recoveries inside the region can win a split it never wins
   over all rows. The code goes on `claude/emphasis-weights` with tests
   and changes nothing else in the harness.
   (ii) *The region as a universe.* The same labels trained on the
   region's rows alone (`universe_scope = "all"`), on fs1 and fs4, for
   cell C and "doubled without a crash", folds 2008 to 2020 (fold 2007
   has 2,148 training rows inside the region). This is the starved
   version of the same idea, run so the two can be compared.
   (iii) *Forests that see few columns per split.* `max_features` 0.05
   at depth 8 on fs1 and fs4, so that a split considers four to ten
   columns and cannot always take the dominant one; and LightGBM with
   `colsample_bytree = 0.1`.
   (iv) *The upper tail as a regression.* `lightgbm_regressor` with the
   quantile objective at 0.8 and 0.9 on `fwd_3y_cagr`, on fs4, measured
   on the label "earned 20% a year". The model is asked where the large
   gains are, not where the average is.
   (v) `year_balance = true` on the best arm of piece (i), so that the
   market level of past years is not the model's prior.
   What is not done: no label or weight read from a label column at
   training time beyond the target itself, no local ranking of features
   (invariant 4), no holdout look, no deployment change.
7. **Records.** The runs go on `claude/lab-2026-11-26` in the same
   session. The results branch gets a second commit, unless Carter has
   merged it by then, in which case a new results branch is cut from
   `Claude`.

### 79. The rare-region program: emphasis weights, the region as a universe, subspace forests, the upper tail as a regression

*Rewritten for readability on 2026-11-27; the substance is unchanged.*

*What happened (2026-11-26, after sweep A of decision 78 was read).*
Sweep A (`forest_fund_labels_3y`, 30 runs; tables in
[the rare-region note](2026-11-26-rare-region.md)) answered the
feature-set half of Carter's request. No fundamentals-only arm passes
the screen rule against the control, which is the candidate's forest in
cell C on the 112 old ranks (lead +0.029 a year, losers 0.167). The raw
fundamentals without any price column (fs1, 193 columns) lose 0.091 of
p@20, keep the lead within noise (−0.004, ahead in 7 of 16 years) and
take 6.7 points more losers; that forest builds itself on operating
cash flow instead of the volatility ranks. The rank group without the
technical family plus the 28 unranked history columns (fs2, 162
columns) matches the control's lead exactly in cell C with 5.6 points
more losers, and on the three harder labels it is the only set ahead of
its fs0 counterpart. The compact own-history sets (fs3, fs4) are behind
fs1 everywhere, and the three fall columns add nothing. On fs0, the
label "doubled without a crash" (a run-up of 100% with no drawdown of
40%) produces a one-month-reversal forest with a lead of +0.081 a year
over the control (t 5.3, ahead in 15 of 16 years, in both halves) and
38% losers against 17%. The same-size peers of its picks lose money a
third to a half of the time in every year after 2008, so the lead is
over stocks that lose, and the arm fails the screen rule on losers.

Sweep A also sharpened Carter's concern. The dominant columns are the
volatility ranks, which carry a third of the importance in the control,
and removing them costs losers rather than lead. A model that finds the
rare region must keep the common structure (calm is good) and still
split on what separates recoveries inside the region. That is what the
pieces below try, in the order decision 78.6 set.

*The region* is the same in every piece: training rows inside the 100k
floor, 40% or more below their five-year high (`dist_5y_high <= -0.4`),
with operating cash flow positive in 18 of the last 20 quarters
(`ocf_positive_frac_20q >= 0.9`). It is 16% of the liquid test rows
(32,052 rows). Its mean three-year CAGR is +0.034, against −0.032 for all
fallen liquid rows and +0.004 for all liquid rows; 35% of its rows
double and 38% lose half. Training rows inside it are thin early: fold
2006 has 705 rows with an effective size of 20, and fold 2012 has 18,052
rows with an effective size of 520.

*What was added to measure the predictions.* The harness did not report
where a screen's picks come from, so a `region` field was added to the
pick screen on `claude/emphasis-weights`. It takes a list of filters on
feature columns and reports the share of the picks, of their peers and
of the top K that fall inside, as the binary pick outcome `in_region`
(`screen_mean_in_region`, `screen_peer_mean_in_region`). A NULL counts
as outside, a label can never be a region, and the field is part of the
config hash like the rest of the screen. Every sweep below declares the
region there. One extra run, `forest_fund_control_region_3y`, repeats
the control with the region declared, so the control's share is known.
Its model-side numbers must reproduce sweep A's run to the digit, which
is a reproducibility check at no extra cost.

*The pieces, and what each one runs.* Each sweep uses the candidate's
forest configuration (decision 24) unless it says otherwise, seed 23,
the same 22 pick outcomes as sweep A, read inside the 100k floor on the
same-size screen. The feature sets in each are fs0, the 112 old ranks
(the control's set); fs1, sweep A's fs2 (162 columns, the ranks without
the technical family plus the unranked history columns), which replaces
the raw set that sweep A placed last; and fs2, sweep A's fs4 (77
columns, the compact own-history set plus the price against its own
past). Every arm is paired by test year with the control, and also with
the same label and set in sweep A, which has the piece's change absent.

1. **Emphasis weights** (`forest_emph3_fund_3y` and
   `forest_emph10_fund_3y`, 9 runs each). The region's training rows
   carry 3 or 10 times their sample weight (`[emphasis] factor`), for
   cell C, "doubled without a crash" and "a real gain without a crash".
   The code is on `claude/emphasis-weights` (commit 340ded7, 19 tests,
   564 in all). The factor multiplies the mandatory sample weight of the
   training rows inside the region after `year_balance`; test rows are
   untouched; the report states the region's share of each fold's
   training weight; the field is in the config hash and in bundles, so
   a deployment refit carries it.
2. **The region as a universe** (`forest_region_universe_3y`, 6 runs).
   The region is the run's universe (`universe_scope = "all"`), folds
   2008 to 2020, for cell C and "doubled without a crash". This is the
   starved version of piece 1: the model never sees a row outside the
   region, and its peers are the same-size rows inside it. Its lead is
   therefore not comparable with the control's and is read against the
   region's own base rates, which the run reports per fold.
3. **Forests that see few columns per split** (`forest_subspace_fund_3y`,
   12 runs). `max_features = 0.05`, which is 5 to 8 columns a split, at
   depth 8 with leaves of 30 rows and at the candidate's depth 4 with
   leaves of 72, for cell C and "doubled without a crash". And
   **LightGBM with `colsample_bytree = 0.1`** (`lgbm_colsample_fund_3y`,
   6 runs), using the r13 parameters otherwise, with class weight 0.25.
4. **The upper tail as a regression** (`lgbm_quantile_fund_3y`, 6 runs).
   `lightgbm_regressor` with the quantile objective at 0.8 and 0.9 on
   `fwd_3y_cagr`, evaluated on the label `fwd_3y_cagr >= 0.2`, on fs0,
   fs1 and fs2. The score is a predicted CAGR and not a probability, so
   there is no Brier score and no calibration.
5. `year_balance = true` on the best arm of piece 1, in its own
   decision, if piece 1 produces an arm worth it.

*Predictions, written before any of it runs.*

- (a) Emphasis at three times the weight, in cell C on fs0: the lead is
  within 0.01 of the control's, losers are within 2 points, and the
  share of its picks inside the region is at most 10 points above the
  control's. The control's share is measured by
  `forest_fund_control_region_3y` and is predicted below 0.15, because
  the control buys calm stocks near their highs. The rival, which is
  Carter's hypothesis: the region's columns win splits they never won,
  the picks' share inside the region rises 10 points or more above the
  control's, and the lead is 0.01 or more above the control's in both
  halves at the same losers. Ten times the weight moves further in the
  same direction as three times and costs 3 points or more of losers,
  because at ten times the region is near half the training weight in
  the late folds and the forest comes to treat fallen stocks as the
  normal case.
- (b) On fs1 and fs2, emphasis changes the lead by less than its noise
  (a standard error of about 0.01) in cell C. On "doubled without a
  crash" it lowers the lead, because the reversal columns that carry
  that label on fs0 are not in those sets and the region adds fallen
  rows that do not recover.
- (c) The universe arms: the lead over in-region peers is positive in
  10 or more of 13 years for cell C on fs0 (the fallen-stocks finding of
  decision 63 on a different region), losers are 0.30 or more, and
  neither fs1 nor fs2 is ahead of fs0 inside the region. The emphasis
  arm for the same label has fewer losers than the universe arm in
  every year they share.
- (d) Subspace forests: p@20 falls 0.03 to 0.06 below the candidate's
  forest on fs0, because forced splits on weak columns dilute the
  volatility signal; the lead is within noise of the control's and
  losers are 2 to 4 points higher. Depth 8 beats depth 4 on p@20 and not
  on the screen. The rival: the subspace forest finds the region's
  columns, and its picks' share inside the region is 10 points or more
  above the control's at the same losers. LightGBM at `colsample` 0.1
  behaves like the subspace forests.
- (e) Quantile regression at 0.8 and 0.9, screened on a CAGR of 20%:
  the picks are small, high-volatility stocks (realized volatility 0.5
  or more, like the run-up label's), losers are 0.35 or more, and the
  lead over same-size peers is positive but no more than the run-up
  label's. The 0.9 quantile is more extreme than 0.8 on each of those.
  This is not a candidate for a portfolio. The question it answers is
  whether asking for the upper tail finds different stocks than asking
  for calm, and the prediction is yes.
- (f) Over the whole program, no arm passes the screen rule against the
  control on both outcomes. The arm most likely to come closest is
  emphasis at three times the weight on fs0 in cell C. If an arm does
  pass, three seeds and a backtest follow in a new decision. If none
  does, the program's finding is that the rare region does not carry a
  three-year edge that the harness can find with weights, universes or
  subspaces, and the next step belongs to the label (a recovery label
  measured inside the region, decision 63's open question) or to
  upstream data.

*Records.* `claude/emphasis-weights` is merged into the lab branch
between chains, so the main checkout's code does not change while a
sweep runs. The six configs and this decision are checkpointed before
the chain starts. Sweeps B and C of decision 78 are read when they
finish and do not change this plan. What is not done: no label or
weight read from a label column at training time beyond the target, no
local feature derivation, no holdout look, no deployment change.

### 80. The rare-region program's verdict: the region is the market's recovery, and every model that buys it loses

*Rewritten for readability on 2026-11-27; the substance is unchanged.*

*What happened (2026-11-27).* The chain of decision 79 finished at 04:30
UTC: 49 runs in seven sweeps. Each was read against the control (the
candidate's forest at seed 23 in cell C on the 112 old ranks: a lead of
+0.029 a year over same-size peers, losers 0.167, p@20 0.747) and, where
sweep A has the same label and set, against that run. The tables and
the reading of each sweep are in
[the rare-region note](2026-11-26-rare-region.md).

*How the predictions of decision 79 fared.*

- (a) held, and Carter's rival prediction failed. Emphasis at three
  times the weight in cell C on fs0 moved the lead by −0.002 and losers
  by −0.2 points, and left the picks' share inside the region at the
  control's 0.006. The clause about ten times the weight was half right:
  the lead fell further (−0.006), but losers fell 0.6 points instead of
  rising 3. With the region near half the late folds' training weight,
  the forest put `dist_5y_high_rank` and `price_vs_5y_avg_rank` third
  and fourth among its splits and used them to score the region's rows
  low.
- (b) held in cell C, where every change was inside noise, and was
  right for the wrong reason on "doubled without a crash". The lead
  fell on fs0 (by 0.046 and 0.079, t −5.6 and −5.8), the set that holds
  the reversal columns, and not on fs1 or fs2.
- (c) held on every count except a tie. Inside the region the forest
  led its in-region peers in 10 of 13 years with losers of 0.331; fs1
  and fs2 were not ahead of fs0; and the emphasis arm had fewer losers
  than the universe arm in 12 of 13 shared years, with a tie in 2020.
- (d) held in substance. The subspace forests kept the lead inside
  noise and added 2 to 3 points of losers. Depth 8 beat depth 4 on p@20
  only. Depth 8 lost 0.025 of p@20, less than the predicted 0.03 to
  0.06, and depth 4 lost 0.113, more. LightGBM with a tenth of the
  columns behaved the same way on fs1 and fs2 and not on fs0, where its
  lead was 0.022 below the control's. The rival failed everywhere: no
  arm's share inside the region rose 10 points at the control's losers.
- (e) held on volatility (0.71 to 1.03), on losers (0.48 to 0.61) and on
  the comparison with the run-up labels, and failed on the sign of the
  lead, which ran from −0.068 to +0.025 with five of six arms at or
  below zero.
- (f) held: no arm passes the screen rule.

*Decided:*

1. **The verdict.** No arm of the program passes the screen rule
   against the control on both outcomes, so no seeds and no backtest
   follow. The program's finding, as prediction 79(f) framed it: the
   rare region (liquid stocks 40% or more below their five-year high
   with cash flow positive in 18 of 20 quarters, 16% of the liquid
   rows) does not carry a three-year edge that the harness can find
   with training weights, a universe, subspace forests, column
   sub-sampling or an upper-tail regression.
2. **What the region is.** This was measured on every test row from
   2008 to 2020, the folds where the region's columns exist. Its rows
   earn a mean three-year CAGR of 0.019 against 0.034 for all liquid
   rows, with 41% losers against 37%, 40% halvings against 34%, and
   18.5% doublers against 15.9%. The tails are wider and the mean is
   lower. By year it earns 0.09 to 0.18 in 2008 to 2012 and 0.15 in
   2020, and loses in every year from 2013 to 2018 (−0.02 to −0.19).
   The region pays when the market recovers from a crash and loses
   through a long rise. "A strong history, a steep fall, a recovery"
   describes the region's good years. The recovery is the market's, and
   what separates 2009 from 2014 inside the region is not in the row.
3. **Every selection that buys the region loses, and every selection
   that leads avoids it.** Across all 49 runs the picks' share inside
   the region and their share of losers rise together: 0.006 and 17%
   for the control; 0.05 to 0.07 and 19% to 21% for the fs1 arms; 0.27
   to 0.34 and 36% to 41% for the reversal forests; 0.47 to 0.86 and
   44% to 61% for the compact-set, universe and quantile arms. Inside
   the region the forest does what it did inside F50 (decision 63). It
   finds the fallen stocks that fall least, using the distance from the
   five-year high, the price against the five-year average and the
   volatility ranks. It leads its in-region peers by 4 points a year,
   and its picks earn 0.062 against 0.121 for the control's picks, with
   three times the losers. Its picks double less often than their
   peers (0.117 against 0.145).
4. **Given the region's columns and more of its weight, the forest
   scores the region lower, not higher.** This answers Carter's concern
   that dominant columns hide the region's columns. At ten times the
   weight the region's own columns rose to third and fourth importance
   in cell C, and the picks' share inside the region stayed at 0.006.
   In the subspace forests, with the volatility ranks absent from 19 of
   20 splits, no column emerged that discriminates inside the region,
   and the same columns led at a third of the weight. The forest was
   never failing to see the region. The region's rate of "not a loser"
   is below the rest of the data's, and the forest reads that
   correctly.
5. **The own-history valuation columns are real, and they are not a
   selection.** `sales_yield_vs_5y_median_rank`,
   `tangible_book_to_market_vs_5y_median_rank`,
   `earnings_yield_5y_peak_rank`, `book_to_market_5y_pctile` and
   `earnings_yield_5y_avg_rank` are the top splits wherever the
   price-based columns are absent or the question is the upper tail:
   the universe on fs1, LightGBM with a tenth of the columns on fs1, and
   the quantile model on fs1. In every such arm the lead is at best the
   control's (+0.027 to +0.044) with 2 to 31 points more losers. The
   columns show where the upside is scattered. They do not pick it out
   at three years.
6. **What is not run.** Piece 5 of decision 79 (`year_balance`) depended
   on piece 1 producing an arm. It did not, so piece 5 is not built.
   Three seeds and a backtest are not run for any arm. The reversal
   forest ("doubled without a crash" on the 112 ranks: +0.081 a year
   over the control, 38% losers, peers losing money in half the years
   after 2008) is recorded as a lead over stocks that lose, and not
   followed.
7. **What follows.** The program is closed on the three-year horizon.
   The evidence points upstream rather than at the model. The region's
   good and bad years are the market's, so the column that would
   separate them is a market-state column per snapshot date, which is
   already on the upstream list (decision 73 and item 3 of the findings
   plan). The label that would name a recovery is a peer-relative or
   market-relative one measured inside the region, decision 63's open
   question, which is also upstream. A recovery label at five years
   inside the region is the one local experiment left. It is not run
   here because the region's rows before 2013 are too few to train on
   alone (effective sizes of 588 to 1,231) and the five-year folds end
   in 2018.

*Records.* Logbook entries exist for all seven sweeps, and the
rare-region note holds every table. Three sweeps are promoted as the
program's records: `forest_fund_labels_3y` (the labels and sets),
`forest_region_universe_3y` (the region's own numbers) and
`forest_emph3_fund_3y` (the emphasis result). The other configs of
decisions 78 and 79 are listed in `experiments/KEEP`. findings.md is
rewritten and TODO.md gains a section "Next, after 2026-11-27". The
results branch `claude/results-2026-11-26` receives a second commit
carrying the emphasis and region code from `claude/emphasis-weights`,
decisions 78 to 80, the notes and the records, and Carter opens the
pull request. What is not done: no holdout look, no deployment change,
no edit to a config that has run.

### 81. Why the candidate has not beaten the market, and what separates the explanations

*What happened (2026-11-27).* Carter asked the project's central
question. The goal is a model that beats the market over the long term
by learning the relationship between fundamentals and long-term
success, holding to the value investor's first rule, never lose money,
and accepting low recall for high precision. The models predict their
labels at precision well above the base rate, and the portfolios built
from them have not beaten the market in the backtests. Why, and what
has not been tried? The answer below rests on the candidate's own
record (`bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_v141`), the
control run of sweep A read against SPY by cohort year, and a survey of
every portfolio-level idea in the decision logs. The tables are in
[the note](2026-11-27-why-not-the-market.md).

*What was measured.*

1. **The candidate beat SPY for sixteen years and lost to it for six.**
   Its time-weighted return was 12.4% a year against SPY's 9.4% over
   2005 to 2020, and 7.1% against 15.3% over 2021 to 2026. It was ahead
   in 10 of the 16 calendar years to 2020 and in all four of SPY's down
   years, and behind in 5 of the 6 years since. Its money-weighted CAGR
   over the whole window is 12.2% against 13.2%, because the deposits
   make the account largest in the years it lost. The shortfall is a
   six-year event, not a sixteen-year one.
2. **The selection skill is real and it is a loser-avoidance skill.**
   Over 1,951 buys with a full three-year window, the buys led stocks of
   the same size by 4.5 points a year and 23% of them lost money against
   33% of their peers. On the walk-forward screen the picks' realized
   volatility was 0.25 against the peers' 0.36 and their drawdown 0.18
   against 0.29. The portfolio's monthly beta to SPY is 0.86, its
   correlation 0.93, and it captured 88% of SPY's up months and 80% of
   its down months.
3. **The skill only just covers a structural gap.** Equal-weighted
   stocks of the picks' own size trailed cap-weighted SPY by 3.8 points
   a year over the same buys, and the whole liquid universe by 10.3.
   The picks' lead over same-size peers (4.5) minus the band's gap to
   SPY (3.8) leaves 0.7 points a year over SPY before costs. On the
   screen the picks' mean three-year CAGR over the sixteen cohort years
   equals SPY's exactly (0.096 against 0.096): 3.3 points above SPY in
   the four crash-era cohorts of 2005 to 2008 and 1.1 below in the
   twelve cohorts of 2009 to 2020, in which SPY compounded at 10% to
   17%.
4. **In the 2019 to 2023 cohorts both terms failed at once.** The buys'
   lead over same-size peers fell to 0.3, 0.3, −2.5, +1.6 and −6.0
   points, and the band's gap to SPY widened to 5 to 12 points. Of the
   2021 buys, 72% had lost money a year later and 47% after three years;
   their peers did little better (45%). The model does not see the
   market's level: every forest's scores are highest at market tops
   (decision 46), its precision in cell C was 0.40 in 2006 and 0.25 in
   2007, and nothing in a row says that 2021 is a year to buy less.
5. **Precision on "not a loser" compresses the return distribution from
   both ends.** The label is met by 43% of liquid rows. The forest finds
   the calmest of them: fewer losers and fewer large winners. A
   portfolio of stocks that each earn 8% to 10% with few losses matches
   a cap-weighted index that earns 13% only when the index crashes
   often enough, which it did in 2005 to 2020 and not since.
6. **The structure, not the model, is the part that cannot keep up in
   2021 to 2026.** SPY beat the equal-weighted mean of its own thirty
   largest members in those years (decision 32.3). No equal-weighted
   selection from this universe could have kept pace. Three ideas that
   address the structure directly were proposed and never run as
   portfolios: a cap-weighted book of large caps with the forest's
   worst excluded (decision 32.3), holding cash when little qualifies
   (decisions 13.2, 43.3, 46), and a two-stage safety-then-return
   selection (TODO). A market-cap-weighted top 10 was run once and
   became a bet on one company (decision 26).

*What this means (hypotheses).* The project has not failed to find
skill. It has built a low-beta, equal-weighted portfolio of calm,
profitable, mostly large stocks with 4 to 5 points a year of real
selection skill against same-size peers, and asked it to beat a
cap-weighted index. That works when the index falls often and fails
when a few giants carry the index, and the model has no input that
tells it which kind of period it is in. Three things could change the
outcome, in order of how much evidence supports them: put the skill
inside the index's own structure (cap weighting), so the band's gap
disappears and the loser-avoidance is all that remains; give the
portfolio a reason to buy less when the market is dear, which needs
either a market-state column from upstream or a row-level valuation
floor; and raise the picks' upside without raising their losers, which
every attempt so far (regressions, run-up labels, the rare region) has
failed to do and which is left for later.

*Decided:*

1. **Six backtests, on `dataset_v1.4.1`, the candidate's build**, each
   with the candidate's costs, window (2005 to 2026-08-21) and
   accounting, one at a time (a v1.4.1 backtest peaks near 10 GB):
   - E1 `bt_lc90_mcap_all_v141`: the control. Every liquid stock in the
     top decile of market cap, bought each month in proportion to market
     cap, with a top-K larger than the universe so no model ranking
     applies. The structure of SPY built from this dataset.
   - E2 `bt_lc90_mcap_top50_v141`: the same universe, each month the 50
     stocks the not-a-loser forest scores highest (about half), cap-
     weighted. The index minus the predicted losers.
   - E3 `bt_lc90_mcap_top25_v141`: the top 25 instead of 50.
   - E4 `bt_lc90_equal_top50_v141`: E2's 50 names with equal weights,
     to separate the weighting from the selection.
   - E5 `bt_candidate_ey5_to2026_v141`: the candidate with a filter
     admitting only stocks whose earnings yield at the snapshot is 5% or
     more. The share of liquid stocks clearing that floor was 10% in
     2021 and 17% in 2018 against 35% to 48% in 2008 to 2009, so the
     filter buys less when the market is dear and leaves the rest in
     cash. It reads one row-level column, no market state.
   - E6 `bt_candidate_ey8_to2026_v141`: the same floor at 8%, to bound
     E5.
2. **The judging rule.** A portfolio is read against SPY on the
   time-weighted return in 2005 to 2020 and in 2021 to 2026 separately,
   on the money-weighted CAGR and final value over the whole window, on
   the worst drawdown, and on its buys' three-year lead over same-size
   peers and share of losers. An arm is carried to three seeds and
   proposed to Carter only if it is ahead of SPY on final value over the
   whole window, no more than 2 points a year behind SPY in 2021 to
   2026, and no deeper than SPY in drawdown. The cap-weighted arms are
   also read against E1, their own control, because E1 and not SPY is
   what the forest's exclusion is measured against.
3. **What is not run here.** A quarterly or horizon-matched selling
   rule, a top-20 book and a two-stage portfolio need engine code and
   are listed in TODO.md with the rest of the plan. Holding cash by a
   score threshold is not run: decision 46 showed the scores are
   highest at tops, so a score floor would buy most when it should buy
   least. The market-state columns stay the upstream request they are.
4. **Predictions, written before the runs.**
   (a) E1 tracks SPY: time-weighted return within 1.5 points a year of
   SPY's over 2005 to 2026 and within 2 points over 2021 to 2026. If E1
   trails SPY by 3 or more in 2021 to 2026, the gap is not the band's
   weighting but the particular giants SPY held, and cap weighting this
   universe cannot close it.
   (b) E2 beats E1 by 0.5 to 1.5 points a year over the whole window
   with a drawdown at least 3 points shallower, ahead of E1 in both
   periods and by less in the second. Against SPY, E2 ends within 1.5
   points a year over the whole window: ahead in 2005 to 2020, behind by
   2 to 4 in 2021 to 2026 rather than the candidate's 8. The rival, and
   the hope: E2 is ahead of SPY by a point or more a year over the whole
   window, 2021 to 2026 included. Then loser-avoidance inside a
   cap-weighted book is the thesis realized and three seeds follow.
   (c) E3 is not better than E2 by more than 0.5 points a year and its
   drawdown is not shallower: concentration adds variance, not return.
   (d) E4 is 2 or more points a year behind E2 in 2021 to 2026 and
   within a point in 2005 to 2020: the weighting is where the recent gap
   comes from.
   (e) E5 buys 15% to 25% fewer stocks, fewest in 2018 and 2021 and
   most in 2008 to 2009. Its 2021 to 2023 buys lose at least 5 points
   less often over three years than the candidate's, its drawdown is
   shallower, and its final value is within 5% of the candidate's. The
   rival: the floor removes the calm, fully priced, profitable stocks
   the forest likes and leaves cheaper and worse ones, so the 2005 to
   2020 return falls a point or more below the candidate's and losers
   rise, as the earnings-yield ranking's 57% losers (sweep B) warn.
   (f) E6 is too tight: cash sits idle in many months and the value-trap
   effect dominates, so its 2005 to 2020 return is a point or more below
   the candidate's with more losers.
   (g) Over the six: at most one arm passes the rule of 81.2, and if one
   does it is E2. If none passes, the finding is that the structure can
   be fixed (E1 tracks SPY, E2 beats E1) and the skill is too small to
   beat the index after the structure is fixed, which points the next
   work at the size of the skill (upside without losers) and at the
   market-state input, not at more feature sets.
5. **Records.** The six configs carry their predictions. Runs go on the
   lab branch `claude/lab-2026-11-26`; the note holds the tables; the
   logbook gets one entry for the six; findings, TODO and the results
   branch follow. What is not done: no holdout look, no deployment
   change, no edit to a config that has run, no local feature
   derivation (the valuation floor is a declared filter on a manifest
   column, like the liquidity floor).
