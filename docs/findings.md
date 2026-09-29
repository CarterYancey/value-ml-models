# Findings

What is known now, by cell, and what is planned. Kept short on purpose:
**this file is rewritten, not appended to**, and stays under about 150
lines.

- What was done, in order, one entry per sweep: [logbook.md](logbook.md).
  Read that first.
- Tables, checks and reasoning behind a conclusion: the note it links
  to, in [notes/](notes/).
- How an unattended session works: [agents.md](agents.md).

Numbers are walk-forward fold means over test years 2005–2020 (16
folds, `split_folds.parquet` of the named dataset version), `p@20`
picks the top 20 per test year, and they are **selection-biased** by
the trial counts given. They rank candidates; none is a result of
record. Results are never compared across dataset versions.

## The goal (Carter, 2026-09-29)

A manageable number of high-precision, low-risk selections with
upside. Results are judged on what a portfolio of the picks went on
to do, then on precision, then on PR-AUC
([decision log](notes/2026-09-29-decisions.md)).

## State (2026-09-29)

| cell (3y, `dataset_v1.4`) | trials | forests on the 112 ranks, p@20 | bar | status |
|---|---|---|---|---|
| C, "not a loser": `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3` | 12 | 0.78–0.79 (2013–20: 0.84), PR-AUC 0.585 | base rate 0.39 | **the candidate's cell**; parameter searches queued |
| A, "from entry": `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` | 80 | 0.48–0.50 (2013–20: 0.53–0.54), PR-AUC 0.327 | single factor 0.39, base rate 0.21 | same picks as C, more winners, more losers |
| B: `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.2` | 6 | 0.28 (2013–20: 0.18) | base rate 0.20 | no skill after 2013; dropped |
| `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` ("whole path") | 29 | 0.37–0.39 | single factor 0.34, base rate 0.11 | not pursued |
| `label_3y_beat_spy` | 47 (725 on v1.1) | 0.40–0.54 | single factor 0.49, base rate 0.35 | parked |

**The candidate** (decision 10): cell C's forest and 12-month
momentum combined by mean rank, top 10 a month, at most 2 per
sector, equal weights, buy and hold. Simulated, 35 bps a side,
`dollar_volume_3m >= 100000`, buys 2005–2020, valued end of 2023,
three forest seeds: **11.1–11.7% a year time-weighted against SPY's
9.6%, worst drawdown −47% to −49% against −53%**, final value
between 3% below and 4% above SPY's. 13 backtest configurations
were tried on those years; momentum was the best of three factors.

- **Sealed holdout:** 19 looks, all at 1y/2y/5y (below). Every 3y
  cell is unopened.
- **Code not yet in `Claude`:** the sector cap,
  `claude/backtest-sector-cap`.

## Conclusions that stand

Each with the note that carries its evidence.

1. **The models avoid losers and give up the big winners.** Top 20
   of cell A's forest: losers (3y CAGR below 0) 0.20 against 0.45
   for all rows, big losers 0.10 against 0.32, big winners (0.25 or
   more) 0.06 against 0.15.
   [pick anatomy](notes/2026-09-29-pick-anatomy.md)
2. **A modest target is predicted with high precision.** Cell C:
   0.78 at 20 picks a year, 0.76 at 50, 0.74 at 100; 0.83 or more in
   11 of 16 years; under 0.60 for entry years 2006–08 and 2019. Its
   picks: losers 0.13, median drawdown 0.13, median CAGR 0.09. Same
   note.
3. **The models are sector selectors.** They rank on market-wide
   volatility ranks, so utilities and REITs (3% and 6% of the
   universe) were half and a quarter of an uncapped portfolio's
   buys, and every buy of 2005–06 was a REIT. Uncapped portfolios
   ended 26–29% below SPY with a −63% drawdown.
   [first backtests](notes/2026-09-29-first-backtests.md)
4. **With at most 2 buys per sector the portfolio compounds at
   SPY's rate with a shallower drawdown** (9.4–9.9% against 9.6%,
   −44% to −47% against −53%): less lost in falls, less gained in
   strong rises.
   [capped backtests](notes/2026-09-29-sector-cap-backtests.md)
5. **Momentum among the stocks the forest ranks as safe adds 1.2 to
   2.4 points a year**, on three seeds; quality gives the shallowest
   drawdown (−41%) at the same return; cheapness makes the portfolio
   worse. Momentum and the value factors alone are the worst picks
   on the screen (losers 0.61–0.68).
   [factor combinations](notes/2026-09-29-factor-combinations.md)
6. **The pick-outcome screen cannot stand in for a backtest.** It
   showed cell C's picks level with SPY at a third of the average
   drawdown; the portfolio had a deeper drawdown than SPY. It counts
   stocks, not sectors. First-backtests note.
7. **A fixed score threshold selects the wrong years.** The top
   scores are 0.81–0.85 for 2006–08 entries (precision 0.15–0.60)
   and 0.65–0.69 for 2011–13 (precision near 1.0); `score >= 0.8`
   has a pooled precision of 0.42. Select by rank within the period.
   Same note.
8. **A relative label makes picks worse at beating the market**
   (cell B: picks beat SPY 0.38 of the time against 0.50 for A), and
   **fundamentals alone worked before 2013 and not after** (0.63 and
   0.28). Pick-anatomy note.
9. **Label thresholds move p@20 and PR-AUC, not what the picks go
   on to do.** Nine rungs around cell A, the same outcomes.
   [label rungs](notes/2026-09-29-label-rungs-dd-entry.md)
10. **No feature set beats the 112 rank columns in cell A, and most
    of the signal is three of them** (`vol_12m_rank`,
    `vol_36m_rank`, `conservative_score_rank`). Sector ranks add
    nothing; 60 raw columns lower PR-AUC by 0.011–0.015.
    [feature sets](notes/2026-09-29-feature-sets-dd-entry.md)
11. **Hyperparameters barely matter inside a family; p@20
    differences under 0.03 are noise. The forest's seed moves a
    backtest by about half a point a year.** A sweep summary's
    `pr_auc` is pooled and reads about 0.05 below the fold mean.
    [v1.1 families](notes/2026-08-beat-spy-v11-families.md),
    factor-combinations note.

Earlier, and standing: forests ahead of LightGBM in the compounder
cells, lift holding after 2013
([note](notes/2026-09-28-drawdown-compounder-cells.md)); no forest
beats a single factor on 3y beat_spy on v1.4
([note](notes/2026-09-beat-spy-v11-to-v14.md)); v1.0/v1.1 work
([earlier](notes/2026-08-earlier-work.md),
[derived labels](notes/2026-09-derived-label-cells.md)).

## Open questions

- Does the candidate hold outside 2005–2023? Only the holdout and
  time can say; the backtests share their years.
- Can the models be made sector-neutral instead of capped? There is
  no within-sector volatility rank upstream, and deriving one here
  is not allowed: an upstream request.
- Would a sell discipline or a shorter horizon raise the return
  without giving the losers back? Not tried.
- Does another family rank the safe stocks better? Queued.

## Plan

The queue is `experiments/queue.toml`; decisions and their reasons
are in the [decision log](notes/2026-09-29-decisions.md).

1. Parameter searches in cell C, 20 draws per family, read on
   fold-mean PR-AUC and on the picks' losers and winners. A winner
   needs +0.01 PR-AUC on three seeds to earn one backtest.
2. Carter's, when he would act on the candidate: one holdout look
   in cell C's 3y cell, promotion, the pull request for the sector
   cap, deployment.
3. Calibration before any rule that reads a score as a probability.

## Sealed holdout record

From `reports/final_evals.csv` (19 looks; the counts are part of every
holdout number). PR-AUC against the base rate, holdout test year in
brackets:

| cell | looks | what the looks showed |
|---|---|---|
| 2y cagr_ge_0 (v1.0 [2022], v1.1 [2022]) | 3 + 2 | PR-AUC 0.62–0.68 vs base 0.51 |
| 1y cagr_ge_0 (v1.1 [2023]) | 3 | PR-AUC 0.59–0.65 vs 0.51 |
| 1y beat_spy (v1.1 [2023]) | 3 | 0.29–0.31 vs 0.27, barely any skill |
| 2y beat_spy (v1.0, v1.1 [2022]) | 1 + 2 | technicals 0.20 vs 0.21 (**none**); valuation 0.26 |
| 5y beat_spy (v1.1 [2019]) | 2 | technicals 0.18 vs 0.17 (**none**); valuation 0.24 |
| 5y cagr_ge_0 (v1.1 [2019]) | 2 | 0.66–0.68 vs 0.50 |
| 2y cagr_ge_8 (v1.0) | 1 | p@20 0.35 vs 0.30 |

The Aug 24 batch opened 12 looks in ~50 minutes, comparing
technicals-vs-valuation pairs on the holdout. That is the pattern the
one-look-per-cell rule now prevents. Read those cells as consumed. The
one consistent signal: **technical-rank models had no holdout skill on
the relative (beat_spy) labels, and valuation/trend models kept some.**

## Process

Rules learned the hard way are in CLAUDE.md ("Before writing a
conclusion"); the incidents behind them are in
[notes/process-issues.md](notes/process-issues.md). The session log
up to the split is in
[notes/session-log-2026-09.md](notes/session-log-2026-09.md).
