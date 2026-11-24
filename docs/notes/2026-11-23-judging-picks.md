# Judging picks, not the market: crash years, worst rank in money, a "came back" label (2026-11-23, third round)

Carter's correction after decision 49 is recorded in decision 50 of the
[decision log](2026-09-29-decisions.md). In short: judge how the picks
did, crash years included, and carry forward gains measured against
noise rather than gains that clear a bar set beforehand. This note reads
three runs under that correction. `dataset_v1.4`, walk-forward test
years 2005–2020, the 100k floor, and the screen and same-size peers of
[the first round](2026-11-23-crash-growth-worst-rank.md).
Paired figures come from per-year differences: the mean, its standard
error (se), and the years ahead out of 16. The 3-year windows of
adjacent years overlap, so the se is a lower bound.

## 1. The crash years, judged by the picks

These come from the screens already on disk (top 10 a quarter, at most
2 per sector), read against same-size peers.

| entries | cell-C forest: picks' 3y max drawdown | peers' | picks lost money | peers lost | lead (3y excess CAGR) |
|---|---|---|---|---|---|
| 2007 | 0.46 | 0.57 | 0.40 | 0.60 | +0.068 |
| 2008 | 0.33 | 0.49 | 0.15 | 0.33 | +0.043 |

The forest's picks were the resilient ones in the crash years. Cell C's
precision of 0.17–0.21 for those entries comes from the label's
drawdown leg, which a market-wide fall of more than 30% fails.
`year_calib_corr` stays in reports but is no longer a gate (decision
50).

## 2. worst_rank against mean_rank, three seeds

Screen (`vml-eval`, the candidate's three legs, paired worst minus
mean):

| forest seed | lead diff a year | se | worst ahead | losers diff |
|---|---|---|---|---|
| 23 | +0.0114 | 0.0055 | 11/16 | −0.009 |
| 232 | +0.0065 | 0.0058 | 12/16 | −0.002 |
| 1776 | +0.0105 | 0.0063 | 12/16 | −0.008 |

Money: the candidate's backtest (rank floor 0.2, top 10 a month, at
most 2 per sector, 35 bps, buys 2005–2020 valued to 2023). Every row
ran at git `cfa451c`.

| forest seed | mean rank TWR | worst rank TWR | diff | drawdown mean / worst | buys' 3y vs_peers mean / worst | buys lost mean / worst |
|---|---|---|---|---|---|---|
| 23 | 11.90% | 11.32% | −0.58 | −40.3% / −45.0% | +5.31 / +6.35 | 20.7% / 21.7% |
| 232 | 12.12% | 11.38% | −0.74 | −40.4% / −44.0% | +5.37 / +6.01 | 20.6% / 21.6% |
| 1776 | 12.23% | 11.49% | −0.74 | −40.5% / −44.9% | +5.20 / +6.23 | 21.6% / 21.6% |

SPY: 9.58%, −52.9%.

The worst rank's buys beat same-size stocks by 0.6 to 1.0 points a
year more. On seed 23 it was ahead in 13 of 16 buy years, and the sign
held on all three seeds. Yet the portfolio earned 0.6 to 0.7 points a
year less, with a drawdown 4 to 5 points deeper. That gap is larger
than the spread across seeds of the mean rank's TWR (0.33). Every
prediction in the configs held on direction: TWR within −1.0 to +0.3
and buys higher. The first config's prediction did not hold: TWR within
−0.5 to +1.5 of 12.15%.

**Measurement:** a better 3-year selection against peers, and less
money, on every seed. **Hypotheses, not tested:**

- The worst rank buys slightly smaller stocks (peers' excess −3.2
  against −2.9).
- Buy and hold keeps positions to 2023, past the screen's 3-year
  window.
- The deeper fall in 2008 compounds.

Nothing here separates these hypotheses.

**Not traced: the candidate on current code.** The same config
(`6005c9c0a2869bc9`) gives TWR 11.90% and 1,742 buys at git `cfa451c`,
against 12.15% and 1,747 buys at git `f96037d`. The old report is kept.
The rerun is in `reports/backtest_rerun_d50/`. Every comparison above
uses the new code on both sides.

## 3. The "came back" label: `label_3y_cagr_ge_0` (`forest_cagr_ge0b_3y`)

This is the candidate forest's configuration on the new label: seed 23,
112 ranks. `forest_cagr_ge0_3y` failed on validation first, because a
sed overwrote its model name. The corrected copy ran.

| screen (paired against cell C's forest, same mode) | lead 05–12 / 13–20 | losers | lead diff (se, ahead) | losers diff |
|---|---|---|---|---|
| alone | +0.043 / +0.027 (C: +0.030 / +0.027) | 0.212 / 0.116 (C: 0.197 / 0.116) | +0.0064 (0.0065, 8/16) | +0.008 |
| candidate blend, mean rank | +0.036 / +0.055 (C: +0.022 / +0.053) | 0.244 / 0.159 | +0.0075 (0.0044, 10/16) | −0.013 |
| candidate blend, worst rank | +0.042 / +0.049 (C: +0.043 / +0.056) | 0.269 / 0.175 | −0.0039 (0.0046, 4/16) | +0.017 |

The picks' mean 3-year drawdown was 0.207 / 0.130 in each half, against
cell C's 0.208 / 0.134.

Predictions:

- Prediction 1 (lead +0.02 to +0.05) held.
- Prediction 2 (losers within 0.03) held.
- Prediction 3 (drawdown 0 to +0.05 higher) held, at 0.
- The rival was rejected: losers did not rise.

**Reading:** dropping the drawdown leg barely changes the picks. The
forest learns "calm" from "the price came back" as well. The gain in
the mean-rank blend is about 1.7 se, ahead in 10 of 16 years. That is
on the edge of decision 50's rule, so it is open, and seeds come
before a backtest.

## 4. The "came back" label on three seeds and in money (decisions 52–53)

Screen, paired against cell C's forest of the same seed (the 100k
floor, top 10 a quarter):

| seed | alone: lead diff (se, ahead) | losers diff | mean-rank blend: lead diff (se, ahead) | losers diff |
|---|---|---|---|---|
| 23 | +0.0064 (0.0065, 8/16) | +0.008 | +0.0075 (0.0044, 10/16) | −0.013 |
| 232 | +0.0002 (0.0048, 9/16) | +0.023 | +0.0030 (0.0033, 11/16) | −0.005 |
| 1776 | +0.0041 (0.0060, 8/16) | +0.005 | +0.0058 (0.0048, 11/16) | −0.017 |

In the blend the gain has the same sign on every seed, about +0.005 a
year, but on no seed does it reach 2 se.

Backtests: the candidate's config with the forest leg swapped. All
rows ran on identical `src/`: candidate at git `cfa451c`, new label at
`a2ffb07`, docs-only commits between.

| seed | candidate TWR / MWR / final / drawdown | came back TWR / MWR / final / drawdown |
|---|---|---|
| 23 | 11.90% / 13.72% / 940,542 / −40.3% | 12.49% / 13.68% / 935,847 / −43.6% |
| 232 | 12.12% / 13.84% / 953,815 / −40.4% | 12.25% / 13.63% / 930,706 / −43.3% |
| 1776 | 12.23% / 13.76% / 944,611 / −40.5% | 12.76% / 13.88% / 958,928 / −43.0% |

The TWR is higher on all three seeds (+0.59 / +0.13 / +0.53, mean
+0.42). The money is not: money-weighted return −0.04 / −0.21 / +0.12,
and final value −4.7k / −23.1k / +14.3k. The drawdown is about 3
points deeper on every seed (2008: −24.6% against −22.1% on seed 23).
On seed 23 the TWR gain sits in 2005–07 (+5.4, +2.1, +6.7 points a
year), when the account held a few tens of thousands. TWR weights
those years like any other; money hardly does. Across 2008–2023 the
two alternate year by year.

Decision 52's rule:
- TWR above on 2 or more seeds: passed (3 of 3).
- Mean gap larger than the seed spread: passed, barely (0.42 against
  0.33).
- Drawdown no more than 2 points deeper: failed (about 3).
- Screen at about 2 se: failed on every seed.

Predictions:
- Screen +0.003 to +0.010: held.
- TWR within ±0.4: contradicted on two seeds.
- Does not pass: held.
- The rival (compounds to more than +0.4) held on TWR and failed on
  money.

## Correction (2026-11-24): the dataset rebuild (decision 54)

In §2 and §3, the seed-23 mean-rank blend and cell C screens were
reports from 2026-10-01, scored on the v1.4 build from before the
rebuild. Rerun on the rebuild (`reports/rerun_dataset_rebuild/`):

| paired comparison | as written | on the rebuild |
|---|---|---|
| worst minus mean rank, seed 23 | +0.0114 (11/16) | +0.0126 (se 0.0055, 11/16) |
| "came back" alone minus cell C, seed 23 | +0.0064 (8/16) | +0.0047 (se 0.0051, 7/16) |
| "came back" blend minus cell C blend, seed 23 | +0.0075 (10/16) | +0.0086 (se 0.0042, 12/16) |

Seeds 232 and 1776 and every backtest ran on the rebuild on both
sides. Section 2's "untraced" difference in the candidate's TWR (12.15%
to 11.90%) is the rebuild.
