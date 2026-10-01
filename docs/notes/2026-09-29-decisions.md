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
