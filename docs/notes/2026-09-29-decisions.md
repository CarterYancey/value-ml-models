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
