# Second rankings on the screen, the screen against the backtests, and calibration

Detail behind the [logbook](../logbook.md) entries of 2026-09-30 for
the blend evaluations, `forest_winner15_fs4_dv100k_3y`,
`factor_net_payout_yield_3y` and the two calibrated runs. Decisions 19
to 21 of the [decision log](2026-09-29-decisions.md).

3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`), cell C
(`fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`), inside
the universe `dollar_volume_3m >= 100000`. One forest seed (23).
Selection-biased by the trial counts below; none is a result of
record.

## What ran, and how it was checked

- Blends: `vml-eval` of the candidate's forest bundle (run
  `53ceedd93e6d`) with `blend = [...]` (code:
  `claude/eval-blend`), each model's scores ranked within the test
  quarter as a share of the quarter's rows and the shares averaged.
  Seven blends and the forest alone, 8 config hashes, 16 fold rows
  each, git `1f0f79b` (the first four) and `5a3065d`.
- New bundles: `factor_net_payout_yield_3y` (run `d3139b8ade6d`),
  `forest_winner15_fs4_dv100k_3y` (run `fef335d5be51`, 151 columns,
  trained inside the floor).
- Calibration: `forest_nonloser_dd30_isotonic_3y` (run `71477d2fcce6`,
  git `1f0f79b`, **not to be read**: see below) and
  `forest_nonloser_dd30_isotonic_lag_3y` (run `dbecfe43f31a`, git
  `5a3065d`, after the fix). The second has the uncalibrated run's
  p@20 0.7875 and fold-mean PR-AUC 0.5854.
- The screen's forest-alone row equals the evaluation of the all-rows
  fs0 bundle inside the floor (the same fit under another name):
  precision 0.766, mean excess −0.001.
- Trials after these runs: cell C on all rows 80; inside 100k 23;
  inside 1m 15. The backtest `bt_nonloser_roc_top10_cap2` was run
  again on the merged code and reproduced to the cent (694,944.59,
  time-weighted 9.648%, drawdown −41.16%): the same config hash, no
  new configuration.

## The blends on the screen

Top 10 per test quarter, at most 2 per sector, 640 picks; mean over
test years of the yearly statistic.

| blend with cell C's forest | screen precision | beat SPY | mean excess | median excess | losers | deep drawdown | big winners | stocks a year |
|---|---|---|---|---|---|---|---|---|
| none (the forest alone) | 0.766 | 0.511 | −0.001 | +0.006 | 0.156 | 0.120 | 0.061 | 24.0 |
| 12-month momentum (the candidate) | 0.633 | 0.458 | −0.018 | −0.011 | 0.244 | 0.211 | 0.094 | 32.5 |
| **return on capital** | 0.753 | **0.581** | **+0.014** | +0.023 | 0.162 | 0.125 | 0.108 | 19.6 |
| earnings yield | 0.602 | 0.411 | −0.030 | −0.027 | 0.283 | 0.256 | 0.088 | 24.1 |
| n1: momentum + net payout yield | 0.619 | 0.495 | −0.010 | −0.001 | 0.262 | 0.250 | 0.145 | 29.9 |
| n2: momentum + return on capital | 0.672 | 0.550 | +0.006 | +0.018 | 0.214 | 0.175 | 0.153 | 28.9 |
| n3: the learned upside model | 0.645 | 0.397 | −0.031 | −0.024 | 0.256 | 0.248 | 0.064 | 26.9 |
| n4: momentum + the upside model | 0.556 | 0.428 | −0.037 | −0.020 | 0.294 | 0.289 | 0.086 | 32.9 |

Mean excess by entry period:

| | 2005–12 | 2013–20 |
|---|---|---|
| forest alone | +0.018 | −0.019 |
| momentum | +0.004 | −0.040 |
| return on capital | +0.016 | +0.011 |
| earnings yield | +0.002 | −0.062 |
| n1 | +0.017 | −0.037 |
| n2 | +0.013 | −0.001 |
| n3 | −0.014 | −0.048 |
| n4 | −0.014 | −0.061 |

The factors and the upside model alone, same screen: net payout yield
precision 0.20, losers 0.63, mean excess −0.22; the upside forest
(`fwd_3y_cagr >= 0.15`) p@20 0.29 against a base rate of 0.27,
fold-mean PR-AUC 0.289, losers 0.40, mean excess −0.08.

## The check of the screen (decision 19)

| blend | its backtest, time-weighted, against the forest alone | predicted on the screen | measured | |
|---|---|---|---|---|
| momentum | +1.3 points a year (three seeds: +1.2 to +2.4) | above the forest by 0.01 or more | 0.017 **below** | **failed** |
| return on capital | −0.1 | within 0.01 | 0.015 above | failed by 0.005 |
| earnings yield | −2.0 | below by 0.01 or more | 0.029 below | held |

So the screen did not order the three as time-weighted return did.

## Reading the backtests one buy at a time

To see which instrument the disagreement belongs to, the four
backtests' own buys were read from their trade logs and the price
panel (`prices_v1.0`): for each buy, the return over the three years
after the trade date against SPY's over the same dates, annualized. A
stock that stopped printing exits at its final print; in the second
column its proceeds stay in cash to the horizon (the dataset's label
convention), in the third they ride SPY (what a portfolio that
reinvests gets). A scratch analysis on 2026-09-30, since built into
the backtest report (`claude/backtest-buy-outcomes`); the chain of
re-runs that follows puts the same table in every report.

| backtest (cap 2 per sector) | buys | exit before 3y | mean excess a year, cash after exit | proceeds in SPY | buys of 2005–12 | buys of 2013–20 | 1-year excess, total | final value | time-weighted | money-weighted |
|---|---|---|---|---|---|---|---|---|---|---|
| forest alone | 1,847 | 0.053 | +0.000 | +0.001 | +0.013 | −0.011 | +0.013 | 633,757 | 9.74% | 10.40% |
| + momentum | 1,783 | 0.113 | −0.002 | +0.005 | +0.025 | −0.016 | +0.011 | 711,494 | 11.07% | 11.38% |
| + return on capital | 1,783 | 0.032 | +0.012 | **+0.013** | **+0.013** | **+0.012** | +0.029 | 694,945 | 9.65% | 11.18% |
| + earnings yield | 1,850 | 0.084 | −0.033 | −0.032 | −0.007 | −0.057 | −0.009 | 493,413 | 7.76% | 8.28% |
| SPY, same deposits | | | | | | | | 732,110 | 9.58% | 11.62% |

The two period columns are with proceeds in SPY.

## Why the screen and the momentum backtest differ

Measured on the screen's picks (rebuilt from the bundles,
`scratchpad/diag_blend.py`, no fit):

| | picks delisted inside 3 years | of which acquisitions | their mean excess | the others' | 1-year mean excess |
|---|---|---|---|---|---|
| forest alone | 0.070 | 40 of 45 | −0.028 | +0.001 | +0.008 |
| + momentum | 0.148 | 90 of 95 | −0.051 | −0.013 | −0.008 |
| + return on capital | 0.033 | 21 of 21 | +0.000 | +0.014 | +0.024 |
| + earnings yield | 0.084 | 51 of 54 | −0.010 | −0.032 | −0.020 |

1. **The label convention counts an acquisition as dead money.** The
   dataset carries a delisted stock's final price flat to the horizon
   (upstream decision 0002), so a stock bought out three months after
   the snapshot has a 3-year "CAGR" of a third of its premium and an
   excess near minus SPY's return. A portfolio gets the cash back.
   Calm stocks with high 12-month momentum are often takeover targets
   (findings, factor-combinations note): 15% of the momentum blend's
   screen picks against 7% of the forest's. In the momentum backtest
   134 positions ended in a delisting, with a mean total return of
   +79% and a median of +39%; 33 of them within ±10% of cost, bought
   a median three months before the delisting.
2. **That is about a third of the gap.** With its acquired picks at
   the other picks' mean the momentum blend would be at −0.013, still
   0.014 below the forest alone; on 1-year outcomes it is 0.015
   below.
3. **The rest is not explained.** The backtest buys one to six months
   after the snapshot the screen enters at, from a cross-section
   ranked on the same stale momentum; per buy from the trade date the
   momentum blend is 0.004 a year *above* the forest alone (proceeds
   in SPY), not 0.017 below. Entry timing is the difference that is
   left; it has not been tested.

## Measured

1. **Per buy, return on capital is the second ranking that helps,
   and the only one that helps in both halves**: +0.013 a year over
   SPY for the buys of 2005–12 and +0.012 for 2013–20, on the
   backtest's own buys; +0.016 and +0.011 on the screen. Its picks
   keep the forest's losers (0.162 against 0.156) and have nearly
   twice its big winners (0.108 against 0.061).
2. **Momentum's lead was a time-weighted figure.** Per buy it is
   +0.005 a year against the forest alone's +0.001, +0.025 for the
   buys of 2005–12 and −0.016 for 2013–20. Time-weighted return
   gives 2005–11, when the portfolio was small and young, the weight
   of the years after; the criterion of decision 8 was written on it.
   In money the momentum portfolio still ends highest of the four
   (711,494), 2% above the quality blend and 3% below SPY.
3. **No portfolio so far has more money than SPY at the end** on
   seed 23; per buy the quality blend is ahead of SPY over each buy's
   first three years. The portfolios hold what they bought for up to
   eighteen years.
4. **A model of who compounds at 15% a year has no skill** from the
   151 columns without risk ranks (p@20 0.29, base rate 0.27), and
   blending it with the forest makes the picks worse than the forest
   alone.
5. **The three-way blends sit between their parts.** Momentum with
   return on capital: +0.006, between −0.018 and +0.014.

## Calibration

`forest_nonloser_dd30_isotonic_3y` was run to read selection by
confidence. Its report did not match the first prediction in its
config (p@20 as in the uncalibrated run): 0.650 against 0.788. Two
defects, both in `harness/calibration.py`, both fixed on
`claude/calibration-label-lag` (incident in
[process issues](process-issues.md)):

- **The calibrator used outcomes from the future.** Fold Y was
  calibrated on the predictions and outcomes of every earlier fold.
  The 3-year outcome of a 2007 snapshot is known in 2010; the 2008
  entries were calibrated on it. In that run no 2008 or 2009 row
  scored 0.5 or more. A fold now uses only folds whose outcomes were
  complete before its year began (fold Y: folds up to Y−4).
- **Isotonic steps tied the top of the ranking**, so a top 20 was the
  first 20 rows of the top step. Rows on a step now keep their raw
  order.

After the fix (`forest_nonloser_dd30_isotonic_lag_3y`; folds 2005–08
raw, 2009–20 calibrated):

| entry year | rows at calibrated 0.5 or more | their precision | at 0.6 or more | their precision | top 20, precision |
|---|---|---|---|---|---|
| 2009 | 11,769 of 16,575 | 0.68 | 7,642 | 0.77 | 0.90 |
| 2010 | 3,087 | 0.87 | 0 | | 1.00 |
| 2011–13 | 0 | | 0 | | 1.00, 1.00, 0.95 |
| 2014 | 1,439 | 0.83 | 0 | | 0.90 |
| 2015 | 3,698 | 0.73 | 0 | | 1.00 |
| 2016 | 5,890 | 0.74 | 0 | | 0.90 |
| 2017 | 6,600 | 0.48 | 0 | | 0.80 |
| 2018 | 6,548 | 0.39 | 0 | | 0.90 |
| 2019 | 6,255 | 0.31 | 3,715 | 0.35 | 0.65 |
| 2020 | 6,470 | 0.55 | 4,139 | 0.58 | 0.70 |

Brier, fold mean: calibrated 0.2266, uncalibrated 0.2148, the
no-skill reference 0.2200; the calibrated run beats the reference in
8 of 16 years, the uncalibrated in 11.

Against the predictions of the second config: p@20 and PR-AUC as
uncalibrated, held. "`score >= 0.7` selects 2019 rows with a precision
under 0.6": no row reaches 0.7 after 2008; at 0.6 the 2019 rows have
0.35. "Rows at a calibrated 0.8 have a precision of 0.70–0.90 over
2009–20": there are none. "0.8 is met in fewer than half of those
years": in none.

**Measured:** an honest calibrator for a 3-year label is four years
behind, and its probabilities follow the regime of four years
before. It gave no row a probability of 0.5 in 2011–13, when the top
20 were right 95% to 100% of the time (its history was the 2005–09
entries), and 0.5 or more to 42–44% of all rows in 2017–19 at a
precision of 0.31–0.48 (its history then reached the 2013–15
entries). It makes Brier
worse than no calibration. The top 20 by rank are right far more
often than any threshold's selection in every calibrated year.

**What it means for selection by confidence.** For this label an
absolute confidence bar, calibrated or not, is a late market-timing
rule, and holding cash when nothing clears it would have kept the
portfolio out of 2011–13. Selection stays by rank within the period.
A shorter label shortens the calibrator's lag (two folds for a
1-year label): that is one of the reasons for the 1-year cell of
decision 22.
