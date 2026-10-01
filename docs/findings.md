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

1. What happened to the candidate after 2023, and why:
   [out of sample](notes/2026-10-01-out-of-sample.md). What was tried
   next: [large caps](notes/2026-10-01-large-caps.md). How:
   [decisions](notes/2026-09-29-decisions.md) 27–34.
2. What to do next: TODO.md, "Next, from the second session of
   2026-10-01". The first items are Carter's.
3. One branch carries everything for `Claude`:
   `claude/results-2026-10-01b` (five code changes, docs, promoted
   results, the ledger shard). Every config and report is on the lab
   branch `claude/lab-2026-10-01` (not for merging).

## State (2026-10-01)

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

**It is not shown to beat SPY.** Buy and hold was 37% ahead in money
at the end of 2020 and is 10% behind in August 2026: −8.6 / +3.2 /
−2.9 / −12.5 / −14.4 / −12.7 points against SPY in the calendar years
2021 to 2026. Its buys of 2021–23 trailed SPY by 11 to 17 points a
year over three years and 32% to 41% lost money (2005–2020: +2.5,
20%). 35 backtest configurations; the four to 2026 are the fixed
candidate and its variant, not a selection.

| cell (3y, `dataset_v1.4`) | trials | best | status |
|---|---|---|---|
| C, "not a loser": `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3` | 87 on all rows; 38 inside the 100k floor; 14 inside large caps | forest on 112 ranks: p@20 0.79 (base 0.39); against same-size peers a lead of +0.03 a year, losers 0.20 / 0.12 against 0.33 / 0.26 | **the candidate's forest**; **holdout look 1 of 1**: p@20 0.65, top 50 0.73, base 0.38 |
| `label_3y_beat_spy` inside large caps | 16 | forest: PR-AUC 0.48 (base 0.45); no lead after 2013 | closed: not learnable with size held fixed |
| `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.3` inside large caps | 10 | p@20 below the base rate | closed |
| 1y, A, B, whole path, `fwd_3y_cagr >= 0.15` | see notes | | closed earlier |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was not chosen on,
   and that is what it is good for.** Holdout (Carter, 2026-10-01,
   look 1 of 1): top 20 a year right 0.65 of the time, top 50 0.73,
   base rate 0.38; 28% of the top 20 lost money against 54% of all
   rows. Net of size too: 22% of its 2021–23 picks lost money against
   34% of same-size stocks. Decision 29; out-of-sample note.
2. **Size decides more than any model, and "beats the average stock"
   is not skill.** The smaller half of the investable stocks trailed
   SPY by 12, 18 and 33 points a year over three years in 2005–12,
   2013–20 and 2021–23; the largest 5% by 0, 2.5 and 6.5. More than
   half of every lead over "all rows" in the earlier notes was the
   picks being large. **Read a selection against same-size peers**:
   `vs_peers` in every backtest report, `peer_column` on the screen.
3. **Against same-size stocks the candidate led by 5 to 6 points a
   year in 2005–2020 and by nothing after.** Its buys' lead over
   same-month, same-size candidates: +0.046 / +0.059 for 2005–12 /
   2013–20, −0.016 for 2021–23 (the forest alone +0.023 / +0.027 /
   +0.006). What momentum and return on capital added to the forest
   reversed; the lead was already zero for the buys of 2019 and 2020.
4. **In 2021–26 SPY outran equal-weighted stocks of every size**, its
   own thirty largest members included (−3.3 points a year): the
   index was carried by a few very large, volatile companies, which a
   model of calm ranks in the middle (NVDA 1,300th to 1,600th of 3,100
   to 3,700 on the forest in the Januaries of 2023–25). No equal-weighted selection from
   this universe kept up. Condition (2) of the thesis, the era.
5. **Among large companies the features rank risk and one quality
   factor, and nothing else.** Inside the largest fifth, forests on
   "not a loser" lead same-size peers by 2 points a year; return on
   capital alone by 3 to 4, the conservative score alone by 3; "beat
   SPY", as a label or as a regression, is not learned (no lead after
   2013). The forest separates the worst quintile and nothing above
   it. Large-caps note.
6. **The forest's sector habit is in its target, not its inputs.**
   With `sector` as an input it picks the same utilities and REITs
   (34% of picks) at the same precision; without the volatility ranks
   it finds them through cash-flow stability
   ([features](notes/2026-09-30-features-and-floor.md)). Return on
   capital as a second ranking is what removes them.
7. **Selection is by rank within the period, not by confidence**; a
   shorter horizon does not help; theory-led features, a
   training-time floor, label thresholds, forest parameters and the
   seed move little.
   [blends](notes/2026-09-30-blends-and-calibration.md),
   [1y](notes/2026-09-30-one-year-cell.md),
   [searches](notes/2026-09-29-searches-nonloser.md)
8. **A rank sell discipline added 0.7 points a year over 21 years**
   and nothing in 2021–26 (−46 against −48 points of yearly excess);
   it is why that variant ends level with SPY.
9. **The dataset's delisting convention understates acquired
   stocks**; the backtest's per-buy reading does not (proceeds ride
   SPY). Upstream request in TODO.
10. **Three things about the instruments** (process issues,
    2026-10-01): backtest reports before today print years that run
    December to December; every backtest before today stopped its
    valuation at 2023-12-29 with data to 2026-08-21 on disk; whole
    shares at 100 a pick fill 64 to 87 of 120 orders a year after
    2020 (it does not change the result).

Earlier work: [backtests to 2023](notes/2026-09-30-backtests.md),
[pick anatomy](notes/2026-09-29-pick-anatomy.md),
[label rungs](notes/2026-09-29-label-rungs-dd-entry.md),
[compounder cells](notes/2026-09-28-drawdown-compounder-cells.md),
[v1.0/v1.1](notes/2026-08-earlier-work.md).

## What this says about the thesis

A high precision on a modest target is achievable and held out of
sample. It bought fewer losers and shallower falls: over 21.6 years
the index's return with three quarters of its worst drawdown. It did
not buy the index's return in 2021–26, because picks chosen for not
losing earn about what calm stocks of their size earn, and the index
earned more than every size of stock. Beating SPY needs either the
upside (which these columns do not rank) or an era in which the
largest companies do not lead (2005–2020 was one).

## Open questions

- What the portfolio is for and what it is measured against (SPY, or
  stocks of the picks' own size). Carter's; it decides whether the
  candidate is a result.
- Whether the 2 to 5 points over same-size stocks of 2005–2018 come
  back. Only paper trading can say; nothing on disk can.
- Whether information outside prices and statements ranks upside
  (insider and institutional transactions, market state). Upstream.

## Plan

1. Carter's: the pull request from `claude/results-2026-10-01b`; the
   yardstick; whether to paper-trade the fixed candidate (both forms)
   as a low-risk portfolio; the upstream requests.
2. Nothing more is run on 2021–26, and no new blend on 2005–2020
   backtests (decisions 28, 34). The search over labels, features and
   models on these columns is closed for now.
3. A sweep is read on the screen against same-size peers
   (`peer_column = "log_marketcap_rank"`); a backtest on `vs_peers`.

## Sealed holdout record

From `reports/final_evals.csv` (20 looks; the counts are part of every
holdout number). PR-AUC against the base rate, holdout test year in
brackets:

| cell | looks | what the looks showed |
|---|---|---|
| **3y C, "not a loser" (v1.4 [2021–23])** | **1** | **p@20 0.65, top 50 0.73 vs base 0.38; PR-AUC 0.56; picks −0.09 a year against SPY (all rows −0.25)** |
| 2y cagr_ge_0 (v1.0 [2022], v1.1 [2022]) | 3 + 2 | PR-AUC 0.62–0.68 vs base 0.51 |
| 1y cagr_ge_0 (v1.1 [2023]) | 3 | PR-AUC 0.59–0.65 vs 0.51 |
| 1y beat_spy (v1.1 [2023]) | 3 | 0.29–0.31 vs 0.27, barely any skill |
| 2y beat_spy (v1.0, v1.1 [2022]) | 1 + 2 | technicals 0.20 vs 0.21 (**none**); valuation 0.26 |
| 5y beat_spy (v1.1 [2019]) | 2 | technicals 0.18 vs 0.17 (**none**); valuation 0.24 |
| 5y cagr_ge_0 (v1.1 [2019]) | 2 | 0.66–0.68 vs 0.50 |
| 2y cagr_ge_8 (v1.0) | 1 | p@20 0.35 vs 0.30 |

A look inside a universe consumes the label's cell. The look in cell
C has no baselines on the holdout rows (a baseline there is a further
read, and Carter's). Process rules: CLAUDE.md; incidents:
[notes/process-issues.md](notes/process-issues.md).
