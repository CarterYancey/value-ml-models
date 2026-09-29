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
