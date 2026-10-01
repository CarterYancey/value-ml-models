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

1. The candidate, its evidence, how to reproduce and run it:
   [the candidate](notes/2026-10-01-candidate.md). How it was
   reached: [decisions](notes/2026-09-29-decisions.md) 14–26.
2. What to do next: TODO.md, "Next, from the sessions of 2026-09-30
   and 2026-10-01".
3. One branch carries everything for `Claude`:
   `claude/results-2026-10-01` (seven code changes, docs, 20 promoted
   results, the ledger shard). Until it is merged, the code is not in
   `Claude`. Every config and report of the sessions, promoted or
   not, is on the lab branch `claude/lab-2026-09-30` (not for
   merging).

## State (2026-09-30)

The goal (Carter): a manageable number of high-precision, low-risk
selections with upside, judged on what a portfolio of the picks went
on to do, then on precision. 0.65 and the number of picks are aims.

**The candidate** (decision 24): cell C's forest, 12-month momentum
and return on capital combined by mean rank; top 10 a month, at most
2 per sector, equal weights, `dollar_volume_3m >= 100000`. Simulated,
35 bps a side, buys 2005–2020, valued end of 2023, three forest seeds:

| | final value on 192,000 | time-weighted | worst drawdown | per buy, 3y excess a year |
|---|---|---|---|---|
| SPY, same deposits | 732,110 | 9.58% | −52.9% | |
| **candidate, buy and hold** | 949,000–960,000 | 12.2% | −41% to −42% | +0.024 to +0.026 (2005–12: +0.034; 2013–20: +0.013 to +0.016) |
| candidate, rank sell discipline | 1,028,000–1,091,000 | 12.7–13.1% | −39.5% to −40.5% | the same |
| forest + return on capital, sell discipline | 800,000–852,000 | 10.6–11.1% | −39% to −40% | +0.012 to +0.019 |
| decision 10's candidate (forest + momentum) | 711,000–764,000 | 11.1–11.7% | −47% to −49% | +0.001 to +0.005 (2013–20: −0.016 to −0.023) |

61% of the candidate's buys beat SPY over their first three years,
20% lost money; 235 stocks bought in sixteen years; utilities and
real estate 1.4% of buys. **Trading on through 2021–23** (Carter's
leave, decision 26; overlaps the holdout era): 985,668 on 228,000
against SPY's 774,140, −9.6 / +4.3 / −2.2 points against SPY in
2021 / 2022 / 2023, and the 2021 buys trailed SPY by 15 points over
their first year, the worst cohort of the sample. **31 backtest configurations were tried on
these years; this is the best of them, and it has not been shown to
hold outside 2005–2023.** [backtests](notes/2026-09-30-backtests.md)

| cell (3y unless said, `dataset_v1.4`) | trials | best | status |
|---|---|---|---|
| C, "not a loser": `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3` | 80 on all rows; 23 inside the 100k floor; 15 inside 1m | forest on 112 ranks: p@20 0.79 (base 0.39), PR-AUC 0.585 | **the candidate's forest**; feature sets, floor and parameters searched, nothing better |
| 1y: `fwd_1y_cagr >= 0 & fwd_1y_max_drawdown_from_entry < 0.2`, inside 100k | 6 | forest p@20 0.67 (base 0.46) | closed: the 3y forest picks better at 1y |
| A, B, whole path, `label_3y_beat_spy`, `fwd_3y_cagr >= 0.15` | 80, 6, 29, 47, 1 | see notes | not pursued (same picks as C, or no skill) |

**Sealed holdout:** 19 looks, none in a 3y cell (below).

## Conclusions that stand

1. **The forest avoids losers and gives up winners; a second and
   third ranking put the winners back.** Forest alone: 17% of buys
   lose money over three years and the portfolio earns SPY's return.
   With return on capital: +0.012 to +0.019 a year per buy in both
   halves. With momentum as well: +0.025. Backtests note.
2. **Momentum helps only beside quality.** Forest + momentum led on
   time-weighted return because of 2005–11; per buy it is negative
   for 2013–20. Time-weighted return gives the small early portfolio
   the weight of the late one: read the per-buy table of every
   backtest beside it.
   [blends](notes/2026-09-30-blends-and-calibration.md)
3. **Theory-led features and a training-time liquidity floor do not
   help in cell C.** Four sets without the risk ranks (fundamentals;
   with 47 unranked scores, shares and flags; without volatility,
   size and liquidity) pick 0.013–0.034 a year worse on the screen
   with more losers. The floor changes nothing for the ranks forest.
   One seed, one forest configuration.
   [features and floor](notes/2026-09-30-features-and-floor.md)
4. **The models are sector selectors whatever they are fed.** Without
   volatility they rank on the stability of operating cash flow and
   pick the same utilities and REITs (33–39% of picks). Return on
   capital as a second ranking removes them (it is undefined for most
   REITs and low for utilities). Same note;
   [first backtests](notes/2026-09-29-first-backtests.md).
5. **Selection is by rank within the period, not by confidence.** An
   honest calibrator for a 3-year label is four years behind: it gave
   no row 0.5 in 2011–13 (top 20 right 95–100%) and 0.5 to 42–44% of
   rows in 2017–19 (precision 0.31–0.48). A 1-year label's is two
   years behind and no better (precision at 0.5 from 0.10 to 0.84 by
   year). Blends note; [1y cell](notes/2026-09-30-one-year-cell.md).
6. **A shorter horizon does not help**: the 3-year forest's picks have
   fewer 1-year losers (0.236 against 0.275) than a forest trained on
   the 1-year label, and neither sees a crash coming. 1y note.
7. **A rank sell discipline helps where the rank is stable**: +0.75
   to +0.99 points a year for the quality blend, +0.4 to +0.9 for the
   candidate, −1.2 for forest + momentum (costs 8.5 times).
8. **The dataset's delisting convention understates acquired
   stocks.** A delisted stock's price is carried flat to the horizon;
   a portfolio reinvests the cash. 15% of the momentum blend's screen
   picks were acquired inside the window. It biases `fwd_*` outcomes
   and every upside label. Blends note; upstream request in TODO.
9. **The screen (top 10 a quarter, 2 per sector) is a shortlist, not
   a verdict.** It agreed with the backtests' per-buy reading on
   return on capital and earnings yield and was 0.02 harsher on every
   blend with momentum. Blends note.
10. **Label thresholds, forest parameters and the seed move little**
    (a seed: half a point a year in a backtest at most); **a relative
    label makes picks worse at beating the market; the cheapest
    stocks are the worst picks.**
    [rungs](notes/2026-09-29-label-rungs-dd-entry.md),
    [searches](notes/2026-09-29-searches-nonloser.md),
    [pick anatomy](notes/2026-09-29-pick-anatomy.md)

Earlier work: [compounder cells](notes/2026-09-28-drawdown-compounder-cells.md),
[3y beat_spy on v1.4](notes/2026-09-beat-spy-v11-to-v14.md),
[v1.0/v1.1](notes/2026-08-earlier-work.md),
[derived labels](notes/2026-09-derived-label-cells.md) (one row
corrected 2026-09-30).

## Open questions

- Does the candidate hold outside 2005–2023? Low risk, quality and
  momentum are known to have paid in this period; the blend may be
  their sum. Only the holdout, 2021–23 trading and time can say.
  Every portfolio trailed SPY in 2021 (the candidate by 9.5 points).
- Why the screen is harsher on momentum blends than the backtests'
  own buys (entry timing is what is left), and whether a parameter
  search on the theory-led features would change conclusion 3.

## Plan

1. Carter's: the pull request from `claude/results-2026-10-01`; one
   holdout look in cell C's 3y cell with `forest_nonloser_dd30_3y`;
   which liquidity floor to deploy with; deployment and paper trading
   of the candidate beside its sell-discipline variant.
2. No further backtests on buys of 2005–2020 (decisions 24, 26: 31
   tried). New ideas are read on the portfolio screen and on the
   per-buy table of an existing run.
3. Proposed, not built: `sector` as a model input; a position cap;
   the floor and sector cap in `vml-predict`; upstream requests
   (delisting-aware outcomes, within-sector risk ranks, market-state
   features). TODO.md has each with its reason.

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

All on older dataset versions and simpler labels (Carter, 2026-09-30:
not a reason to hold experiments back). A look inside a universe
consumes the label's cell. Process rules: CLAUDE.md; incidents:
[notes/process-issues.md](notes/process-issues.md) (2026-09-30:
calibration fitted on outcomes from the future).
