# Feature sets and a liquidity floor in cell C, read on the portfolio screen

Detail behind the [logbook](../logbook.md) entries of 2026-09-30 for
`forest_features_nonloser_{allrows,dv100k,dv1m}_3y` and
`baseline_factors_nonloser_{dv100k,dv1m}_3y`. Decisions 15, 16 and 18
of the [decision log](2026-09-29-decisions.md). Carter's two questions
of 2026-09-30: do features chosen on theory do better than the ranks
the models lean on, and does a liquidity floor at training time help?

3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`). Cell C: `fwd_3y_cagr >= 0 &
fwd_3y_max_drawdown_from_entry < 0.3`. **One seed (23), one forest
configuration** (the candidate's, which was tuned on the ranks).
Numbers are selection-biased by the trial counts below and none is a
result of record.

## What ran, and how it was checked

- Code: `claude/universe-and-portfolio-screen` (universe, screen),
  merged into the lab branch. Runs at git `3ecbcbe` (the two baseline
  sweeps and all-rows fs0) and `b9b230b` (the rest); the second commit
  added configs and the decision log, no code.
- 15 forest fits: five feature sets on every row (bundles saved), and
  trained inside each floor. 10 evaluations of the all-rows bundles
  inside each floor (`vml-eval`, scope `test`: the models as trained,
  fewer test rows). 10 single-factor baselines inside the floors. 35
  config hashes, 16 fold rows each, none failed.
- All-rows fs0 reproduces the candidate's forest: p@20 0.7875,
  fold-mean PR-AUC 0.585 (run `53ceedd93e6d`: the same).
- Resolved columns (from each run's `*_config.json`): 112 / 97 / 144 /
  104 / 151.
- Rows, fold 2005 and fold 2020: all rows, 299,982 and 1,066,158 train
  rows (effective 12,691 and 37,198), 18,684 and 14,944 test rows;
  inside 100k, 194,708 and 756,840 (8,299 and 26,000), 13,784 and
  13,019; inside 1m, 109,036 and 523,023 (4,610 and 17,534), 9,738 and
  10,265. Base rate, fold mean: 0.392, 0.428, 0.461.
- Trials after these runs: cell C on all rows 77; inside 100k 16;
  inside 1m 15 (the five all-rows bundles count once in each cell
  they were evaluated in).

The screen (decision 16): top 10 per test quarter, at most 2 per
sector, 640 picks over 64 quarters. Equal weights, no costs, entry at
the snapshot, held three years. Every figure is the mean over test
years of the yearly statistic (40 picks a year).

## The feature sets

| | columns | what |
|---|---|---|
| fs0 | 112 | the `ranks` group |
| fs1 | 97 | ranks without the technical family |
| fs2 | 144 | fs1 plus the 47 unranked scores, shares, counts and flags |
| fs3 | 104 | ranks without the eight risk, size and liquidity ranks |
| fs4 | 151 | fs3 plus the 47 |

## Inside the 100k floor (the backtest template's universe)

"all" is trained on every row and measured inside the floor; "floor"
is trained inside it.

| | trained on | p@20 | PR-AUC | screen precision | beat SPY | mean excess | median excess | losers | deep drawdown | big winners |
|---|---|---|---|---|---|---|---|---|---|---|
| fs0 | all | 0.784 | 0.602 | 0.766 | 0.511 | −0.001 | +0.006 | 0.156 | 0.120 | 0.061 |
| fs0 | floor | 0.769 | 0.601 | 0.753 | 0.498 | −0.003 | −0.001 | 0.162 | 0.128 | 0.061 |
| fs1 | all | 0.659 | 0.577 | 0.620 | 0.433 | −0.027 | −0.026 | 0.244 | 0.273 | 0.050 |
| fs1 | floor | 0.628 | 0.575 | 0.620 | 0.409 | −0.028 | −0.030 | 0.239 | 0.269 | 0.056 |
| fs2 | all | 0.672 | 0.570 | 0.644 | 0.442 | −0.022 | −0.021 | 0.227 | 0.261 | 0.070 |
| fs2 | floor | 0.666 | 0.569 | 0.650 | 0.441 | −0.021 | −0.022 | 0.223 | 0.245 | 0.064 |
| fs3 | all | 0.644 | 0.587 | 0.658 | 0.417 | −0.030 | −0.027 | 0.234 | 0.230 | 0.038 |
| fs3 | floor | 0.656 | 0.587 | 0.675 | 0.422 | −0.025 | −0.022 | 0.214 | 0.216 | 0.050 |
| fs4 | all | 0.666 | 0.580 | 0.663 | 0.419 | −0.030 | −0.022 | 0.233 | 0.233 | 0.056 |
| fs4 | floor | 0.669 | 0.580 | 0.650 | 0.394 | −0.034 | −0.026 | 0.239 | 0.225 | 0.048 |
| highest conservative score | | 0.588 | | 0.619 | 0.523 | −0.006 | +0.008 | 0.245 | 0.259 | 0.141 |
| lowest 36-month volatility | | 0.741 | | 0.736 | 0.452 | −0.025 | −0.008 | 0.167 | 0.155 | 0.022 |
| highest return on capital | | 0.528 | | 0.519 | 0.477 | −0.052 | −0.018 | 0.347 | 0.372 | 0.206 |
| highest 12-month momentum | | 0.181 | | 0.211 | 0.236 | −0.238 | −0.244 | 0.658 | 0.720 | 0.134 |
| highest earnings yield | | 0.256 | | 0.245 | 0.288 | −0.200 | −0.165 | 0.573 | 0.641 | 0.178 |

Losers: `fwd_3y_cagr < 0`. Deep drawdown: 0.4 or more from entry. Big
winners: CAGR of 0.25 or more. All test rows inside the floor: losers
0.423, mean excess −0.089.

## Inside the 1m floor

| | trained on | p@20 | PR-AUC | screen precision | beat SPY | mean excess | median excess | losers | deep drawdown | big winners |
|---|---|---|---|---|---|---|---|---|---|---|
| fs0 | all | 0.797 | 0.618 | 0.778 | 0.522 | +0.002 | +0.009 | 0.145 | 0.114 | 0.055 |
| fs0 | floor | 0.788 | 0.615 | 0.755 | 0.513 | −0.002 | +0.004 | 0.172 | 0.119 | 0.047 |
| fs1 | all | 0.656 | 0.590 | 0.614 | 0.433 | −0.028 | −0.025 | 0.250 | 0.267 | 0.052 |
| fs1 | floor | 0.694 | 0.588 | 0.650 | 0.458 | −0.015 | −0.011 | 0.242 | 0.236 | 0.077 |
| fs2 | all | 0.669 | 0.583 | 0.639 | 0.442 | −0.023 | −0.020 | 0.236 | 0.264 | 0.072 |
| fs2 | floor | 0.672 | 0.580 | 0.669 | 0.473 | −0.019 | −0.012 | 0.223 | 0.227 | 0.072 |
| fs3 | all | 0.647 | 0.600 | 0.661 | 0.425 | −0.028 | −0.022 | 0.225 | 0.216 | 0.033 |
| fs3 | floor | 0.703 | 0.599 | 0.697 | 0.448 | −0.016 | −0.011 | 0.195 | 0.189 | 0.048 |
| fs4 | all | 0.659 | 0.593 | 0.650 | 0.417 | −0.032 | −0.022 | 0.245 | 0.233 | 0.056 |
| fs4 | floor | 0.684 | 0.591 | 0.664 | 0.419 | −0.028 | −0.022 | 0.239 | 0.200 | 0.070 |
| highest conservative score | | 0.594 | | 0.628 | 0.525 | −0.002 | +0.009 | 0.241 | | 0.148 |
| lowest 36-month volatility | | 0.747 | | 0.727 | 0.438 | −0.030 | −0.017 | 0.177 | | 0.016 |

## By entry period, inside the 100k floor, models trained on every row

| | | screen precision | beat SPY | mean excess | losers | big winners |
|---|---|---|---|---|---|---|
| 2005–12 | fs0 | 0.706 | 0.572 | +0.018 | 0.197 | 0.078 |
| | fs1 | 0.609 | 0.581 | +0.009 | 0.256 | 0.062 |
| | fs2 | 0.619 | 0.562 | +0.010 | 0.244 | 0.081 |
| | fs3 | 0.634 | 0.550 | +0.006 | 0.256 | 0.050 |
| | fs4 | 0.650 | 0.544 | +0.005 | 0.244 | 0.072 |
| | conservative score | 0.619 | 0.591 | +0.016 | 0.259 | 0.166 |
| 2013–20 | fs0 | 0.825 | 0.450 | −0.019 | 0.116 | 0.044 |
| | fs1 | 0.631 | 0.284 | −0.063 | 0.231 | 0.038 |
| | fs2 | 0.669 | 0.322 | −0.054 | 0.209 | 0.059 |
| | fs3 | 0.681 | 0.284 | −0.066 | 0.212 | 0.025 |
| | fs4 | 0.675 | 0.294 | −0.065 | 0.222 | 0.041 |
| | conservative score | 0.619 | 0.456 | −0.027 | 0.231 | 0.116 |

## What the screen picked, by sector

Utilities and real estate are 3% and 6% of the test rows. Share of the
screen's 640 picks (the cap allows at most 0.20 for one sector):

| | utilities | real estate |
|---|---|---|
| fs0, all rows | 0.18 | 0.17 |
| fs1 | 0.18 | 0.20 |
| fs2 | 0.18 | 0.19 |
| fs3 | 0.19 | 0.20 |
| fs4 | 0.18 | 0.18 |

The same within 0.04 inside both floors and whether trained inside
them or not. The largest importances without the risk ranks (fs2 and
fs3, inside 100k): `ocf_trend_4q_rank`, `ocf_consistency_4q_rank`,
`ocf_yield_rank`, `ocf_trend_8q_rank`, then `log_assets_rank`,
the `ocf_positive_frac_*` shares (fs2), `ret_6m_rank` and
`dist_52w_high_rank` (fs3). With them (fs0): `vol_12m_rank` 0.20,
`vol_36m_rank` 0.13, then the same cash-flow columns.

## Against the predictions in the configs

| | prediction | measured | matched? |
|---|---|---|---|
| all rows 1 | fs0 reproduces the candidate's forest | p@20 0.788, PR-AUC 0.585 | yes |
| 2 | fs1 p@20 0.64–0.68 | 0.659 | yes |
| 3 | fs2 above fs1 by 0.02 or more on p@20 and on PR-AUC | +0.013; PR-AUC 0.554 against 0.561 | **no** |
| 4 | fs3 between fs1 and fs0 on p@20 | 0.644, below fs1 | **no** (PR-AUC is between) |
| 5 | fs4 the best of fs1–fs4, below fs0 by 0.03 or more | 0.666, fs2 has 0.672; 0.12 below fs0 | half |
| 6 | no arm's screen mean excess more than 0.01 above fs0's; more losers than fs0 | all four are 0.02–0.03 below; losers 0.23–0.25 against 0.16 | yes |
| 6 | utilities and real estate under 0.20 of fs1's and fs2's picks | 0.38 and 0.37 | **no** |
| floors 1 | fs0 trained inside against trained on all: screen precision within 0.02, mean excess within 0.01, p@20 within 0.02 | 100k: −0.013, −0.002, −0.015. 1m: −0.023, −0.004, −0.009 | yes, but for screen precision at 1m |
| 1, rival | PR-AUC rises by 0.01 or more inside the floor | −0.001 and −0.003 | no |
| 2 | the floor helps fs1 and fs2 by 0.02 or more on p@20 | 100k: −0.031 and −0.006. 1m: +0.038 and +0.003 | **no**, one of four |
| 3 | order on p@20: fs0, fs4, fs3, fs2, fs1 | 100k: fs0, fs4, fs2, fs3, fs1. 1m: fs0, fs3, fs1, fs4, fs2 | fs0 first; the rest within noise of one another |
| 4 | no arm's mean excess more than 0.01 above fs0's | none above it at all | yes |

## Measured

1. **No feature set passes the rule of decision 16.** In every
   universe and however trained, the four sets without the risk ranks
   have a screen mean excess CAGR 0.013 to 0.034 a year below the
   ranks', losers of 0.20–0.25 against 0.15–0.17 and 1.6 to 2.3
   times the deep drawdowns. None goes to three seeds or to a backtest.
2. **The training-time floor changes nothing for the ranks forest.**
   Trained inside either floor or on every row, measured on the same
   test rows: p@20, PR-AUC, screen precision and mean excess within
   0.02, 0.003, 0.023 and 0.004.
3. **For the sets without risk ranks the floor at 1m moves p@20 by
   +0.003 to +0.056 and the screen's mean excess by +0.004 to
   +0.013; at 100k by −0.031 to +0.012 and −0.004 to +0.005.** One
   seed, and seed noise on p@20 is about 0.02: no more than a hint
   that a high floor helps a model that cannot see size.
4. **Leaving the volatility and liquidity ranks out does not change
   what kind of stock is picked.** Utilities and real estate are 33%
   to 39% of the picks in every arm and universe. Without the volatility ranks the
   forests rank on the trend, consistency and sign of operating cash
   flow, and the same two sectors have the steadiest cash flows.
5. **The 47 unranked columns add little** (fs2 against fs1, fs4
   against fs3): p@20 +0.01 to +0.04 on all rows and inside 100k,
   −0.02 inside 1m; PR-AUC lower in every comparison; the screen's
   mean excess within 0.012.
6. **Every arm beats SPY on the screen for 2005–12 entries and none
   does for 2013–20.** fs0: +0.018 and −0.019. The sets without risk
   ranks: +0.005 to +0.010 and −0.054 to −0.066, with picks beating
   SPY 0.28–0.32 of the time after 2013.
7. **The conservative score as a single factor has the forest's mean
   excess** (−0.006 against −0.001) with more losers (0.245 against
   0.156) and more than twice the big winners (0.141 against 0.061).
   Lowest volatility alone has the forest's losers (0.167) and a mean
   excess 0.024 lower: what the forest adds to a volatility sort is
   return, not safety.

## What it might mean (hypotheses)

- *Why theory-led features do not help here.* The label is "did not
  lose and did not fall 30%". Price risk answers that directly;
  fundamentals answer it through cash-flow stability, which is a
  weaker reading of the same thing and finds the same sectors. Rival:
  the forest configuration (depth 4, leaves of 72) was tuned on the
  ranks and is too shallow for 144 columns of which 47 are coarse; a
  parameter search on fs2 would separate the two. Not run: in cell C
  twenty draws moved fold-mean PR-AUC by 0.005 on the ranks.
- *Why the floor does nothing for the ranks.* The ranks include
  liquidity and size, so the forest already knows a microcap when it
  sees one and its picks were inside the floor before there was one:
  measured on all rows and inside 100k, the all-rows model's screen
  has the same precision (0.766), mean excess (−0.000 and −0.001) and
  number of stocks a year (24.1 and 24.0). Not checked row by row.

## What follows

Features and the floor are not where the upside is in this cell. The
candidate's model stays the ranks forest trained on every row, and the
floor stays in the backtest (and now in the screen). The open problem
is unchanged: the picks match the index and lack winners. Next
(decision 19): second rankings blended with the forest, read on the
screen.
