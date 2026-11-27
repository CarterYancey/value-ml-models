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

## Where the project stands

Carter asked on 2026-11-27 why models with precision far above the base
rate have not beaten the market. The answer, measured in
[why not the market](notes/2026-11-27-why-not-the-market.md) (decision
81), is this. The project has not failed to find skill. It has built a
low-beta, equal-weighted portfolio of calm, profitable, mostly large
stocks with 4 to 5 points a year of real selection skill against
same-size peers, and asked it to beat a cap-weighted index. That works
when the index falls often and fails when a few giants carry the index,
and the model has no input that tells it which kind of period it is in.

Three things could change the outcome. They lead the plan, in the
order of how much evidence supports them (decision 85).

1. **Put the skill inside the index's own structure.** Cap-weight the
   book, so that the gap between a size-broad equal-weighted band and
   the index disappears and the loser-avoidance is all that remains.
   The first instance is E11, the candidate's blend choosing the top 50
   large caps with an earnings yield of 5% or more, cap-weighted: 12.1%
   a year against SPY's 10.9% over 2005 to 2026, drawdown −37% against
   −53%, the same at three seeds. Next: three seeds on
   `dataset_v1.5.1`, then its pick list beside the candidate's.
2. **Give the portfolio a reason to buy less when the market is dear.**
   That needs either a market-state column from upstream or a row-level
   valuation floor. The earnings-yield floor is the stand-in that
   worked, and it recovered 1.6 of the 2.6 points E10 lacked in 2021 to
   2026. A floor tight enough to hold cash has not been tried.
3. **Raise the picks' upside without raising their losers.** Every
   attempt so far (regressions, run-up labels, one rare region) has
   failed. The search for a region reopens (decision 85.3): a steep
   recent fall as the region, and a model trained inside it to separate
   the market's over-reactions from justified sell-offs.

**How a portfolio is judged** (decision 83, amended by 85). A portfolio
is compared with SPY over the walk-forward years, 2005 to 2020, on
three things: its time-weighted return, its worst fall from a peak, and
how often its buys lost money against same-size peers. It is carried to
three seeds and proposed to Carter when it beats SPY on the first two
and its buys pass the screen rule (decision 74.4) against the control.
The years 2021 to 2026 are reported beside, as context: Carter expects
the strategies this project looks for to trail in those years. The
final value is read beside the table of five deposit schedules that
every report now carries (decision 84), because the deposit schedule
alone moves the candidate from 13% behind SPY to 1% ahead. More money
than SPY over the long run stays the goal in principle; 20% a year is
the stretch target, and the deep-value stock is the direction.

## Next session: start here

1. Read the section above, then
   [the decision log](notes/2026-11-26-decisions.md), decisions 81 to
   85 (the answer; E11 at three seeds; the goal; the backtest's realism,
   [its note](notes/2026-11-27-backtest-realism.md); Carter's review).
   Before those, the same sessions wrote
   [the rare-region program](notes/2026-11-26-rare-region.md)
   (decisions 78 to 80) and
   [the v1.5.1 program](notes/2026-11-26-v151-program.md) (decisions 74
   to 77). The sessions of 2026-11-25 wrote
   [the fallen-stock program](notes/2026-11-25-fallen-stocks.md)
   (decisions 61 to 72) and
   [the training cutoff](notes/2026-11-25-training-cutoff.md)
   (decision 60).
2. TODO.md says what to do next, under "Next, after 2026-11-27, third
   part". The candidate's runbook is [paper-trading.md](paper-trading.md).
3. The branch `claude/results-2026-11-26` carries this file, the code
   of these sessions and the promoted records. The configs and reports
   are on the lab branch `claude/lab-2026-11-26`, archived as a tag once
   the results branch merges.

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

**Why the candidate has not beaten the market (decisions 81, 82).**
The four measured causes are at the top of this file. The numbers: the
candidate beat SPY by 3 points a year over 2005 to 2020 (time-weighted
12.4% against 9.4%) and trailed by 8 over 2021 to 2026 (7.1% against
15.3%). A cap-weighted book of the top-decile large caps with no model
ended with 7% more money than SPY and a drawdown of −46% against −53%;
it is a home-made large-cap index, and it is the control that puts the
recent gap on the structure. E11, the best portfolio on record, holds
at three seeds: 12.1% to 12.3% a year against 10.9%, drawdown −37%,
beta 0.77, 4% less final money under flat deposits and 25% more under a
lump sum. The rank sell discipline destroys it through turnover.

**The rare-region program measured one region (decisions 78 to 80) and
reopens (decision 85).** Carter asked whether a model can learn the
rare case: a strong record, a steep fall, a recovery. The region tried
(liquid stocks 40% or more below their five-year high with positive
operating cash flow in 18 of 20 quarters, 16% of liquid rows) earns
1.9% a year against 3.4% for all liquid rows with 41% losers, wins in
2009 to 2012 and 2020 and loses every year from 2013 to 2018. Five
methods across 49 runs (training weights, the region as a universe,
forests seeing 5% of the columns a split, LightGBM with a tenth of the
columns, quantile regression) found no arm that passes the screen rule:
the more of a selection sat inside the region, the more of it lost
money. Of Carter's labels, "doubled without a crash" became a
one-month-reversal forest and "a run-up of 75%" was learned as
volatility. The next region is a steep recent fall.

**`dataset_v1.5.1` adds nothing to the candidate (decisions 74 to
77).** Every set with the new history, trend or event columns had the
control's lead and about two points more losers; the 8-K counts' gain
on the screen (+0.011 a year at three seeds) became 5% to 9% less money.
Labels defined against the S&P 500's path or drawdown are behind cell C
on losers. The blend on v1.5.1 reproduces the v1.4.1 final value to the
dollar, so the legs are not refit.

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
| C inside the rare region (folds 2008 to 2020); "earned 20% a year" by quantile regression | 3; 6 | lead over in-region peers +0.040, losers 0.33; lead at most +0.025, losers 0.48 to 0.61 | one region measured; the search reopens (85) |
| C, five-year horizon (folds 2007 to 2018) | 12 | old ranks: lead +0.032, losers 0.09; the three-year ordering repeats | closed |
| C, `dataset_v1.4.1`, all rows | 3 legs and the seeds of decision 57 | PR-AUC 0.585, p@20 0.75 against a base rate of 0.39 | **the candidate's forest** |
| C on `dataset_v1.4` (retired build) | 96; 38 in the floor; 14 in large caps | p@20 0.79 against 0.39 | **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base rate 0.38 |
| `label_3y_beat_spy`; excess CAGR ≥ 0 with drawdown < 0.3; "fell 50%"; regressions on CAGR; `cagr_ge_0`; the one-year labels; the recovery label (v1.4) | see the notes | no lead after 2013; no short leg (decision 39); closed as a leg (40, 49); an equivalent label (53) | closed |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on.**
   Carter took the one holdout look in cell C on 2026-10-01, on the old
   v1.4 build. Of the top 20 picks a year, 65% met the label, and of the
   top 50, 73%, against a base rate of 38%. Of the 60 top-20 picks (20
   a year for 2021, 2022 and 2023), 17 lost money over three years,
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
11. **The one rare region measured so far, stocks 40% or more below
    their five-year high with a strong cash-flow record, is the market's
    recovery, not a pool of mispriced survivors** (decisions 79, 80).
    Its rows have wider tails and a lower mean than the market. They win
    after crashes and lose through the long rise. Every selection that
    buys the region loses more often, and every selection that leads
    avoids it. Inside the region, as inside F50 (decision 63), the
    forest finds the stocks that fall least, not the ones that recover.
    This is a measurement of one region, not a verdict on the idea: the
    search for a better region, with a model trained inside it, is open
    again (decision 85.3).
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
- What separates the rare region's good years (2009 to 2012, 2020) from
  its bad ones (2013 to 2018)? Nothing in the row. The state of the
  market at the snapshot date would, and that is an upstream column.
- Does a model trained inside a region of steep recent falls separate
  the market's over-reactions from justified sell-offs better than the
  same model does across the whole universe? Carter's hypothesis
  (decision 85.3); the first region to try is 30% or more below the
  one-year high.
- Can information outside prices and financial statements rank upside?
  Insider and institutional transactions and the state of the market
  are the examples. They would be built upstream.
- Why do huber regressions on CAGR and on excess CAGR rank stocks so
  differently (decision 45)? Unexplained.

## Plan

Decision 36 stands: the bubble reading is the working assumption, the
candidate is paper-traded as it is, and the search continues. The three
remedies at the top of this file lead the plan; this is the order of
work (decision 85).

1. **The skill inside the cap-weighted structure.** E11 on
   `dataset_v1.5.1` at the forest's three seeds (two forest bundles need
   training first; one v1.5.1 backtest at a time, about 14 GB). Then a
   paper-trading list for E11 beside the candidate's, as a second
   portfolio. A dry run of that list already exists: on
   `inference_2026-11-20`, `vml-predict` with E11's filters and
   `--weighting marketcap` (decision 85.4) chose 50 of the 120
   top-decile large caps whose earnings yield was 5% or more (of 372
   above the liquidity floor). Energy is 39% of the weight and
   technology 26%; the largest positions are MU 12.8%, XOM 12.4% and
   CVX 7.8%. The floor does most of the choosing on that day: the model
   cuts 120 names to 50. That is a fact about the list, not a reason to
   change the rule before the seeds run.
2. **A reason to buy less when the market is dear.** The upstream
   market-state columns (the request of decision 46, now also the rare
   region's open question) would let a model learn it. Until then, a
   valuation floor tight enough to hold cash on the equal-weighted
   candidate: the 5% and 8% floors held none, because ten stocks always
   cleared them (decision 81); E6's 12.6% a year in 2021 to 2026 is the
   reason to look, its 8% less final money the reason for caution.
3. **Upside without losers: the region search reopens** (decision
   85.3). The next decision writes the regions (first, 30% or more
   below the one-year high) and the predictions, then trains the
   candidate's forest inside each region as a universe and as an
   emphasis, and reads its picks on the control's outcomes: lead over
   same-size peers, losers and doublers, inside the region and across
   the universe. Then the deep-value floors and universes of decision
   83.5: net current asset value, tangible book and the earnings yield,
   with the forest as the gate and the five-year horizon as the outcome.
4. **Paper trading** of the candidate follows
   [paper-trading.md](paper-trading.md). The November 2026 list came
   from the v1.4.1 bundles on 2026-11-24. The v1.5.1 build gives the
   same forest, so nothing is refit.
5. **Carter's other open decisions:** the larger-half filter (58), the
   training cutoff (60), the F50 portfolio (71), the price floor (71.3)
   and the Foamex request (73). **Upstream requests:** the market-state
   columns, a peer-relative label, a recovery label measured inside a
   region, and the Foamex price check. New columns arrive as a dataset
   version and run through decision 74's program.
6. **Later:** the rest of the realism audit (a cost model by size and
   era, taxes, market impact; none blocks the next step); Carter's rules
   for other model families (a logistic regression and an MLP on the
   ranks, judged on the screen first); the engine gaps (selling at the
   horizon, quarterly buys, a rank gate).

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
