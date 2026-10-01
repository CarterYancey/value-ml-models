# Selection inside large caps, and the screen read against same-size peers

Detail behind the [logbook](../logbook.md) entries of 2026-10-01 for
`forest_sector_nonloser_3y`, the `*_peers_dv100k` and `*_large`
evaluations, `baseline_factors_largecap_3y`,
`forest_largecap_cells_3y` and `lgbm_regressor_largecap_excess_3y`.
Decisions 31 to 34 of the [decision log](2026-09-29-decisions.md);
follows [the candidate outside 2005–2023](2026-10-01-out-of-sample.md).

3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`). Selection-biased by the
trial counts below; none is a result of record. Every figure is the
mean over test years of the yearly statistic.

## What ran, and how it was checked

- Code: `claude/screen-size-peers` (the screen's `peer_column`) and
  `claude/sector-feature`, merged into the lab branch. All runs of
  this note at git `88572e1`, except the four `*_peers_dv100k`
  evaluations of the candidate's bundles (`74c5637`; the commits
  between add notes, no code) and the sector sweep (`232457c` to
  `a8e29b9`, the code of `ad52395`).
- The screen: top 10 per test quarter, at most 2 per sector, 640 picks
  over 64 quarters. **Peers**: the test rows of the pick's quarter in
  its own 5% band of `log_marketcap_rank`; "lead" is the picks' mean
  `fwd_3y_excess_cagr` minus their peers' mean.
- The large-cap universe: `log_marketcap_rank >= 0.8`, trained and
  measured inside (scope "all") for the three sweeps; fold 2005 has
  53,478 train rows (effective 2,077) and fold 2020 204,240 (6,566),
  3,167 test rows a year on average. The evaluations of all-rows
  bundles inside it are scope "test".
- 9 forest fits, 21 single-factor runs and 6 LightGBM regressions
  inside large caps (36 hashes, 576 fold rows, none failed); 8
  evaluations of the candidate's seed-23 bundle and 6 of the sector
  sweep's bundles (14 hashes).
- Checks: the sector sweep's fs0 reproduces the candidate's forest on
  each seed (p@20 0.788 / 0.778 / 0.781, PR-AUC 0.585). The forest
  alone with peers inside the 100k floor has the screen precision and
  mean excess of `screen_dv100k` (0.766 and −0.001 over 16 years;
  0.706 / 0.825 and +0.018 / −0.019 by half). The three backtests
  re-run for their reference tables reproduce to the cent, and the
  fractional run's `vs_peers` by buy year equals the scratch
  diagnostic's (2021–23: −0.034, +0.011, −0.030).
- Trials after these runs (from the reports): cell C on all rows 87;
  inside the 100k floor 38; inside large caps 14; 154 in any universe.
  `label_3y_beat_spy` inside large caps 16 (63 in any universe).
  `fwd_3y_excess_cagr > 0 & fwd_3y_max_drawdown_from_entry < 0.3`
  inside large caps 10, its first.

## `sector` as a model input (decision 31)

Cell C, the candidate's forest, three seeds, all rows:

| | p@20 | PR-AUC | screen precision | screen mean excess | losers | utilities + real estate, share of picks | lead over peers, inside 100k: 2005–12 / 2013–20 |
|---|---|---|---|---|---|---|---|
| ranks (fs0), seeds 23 / 232 / 1776 | 0.788 / 0.778 / 0.781 | 0.585 | 0.766 / 0.759 / 0.758 | −0.000 / +0.004 / +0.004 | 0.164 / 0.163 / 0.167 | 0.348 / 0.350 / 0.342 | +0.030 / +0.027; +0.036 / +0.030; +0.034 / +0.028 |
| ranks + sector (fs1) | 0.766 / 0.756 / 0.772 | 0.585 | 0.764 / 0.762 / 0.747 | +0.003 / +0.003 / +0.002 | 0.169 / 0.158 / 0.167 | 0.342 / 0.341 / 0.342 | +0.035 / +0.026; +0.035 / +0.029; +0.034 / +0.026 |

The eleven sector indicators carry 0.9% of fs1's importance on each
seed (real estate 0.5%, utilities 0.4%, the other nine under 0.1%
together). All five predictions in the config held; the rival (the
two sectors' share falls under 0.20) is not supported.

## The candidate's bundles against same-size peers (decision 33)

Seed 23, the screen of decision 19 again with the peer column:

| | inside the 100k floor: screen precision (peers') 2005–12 / 2013–20 | lead over peers | losers (peers') | inside large caps: lead over peers | losers (peers') |
|---|---|---|---|---|---|
| forest alone | 0.71 (0.53) / 0.83 (0.60) | +0.030 / +0.027 | 0.20 (0.33) / 0.12 (0.26) | +0.030 / +0.028 | 0.17 (0.31) / 0.12 (0.26) |
| + return on capital | 0.68 (0.55) / 0.82 (0.59) | +0.021 / +0.058 | 0.23 (0.32) / 0.09 (0.27) | +0.022 / +0.047 | 0.24 (0.31) / 0.11 (0.26) |
| + momentum | 0.58 (0.52) / 0.68 (0.56) | +0.018 / +0.019 | 0.27 (0.33) / 0.22 (0.29) | +0.015 / +0.023 | 0.26 (0.31) / 0.19 (0.26) |
| + both (the candidate) | 0.58 (0.52) / 0.77 (0.58) | +0.022 / +0.053 | 0.28 (0.33) / 0.15 (0.28) | +0.038 / +0.047 | 0.23 (0.31) / 0.14 (0.26) |

Against all rows the same four screens lead by 0.071 / 0.106, 0.070 /
0.135, 0.058 / 0.084 and 0.066 / 0.124 inside the 100k floor: more
than half of every "lead over the average row" was size. Decision 33's
predictions held (forest +0.01 to +0.04; with return on capital 0.00
to +0.03 and +0.03 to +0.07; all three +0.02 to +0.06).

## Inside large caps: single factors, forests, a regression

Lead over same-size peers, entries of 2005–12 / 2013–20, and the
screen's losers (their peers': 0.31 to 0.32 / 0.24 to 0.29 in every
row).

| ranking | lead 2005–12 | lead 2013–20 | losers | big winners (CAGR ≥ 0.25) |
|---|---|---|---|---|
| **single factors** (the same picks in every cell) | | | | |
| highest return on capital | **+0.039** | **+0.030** | 0.22 / 0.19 | 0.20 / 0.14 |
| highest conservative score | **+0.031** | **+0.029** | 0.24 / 0.21 | 0.19 / 0.13 |
| lowest 36-month volatility | −0.011 | +0.020 | 0.22 / 0.08 | 0.02 / 0.02 |
| highest gross profitability | −0.017 | +0.040 | 0.39 / 0.27 | 0.17 / 0.26 |
| highest 3-year revenue growth | −0.010 | +0.017 | 0.41 / 0.32 | 0.23 / 0.19 |
| highest 12-month momentum | −0.033 | −0.033 | 0.44 / 0.46 | 0.21 / 0.18 |
| highest earnings yield | −0.052 | −0.031 | 0.40 / 0.38 | 0.16 / 0.10 |
| **forests trained inside large caps**, seeds 23 / 232 / 1776 | | | | |
| C, not a loser | +0.022 / +0.023 / +0.022 | +0.021 / +0.025 / +0.020 | 0.19–0.21 / 0.12–0.13 | 0.05–0.06 / 0.03 |
| S, beat SPY | +0.033 / +0.039 / +0.037 | +0.008 / +0.013 / −0.001 | 0.18–0.19 / 0.23–0.27 | 0.12–0.14 / 0.08–0.09 |
| CS, beat SPY without a 30% fall | +0.003 / +0.006 / +0.004 | +0.033 / +0.034 / +0.027 | 0.24–0.25 / 0.12–0.16 | 0.04–0.06 / 0.03–0.04 |
| **LightGBM on `fwd_3y_excess_cagr`** | | | | |
| huber | +0.020 / +0.024 / +0.016 | −0.024 / −0.036 / −0.026 | 0.28–0.31 / 0.33–0.35 | 0.15–0.18 / 0.08–0.09 |
| quantile 0.25 | +0.028 / +0.030 / +0.031 | +0.016 / +0.020 / +0.017 | 0.17–0.19 / 0.22–0.23 | 0.12–0.13 / 0.09–0.11 |
| **the all-rows bundles measured here** (table above) | | | | |
| the candidate's forest | +0.030 | +0.028 | 0.17 / 0.12 | 0.07 / 0.06 |
| the candidate (three legs) | +0.038 | +0.047 | 0.23 / 0.14 | 0.16 / 0.12 |

On their own labels, fold means over the 16 years: C p@20 0.78
against a base rate of 0.57, PR-AUC 0.676; S p@20 0.49 to 0.51
against 0.45, PR-AUC 0.48 (2013–20: p@20 0.43 against 0.37, PR-AUC
0.396); CS p@20 0.27 to 0.30 against a base rate of 0.35, PR-AUC
0.377. The regression arms on `label_3y_beat_spy`: PR-AUC 0.531 /
0.377 (huber) and 0.553 / 0.398 (quantile) in the two halves, base
rates 0.523 / 0.369.

## Against the rule and the predictions

The rule (decisions 32 and 33): a lead of 0.02 or more over same-size
peers in both periods on every seed, and 0.01 or more above the best
single factor's lead in both.

| arm | first condition | second (best single factor: return on capital, +0.039 / +0.030) | |
|---|---|---|---|
| forest C | met, at +0.020 to +0.025 | no: 0.016 to 0.017 and 0.005 to 0.010 *below* it | fails |
| forest S | no (2013–20: +0.008, +0.013, −0.001) | | fails |
| forest CS | no (2005–12: +0.003 to +0.006) | | fails |
| huber | no (2013–20 negative on every seed) | | fails |
| quantile 0.25 | no (2013–20: +0.016, +0.017 on two seeds) | | fails |

**No arm passes.** Predictions:

| | prediction | measured | matched? |
|---|---|---|---|
| forests 1 | C: base rate about 0.55; p@20 0.85 or more; PR-AUC 0.05 above the base rate; lead +0.01 to +0.03; losers under half the universe's | 0.57; 0.78; +0.10; +0.020 to +0.025; 0.16 to 0.17 against 0.30 | p@20 **no**; losers **no** (0.53 to 0.57 of the universe's); the rest yes |
| 2 | S: PR-AUC within 0.03 of its base rate; p@20 within 0.10 of it for 2013–20; lead within 0.015 of zero for 2013–20 | +0.035 over 16 years (+0.027 for 2013–20); +0.06; −0.001 to +0.013 | PR-AUC **no** by 0.005; the rest yes |
| 2, rival | S leads by 0.02 or more in both periods | 2013–20: at most +0.013 | not supported |
| 3 | CS: p@20 1.3 to 1.8 times its base rate; lead between S's and C's | 0.8 times; below both for 2005–12, above both for 2013–20 | **no** |
| 4 | no arm passes | none | yes |
| factors 1 | lowest volatility within 0.015 of zero in both | −0.011 / +0.020 | **no** for 2013–20 |
| 2 | return on capital and gross profitability +0.00 to +0.03 for 2013–20, smaller for 2005–12 | +0.030 and +0.040; +0.039 and −0.017 | **no** (return on capital is larger in 2005–12; gross profitability outside the range) |
| 3 | momentum negative in both; earnings yield negative for 2013–20; revenue growth within 0.02 of zero | −0.033 / −0.033; −0.031; −0.010 / +0.017 | yes |
| 4 | no factor leads by 0.02 in both periods | return on capital and the conservative score do | **no** |
| regression 1 | PR-AUC within 0.03 of the base rate; lead within 0.02 of zero for 2013–20 | +0.008 and +0.030; huber −0.024 to −0.036, quantile +0.016 to +0.020 | huber's lead **no** (worse than zero) |
| 2 | quantile: losers at most two thirds of the universe's; lead within 0.015 of the large-cap forest C's | 0.18 against 0.32 and 0.22 against 0.29; within 0.009 | losers **no** for 2013–20 |
| 3 | huber: losers within 0.05 of the universe's; more big winners than the quantile arm | within 0.06; more for 2005–12, fewer for 2013–20 | half |
| 4, rival | neither passes; the huber arm does not lead by 0.02 in both | as predicted | yes |

## Measured

1. **Making the sector visible to the forest changes nothing**: the
   same precision, return, losers and the same 34% of picks from
   utilities and real estate on every seed.
2. **Read against same-size peers, the forest's screen leads by 3
   points a year in both halves of 2005–2020** (+0.030 / +0.027; three
   seeds +0.027 to +0.036), with 0.20 / 0.12 of its picks losing money
   against 0.33 / 0.26 of their peers, and a precision of 0.71 / 0.83
   against the peers' 0.53 / 0.60. Against all rows it "led" by 7 and
   11 points.
3. **Inside large caps a model trained there does no better than the
   model trained on every row** (C: +0.022 / +0.021 against +0.030 /
   +0.028 for the all-rows forest measured on the same rows).
4. **The relative label is not learnable with size held fixed
   either.** Forests on "beat SPY" inside large caps: +0.033 to
   +0.039 for 2005–12 entries and −0.001 to +0.013 for 2013–20, a
   fold-mean PR-AUC 0.03 above the base rate. A regression on the
   size of the excess return is worse (−0.024 to −0.036 for 2013–20).
5. **Two single factors lead same-size peers by 3 points a year in
   both halves, as much as any model**: return on capital (+0.039 /
   +0.030) and the conservative score (+0.031 / +0.029), with about
   three times the forest's big winners and a third to a half more
   losers.
   Lowest volatility alone has the fewest losers and no lead in
   2005–12.
6. **What the forest adds to a quality factor is fewer losers, not
   more return**: return on capital alone 0.22 / 0.19 losers, the
   forest with it 0.24 / 0.11, the forest alone 0.17 / 0.12; leads
   +0.039 / +0.030, +0.022 / +0.047, +0.030 / +0.028.
7. **Momentum and cheapness lose to same-size peers inside large
   caps in both halves** (−0.033 / −0.033; −0.052 / −0.031).

## What it might mean (hypotheses)

- *The feature set ranks risk and one quality factor, and that is all
  it ranks.* Every arm that leads its peers does so by 2 to 4 points,
  whether it is a 490-tree forest, a regression or one column, and
  the columns that do it are return on capital and low volatility.
  A target that asks for more (beat the index; beat it safely) is not
  learned better with size fixed. Rival: the forest configuration was
  tuned on every row and on cell C, and LightGBM's parameters were not
  searched at all; a search inside large caps could find more. The
  three searches of 2026-09-29 moved fold-mean PR-AUC by 0.005 in
  cell C, which is why none was run here.
- *The 3 points are in-sample.* For the buys of 2021–23 the same
  kinds of picks led same-size peers by about zero
  ([out-of-sample note](2026-10-01-out-of-sample.md): forest +0.006,
  with return on capital +0.005, all three −0.016; return on capital
  alone −0.034 against +0.034 / +0.010 before). Three cohorts.

## What follows

Decision 34. No new model goes to a backtest and none is run on
2021–26. What the models reliably deliver is fewer losers at about
the return of same-size stocks; what would add return is not in
these columns.
