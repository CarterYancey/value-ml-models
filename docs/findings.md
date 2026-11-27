# Findings

This file says what we know now, label by label, and what is planned.
It is rewritten each time rather than appended to, and it stays under
about 250 lines. Terms such as *cell*, *look*, *p@20*, *base rate*,
*lead* and *same-size peers* are defined once, in
[GLOSSARY.md](../GLOSSARY.md).

- [logbook.md](logbook.md) records what was done, in order. Read it
  first.
- Each conclusion below links to a note in [notes/](notes/) that holds
  the tables, checks and reasoning. [agents.md](agents.md) describes
  how an unattended session works.

**How to read the numbers.** Unless a line says otherwise, a number is
an average over the 16 walk-forward test years, 2005 to 2020, as
`split_folds.parquet` of the named dataset version defines them. Each
number is the best of the trials counted beside it, so it is
selection-biased. None is a result of record. Numbers from different
dataset versions, or from different universes, are never compared.
**New work uses `dataset_v1.5.1`** (decision 77). The candidate's record
is on `dataset_v1.4.1` (decision 55), and the v1.5.1 build reproduces
it to the dollar. Every v1.4 number in notes before 2026-11-24 belongs
to a build that no longer exists and is context only.

## Next session: start here

1. The latest session (2026-11-26 into 2026-11-27) ended with Carter's
   question, why the models have not beaten the market, answered in
   [why not the market](notes/2026-11-27-why-not-the-market.md)
   (decision 81 of [the decision log](notes/2026-11-26-decisions.md)):
   the structure, the loser-avoidance trade, the missing market-level
   input and the timing of the deposits, with twelve backtests. Before
   that it wrote [the rare-region program](notes/2026-11-26-rare-region.md),
   decisions 78 to 80: Carter's run-up labels, feature sets built from
   fundamentals, and five ways of making a model attend to stocks with a
   strong record that have fallen hard. Nothing there passes the screen
   rule. Earlier the same day,
   [the v1.5.1 program](notes/2026-11-26-v151-program.md)
   (decisions 74 to 77) found that the new columns, labels and boosted
   models add nothing to the candidate. The sessions of 2026-11-25 wrote
   [the fallen-stock program](notes/2026-11-25-fallen-stocks.md)
   (decisions 61 to 72) and
   [the training cutoff](notes/2026-11-25-training-cutoff.md)
   (decision 60).
2. TODO.md says what to do next, under "Next, after 2026-11-27". The
   candidate's runbook is [paper-trading.md](paper-trading.md).
3. The branch `claude/results-2026-11-26` carries this file, the
   v1.5.1 support code, the emphasis and region features of the
   harness, decisions 74 to 80 and the promoted records. The configs and
   reports are on the lab branch `claude/lab-2026-11-26`, which is
   archived as a tag once the results branch merges.

## State (2026-11-27)

Carter's goal is a manageable number of high-precision, low-risk
selections with upside. They are judged first on what a portfolio of
the picks went on to do, and second on precision.

**The candidate** (decision 24, unchanged since 2026-09-30) is a forest
trained on cell C, the label "not a loser" (a three-year CAGR of zero
or more, never 30% below the entry price). Its score is combined by
mean rank with 12-month momentum and return on capital. The portfolio
buys the ten highest-ranked stocks each month, at most two per sector,
with equal weights, inside Carter's liquidity floor
(`dollar_volume_3m_rank >= 0.2`). The backtest charges 35 basis points
a side, buys and deposits from 2005 to 2026-08-21, and refits the
forest at each year end after 2020. All three legs were refit on
`dataset_v1.4.1` on 2026-11-24. These are the numbers of record:

| | final value on 260,000 | CAGR | TWR | worst drawdown |
|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 13.2% | 10.9% | −52.9% |
| **candidate, buy and hold** | 1,159,740 | 12.2% | 11.0% | −41.0% |
| candidate, rank sell discipline | 1,294,414 | 13.0% | 11.5% | −41.3% |

The CAGR is the money-weighted growth rate of the deposits into the
final value. It has been the metric of record since decision 72.

**The screen rule** (decision 74.4) decides whether a new model beats
the candidate's. Each model's picks are compared with stocks of the
same size on two outcomes: the lead, which is the picks' mean
three-year CAGR minus their peers', and the share of picks that lost
money. The comparison is paired by test year with the control, which is
the candidate's forest in cell C on the 112 old rank columns inside the
100k liquidity floor: p@20 0.75, a lead of +0.029 a year, and 17%
losers against 30% for its peers. To pass, a model's gain over the
control must be positive at about two standard errors, ahead in ten or
more of the sixteen years, no worse than noise in either half of the
period, and this must hold for both outcomes. A model that passes goes
on to three seeds and then a backtest.

**Why the candidate has not beaten the market (decision 81).** Carter
asked why models that predict their labels far above the base rate have
not beaten the market. The candidate beat SPY by 3 points a year over
2005 to 2020 (time-weighted 12.4% against 9.4%) and trailed by 8 over
2021 to 2026 (7.1% against 15.3%); the money-weighted CAGR counts the
six years most, because the deposits made the account largest then.
Four causes were measured. First, the structure: a cap-weighted book of
this dataset's top-decile large caps with no model at all ended with 7%
more money than SPY, a drawdown of −46% against −53%, and kept pace in
2021 to 2026 (15.6% against 15.3%), where the equal-weighted candidate
earned 7.1%. Second, the skill is loser-avoidance, and loser-avoidance
leaves out the volatile winners: inside that cap-weighted book every
cut by the model lowered the 2021 to 2026 return while it lowered the
drawdown and the losers, the deeper the cut the more of both. Third, the
model has no input about the market's level; an absolute earnings-yield
floor of 5%, a row-level stand-in, recovered most of the recent gap.
Fourth, the deposits. The closest portfolio to the goal is the
candidate's blend choosing the top 50 large caps with an earnings yield
of 5% or more, cap-weighted: 12.1% a year against SPY's 10.9% over
2005 to 2026, drawdown −37% against −53%, beta 0.77, one point a year
behind SPY in 2021 to 2026, and 3.9% less final money. At three seeds
it holds (decision 82): 12.1% to 12.3% against 10.9%, drawdown −37%,
4.2% less final money; the rank sell discipline destroys it through
turnover. The
thesis held for sixteen years that held two crashes and failed in a
six-year stretch carried by the stocks a loser-avoiding model declines
to hold.

**The rare-region program is closed (decisions 78 to 80).** Carter
asked whether a model can learn the rare case: a stock with a strong
record that has fallen hard and then recovers. The region was defined
as liquid stocks 40% or more below their five-year high whose operating
cash flow was positive in 18 of the last 20 quarters; it is 16% of the
liquid rows. Its rows earn a mean three-year CAGR of 1.9% against 3.4%
for all liquid rows, with 41% losers against 37% and 18.5% doublers
against 15.9%. It earns in 2009 to 2012 and in 2020, and loses in every
year from 2013 to 2018. Five methods were tried across 49 runs: weighting
the region's rows three and ten times in training, training on the
region alone, forests that see 5% of the columns at each split, LightGBM
with a tenth of the columns per tree, and quantile regression for the
upper tail of returns. No arm passes the screen rule. In every sweep,
the more of a selection sat inside the region, the more of it lost
money, from 0.6% inside and 17% losers for the control to 47% to 86%
inside and 44% to 61% losers for the arms that bought the region. Given
the region's columns and more of its weight, the forest scored the
region's rows lower, not higher. Of Carter's labels, "doubled without a
crash" on the old ranks became a one-month-reversal forest: a lead of
+0.081 a year over the control, 38% losers, and peers that lost money
half the years after 2008. "A run-up of 75%" was learned as volatility.
Of the feature sets, the rank columns without the technical family plus
the 28 unranked history columns (162 columns) matched the control's
lead with 5.6 points more losers; the compact own-history sets were
worst everywhere.

**`dataset_v1.5.1` adds nothing to the candidate (decisions 74 to
77).** Every set that included the new history, trend or event columns
had the control's lead and about two points more losers. The one gain
beyond noise, from the 8-K filing counts (+0.011 a year at three seeds),
ended with 5.1% less money on its own and 8.6% less in the blend. The
path-average twin of cell C picks the same stocks. Every label defined
against the S&P 500's path or drawdown is behind cell C on losers.
LightGBM at the 2026-09 size reaches the forest's p@20 with no lead
over peers. The blend on v1.5.1 ends 2005 to 2020 with exactly the
v1.4.1 final value, so the legs are not refit.

**The fallen-stock program is closed (decisions 61 to 73).** No tree
model learns the recovery label in any universe. The "not a loser"
forest trained inside F50 (stocks 50% or more below their five-year
high) finds the fallen stocks that do not fall further. Its portfolio
ends 2020 with 2.5% to 4.9% more money than SPY at three seeds, and
below SPY at two seeds of three when valued at the end of 2023. Whether
it runs beside the candidate is Carter's decision.

**The candidate is not shown to beat SPY.** At the end of 2020 it was
ahead by final value and by TWR. In August 2026 it is 13% behind, having
trailed SPY in every year since 2021 except 2022, by 3.9 to 14.5 points.
The buys of 2021 trailed SPY by 14.6 points a year over three years and
72% of them lost money. In all, 49 backtest configurations have
completed on 2005 to 2020 (38 on v1.4, 7 on v1.4.1, 4 on v1.5.1), plus
seven failed runs of 2026-11-24.

| cell (three-year horizon, `dataset_v1.5.1` inside the 100k floor unless said) | trials | best result | status |
|---|---|---|---|
| C, "not a loser" | 62 | the control: p@20 0.75, lead +0.029, losers 0.17. No arm ahead on both outcomes | **closed: the candidate's forest stands** |
| "doubled without a crash" (run-up of 100%, never 40% down) | 22 | old ranks: lead +0.110, losers 0.38; a reversal forest among stocks that lose | closed: not a leg |
| "a real gain without a crash"; "a run-up of 75%"; CAGR of 20% or a drawdown no deeper than SPY's; the five full-path labels | 5 to 18 each | lead at most the control's; learned as volatility; a calmer, poorer cell C; cell C's twin | closed |
| C inside the rare region (folds 2008 to 2020); "earned 20% a year" by quantile regression | 3; 6 | lead over in-region peers +0.040, losers 0.33; lead at most +0.025, losers 0.48 to 0.61 | closed |
| C, five-year horizon (folds 2007 to 2018) | 12 | old ranks: lead +0.032, losers 0.09; the three-year ordering repeats | closed |
| C, `dataset_v1.4.1`, all rows | 3 legs and the seeds of decision 57 | PR-AUC 0.585, p@20 0.75 against a base rate of 0.39 | **the candidate's forest** |
| C on `dataset_v1.4` (retired build) | 96; 38 in the floor; 14 in large caps | p@20 0.79 against 0.39 | **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base rate 0.38 |
| `label_3y_beat_spy`; excess CAGR ≥ 0 with drawdown < 0.3; "fell 50%"; regressions on CAGR; `cagr_ge_0`; the one-year labels; the recovery label (v1.4) | see the notes | no lead after 2013; no short leg (decision 39); closed as a leg (40, 49); an equivalent label (53) | closed |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on.**
   Carter took the one holdout look in cell C on 2026-10-01, on the old
   v1.4 build. Of the top 20 picks a year, 65% met the label, and of the
   top 50, 73%, against a base rate of 38%. 28% of the top 20 lost money
   against 54% of all rows
   ([out-of-sample note](notes/2026-10-01-out-of-sample.md)).
2. **Company size decides more than any model, so every selection is
   read against same-size peers.** Over three years the smaller half of
   investable stocks trailed SPY by 12 to 33 points a year, and the
   largest 5% by 0 to 6.5 points. Against same-size stocks the
   candidate's picks led in 13 of the 16 years from 2005 to 2020, by 3.0
   points a year in the first half and 5.3 in the second. The buys of
   2021 trailed their peers by 6.4 points; the buys of 2022 led by 3.5
   and those of 2023 by 6.0. In 2021 to 2026 SPY beat equal-weighted
   portfolios of stocks of every size.
3. **The larger half of the candidate's picks adds a little** (decision
   57): +0.72 points a year at a standard error of 0.61, ahead in 11 of
   16 years, on every seed. This filter is proposed to Carter (decision
   58).
4. **Selection is by rank within the period, not by confidence.** Every
   forest's score level is highest at market tops (decision 46). A
   rank-based sell discipline adds 12% to the final value over 21
   years. Return on capital as a second ranking removes the forest's
   utilities and REITs.
5. **Downside is mostly past volatility.** The 12-month volatility rank
   alone predicts a 30% or 50% fall within a year as well as a forest
   does, so there is no short leg (decision 45). The picks are judged
   against their peers, not the market (decision 50): in 2007 and 2008
   the forest's picks fell 0.46 and 0.33 against their peers' 0.57 and
   0.49.
6. **A screen gain is not a money gain.** This has happened three times
   (decisions 51, 77). The 8-K counts' forest led by 1.1 points a year
   at three seeds and ended with 5% to 9% less money. An arm goes from
   the screen to a backtest, never straight into the candidate.
7. **Two builds can share a version label** (decision 54), so every
   record carries `dataset_sha256`. The v1.5.1 control reproduces the
   v1.4.1 candidate to the dollar (decision 77). Today's list barely
   depends on the snapshots of 2021 to 2023 (decision 60).
8. **The forest learns an absolute floor, not a comparison with SPY**
   (decision 75). A peer-relative target is a question for upstream.
9. **Top-20 precision does not say what a portfolio does; the model
   family does** (decision 76). LightGBM matches the forest's p@20 and
   its picks have no lead over their peers.
10. **The stock's own history buys nothing in cell C** (decisions 74,
    78). The history and trend ranks, the raw fundamentals and the
    compact own-history sets give the control's lead or less with 2 to 7
    points more losers. The volatility ranks are what keep the losers
    down. Removing them costs losers, not lead.
11. **The rare region of fallen stocks with a strong record is the
    market's recovery, not a pool of mispriced survivors** (decisions
    79, 80). Its rows have wider tails and a lower mean than the market.
    They win after crashes and lose through the long rise. Every
    selection that buys the region loses more often, and every selection
    that leads avoids it. Given the region's columns and ten times its
    weight, the forest reads its lower label rate correctly and scores
    it low. Inside the region, as inside F50 (decision 63), the forest
    finds the stocks that fall least, not the ones that recover.
12. **The own-history valuation columns are real and are not a
    selection** (decision 80.5). Where the price columns are absent, or
    where the question is the upper tail of returns, the sales yield and
    tangible book value against the five-year median, the earnings yield
    at the five-year peak and the book-to-market percentile are the top
    splits. The arm then has at best the control's lead with more
    losers.
13. **Emphasis weights, subspace forests and column sub-sampling do not
    change what a forest buys** (decision 80.4). Sixteen of the 18
    emphasized arms and every subspace arm sit within two standard
    errors of their unemphasized counterparts, and the same columns lead
    at a third of the weight.
14. **The structure explains the recent gap to SPY; the model explains
    none of it** (decision 81). A cap-weighted book of the top-decile
    large caps with no model kept pace with SPY in 2021 to 2026 and beat
    it over the whole window with a shallower drawdown. An
    equal-weighted book of the same names cost 2.9 points a year in 2021
    to 2026 and gained 1.5 in 2005 to 2020.
15. **Inside the index's own structure, avoiding the predicted losers
    trades return for safety** (decision 81). Every cut by the model
    lowered the 2021 to 2026 return and the drawdown together, the
    deeper the cut the more of both; the forest alone pays more for the
    same safety than the blend, because it buys utilities, REITs and
    staples. Over 2005 to 2020 the blend's top 50 beat SPY by 2.2 points
    a year with 15 points less drawdown. An absolute earnings-yield floor
    inside the safe set recovered most of the 2021 to 2026 shortfall.

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable. It
held out of sample: the candidate bought fewer losers and suffered
shallower falls. What it did not do is earn the index's return in 2021
to 2026, years in which the index beat every size of stock.

**Carter's working assumption (decision 36)** is that 2021 to 2026 is a
bubble led by stocks that fail a value investor's test. A value
strategy trails through such a period, leads again during and after the
correction, and should be waited out. Conclusion 2 supports this, and
so does the one precedent in the data, 1999 to 2004. The record cannot
yet show whether the buys of 2021 to 2023 recover.

## Open questions

- Is 2021 to 2026 a bubble, and does the candidate lead again when it
  deflates? Only paper trading and time can answer.
- What is the goal, exactly? By final money against SPY on a date
  inside a mega-cap boom, no loser-avoiding book in the record wins, and
  the best comes within 4%. By drawdown, losers and return per unit of
  market risk, that book wins on every reading. Carter's call (decision
  81).
- What separates the rare region's good years (2009 to 2012, 2020) from
  its bad ones (2013 to 2018)? Nothing in the row. The state of the
  market at the snapshot date would, and that is an upstream column.
- Can information outside prices and financial statements rank upside?
  Insider and institutional transactions and the state of the market
  are the examples. They would be built upstream.
- Why do huber regressions on CAGR and on excess CAGR rank stocks so
  differently (decision 45)? Unexplained.

## Plan

Decision 36 stands: the bubble reading is the working assumption, the
candidate is paper-traded as it is, and the search continues.

1. **Paper trading** follows [paper-trading.md](paper-trading.md). The
   November 2026 list came from the v1.4.1 bundles on 2026-11-24. The
   v1.5.1 build gives the same forest, so nothing is refit.
2. **Carter's open decisions:** the goal itself (final money against
   SPY by a date, or return per unit of risk; decision 81), the
   larger-half filter (58), the training cutoff (60), the F50 portfolio
   (71), the price floor (71.3) and the Foamex request (73).
2a. **The best portfolio on record is not yet proposed.** Decision 82
   ran E11 at three seeds: 12.1% to 12.3% a year time-weighted against
   SPY's 10.9%, drawdown −37% against −53%, beta 0.77, and 4.2% less
   final money at the three-seed mean. The rank sell discipline destroys
   it (5,800 sales, costs of half the deposits), so it is held to the
   horizon. What happens to it depends on item 2's first question.
3. **Upstream requests:** market-state columns per snapshot date (now
   also the rare region's open question), a peer-relative label, a
   recovery label measured inside a region, and the Foamex price check.
   New columns arrive as a dataset version and run through decision 74's
   program: the control rerun, the screen, three seeds, then money.
4. **Carter's rules** for other model families come next (research plan
   item 7): a logistic regression and an MLP on the ranks, judged on the
   screen first (conclusion 9).
5. New arms are judged on walk-forward 2005 to 2020 against same-size
   peers, in both halves and on three seeds, with the rule written
   before the run (decision 50), and then in money (decision 51). The
   years 2021 to 2026 are context only.
6. **Before any unattended backtest chain on v1.5.1, cut the backtest's
   memory.** A run peaks at 13.8 GB of the sandbox's 14 (decision 77.4).

## Sealed holdout record

`reports/final_evals.csv` records 20 looks at the sealed holdout. The
look count is part of every holdout number: a cell looked at twice is
no longer a clean test. No look has been taken on `dataset_v1.4.1` or
`dataset_v1.5.1`.

| cell | looks | what the looks showed |
|---|---|---|
| **3y C, "not a loser" (v1.4 [2021–23], old build)** | **1** | **p@20 0.65, top 50 0.73, base rate 0.38; PR-AUC 0.56; picks −0.09 a year against SPY, all rows −0.25** |
| 1y, 2y, 5y cells on v1.0 and v1.1 | 1 to 5 each | cagr_ge_0: PR-AUC 0.59–0.68 against about 0.5; beat_spy: none to barely any skill. See `reports/final_evals.csv` |

A look inside a universe uses up the whole label's cell. The one look
in cell C has no baselines computed on the holdout rows. Computing one
would be a second look, and that look is Carter's to take. Process
rules are in CLAUDE.md. Incidents are in
[notes/process-issues.md](notes/process-issues.md).
