# Decision log, from 2026-09-29

On 2026-09-29 Carter lifted the stop rules of [agents.md](../agents.md)
for the time being and asked that every decision be logged. This is
that log: one numbered entry per decision, newest last, with the
reason and what it rests on. Results are in the
[logbook](../logbook.md) and the notes it links to.

Not lifted, and kept: the hard invariants of CLAUDE.md (no local
splits, no feature engineering, the sealed holdout, era-sliced
reporting, reproducible runs), the branch workflow, and the rules
under "Before writing a conclusion". No holdout look, promotion, pull
request into `Claude` or deployment is made under this log.

## The goal, in Carter's words (2026-09-29)

A model capable of making a few high-precision selections that have
low risk and plenty of upside potential (value picks). The thesis of
the project: a high precision on a modest target can outperform the
market over the long term by avoiding big losers. Carter's
simulations elsewhere support it, depending on (1) a precision of
about 0.65 or more, (2) the era: such strategies outperform during
and after market drawdowns, (3) the variance of the returns of the
picks.

Carter's reading of the label rungs: the lower drawdown of the picks
suggests fewer losers, so an excess CAGR that is no higher must mean
too little recall on big winners.

Clarified by Carter later the same day:

- **0.65 is not a hard minimum.** It came from simplified simulations
  on a label like `fwd_1y_cagr > 0`; the precision needed may differ
  for other labels or more accurate simulations. The point is to aim
  for higher precision.
- **The selection rule is open.** Higher precision may come from
  picking by score (say, confidence above 0.70) instead of the top
  20.
- **The number of picks is flexible.** It has to be manageable by one
  person putting in a few hours a week with the model as a screener:
  20 or more trades a quarter are feasible, 50 a year are fine, 1,000
  are not.
- **Sweeps are for finding a candidate, not for settling it.** The
  aim is a cell, feature set and model that does pretty well, carried
  forward through the workflow for the experiments and simulations
  that are hard to do quickly.

## What a result is judged on from here

In this order: what the picks went on to do (losers, big winners,
excess CAGR, drawdown), by entry year; the precision on the label,
higher being better and 0.65 a reference point, at whatever number
of picks up to some tens a quarter gives it; then PR-AUC and p@20 for ranking candidates inside one
cell. The pick-outcome screen stays a screen: no costs, equal
weights, top K rows per year.

## Decisions

### 1. Measure the tails of the picks before searching parameters

*Decided:* run `baseline_pick_anatomy_3y` and `forest_pick_anatomy_3y`
ahead of the three parameter searches.

*Why:* Carter's reading is a hypothesis about the distribution of
the picks' returns, and mean and median cannot test it. Label
expressions as pick outcomes give the tails with no code change:
the share of picks with `fwd_3y_cagr < 0`, `< -0.1`, `>= 0.15`,
`>= 0.25`, a drawdown from entry of 0.4 or more, and an excess CAGR
of 0.05 or more. The rungs showed that thresholds of one kind of
label do not move the picks' outcomes, so the forest sweep changes
the kind of label (absolute, relative, "not a loser") and the
columns (all ranks, fundamentals only), the two things that might.
top_k gains 5 and 10 because the goal is a few selections.

*Cost:* 4 + 18 runs, about 2.5 hours. 7 configurations added to the
primary cell.

### 2. Put pick outcomes in the three parameter searches

*Decided:* `pick_outcomes` (the four of the rungs and the six tails)
and `top_k = [20, 10, 5, 50]` are added to
`{forest,lgbm,xgb}_random_search_dd_entry_3y`. None had run, so the
files are edited, not copied.

*Why:* proposed in the
[rungs note](2026-09-29-label-rungs-dd-entry.md): PR-AUC and p@20
moved across the rungs without the picks' outcomes moving, so a
search read on PR-AUC alone can only find a better predictor of the
label. The searches still rank on PR-AUC; the outcomes are read
beside it.

### 3. The searches stay queued, behind the anatomy sweeps

*Decided:* not dropped, not run first. Their cell and feature set
may change with what decision 1 finds; they are re-examined when it
has been read.

### 4. Read selection by score beside selection by top K

*Decided (2026-09-29, after Carter's clarification):* sweeps from the
next one on set `score_thresholds` as well as `top_k` (up to 100),
and are read on how many picks a year a threshold gives and what
precision they have. The two anatomy sweeps were already running
with `top_k = [20, 10, 5, 50]` and are not restarted.

*Why:* the selection rule and the number of picks are open, so a
candidate is not rejected for its p@20 alone. *Caveat, to be checked
before any threshold is read:* scores of different folds are not
comparable (CLAUDE.md), and forest scores in these cells are not
probabilities (findings, conclusion 10), so a fixed threshold picks
very different numbers of rows in different years. The number of
picks per year is reported with every threshold.

### 5. Carry cell C forward, with cell A beside it

*Decided (2026-09-29, after the
[pick anatomy](2026-09-29-pick-anatomy.md)):* two regular configs,
`forest_nonloser_dd30_3y` (cell C) and `forest_cagr10_dd20_3y` (cell
A), run through `vml-run` so that their fold bundles are saved. Same
forest configuration and columns as the sweep, seed 23.

*Why:* cell C is the first candidate that does what the thesis asks
of the model (precision 0.78 on a modest target, losers 0.13), and
Carter asked for a combination that does pretty well to be carried
forward instead of settled in sweeps. Cell A goes with it because
its picks hold more winners and it is the comparison every earlier
result was made against. No parameter search first: parameters
moved nothing inside the forest family so far (findings, conclusion
13), and what is unknown about these candidates is what a portfolio
of their picks does, not their third decimal.

*Cost:* 2 runs, 2 configurations (one per cell).

### 6. The backtest template

*Decided:* one template for every candidate, fixed before the first
backtest is run, only the bundle changing:

| | value | from |
|---|---|---|
| strategy | `buy_and_hold`, monthly deposit 1,000, SPY leg with identical deposits | the repo's template (`allprob_top25_5models`) |
| picks | top 10 of the month's cross-section by score, equal weights | 10 a month is about 30 trades a quarter, inside what Carter called feasible (2026-09-29); equal weights because the scores are not probabilities |
| `min_score` | none | selection by score is studied on the bundle with `vml-eval` first |
| filters | none | |
| investability | `dollar_volume_3m >= 100000` | the repo's template |
| `cost_bps` | 35 per side | the repo's template |
| buys | 2005-01-01 to 2020-12-31 | the walk-forward test years; later years overlap the holdout era |
| valuation end | 2023-12-29 | three years after the last buy |
| `model_update` | not reached: no buy after the last fold | |

*Why these values:* `cost_bps` and the investability filter were
waiting for Carter. He has since asked for decisions to be made and
logged; both values are the ones in the template he wrote for the
live screen, so they are his earlier choices, not new ones. They are
modelling decisions and are reported with every result.

*Rules kept:* every backtest is a trial and is counted; the template
is not tuned per candidate; the per-year table is read, not the
final figure alone. Three backtests are planned: cell C's forest,
cell A's forest, and the two together (`combine = "mean_rank"`).

### 7. A sector cap at selection, on a feature branch

*Decided (2026-09-29, after the
[first backtests](2026-09-29-first-backtests.md)):* add
`max_per_group` to the backtest's selection: at each rebalance, walk
the candidates in score order and skip a stock once its group
(`sector` by default) already holds the cap among that month's buys.
Report the sector shares of the buys in every backtest report. Code
and tests on `claude/backtest-sector-cap`, off the branch this
session was given; the lab branch merges it and continues.

*Why:* half the buys of all three portfolios were utilities and a
quarter REITs; every buy of 2005–06 was a REIT, bought into the
2007–08 fall. The portfolios ended 26–29% below SPY with a deeper
drawdown than SPY's. The thesis is about avoiding big losers stock
by stock; a portfolio of one sector avoids nothing when the sector
falls. The cap is a selection rule, as the investability filter is.
It reads `sector`, a column of the manifest's `features` group, at
the snapshot the pick is scored on; it derives nothing and changes
no fit.

*What it is not:* not a new feature for the models (invariant 4),
and not a fix to the models, which will still rank utilities first.
Whether the models should be made sector-neutral is a separate
question; upstream has no within-sector volatility rank, and
deriving one here is not allowed.

*Values:* cap of 2 per sector among 10 monthly buys, fixed before
the run. One alternative, 1 per sector, is run beside it and both
are reported. The template is otherwise decision 6's.

### 8. A second ranking beside the forest's

*Decided (2026-09-29, after the
[capped backtests](2026-09-29-sector-cap-backtests.md)):* three
backtests of cell C's forest combined by mean rank with one single
factor each, under the template of decision 6 with a cap of 2 per
sector:

| factor | column, highest first | why this one |
|---|---|---|
| value | `earnings_yield_rank` | the goal is value picks; alone, the cheapest stocks were the worst picks, so this tests whether cheapness helps *among calm stocks* |
| momentum | `mom_12_2_rank` | the usual source of upside; the forests use `ret_1m_rank` and `ret_6m_rank` but little of the 12-month momentum |
| quality | `roc_greenblatt_rank` | return on capital: the other half of the magic formula, without the cheapness |

The factors were chosen before any of them was run in a backtest,
one per family, and no others are tried on this template. Each
factor is a `rank_factor` config run through `vml-run` so that it
has a fold bundle; a rank factor fits nothing.

*Why mean rank:* the forest's score level moves from 0.65 to 0.85
between years, so a fixed floor on it selects years, not stocks
([first backtests](2026-09-29-first-backtests.md), measured 5). A
rank is relative to the month's cross-section.

*What would count:* a combination that keeps cell C's drawdown
(within 5 points of −46%) and raises the time-weighted CAGR by a
point or more, with the gain not confined to 2005–12. Nine backtest
configurations will then have been tried on these years; the number
goes with every figure.

### 9. Check the backtests against the forest's seed

*Decided (2026-09-29, after the factor combinations):* cell C's
forest is run with seeds 232 and 1776 (the sweep's other two), and
two backtests are repeated with each: the forest alone with a cap of
2, and the forest with momentum. Four more backtest configurations,
thirteen in all.

*Why:* the forest-and-momentum portfolio met what decision 8 said
would count. It is one path from one seed, and it was the best of
three. The seed is not a parameter anyone would tune, so the spread
over seeds is a measure of how much of a backtest's figure is
chance. A result that does not hold on the other two seeds is not
carried forward.

### 10. The candidate, and what is Carter's

*Decided (2026-09-29, after the seed check):* the candidate carried
forward is **cell C's forest and 12-month momentum by mean rank, at
most 2 buys per sector a month, top 10 a month, equal weights, buy
and hold**. Bundles: `forest_nonloser_dd30_3y` (run `53ceedd93e6d`;
seeds 232 and 1776 beside it) and `factor_mom_12_2_3y`.

*What it has shown:* on buys of 2005–2020, 11.1–11.7% a year
time-weighted against SPY's 9.6%, a worst drawdown of −47% to −49%
against −53%, on three seeds; between 3% below and 4% above SPY in
money. Thirteen backtest configurations were tried on those years.

*Not done, because they are Carter's:* a look at the sealed holdout
(the 3y cell for this label is unopened), `vml-promote`, a pull
request for `claude/backtest-sector-cap` into `Claude`, and
`vml-train-deploy`. The backtest engine can also trade 2021 onwards
with year-end refits; that overlaps the holdout era and was not run.

### 11. The parameter searches move to cell C, smaller

*Decided:* the three searches queued for the primary cell
(`*_random_search_dd_entry_3y`, 40 draws each) are taken off the
queue unrun; their files stay. In their place: the same three
families in cell C, 20 draws each, one seed, with pick outcomes
(`*_random_search_nonloser_3y`).

*Why:* the candidate's model is cell C's forest, whose parameters
were tuned on 3y beat_spy on another dataset version. Whether
another family or other parameters rank the safe stocks better is
still unknown, and a better ranking feeds the portfolio directly.
20 draws, not 40: parameters have moved little inside a family so
far, and what decides is the three-seed round and the backtest that
follow, not the search. A search winner is backtested once, under
the candidate's template, and only if its fold-mean PR-AUC is above
the forest's 0.585 by 0.01 or more on three seeds.

### 12. The searches are closed; what is proposed and not run

*Decided (2026-09-30, after the
[three searches](2026-09-29-searches-nonloser.md)):* no draw of any
family exceeded the reference forest, so no three-seed round and no
further backtest follow. The queue is empty and is left empty.

*Why nothing else is launched:* the experiments that remain would
change the portfolio's rules (a sell discipline, the number of
picks, the rebalance period) or the horizon, and would be read on
the same sixteen buy years that thirteen backtests have already
been read on. Each further variant makes the best figure less
believable, not more. The evidence that would add something is of
another kind: years the choices were not made on.

*Proposed, for Carter to choose from:*

1. **One holdout look** in cell C's 3y cell with the candidate's
   forest, when he would act on it.
2. **A sell discipline** (`sell_below_criteria`): the portfolio
   holds for ever what it bought. One backtest, criteria fixed
   beforehand; it would be the fourteenth.
3. **A 1y or 2y version of the label**, for a model whose picks
   turn over faster. A new cell, new sweeps.
4. **Upstream:** a within-sector rank of volatility (and of the
   conservative score), so that the models can be made
   sector-neutral instead of capped.
5. **Ranking metric for boosted families:** if they are searched
   again, rank on p@K over 2013–20 of the worst seed, not on PR-AUC.

### 13. Carter's notes at the close of the session (2026-09-30)

Recorded as next steps in TODO.md ("Next, from the session of
2026-09-29/30"); the reasoning here.

1. **Feature selection.** The models lean on a few columns, the
   volatility and liquidity ranks among them; Carter would rather
   select features with a causal story in value investing, try
   excluding the dominant ones, and consider a training-time
   liquidity floor (rows below a dollar-volume threshold out of the
   dataset, not only out of the backtest). What today's runs say:
   fundamentals only (97 columns) scored below the ranks on p@20 in
   cell A and its picks beat SPY more often before 2013 and less
   after; that was one arm, one cell, on the screen. The question
   is open in cell C, on pick outcomes and backtests.
2. **Evaluation.** Median excess CAGR of the top K is a quick look,
   not a verdict: the best picks may outweigh the worst, so the
   mean (what an equal-weighted portfolio earns) belongs beside it;
   holding cash when nothing clears a confidence bar is a valid
   strategy; and the "High-confidence picks" table should carry the
   picks' outcomes at each score threshold. The scores of the
   models in use can be read as confidence once calibrated; today's
   finding that a fixed threshold selects the pre-crash years is
   about the uncalibrated scores of one forest.
3. **The holdout record.** The 19 consumed looks were on older
   dataset versions and simpler labels; Carter does not want the
   counts to hold experiments back. The record is kept, the counts
   stay with every holdout number, and cell C's 3y cell is
   unopened.
4. **A sell discipline** goes on the list, and pairs with
   calibration: buy on high confidence, sell or rebalance when it
   falls.

## Session of 2026-09-30 (second), decisions 14 onwards

Carter opened the session with the thesis restated and the stop rules
still lifted ("do anything you feel is best to reach this goal", every
decision logged, code on a feature branch). He added, in the same
session, that the 0.65 precision and the small number of picks are
aims, not limits (already recorded above, "Clarified by Carter"). Not
lifted, as before: the hard invariants, the branch workflow, the rules
under "Before writing a conclusion". No holdout look, promotion, pull
request into `Claude` or deployment is made under this log.

Lab branch: `claude/lab-2026-09-30`, off `claude/lab-2026-09-28` with
`Claude` merged in (the session's checkout was `Claude` itself, which
is never committed to).

### 14. Build the three tools Carter's notes ask for before running anything

*Decided:* one feature branch, `claude/universe-and-portfolio-screen`
(off `Claude`, merged into the lab branch), with:

1. **`[[universe]]`**, a declared row filter on manifest feature
   columns, for the training-time liquidity floor (decision 13.1);
2. **`[pick_screen]`**, the backtest template's selection rule (top K
   per test quarter, a cap per sector) applied to the test rows, with
   the picks' share by sector (TODO "Sector cap in the pick-outcome
   screen");
3. **selection by score**: what every row at or above a score
   threshold went on to do, mean beside median, per year, years
   without a pick shown (decision 13.2);
4. boolean flags as model inputs (decision 17).

*Why first:* each of the experiments Carter named needs one of them,
and the screen decides how every later sweep is read. The top-20-a-year
tables said cell C's picks matched SPY at a third of the drawdown; the
portfolio of those picks was one sector (findings, conclusion 6). A
screen that picks what the backtest buys makes a sweep worth reading
without a backtest per arm.

*Checked on real data before use:* the candidate's forest (run
`53ceedd93e6d`) under the screen (top 10 per quarter, at most 2 per
sector, rows with `dollar_volume_3m >= 100000`) picks 180 distinct
stocks in 640 picks; its backtest under the same rule bought 178. Mean
excess CAGR of the screen's picks −0.001 (the backtest: 9.74% a year
against SPY's 9.58%). A smoke run outside the ledger; the same
evaluation is repeated through the ledger below.

### 15. What a universe is, and how it is counted

*Decided:*

- A universe qualifies the ledger cell: runs inside one are logged
  under `label [universe: ...]`. Base rates and baselines differ
  inside a universe (cell C's base rate is 0.25 below 10,000 a day of
  dollar volume and 0.55 above 100 million), so its numbers are never
  set beside an all-rows run's.
- Reports state two counts: configurations in the universe's cell, and
  against the label in any universe. A universe is not a clean slate.
- The sealed holdout stays per label: a look inside a universe would
  consume the label's cell.
- `universe_scope = "test"` (train on every row, evaluate inside) is
  the reference arm: without it a training-time floor cannot be told
  apart from a test-time one.
- A bundle trained inside a universe is refused by a backtest that
  does not screen on the same filters.
- Floors, fixed before any run: `dollar_volume_3m >= 100000` (the
  backtest template's investability filter, decision 6) and
  `dollar_volume_3m >= 1000000` (ten times it; leaves out 45% of test
  rows against 19–29%). Nominal dollars: the floor is looser in later
  years (the 25th percentile of test rows is 85,000 in 2005 and
  517,000 in 2020). A rank floor would be era-neutral; the template
  uses dollars, so the experiments do.

*Why it is not a split or a feature:* upstream tags still assign every
row its role; the filter leaves rows out of both sides and reads only
what was known at the snapshot. `sample_weight_3y` is kept as shipped:
leaving a stock's illiquid quarters out makes its remaining rows
slightly more unique than their weights say, which under-weights them
a little and inflates nothing.

### 16. Sweeps are read on the portfolio screen first

*Decided:* from this session, a sweep's arms are compared on the
screen with the template's rule, fixed here: **top 10 per test
quarter, at most 2 per sector**. In this order: mean excess CAGR of
the screen's picks (an equal-weighted portfolio earns the mean;
decision 13.2) with the median beside it, the share of losers
(`fwd_3y_cagr < 0`) and of deep drawdowns, the precision on the run's
label, each by entry period (2005–12, 2013–20) before pooled. p@20 and
PR-AUC stay the metrics of record for ranking inside a cell.

*What would send an arm to a backtest:* a mean excess CAGR on the
screen at least 0.01 a year above the reference arm's in the same
universe, not more than 0.01 below it in either period, with losers at
0.20 or less. Fixed before the first sweep. An arm that passes on one
seed is run on three before it is backtested.

*Caveat:* the screen is still equal weights, no costs, entry at the
snapshot, held three years; and it cannot read a combination of two
models, which is what the candidate is.

### 17. Boolean flags are handed to models as 0/1 with NULL kept

*Decided:* route (b) of the TODO item on non-numeric columns, for the
boolean flags only (`harness.dataset.feature_matrix`).

*Why:* the flags carry what a value investor looks at first (two
years of losses, negative equity, the nine Piotroski signals) and
could not be selected at all: a nullable boolean reaches pandas as an
object column. Storing True as 1.0 and False as 0.0 changes the
representation of a value, row by row, and reads no other row or
column; it is not a derived feature (invariant 4). NULL stays NaN
because a NULL flag means "unknown" (data/features.md), not "failed".
Strings and dates (`sector`, `industry`, `fund_datekey`) stay out.

### 18. The feature sets, named before the run

*Decided:* five sets in cell C, one forest configuration (the
candidate's), seed 23:

| | set | columns | the question |
|---|---|---|---|
| fs0 | the `ranks` group | 112 | the reference |
| fs1 | ranks without the technical family | 97 | fundamentals as ranks (run before on all rows: p@20 0.66) |
| fs2 | fs1 plus the 47 columns upstream ships unranked because they are already comparable across quarters: the Piotroski and Mohanram scores and the nine signals, the `*_up_frac_*` and `ocf_positive_frac_*` consistency shares, the dividend record (`div_*_10y`), the own-history valuation percentiles (`*_5y_pctile`), filing age and the loss, negative-equity and negative-EBITDA flags | 144 | Carter's theory-led set: cash generation, balance sheet, profitability, consistency. None of the 47 has been a model input on v1.4 in these cells. |
| fs3 | ranks without the eight risk, size and liquidity ranks (`vol_12m`, `vol_36m`, `beta_12m`, `max_ret_21d`, `conservative_score`, `log_marketcap`, `dollar_volume_3m`, `amihud_12m`) | 104 | the dominant columns excluded, price trend kept |
| fs4 | fs3 plus the 47 | 151 | everything with a story, nothing that measures risk or liquidity directly |

On all rows (bundles saved, then evaluated inside each floor without
refitting) and trained inside each floor: 15 fits. The five all-rows
fits are five more configurations in cell C (the screen is in the
hash).

### 19. Read two-model candidates on the screen: `blend` in `vml-eval`

*Decided:* a third feature branch, `claude/eval-blend` (on top of the
universe branch): an eval config's `blend = [bundle directories]`
combines the evaluated bundle's fold scores with other bundles' by
mean rank within the test quarter, the backtest's `mean_rank` on test
rows. Each blend is its own configuration in the cell's trial count.

*Why:* the candidate is a blend (cell C's forest and momentum), and
the screen of decision 16 can only read one model. Every second
ranking tried so far cost a backtest on the same sixteen years, and
the best of three was kept. With the blend on the screen, second
rankings are compared on 640 picks over 64 quarters before any
backtest is spent, and the backtest count grows only for the ones
that pass.

*First, check the screen against what the backtests already said.*
Three blends whose backtests exist (decision 8), inside the 100k
floor:

| blend with cell C's forest | its backtest against the forest alone | what the screen should show if it is a fair proxy |
|---|---|---|
| 12-month momentum | +1.2 to +2.4 points a year, three seeds | mean excess CAGR above the forest alone's by 0.01 or more |
| return on capital | the same return, drawdown 5 points shallower | within 0.01 of the forest alone |
| earnings yield | −2.0 points a year | below the forest alone by 0.01 or more |

If the screen orders the three as the backtests did, it is used to
choose second rankings. If it does not, it is not, and the note says
so.

*Then, the second rankings to try, named before any is run:*

| | blend | why this one |
|---|---|---|
| n1 | forest + momentum + net payout yield | the conservative formula (low volatility, momentum, payout) with the forest as its low-risk leg |
| n2 | forest + momentum + return on capital | safe, rising and profitable: the two second rankings that each helped one thing |
| n3 | forest + a learned upside model | a forest on `fwd_3y_cagr >= 0.15` (feature set fs4, inside the 100k floor): does a model of who compounds beat a single factor as the second ranking? |
| n4 | forest + momentum + the upside model | |

*What would send a blend to a backtest:* screen mean excess CAGR at
least 0.005 a year above the momentum blend's, losers no more than
0.02 above it, and not more than 0.01 below it in 2005–12 or in
2013–20. At most two blends are backtested.

### 20. One calibrated run, for selection by confidence

*Decided:* `forest_nonloser_dd30_isotonic_3y`, the candidate's forest
with prequential isotonic calibration, five score thresholds and the
new "Selection by score" tables. One run, one more configuration in
cell C.

*Why:* Carter wants candidates read by confidence ("mean excess CAGR
at score > 0.7"), with cash as a valid position, and notes that the
scores can be read as confidence once calibrated (decision 13.2). The
uncalibrated forest's fixed thresholds selected the pre-crash years.
Whether calibration repairs that is an empirical question with a
prediction written in the config: it should not, because a fold's
calibration map is learned from earlier years' outcomes and a crash
is not in them until it has happened.

### 21. The screen's check failed for momentum; read the backtests per buy, and test a sell discipline

*What happened (2026-09-30):* the check of decision 19 did not come
out as predicted. On the screen inside the 100k floor, mean excess
CAGR of the picks: forest alone −0.001; with momentum **−0.018**
(predicted: above the forest by 0.01 or more); with return on capital
**+0.014** (predicted: within 0.01); with earnings yield −0.030
(predicted: below by 0.01 or more, matched). By the rule written in
decision 19 the screen is therefore **not** used on its own to choose
second rankings.

*What the disagreement is.* The backtests were read on time-weighted
return, where momentum led the forest alone by 1.3 points a year and
return on capital did not. The backtests' own buys, read one by one
over the three years after each trade date from the price panel
(delisting proceeds riding SPY), say this: mean excess a year per buy
+0.001 for the forest alone, +0.005 with momentum, **+0.013 with
return on capital**, −0.032 with earnings yield; for the buys of
2005–12 and of 2013–20 separately, +0.013 / −0.011, +0.025 / −0.016,
**+0.013 / +0.012**, −0.007 / −0.057. In money (final value on
192,000 deposited): 633,757, 711,494, 694,945, 493,413; SPY 732,110.
So the screen and the per-buy reading agree on return on capital
(best, and the only one positive in both halves) and on earnings
yield (worst); they differ on the size of momentum's effect (−0.017
against +0.004 relative to the forest alone), and both put it far
below what time-weighted return suggested. Part of the screen's gap
is the label convention: 15% of the momentum blend's screen picks
were acquired inside the window (7% for the forest alone), and the
dataset carries an acquired stock's final price flat to the horizon,
where a portfolio gets the cash back. Detail:
[blends note](2026-09-30-blends-and-calibration.md).

*Decided:*

1. **Per-buy outcomes go into every backtest report**
   (`claude/backtest-buy-outcomes`): each buy over the 1 and 3 years
   after its trade date against the benchmark, by buy year and
   pooled. Time-weighted return gives the small early portfolio the
   weight of the large late one; decision 8's criterion was written on
   it, and momentum's lead sits in 2005–11.
2. **A candidate is judged on four things together**, fixed here
   before the next backtests: final value at or above SPY's under the
   same deposits; time-weighted CAGR at least a point above SPY's;
   worst drawdown at least 5 points shallower; and a positive mean
   3-year excess per buy for the buys of 2005–12 and of 2013–20. The
   candidate of decision 10 meets the second and third, misses the
   first on two seeds of three and the fourth (−0.016 for 2013–20).
3. **Five backtests** (14th to 18th on these years), each with its
   prediction in its config:
   - the quality blend (forest and return on capital) on the forest's
     other two seeds: it was never seed-checked;
   - forest, momentum and return on capital (blend n2; it passed
     decision 19's bar against the momentum blend on the screen, as
     did n1, forest with momentum and net payout yield, by a smaller
     margin: n1 is not backtested);
   - the quality blend and the momentum blend each with a sell
     discipline, `[sell] max_rank_pct = 0.2`: a holding is sold once
     it is outside the top 20% of the month's candidates by combined
     rank. One value, chosen before any run: bought at the top 0.3%,
     kept to the top 20%.
4. The learned upside model is dropped: the forest on
   `fwd_3y_cagr >= 0.15` has no skill at its own label (p@20 0.29
   against a base rate of 0.27 inside the floor, fold-mean PR-AUC
   0.289), and both blends
   with it are below the forest alone on the screen (−0.031 and
   −0.037).

*Why a sell discipline now.* Buy and hold keeps for ever what the
models ranked first once, and the label is about three years. Per buy
the quality blend is 1.3% a year ahead of SPY over its first three
years in both halves of the sample, yet the portfolio ends 5% behind
SPY in money: no portfolio kept up with SPY in 2021 and 2023, years
in which it held stocks bought up to eighteen years earlier. Selling
what the models no longer rank highly, and buying what they do, keeps
the money where the measured edge is. Whether that survives costs and
turnover is what the two backtests measure.

### 22. A one-year "not a loser" cell

*Decided (2026-09-30):* `forest_nonloser_dd20_1y`: the candidate's
forest on `fwd_1y_cagr >= 0 & fwd_1y_max_drawdown_from_entry < 0.2`
(base rate 0.42 on all test rows of 2005–2020, 0.45 inside the 100k
floor), calibrated, trained on every row and measured inside the
floor, with 1-year pick outcomes and the screen; five single-factor
bars in the same cell; and cell C's 3-year forest read on the same
1-year outcomes as the reference. Decision 12 proposed a shorter
horizon; two things found today make the case for it:

- a 3-year label's calibrator is four years behind (the calibration
  run above), a 1-year label's two;
- a 3-year fold for year Y is trained on snapshots up to Y−3, a
  1-year fold up to Y−1, and a sell discipline re-decides monthly.

*Folds 2005–2020 only.* The 1-year fold calendar runs to 2022, but
the 2021–22 snapshots are in the 3-year holdout window and their
1-year outcomes are part of what that holdout measures. They stay
unseen.

*What it is compared on:* the same test rows as the 3-year cells
(256,351 on all rows), 1-year outcomes for both models. A new cell:
its first configurations.

*What would carry it forward:* written in the config. Fewer losers
than the 3-year forest among the entries of 2008–09 and 2020 by 0.05
or more, or a calibrated threshold that selects rows in 12 or more of
the 16 years at a precision near its score.

### 23. Two blends meet the four criteria on one seed; check them before believing them

*What came out (2026-09-30, backtests 14 to 18;
[backtests note](2026-09-30-backtests.md)):*

| | final value | time-weighted | money-weighted | worst drawdown | per buy, 3y excess | buys of 2005–12 | of 2013–20 |
|---|---|---|---|---|---|---|---|
| SPY, same deposits | 732,110 | 9.58% | 11.62% | −52.9% | | | |
| forest + return on capital, seeds 23 / 232 / 1776 | 694,945 / 752,267 / 721,826 | 9.65 / 10.18 / 10.04% | 11.18 / 11.85 / 11.50% | −41.2 / −42.4 / −41.3% | +0.013 / +0.019 / +0.012 | +0.013 / +0.023 / +0.018 | +0.012 / +0.014 / +0.005 |
| the same with the sell discipline (seed 23) | 800,456 | 10.64% | 12.37% | −38.8% | +0.013 | +0.014 | +0.012 |
| forest + momentum + return on capital (seed 23) | **948,956** | **12.24%** | **13.79%** | −41.2% | **+0.025** | +0.034 | +0.016 |
| forest + momentum with the sell discipline (seed 23) | 674,817 | 9.87% | 10.93% | −51.7% | +0.004 | +0.024 | −0.017 |

The three-way blend and the quality blend with the sell discipline
each meet all four criteria of decision 21 on seed 23. The three-way
blend was predicted to land between its parents and landed above both
on every measure: a prediction missed upwards, and the best of
eighteen backtests. It is treated as suspect until checked.

*Decided:* six more backtests (19th to 24th), predictions in each
config:

1. the three-way blend on the forest's other two seeds;
2. the quality blend with the sell discipline on the other two seeds;
3. the three-way blend with **fractional shares**. The template buys
   whole shares with 100 a pick on total-return adjusted prices, so a
   stock priced above its budget is skipped (111 of 192 months bought
   fewer than ten stocks in the three-way run). That is a selection
   rule nobody chose, applied to a price nobody paid. If the result
   depends on it, it is not the blend's;
4. the three-way blend with the sell discipline.

*What carries a blend forward:* all four criteria on all three seeds,
and for the three-way blend a fractional-share result within a point
a year of the whole-share one. *What does not change whatever comes
out:* these are backtests 19 to 24 on the same sixteen buy years; the
blend that comes through is a candidate for Carter's holdout look and
for paper trading, not a result.

*Not done:* no further second rankings are tried. Return on capital
and momentum were both named in decision 8 before any backtest; the
three-way blend is their union, named in decision 19 before it was
run. Trying more factors on these years from here would be fitting
them.

### 24. The candidate is now the three-way blend; backtesting on these years stops

*What the checks of decision 23 showed (2026-09-30, backtests 19 to
26; [backtests note](2026-09-30-backtests.md)):*

| | seed 23 | seed 232 | seed 1776 | SPY |
|---|---|---|---|---|
| **forest + momentum + return on capital, buy and hold** | | | | |
| final value on 192,000 deposited | 948,956 | 959,660 | 949,366 | 732,110 |
| time-weighted CAGR | 12.24% | 12.26% | 12.23% | 9.58% |
| worst drawdown | −41.2% | −41.3% | −42.0% | −52.9% |
| per buy, 3y excess a year (buys of 2005–12 / 2013–20) | +0.034 / +0.016 | +0.034 / +0.016 | +0.035 / +0.013 | |
| **the same with the rank sell discipline** | | | | |
| final value | 1,090,591 | 1,042,252 | 1,028,085 | 732,110 |
| time-weighted CAGR | 13.14% | 12.70% | 12.66% | 9.58% |
| worst drawdown | −39.5% | −40.2% | −40.5% | −52.9% |
| **forest + return on capital with the sell discipline** | | | | |
| final value | 800,456 | 852,325 | 803,800 | 732,110 |
| time-weighted CAGR | 10.64% | 11.09% | 10.79% | 9.58% |
| worst drawdown | −38.8% | −39.7% | −39.4% | −52.9% |

With fractional shares the three-way blend (seed 23) ends at 936,540,
12.12%, −43.0%: the whole-share rule was not doing the selecting. All
three rows meet the four criteria of decision 21 on all three seeds.

*Decided:*

1. **The candidate carried forward is cell C's forest, 12-month
   momentum and return on capital by mean rank**, top 10 a month, at
   most 2 per sector, equal weights, inside `dollar_volume_3m >=
   100000`. It replaces the candidate of decision 10 (forest and
   momentum), which misses two of the four criteria. Bundles:
   `forest_nonloser_dd30_3y` (run `53ceedd93e6d`; seeds 232 and 1776
   beside it), `factor_mom_12_2_3y`, `factor_roc_greenblatt_3y`.
2. **Buy and hold is the base case; the rank sell discipline
   (`[sell] max_rank_pct = 0.2`) is the variant to paper-trade beside
   it.** It added 0.4 to 0.9 points a year on the three seeds at four
   times the costs and about 15 sales a year, and it was predicted to
   do worse, so its gain is the less certain of the two.
3. **No further backtest is run on buys of 2005–2020.** Twenty-six
   configurations have been tried on those years. Each further
   variant makes the best figure less believable, not more (decision
   12); what is missing now is evidence from years the choices were
   not made on.

*What the candidate is, in plain terms:* stocks the forest ranks as
unlikely to lose over three years, that earn a high return on their
capital, and whose price has risen over the past year. Low risk,
quality and trend: three premia with long records, combined by rank.
The forest keeps the losers down (20% of the blend's buys lost money
over the three years after the trade; 42% of all test rows inside
the floor have a negative 3-year CAGR); return
on capital moves the picks from utilities and real estate (1.4% of
buys, from 35%) to operating companies; momentum adds the winners.

*What it has not shown:* that it holds outside 2005–2023. The three
ingredients were named before any of them was backtested (decision
8), and the blend before it was run (decision 19), but it is the best
of 26 configurations on sixteen buy years, its forest was chosen on
the same years, and the three premia are well known to have paid in
this period. A figure of +2.7 points a year over SPY should be
expected to shrink.

*Carter's, as before:* one holdout look in cell C's 3y cell with the
candidate's forest; promotion; the pull requests for the five feature
branches; deployment. Also his to decide: whether the backtest engine
may trade 2021–2023 with year-end refits for the candidate (it
overlaps the holdout era and was not run).

### 25. Carter's questions of 2026-10-01: the universe through to inference, a rank floor, the sector cap

Carter read decisions 14–24 and asked four things. What was done and
answered:

1. **A universe is used to train, test and deploy, and inference
   applies it.** `vml-train-deploy` already refit inside it; the gap
   was `vml-predict`, which ranked every inference row. Fixed on
   `claude/predict-universe`: the ranking is made over the rows
   inside the bundle's universe (a combined run, the rows inside
   every model's), the sidecar names the universe and counts the
   rows left out, and a missing universe column is an error. The
   backtest already refuses a bundle trained inside a universe
   unless its `[[investability]]` or `[[filters]]` carry the same
   filters, so the investability filter has to match the universe,
   as Carter expected. *What `universe_scope = "test"` was for:* a
   floor changes the test population (cell C's base rate is 0.39 on
   all rows and 0.43 inside 100k), so "trained inside the floor"
   had to be compared with "trained on everything, measured on the
   same floored test rows", or the floor's effect on the measurement
   would be read as an effect on the model. It is the reference arm
   of one experiment, not a way to deploy.
2. **A rank floor needs nothing upstream.** `dollar_volume_3m_rank`
   is a column; `dollar_volume_3m_rank >= 0.2` is one line in a
   universe or an investability filter, era-neutral by construction.
   Checked on the candidate (backtest 27, seed 23,
   `bt_nonloser_mom_roc_top10_cap2_rankfloor`): 965,380 against
   948,956, 12.15% against 12.24%, drawdown −41.4% against −41.2%,
   per buy +0.026 against +0.025. The candidate does not depend on
   the form of its floor. Which floor to deploy with is Carter's:
   100,000 a day was about the 27th percentile of the test rows in
   2005 and the 12th in 2020.
3. **The sector cap is a bandage, and the deeper question is
   recorded.** Agreed on both counts. What the data says about
   "what if the REITs had recovered": in the capped forest-alone
   backtest the REITs bought in 2005 (24 buys) earned +0.055 a year
   over SPY over three years and +0.075 over seven; those bought in
   2006 earned −0.119 over three and −0.030 over seven, and 2007's
   −0.019 and −0.016. The 2005 cohort was right; the 2006 and 2007
   cohorts never caught up with SPY. Why: the fold models of 2006–07
   were trained on snapshots up to 2003–04, in which no REIT had
   fallen 40%; a sector feature would not have helped them, because
   the lesson was not in their training window. What a sector
   feature could do is let the model learn that a given column means
   something different for REITs (book value, cash-flow stability,
   leverage all do). Two routes, recorded in TODO: (a) upstream
   within-sector ranks of the risk columns (already requested); (b)
   `sector` one-hot as a model input here, a per-row recoding like
   the boolean flags (decision 17), with the current-state caveat of
   data/features.md (a reclassified company's whole history carries
   today's sector). Not run in this session.
4. **Return on capital is the answer that was found**: it moves the
   portfolio from utilities and real estate (35% of the forest's
   buys) to operating companies (1.4%) without a cap, because the
   factor is undefined for most REITs and low for utilities, and it
   does so by what the picks earn on their capital, not by a quota.
   The cap stays in the template as a safeguard; with return on
   capital in the blend it binds rarely.

### 26. Carter lets the engine trade 2021–23 for the candidate; three questions on a report

*Carter (2026-10-01):* "Let the backtest engine trade 2021–23 for the
candidate." Done as two backtests, predictions in the configs:
`bt_nonloser_mom_roc_top10_cap2_to2023` and the sell-discipline
variant, buys and deposits through 2023-12-29, the forest served for
2021–23 by year-end refits on rows whose 3-year label was observable
by Jan 1 of the trade year. These years overlap the sealed 3-year
holdout window; the candidate was fixed in decision 24 before they
were run, and they are read as context for the holdout look, not as
selection.

Carter also ran `forest_nonloser_dd30_3y` on the host (same config
hash: no new configuration) and asked three things about its report:

1. *How can the top 20 a year be 0.79 precise when the 37 rows a
   year at `score >= 0.8` are 0.42?* Because "37 a year" is 597
   rows pooled over sixteen years, and 517 of them are 2006, 2007
   and 2008 entries (41, 120, 356; precision 0.39, 0.15, 0.40),
   where the fold models scored hottest and were most wrong. No row
   scores 0.8 after 2009. Top 20 *per year* takes the best of each
   year; a fixed threshold takes the years the model was most
   confident, which were the pre-crash years (findings, conclusion
   5). The era table's `n_at_thr_0.8` column shows it per year.
2. *Do 17% of the picks and 46% of all rows get 0% over three
   years?* No: `label_3y_cagr_lt_0p0` is the label expression
   `fwd_3y_cagr < 0`, the share of rows whose 3-year CAGR is
   negative (losers), not zero. 17% of the top 50 picks lost money
   over three years against 46% of all test rows. The low/high
   snapshot kinds are training rows only; every test row is a
   median-kind snapshot.
3. *Does the average stock trail SPY by 10 points a year, and would
   capitalization-weighting the buys help?* Yes to the first: the
   mean `fwd_3y_excess_cagr` over all test rows is −0.106 (median
   −0.073), −0.089 inside the 100k floor, −0.07 inside 1m. Three
   reasons, all real: the test rows are a universe of mostly small
   companies, equally weighted; a stock's CAGR is pulled below its
   average return by its volatility (a stock that halves and doubles
   has a CAGR of zero) and most of the market's return comes from a
   few large winners; and a delisted stock is carried at 0% to the
   horizon. The candidate's buys are not the average stock (61% beat
   SPY over three years, mean excess +0.025). Whether weighting them
   by capitalization helps is a question the engine can now answer
   (`weighting = "marketcap"`, `claude/backtest-marketcap-weighting`):
   `bt_nonloser_mom_roc_top10_cap2_mcap`, the 28th configuration on
   2005–20, prediction in the config (within 1.5 points either way,
   more concentrated).

*What came out (2026-10-01, backtests 28 to 31 on `dataset_v1.4`):*

| | final value | deposits | time-weighted | drawdown | 2021 / 2022 / 2023 against SPY |
|---|---|---|---|---|---|
| SPY, deposits through 2023 | 774,140 | 228,000 | 9.58% | −52.9% | |
| candidate, buys through 2023 | 985,668 | 228,000 | 12.21% | −41.2% | −9.6 / +4.3 / −2.2 |
| the same with the sell discipline | 1,054,924 | 228,000 | 12.70% | −39.5% | −7.9 / +1.2 / −6.7 |
| (the candidate without buys after 2020, for reference) | 948,956 | 192,000 | 12.24% | −41.2% | −9.5 / +4.6 / −2.0 |

The forest for 2021, 2022 and 2023 was refit at each year end on
rows whose 3-year label was observable by then; the years with new
buys are within 0.3 points of the years without them, so the refits
and the new buys changed the portfolio's path very little. **What
the new buys did:** the 86 buys of 2021 trailed SPY by 15 points a
year over their first year (77% lost money; 2022 was the year after),
the 81 buys of 2022 by 2.8 points (54% lost money); 2023's have no
outcome yet. In the selection years the worst one-year cohorts were
2020 (−13.5 points) and 2006 (−11.0): 2021's is the worst of the
sample, and of a kind with them. The predictions held for the years
and the final value and missed for the 2021 cohort (within 0.03 of
+0.03 predicted; −0.15 measured). These are the only numbers so far
from years the candidate was not chosen on, and they overlap the
holdout era: context for the holdout look.

**Capitalization weighting is an Apple bet.** The candidate with
`weighting = "marketcap"` ends at 1,108,044 (13.82% a year, drawdown
−37.0%) on seed 23, 1,161,451 and 1,090,347 on the other two: 1.6 to
2.2 points a year above equal weights. But the median month puts 54%
of its cash into one buy, it makes 5.2 buys a month instead of 9.1,
and at the end 46% of the portfolio is AAPL (the five largest
holdings are 60%, against 26% equal-weighted). The prediction missed
on the return (+1.58, predicted within 1.5) and on the drawdown
(shallower, not deeper); it held on concentration. The answer to
Carter's question is that the index's advantage over the average
stock comes from a few very large winners, and weighting the picks
by size reproduces that by holding the largest of them: a
single-stock bet, not a sizing rule. Equal weights stay.

Backtest configurations tried on these years: 31.

## Session of 2026-10-01 (second), decisions 27 onwards

Carter opened the session with the thesis restated and the same
freedom as before ("do anything you feel is best to reach this goal",
the stop rules of agents.md disregarded for now, every decision
logged, code on a feature branch), and with explicit leave to rewrite
agents.md to match. Since the last session he merged pull request 18
into `Claude`, took the one holdout look in cell C's 3y cell
(`reports/final_eval/forest_nonloser_dd30_3y.md`) and chose the
era-neutral rank floor for deployment (TODO.md).

Not lifted, as before: the hard invariants of CLAUDE.md (no local
splits, no feature engineering, the sealed holdout, era-sliced
reporting, reproducible runs), the branch workflow, the rules under
"Before writing a conclusion". No holdout look, deployment or merge
into `Claude` is made under this log.

Lab branch: `claude/lab-2026-10-01`, off `claude/lab-2026-09-30` with
`Claude` merged in (the session's checkout was `Claude` itself, which
is never committed to).

### 27. agents.md is rewritten to say what the sessions have done since 2026-09-29

*Decided:* with Carter's leave, docs/agents.md now describes two ways
of working. The queue loop and its stop rules stay as written for a
session told to "work the queue". A session told to pursue the goal
works as these four sessions have: it may open a new direction, extend
the queue, build code on a feature branch and continue experiments off
it, on condition that every decision is logged here before it is acted
on, with its reason and, for a run, its prediction in the config.

*What stays Carter's in both:* a holdout look or re-look, deployment,
and the merge into `Claude`. *What moves to the agent in a
goal-directed session:* promoting results (`vml-promote`, as at the
close of the last two sessions) and building the results branch a pull
request is opened from.

*What a contradicted prediction does now:* it no longer ends the
session. It gets a note with the rival explanations, and the next
experiment is the one that separates them, which the session may run.
A result far above its baseline, or far below an earlier one, is still
checked as a bug or a changed input before anything is built on it.

### 28. The candidate is traded to the end of the price panel, once

*Decided:* two backtests, predictions in the configs, before anything
else: `bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026` and its
sell-discipline variant. Decision 24's blend with the floor Carter
chose for deployment (`dollar_volume_3m_rank >= 0.2`), buys and
deposits through 2026-08-21, valued on that day, year-end refits of
the forest for 2021 to 2026.

*Why:* the first open question in findings.md is whether the candidate
holds outside 2005–2023, and "only the holdout, 2021–23 trading and
time can say". The price panel and the dataset's snapshots both run to
2026-08-21; every backtest so far stopped its valuation at 2023-12-29
because decision 6's template did. So 2024, 2025 and most of 2026
have been seen by no selection in this repository, and the buys of
2021–22 now have the three-year outcomes that the run to 2023 could
not show. It is the nearest thing to a paper-trading record that
exists, and it costs no configuration on the years the candidate was
chosen on.

*Why it is not a holdout look:* the engine reads no split tags and
evaluates no label. Its year-end refits train on rows whose label was
observable by Jan 1 of the trade year (data/manual.md §4 rule 7,
point-in-time), which from trade year 2025 on includes snapshots of
2021 that the holdout scheme tags as test rows: that is what a
deployed model would have been trained on. Carter allowed the same
for 2021–23 (decision 26) and has since taken the cell's look.

*The condition that keeps it honest:* these two portfolios are the
only ones traded on 2021–26, and nothing is chosen on what they show.
A third portfolio on those years needs a decision here that says why
it is not a selection. If the candidate did badly, that is the
finding.

*Counted:* backtest configurations 32 and 33 on `dataset_v1.4`. The
buy-and-hold run's path to the end of 2020 is that of backtest 27 (a
check before reading); the sell variant has not been run with the rank
floor before, so its 2005–2020 path is new, the same strategy under
the floor Carter chose.

### 29. What the holdout look in cell C says, and what it does not

Carter's look (2026-10-01, look 1 of 1 in the cell; run
`b6707d087996`, config hash `419b84929382132f`, the walk-forward
config unchanged, one fit on 1,110,907 train rows, effective 38,640;
47,012 test rows of 2021–2023, the 2023 rows those whose label was
observable). Read from the report only; no holdout row was read here.

| | 2021 | 2022 | 2023 | pooled, per year | walk-forward 2005–20 |
|---|---|---|---|---|---|
| base rate | 0.338 | 0.408 | 0.399 | 0.379 | 0.392 |
| precision, top 20 | 0.75 | 0.65 | 0.55 | 0.65 | 0.79 (0.23 to 1.00 by year; 2019: 0.53–0.65, 2020: 0.70–0.73) |
| top 50 | 0.76 | 0.70 | 0.72 | 0.727 | 0.76 |
| top 100 | 0.70 | 0.67 | 0.71 | 0.693 | |
| PR-AUC | 0.485 | 0.596 | 0.630 | 0.564 | 0.585 |
| Brier / no-skill Brier | 0.209 / 0.224 | 0.207 / 0.242 | 0.196 / 0.240 | 0.205 / 0.235 | ahead in 11 of 16 years |
| top 20: lost money over 3y (all rows) | 0.15 (0.59) | 0.30 (0.51) | 0.40 (0.49) | 0.28 (0.54) | 0.13 (0.45) |
| top 20: fell 40% from entry (all rows) | 0.05 (0.57) | 0.00 (0.51) | 0.10 (0.51) | 0.05 (0.53) | 0.10 (0.50) |
| top 20: mean 3y CAGR (all rows) | +0.072 (−0.147) | +0.047 (−0.092) | +0.030 (−0.052) | +0.050 (−0.103) | |
| top 20: mean excess CAGR (all rows) | −0.022 (−0.242) | −0.077 (−0.252) | −0.177 (−0.261) | −0.092 (−0.251) | about 0 (−0.106) |
| top 20: CAGR of 0.25 or more (all rows) | 0 (0.07) | 0 (0.11) | 0 (0.15) | 0 (0.11) | 0.03 (0.15) |

The walk-forward column is from the pick-anatomy note (three seeds)
and the forest's own report; the walk-forward mean excess is the
top-20 median and the screen's mean, both about zero.

*Measured:*

1. **The label is still predicted on snapshots the forest was not
   chosen on.** Top 50 a year: 0.73 against a base rate of 0.38 (walk-
   forward 0.76 against 0.39). Top 20: 0.65, below the walk-forward
   mean of 0.79 and inside the range of its last two years. PR-AUC
   0.564 against 0.585; Brier ahead of no skill in each of the three
   years. 0.65 is the reference precision of the thesis, met at 20 and
   exceeded at 50 picks a year.
2. **The picks avoided the losers and gave up the market.** 28% of the
   top 20 lost money over three years against 54% of all test rows;
   5% fell 40% from entry against 53%. Their mean CAGR was +5% a year
   where the average row lost 10%. SPY returned about 14% a year over
   the same windows: the picks trailed it by 9 points a year, the
   average row by 25. None of the 60 picks compounded at 25%.
3. **The top of the ranking weakened towards 2023**: p@20 0.75, 0.65,
   0.55 and p@5 0.8, 0.4, 0.4, while p@50 and p@100 held at 0.67 to
   0.76. With 20 picks a year a difference of 0.2 is four picks.

*What it does not say:* anything about the blend. The forest is the
only fitted part of the candidate, and the forest alone was already
known to earn SPY's return or less (findings, conclusion 1: return on
capital and momentum put the winners back). The look does not test
them. It also has no baselines: the report says "No baseline runs
recorded for this cell" under the holdout scheme, so whether lowest
volatility alone would have scored the same 0.65 on these rows is not
known (on walk-forward, lowest 36-month volatility has the forest's
loser rate and 0.024 a year less return). A baseline on the holdout
rows is a further read of them and is Carter's.

*Hypotheses, not tested:* (a) the era: SPY's 14% a year over 2021–26
came from its largest members, and the mean row's excess of −0.25 is
the widest gap of any period in the data (−0.106 over 2005–20);
calm stocks did what the label asks and the index outran them; (b)
the forest's ranking of the very top is weaker on recent data (item
3), which would show as the top 20 falling below the top 50 again in
the next cohort. The run of decision 28 reads the same years for the
blend through prices.

*Decided:* the look stands as the cell's one look. The forest stays
the candidate's first leg: it did on the holdout what it was chosen
for (few losers, shallow drawdowns), at about the precision the
thesis names. The open problem is unchanged and is now measured out
of sample as well: the upside.

### 30. The candidate ended behind SPY: tell the era from the fit before anything else

*What came out (2026-10-01, backtests 32 and 33, both at git
`5ed44ef`; the buy-and-hold path to the end of 2020 equals backtest
27's to the cent):*

| | deposits | final value 2026-08-21 | time-weighted | money-weighted | worst drawdown |
|---|---|---|---|---|---|
| SPY | 260,000 | 1,326,084 | 10.93% | 13.20% | −52.9% |
| candidate, buy and hold | 260,000 | 1,193,902 | 11.31% | 12.42% | −41.4% |
| candidate, rank sell discipline | 260,000 | 1,344,630 | 11.99% | 13.31% | −39.6% |

Calendar years against SPY, points (computed from the equity curves,
first trading day of January to the next; the report's own yearly
table runs December to December, see below):

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to 08-21 | sum 2005–12 | 2013–20 | 2021–26 |
|---|---|---|---|---|---|---|---|---|---|
| SPY's return | +31.3% | −19.0% | +26.0% | +25.3% | +18.2% | +12.7% | | | |
| buy and hold | −8.6 | +3.2 | −2.9 | −12.5 | −14.4 | −12.7 | +25.3 | +26.1 | −47.9 |
| sell discipline | −8.2 | +0.6 | −7.9 | −9.1 | −12.4 | −9.3 | +26.5 | +35.5 | −46.3 |

Per buy over three years (buy and hold): the 2021 buys −0.116 a year
against SPY with 41% losing money, 2022's −0.109 and 32%, 2023's (50
of 75 with an outcome) −0.169 and 38%. The buys of 2005–2020 averaged
+0.025 with 20% losing money. Buy and hold was 37% ahead of SPY in
money at the end of 2020, 29% ahead at the end of 2023 and is 10%
behind now.

*Against the predictions:* 2021–23 within 1.5 points of the
dollar-floor run, held. 2024 behind by 2 to 12: −12.5, missed by half
a point. 2025 and 2026 within 6 points either way: missed (−14.4,
−12.7). Final value above SPY's: missed for buy and hold. Per buy:
all three cohorts behind SPY, held in sign and missed in size and in
losers (32% to 41%, predicted under 30%). The sell variant: within 4
points of buy and hold each year, held; above SPY, held by 1.4%;
costs 9.3 times (predicted 3 to 6), missed.

*Three things found while reading it, none of them the strategy's:*

1. **The reports' yearly table is a month off.** `yearly_table`
   groups each monthly return by the year of the date it *ends* on,
   and the equity curve is sampled on the first trading day of each
   month, so "2022" runs from 2021-12-01 to 2022-12-01. SPY's
   "2022" reads −8.2% where the calendar year was −19.0%; the
   candidate's excess reads +4.3 where the calendar year's is +3.2.
   Both legs share the window, so no comparison was wrong, but the
   label was, in every backtest report and in the yearly figures of
   findings.md. Fixed on a feature branch; the candidate's years are
   restated above from the equity curve.
2. **The whole-share rule binds after 2020.** 64 to 87 buys a year
   from 120 orders in 2020–25 (108 to 120 in 2005–12): at about 100
   a pick, a stock priced above the budget is never bought, and
   adjusted prices are low early in the sample and real late in it.
   Decision 23's fractional-share check was on buys of 2005–2020.
3. **There is no reference for "the average stock" in a backtest
   report.** The holdout look says the average row trailed SPY by 25
   points a year over 2021–26 windows and the forest's picks by 9.
   Whether the candidate's buys still beat the stocks they were
   chosen from is the question that separates a selection that
   stopped working from an index that outran every equal-weighted
   portfolio, and no report answers it.

*Decided,* in this order, before any new modelling:

1. **Fractional shares to 2026** for both portfolios (backtests 34
   and 35; predictions in the configs). A check of the template: if
   the result depends on the whole-share rule it is not the blend's.
   Not a selection: the deployed form is one or the other by what a
   real account can do, not by which did better.
2. **The buys against the stocks they were chosen from.** For every
   rebalance, the per-buy outcomes of *all* investable candidates
   (equal weight, the same horizon, the same delisting convention),
   beside the picks'. First as a scratch diagnostic on these runs,
   then built into the backtest report on a feature branch, because
   every later backtest needs it.
3. **Which leg.** The same per-pick reading for the forest alone,
   the forest with each factor, and each factor alone, 2021–26
   against 2005–20: picks only, no portfolio is simulated and no
   configuration is added.
4. **Where the index's largest winners ranked** on each leg at the
   start of 2023, 2024 and 2025, from the cross-sections (features
   and fold or refit models only; no label is read).

*What each reading would mean, written before the diagnostics run:*

- (a) *The era.* The candidates' own mean excess over SPY fell as far
  as the picks' did (the holdout look suggests −0.2 or worse), and
  the picks stayed ahead of their candidates by about as much as in
  2005–20. Then the selection kept its skill and an index led by its
  largest members outran every equal-weighted portfolio. The thesis
  condition (2), the era, in its plainest form.
- (b) *The fit.* The picks' lead over their own candidates shrank
  towards zero after 2020, or their loser rate rose towards the
  candidates'. Then the blend was fitted to 2005–2020.
- (c) *The template.* The fractional run is 5 or more points a year
  better in 2024–26.
- They are not exclusive; the diagnostics size each.

*The condition of decision 28 stands:* nothing is chosen on 2021–26.
The fractional runs and the per-leg reading are diagnostics of the
fixed candidate. Whatever they show, a new candidate is not picked
by its 2021–26 numbers.

### 31. `sector` as a model input: built, and one sweep

*Decided:* route (b) of decision 25.3, on `claude/sector-feature`:
`sector` is handed to models as eleven 0/1 indicators against a fixed
vocabulary, NULL kept (`harness.dataset.CATEGORICAL_FEATURES`). A
per-row recoding like the flags of decision 17; no vocabulary is
learned from a frame, so every fold, cross-section and inference frame
has the same columns. The other classification columns are refused in
code: `scalemarketcap` is today's size bucket on a firm's whole
history, which is the future. Every report that uses `sector` states
the current-state caveat.

One sweep, `forest_sector_nonloser_3y`: cell C, the candidate's
forest, three seeds, the ranks against the ranks with `sector`; read
on the screen and on the picks' sector shares, predictions and
Carter's rival in the config. Six more configurations in cell C.

*Why now, when the candidate has just ended behind SPY:* it was asked
for, it is half an hour, and whether the forest's sector habit is in
its inputs or in its target is a fact about the forest that every
later use of it rests on.

### 32. What the diagnostics say: size first, then the era; the next question is selection inside large caps

*What came out (2026-10-01; tables in
[the out-of-sample note](2026-10-01-out-of-sample.md)):*

1. **Not the template.** With fractional shares (backtests 34, 35)
   the candidate ends at 1,172,560 and the sell variant at 1,329,280
   (whole shares: 1,193,902 and 1,344,630); every year of 2021–26 is
   within a point of the whole-share run. Reading (c) is out.
2. **The average investable stock trailed SPY by 22 points a year**
   over the three-year windows of the 2021–23 cohorts (equal weight,
   every candidate of every month): −0.057 for 2005–12, −0.111 for
   2013–20, −0.218 for 2021–23. 52% lost money.
3. **Size decides more than any model.** Mean three-year excess over
   SPY by market-capitalization rank, the three periods: smaller half
   −0.116 / −0.179 / −0.333; 50th to 80th percentile −0.033 / −0.083 /
   −0.176; 80th to 95th −0.002 / −0.049 / −0.120; largest 5% +0.002 /
   −0.025 / −0.065; largest 1% +0.010 / −0.022 / −0.033. In 2021–26
   SPY beat the equal-weighted mean of its own thirty largest members.
4. **Against stocks of their own size the candidate's lead is gone
   after 2020, and the forest's is small throughout.** Mean
   three-year excess of the picks minus that of the same month's
   candidates in the same 5% size band:

   | | 2005–12 | 2013–20 | buys of 2021–23 |
   |---|---|---|---|
   | forest alone | +0.023 | +0.027 | +0.006 |
   | forest + return on capital | +0.015 | +0.052 | +0.005 |
   | forest + momentum | +0.033 | +0.034 | +0.027 |
   | **the candidate (all three)** | **+0.046** | **+0.059** | **−0.016** |

   Against all candidates the candidate "led" by 0.090, 0.122 and
   0.100: most of that was its picks being large (mean
   capitalization rank 0.83 to 0.91).
5. **Loser avoidance held, net of size.** Share of picks losing money
   over three years, against their same-size peers': forest alone
   0.24 / 0.12 / 0.22 against 0.35 / 0.25 / 0.34; the candidate 0.25
   / 0.16 / 0.34 against 0.36 / 0.27 / 0.37.
6. **Inside the largest fifth the forest separates the worst quintile
   and nothing above it.** Three-year excess by forest-score quintile
   among large caps, worst to best: 2005–12 −0.038 … +0.016; 2013–20
   −0.088 … −0.022; 2021–23 −0.203, −0.088, −0.077, −0.077, −0.087.
7. **The forest ranks the index's most volatile giants in the middle
   of the list.** January 2023, of 3,673 investable stocks: NVDA
   1,599th on the forest (1,477th combined), TSLA 1,987th, META
   1,940th, AMZN 1,209th. The calm ones rank high (AAPL 38th
   combined, LLY 14th).

*Read against the three readings of decision 30:* (c) no. (a) the
era, yes, and larger than the question: SPY outran equal-weighted
stocks of every size in 2021–26, so no equal-weighted selection from
this universe could have kept up without holding a handful of
giants. (b) the fit, yes for the blend's increment: what momentum and
return on capital added to the forest in 2005–2020 (2 to 3 points a
year against same-size stocks) was −2 for the 2021–23 buys. Three
cohorts, 320 picks, one of them 2021; it is evidence, not a verdict.

*What it changes about how anything here is read:*

- "Beats the average stock" is not skill. Every screen, pick-outcome
  table and per-buy table in this repository compares picks with all
  rows or with SPY, and both comparisons are dominated by size. From
  now on a selection is read against same-size stocks:
  `claude/backtest-universe-outcomes` puts that reference in every
  backtest report (`vs_peers`), and on the screen a run is read
  inside the universe `log_marketcap_rank >= 0.8`, where the all-rows
  statistic is a same-size reference.
- The thesis, on this evidence: a high precision on "not a loser"
  is achievable and holds out of sample (decision 29), and it buys
  fewer losers and shallower falls. It does not by itself buy the
  index's return when the index is led by its largest and more
  volatile members: those are the stocks a loser-avoiding model
  ranks in the middle. Condition (2), the era, is the whole of
  2021–26.

*Decided:*

1. **The record first**: the out-of-sample note, findings.md
   rewritten around it, the yearly figures restated on calendar
   years, a process note on the yearly table.
2. **One experiment on the open question, selection inside large
   caps** (`forest_largecap_cells_3y`, `baseline_factors_largecap_3y`,
   and the existing bundles evaluated inside the same universe):
   three targets (not a loser; beat SPY; beat SPY without a deep
   fall), the candidate's forest, three seeds, seven single-factor
   bars, all trained and read inside `log_marketcap_rank >= 0.8`.
   The rule that carries an arm forward is in the sweep's header
   (a lead of 0.02 over the universe in both halves of 2005–2020 on
   every seed, and 0.01 over the best single factor). An arm that
   passes is the one new model that gets a backtest and one run on
   2021–26. If none passes, the finding is that these features rank
   risk and not return among investable large companies, and the
   upside has to come from new information upstream.
3. **Not done:** no new blend is tried on 2005–2020 backtests, and
   no variant of the candidate is run on 2021–26. A
   capitalization-weighted portfolio of large caps without the
   forest's worst quintile ("the index minus the predicted losers")
   is the literal form of the thesis and is recorded in TODO as a
   proposal: it would have left out NVDA, TSLA and META in 2023, and
   it is a 600-stock portfolio, not a screener for one person.

### 33. The screen gets the same-size reference too, and decision 32's rule is read on it

*Decided:* `claude/screen-size-peers` (on top of the sector branch):
`[pick_screen] peer_column = "log_marketcap_rank"` makes the screen
report, beside each pick, what the test rows of its own quarter in
its own 5% band of that rank went on to do (`screen_peer_mean_<o>`,
`screen_peer_precision`, and a `peers` column in the screen table).
It is the harness counterpart of the backtest report's `vs_peers`
(`claude/backtest-universe-outcomes`).

*Why now:* decision 16 made the screen the way every sweep is read,
and its reference was all test rows. Decision 32 found that reference
dominated by size. Reading inside a large-cap universe is a
workaround for one experiment; the reference belongs in the screen,
so that a sweep over all rows can be read net of size and old bundles
can be re-read without a refit.

*Used at once:* the three large-cap sweeps and the four large-cap
evaluations of decision 32 carry the peer column (none had run; the
rule that carries an arm forward is now "0.02 over its same-size
peers in both periods on every seed", with the lead over the
universe's all rows reported beside it). And the candidate's bundles
are evaluated again inside the 100k floor with the peer column
(`eval_*_peers_dv100k`): the forest alone and its three blends, the
screens of decision 19 read net of size. Four more evaluation hashes
inside the 100k floor.

*Prediction for those four (2026-10-01):* the screen's lead over
same-size peers, entries of 2005–12 and of 2013–20: forest alone
+0.01 to +0.04 in both; with return on capital 0.00 to +0.03 and
+0.03 to +0.07; all three legs +0.02 to +0.06 in both. That is the
diagnostic's reading (+0.023 / +0.027, +0.015 / +0.052, +0.046 /
+0.059 on monthly picks and price-panel outcomes) within 0.02: the
screen picks quarterly from test rows and reads label outcomes, where
an acquired stock is carried flat.

### 34. No arm passes inside large caps; what is carried forward

*What came out (2026-10-01; [large-caps note](2026-10-01-large-caps.md)):*

- `sector` as an input changes nothing (decision 31's five
  predictions held): the forest picks the same utilities and REITs
  with the sector in view.
- On the harness screen, against same-size peers, the candidate's
  forest leads by +0.030 / +0.027 a year for entries of 2005–12 /
  2013–20, the candidate by +0.022 / +0.053 (inside large caps +0.038
  / +0.047): decision 33's predictions held, and the screen agrees
  with the diagnostic and with the backtest reports' new `vs_peers`.
- Inside large caps no model passes decision 32's rule. Forests on
  "not a loser" lead their peers by +0.020 to +0.025 in both halves,
  which is less than return on capital alone (+0.039 / +0.030) or the
  conservative score alone (+0.031 / +0.029). "Beat SPY" is not
  learned with size held fixed (2013–20: −0.001 to +0.013), a
  regression on the size of the excess return is worse, and "beat
  SPY without a 30% fall" has a p@20 below its base rate.

*Decided:*

1. **No new model goes to a backtest, and nothing more is run on
   2021–26.** The rule was fixed before the runs and no arm met it.
   The one surprise, two single factors leading by 3 points in both
   halves, is in-sample: for the buys of 2021–23 return on capital
   alone trailed its same-size peers by 3.4 points (out-of-sample
   note). It is recorded, not chased.
2. **The candidate's definition stands and its claim is restated.**
   Cell C's forest, momentum and return on capital by mean rank, top
   10 a month, 2 per sector, `dollar_volume_3m_rank >= 0.2`; buy and
   hold, and the rank sell discipline beside it. What it has shown:
   over 2005 to 2026-08, the index's return (11.3% to 12.0% a year
   time-weighted against 10.9%) with three quarters of its worst
   drawdown; 37% ahead of SPY in money at the end of 2020 and between
   10% behind and 1% ahead in August 2026. What it has not shown: a
   lead over SPY on the buys of any year after 2018, or a lead of
   more than about a point over stocks of its picks' own size on any
   of them. It is a low-risk equity portfolio, not a market-beating
   one, on this evidence.
3. **A selection is read against same-size peers from here on.**
   Decision 16's rule is amended: an arm goes to a backtest when its
   screen's lead over same-size peers (`peer_column =
   "log_marketcap_rank"`) is 0.01 or more above the reference arm's in
   both halves, with losers no higher; backtests are read on
   `vs_peers` beside the headline. Sweep configs carry the peer
   column.
4. **The search over labels, features and models on these columns is
   closed for now.** Four sessions have tried 87 configurations in
   cell C on all rows, 38 inside the 100k floor, 14 inside large
   caps, and 35 backtests. Every arm that leads its same-size peers
   does so by 2 to 5 points in-sample, through low risk and one
   quality factor, and none of it carried to the buys of 2021–23.
   More configurations on 2005–2020 cannot change that; what can is
   information the columns do not hold and years that have not
   happened.

*What is Carter's (in TODO.md, with the reason for each):*

- What the portfolio is for, and its yardstick: SPY, or stocks of the
  picks' own size. The answer decides whether the candidate is a
  result or a starting point.
- Whether to paper-trade the fixed candidate (both forms) as the
  low-risk portfolio it is. Nothing else is proposed for paper
  trading: choosing a different blend now would be choosing it on
  2021–26.
- The pull request (five code changes, the docs, the promoted
  results), and the upstream requests: an outcome and a label
  measured against same-size peers, size-neutral ranks, market-state
  features, and information about upside that prices and statements
  do not carry (insider and institutional transactions).

### 35. Carter's reading of 2021–26 (a bubble the strategy sits out), tested on the last one

*Carter (2026-10-01, on the session's summary):* the lead of 2005–2020
is a good sign; the likeliest reason for 2021–26 is a temporary
change in market behaviour. Returns in that period were dominated by
stocks like Tesla and NVIDIA, which do not pass a value investor's
test; if this is a bubble, a value strategy is expected to trail
through it and to dominate again during and after the correction.

*What the record already says for and against:*

- For: SPY outran equal-weighted stocks of every size in 2021–26,
  its own thirty largest included, and the forest ranks NVDA, TSLA
  and META in the middle of its list (decision 32, items 3 and 7).
  That is the pattern the reading describes.
- Not explained by it: against stocks of their own size, a
  comparison that leaves the giants' index weight out, the
  candidate's picks stopped leading with the buys of 2019, and its
  protection in falls was smaller after 2020 (+3.2 points in 2022,
  +11.4 in 2008). A bubble in a handful of giants explains trailing
  SPY; it does not by itself explain no longer beating calm stocks'
  own neighbours.
- Cannot be told from the 2021–26 data: whether the lead returns
  after a correction. There has been none inside the panel.

*What can be tested:* the dataset's snapshots start at the end of
1997 and nothing in this repository has ever been run, selected or
read before 2005 (the 3-year fold calendar starts there). 1999–2004
holds the last bubble led by a few large, fast-growing, expensive
companies, its top (March 2000) and the three years after. The
forest cannot be used there: no fold model exists before 2005. Its
largest input can: the lowest 12-month volatility rank
(`vol_12m_rank`, 19% of the forest's importance; `vol_36m_rank` is
empty before 2000). So, as a **stand-in for the candidate**: lowest
12-month volatility, 12-month momentum and return on capital by mean
rank, the candidate's rule otherwise (rank floor, top 10 a month, at
most 2 per sector), read per pick against SPY and against same-size
candidates exactly as decision 30's diagnostic read the candidate.
Columns and the price panel only: nothing is fitted, no label is
read, no split tag is touched, no portfolio is simulated, nothing is
logged to the ledger.

*Is the stand-in the candidate?* Checked in the same run: it is run
over 2005–2026 too and set beside the candidate's own figures there
(same-size lead +0.046 / +0.059 / −0.016 for 2005–12 / 2013–20 /
2021–23). If it does not track them, what it shows for 1999–2004
says little about the candidate.

*Predictions, written before the run. If Carter's reading holds here
as it did for value strategies in general then:*

1. Buys of 1999 (momentum and the volatility rank exist from early
   1999), over their first year, which ends inside the bubble or at
   its top: behind SPY, and not ahead of their same-size peers.
2. Buys of 2000 to 2002, over three years: ahead of SPY by more than
   the candidate's 2005–2020 average (+0.025 a year), ahead of their
   same-size peers by 0.05 a year or more, and with a share of losers
   under half their peers'.
3. The stand-in tracks the candidate in 2005–2026: same-size lead
   within 0.03 of the candidate's in each of the three periods.

*What each outcome would mean:* 1 and 2 holding says this kind of
selection, in this dataset, did sit out the last bubble and was paid
after it, on years no choice here was made on: the reading is
consistent with the only precedent the data holds, though one
precedent and a stand-in. 2 failing (no lead after March 2000) would
count against it. Either way it cannot say that 2021–26 is a bubble,
or when a correction comes.

*What came out (2026-10-01; `scratch/2026-10-01-oos-diagnostics/diag_standin.py`,
git `1d5b4ec`; table in [the out-of-sample note](2026-10-01-out-of-sample.md),
"The last bubble"):* the stand-in (lowest 12-month volatility,
momentum and return on capital by mean rank; 120 picks a year).

| buys of | first year: against SPY | against same-size peers | three years: against SPY | against same-size peers | lost money over 3y (peers) |
|---|---|---|---|---|---|
| 1999 | −0.027 | −0.147 | +0.082 | +0.071 | 0.34 (0.55) |
| 2000 | +0.132 | +0.096 | +0.066 | +0.103 | 0.62 (0.64) |
| 2001 | +0.187 | +0.128 | +0.098 | +0.088 | 0.13 (0.41) |
| 2002 | +0.150 | +0.072 | +0.112 | +0.084 | 0.02 (0.26) |
| 2003 | +0.080 | −0.066 | −0.003 | −0.027 | 0.12 (0.21) |
| 2004 | +0.089 | +0.030 | +0.013 | +0.015 | 0.20 (0.25) |

*Against the predictions:* (1) held: the buys of 1999 trailed SPY
over their first year (29% beat it) and trailed their same-size
peers by 15 points. (2) held on return: the buys of 2000–02 led SPY
by 9.2 points a year over three years and their same-size peers by
9.2; missed on losers (0.25 against 0.44 of their peers, 0.58 of it,
not under half: the buys of 2000 lost money as often as their
peers). (3) held: the stand-in's same-size lead in 2005–12 / 2013–20
/ 2021–23 is +0.020 / +0.055 / −0.016 against the candidate's +0.046
/ +0.059 / −0.016.

*Read:* on the one earlier bubble in the data, on six cohorts no
choice in this repository was ever made on, this kind of selection
did what Carter's reading says: it lagged in the last year of the
run-up and was paid for three years after the top, against the index
and against stocks of its own size. That is real support, of a
limited kind:

- It is one precedent, read with a stand-in (a volatility rank where
  the candidate has a forest), and low risk, quality and momentum
  were chosen here knowing they paid in 2005–2020; that calm,
  profitable stocks did well after March 2000 is well known.
- The two episodes differ in kind. In 1999 the run-up was in small
  stocks: the smaller half of the investable stocks beat SPY by 51
  points over a year and the largest 5% matched it. In 2021–26 the
  smaller half trailed SPY by 33 points a year and the largest 1% by
  3: the excess is in a few giants inside the index. "Returns
  dominated by stocks that fail a value investor's test" describes
  both; "the index is the thing that is expensive" describes only
  the second, and it is the index the candidate is measured against.
- In the precedent the lag visible here lasted one cohort year and
  the buys made *during* it were ahead within three years. The buys
  of 2021, 2022 and 2023 are behind SPY after three years, because
  no correction has come inside the panel. The reading predicts that
  they recover relative to SPY when one does; nothing on disk can
  test that, and the reading cannot say when.

*Decided:* the reading is recorded in findings as the leading
hypothesis for 2021–26, with what supports it and what it does not
explain, not as a conclusion. It does not change decision 34 (nothing
further is run on 2021–26, no new blend). It does bear on Carter's
two open choices: it is a reason to paper-trade the fixed candidate
through whatever comes, and a reason for the market-state features
upstream, since "an era in which to stand aside" is exactly what a
stock's own columns cannot say.
