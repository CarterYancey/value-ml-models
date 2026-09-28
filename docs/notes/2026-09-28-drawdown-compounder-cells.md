# Drawdown-compounder cells on dataset_v1.4

Detail behind entries in the [logbook](../logbook.md) and conclusions in
[findings](../findings.md). Moved here unchanged from `docs/findings.md` on
2026-09-28, when that file was split; section references inside the text
("section above", "below") are to this note or to its neighbours in
[notes/](.).

Unless stated otherwise, numbers are walk-forward fold means over test
years 2005–2020 (16 folds, `split_folds.parquet` of the named dataset
version), `p@20` picks the top 20 per test year, and they are
**selection-biased** by the trial counts given. None is a result of record.

## Drawdown-compounder cells (dataset_v1.4, 3 seeds)

Two cells, 3y, walk-forward, test years 2005–2020,
`split_folds.parquet` of `dataset_v1.4`, git `86ef0c4`:

- **A, whole path:** `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3`.
  Base rate 0.11 pooled (0.12 in 2005–12, 0.10 in 2013–20), 0.02 to
  0.25 by year. 25 configurations tried.
- **B, from entry:**
  `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2`. Base
  rate 0.21 pooled (0.22 / 0.20), 0.04 to 0.37 by year. 30
  configurations tried.

Sweeps: `forest_drawdown_compounder_seeds_3y` (2 parameter sets × 2
class weights × 3 seeds per cell), `lgbm_drawdown_compounder_seeds_3y`
(2 class weights × 3 seeds), and the three
`baseline_*_drawdown_compounder_3y` sweeps. Features: the `ranks`
group, 112 columns, in every model. Seeds 23, 232, 1776. Training
rows and effective sizes are those of the beat_spy cell (mean Σ
`sample_weight_3y` 25.5k, 12.7k in the 2005 fold to 37.2k in 2020).
The forest sets are set3 and set1 of `forest_candidate_sets_3y`
(named set0 and set1 in this sweep); they were tuned on beat_spy, not
here. The numbers are selection-biased by the counts above and none
is a result of record.

Seed-mean fold-mean p@20. "Years" is how many of the 16 test years
the seed-mean p@20 beat the base rate; "Brier yrs" how many years
Brier beat `base_rate_brier`, averaged over seeds:

| cell | candidate | p@20 | seed std | worst seed | 2005–12 | 2013–20 | years | p@50 | PR-AUC | Brier yrs |
|---|---|---|---|---|---|---|---|---|---|---|
| A | forest set1, cw 1.0 | 0.389 | 0.002 | 0.388 | 0.356 | 0.421 | 13 | 0.381 | 0.268 | 9.0 |
| A | forest set0, cw 1.0 | 0.374 | 0.005 | 0.369 | 0.308 | 0.440 | 12 | 0.371 | 0.268 | 8.7 |
| A | forest set0, cw 0.5 | 0.369 | 0.003 | 0.366 | 0.340 | 0.398 | 14 | 0.376 | 0.268 | 8.0 |
| A | forest set1, cw 0.5 | 0.365 | 0.016 | 0.350 | 0.342 | 0.388 | 12 | 0.369 | 0.267 | 8.0 |
| A | lightgbm, cw 0.25 | 0.348 | 0.007 | 0.341 | 0.321 | 0.375 | 11 | 0.355 | 0.257 | 4.0 |
| A | lightgbm, cw 0.5 | 0.327 | 0.022 | 0.303 | 0.294 | 0.360 | 10 | 0.343 | 0.258 | 7.7 |
| A | random (3 seeds) | 0.110 | 0.010 | 0.100 | 0.121 | 0.100 | 9 | 0.108 | 0.112 | |
| A | book-to-market rank | 0.038 | | | 0.050 | 0.025 | 2 | 0.021 | 0.104 | |
| A | earnings-yield rank | 0.028 | | | 0.031 | 0.025 | 3 | 0.031 | 0.146 | |
| A | base rate | 0.112 | | | 0.124 | 0.100 | | | | |
| B | forest set1, cw 1.0 | 0.500 | 0.016 | 0.491 | 0.465 | 0.535 | 14 | 0.479 | 0.327 | 10.0 |
| B | forest set0, cw 1.0 | 0.499 | 0.016 | 0.481 | 0.454 | 0.544 | 14 | 0.488 | 0.327 | 9.3 |
| B | forest set0, cw 0.5 | 0.498 | 0.028 | 0.466 | 0.460 | 0.535 | 14 | 0.493 | 0.328 | 5.0 |
| B | forest set1, cw 0.5 | 0.481 | 0.008 | 0.475 | 0.433 | 0.529 | 13 | 0.484 | 0.327 | 5.0 |
| B | lightgbm, cw 0.5 | 0.400 | 0.014 | 0.384 | 0.371 | 0.429 | 11 | 0.391 | 0.303 | 5.0 |
| B | lightgbm, cw 0.25 | 0.394 | 0.019 | 0.381 | 0.390 | 0.398 | 11 | 0.403 | 0.303 | 1.0 |
| B | random (3 seeds) | 0.214 | 0.014 | 0.200 | 0.212 | 0.215 | 6 | 0.208 | 0.208 | |
| B | book-to-market rank | 0.106 | | | 0.125 | 0.088 | 3 | 0.084 | 0.197 | |
| B | earnings-yield rank | 0.075 | | | 0.062 | 0.088 | 2 | 0.099 | 0.245 | |
| B | base rate | 0.207 | | | 0.216 | 0.199 | | | | |

Per test year, family means over every run of the family (12 forest
runs, 6 lightgbm, 3 random):

| year | A base | A forest | A lgbm | A random | B base | B forest | B lgbm | B random |
|---|---|---|---|---|---|---|---|---|
| 2005 | 0.10 | 0.08 | 0.08 | 0.10 | 0.21 | 0.14 | 0.03 | 0.27 |
| 2006 | 0.05 | 0.03 | 0.01 | 0.07 | 0.09 | 0.16 | 0.02 | 0.07 |
| 2007 | 0.02 | 0.00 | 0.00 | 0.00 | 0.04 | 0.13 | 0.00 | 0.03 |
| 2008 (GFC) | 0.03 | 0.11 | 0.00 | 0.03 | 0.05 | 0.16 | 0.17 | 0.08 |
| 2009 (GFC) | 0.16 | 1.00 | 0.65 | 0.13 | 0.36 | 0.84 | 0.79 | 0.33 |
| 2010 | 0.17 | 0.57 | 0.59 | 0.18 | 0.32 | 0.74 | 0.87 | 0.32 |
| 2011 | 0.21 | 0.47 | 0.78 | 0.18 | 0.27 | 0.70 | 0.56 | 0.23 |
| 2012 | 0.25 | 0.43 | 0.34 | 0.27 | 0.37 | 0.75 | 0.61 | 0.37 |
| 2013 | 0.15 | 0.48 | 0.36 | 0.20 | 0.28 | 0.57 | 0.38 | 0.40 |
| 2014 | 0.14 | 0.60 | 0.64 | 0.12 | 0.21 | 0.66 | 0.45 | 0.15 |
| 2015 | 0.15 | 0.60 | 0.49 | 0.10 | 0.18 | 0.66 | 0.49 | 0.13 |
| 2016 | 0.17 | 0.71 | 0.58 | 0.18 | 0.30 | 0.79 | 0.60 | 0.37 |
| 2017 | 0.06 | 0.36 | 0.43 | 0.08 | 0.18 | 0.50 | 0.62 | 0.15 |
| 2018 | 0.03 | 0.35 | 0.37 | 0.05 | 0.13 | 0.69 | 0.71 | 0.18 |
| 2019 | 0.02 | 0.04 | 0.02 | 0.00 | 0.09 | 0.01 | 0.00 | 0.08 |
| 2020 (COVID) | 0.08 | 0.15 | 0.07 | 0.07 | 0.22 | 0.41 | 0.07 | 0.25 |

Measured:

- **The single-seed results held.** LightGBM over three seeds: 0.33–
  0.35 in A (0.36 on seed 7 before) and 0.39–0.40 in B (0.40–0.42
  before). Seed std is 0.002–0.028 across all twelve candidates.
- **The lift is not a 2005–12 lift.** Every model candidate scores
  higher in 2013–20 than in 2005–12, the opposite of beat_spy.
  Forests, 2013–20: 0.39–0.44 in A against a 0.10 base rate,
  0.53–0.54 in B against 0.20.
- **Forests are ahead of LightGBM in both cells, on p@20 and on
  PR-AUC.** B: 0.48–0.50 against 0.39–0.40, PR-AUC 0.327 against
  0.303. A: 0.37–0.39 against 0.33–0.35, PR-AUC 0.268 against 0.258.
  The B gap (0.08–0.10) is three or more seed standard deviations;
  the A gap is smaller and the families swap places year by year. LightGBM ran
  one untuned parameter set, so this compares two configurations,
  not two tuned families.
- **Inside the forest family nothing separates.** The four forest
  candidates span 0.48–0.50 in B and 0.37–0.39 in A, within one
  standard error (about 0.03). class_weight 1.0 has the better Brier
  (B: better than `base_rate_brier` in 9–10 of 16 years against 5
  for class_weight 0.5) at the same p@20 and PR-AUC.
- **The lift sits in entry years 2009–2018.** Forest family there:
  0.56 in A (base 0.15) and 0.69 in B (base 0.26). In 2005–08 the
  forests score 0.05 in A (base 0.05) and 0.15 in B (base 0.10); in
  2019, 9 hits in 240 picks in A and 3 in 240 in B (base 0.02 and
  0.09), with all twelve forest runs below the base rate in B. Those
  are the entry years whose 3-year window holds the 2008 or the 2020
  crash, and the base rate is at its lowest there (A: 0.02–0.10;
  B: 0.04–0.09 in 2006–08 and 2019, 0.21 in 2005).
  Explanation, untested: the models rank stocks by how calm they
  have been, which does not protect against a market-wide fall.
  2020 entries are above the base rate for forests (0.41 in B) and
  not for LightGBM (0.07).
- **PR-AUC beats the base rate in all 16 years** for every forest
  and LightGBM candidate, in both cells.
- **The value baselines are far below the base rate** (0.03–0.11),
  as on beat_spy: the cheapest stocks are rarely drawdown-free
  compounders. The random baseline sits at the base rate (0.110 and
  0.214, three seeds). The majority baseline's p@K is a tie-break
  and is not read.
- **What the models use.** `vol_12m_rank` + `vol_36m_rank` hold 0.53
  of the forest importance in A and 0.42 in B (LightGBM: 0.47 and
  0.31). The forest share is 0.38–0.50 in the 2005–12 folds and
  0.45–0.56 in the 2013–20 folds, so it does not fade. Next in B: `ret_1m_rank`, `conservative_score_rank`,
  `ocf_yield_rank`.

### Against low-risk single factors (added 2026-09-28, night)

`baseline_lowvol_rank_3y`, git `3f2bfdf`, one deterministic run per
factor and cell. Trial counts after it: cell A 29, cell B 34.
"Crash" is the mean over entry years 2005–08 and 2019:

| cell | candidate | p@20 | 2005–12 | 2013–20 | 2009–18 | crash | p@50 | PR-AUC |
|---|---|---|---|---|---|---|---|---|
| B | forests (4 candidates, 3 seeds) | 0.48–0.50 | 0.43–0.47 | 0.53–0.54 | 0.68–0.71 | 0.09–0.15 | 0.48–0.49 | 0.327 |
| B | lightgbm (2 candidates, 3 seeds) | 0.39–0.40 | 0.37–0.39 | 0.40–0.43 | 0.60–0.61 | 0.04 | 0.39–0.40 | 0.303 |
| B | highest `conservative_score_rank` | 0.388 | 0.356 | 0.419 | 0.560 | 0.100 | 0.392 | 0.301 |
| B | lowest `vol_36m_rank` | 0.325 | 0.294 | 0.356 | 0.490 | 0.060 | 0.416 | 0.318 |
| B | lowest `vol_12m_rank` | 0.094 | 0.125 | 0.062 | 0.135 | 0.020 | 0.190 | 0.311 |
| B | lowest `beta_12m_rank` | 0.050 | 0.050 | 0.050 | 0.060 | 0.030 | 0.046 | 0.194 |
| B | base rate | 0.207 | 0.216 | 0.199 | 0.261 | 0.097 | | |
| A | forests | 0.37–0.39 | 0.31–0.36 | 0.39–0.44 | 0.54–0.59 | 0.04–0.06 | 0.37–0.38 | 0.268 |
| A | lightgbm | 0.33–0.35 | 0.29–0.32 | 0.36–0.38 | 0.51–0.54 | 0.02 | 0.34–0.36 | 0.258 |
| A | highest `conservative_score_rank` | 0.344 | 0.319 | 0.369 | 0.510 | 0.070 | 0.319 | 0.221 |
| A | lowest `vol_36m_rank` | 0.316 | 0.306 | 0.325 | 0.470 | 0.070 | 0.395 | 0.259 |
| A | lowest `vol_12m_rank` | 0.075 | 0.106 | 0.044 | 0.110 | 0.020 | 0.181 | 0.250 |
| A | lowest `beta_12m_rank` | 0.009 | 0.000 | 0.019 | 0.005 | 0.010 | 0.010 | 0.110 |
| A | base rate | 0.112 | 0.124 | 0.100 | 0.149 | 0.046 | | |

Per test year, cell B, p@20:

| year | base | conservative score | low vol_36m | forest family |
|---|---|---|---|---|
| 2005 | 0.21 | 0.35 | 0.10 | 0.14 |
| 2006 | 0.09 | 0.05 | 0.05 | 0.16 |
| 2007 | 0.04 | 0.00 | 0.00 | 0.13 |
| 2008 (GFC) | 0.05 | 0.05 | 0.10 | 0.16 |
| 2009 (GFC) | 0.36 | 0.55 | 0.50 | 0.84 |
| 2010 | 0.32 | 0.55 | 0.55 | 0.74 |
| 2011 | 0.27 | 0.60 | 0.55 | 0.70 |
| 2012 | 0.37 | 0.70 | 0.50 | 0.75 |
| 2013 | 0.28 | 0.65 | 0.65 | 0.57 |
| 2014 | 0.21 | 0.75 | 0.40 | 0.66 |
| 2015 | 0.18 | 0.65 | 0.55 | 0.66 |
| 2016 | 0.30 | 0.80 | 0.70 | 0.79 |
| 2017 | 0.18 | 0.20 | 0.35 | 0.50 |
| 2018 | 0.13 | 0.15 | 0.15 | 0.69 |
| 2019 | 0.09 | 0.05 | 0.05 | 0.01 |
| 2020 (COVID) | 0.22 | 0.10 | 0.00 | 0.41 |

The config stated two readings before the run: a baseline within
0.05 of the forests means a low-volatility screen, baselines under
0.35 (B) / 0.25 (A) mean more than a single factor.

- **Cell B falls between the two readings.** The best single factor
  scores 0.388, which is 0.11 below the forests and above the 0.35
  line. The forest family is higher than it in 11 of 16 years on
  p@20 and in 15 of 16 on PR-AUC (0.327 against 0.301), and the gap
  is widest in 2017, 2018 and 2020 (0.50 / 0.69 / 0.41 against
  0.20 / 0.15 / 0.10). So in B the forests add to the single factor,
  and about 60% of their lift over the base rate (0.18 of 0.29) is
  available from one column.
- **LightGBM, as configured, adds nothing to the single factor in
  B:** 0.39–0.40 against 0.388, PR-AUC 0.303 against 0.301.
- **Cell A is a screen by the stated reading.** The best factor
  (0.344) is within 0.05 of the forests (0.37–0.39), and the forest
  family is higher in only 7 of 16 years. Its PR-AUC is higher
  (0.268 against 0.221 and 0.259), so the forests order the whole
  cross-section better and the top 20 about equally.
- **Nothing escapes the crash windows.** Over 2005–08 and 2019 every
  factor is within 0.03 of the base rate (B: 0.02–0.10 against
  0.10; A: 0.01–0.07 against 0.05), like the models.
- **The lowest `vol_12m_rank` is a bad top-20 and a good ranking:**
  p@20 0.09 in B with PR-AUC 0.311. The few calmest stocks over 12
  months are rarely compounders. Explanation, untested: prices
  pinned by a pending acquisition or by illiquidity. It argues for
  having the investability filter in place before any top-K number
  in these cells is acted on.

Open, and what would close it:

- **Is this more than a low-volatility screen?** Answered above for
  the top 20: yes in B (by 0.11), barely in A.
- **Treat the size of the lift as suspect** (a result far above
  baseline is leakage first). The single factors reach 0.39 with no
  model at all, which leakage in the fitting cannot explain, so most
  of the lift is a property of the label. What was
  checked: tags, rows and effective sizes are the beat_spy cell's,
  which shows no such lift with the same code; labels are loader
  expressions over the manifest's label columns. What was not: that
  the top 20 rows are different stocks. p@K counts test rows, a
  stock has up to four median rows per test year, and in A every one
  of the twelve forest runs scored 20 of 20 in 2009. If the 20 rows
  are five stocks, the standard errors quoted here are too small.
  Needs distinct-`permaticker` counts for the picks in the report.
- **Scores are not probabilities.** conf@20 is 0.46–0.48 for the
  class_weight 1.0 forests against a realized 0.37–0.39 in A and
  0.50 in B, and Brier beats the no-skill reference in about half
  the years only.

**Decision: no holdout look in either cell.** The candidates are
untuned and have not met their real baseline. Both cells stay
unopened.
