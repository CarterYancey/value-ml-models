# Findings

This file says what we know now, label by label, and what is planned.
It is rewritten each time rather than appended to, and it stays under
about 250 lines.

- [logbook.md](logbook.md) records what was done, in order. Read it
  first.
- Each conclusion below links to a note in [notes/](notes/) that holds
  the tables, checks and reasoning. [agents.md](agents.md) describes
  how an unattended session works.

**How to read the numbers.** Unless a line says otherwise, a number is
a fold mean over the 16 walk-forward folds with test years 2005 to
2020. The folds are those of `split_folds.parquet` in the named dataset
version. Each number is the best of the trials counted beside it, so it
is selection-biased. None is a result of record. Numbers from different
dataset versions, or from different universes, are never compared.

Terms such as *cell*, *look*, *p@20*, *base rate*, *lead* and
*same-size peers* are defined once, in [GLOSSARY.md](../GLOSSARY.md).

## Next session: start here

1. For what happened to the candidate after 2023, and why, read the
   [out-of-sample note](notes/2026-10-01-out-of-sample.md). For what
   was tried next, read the [large-caps note](notes/2026-10-01-large-caps.md).
   Items 27 to 35 of the [decision log](notes/2026-09-29-decisions.md)
   record how those choices were made.
2. For what to do next, read TODO.md under "Next, from Carter's
   direction of 2026-10-01" and the
   [research plan](notes/2026-10-01-research-plan.md). The candidate's
   paper-trading runbook is [paper-trading.md](paper-trading.md).
3. The branch `claude/results-2026-10-01b` carries everything meant for
   `Claude`: five code changes, the docs, the promoted results and the
   ledger shard. Every config and report sits on the lab branch
   `claude/lab-2026-10-01`, which is not for merging.

## State (2026-10-01)

Carter's goal is a manageable number of high-precision, low-risk
selections with upside. They are judged first on what a portfolio of
the picks went on to do, and second on precision.

**The candidate** (decision 24, unchanged) is the forest trained on
cell C, combined by mean rank with 12-month momentum and return on
capital. It buys the top 10 each month, at most 2 per sector, with equal
weights, inside Carter's floor (`dollar_volume_3m_rank >= 0.2`). The
backtest charges 35 bps a side. It buys and deposits from 2005 to
2026-08-21 and refits the forest at each year end after 2020:

| | final value on 260,000 | time-weighted | worst drawdown | 2005–2020 | 2021–2026 |
|---|---|---|---|---|---|
| SPY, same deposits | 1,326,084 | 10.9% | −52.9% | 9.4% a year | 15.4% a year |
| **candidate, buy and hold** | 1,193,902 | 11.3% | −41.4% | 12.7% | 7.3% |
| candidate, rank sell discipline | 1,344,630 | 12.0% | −39.6% | 13.6% | 7.6% |

**The candidate is not shown to beat SPY.** The buy-and-hold version
was 37% ahead of SPY in money at the end of 2020 and 10% behind in
August 2026. Its yearly return minus SPY's, by calendar year:

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| −8.6 | +3.2 | −2.9 | −12.5 | −14.4 | −12.7 |

The stocks it bought in 2021 to 2023 trailed SPY by 11 to 17 points a
year over the following three years, and 32% to 41% of them lost
money. For the buys of 2005 to 2020 the same two figures were +2.5
points and 20%. In all, 35 backtest configurations were tried. The
four runs that reach 2026 are the fixed candidate and its variant, so
they were not selected on the 2021–26 years.

| cell (3-year horizon, `dataset_v1.4`) | trials | best result | status |
|---|---|---|---|
| C, "not a loser" (see vocabulary) | 96 on all rows; 38 inside the 100k dollar-volume floor; 14 inside large caps | forest on 112 rank features: p@20 0.79 against a base rate of 0.39. Inside the floor it led same-size peers by 0.03 a year; 20% of its picks lost money for the 2005–12 entries and 12% for 2013–20, against 33% and 26% of the peers | **the candidate's forest**. **Holdout look 1 of 1**: p@20 0.65, top 50 0.73, base rate 0.38 |
| `label_3y_beat_spy` inside large caps | 16 | forest: PR-AUC 0.48 against a base rate of 0.45; no lead after 2013 | closed: not learnable once size is held fixed |
| `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.3` inside large caps | 10 | p@20 below the base rate | closed |
| the 1-year labels, cells A and B, the whole-path labels, `fwd_3y_cagr >= 0.15` | see the notes | | closed earlier |

## Conclusions that stand

1. **The forest predicts "not a loser" on data it was never chosen on,
   and that is what it is good for.** Carter ran the one holdout look
   in cell C on 2026-10-01. Of the top 20 picks a year, 65% met the
   label. Of the top 50, 73% did. The base rate was 38%. Among the top
   20, 28% lost money, against 54% of all rows. The lead survives a
   size adjustment: 22% of its 2021–23 picks lost money, against 34%
   of same-size peers. See decision 29 and the out-of-sample note.
2. **Company size decides more than any model, and "beats the average
   stock" is not skill.** The table shows the three-year
   lead over SPY, in points a year, by the year the stocks were bought.

   | bought in | smaller half of investable stocks | largest 5% |
   |---|---|---|
   | 2005–12 | −12 | 0 |
   | 2013–20 | −18 | −2.5 |
   | 2021–23 | −33 | −6.5 |

   More than half of every lead over all rows in the earlier notes
   came from the picks being large companies. So every selection is
   read against same-size peers. Each backtest report has a
   `vs_peers` table and the screen has a `peer_column`.
3. **Against same-size stocks the candidate led by 5 to 6 points a
   year in 2005–2020 and by nothing after.** The table shows the three-year
   lead over same-size peers, in points a year, by the year the stocks
   were bought.

   | bought in | the candidate | the forest alone |
   |---|---|---|
   | 2005–12 | +4.6 | +2.3 |
   | 2013–20 | +5.9 | +2.7 |
   | 2021–23 | −1.6 | +0.6 |

   What momentum and return on capital added to the forest reversed
   sign. The lead was already zero for the buys of 2019 and 2020.
4. **In 2021–26 SPY beat equal-weighted portfolios of stocks of every
   size**, including its own thirty largest members, which trailed it
   by 3.3 points a year. A few very large, volatile companies carried
   the index. A model that favours calm stocks ranks them in the
   middle. In three Januaries the forest placed NVDA about 1,500th of
   3,400. No equal-weighted selection from this universe kept up. This
   is condition (2) of the thesis, the one about the era.
5. **Among large companies the features rank risk and one quality
   factor, and nothing else.** Inside large caps, forests on "not a
   loser" lead same-size peers by 2 points a year. Return on capital
   alone leads by 3 to 4 points. The conservative score alone leads by
   3. Models of "beat SPY", as a label or as a regression target, show
   no lead after 2013. The forest
   separates the worst quintile from the rest and nothing above it.
   See the large-caps note.
6. **The forest's taste for utilities and REITs comes from its target,
   not its inputs.** Given `sector` as an input, the forest picks the
   same utilities and REITs, 34% of its picks, at the same precision.
   Without the volatility ranks it finds them anyway, through
   cash-flow stability
   ([features note](notes/2026-09-30-features-and-floor.md)).
   Adding return on capital as a second ranking is what removes them.
7. **Selection is by rank within the period, not by confidence.** An
   honest calibrator may only use outcomes that were observable at the
   time, so it runs years behind the regime. These changes moved the
   result little: a shorter horizon, theory-led features, a
   training-time liquidity floor, label thresholds, forest parameters
   and the seed. See the
   [blends note](notes/2026-09-30-blends-and-calibration.md) and the
   [searches note](notes/2026-09-29-searches-nonloser.md). One side
   result: in cell C, a forest on the nine separate Piotroski signals
   scores a PR-AUC of 0.507 and a forest on their sum 0.466. The gain
   comes mostly through the "operating cash flow positive" signal.
   Both are far below the forest on the 112 ranks, which scores 0.585.
8. **A rank-based sell discipline added 0.7 points a year over 21
   years** and nothing in 2021–26. It is why that variant ends level
   with SPY.
9. **Two known instrument faults** ([process issues](notes/process-issues.md)).
   Backtest reports dated before 2026-10-01 print "years" that run
   December to December. The delisting convention understates acquired
   stocks on the screen, though not in the backtest's per-buy reading.

Earlier work: [backtests to 2023](notes/2026-09-30-backtests.md),
[pick anatomy](notes/2026-09-29-pick-anatomy.md),
[label rungs](notes/2026-09-29-label-rungs-dd-entry.md),
[compounder cells](notes/2026-09-28-drawdown-compounder-cells.md),
[v1.0/v1.1](notes/2026-08-earlier-work.md).

## The thesis, and the working assumption

The thesis is that high precision on a modest target is achievable,
and it held out of sample: the candidate bought fewer losers and
suffered shallower falls. What it did not do is earn the index's
return in 2021–26, years in which the index beat every size of stock.

**Carter's working assumption (decision 36)** is that 2021–26 is a
bubble led by stocks that fail a value investor's test. On that
reading a value strategy trails through the bubble, leads again during
and after the correction, and should be waited out.

Evidence for it: conclusion 4 above, and the one precedent in the
data. On 1999–2004, years no model here was chosen on, a stand-in for
the candidate trailed in 1999. For the buys of 2000–02 it then led by
9 points a year, against SPY and against same-size peers alike.

What the record cannot show: the years in which that earlier bubble
grew are before the data (Sharadar starts in 1998). The candidate's
same-size lead had already gone for the buys of 2019–20. The 1999
run-up was in small stocks, whereas today's excess is in a few giants
inside the index. And nobody yet knows whether the buys of 2021–23
recover. See decision 35 and the section "The last bubble" of the
[out-of-sample note](notes/2026-10-01-out-of-sample.md).

## Open questions

- Is 2021–26 a bubble, and does the candidate lead again when it
  deflates? Carter's working assumption is that it is one, led by
  stocks that fail a value investor's test, and that a value strategy
  trails through it and leads again during and after the correction.
  Only paper trading and time can answer.
- Can information outside prices and financial statements rank upside:
  insider and institutional transactions, the state of the market?
  Those features would have to be built upstream.

## Plan

Carter's direction of 2026-10-01 (decision 36): treat the bubble
reading as the working assumption, paper-trade the candidate as it is,
and keep widening the search.

1. Paper trading follows [paper-trading.md](paper-trading.md). The
   path has been run end to end once and reproduced 9 of the
   backtest's 10 picks for August 2026.
2. Queued, needing no new code: an over-priced-stock model (label
   "fell 50% from entry") and continuous growth models. After those,
   blends by worst rank, then sessions on calibration and on other
   model families. See the
   [research plan](notes/2026-10-01-research-plan.md).
3. Every new arm is judged on the walk-forward test years 2005–2020,
   against same-size peers, in both halves, on three seeds. The
   decision rule is written down before the run. The years 2021–26 are
   context only. Even so, every number on disk was touched by past
   choices. Paper trading is the only clean out-of-sample evidence.

## Sealed holdout record

`reports/final_evals.csv` records 20 looks at the sealed holdout so
far. The look count is part of every holdout number: a cell looked at
twice is no longer a clean test. Each row gives PR-AUC against the
base rate, with the holdout test year in brackets.

| cell | looks | what the looks showed |
|---|---|---|
| **3y C, "not a loser" (v1.4 [2021–23])** | **1** | **p@20 0.65, top 50 0.73, base rate 0.38; PR-AUC 0.56; picks −0.09 a year against SPY, all rows −0.25** |
| 2y cagr_ge_0 (v1.0 [2022], v1.1 [2022]) | 3 + 2 | PR-AUC 0.62–0.68 against a base rate of 0.51 |
| 1y cagr_ge_0 (v1.1 [2023]) | 3 | 0.59–0.65 against 0.51 |
| 1y beat_spy (v1.1 [2023]) | 3 | 0.29–0.31 against 0.27: barely any skill |
| 2y beat_spy (v1.0, v1.1 [2022]) | 1 + 2 | technicals 0.20 against 0.21 (**no skill**); valuation 0.26 |
| 5y beat_spy (v1.1 [2019]) | 2 | technicals 0.18 against 0.17 (**no skill**); valuation 0.24 |
| 5y cagr_ge_0 (v1.1 [2019]) | 2 | 0.66–0.68 against 0.50 |
| 2y cagr_ge_8 (v1.0) | 1 | p@20 0.35 against 0.30 |

A look inside a universe uses up the whole label's cell. The one look
in cell C has no baselines computed on the holdout rows. Computing one
would be a second look, and that look is Carter's to take. Process
rules are in CLAUDE.md. Incidents are in
[notes/process-issues.md](notes/process-issues.md).
