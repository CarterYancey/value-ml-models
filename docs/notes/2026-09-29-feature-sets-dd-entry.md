# Feature sets in the from-entry compounder cell

Detail behind the [logbook](../logbook.md) entry for
`forest_feature_sets_dd_entry_3y`, read 2026-09-29.

Cell: `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2`, 3y,
`dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`). 64 configurations tried in
the cell after this sweep (34 before it). The numbers are
selection-biased by that count and none is a result of record.

## What ran, and how it was checked

- The sweep ran on the host, by hand, at git `00ba3ec`; sweep identity
  `bffc9fd4`. Read from the host's report directory
  (`reports/sweeps/forest_feature_sets_dd_entry_3y/`) and the host's
  ledger (`experiments/results.csv`).
- 30 runs, 0 failed. The 30 config hashes of the summary CSV are all
  in the ledger: 480 fold rows, 16 per hash, no duplicates, all
  `completed`, all `dataset_v1.4`, all this label.
- The reference arm was not re-run. It is the six class-weight-1.0
  runs of `forest_drawdown_compounder_seeds_3y` (git `86ef0c4`),
  matched by config hash from that sweep's summary CSV: the same two
  parameter sets and the same seeds (23, 232, 1776).

Differences between the sweep and its reference:

| | reference | this sweep |
|---|---|---|
| git SHA | `86ef0c4` | `00ba3ec` |
| dataset | `dataset_v1.4` | `dataset_v1.4` |
| parameters, seeds | set0, set1; 23, 232, 1776 | the same |
| rows per fold (mean) | train 702,905, Σ `sample_weight_3y` 25,545, test 16,022 | identical |
| base rate (fold mean) | 0.2074 | identical |
| columns | 112 (`ranks`) | by arm, below |

The git SHA differs and the reference was not re-run at `00ba3ec`, so
a code change between the two is not excluded by this sweep. It is
made unlikely by arm fs3, which has the reference's 112 columns plus
13 and reproduces its PR-AUC to 0.0006 in both parameter sets, and by
the forest memory check of 2026-09-28, which reproduced the reference
fold rows exactly at `feb0b55`.

Resolved columns, from each run's `*_config.json`:

| arm | spec | columns | against the reference's 112 |
|---|---|---|---|
| fs0 | ranks minus `ranks/technical` | 97 | 15 removed |
| fs1 | `ranks/technical` alone | 15 | 97 removed |
| fs2 | ranks minus three columns | 109 | `vol_12m_rank`, `vol_36m_rank`, `conservative_score_rank` removed |
| fs3 | ranks + sector ranks | 125 | 13 `*_secrank` columns added |
| fs4 | ranks + raw technical + raw trend | 172 | 60 added: 15 raw technical, 45 raw trend |

The 15 technical ranks: `mom_12_2`, `mom_36_12`, `ret_6m`, `ret_1m`,
`max_ret_21d`, `vol_12m`, `vol_36m`, `beta_12m`, `dist_52w_high`,
`dist_5y_high`, `price_vs_5y_avg`, `log_marketcap`,
`dollar_volume_3m`, `amihud_12m`, `conservative_score` (each
`_rank`).

## A trap in the summary: pooled PR-AUC

The sweep summary's `pr_auc` is computed over the pooled test rows of
all years (0.24–0.27 for every arm). The reference figure in the
config, 0.327, is the mean of the 16 per-fold PR-AUCs. The two are
not comparable: the reference's own pooled PR-AUC is 0.274–0.275.
Every PR-AUC below is the fold mean, from the ledger's fold rows.
p@20 picks per year, so its pooled value and its fold mean are the
same number.

## Results

Seed-mean fold-mean. "Worst" is the lowest seed. "Crash" is the mean
over entry years 2005–08 and 2019. "Years" counts test years in which
the seed-mean p@20 beat the base rate; "Brier yrs" is the number of
years Brier beat `base_rate_brier`, averaged over seeds.

| arm | set | p@20 | seed std | worst | 2005–12 | 2013–20 | 2013–20 worst | 2009–18 | crash | p@50 | PR-AUC | PR-AUC 2013–20 | years | Brier yrs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| reference (112) | 0 | 0.499 | 0.016 | 0.481 | 0.454 | 0.544 | 0.538 | 0.685 | 0.143 | 0.488 | 0.3273 | 0.3255 | 14 | 9.3 |
| reference (112) | 1 | 0.500 | 0.016 | 0.491 | 0.465 | 0.535 | 0.513 | 0.705 | 0.107 | 0.479 | 0.3267 | 0.3241 | 14 | 10.0 |
| fs3, + sector ranks | 0 | 0.493 | 0.005 | 0.488 | 0.463 | 0.523 | 0.513 | 0.670 | 0.153 | 0.481 | 0.3266 | 0.3246 | 14 | 9.0 |
| fs3, + sector ranks | 1 | 0.499 | 0.007 | 0.494 | 0.467 | 0.531 | 0.525 | 0.705 | 0.107 | 0.485 | 0.3267 | 0.3240 | 15 | 10.0 |
| fs1, technical alone | 0 | 0.457 | 0.008 | 0.450 | 0.404 | 0.510 | 0.494 | 0.657 | 0.060 | 0.464 | 0.3220 | 0.3200 | 12 | 9.0 |
| fs1, technical alone | 1 | 0.456 | 0.005 | 0.453 | 0.383 | 0.529 | 0.519 | 0.663 | 0.050 | 0.453 | 0.3222 | 0.3192 | 12 | 9.7 |
| fs4, + raw tech, trend | 0 | 0.454 | 0.014 | 0.438 | 0.425 | 0.483 | 0.456 | 0.650 | 0.080 | 0.438 | 0.3125 | 0.3201 | 14 | 10.0 |
| fs4, + raw tech, trend | 1 | 0.444 | 0.008 | 0.434 | 0.402 | 0.485 | 0.475 | 0.643 | 0.070 | 0.425 | 0.3153 | 0.3179 | 13 | 9.3 |
| fs0, no technical | 0 | 0.416 | 0.011 | 0.403 | 0.402 | 0.429 | 0.406 | 0.600 | 0.093 | 0.390 | 0.3123 | 0.3037 | 11 | 9.0 |
| fs0, no technical | 1 | 0.397 | 0.008 | 0.388 | 0.421 | 0.373 | 0.356 | 0.553 | 0.100 | 0.376 | 0.3112 | 0.3021 | 12 | 9.0 |
| fs2, no vol, no score | 0 | 0.390 | 0.021 | 0.372 | 0.377 | 0.402 | 0.375 | 0.570 | 0.070 | 0.393 | 0.3052 | 0.2962 | 11 | 9.0 |
| fs2, no vol, no score | 1 | 0.388 | 0.011 | 0.381 | 0.398 | 0.377 | 0.363 | 0.557 | 0.083 | 0.387 | 0.3093 | 0.3002 | 11 | 9.0 |
| `conservative_score_rank` | | 0.388 | | | 0.356 | 0.419 | | 0.560 | 0.100 | 0.392 | 0.301 | | | |
| base rate | | 0.207 | | | 0.216 | 0.199 | | 0.261 | 0.097 | | | | | |

PR-AUC seed std is 0.0000–0.0008 in every arm. PR-AUC beats the base
rate in all 16 years in every arm.

PR-AUC against the reference with the same parameter set, per test
year (seed means):

| arm | set0 mean difference | years lower / higher | set1 mean difference | years lower / higher |
|---|---|---|---|---|
| fs3 | −0.0004 | 5 / 3 | +0.0002 | 4 / 6 |
| fs1 | −0.0052 | 14 / 1 | −0.0044 | 11 / 4 |
| fs4 | −0.0145 | 13 / 2 | −0.0113 | 13 / 0 |
| fs0 | −0.0147 | 13 / 3 | −0.0155 | 13 / 3 |
| fs2 | −0.0219 | 13 / 3 | −0.0172 | 14 / 1 |

(Years not counted are equal at the rounding used, three decimals.)

p@20 by test year, seed means:

| year | base | ref s0 | ref s1 | fs3 s0 | fs3 s1 | fs1 s0 | fs1 s1 | fs4 s0 | fs4 s1 | fs0 s0 | fs0 s1 | fs2 s0 | fs2 s1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2005 | 0.21 | 0.03 | 0.22 | 0.05 | 0.22 | 0.08 | 0.12 | 0.03 | 0.13 | 0.42 | 0.48 | 0.20 | 0.37 |
| 2006 | 0.09 | 0.22 | 0.15 | 0.23 | 0.13 | 0.00 | 0.00 | 0.18 | 0.10 | 0.00 | 0.00 | 0.10 | 0.00 |
| 2007 | 0.04 | 0.23 | 0.03 | 0.28 | 0.12 | 0.00 | 0.00 | 0.05 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2008 | 0.05 | 0.23 | 0.12 | 0.20 | 0.07 | 0.22 | 0.13 | 0.10 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2009 | 0.36 | 0.83 | 0.88 | 0.82 | 0.87 | 0.72 | 0.62 | 0.83 | 0.83 | 0.88 | 0.92 | 0.72 | 0.83 |
| 2010 | 0.32 | 0.77 | 0.73 | 0.77 | 0.78 | 0.78 | 0.68 | 0.80 | 0.73 | 0.73 | 0.72 | 0.73 | 0.73 |
| 2011 | 0.27 | 0.70 | 0.75 | 0.73 | 0.75 | 0.65 | 0.72 | 0.67 | 0.73 | 0.48 | 0.62 | 0.52 | 0.65 |
| 2012 | 0.37 | 0.62 | 0.83 | 0.62 | 0.80 | 0.78 | 0.80 | 0.73 | 0.60 | 0.70 | 0.63 | 0.75 | 0.60 |
| 2013 | 0.28 | 0.55 | 0.58 | 0.52 | 0.57 | 0.68 | 0.72 | 0.52 | 0.43 | 0.63 | 0.60 | 0.53 | 0.47 |
| 2014 | 0.21 | 0.68 | 0.65 | 0.73 | 0.67 | 0.63 | 0.68 | 0.67 | 0.78 | 0.55 | 0.47 | 0.52 | 0.42 |
| 2015 | 0.18 | 0.62 | 0.72 | 0.60 | 0.73 | 0.55 | 0.53 | 0.68 | 0.72 | 0.45 | 0.45 | 0.62 | 0.53 |
| 2016 | 0.30 | 0.82 | 0.80 | 0.82 | 0.80 | 0.82 | 0.87 | 0.67 | 0.75 | 0.57 | 0.43 | 0.73 | 0.65 |
| 2017 | 0.18 | 0.55 | 0.47 | 0.50 | 0.48 | 0.48 | 0.57 | 0.48 | 0.45 | 0.53 | 0.25 | 0.33 | 0.38 |
| 2018 | 0.13 | 0.72 | 0.63 | 0.60 | 0.60 | 0.47 | 0.45 | 0.45 | 0.40 | 0.47 | 0.45 | 0.25 | 0.30 |
| 2019 | 0.09 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.03 | 0.05 | 0.02 | 0.05 | 0.05 |
| 2020 | 0.22 | 0.42 | 0.42 | 0.42 | 0.40 | 0.45 | 0.42 | 0.37 | 0.32 | 0.18 | 0.32 | 0.18 | 0.22 |

Mean forest importance (three seeds, 16 folds), top columns:

| arm | set0 | set1 |
|---|---|---|
| fs1 | `vol_12m_rank` 0.35, `vol_36m_rank` 0.25, `conservative_score_rank` 0.09, `ret_1m_rank` 0.08 | 0.22, 0.16, 0.12, `ret_6m_rank` 0.08 |
| fs3 | `vol_12m_rank` 0.33, `vol_36m_rank` 0.23, `ret_1m_rank` 0.07 | 0.17, 0.14, `conservative_score_rank` 0.05 |
| fs4 | `vol_12m_rank` 0.27, `vol_36m_rank` 0.18, `ret_1m` 0.09, `vol_12m` 0.08 | 0.14, 0.11, 0.06, 0.06 |
| fs0 | `earnings_yield_vs_5y_median_rank` 0.14, `ocf_trend_4q_rank` 0.10, `ocf_yield_vs_5y_median_rank` 0.09 | 0.08, 0.06, 0.06 |
| fs2 | `earnings_yield_vs_5y_median_rank` 0.12, `ret_6m_rank` 0.09, `ocf_trend_4q_rank` 0.08 | 0.07, 0.06, 0.06 |

No sector-rank column is among the top six in fs3.

## Against the predictions in the config

| prediction | measured | matched? |
|---|---|---|
| fs1 within 0.03 of the reference on p@20 | 0.457 and 0.456 against 0.499 and 0.500: 0.042 and 0.044 below | **no**, by 0.012–0.014 |
| fs1 within 0.01 on PR-AUC | 0.0052 and 0.0044 below | yes |
| fs0 well below, p@20 under 0.40 | 0.416 (set0), 0.397 (set1); PR-AUC 0.015 below | set1 yes; set0 0.016 above the line, and 0.08 below the reference |
| fs3 moves PR-AUC by no more than 0.005 | −0.0004, +0.0002 | yes |
| fs4 moves PR-AUC by no more than 0.005 | −0.0145, −0.0113, lower in 13 of 16 years in both sets | **no** |

Two predictions failed. Neither failure changes which feature set
goes forward (below), so the queued sweeps, which use the reference
set, do not depend on them.

## Measured

1. **No arm is better than the 112 rank columns.** fs3 is level with
   the reference on every column of the table (PR-AUC within 0.0006,
   p@20 within 0.006, the same crash-year and 2013–20 numbers). The
   13 sector ranks change nothing measurable and are barely used.
2. **The 15 technical ranks alone reach PR-AUC 0.322 against 0.327,
   and 0.51–0.53 against 0.535–0.544 on 2013–20 p@20.** Their p@20
   shortfall is in 2005–12 (0.38–0.40 against 0.45–0.47), mostly in
   the crash-window years 2005–07, where the reference is itself at or
   near the base rate, and the 2013–20 shortfall of set1 is 0.006.
   Lower PR-AUC than the reference in 14 and 11 of 16 years, so the
   97 other ranks add a small amount that is there in most years.
3. **Without the technical ranks the forests score 0.40–0.42**, PR-AUC
   0.311–0.312: twice the base rate (0.207), and level with the best
   single factor on p@20 (0.388) while above it on PR-AUC (0.301).
   The fundamentals carry a signal of their own, smaller than the
   technical family's, and it does not hold up after 2013 as well
   (2013–20: 0.37–0.43 against the reference's 0.535–0.544).
4. **Removing three columns costs as much as removing all 15.** fs2
   (109 columns) scores 0.388–0.390 and PR-AUC 0.305–0.309; fs0 (97
   columns) 0.397–0.416 and 0.311–0.312. fs2's PR-AUC is below fs0's
   in 14 and 11 of 16 years. The twelve technical ranks that remain
   in fs2 (momentum, returns, price distance, size, liquidity, beta)
   do not replace `vol_12m_rank`, `vol_36m_rank` and
   `conservative_score_rank`, and with those three gone they lower
   PR-AUC slightly.
5. **60 raw technical and trend columns lower PR-AUC by 0.011–0.015**,
   in 13 of 16 years, and p@20 by 0.045–0.056. The loss is in the
   2005–12 folds (2011: 0.42–0.44 against 0.48; 2012: 0.49–0.51
   against 0.57); in 2013–20 fs4's PR-AUC is 0.318–0.320 against
   0.324–0.326.
6. **Crash-window entry years are at the base rate in every arm.**
   2019: 0.00–0.05 against a base rate of 0.09, all ten arms and the
   reference. 2006–08: only arms holding the volatility ranks beat
   the base rate at all, and only with set0. fs0 and fs2 score 0.42–
   0.48 and 0.20–0.37 in 2005 where the reference scores 0.03–0.22;
   one year, not read further.
7. **The two parameter sets agree** on the order of the arms by
   PR-AUC (reference = fs3 > fs1 > fs4 ≈ fs0 > fs2) and, within 0.02,
   on p@20.

## What it might mean (hypotheses, not tested)

- *The signal is mostly "how calm has this stock been".* Consistent
  with 2, 4 and the importances. It would also explain 6: calmness
  does not protect against a market-wide fall. Not separated from the
  alternative that volatility ranks stand in for something else
  (size, profitability stability) that fundamentals measure worse.
- *Why fs4 lowered PR-AUC.* Rivals: (a) the raw technical columns
  duplicate their ranks and take splits from them with values that
  drift over time (a raw volatility level means different things in
  2008 and 2017, a rank does not), which hurts most where the
  training window is short, as the 2005–12 concentration suggests;
  (b) the 45 raw trend columns add noise at `max_features` 0.2–0.5,
  diluting the volatility ranks in each split's candidate set;
  (c) both. The importances show raw `ret_1m` and `vol_12m` taking
  0.06–0.09 each, which (a) predicts, and says nothing about (b).
  Separating them takes two arms: ranks + `features/technical` and
  ranks + `features/trend`. **Proposed, not queued**: the answer
  would not change the feature set, since neither can beat the
  reference by more than fs4 lost.
- *Why fs1 missed the p@20 prediction.* The miss is 0.012–0.014 and
  sits in 2005–07, three years with base rates of 0.04–0.21 where a
  pick or two per seed moves the number. The PR-AUC prediction held.
  Read as: the prediction's p@20 tolerance was tighter than the
  metric's noise.

## Decision

The feature set for the parameter search in the primary cell is the
`ranks` group, 112 columns on `dataset_v1.4`: the reference. fs3
equals it with 13 more columns and no arm exceeds it. This is the
feature set for the search, not a finalist: the parameter sets were
tuned on beat_spy.

A 15-column model (fs1) within 0.005 PR-AUC of the 112-column one is
worth remembering when a model has to be explained or deployed; it
is not pursued now.

## Next

Queued (`experiments/queue.toml`), in order, after the two items
already there:

1. `forest_random_search_dd_entry_3y`, 40 draws, one seed.
2. `lgbm_random_search_dd_entry_3y`, 40 draws, one seed.
3. `xgb_random_search_dd_entry_3y`, 40 draws, one seed, `device =
   "cpu"` (the sandbox has no GPU).

Plan step 3, equal budgets, ranked on fold-mean PR-AUC and 2013–20
p@20. The top five of each on three seeds follow once the searches
are read; they cannot be written before.
