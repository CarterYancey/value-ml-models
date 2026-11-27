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

1. The latest session (2026-11-26 into 2026-11-27) wrote
   [the rare-region program](notes/2026-11-26-rare-region.md), decisions
   78 to 80 of [the decision log](notes/2026-11-26-decisions.md): Carter's
   run-up labels, fundamentals-leaning feature sets and five ways of
   making a model attend to fallen stocks with a strong record. Nothing
   passes the screen rule. Earlier the same day
   [the v1.5.1 program](notes/2026-11-26-v151-program.md) (decisions 74
   to 77) found that the new columns, labels and boosters add nothing to
   the candidate; 2026-11-25 wrote
   [the fallen-stock program](notes/2026-11-25-fallen-stocks.md)
   (decisions 61 to 72) and
   [the training cutoff](notes/2026-11-25-training-cutoff.md) (60).
2. TODO.md says what to do next, under "Next, after 2026-11-27". The
   candidate's runbook is [paper-trading.md](paper-trading.md).
3. The branch `claude/results-2026-11-26` carries this file, the
   v1.5.1 support code, the `[emphasis]` and `[pick_screen] region`
   code, decisions 74 to 80 and the promoted records. The configs and
   reports are on the lab branch `claude/lab-2026-11-26`, archived as
   a tag once the results branch merges.

## State (2026-11-27)

Carter's goal is a manageable number of high-precision, low-risk
selections with upside. They are judged first on what a portfolio of
the picks went on to do, and second on precision.

**The candidate** (decision 24, unchanged since 2026-09-30) is the
forest trained on cell C ("not a loser": a 3-year CAGR of zero or more
and never 30% down), combined by mean rank with 12-month momentum and
return on capital. It buys the top 10 each month, at most 2 per sector,
with equal weights, inside Carter's floor
(`dollar_volume_3m_rank >= 0.2`). The backtest takes 35 bps a side as
costs, buys and deposits from 2005 to 2026-08-21 and refits the forest
at each year end after 2020. All three legs were refit on
`dataset_v1.4.1` on 2026-11-24; these are the numbers of record:

| | final value on 260,000 | CAGR | TWR | worst drawdown |
|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 13.2% | 10.9% | −52.9% |
| **candidate, buy and hold** | 1,159,740 | 12.2% | 11.0% | −41.0% |
| candidate, rank sell discipline | 1,294,414 | 13.0% | 11.5% | −41.3% |

The CAGR is the money-weighted growth rate of the deposits into the
final value, the metric of record since decision 72.

**The screen rule** (decision 74.4): an arm is judged on its picks'
lead over same-size peers on the 3-year CAGR and on its share of
losers, paired by test year with the control, in both halves of
2005–2020. The control is the candidate's forest in cell C on the 112
old ranks inside the 100k floor: p@20 0.75, lead +0.029 a year, losers
0.17 against its peers' 0.30. A gain must be positive at about two
standard errors, ahead in 10 or more of 16 years, with no half worse
than its noise, on both outcomes; then three seeds, then money.

**The rare-region program is closed (decisions 78 to 80).** Carter
asked whether a model can learn the rare case: a strong record, a steep
fall, a recovery. The region (liquid, 40% or more below the 5-year high,
cash-flow positive in 18 of 20 quarters; 16% of liquid rows) earns a
mean 3-year CAGR of 1.9% against 3.4% for all liquid rows, with 41%
losers against 37% and 18.5% doublers against 15.9%; it earns in
2009–2012 and 2020 and loses every year from 2013 to 2018. Across 49
runs (training weights ×3 and ×10 inside it, the region as a universe,
forests seeing 5% of the columns a split, LightGBM at a tenth of the
columns, quantile regression for the upper tail) no arm passes the
screen rule. The picks' share inside the region and their share of
losers rise together in every sweep, from 0.6% and 17% (the control) to
47–86% and 44–61%; given the region's columns and more of its weight,
the forest learns to avoid it. Of Carter's labels, 'doubled without a
crash' on the old ranks is a one-month-reversal forest (+0.081 a year
over the control, 38% losers, peers losing money half the years after
2008); 'run-up of 75%' is learned as volatility. Of the sets, the ranks
without the technical family plus the unranked history columns (162)
match the control's lead at 5.6 points more losers; the compact
own-history sets are worst everywhere.

**`dataset_v1.5.1` adds nothing to the candidate (decisions 74 to
77).** Every set with the new history, trend or event columns has the
control's lead and about two points more losers. The one gain beyond
noise, the 8-K counts (+0.011 a year at three seeds), ended with 5.1%
less money alone and 8.6% less in the blend. The path-average twin of
cell C picks the same stocks; every label defined against SPY's path or
drawdown is behind cell C on losers. LightGBM at the 2026-09 size
reaches the forest's p@20 with no lead over peers. The blend on v1.5.1
ends 2005–2020 with exactly the v1.4.1 final value, so the legs are not
refit.

**The fallen-stock program is closed (decisions 61 to 73).** No tree
model learns the recovery label in any universe. The "not a loser"
forest inside F50 (50% or more below the 5-year high) finds the fallen
stocks that do not fall further; its portfolio ends 2020 with 2.5% to
4.9% more money than SPY at three seeds and below SPY at two seeds of
three when valued at the end of 2023. Whether it runs beside the
candidate is Carter's decision.

**The candidate is not shown to beat SPY.** At the end of 2020 it was
ahead by final value and TWR; in August 2026 it is 13% behind, trailing
SPY in every year since 2021 but 2022 (by 3.9 to 14.5 points). The buys
of 2021 trailed SPY by 14.6 points a year over three years and 72% of
them lost money. In all, 49 backtest configurations have completed on
2005–2020 (38 on v1.4, 7 on v1.4.1, 4 on v1.5.1), plus seven failed
runs of 2026-11-24.

| cell (3-year horizon, `dataset_v1.5.1` inside the 100k floor unless said) | trials | best result | status |
|---|---|---|---|
| C, "not a loser" | 62 | the control: p@20 0.75, lead +0.029, losers 0.17. No arm ahead on both outcomes | **closed: the candidate's forest stands** |
| 'doubled without a crash' (run-up ≥100%, never 40% down) | 22 | old ranks: lead +0.110, losers 0.38; a reversal forest in a losing neighbourhood | closed: not a leg |
| 'a real gain without a crash'; run-up ≥75%; CAGR ≥20% or a drawdown no deeper than SPY's; the five full-path cells | 5 to 18 each | lead at most the control's; volatility; a calmer, poorer cell C; cell C's twin | closed |
| C inside the rare region (folds 2008–20); 'earned 20% a year' by quantile regression | 3; 6 | lead over in-region peers +0.040, losers 0.33; lead ≤ +0.025, losers 0.48–0.61 | closed |
| C, 5-year horizon (folds 2007–18) | 12 | old ranks: lead +0.032, losers 0.09; the 3-year ordering repeats | closed |
| C, `dataset_v1.4.1`, all rows | 3 legs and the seeds of decision 57 | PR-AUC 0.585, p@20 0.75 against 0.39 | **the candidate's forest** |
| C on `dataset_v1.4` (retired build) | 96; 38 in the floor; 14 in large caps | p@20 0.79 against 0.39 | **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base 0.38 |
| `label_3y_beat_spy`; excess ≥0 & dd<0.3; "fell 50%"; regressions on CAGR; `cagr_ge_0`; the 1-year labels; the recovery label (v1.4) | see the notes | no lead after 2013; no short leg (39); closed as a leg (40, 49); an equivalent label (53) | closed |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on.**
   Carter's one holdout look in cell C (2026-10-01, the old v1.4
   build): of the top 20 a year 65% met the label, of the top 50 73%,
   against a base rate of 38%; 28% of the top 20 lost money against 54%
   of all rows ([out-of-sample note](notes/2026-10-01-out-of-sample.md)).
2. **Company size decides more than any model, so every selection is
   read against same-size peers.** Over three years the smaller half of
   investable stocks trailed SPY by 12 to 33 points a year, the largest
   5% by 0 to 6.5. Against same-size stocks the candidate's picks led in
   13 of 16 years of 2005–2020 (3.0 points a year in the first half,
   5.3 in the second); the buys of 2021 trailed their peers by 6.4
   points, of 2022 led by 3.5 and of 2023 by 6.0. In 2021–26 SPY beat
   equal-weighted portfolios of stocks of every size.
3. **The larger half adds a little** (decision 57): +0.72 points a year
   at a standard error of 0.61, ahead in 11 of 16 years, on every seed.
   Proposed to Carter (decision 58).
4. **Selection is by rank within the period, not by confidence** (every
   forest's score level is highest at market tops, decision 46); a
   rank-based sell discipline adds 12% of final value over 21 years;
   return on capital as a second ranking removes the forest's utilities
   and REITs.
5. **Downside is mostly past volatility**: `vol_12m_rank` alone predicts
   a 30% or 50% fall within a year as well as a forest; no short leg
   (decision 45). The picks are judged against their peers, not the
   market (decision 50): in 2007 and 2008 the forest's picks fell 0.46
   and 0.33 against their peers' 0.57 and 0.49.
6. **A screen gain is not a money gain**, three times now (decisions 51,
   77): the 8-K counts' forest led by 1.1 points a year at three seeds
   and ended with 5% to 9% less money. An arm goes from the screen to a
   backtest, never straight into the candidate.
7. **Two builds can share a version label** (decision 54); every record
   carries `dataset_sha256`; the v1.5.1 control reproduces the v1.4.1
   candidate to the dollar (decision 77). Today's list barely depends on
   the snapshots of 2021–2023 (decision 60).
8. **The forest learns an absolute floor, not a comparison with SPY**
   (decision 75); a peer-relative target is an upstream question.
9. **Top-20 precision does not say what a portfolio does; the model
   family does** (decision 76). LightGBM matches the forest's p@20 and
   its picks have no lead over their peers.
10. **The stock's own history buys nothing in cell C** (decisions 74,
    78): the history and trend ranks, the raw fundamentals and the
    compact own-history sets give the control's lead or less with 2 to 7
    points more losers. The volatility ranks hold the losers down;
    removing them costs losers, not lead.
11. **The rare region of fallen stocks with a strong record is the
    market's recovery, not mispriced survivors** (decisions 79, 80). Its
    rows have wider tails and a lower mean than the market, win after
    crashes and lose through the long rise. Every selection that buys it
    loses more often; every selection that leads avoids it. Given the
    region's columns and ten times its weight, the forest reads its
    lower label rate correctly and says no. Inside the region, as inside
    F50 (decision 63), the forest finds the stocks that fall least, not
    the ones that recover.
12. **The own-history valuation columns are real and are not a
    selection** (decision 80.5). Where the price columns are absent or
    the question is the upper tail, `sales_yield_vs_5y_median_rank`,
    `tangible_book_to_market_vs_5y_median_rank`,
    `earnings_yield_5y_peak_rank` and `book_to_market_5y_pctile` are the
    top splits, and the arm has at best the control's lead with more
    losers.
13. **Emphasis weights, subspace forests and column sub-sampling do not
    change what a forest buys** (decision 80.4): 16 of 18 emphasized
    arms and every subspace arm sit within two standard errors of their
    twins; the same columns lead at a third of the weight.

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable. It
held out of sample: the candidate bought fewer losers and suffered
shallower falls. What it did not do is earn the index's return in
2021–26, years in which the index beat every size of stock.

**Carter's working assumption (decision 36)** is that 2021–26 is a
bubble led by stocks that fail a value investor's test: a value
strategy trails through it, leads again during and after the
correction, and should be waited out. Conclusion 2 supports it, and so
does the one precedent in the data, 1999–2004. The record cannot show
whether the buys of 2021–23 recover.

## Open questions

- Is 2021–26 a bubble, and does the candidate lead again when it
  deflates? Only paper trading and time can answer.
- What separates the rare region's good years (2009–2012, 2020) from
  its bad ones (2013–2018)? Nothing in the row: the market's state at
  the snapshot date, which is an upstream column.
- Can information outside prices and financial statements rank upside?
  Insider and institutional transactions and the state of the market
  are the examples; they would be built upstream.
- Why do huber regressions on CAGR and on excess CAGR rank so
  differently (decision 45)? Unexplained.

## Plan

Decision 36 stands: the bubble reading is the working assumption, the
candidate is paper-traded as it is, and the search continues.

1. **Paper trading** follows [paper-trading.md](paper-trading.md). The
   November 2026 list came from the v1.4.1 bundles on 2026-11-24; the
   v1.5.1 build gives the same forest, so nothing is refit.
2. **Carter's open decisions:** the larger-half filter (58), the
   training cutoff (60), the F50 portfolio (71), the price floor (71.3),
   the Foamex request (73).
3. **Upstream requests:** market-state columns per snapshot date (now
   also the rare region's open question), the peer-relative label, a
   recovery label measured inside a region, the Foamex price check. New
   columns arrive as a dataset version and run through decision 74's
   program: the control rerun, the screen, three seeds, then money.
4. **Carter's rules** for other model families come next (research plan
   item 7): a logistic regression and an MLP on the ranks, judged on the
   screen first (conclusion 9).
5. New arms are judged on walk-forward 2005–2020 against same-size
   peers, in both halves and on three seeds, with the rule written
   before the run (decision 50), and then in money (decision 51). The
   years 2021–26 are context only.
6. **Before any unattended backtest chain on v1.5.1, cut the backtest's
   memory**: a run peaks at 13.8 GB of 14 (decision 77.4).

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
