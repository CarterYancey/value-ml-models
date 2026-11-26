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
a fold mean over the 16 walk-forward folds. The test years are 2005 to
2020, as `split_folds.parquet` of the named dataset version defines
them. Each number is the best of the trials counted beside it, so it
is selection-biased. None is a result of record. Numbers from
different dataset versions, or from different universes, are never
compared. **The dataset of record for new work is `dataset_v1.5.1`**
(decision 77); the candidate's record is on `dataset_v1.4.1` (decision
55), and the v1.5.1 build reproduces it to the dollar. Every v1.4
number in the notes before 2026-11-24 belongs to a build that no longer
exists and is context only.

## Next session: start here

1. The latest session was on 2026-11-26: `dataset_v1.5.1` arrived and
   [the v1.5.1 program](notes/2026-11-26-v151-program.md) ran its new
   columns, labels and two boosters through cell C (decisions 74 to 77
   of [the decision log](notes/2026-11-26-decisions.md)). Nothing
   improves on the candidate; the program is closed. Earlier the same
   day Carter rejected the Foamex price path as a data error
   ([upstream request](notes/2026-11-26-upstream-foamex-price-check.md),
   decision 73). The sessions of 2026-11-25 wrote
   [the fallen-stock program](notes/2026-11-25-fallen-stocks.md)
   (decisions 61 to 72) and
   [the training cutoff](notes/2026-11-25-training-cutoff.md)
   (decision 60). The session of 2026-11-24 wrote
   [dataset_v1.4.1 and the size band](notes/2026-11-24-v141-and-size-band.md)
   (decisions 55 to 59).
2. TODO.md says what to do next, under "Next, after 2026-11-26". The
   candidate's runbook is [paper-trading.md](paper-trading.md).
3. The branch `claude/results-2026-11-26` carries this file, the
   v1.5.1 support code, decisions 74 to 77 and the promoted records.
   The configs and reports are on the lab branch `claude/lab-2026-11-26`,
   which is archived as a tag once the results branch merges.

## State (2026-11-26)

Carter's goal is a manageable number of high-precision, low-risk
selections with upside. They are judged first on what a portfolio of
the picks went on to do, and second on precision.

**The candidate** (decision 24, unchanged since 2026-09-30) is the
forest trained on cell C, combined by mean rank with 12-month momentum
and return on capital. It buys the top 10 each month, at most 2 per
sector, with equal weights, inside Carter's floor
(`dollar_volume_3m_rank >= 0.2`). The backtest takes 35 bps a side as
costs. It buys and deposits from 2005 to 2026-08-21 and refits the
forest at each year end after 2020. All three legs were refit on
`dataset_v1.4.1` on 2026-11-24, and these are the numbers of record:

| | final value on 260,000 | CAGR | TWR | worst drawdown |
|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 13.2% | 10.9% | −52.9% |
| **candidate, buy and hold** | 1,159,740 | 12.2% | 11.0% | −41.0% |
| candidate, rank sell discipline | 1,294,414 | 13.0% | 11.5% | −41.3% |

The CAGR is the money-weighted growth rate of the deposits into the
final value, the metric of record since decision 72. The TWR is read
only beside it.

**`dataset_v1.5.1` adds nothing to the candidate (decisions 74 to
77).** The build adds the stock's own fundamental history (five-year
medians, z-scores, normalized yields, distance from own peaks), wider
trend columns, fourteen trailing-year 8-K counts and full-path labels.
In cell C inside the 100k floor, with the candidate's forest at seed
23, every set with new columns has the control's lead over same-size
peers (+0.029 a year) and about two points more losers. The one gain
beyond noise is the 8-K counts added to the old ranks: +0.011 a year
at three seeds, ahead in 13 of 16 years, with 1.4 points more losers.
In money that forest ends with 5.1% less than the control alone and
8.6% less as the candidate's forest leg, with the buys' lead over
same-size peers a point higher or the same. The counts are not
carried. The path-average twin of cell C picks the same stocks; every
label defined against SPY's own path or drawdown is behind cell C on
losers and below a single-factor bar on precision. LightGBM at the
2026-09 size reaches the forest's p@20 and its picks have no lead over
their peers. The candidate's blend on v1.5.1 ends 2005–2020 with
exactly the v1.4.1 final value, so the legs are not refit.

**The fallen-stock program ran six rounds and is closed (decisions 61
to 73).** No tree model learns the recovery label (a stock doubling
within three years) in any universe. The "not a loser" forest trained
inside F50 (liquid stocks 50% or more below their 5-year high) finds
the fallen stocks that do not fall further: a portfolio of its picks,
2006 to 2020, ends 2020 with 2.5% to 4.9% more money than SPY at three
seeds (CAGR 12.9% to 13.1% against 12.6%), with a drawdown of −58%
against −53%; valued at the end of 2023 it ends below SPY at two seeds
of three. Every deeper fall ends behind SPY on both windows. Whether
the F50 portfolio runs beside the candidate is Carter's decision. The
W70 run rests on a 1-cent price that upstream is asked to check
(decision 73).

**The candidate is not shown to beat SPY.** At the end of 2020 it was
ahead of SPY by final value and by TWR. In August 2026 it is 13%
behind. The run to the end of 2020, valued at the end of 2023:

| 2005–2020 run | final value on 192,000 | TWR |
|---|---|---|
| candidate | 932,471 | 11.8% |
| SPY | 732,110 | 9.6% |

The candidate's yearly return minus SPY's, in points:

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to August |
|---|---|---|---|---|---|
| −8.9 | +2.3 | −3.9 | −11.4 | −14.5 | −13.2 |

The buys of 2021 are the worst cohort in the record: over three years
they trailed SPY by 14.6 points a year and 72% of them lost money. The
buys of 2022 matched SPY; the buys of 2023 trailed it by 4.3 points.
In all, 49 backtest configurations have completed on 2005–2020: 38 on
v1.4, 7 on v1.4.1, 4 on v1.5.1. Seven failed runs of 2026-11-24 count
as trials too.

| cell (3-year horizon) | trials | best result | status |
|---|---|---|---|
| C, "not a loser", `dataset_v1.5.1`, inside the 100k floor | 33 (6 column sets, 3 seeds, 10 LightGBM, 2 XGBoost, 8 bars) | the control (112 old ranks): p@20 0.75, lead over same-size peers +0.029 a year, losers 0.17 against 0.30. No arm ahead on both outcomes | **closed: the candidate's forest stands** |
| the five full-path cells of v1.5.1 inside the floor | 9 each | path-positive "not a loser" is cell C's twin (p@20 0.77 against 0.44); the four relative or run-up cells are below a bar | closed |
| C, `dataset_v1.4.1`, all rows | 3 legs and the seeds of decision 57 | forest on 112 ranks: PR-AUC 0.585, p@20 0.75 against 0.39. Blend screen inside the 100k floor: lead +0.030 / +0.053 a year, losers 0.26 / 0.16 against 0.33 / 0.28 | **the candidate's forest** |
| C on `dataset_v1.4` (retired build) | 96 all rows; 38 inside the floor; 14 inside large caps | p@20 0.79 against 0.39 | **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base rate 0.38 |
| `label_3y_beat_spy` inside large caps (v1.4) | 16 | forest PR-AUC 0.48 against 0.45; no lead after 2013 | closed |
| `fwd_3y_excess_cagr > 0 & dd < 0.3` inside large caps (v1.4) | 10 | p@20 below the base rate | closed |
| "fell 50% from entry", 1y and 3y, liquid half (v1.4) | 8 each | 3y forest PR-AUC 0.49 against 0.31; the 1y forest below `vol_12m` alone | closed: no short leg (decision 39) |
| regressions on 3y CAGR or excess, screened in the floor (v1.4) | 8 | huber led peers by +0.072 / +0.054 with losers 0.39 / 0.37 | closed as a leg (decisions 40, 49) |
| `label_3y_cagr_ge_0` (v1.4) | 3 seeds | the same picks as cell C by final value | an equivalent label (decision 53) |
| the 1-year labels, the recovery label, `fwd_3y_cagr >= 0.15` | see the notes | | closed earlier |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on,
   and that is what it is good for.** Carter ran the one holdout look
   in cell C on 2026-10-01, on the old v1.4 build: of the top 20 picks
   a year 65% met the label, of the top 50 73%, against a base rate of
   38%; 28% of the top 20 lost money against 54% of all rows (decision
   29, [out-of-sample note](notes/2026-10-01-out-of-sample.md)).
2. **Company size decides more than any model, and "beats the average
   stock" is not skill.** Over three years, stocks trailed SPY by these
   points a year, by size and entry period:

   | entries of | the smaller half of investable stocks | the largest 5% |
   |---|---|---|
   | 2005–12 | −12 | 0 |
   | 2013–20 | −18 | −2.5 |
   | 2021–23 | −33 | −6.5 |

   So every selection is read against same-size peers.
3. **Against same-size stocks the candidate leads in 2005–2020 and by
   nothing after.** On v1.4.1 the blend's screen picks led their peers
   in 13 of 16 years, by 3.0 points a year in the first half and 5.3
   in the second. The buys of 2021 trailed their peers by 6.4 points;
   the buys of 2022 led by 3.5 and of 2023 by 6.0.
4. **In 2021–26 SPY beat equal-weighted portfolios of stocks of every
   size**, its own thirty largest members included. A few very large,
   volatile companies carried the index, and a model that favours calm
   stocks ranks them in the middle.
5. **The candidate buys mostly large stocks, and the larger half adds a
   little return** (decision 57): +0.72 points a year at a standard
   error of 0.61, ahead in 11 of 16 years, with a shallower drawdown
   and fewer losers, on every seed. The filter is proposed to Carter
   (decision 58).
6. **Inside large caps the blend selects best and loses least, for the
   same final value**, because large caps as a group earn less than
   the candidate's peers do.
7. **The forest's taste for utilities and REITs comes from its target,
   not its inputs**; return on capital as a second ranking removes
   them ([features note](notes/2026-09-30-features-and-floor.md)).
8. **Selection is by rank within the period, not by confidence.** An
   honest calibrator runs years behind the regime; every forest's
   score level is highest at market tops (decision 46). The monthly top
   5 earns 1.55 points a year less than the top 10; score weights
   change nothing (decisions 42, 56).
9. **A rank-based sell discipline adds return over 21 years** (TWR
   11.5% against 11.0% on v1.4.1 to 2026, final value 12% higher, ten
   times the costs); it trailed SPY in 2021–26 like the buy-and-hold rule.
10. **Downside is mostly past volatility.** `vol_12m_rank` alone
    predicts a 30% or 50% fall within a year as well as a forest; over
    three years the forest adds 0.03 to 0.04 of PR-AUC. No short leg
    (decision 45).
11. **Judge the picks, not the market** (decision 50). In 2007 and 2008
    the forest's picks fell 0.46 and 0.33 against their peers' 0.57 and
    0.49, and 40% and 15% of them lost money against 60% and 33%.
12. **A screen gain is not a money gain**, three times now (decisions
    51, 77). The worst-rank blend's buys led peers by 0.6 to 1.0 points
    a year more than the candidate's and its portfolio earned 0.6 to
    0.7 points less. The 8-K counts' forest led by 1.1 points a year
    at three seeds and ended with 5% to 9% less money: the lead was
    earned in 2011–2015 when the account was small, and the holdings
    of 2016–2020 did worse. An arm goes from the screen to a backtest,
    never straight into the candidate.
13. **Two builds can share a version label** (decision 54); every
    record carries `dataset_sha256` (decision 55). An additive build
    on the same snapshot gives the same trades: the v1.5.1 control
    reproduces the v1.4.1 candidate to the dollar (decision 77).
14. **Today's list barely depends on the snapshots of 2021–2023**
    (decision 60): a training cutoff of 2021 changes one pick of ten,
    of 2018 two; the backtest's refits for the 2021–23 trades had
    trained on nothing after 2017 and still trailed SPY
    ([training cutoff note](notes/2026-11-25-training-cutoff.md)).
15. **The forest on these columns learns an absolute floor, not a
    comparison with SPY** (decision 75). Cell C and its path-average
    twin are above every bar; the labels defined against SPY's path or
    drawdown are below the size or low-volatility bar on precision and
    behind cell C on losers, as `label_3y_beat_spy` was on earlier
    builds. A peer-relative target is an upstream question.
16. **Top-20 precision does not say what a portfolio of the picks
    does; the model family does** (decision 76). LightGBM of the
    2026-09 size matches the forest's p@20 and PR-AUC in cell C, and
    its screen picks have no lead over their peers and earn less than
    them on the path; XGBoost is below both. The forest stays the only
    leg.
17. **The stock's own history and the wider trend columns buy nothing
    in cell C** (decisions 74, 75): the same lead, two points more
    losers, fewer distinct stocks. The forest at depth 4 with a fifth
    of the columns a split already reads the level ranks they restate.

Earlier notes: [notes/](notes/), linked from the decision log.

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable.
It held out of sample: the candidate bought fewer losers and suffered
shallower falls. What it did not do is earn the index's return in
2021–26, years in which the index beat every size of stock.

**Carter's working assumption (decision 36)** is that 2021–26 is a
bubble led by stocks that fail a value investor's test: a value
strategy trails through it, leads again during and after the
correction, and should be waited out. Conclusion 4 supports it, and so
does the one precedent in the data, 1999–2004, where a stand-in for
the candidate trailed in 1999 and led by 9 points a year for the buys
of 2000–02. The record cannot show whether the buys of 2021–23
recover, and the 1999 run-up was in small stocks where today's excess
is in a few giants inside the index (decision 35).

## Open questions

- Is 2021–26 a bubble, and does the candidate lead again when it
  deflates? Only paper trading and time can answer.
- Can information outside prices and financial statements rank upside?
  Insider and institutional transactions and the state of the market
  are the examples; they would be built upstream. The 8-K counts were
  the first such columns, and the forest used two of fourteen.
- Why do huber regressions on CAGR and on excess CAGR rank so
  differently (decision 45)? Unexplained.
- Why did the 8-K counts' picks do worse in 2016–2020 when they led
  their peers over the whole period? Not pursued; the arm is closed.

## Plan

Decision 36 stands: the bubble reading is the working assumption, the
candidate is paper-traded as it is, and the search continues.

1. **Paper trading** follows [paper-trading.md](paper-trading.md). The
   November 2026 list was produced from the v1.4.1 bundles on
   2026-11-24; the v1.5.1 build gives the same forest, so nothing is
   refit.
2. **Carter's open decisions:** the larger-half filter (decision 58),
   the training cutoff (decision 60), the F50 portfolio (decision 71),
   the price floor (decision 71.3), the Foamex request (decision 73).
3. **Upstream requests:** market-state columns per snapshot date, the
   peer-relative label, the Foamex price check. New columns arrive as
   a dataset version and are run through decision 74's program: the
   control rerun, the screen, three seeds, then money.
4. **Carter's rules** for other model families come next (research
   plan item 7). Boosters are judged on the screen first (conclusion
   16). After them, a logistic regression and an MLP on the ranks are
   the first arms.
5. New arms are judged on walk-forward 2005–2020 against same-size
   peers, in both halves and on three seeds, with the rule written
   before the run (decision 50), and then in money (decision 51). The
   years 2021–26 are context only.
6. **Before any unattended backtest chain on v1.5.1, cut the
   backtest's memory**: a run peaks at 13.8 GB of 14 (decision 77.4).

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
in cell C has no baselines computed on the holdout rows; computing one
would be a second look, and that look is Carter's to take. Process
rules are in CLAUDE.md. Incidents are in
[notes/process-issues.md](notes/process-issues.md).
