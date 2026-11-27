# Findings

What the project knows now, and where it stands. Terms such as *cell*,
*look*, *p@20*, *base rate*, *lead* and *same-size peers* are defined
in [GLOSSARY.md](../GLOSSARY.md).

## What belongs in this file

- **It holds conclusions, not plans.** What to do next is in
  [next-steps.md](next-steps.md). The rules and criteria in force are in
  [decisions.md](decisions.md). What was done, run by run, is in
  [logbook.md](logbook.md).
- **Each conclusion is a measurement first**, with its numbers, dataset
  version and trial count, and then what it might mean, marked as a
  hypothesis until a run has tested it (CLAUDE.md, "Before writing a
  conclusion"). It links to the note that holds the tables.
- **A conclusion is a few sentences.** Tables longer than a few rows go
  in a note under [notes/](notes/).
- **It is rewritten, not appended to.** When a new result includes an
  older one, merge them. When a line of research closes, its conclusion
  shrinks to one row of the table "Lines of research" and one line in
  decisions.md, "Closed lines of research".
- **It changes when a conclusion changes**, not when a sweep ends.

**How to read the numbers.** Unless a line says otherwise, a number is
an average over the 16 walk-forward test years, 2005 to 2020, as
`split_folds.parquet` of the named dataset version defines them. Each
number is the best of the trials counted beside it, so it is
selection-biased; none is a result of record. Numbers from different
dataset versions, or from different universes, are never compared. New
work uses `dataset_v1.5.1`. The candidate's record is on
`dataset_v1.4.1`, and the v1.5.1 build reproduces it to the dollar.
Every v1.4 number in notes written before 2026-11-24 belongs to a build
that no longer exists and is context only.

## Where the project stands (2026-11-27)

The project has not failed to find skill. It has built a low-beta,
equal-weighted portfolio of calm, profitable, mostly large stocks,
whose picks beat stocks of the same size by 4 to 5 points a year. That
portfolio beat SPY by 3 points a year from 2005 to 2020 and trailed it
by 8 points a year from 2021 to 2026. The gap comes from the
portfolio's structure, not from the model: an equal-weighted portfolio
cannot keep pace with a cap-weighted index carried by a few giant
stocks, and the model has no input that tells it what kind of market it
is in (decision 81,
[why not the market](notes/2026-11-27-why-not-the-market.md)).

The best portfolio on record, E11, puts the model's skill inside the
index's own structure. It takes the candidate's ranking, chooses the 50
highest-ranked large caps with an earnings yield of 5% or more, and
weights them by market capitalization. At three seeds on
`dataset_v1.4.1` it earned 12.1% to 12.3% a year time-weighted against
SPY's 10.9%, with a worst drawdown of −37% against −53% and a beta of
0.77. It has not yet run on `dataset_v1.5.1`.

Under the portfolio rule of decision 85.1 (beat SPY over 2005 to 2020
on time-weighted return and worst drawdown, with buys that pass the
screen rule), the candidate, E10 and E11 all pass. None is shown to
beat SPY over the whole window to 2026.

## The portfolios of record

**The candidate** is defined in [decisions.md](decisions.md), "The
candidate and paper trading". These are its numbers of record, on
`dataset_v1.4.1`, with 35 basis points a side, buys and deposits from
2005 to 2026-08-21, and the forest refit at each year end after 2020:

| | final value on 260,000 | CAGR | time-weighted | worst drawdown |
|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 13.2% | 10.9% | −52.9% |
| **candidate, buy and hold** | 1,159,740 | 12.2% | 11.0% | −41.0% |
| candidate, rank sell discipline | 1,294,414 | 13.0% | 11.5% | −41.3% |

Over 2005 to 2020 the candidate earned 12.4% a year time-weighted
against SPY's 9.4%, with a worst drawdown of −41% against −53%. In
August 2026 it is 13% behind SPY, having trailed in every year since
2021 except 2022, by 3.9 to 14.5 points. The buys of 2021 trailed SPY
by 14.6 points a year over three years, and 72% of them lost money.

**E11**, at three seeds on `dataset_v1.4.1` (decision 82): 12.1% to
12.3% a year time-weighted, worst drawdown −37%, beta 0.77. Under flat
monthly deposits it ends with 4.2% less money than SPY (three-seed
mean); with all the money invested at the start it ends with 25% more.
The deposit schedule alone moves the candidate from 13% behind SPY to
1% ahead
([backtest realism](notes/2026-11-27-backtest-realism.md)).

The findings of 2026-11-26 counted 49 backtest configurations
completed on 2005 to 2020 (38 on v1.4, 7 on v1.4.1, 4 on v1.5.1), plus
seven failed runs of 2026-11-24. That count has not been checked
against the ledger since: the sandbox's ledger shard holds 46 completed
backtests on v1.4.1, including those of decisions 81 and 82, so the
count needs restating before it is cited.

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen
   on.** In the one holdout look in cell C (2026-10-01, the old v1.4
   build), 65% of the top 20 picks a year met the label, and 73% of the
   top 50, against a base rate of 38%. Of the 60 top-20 picks over 2021
   to 2023, 17 lost money over three years, against 54% of all rows
   ([out of sample](notes/2026-10-01-out-of-sample.md)).
2. **Company size decides more than any model.** Over three years the
   smaller half of investable stocks trailed SPY by 12 to 33 points a
   year, and the largest 5% by 0 to 6.5 points. Against same-size
   stocks the candidate's picks led in 13 of the 16 years from 2005 to
   2020, by 3.0 points a year in the first half and 5.3 in the second.
   In 2021 to 2026 SPY beat equal-weighted portfolios of stocks of
   every size ([large caps](notes/2026-10-01-large-caps.md)).
3. **The structure explains the recent gap to SPY; the model explains
   none of it.** A cap-weighted book of the top-decile large caps with
   no model ended with 7% more money than SPY and a worst drawdown of
   −46% (decision 81). The same names equal-weighted cost 2.9 points a
   year in 2021 to 2026 and gained 1.5 in 2005 to 2020.
4. **Inside the cap-weighted structure, avoiding predicted losers
   trades return for safety.** Every cut by the model lowered both the
   2021 to 2026 return and the drawdown, more so the deeper the cut. The
   forest alone pays more for the same safety than the blend, because it
   buys utilities, REITs and staples. An absolute earnings-yield floor
   inside the safe set recovered 1.6 of the 2.6 points a year that the
   same book without it lacked in 2021 to 2026 (decision 81).
5. **The model's skill is loser-avoidance, and downside is mostly past
   volatility.** The 12-month volatility rank alone predicts a fall of
   30% or 50% within a year as well as a forest does (decision 45). The
   volatility ranks are what keep the losers down; removing them costs
   losers, not lead (decisions 74, 78). In 2007 and 2008 the forest's
   picks fell 0.46 and 0.33 against their peers' 0.57 and 0.49.
6. **Selection is by rank within the period, not by confidence.** Every
   forest's score level is highest at market tops (decision 46). A
   rank-based sell discipline adds 12% to the candidate's final value
   over 21 years. Return on capital as a second ranking removes the
   forest's utilities and REITs.
7. **A screen gain is not a money gain.** It has happened three times
   (decisions 51, 77). The 8-K counts' forest led its peers by 1.1
   points a year at three seeds and ended with 5% to 9% less money.
8. **Top-20 precision does not say what a portfolio does; the model
   family does** (decision 76). LightGBM matches the forest's p@20, and
   its picks have no lead over their peers.
9. **The forest learns an absolute floor, not a comparison with SPY**
   (decision 75). Labels defined against SPY's path or drawdown are
   below a single-factor bar on precision. A label relative to same-size
   peers would have to come from upstream.
10. **The larger half of the candidate's picks adds a little** (decision
    57): +0.72 points a year at a standard error of 0.61, ahead in 11 of
    16 years, on every seed. Large caps alone (`log_marketcap_rank >=
    0.8`) earned the same final value as the candidate with four points
    fewer losing buys and a lead over peers 1.5 points larger.
11. **The one rare region measured is the market's recovery, not a pool
    of mispriced survivors** (decisions 79, 80;
    [rare region](notes/2026-11-26-rare-region.md)). Stocks 40% or more
    below their five-year high with a strong cash-flow record earned
    1.9% a year against 3.4% for all liquid rows, with 41% losers. They
    win in 2009 to 2012 and in 2020 and lose in every year from 2013 to
    2018. Every selection that buys the region loses more often. Inside
    the region, as inside F50, the forest finds the stocks that fall
    least, not the ones that recover. This measures one region, not the
    idea.
12. **Emphasis weights, subspace forests and column sub-sampling do not
    change what a forest buys** (decision 80.4). Sixteen of the 18
    emphasized arms and every subspace arm sit within two standard
    errors of their unemphasized counterparts.
13. **The own-history valuation columns are real but are not a
    selection** (decision 80.5). Where the price columns are absent, the
    sales yield and tangible book value against their five-year median,
    the earnings yield at the five-year peak and the book-to-market
    percentile are the top splits; the arm then has at best the
    control's lead, with more losers.
14. **Today's list barely depends on the most recent years.** A forest
    trained without the snapshots after 2021 changes one of the ten
    November picks, and one trained without those after 2018 changes two
    (decision 60, [training cutoff](notes/2026-11-25-training-cutoff.md)).

## Lines of research

Three-year horizon, `dataset_v1.5.1` inside the 100k floor, unless the
row says otherwise. Closed lines are also listed in decisions.md.

| line | trials | best result | status |
|---|---|---|---|
| Cell C, "not a loser" | 62 | the control: p@20 0.75, lead +0.029, losers 0.17; no arm ahead on both outcomes | **the candidate's forest stands** |
| Cell C, `dataset_v1.4.1`, all rows | 3 legs and the seeds of decision 57 | PR-AUC 0.585, p@20 0.75 against a base rate of 0.39 | **the candidate's forest** |
| Cell C on `dataset_v1.4` (retired build) | 96; 38 in the floor; 14 in large caps | p@20 0.79 against 0.39 | holdout look 1 of 1: p@20 0.65 |
| Portfolio structure: cap-weighted books and valuation floors (`dataset_v1.4.1`) | the 12 backtests of decision 81 and the 5 of decision 82 | E11 at three seeds: 12.1% to 12.3% time-weighted, drawdown −37% | **open: E11 on v1.5.1 next** |
| "Doubled without a crash" | 22 | old ranks: lead +0.110, losers 0.38; a reversal forest among stocks that lose | closed |
| "A real gain without a crash"; "a run-up of 75%"; CAGR of 20% or a drawdown no deeper than SPY's; the five full-path labels | 5 to 18 each | lead at most the control's; learned as volatility | closed |
| Cell C inside the rare region (folds 2008 to 2020); "earned 20% a year" by quantile regression | 3; 6 | lead over in-region peers +0.040, losers 0.33; lead at most +0.025, losers 0.48 to 0.61 | one region closed; the search is open (85.3) |
| Cell C, five-year horizon (folds 2007 to 2018) | 12 | old ranks: lead +0.032, losers 0.09 | closed |
| The fallen-stock program (F and W universes, `dataset_v1.4.1`) | see the note | F50 forest portfolio beats SPY before 2021 by 2.5% to 4.9% in money at three seeds; W30 within 2% of SPY | closed; F50 portfolio waiting on Carter (71.1) |
| `label_3y_beat_spy`; excess CAGR ≥ 0 with drawdown < 0.3; "fell 50%"; regressions on CAGR; `cagr_ge_0`; the one-year labels; the recovery label (v1.4) | see the notes | no lead after 2013; no short leg; an equivalent label (`cagr_ge_0`) | closed |

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable and
beats the market by avoiding losers. The precision held out of sample:
the candidate bought fewer losers and suffered shallower falls. What it
did not do is earn the index's return in 2021 to 2026, years in which
the index beat stocks of every size.

The working assumption (decision 36) is that 2021 to 2026 is a bubble
that a value strategy trails through and then waits out. Conclusion 2
is consistent with it, and so is the one precedent in the data: on 1999
to 2004 a stand-in for the candidate trailed in the last year of the
run-up and led by about 9 points a year for the buys of 2000 to 2002.
The record cannot yet show whether the buys of 2021 to 2023 recover.

## Open questions

Questions the evidence does not yet answer. The experiments that would
answer them are in next-steps.md.

- Is 2021 to 2026 a bubble, and does the candidate lead again when it
  deflates? Only paper trading and time can answer.
- Does a model trained inside a region of steep recent falls separate
  the market's over-reactions from justified sell-offs better than the
  same model does across the universe? (Carter's hypothesis, 85.3.)
- What separates the rare region's good years from its bad ones?
  Nothing in the row; the state of the market at the snapshot date
  might, and that is an upstream column.
- Can information outside prices and financial statements, such as
  insider and institutional transactions, rank upside?
- Why do huber regressions on CAGR and on excess CAGR rank stocks so
  differently (decision 45)?

## Sealed holdout record

`reports/final_evals.csv` records 20 looks at the sealed holdout. The
look count is part of every holdout number: a cell looked at twice is no
longer a clean test. No look has been taken on `dataset_v1.4.1` or
`dataset_v1.5.1`.

| cell | looks | what the looks showed |
|---|---|---|
| **3y cell C, "not a loser" (v1.4, 2021 to 2023, old build)** | **1** | **p@20 0.65, top 50 0.73, base rate 0.38; PR-AUC 0.56; picks −0.09 a year against SPY, all rows −0.25** |
| 1y, 2y, 5y cells on v1.0 and v1.1 | 1 to 5 each | `cagr_ge_0`: PR-AUC 0.59 to 0.68 against about 0.5; `beat_spy`: little or no skill. See `reports/final_evals.csv` |

A look inside a universe uses up the whole label's cell. The one look in
cell C has no baselines computed on the holdout rows; computing one
would be a second look, and that is Carter's to take. Process incidents
are in [notes/process-issues.md](notes/process-issues.md).
