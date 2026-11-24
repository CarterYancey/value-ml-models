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
a fold mean over the 16 walk-forward folds with test years 2005 to
2020, as defined in `split_folds.parquet` of the named dataset
version. Each number is the best of the trials counted beside it, so
it is selection-biased. None is a result of record. Numbers from
different dataset versions, or from different universes, are never
compared. **The dataset of record is now `dataset_v1.4.1`** (decision
55). Every v1.4 number in the notes before 2026-11-24 belongs to a
build that no longer exists and is context only.

## Next session: start here

1. The latest session (2026-11-24): [dataset_v1.4.1, the candidate's
   record on it, and the size band in money](notes/2026-11-24-v141-and-size-band.md),
   decisions 55 to 57 of the [decision log](notes/2026-09-29-decisions.md).
   Before it, 2026-11-23: [crash, growth, worst rank, buckets](notes/2026-11-23-crash-growth-worst-rank.md)
   (decisions 38–42), [downside, gates, calibration](notes/2026-11-23-downside-gates-calibration.md)
   with the [calibration plan](notes/2026-11-23-calibration-plan.md)
   (decisions 43–49), and [judging picks](notes/2026-11-23-judging-picks.md)
   (decisions 50–54).
2. What to do next: TODO.md, "Next, after 2026-11-24". The candidate's
   runbook is [paper-trading.md](paper-trading.md).
3. Branches for `Claude`: `claude/results-2026-11-24` carries this
   session's code (`dataset_sha256` in every record), docs, promoted
   results and the ledger shard, on top of `claude/results-2026-11-23`
   (pull request 20, still open). Configs and reports are on the lab
   branch `claude/lab-2026-11-24`, which is not for merging.

## State (2026-11-24)

Carter's goal is a manageable number of high-precision, low-risk
selections with upside. They are judged first on what a portfolio of
the picks went on to do, and second on precision.

**The candidate** (decision 24, unchanged since 2026-09-30) is the
forest trained on cell C, combined by mean rank with 12-month momentum
and return on capital. It buys the top 10 each month, at most 2 per
sector, with equal weights, inside Carter's floor
(`dollar_volume_3m_rank >= 0.2`). The backtest charges 35 bps a side.
It buys and deposits from 2005 to 2026-08-21 and refits the forest at
each year end after 2020. All three legs were refit on `dataset_v1.4.1`
on 2026-11-24, and these are the numbers of record:

| | final value on 260,000 | TWR | MWR | worst drawdown |
|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 10.9% | 13.2% | −52.9% |
| **candidate, buy and hold** | 1,159,740 | 11.0% | 12.2% | −41.0% |
| candidate, rank sell discipline | 1,294,414 | 11.5% | 13.0% | −41.3% |

**The candidate is not shown to beat SPY.** It was ahead of SPY in
money at the end of 2020 (932,471 against 732,110 on the 2005–2020 run,
TWR 11.8% against 9.6%) and is 13% behind in August 2026. Its yearly
return minus SPY's:

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to August |
|---|---|---|---|---|---|
| −8.9 | +2.3 | −3.9 | −11.4 | −14.5 | −13.2 |

The buys of 2021 trailed SPY by 14.6 points a year over three years
and 72% of them lost money, the worst cohort in the record. The buys
of 2022 matched SPY and the buys of 2023 trailed it by 4.3 points.
In all, 45 backtest configurations have completed on 2005–2020 (38 on
v1.4, 7 on v1.4.1), and 4 failed runs of 2026-11-24 count as trials. The runs to 2026 are the fixed candidate, its
sell variant and, as context, the larger-half variant below.

| cell (3-year horizon) | trials | best result | status |
|---|---|---|---|
| C, "not a loser", `dataset_v1.4.1`, all rows | 3 (the candidate's legs) and the seeds of decision 57 | forest on 112 ranks: PR-AUC 0.585, p@20 0.75 against a base rate of 0.39. Blend screen inside the 100k floor: lead over same-size peers +0.030 / +0.053 a year, losers 0.26 / 0.16 against peers' 0.33 / 0.28 | **the candidate's forest** |
| C on `dataset_v1.4` (retired build) | 96 on all rows; 38 inside the 100k floor; 14 inside large caps | p@20 0.79 against 0.39 | **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base rate 0.38 |
| `label_3y_beat_spy` inside large caps (v1.4) | 16 | forest: PR-AUC 0.48 against 0.45; no lead after 2013 | closed: not learnable once size is held fixed |
| `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.3` inside large caps (v1.4) | 10 | p@20 below the base rate | closed |
| "fell 50% from entry", 1y and 3y, liquid half (v1.4) | 8 each | 3y forest PR-AUC 0.49 against 0.31; the 1y forest is below `vol_12m` alone | closed: no short leg, no cash rule (decision 39) |
| regression on 3y CAGR or excess (huber, quantiles), screened in the 100k floor (v1.4) | 8 | huber on CAGR led peers by +0.072 / +0.054 with losers 0.39 / 0.37 | closed as a leg; blends with the forest are below both (decisions 40, 49) |
| `label_3y_cagr_ge_0`, "came back" (v1.4) | 3 seeds | the same picks as cell C in money, drawdown 3 points deeper | an equivalent label, not a replacement (decision 53) |
| the 1-year labels, cells A and B, the whole-path labels, `fwd_3y_cagr >= 0.15` | see the notes | | closed earlier |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on,
   and that is what it is good for.** Carter ran the one holdout look
   in cell C on 2026-10-01 (v1.4, old build). Of the top 20 picks a
   year, 65% met the label; of the top 50, 73%; the base rate was 38%.
   Among the top 20, 28% lost money, against 54% of all rows. See
   decision 29 and the [out-of-sample note](notes/2026-10-01-out-of-sample.md).
2. **Company size decides more than any model, and "beats the average
   stock" is not skill.** Over three years the smaller half of the
   investable stocks trailed SPY by 12 points a year for the 2005–12
   entries, by 18 for 2013–20 and by 33 for 2021–23. The largest 5%
   trailed by 0, 2.5 and 6.5 points. So every selection is read
   against same-size peers: each backtest report has a `vs_peers`
   table and the screen has a `peer_column`.
3. **Against same-size stocks the candidate leads in 2005–2020 and by
   nothing after.** On v1.4.1 the blend's screen picks led their peers
   by 3.0 and 5.3 points a year in the two halves, in 13 of 16 years.
   The backtest's buys of 2021 trailed their peers by 6.4 points; the
   buys of 2022 and 2023 led by 3.5 and 6.0.
4. **In 2021–26 SPY beat equal-weighted portfolios of stocks of every
   size**, including its own thirty largest members. A few very large,
   volatile companies carried the index, and a model that favours calm
   stocks ranks them in the middle. No equal-weighted selection from
   this universe kept up. This is condition (2) of the thesis.
5. **The candidate already buys mostly large stocks, and restricting it
   to the larger half adds a little money** (decision 57, v1.4.1,
   2005–2020). The candidate's peers earn what the larger half's peers
   earn. With `log_marketcap_rank >= 0.5` added to the rule the
   portfolio earned 0.72 points a year more (se 0.61, ahead in 11 of
   16 years), with a shallower drawdown and 0.9 points fewer losers.
   On seeds 232 and 1776 the gap held (+0.70 and +0.32 points of TWR,
   MWR and final value above, drawdown shallower on every seed): the
   rule written before the run is met, and the filter is **proposed to
   Carter** as a change to the candidate (decision 58). The gain is
   the band, not the selection: the picks lead their peers by the same
   amount with or without the filter.
6. **Inside large caps the blend selects best and loses least, for the
   same money.** With `log_marketcap_rank >= 0.8` the buys led
   same-size peers by 1.9 and 3.1 points a year and 4 points fewer of
   them lost money (both beyond two standard errors), and the
   portfolio earned the same as the candidate's because the band earns
   less. Decision 34, which found the forest alone separates only the
   worst quintile of large caps, measured the forest without the two
   factors.
7. **The forest's taste for utilities and REITs comes from its target,
   not its inputs.** Given `sector` as an input it picks the same
   utilities and REITs at the same precision. Adding return on capital
   as a second ranking is what removes them
   ([features note](notes/2026-09-30-features-and-floor.md)).
8. **Selection is by rank within the period, not by confidence.** An
   honest calibrator may only use outcomes that were observable at
   the time, so it runs years behind the regime. Every forest's score
   level is highest at market tops, and adding raw level columns makes
   that worse (decision 46). A shorter horizon, theory-led features,
   a training-time floor, label thresholds, forest parameters and the
   seed moved the result little. The forest's confidence counts only
   at the very top: the monthly top 5 earns 1.55 points a year less
   than the top 10 and score weights change nothing (decisions 42,
   56).
9. **A rank-based sell discipline adds money over 21 years** (11.5%
   against 11.0% TWR to 2026 on v1.4.1, final value 12% higher) with
   the same drawdown and ten times the costs. In 2021–26 it trailed
   SPY in every year but 2022, like the buy-and-hold rule.
10. **Downside is mostly past volatility.** `vol_12m_rank` alone
    predicts a 30% or 50% fall within a year as well as a forest; over
    three years the forest adds 0.03 to 0.04 of PR-AUC. A short leg is
    not justified (decision 45).
11. **Judge the picks, not the market** (decision 50, Carter). In
    2007–08 the forest's picks fell 0.46 and 0.33 against their peers'
    0.57 and 0.49, and lost money 0.40 and 0.15 of the time against
    0.60 and 0.33. Cell C's low precision in those years is its
    drawdown leg failing on the market's fall, not the selection.
12. **A screen gain is not a money gain.** The worst-rank blend's buys
    led peers by 0.6 to 1.0 points a year more on three seeds, and its
    portfolio earned 0.6 to 0.7 less (decision 51). An arm goes from
    the screen to a backtest, never straight into the candidate.
13. **Two builds can share a version label.** v1.4 was rebuilt on
    2026-11-23 and the ledger could not tell (decision 54). Upstream
    now versions patches and writes a provenance block; every record
    here carries `dataset_sha256` (decision 55).

Earlier notes: [notes/](notes/), linked from the decision log.

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable,
and it held out of sample: the candidate bought fewer losers and
suffered shallower falls. What it did not do is earn the index's
return in 2021–26, years in which the index beat every size of stock.

**Carter's working assumption (decision 36)** is that 2021–26 is a
bubble led by stocks that fail a value investor's test. On that
reading a value strategy trails through the bubble, leads again during
and after the correction, and should be waited out. Evidence for it:
conclusion 4, and the one precedent in the data: on 1999–2004, years
no model here was chosen on, a stand-in for the candidate trailed in
1999 and then led for the buys of 2000–02 by 9 points a year, against
SPY and same-size peers alike. What the record cannot show: the years
in which that earlier bubble grew are before the data; the candidate's
same-size lead had already gone for the buys of 2019–20; the 1999
run-up was in small stocks, whereas today's excess is in a few giants
inside the index; and nobody yet knows whether the buys of 2021–23
recover. See decision 35.

## Open questions

- Is 2021–26 a bubble, and does the candidate lead again when it
  deflates? Carter's working assumption is that it is one, and that a
  value strategy trails through it and leads again during and after
  the correction. Only paper trading and time can answer.
- Can information outside prices and financial statements rank upside:
  insider and institutional transactions, the state of the market?
  Those features would have to be built upstream.
- Why do huber regressions on CAGR and on excess CAGR rank so
  differently? Three seeds agree it is not the seed (decision 45); the
  cause is unexplained.

## Plan

Decision 36 stands: the bubble reading is the working assumption, the
candidate is paper-traded as it is, and the search continues. Carter's
three directions of 2026-11-23 (decision 43) were followed to the end
of what the data on disk can answer. What is left:

1. **Paper trading** ([paper-trading.md](paper-trading.md)). The
   November 2026 list was produced from the v1.4.1 deployment bundles
   on 2026-11-24; Carter decides what is bought.
2. **The larger-half filter** (decision 57): Carter confirms or declines
   `log_marketcap_rank >= 0.5` as one more investability filter. If
   confirmed, the sell-discipline variant is backtested with it and the
   runbook's `vml-predict` gains a second `--filter`.
3. **Upstream** (calibration plan, "Upstream request"): market-state
   columns per snapshot date, which a threshold rule needs, and the
   peer-relative label.
4. **Carter's rules** for other model families (research plan item 7),
   then a logistic regression and an MLP on the ranks.
5. New arms are judged on walk-forward 2005–2020 against same-size
   peers, in both halves, on three seeds, with the rule written before
   the run, and carried forward on paired per-year gains beyond noise
   (decision 50). The years 2021–26 are context only.

## Sealed holdout record

`reports/final_evals.csv` records 20 looks at the sealed holdout. The
look count is part of every holdout number: a cell looked at twice is
no longer a clean test. Each row gives PR-AUC against the base rate,
with the holdout test year in brackets. No look has been taken on
`dataset_v1.4.1`.

| cell | looks | what the looks showed |
|---|---|---|
| **3y C, "not a loser" (v1.4 [2021–23], old build)** | **1** | **p@20 0.65, top 50 0.73, base rate 0.38; PR-AUC 0.56; picks −0.09 a year against SPY, all rows −0.25** |
| 1y, 2y, 5y cells on v1.0 and v1.1 | 1 to 5 each | cagr_ge_0: PR-AUC 0.59–0.68 against about 0.5; beat_spy: none to barely any skill. See `reports/final_evals.csv` |

A look inside a universe uses up the whole label's cell. The one look
in cell C has no baselines computed on the holdout rows. Computing one
would be a second look, and that look is Carter's to take. Process
rules are in CLAUDE.md. Incidents are in
[notes/process-issues.md](notes/process-issues.md).
