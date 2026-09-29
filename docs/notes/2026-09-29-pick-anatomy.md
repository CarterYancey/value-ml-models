# What the picks are made of

Detail behind the [logbook](../logbook.md) entries for
`baseline_pick_anatomy_3y` and `forest_pick_anatomy_3y`, run and read
2026-09-29 in the sandbox. Decision 1 of the
[decision log](2026-09-29-decisions.md).

3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`). Numbers are
selection-biased by the trial counts and none is a result of record.
Pick outcomes read the top K rows per test year with no costs, no
investability filter and equal weights: a screen, not a backtest.
Every figure is the mean over test years of the yearly statistic,
and over seeds.

## What ran, and how it was checked

- `forest_pick_anatomy_3y`: 3 cells × 2 feature sets × 3 seeds (23,
  232, 1776) = 18 runs, 0 failed, git `b8de57a` and `f4fe2a9` (the
  second is a commit to the decision log made while the sweep ran; no
  code differs). One forest configuration: set1 of
  `forest_candidate_sets_3y`, class weight 1.0. 18 hashes in the
  ledger shard, 288 fold rows, 16 per hash. Resolved columns 112
  (fs0, `ranks`) and 97 (fs1, ranks minus `ranks/technical`).
- `baseline_pick_anatomy_3y`: 4 deterministic single-factor runs, git
  `603c440`, 64 fold rows.
- A/fs0 reproduces the reference and the rungs' centre cell: p@20
  0.5000, seed std 0.0162, fold-mean PR-AUC 0.3267, picks beat SPY
  0.498.
- Trials after the sweeps: cell A 79; cells B and C 6 each, none
  before.

Cells:

| | label | base rate |
|---|---|---|
| A | `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` | 0.207 |
| B | `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.2` | 0.198 |
| C | `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3` | 0.392 |

## Top 20 per year, all test years

"Losers" is the share with `fwd_3y_cagr < 0`, "big losers" below
−0.1, "deep drawdown" a drawdown from entry of 0.4 or more, "winners"
a CAGR of 0.15 or more, "big winners" 0.25 or more.

| | p@20 | PR-AUC | beat SPY | median excess | median CAGR | median drawdown | losers | big losers | deep drawdown | winners | big winners | stocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all test rows | | | 0.358 | −0.073 | 0.023 | 0.391 | 0.452 | 0.318 | 0.498 | 0.271 | 0.149 | |
| A, ranks | 0.500 | 0.327 | 0.498 | −0.003 | 0.088 | 0.200 | 0.200 | 0.100 | 0.171 | 0.335 | 0.060 | 14.2 |
| A, fundamentals | 0.397 | 0.311 | 0.456 | −0.008 | 0.085 | 0.230 | 0.223 | 0.084 | 0.252 | 0.237 | 0.052 | 10.4 |
| B, ranks | 0.278 | 0.289 | 0.380 | −0.026 | 0.073 | 0.196 | 0.247 | 0.077 | 0.205 | 0.207 | 0.041 | 13.3 |
| B, fundamentals | 0.291 | 0.278 | 0.427 | −0.021 | 0.074 | 0.243 | 0.242 | 0.069 | 0.284 | 0.223 | 0.048 | 10.0 |
| **C, ranks** | **0.782** | 0.585 | 0.462 | +0.001 | 0.091 | 0.126 | 0.131 | 0.058 | 0.096 | 0.265 | 0.032 | 14.1 |
| C, fundamentals | 0.662 | 0.561 | 0.453 | −0.011 | 0.085 | 0.218 | 0.208 | 0.073 | 0.230 | 0.247 | 0.049 | 10.7 |
| `conservative_score_rank` | 0.388 | | 0.491 | −0.004 | 0.090 | 0.261 | 0.272 | 0.119 | 0.309 | 0.362 | 0.128 | 15.4 |
| `earnings_yield_rank` | 0.075 | | 0.216 | −0.220 | −0.121 | 0.585 | 0.631 | 0.519 | 0.688 | 0.162 | 0.119 | 10.3 |
| `book_to_market_rank` | 0.106 | | 0.194 | −0.207 | −0.105 | 0.489 | 0.609 | 0.497 | 0.588 | 0.131 | 0.081 | 9.6 |
| `magic_formula_score_rank` | 0.097 | | 0.247 | −0.196 | −0.100 | 0.576 | 0.616 | 0.484 | 0.669 | 0.200 | 0.109 | 12.4 |

p@20 is against each cell's own label (the single factors': cell A)
and is not compared between cells. Seed std of p@20 is 0.005–0.017;
no outcome in the table differs between seeds by more than 0.04.

## By period, top 20

Forests on the ranks group and the single-factor bar. SPY's CAGR over
the same windows is the median CAGR of the picks minus their median
excess, roughly.

| entry years | | p@20 | beat SPY | median excess | median CAGR | median drawdown | losers | big losers | big winners |
|---|---|---|---|---|---|---|---|---|---|
| 2005–12 | all rows | | 0.412 | −0.044 | 0.025 | 0.402 | 0.453 | 0.326 | 0.160 |
| | A | 0.465 | 0.519 | +0.007 | 0.070 | 0.272 | 0.242 | 0.167 | 0.090 |
| | C | 0.723 | 0.540 | +0.027 | 0.092 | 0.149 | 0.160 | 0.108 | 0.042 |
| | A, fundamentals | 0.421 | 0.629 | +0.035 | 0.098 | 0.287 | 0.225 | 0.083 | 0.081 |
| | bar | 0.356 | 0.544 | +0.012 | 0.075 | 0.253 | 0.300 | 0.125 | 0.144 |
| 2013–16 | all rows | | 0.320 | −0.088 | 0.027 | 0.298 | 0.437 | 0.299 | 0.121 |
| | A | 0.688 | 0.654 | +0.019 | 0.133 | 0.085 | 0.117 | 0.054 | 0.021 |
| | C | 0.925 | 0.508 | −0.007 | 0.108 | 0.060 | 0.050 | 0.013 | 0.017 |
| | A, fundamentals | 0.488 | 0.400 | −0.022 | 0.094 | 0.087 | 0.142 | 0.075 | 0.038 |
| | bar | 0.712 | 0.675 | +0.046 | 0.160 | 0.078 | 0.138 | 0.050 | 0.150 |
| 2017–20 | all rows | | 0.290 | −0.117 | 0.016 | 0.463 | 0.463 | 0.321 | 0.155 |
| | A | 0.383 | 0.300 | −0.045 | 0.081 | 0.171 | 0.200 | 0.013 | 0.042 |
| | C | 0.758 | 0.262 | −0.043 | 0.071 | 0.147 | 0.154 | 0.004 | 0.029 |
| | A, fundamentals | 0.258 | 0.167 | −0.080 | 0.048 | 0.258 | 0.300 | 0.096 | 0.008 |
| | bar | 0.125 | 0.200 | −0.084 | 0.051 | 0.459 | 0.350 | 0.175 | 0.075 |
| crash windows (2005–08, 2019) | all rows | | 0.409 | −0.050 | −0.038 | 0.559 | 0.558 | 0.403 | 0.100 |
| | A | 0.107 | 0.430 | −0.011 | −0.012 | 0.458 | 0.430 | 0.260 | 0.020 |
| | C | 0.480 | 0.523 | +0.041 | 0.040 | 0.246 | 0.287 | 0.173 | 0.007 |
| | bar | 0.100 | 0.480 | −0.004 | −0.007 | 0.452 | 0.420 | 0.210 | 0.050 |

Cell C, ranks, by test year (three seeds):

| year | base rate | p@20 | p@50 | picks beat SPY | median excess | median CAGR | losers | big losers | median drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 2005 | 0.44 | 0.70 | 0.70 | 0.43 | −0.008 | 0.043 | 0.22 | 0.13 | 0.10 |
| 2006 | 0.25 | 0.55 | 0.35 | 0.62 | +0.085 | −0.011 | 0.40 | 0.33 | 0.15 |
| 2007 | 0.16 | 0.23 | 0.21 | 0.63 | +0.070 | 0.001 | 0.48 | 0.30 | 0.42 |
| 2008 | 0.17 | 0.38 | 0.39 | 0.88 | +0.111 | 0.125 | 0.10 | 0.10 | 0.32 |
| 2009 | 0.57 | 0.97 | 0.98 | 0.72 | +0.045 | 0.191 | 0.03 | 0.00 | 0.04 |
| 2010 | 0.53 | 1.00 | 0.99 | 0.42 | −0.020 | 0.138 | 0.00 | 0.00 | 0.04 |
| 2011 | 0.49 | 0.97 | 0.98 | 0.38 | −0.026 | 0.136 | 0.03 | 0.00 | 0.06 |
| 2012 | 0.59 | 0.98 | 0.97 | 0.23 | −0.042 | 0.111 | 0.02 | 0.00 | 0.06 |
| 2013 | 0.49 | 0.95 | 0.93 | 0.68 | +0.009 | 0.120 | 0.05 | 0.00 | 0.07 |
| 2014 | 0.40 | 0.87 | 0.93 | 0.53 | +0.007 | 0.108 | 0.03 | 0.00 | 0.06 |
| 2015 | 0.38 | 0.97 | 0.93 | 0.45 | −0.029 | 0.085 | 0.03 | 0.03 | 0.05 |
| 2016 | 0.54 | 0.92 | 0.88 | 0.37 | −0.015 | 0.120 | 0.08 | 0.02 | 0.06 |
| 2017 | 0.36 | 0.83 | 0.81 | 0.58 | +0.010 | 0.120 | 0.17 | 0.02 | 0.12 |
| 2018 | 0.28 | 0.93 | 0.87 | 0.17 | −0.088 | 0.090 | 0.03 | 0.00 | 0.04 |
| 2019 | 0.24 | 0.53 | 0.56 | 0.05 | −0.052 | 0.042 | 0.23 | 0.00 | 0.24 |
| 2020 | 0.38 | 0.73 | 0.62 | 0.25 | −0.041 | 0.031 | 0.18 | 0.00 | 0.19 |

Brier beats `base_rate_brier` in 11 of 16 years in C with ranks (10
in A). Mean score of the top 20 in C: 0.75 against a precision of
0.78.

## Fewer or more picks

Cells A and C, ranks:

| | K | precision | beat SPY | median excess | losers | big losers | big winners | stocks |
|---|---|---|---|---|---|---|---|---|
| A | 5 | 0.508 | 0.529 | +0.007 | 0.192 | 0.100 | 0.100 | 4.3 |
| A | 10 | 0.506 | 0.535 | +0.004 | 0.200 | 0.096 | 0.081 | 7.6 |
| A | 20 | 0.500 | 0.498 | −0.003 | 0.200 | 0.100 | 0.060 | 14.2 |
| A | 50 | 0.479 | 0.477 | −0.002 | 0.198 | 0.093 | 0.050 | 31.6 |
| C | 5 | 0.763 | 0.454 | −0.011 | 0.154 | 0.071 | 0.054 | 4.1 |
| C | 20 | 0.782 | 0.462 | +0.001 | 0.131 | 0.058 | 0.032 | 14.1 |
| C | 50 | 0.755 | 0.442 | −0.009 | 0.170 | 0.076 | 0.040 | 29.4 |

## Against the predictions in the config

| | prediction | measured | matched? |
|---|---|---|---|
| 1 | A with ranks reproduces the rungs' centre | p@20 0.500, beat SPY 0.498 | yes |
| 2 | A's picks: losers under 0.15, all rows near 0.45 | 0.200; all rows 0.452 | **no** on the level (0.20), yes on the direction: under half the all-row rate |
| 2 | A's picks: big winners at or under the all-row rate | 0.060 against 0.149 | yes |
| 3 | fundamentals only: more big winners and more big losers | big winners 0.052 / 0.048 / 0.049 against 0.060 / 0.041 / 0.032; big losers 0.084 / 0.069 / 0.073 against 0.100 / 0.077 / 0.058 (A / B / C) | **no**: within 0.02 either way, no pattern |
| 3 | fundamentals only: a higher drawdown, median excess not higher | drawdown higher in all three cells by 0.03–0.09; median excess lower in A and C, 0.005 higher in B | yes |
| 4 | B picks nearly what A picks, beat SPY within 0.03 | 0.380 against 0.498 | **no**: 0.12 lower |
| 5 | C reaches p@20 of 0.70 or more | 0.782, worst seed 0.778 | yes |
| 5 | C's picks' outcomes within noise of A's | beat SPY 0.462 against 0.498, median excess +0.001 against −0.003; losers 0.131 against 0.200, drawdown 0.126 against 0.200, big winners 0.032 against 0.060 | returns yes; C's picks are calmer than A's on every risk measure |
| 6 | p@5 and p@10 within 0.03 of p@20 in A | 0.508, 0.506, 0.500 | yes |
| baseline | conservative score: losers and big losers under half the all-row rates | 0.272 of 0.452, 0.119 of 0.318 | losers **no** (0.60 of the rate), big losers yes |
| baseline | conservative score: big winners at or under the all-row rate | 0.128 against 0.149 | yes |
| baseline | value factors: big winners above the all-row rate | 0.081–0.119 against 0.149 | **no**: below it |
| baseline | value factors: big losers at or above the all-row rate, median excess below the conservative score's | 0.48–0.52 against 0.32; −0.20 to −0.22 | yes |

## Measured

1. **Carter's reading holds.** The picks of the primary cell's forest
   hold fewer than half the losers of the universe (0.20 against
   0.45), a third of the big losers (0.10 against 0.32) and a third
   of the deep drawdowns, and 40% of its big winners (0.06 against
   0.15). Ordinary winners (CAGR of 0.15 or more) are more frequent
   among the picks than in the universe (0.34 against 0.27). The
   picks' returns are squeezed from both ends.
2. **The "not a loser" label is predicted with a precision of 0.78**
   at 20 picks a year and 0.76 at 50, against a base rate of 0.39:
   0.84 in 2013–20, 0.83 or more in 11 of 16 years. Its picks hold
   the fewest losers of any arm (0.13; 0.05 for entry years 2013–16)
   and almost no big losers after 2009 (at most 0.03 in any year).
   It is below 0.60 for entry years 2006, 2007, 2008 and 2019.
3. **High precision on the modest target did not bring excess return
   on this screen.** C's picks have a median CAGR of 0.09 and a
   median excess CAGR of zero; they beat SPY 0.46 of the time. For
   entry years 2009–18 their median CAGR is 0.085–0.19 a year with a
   median drawdown from entry of 0.04–0.07, and SPY returned more
   than they did in six of those ten years.
4. **The picks beat SPY in and after market falls and lose to it in
   the long rise.** C's picks beat SPY 0.52 of the time in the
   crash-window years and 0.72–0.88 for 2008–09 entries; 0.17–0.25
   for 2018 and 2020 entries. Condition (2) of the thesis, seen in
   the data.
5. **Training on a relative label makes the picks worse at beating
   the market.** Cell B's picks beat SPY 0.38 of the time against
   0.50 for A's and 0.46 for C's; in 2013–20, 0.22 against an
   all-row rate of 0.31. B's p@20 is at its base rate in 2013–20
   (0.18 against 0.18). Consistent with the earlier finding that
   forests have no edge on 3y beat_spy on v1.4 after 2012.
6. **Fundamentals alone worked before 2013 and not after.** A with
   fundamentals only: picks beat SPY 0.63 of the time for 2005–12
   entries (ranks: 0.52) and 0.28 for 2013–20 (ranks: 0.48, all
   rows: 0.31). It concentrates on fewer stocks (10 per 20 picks).
7. **The cheapest stocks are the worst picks on every measure.**
   Highest earnings yield, book to market or magic-formula score:
   losers 0.61–0.63, big losers 0.48–0.52, median excess CAGR about
   −0.20, and fewer big winners than the universe.
8. **The top of the ranking is no purer than the top 20,** and the
   top 50 loses 0.02–0.03 of precision. The top 5 of cell A hold
   more big winners (0.10 against 0.06).
9. **The single low-risk factor keeps the upside the forests give
   up:** big winners 0.13 against 0.06 (top 5: 0.21), with more
   losers (0.27) and a deeper drawdown (0.26). After 2017 it fails
   (losers 0.35, beat SPY 0.20) where the forests hold their risk
   profile.

## What it might mean (hypotheses, not tested)

- *Why the picks match the index and do not beat it.* What the
  models have learned to recognise is calm, cash-generative stocks.
  Those rarely fall far and rarely triple. With top-K rows a year,
  equal weights and a three-year hold that is an index-like return
  at about a third of the drawdown of the average stock. Rivals for
  why that is not more: (a) the period: SPY's 3-year CAGR was above
  0.10 for most entry years 2009–18, a bar that a no-loser portfolio
  does not clear by construction; (b) the screen: it counts rows,
  ignores when in the year a pick is made, and compares with SPY's
  median, not with a portfolio's path; the thesis is about
  compounding without large losses, which a median of three-year
  CAGRs does not measure; (c) the models really have no upside
  skill. A backtest separates (b) from the rest; (a) and (c) need an
  upside-seeking second stage to tell apart.
- *Why B is worse than A at B's own game.* A relative label asks
  the model to predict SPY's return as well as the stock's; what it
  learned about that before 2013 (fundamentals, value) reversed
  after. Not tested further.

## Decision

Cell C with the ranks group is the first candidate that does what
the thesis asks of the model: high precision on a modest target and
very few losers. It is carried forward (decisions 5 and 6 of the
[decision log](2026-09-29-decisions.md)): a saved fold bundle,
selection by score, and a backtest against cell A's forest and the
single factor. The upside is the open problem and gets its own
sweeps.
