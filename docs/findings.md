# Findings

What is known now, by cell, and what is planned. Kept short on purpose:
**this file is rewritten, not appended to**, and stays under about 150
lines.

- What was done, in order: [logbook.md](logbook.md). Read that first.
- Tables, checks and reasoning: the note a conclusion links to, in
  [notes/](notes/). Unattended sessions: [agents.md](agents.md).

Numbers are walk-forward fold means over test years 2005–2020 (16
folds, `split_folds.parquet` of the named dataset version),
**selection-biased** by the trial counts given; none is a result of
record. Never compared across dataset versions or universes.

## Next session: start here

1. The latest session (2026-11-23), two rounds:
   [crash, growth, worst rank, buckets](notes/2026-11-23-crash-growth-worst-rank.md)
   (decisions 38–42), then Carter's three directions:
   [downside, gates, calibration](notes/2026-11-23-downside-gates-calibration.md)
   and the [calibration plan](notes/2026-11-23-calibration-plan.md)
   (decisions 43–49 of the [decision log](notes/2026-09-29-decisions.md)). Before
   it: [out of sample](notes/2026-10-01-out-of-sample.md),
   [large caps](notes/2026-10-01-large-caps.md), decisions 27–37.
2. What to do next: TODO.md, "Next, after 2026-11-23", and
   [the research plan](notes/2026-10-01-research-plan.md). The
   candidate's runbook: [paper-trading.md](paper-trading.md).
3. For `Claude`: `claude/results-2026-11-23` (code: `worst_rank`,
   `year_balance` and the year-calibration measures, `[[gate]]`; docs;
   the ledger shard). Configs and reports: the lab branch
   `claude/lab-2026-11-23` (not for merging).

## State (2026-11-23; the candidate unchanged since 2026-10-01)

The goal (Carter): a manageable number of high-precision, low-risk
selections with upside, judged on what a portfolio of the picks went
on to do, then on precision.

**The candidate** (decision 24, unchanged): cell C's forest, 12-month
momentum and return on capital by mean rank; top 10 a month, at most
2 per sector, equal weights, `dollar_volume_3m_rank >= 0.2` (Carter's
floor). Simulated, 35 bps a side, buys and deposits 2005 to
2026-08-21, the forest refit each year end after 2020:

| | final value on 260,000 | time-weighted | worst drawdown | 2005–2020 | 2021–2026 |
|---|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 10.9% | −52.9% | 9.4% a year | 15.4% a year |
| **candidate, buy and hold** | 1,193,902 | 11.3% | −41.4% | 12.7% | 7.3% |
| candidate, rank sell discipline | 1,344,630 | 12.0% | −39.6% | 13.6% | 7.6% |

**It is not shown to beat SPY**: 37% ahead in money at the end of 2020,
10% behind in August 2026; its buys of 2021–23 trailed SPY by 11 to
17 points a year over three years. 37 backtest configurations on
2005–2020; the four to 2026 are the fixed candidate and a variant.

| cell (3y, `dataset_v1.4`) | trials | best | status |
|---|---|---|---|
| C, "not a loser": `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3` | 96 on all rows; 38 inside the 100k floor; 14 inside large caps | forest on 112 ranks: p@20 0.79 (base 0.39); against same-size peers a lead of +0.03 a year, losers 0.20 / 0.12 against 0.33 / 0.26 | **the candidate's forest**; **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base 0.38 |
| `label_3y_beat_spy` inside large caps | 16 | forest: PR-AUC 0.48 (base 0.45); no lead after 2013 | closed: not learnable with size held fixed |
| `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.3` inside large caps | 10 | p@20 below the base rate | closed |
| "fell 50% from entry", 1y / 3y, liquid half | 8 each | 3y forest PR-AUC 0.49 (base 0.31); 1y forest 0.25, below `vol_12m` alone (0.27) | closed: no short leg, no cash rule (decision 39) |
| regression on 3y CAGR / excess (huber, quantiles), screened in cell C's floor | 8 | huber on CAGR +0.072 / +0.054 over peers, losers 0.39 / 0.37 | closed as a leg; blends with the forest below both (decision 40) |
| 1y, A, B, whole path, `fwd_3y_cagr >= 0.15` | see notes | | closed earlier |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was not chosen on.**
   Holdout (look 1 of 1): top 20 a year right 0.65 of the time, top 50
   0.73, base 0.38; 28% of the top 20 lost money against 54% of all
   rows, and 22% of its 2021–23 picks against 34% of same-size stocks.
2. **Size decides more than any model.** The smaller half of the
   investable stocks trailed SPY by 12, 18 and 33 points a year (3y)
   in 2005–12, 2013–20, 2021–23; the largest 5% by 0, 2.5, 6.5.
   **Read a selection against same-size peers** (`vs_peers`,
   `peer_column`).
3. **Against same-size stocks the candidate led by 5 to 6 points a
   year in 2005–2020 and by nothing after** (buys: +0.046 / +0.059,
   then −0.016 for 2021–23; the forest alone +0.023 / +0.027 / +0.006).
4. **In 2021–26 SPY outran equal-weighted stocks of every size**, its
   thirty largest members included: a few very large, volatile
   companies a model of calm ranks in the middle.
5. **Among large companies the features rank risk and one quality
   factor**: forests lead same-size peers by 2 points a year, return
   on capital alone by 3 to 4; "beat SPY" is not learned. Large-caps note.
6. **The forest's sector habit (utilities, REITs) is in its target,
   not its inputs**; return on capital as a second ranking removes it
   ([features](notes/2026-09-30-features-and-floor.md)).
7. **Horizon, theory-led features (Piotroski too), a training-time
   floor, label thresholds, forest parameters and the seed move
   little**; an honest calibrator is years behind the regime
   ([blends](notes/2026-09-30-blends-and-calibration.md),
   [searches](notes/2026-09-29-searches-nonloser.md)).
8. **A rank sell discipline added 0.7 points a year over 21 years**,
   nothing in 2021–26. Instruments: [process issues](notes/process-issues.md).
9. **A regression on 3y CAGR selects best within a size band, but only
   among small stocks** (decisions 39–49). Its backtested buys led
   same-size candidates by 6.5–6.8 points a year (the forest 2.7–3.3),
   yet the portfolio ended behind SPY (TWR 9.4%, drawdown −61%): its
   band trails SPY by 9–12 points a year. Among the larger half it has
   no edge (−0.01 / +0.01); gates by the forest or downside models
   keep its lead and remove few losers; blends with the forest are
   below both. Closed as a candidate.
10. **The forest's confidence counts only at the very top**: its top
    10 a year beat ranks 11–50 (precision +0.06, losers 0.14 / 0.08
    against 0.23 / 0.15), flat below rank 20; but a monthly top 5
    trailed the top 10 (+1.8 / +2.7 against +2.7 / +3.3 points a year
    over same-size peers, drawdown 9 points deeper) and score weights
    changed nothing. Confidence sizing is closed for the forest.
11. **Downside is mostly past volatility**: `vol_12m_rank` alone predicts
    a 30% or 50% fall within a year as well as a forest (PR-AUC 0.54 /
    0.36); over three years the forest adds 0.03–0.04. A short leg is
    not justified (the top calls' winners).
12. **No model here can be calibrated across years** (decisions 44–46):
    every forest's score level is highest at market tops (2007–08) and
    its top confidence is negatively correlated with the year's base
    rate (−0.5 to −0.7); per-stock level columns make it worse (calm
    before a crash); `year_balance` removes the stale prior but not the
    problem. "Buy every stock over X" would buy most at a top. The
    market's level must come from upstream market-state columns.

Earlier work: [backtests to 2023](notes/2026-09-30-backtests.md),
[pick anatomy](notes/2026-09-29-pick-anatomy.md),
[label rungs](notes/2026-09-29-label-rungs-dd-entry.md),
[compounder cells](notes/2026-09-28-drawdown-compounder-cells.md),
[v1.0/v1.1](notes/2026-08-earlier-work.md).

## The thesis, and the working assumption

A high precision on a modest target is achievable and held out of
sample. It bought fewer losers and shallower falls; it did not buy the
index's return in 2021–26, when the index earned more than every size
of stock.

**Carter's working assumption (decision 36):** 2021–26 is a bubble a
value strategy trails through and is waited out. *For it:* item 4,
and on 1999–2004 a stand-in for the candidate trailed in 1999 and led
for the buys of 2000–02 by 9 points a year. *Against, or unknown:*
the candidate's same-size lead had gone for the buys of 2019–20; the
1999 excess was in small stocks, today's is in a few giants.
Decision 35; [out of sample](notes/2026-10-01-out-of-sample.md).

## Open questions

- Whether the lead returns when the index's giants stop leading
  (Carter's reading): paper trading and time.
- Whether data outside prices and statements ranks upside. Upstream.
- Why huber on CAGR and on excess CAGR rank so differently (one seed
  each; three seeds would test chance).

## Plan

Carter's direction (2026-10-01, decision 36) stands: the bubble
reading is the working assumption, the candidate is paper traded as
it is, and the search widens. After 2026-11-23 the research plan's
items 1, 2, 3 and the first step of 6 are done (no arm carried
forward). What is left needs Carter or upstream:

1. Paper trading: [paper-trading.md](paper-trading.md).
2. **Upstream (written in the calibration plan):** market-state
   columns per date (cross-sectional medians of valuation and
   volatility, breadth, SPY's trailing return and drawdown, spreads),
   which the threshold rule needs; and the peer-relative label ("beat same-size stocks over
   3 years"), the one target whose base rate does not move with the
   market; it reopens calibration and sizing (item 6). Then
   market-state features (item 8).
3. **Carter's rules** for other model families (item 7): fold-internal
   imputation with an is-missing indicator; learned transforms inside
   the fold only; PyTorch or not. Then a logistic regression and an
   MLP on the ranks.
4. New arms are judged on walk-forward 2005–2020 against same-size
   peers, both halves, the rule written before the run; 2021–26 is
   context. 37 backtest configurations have been tried on 2005–2020;
   model trial counts per cell: `vml-experiments list`.

## Sealed holdout record

From `reports/final_evals.csv` (20 looks; the counts are part of every
holdout number). PR-AUC against the base rate, holdout test year in
brackets:

| cell | looks | what the looks showed |
|---|---|---|
| **3y C, "not a loser" (v1.4 [2021–23])** | **1** | **p@20 0.65, top 50 0.73 vs base 0.38; PR-AUC 0.56; picks −0.09 a year against SPY (all rows −0.25)** |
| 1y, 2y, 5y cells on v1.0 / v1.1 | 1–5 each | cagr_ge_0: PR-AUC 0.59–0.68 vs ~0.5; beat_spy: none to barely any; see `reports/final_evals.csv` |

A look inside a universe consumes the label's cell. The look in cell
C has no baselines on the holdout rows (a baseline there is a further
read, and Carter's). Process rules: CLAUDE.md; incidents:
[notes/process-issues.md](notes/process-issues.md).
