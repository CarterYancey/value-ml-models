# Over-priced stocks, continuous growth models, worst rank (2026-11-23)

Decisions 38 and 39 of the [decision log](2026-09-29-decisions.md).
`dataset_v1.4`, walk-forward test years 2005–2020 (16 folds,
`split_folds.parquet`), git `9df7b1a` (crash sweeps) and `3a85671`
(growth sweep); every figure is selection-biased by the trial counts
given and is no result of record.

How the screen is read (as in decisions 33–34): the screen's top 10 a
test quarter (at most 2 per sector) inside the 100k floor; "lead" is
the mean over a half's years of the picks' mean `fwd_3y_excess_cagr`
minus the mean of their same-size peers (the test rows of the same
quarter in the same 5% band of `log_marketcap_rank`); "losers" is
the share with 3y CAGR < 0. Computed from each report's screen table
(the script reproduces decision 34's +0.022 / +0.053 and +0.030 /
+0.027 exactly).

## 1. Over-priced stocks: "fell 50% from entry" (research plan, item 2)

Inside `dollar_volume_3m_rank >= 0.5`. Trials in each cell: 7 single
factors (`baseline_factors_crash_dd50`) + 1 forest configuration on
three seeds (`forest_crash_dd50`).

| cell | base rate | best factor PR-AUC (p@20) | forest PR-AUC (p@20), 3 seeds |
|---|---|---|---|
| 1y | 0.137 | `vol_12m_rank` 0.266 (0.57) | 0.250–0.252 (0.51–0.52) |
| 3y | 0.310 | `vol_12m_rank` 0.451 (0.75); `vol_36m_rank` 0.424 (0.76) | 0.490 (0.75–0.76) |

The 1-year forest is below one volatility rank. The 3-year forest is
above every factor on PR-AUC and level at the top.

Predictions (config of 2026-10-01):

1. *1y PR-AUC 0.10 above base; p@20 ≥ 0.50 in most years and under
   0.30 in the calm years.* PR-AUC +0.114: held. p@20 ≥ 0.50 in 8 of
   16 years (seed 23), not "most"; in the six calm years 0.10–0.50
   (2016 0.10, 2012 and 2013 0.35, 2009 0.45, 2010 0.40, 2017 0.50):
   partly held.
2. *The top 20's mean 1y return negative in ≥ 12 of 16 years, ≥ 10%
   of them rise 30%.* Negative in exactly 12 (2005–07, 2010–15,
   2017–19); 19% rose 30% or more. Held. The four positive years are
   the short's disasters: 2008 entries +58% mean (median −36%), 2016
   +34%, 2020 +100% (median −11%).
3. *The count of rows at score ≥ 0.5 is highest for 2009–10 entries
   (lagging).* Contradicted, and so is the rival ("2007 above 2005–06
   by half"):

| entry year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1y, rows ≥ 0.5 | 408 | 205 | 147 | 52 | 19 | 46 | 56 | 58 | 73 | 122 | 70 | 65 | 35 | 7 | 1 | 4 |
| its precision | .32 | .40 | .50 | .75 | .47 | .39 | .64 | .40 | .29 | .31 | .74 | .12 | .46 | .57 | 1 | .50 |
| 3y, rows ≥ 0.5 | 2770 | 2244 | 1323 | 827 | 628 | 825 | 1032 | 1210 | 1095 | 1223 | 1189 | 893 | 858 | 1047 | 1045 | 1186 |

The count is highest when the training window is mostly 2000–02 and
falls as that crash becomes a smaller part of a growing window; it
does not move ahead of 2008 or 2020. Rival explanations: (a) the
training window's crash share (the reading above); (b) the market's
own state, which would make the count rise in 2007 (it fell). The
1-year counts against each fold's training base rate would separate
them; not run, because neither reading gives a usable signal.

**Concluded** (decision 39): no short leg (precision 0.5 at the top
with a fat right tail is not a short), and no cash rule from this
count.

## 2. Continuous growth models (research plan, item 1)

`lgbm_regressor_growth_allrows_3y`: LightGBM on every row, read inside
the 100k floor. 8 configurations (2 targets × 4 objectives), one seed.
Bars: the forest +0.030 / +0.027, losers 0.197 / 0.116; the candidate
+0.022 / +0.053. Rule (decision 34.3): lead ≥ forest + 0.01 in both
halves, losers ≤ forest + 0.03.

| target, objective | lead 05–12 | lead 13–20 | losers 05–12 | losers 13–20 | peers' losers | ≥15% CAGR |
|---|---|---|---|---|---|---|
| CAGR, huber | **+0.072** | **+0.054** | 0.394 | 0.372 | 0.47 / 0.45 | 0.35 / 0.28 |
| CAGR, q0.5 | +0.049 | +0.041 | 0.316 | 0.250 | 0.41 / 0.38 | 0.34 / 0.27 |
| CAGR, q0.25 | +0.030 | +0.026 | 0.250 | 0.178 | 0.35 / 0.33 | 0.33 / 0.21 |
| CAGR, q0.1 | +0.012 | +0.006 | 0.228 | 0.184 | 0.33 / 0.31 | 0.28 / 0.19 |
| excess, huber | +0.028 | +0.009 | 0.425 | 0.378 | 0.45 / 0.42 | 0.29 / 0.19 |
| excess, q0.5 | +0.025 | +0.006 | 0.350 | 0.362 | 0.40 / 0.40 | 0.32 / 0.23 |
| excess, q0.25 | +0.038 | +0.022 | 0.256 | 0.288 | 0.35 / 0.36 | 0.35 / 0.31 |
| excess, q0.1 | +0.019 | +0.013 | 0.256 | 0.253 | 0.33 / 0.33 | 0.31 / 0.26 |
| *forest (cell C)* | +0.030 | +0.027 | 0.197 | 0.116 | 0.33 / 0.26 | 0.37 / 0.32 |

Predictions (config of 2026-10-01):

1. *Low quantiles within 0.015 of the forest's lead, losers within
   0.05.* Lead: held for three of four (CAGR q0.1 is 0.018 / 0.021
   short). Losers: not held (CAGR q0.25 +0.053 / +0.062).
2. *Huber and median pick volatile stocks: losers 0.10 above the
   forest's, more big winners, a lead under the forest's for
   2013–20.* Losers: held (+0.20 / +0.26). More big winners: not held
   (≥15% CAGR 0.35 / 0.28 against 0.37 / 0.32). Lead under the
   forest's for 2013–20: **contradicted** for CAGR huber (+0.054)
   and median (+0.041); held for the excess-return target.
3. *No arm passes.* Held, on losers.

Why huber on CAGR leads, per year (lead / picks' median CAGR / losers,
forest beside it):

| year | huber lead | huber median | huber losers | forest lead | forest median | forest losers |
|---|---|---|---|---|---|---|
| 2005 | .120 | .085 | .35 | .002 | .023 | .38 |
| 2006 | .137 | −.073 | .65 | .005 | −.087 | .60 |
| 2007 | .026 | −.181 | .85 | .068 | .034 | .40 |
| 2008 | .028 | .006 | .48 | .043 | .102 | .15 |
| 2009 | .048 | .173 | .28 | .056 | .196 | .00 |
| 2010 | .064 | .128 | .23 | .040 | .153 | .03 |
| 2011 | .100 | .150 | .18 | .018 | .159 | .00 |
| 2012 | .052 | .142 | .15 | .012 | .142 | .03 |
| 2013 | .129 | .074 | .30 | .053 | .113 | .05 |
| 2014 | .099 | .066 | .38 | .075 | .120 | .08 |
| 2015 | .051 | .070 | .35 | .030 | .085 | .08 |
| 2016 | .074 | .114 | .20 | .024 | .133 | .13 |
| 2017 | .016 | −.020 | .53 | .047 | .131 | .15 |
| 2018 | −.015 | .010 | .45 | .004 | .122 | .05 |
| 2019 | .040 | .014 | .43 | −.011 | .100 | .15 |
| 2020 | .040 | .043 | .35 | −.002 | .065 | .25 |

Leakage checked first, as a lead this far above the forest requires:
same harness, the same `ranks` group and folds as every classifier;
the lead is in the mean while the median is *below* the forest's in
13 of 16 years and precision against peers is modest (0.44 / 0.38
against 0.36 / 0.35), which is the shape of right-skewed picks, not
of a label in the inputs. The huber model buys small, fragile stocks
(peers lose 45–47% of the time) whose winners carry the mean.

Why CAGR and excess differ so much although SPY's return is the same
for every stock of a date: open. Rivals: (a) the excess target's
date-level noise differs (snapshot dates within a quarter differ by
weeks, and SPY's 3-year return moves with them), so the two fits
learn different trees; (b) chance between two single-seed fits. Three
seeds of both would separate (b).

## 3. Worst rank of the candidate's three legs (research plan, item 3)

`blend_combine = "worst_rank"` (`claude/worst-rank`), the forest
bundle `53ceedd93e6d` with momentum and return on capital, same screen
as decision 33. One configuration.

| | lead 05–12 | lead 13–20 | losers | peers' losers | precision | ≥15% CAGR |
|---|---|---|---|---|---|---|
| worst rank | +0.043 | +0.056 | 0.259 / 0.150 | 0.335 / 0.288 | 0.606 / 0.738 | 0.391 / 0.428 |
| mean rank (candidate) | +0.022 | +0.053 | 0.275 / 0.153 | 0.331 / 0.280 | 0.578 / 0.766 | 0.328 / 0.412 |

Rule (decision 38): ≥ 0.032 / ≥ 0.063 with losers ≤ mean rank's
+ 0.03. Passes the first half, misses the second by 0.007: not carried
forward. Predictions: 1 (lead +0.01–0.04 / +0.03–0.06) held for
2013–20 and is just over for 2005–12; 2 (losers between the forest's
and the mean rank's) held; 3 (does not pass) held.

## 4. The forest blended with the huber regressor (decision 39)

The huber bundle refit unchanged (`233299a55d4c`, config
`7c1507e3f386652f`; its screen reproduced the sweep run's +0.072 /
+0.054 exactly). Two configurations.

| | lead 05–12 | lead 13–20 | losers | peers' losers | precision | ≥15% CAGR |
|---|---|---|---|---|---|---|
| forest × huber, worst rank | +0.028 | +0.017 | 0.266 / 0.244 | 0.355 / 0.327 | 0.622 / 0.694 | 0.306 / 0.203 |
| forest × huber, mean rank | +0.029 | +0.023 | 0.247 / 0.231 | 0.353 / 0.332 | 0.638 / 0.700 | 0.291 / 0.234 |
| forest alone | +0.030 | +0.027 | 0.197 / 0.116 | 0.327 / 0.263 | 0.706 / 0.825 | 0.366 / 0.319 |
| huber alone | +0.072 | +0.054 | 0.394 / 0.372 | 0.474 / 0.451 | 0.441 / 0.381 | 0.350 / 0.275 |

Rule: ≥ 0.040 / ≥ 0.063, losers ≤ 0.227 / ≤ 0.146. Both fail; every
prediction and the rival are contradicted (the blends are below both
legs). Worst rank's lead was negative for 2018, 2019 and 2020 entries
(−0.027, −0.068, −0.018). Reading and rival: decision 40.

## 5. Does the outcome rise with rank inside the forest's top 200? (decision 40)

`topk_buckets2_dv100k`: the forest bundle `53ceedd93e6d` inside the
100k floor, top K a year for K = 5 … 200; buckets from differences
(precision of ranks 11–50 = (50·p@50 − 10·p@10) / 40). One evaluation
(an earlier copy failed on parse and is logged).

| half | top 5 | top 10 | 11–20 | 21–50 | 51–100 | 101–200 | base | losers top 10 | losers 11–50 | losers 51–200 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2005–12 | 0.700 | 0.738 | 0.700 | 0.671 | 0.655 | 0.660 | 0.445 | 0.138 | 0.231 | 0.252 |
| 2013–20 | 0.825 | 0.862 | 0.838 | 0.783 | 0.810 | 0.780 | 0.411 | 0.075 | 0.147 | 0.153 |

Means of yearly values. The top 10 is purer than ranks 11–50 by
0.06 on precision and 0.07–0.09 on losers in both halves; below rank
20 the precision is flat to rank 200. The top 5 is not purer than the
top 10. Prediction (under 0.05 in a half) contradicted; rival (top 10
≥ 0.85 and steadily rising) half right: rising at the very top only.
Caution: 80 picks a half, about one standard error.

## 6. Two backtests from the buckets (decisions 41–42)

The forest alone, top N a month, at most 2 per sector, 100k floor,
35 bps, 2005–2020 valued to 2023; 37 backtest configurations on
these years with these two. Buys' 3-year lead over same-size
candidates (`vs_peers`, mean over the buy years of a half):

| | lead 05–12 | lead 13–20 | buys lost | peers lost | TWR | worst drawdown |
|---|---|---|---|---|---|---|
| top 10, equal (bar, `f84cc523`) | +2.68 | +3.27 | 24.6% / 10.8% | 34.6% / 25.6% | 10.01% | −46.6% |
| top 5, equal (`dfe4445f`) | +1.79 | +2.68 | 26.3% / 10.6% | 35.5% / 25.9% | 8.38% | −55.9% |
| top 10, score (`835bf888`) | +2.67 | +3.29 | 24.7% / 10.6% | 34.6% / 25.6% | 9.98% | −47.2% |

SPY with the same deposits: TWR 9.58%, worst drawdown −52.9%. Both
fail the rule; decision 42.
