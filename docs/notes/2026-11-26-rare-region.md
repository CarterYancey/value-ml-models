# The run-up labels, fundamentals without price, and the rare region (2026-11-26, decisions 78–79)

Carter's second request of 2026-11-26: more experiments on the run-up and
market-relative labels, feature sets that lean less on ranks and leave out
volume and momentum, the fundamental-history columns beside other
fundamentals, and a way to make a model find the rare region (a strong
record, a steep but temporary fall) instead of "big momentum good".
Decision 78 holds the plan and the predictions; this note holds the tables.
Every number is from `experiments/ledger/claude-value-ml-models.csv`,
dataset_v1.5.1, seed 23, the candidate's forest configuration (decision 24),
trained on every row and read inside the 100k floor on the same-size screen
(10 per quarter, 2 per sector, peers = same `log_marketcap_rank` ventile).
"Lead" is the picks' mean 3-year CAGR minus their same-size peers' mean, a
fold mean over the 16 test years 2005–2020. "Losers" is the share of picks
with a negative 3-year CAGR. Gains are paired by test year with the control
(cell C × fs0 of `forest_fund_labels_3y`: lead +0.029, losers 0.167, p@20
0.747).

## Sweep A: six cells × five feature sets (`forest_fund_labels_3y`, 30 runs)

Feature sets: fs0 the 112 ranks of v1.4.1 (the control set); fs1 the 193
raw fundamental columns (no technical, events, classification or meta
family; nothing about price); fs2 the rank group without the 15 technical
ranks plus the 28 columns upstream ships unranked (history fractions,
dividend history, 5-year percentiles), 162; fs3 the compact own-history set
(fundhist and relvalue families plus 31 named fundamentals), 74; fs4 = fs3
plus `dist_5y_high`, `dist_52w_high`, `price_vs_5y_avg`, 77.

| cell | set | p@20 | base | lead | gain vs control (t, ahead/16) | losers | lost half | doubled | picks' CAGR | peers' CAGR |
|---|---|---|---|---|---|---|---|---|---|---|
| C: cagr ≥ 0 & dd < 0.3 | fs0 | 0.747 | 0.428 | +0.029 | control | 0.167 | 0.077 | 0.052 | 0.096 | 0.067 |
| | fs1 | 0.656 | | +0.025 | −0.004 (−0.5, 7) | 0.234 | 0.170 | 0.058 | 0.071 | 0.046 |
| | fs2 | 0.678 | | +0.029 | +0.000 (0.1, 6) | 0.223 | 0.162 | 0.066 | 0.079 | 0.050 |
| | fs3 | 0.644 | | +0.021 | −0.008 (−0.8, 8) | 0.259 | 0.194 | 0.059 | 0.063 | 0.042 |
| | fs4 | 0.653 | | +0.019 | −0.010 (−1.0, 6) | 0.238 | 0.180 | 0.055 | 0.064 | 0.044 |
| cagr ≥ 0.15 & dd < 0.3 | fs0 | 0.244 | 0.211 | +0.022 | −0.006 (−0.9, 7) | 0.247 | 0.158 | 0.067 | 0.070 | 0.048 |
| | fs1 | 0.206 | | −0.022 | −0.051 (−2.8, 3) | 0.403 | 0.359 | 0.116 | −0.002 | 0.020 |
| | fs2 | 0.341 | | +0.032 | +0.003 (0.5, 9) | 0.259 | 0.205 | 0.097 | 0.078 | 0.046 |
| | fs3 | 0.194 | | −0.043 | −0.072 (−3.4, 3) | 0.427 | 0.394 | 0.125 | −0.028 | 0.015 |
| | fs4 | 0.194 | | −0.047 | −0.075 (−4.0, 2) | 0.439 | 0.394 | 0.114 | −0.033 | 0.014 |
| cagr ≥ 0.2 \| dd ≤ SPY's dd | fs0 | 0.656 | 0.335 | +0.009 | −0.020 (−3.1, 2) | 0.142 | 0.067 | 0.039 | 0.066 | 0.056 |
| | fs1 | 0.456 | | +0.003 | −0.026 (−1.7, 3) | 0.319 | 0.250 | 0.091 | 0.038 | 0.035 |
| | fs2 | 0.459 | | +0.029 | −0.000 (0.0, 8) | 0.253 | 0.173 | 0.072 | 0.083 | 0.054 |
| | fs3 | 0.406 | | −0.004 | −0.033 (−2.5, 2) | 0.352 | 0.291 | 0.092 | 0.023 | 0.027 |
| | fs4 | 0.434 | | −0.001 | −0.030 (−1.7, 3) | 0.320 | 0.280 | 0.091 | 0.025 | 0.026 |
| run-up ≥ 0.5 & dd < 0.3 | fs0 | 0.431 | 0.305 | +0.025 | −0.004 (−0.6, 7) | 0.244 | 0.164 | 0.078 | 0.077 | 0.053 |
| | fs1 | 0.369 | | −0.009 | −0.038 (−1.9, 4) | 0.359 | 0.309 | 0.100 | 0.017 | 0.026 |
| | fs2 | 0.478 | | +0.036 | +0.007 (0.8, 9) | 0.234 | 0.177 | 0.077 | 0.081 | 0.045 |
| | fs3 | 0.375 | | −0.009 | −0.038 (−2.2, 5) | 0.370 | 0.328 | 0.106 | 0.013 | 0.022 |
| | fs4 | 0.362 | | −0.023 | −0.051 (−3.0, 5) | 0.391 | 0.338 | 0.094 | −0.000 | 0.022 |
| run-up ≥ 1.0 & dd < 0.4 | fs0 | 0.253 | 0.188 | +0.110 | +0.081 (5.3, 15) | 0.381 | 0.356 | 0.192 | 0.069 | −0.041 |
| | fs1 | 0.241 | | −0.037 | −0.066 (−1.7, 4) | 0.530 | 0.566 | 0.172 | −0.072 | −0.034 |
| | fs2 | 0.288 | | +0.020 | −0.009 (−0.4, 7) | 0.452 | 0.452 | 0.189 | 0.011 | −0.009 |
| | fs3 | 0.222 | | −0.048 | −0.077 (−2.1, 4) | 0.514 | 0.558 | 0.175 | −0.079 | −0.031 |
| | fs4 | 0.216 | | −0.066 | −0.095 (−2.8, 4) | 0.534 | 0.573 | 0.152 | −0.096 | −0.031 |
| run-up ≥ 0.75 | fs0 | 0.419 | 0.361 | +0.026 | −0.003 (−0.3, 9) | 0.691 | 0.716 | 0.098 | −0.145 | −0.171 |
| | fs1 | 0.488 | | −0.005 | −0.034 (−0.9, 7) | 0.531 | 0.589 | 0.188 | −0.076 | −0.071 |
| | fs2 | 0.547 | | +0.033 | +0.004 (0.2, 7) | 0.556 | 0.572 | 0.183 | −0.049 | −0.082 |
| | fs3 | 0.488 | | −0.047 | −0.076 (−1.6, 7) | 0.555 | 0.605 | 0.181 | −0.099 | −0.053 |
| | fs4 | 0.509 | | −0.067 | −0.096 (−2.2, 4) | 0.575 | 0.639 | 0.180 | −0.122 | −0.055 |

"Lost half" = share of picks whose drawdown from entry reached 50%;
"doubled" = share with a 3-year CAGR of 26% or more.

Path of the picks (fold means): cell C × fs0 realized volatility 0.248
(peers 0.360), drawdown 0.175 (0.294); run-up ≥ 0.75 × fs0 volatility 0.848
(0.884), drawdown 0.644 (0.634); run-up ≥ 1.0 & dd < 0.4 × fs0 volatility
0.501 (0.648), run-up 1.008 (1.171), drawdown 0.407 (0.499).

Per-year lead of the 'doubled without a crash' arm (fs0) and the control:

| year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C fs0 lead | .002 | .058 | .048 | .040 | .060 | .040 | .006 | .019 | .051 | .067 | .022 | .029 | .040 | .000 | −.017 | −.002 |
| ru100 fs0 lead | .092 | .080 | .135 | .091 | .078 | .117 | .131 | .132 | .156 | .161 | .159 | .055 | .030 | .011 | .101 | .235 |
| C fs0 picks' CAGR | .010 | −.042 | −.013 | .087 | .217 | .169 | .149 | .154 | .111 | .125 | .090 | .125 | .102 | .113 | .072 | .064 |
| ru100 fs0 picks' CAGR | .041 | −.146 | −.084 | .072 | .205 | .122 | .162 | .185 | .069 | .093 | .120 | .034 | −.050 | .020 | .069 | .192 |
| C fs0 peers' losers | .43 | .66 | .60 | .35 | .16 | .16 | .14 | .17 | .27 | .27 | .28 | .22 | .33 | .23 | .24 | .30 |
| ru100 fs0 peers' losers | .53 | .75 | .73 | .49 | .33 | .44 | .40 | .36 | .55 | .52 | .47 | .45 | .59 | .47 | .51 | .52 |

Importances (mean over folds, top of the list): cell C × fs0 `vol_12m_rank`
0.198, `vol_36m_rank` 0.126, `ocf_trend_4q_rank` 0.067 (top ten 0.66 of
the total); cell C × fs1 `ocf_yield` 0.105, `ocf_trend_4q` 0.078,
`ocf_positive_frac_4q` 0.049 (top ten 0.49); cell C × fs2 `ocf_trend_4q_rank`
0.091, `ocf_consistency_4q_rank` 0.075, `ocf_trend_8q_rank` 0.057 (top ten
0.44); 'doubled without a crash' × fs0 `ret_1m_rank` 0.128,
`dist_52w_high_rank` 0.060, `ret_6m_rank` 0.059 (top ten 0.44); run-up ≥ 0.75
× fs0 `ret_1m_rank` 0.207, `max_ret_21d_rank` 0.129, `dist_52w_high_rank`
0.102 (top ten 0.69); the union label × fs0 `vol_12m_rank` 0.163,
`beta_12m_rank` 0.122 (top ten 0.69).

### Reading of sweep A against decision 78.5

- (a) held: fs1 in cell C is 0.091 below fs0 on p@20 (predicted 0.08–0.12),
  its lead is within 0.02 of fs0's (−0.004), and its losers are 6.7 points
  higher (predicted 3–6). The rival (same lead, no more losers) is out.
- (b) held in part: fs3 and fs4 are no better than fs1 anywhere; fs4 does not
  lead fs3 (−0.010 against −0.008 in cell C) — the three fall columns added
  nothing to the compact set.
- (c) held for run-up ≥ 0.75: learned as volatility (picks' realized
  volatility 0.848 against 0.248 for cell C), picks lose 14.5% a year. Not
  held for run-up ≥ 1.0 & dd < 0.4: its picks do not look like cell C's. The
  fs0 forest on that cell is a one-month reversal screen (`ret_1m_rank`,
  `dist_52w_high_rank`) whose picks lead their same-size peers by +0.081 a
  year more than the control does (t 5.3, ahead in 15 of 16 years, both
  halves), with 19% of picks doubling against 5% — but 38% losers against
  17%, 36% losing half their value against 8%, and a mean CAGR of 0.069
  against 0.096. The peers of its picks lose money in 33–59% of cases in
  every year after 2008 (the control's peers: 14–33%): the lead is over a
  bad neighbourhood. It fails rule 74.4 on the second outcome.
- (d) not held as written: the union label's p@20 lift is 0.32, not ≤ 0.10;
  its lead is 0.020 below cell C's (t −3.1, ahead in 2 years) and its losers
  are 2.5 points fewer (1.4 se). It is a calmer, poorer cell C (picks'
  volatility 0.190, CAGR 0.066).
- (f) held: no fundamentals-only arm passes 74.4 against the control. The
  best of them is fs2 (ranks without the technical family plus the unranked
  history columns): in cell C it matches the control's lead exactly
  (+0.000, 6 of 16 years ahead) with 5.6 points more losers and twice the
  share losing half; on the three harder cells it is the only set that leads
  its fs0 twin (cagr ≥ 0.15 & dd < 0.3: +0.032 against +0.022; run-up ≥ 0.5 &
  dd < 0.3: +0.036 against +0.025; the union: +0.029 against +0.009), each
  within noise of the control on the lead and 7–9 points behind on losers.
  Without the volatility ranks the forest builds itself on operating cash
  flow (yield, trend, consistency), as the raw set does.

What this means (hypotheses, not measurements): the control's edge on losers
is the volatility ranks; the fundamentals sets reach the same lead with more
losers because they cannot see calm. The fundamental-history columns do not
add a lead by themselves. The run-up label with a drawdown cap finds a real
lead, carried by short-term reversal, in a neighbourhood that loses money.

## Sweep B: ten single-rank bars on the four new cells (`baseline_fund_labels_3y`, 40 runs)

A rank bar picks the same stocks whatever the cell, so its screen
outcomes are one row per bar; only p@20 depends on the cell. Paired by
test year with the control (cell C × fs0 of sweep A).

| bar (direction) | lead | 2005–12 | 2013–20 | gain vs control (t, ahead/16) | losers | losers vs control (fewer in n years) | picks' CAGR | distinct stocks/yr |
|---|---|---|---|---|---|---|---|---|
| vol_36m low | +0.013 | −0.008 | +0.034 | −0.016 (−1.6, 6) | 0.173 | +0.006 (8) | 0.071 | 17.1 |
| vol_12m low | −0.021 | −0.006 | −0.036 | −0.050 (−2.5, 1) | 0.239 | +0.072 (3) | 0.026 | 24.0 |
| conservative_score high | +0.031 | +0.027 | +0.035 | +0.002 (0.3, 7) | 0.238 | +0.070 (4) | 0.090 | 28.8 |
| roc_greenblatt high | +0.008 | +0.019 | −0.002 | −0.020 (−1.3, 7) | 0.350 | +0.183 (0) | 0.043 | 26.2 |
| mom_12_2 high | −0.100 | −0.116 | −0.083 | −0.129 (−7.1, 1) | 0.659 | +0.492 (0) | −0.142 | 29.9 |
| earnings_yield high | −0.009 | −0.032 | +0.014 | −0.038 (−1.5, 8) | 0.569 | +0.402 (0) | −0.096 | 25.2 |
| earnings_yield_5y_avg high | −0.029 | −0.053 | −0.005 | −0.058 (−1.4, 6) | 0.612 | +0.445 (0) | −0.125 | 21.4 |
| log_marketcap high | +0.023 | +0.003 | +0.043 | −0.005 (−0.5, 7) | 0.183 | +0.016 (4) | 0.107 | 10.9 |
| dist_5y_high high (near the high) | +0.013 | +0.018 | +0.009 | −0.016 (−1.0, 6) | 0.256 | +0.089 (3) | 0.051 | 36.6 |
| roe_5y_z high | +0.025 | +0.033 | +0.017 | −0.004 (−0.4, 11) | 0.312 | +0.145 (0) | 0.062 | 32.4 |

p@20 of the bars by cell (fold means), beside the best forest of sweep A
on that cell:

| cell | base | best bar | forest fs0 | forest fs2 |
|---|---|---|---|---|
| cagr ≥ 0.15 & dd < 0.3 | 0.211 | log_marketcap 0.403, conservative_score 0.341 | 0.244 | 0.341 |
| cagr ≥ 0.2 \| dd ≤ SPY's | 0.335 | log_marketcap 0.550, vol_36m 0.528, dist_5y_high 0.528 | 0.656 | 0.459 |
| run-up ≥ 1.0 & dd < 0.4 | 0.188 | log_marketcap 0.269, roc_greenblatt 0.234 | 0.253 | 0.288 |
| run-up ≥ 0.75 | 0.361 | earnings_yield_5y_avg 0.475, earnings_yield 0.428 | 0.419 | 0.547 |

### Reading of sweep B

- No bar passes 74.4 against the control. The size bar (the largest
  liquid stocks, 10.9 distinct names a year) matches the control on
  both outcomes within noise (lead −0.005, losers +1.6 points) and earns
  more in absolute terms (0.107 against 0.096) because its peers are the
  largest stocks; it is a different portfolio (a basket of the biggest
  companies), not a selection. The conservative-score bar matches the
  control's lead (+0.002) with 7 points more losers. Every other bar is
  behind on losers by 7 to 49 points.
- "Big momentum good" is false here: the 12-2 momentum bar loses 14.2% a
  year, 10 points a year behind its same-size peers in both halves, with
  66% losers. The forests never learned momentum as good; what they
  learned is calm (low volatility) and size.
- The `roe_5y_z` bar alone (a strong record against the stock's own past)
  is ahead of the control on lead in 11 of 16 years (gain −0.004, within
  noise) and 14.5 points worse on losers: the history columns carry a
  lead, not a loser filter — the same pattern sweep A's fs2 shows.
- On 'a real gain without a crash' the size bar (0.403) beats every
  forest on p@20 (fs0 0.244, fs2 0.341); on 'doubled without a crash' the
  size bar's 0.269 is above the fs0 forest's 0.253. On those two cells
  the forests do not beat a trivial bar as predictors; cell C and the
  union label are where the forest has something to add on precision.

## Sweep C: the 5-year horizon (`forest_fund_labels_5y`, 12 runs, folds 2007–2018)

Feature sets: fs0 the 112 old ranks, fs1 the 193 raw fundamentals, fs2
the compact own-history set plus the fall columns (sweep A's fs4). The
control is cell C's 5-year twin × fs0 (lead over same-size peers on the
5-year CAGR +0.032 a year, losers 0.092, p@20 0.788, 27.5 distinct
stocks a year). Paired by test year, 12 years, halves 2007–12 and 2013–18.

| cell | set | p@20 | base | lead | gain vs control (t, ahead/12) | losers | lost half | picks' CAGR | peers' CAGR |
|---|---|---|---|---|---|---|---|---|---|
| C5: cagr ≥ 0 & dd < 0.3 | fs0 | 0.788 | 0.425 | +0.032 | control | 0.092 | 0.065 | 0.105 | 0.073 |
| | fs1 | 0.638 | | +0.008 | −0.024 (−2.6, 4) | 0.240 | 0.277 | 0.049 | 0.041 |
| | fs2 | 0.638 | | +0.008 | −0.024 (−3.5, 2) | 0.269 | 0.285 | 0.043 | 0.036 |
| cagr ≥ 0.15 & dd < 0.3 | fs0 | 0.171 | 0.170 | +0.024 | −0.008 (−1.0, 5) | 0.227 | 0.219 | 0.065 | 0.041 |
| | fs1 | 0.192 | | −0.039 | −0.071 (−6.6, 0) | 0.394 | 0.417 | −0.025 | 0.013 |
| | fs2 | 0.175 | | −0.040 | −0.072 (−5.9, 1) | 0.404 | 0.429 | −0.035 | 0.005 |
| run-up ≥ 1.0 & dd < 0.4 | fs0 | 0.333 | 0.262 | +0.032 | −0.000 (−0.1, 5) | 0.215 | 0.227 | 0.075 | 0.044 |
| | fs1 | 0.279 | | −0.037 | −0.069 (−4.5, 0) | 0.390 | 0.438 | −0.028 | 0.009 |
| | fs2 | 0.267 | | −0.035 | −0.067 (−4.9, 1) | 0.406 | 0.456 | −0.029 | 0.005 |
| run-up ≥ 1.0 | fs0 | 0.438 | 0.371 | +0.103 | +0.071 (4.5, 11) | 0.483 | 0.548 | −0.019 | −0.122 |
| | fs1 | 0.438 | | −0.096 | −0.128 (−5.6, 1) | 0.588 | 0.627 | −0.139 | −0.043 |
| | fs2 | 0.429 | | −0.103 | −0.135 (−6.2, 1) | 0.590 | 0.640 | −0.144 | −0.041 |

### Reading of sweep C

- Prediction 78.5(e) held: the 5-year ordering is the 3-year ordering.
  The control is the only arm on both outcomes; every fundamentals-only
  set is 0.024 a year behind it on lead and 15–18 points behind on losers
  in cell C, and 7 points a year behind on the harder cells.
- At 5 years the run-up label with a drawdown cap on fs0 is no longer a
  reversal screen with a lead over a bad neighbourhood: it matches the
  control's lead exactly (−0.000, 5 of 12) with 12 points more losers.
  The uncapped run-up label is the 3-year pattern again (lead +0.071 over
  the control, t 4.5, 11 of 12 years; 48% losers; picks lose money).
- The compact own-history set with the fall columns (fs2) is the worst set
  at 5 years as at 3: the history columns beside a handful of fundamentals
  do not make a selection.

## Decision 79: the rare-region program

The region: inside the 100k floor, `dist_5y_high <= -0.4` and
`ocf_positive_frac_20q >= 0.9`. `[pick_screen] region` reports the share
of a selection inside it as the pick outcome `in_region`.

### The control's share of the region (`forest_fund_control_region_3y`, 1 run)

The control (cell C × fs0 of sweep A) re-run with the screen's region.
Model side identical to sweep A's run on every fold (p@20, PR-AUC,
screen CAGR, peers' CAGR, losers, distinct stocks; one Brier value
differs in the 15th digit). Shares inside the region, by test year:

| year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| control's picks | 0 | 0 | 0 | .10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | .006 |
| their same-size peers | .11 | .08 | .06 | .23 | .39 | .20 | .14 | .15 | .06 | .02 | .06 | .09 | .06 | .08 | .09 | .10 | .120 |
| all liquid test rows | .12 | .10 | .09 | .25 | .39 | .25 | .21 | .20 | .10 | .07 | .11 | .15 | .12 | .12 | .15 | .19 | .163 |

The candidate's forest buys nothing from the region: four picks in 2008
and none in any other year, while the region is 7–39% of the liquid rows
and 2–39% of the picks' own size band. Prediction 79(a)'s baseline
(control share below 0.15) held with room; the rival's bar for an
emphasized arm is a picks' share of 0.10 or more.

### Emphasis weights (`forest_emph3_fund_3y` and `forest_emph10_fund_3y`, 9 runs each)

The candidate's forest, seed 23, trained on every row with the training
rows inside the region (liquid, 40% or more below the 5-year high, cash
flow positive in 18 of 20 quarters) carrying 3× or 10× their sample
weight. The region is 0 of the training weight in fold 2005 (the
columns need 5 years of history), 1.4% in 2006, 4.9% in 2012 and 7.6%
in 2020, before the factor; so at ×3 it is at most a fifth of the
weight and at ×10 at most 45%, in the late folds. Each arm is paired by
test year with its unemphasized twin in sweep A (fs0 with fs0, fs1 with
sweep A's fs2, fs2 with sweep A's fs4). Lead = picks' 3-year CAGR minus
their same-size peers', fold mean; gain = lead minus the twin's; losers
= share of picks with a negative CAGR; region = share of the picks
inside the region.

| cell | set | × | p@20 | lead | gain vs twin (t, ahead) | losers (twin) | picks' CAGR | region |
|---|---|---|---|---|---|---|---|---|
| C | fs0 | 3 | .772 | +.027 | −.002 (−0.9, 6/16) | .166 (.167) | .096 | .006 |
| C | fs0 | 10 | .756 | +.023 | −.006 (−1.4, 7/16) | .161 (.167) | .093 | .006 |
| C | fs1 | 3 | .700 | +.031 | +.001 (0.6, 9/16) | .206 (.223) | .084 | .061 |
| C | fs1 | 10 | .700 | +.029 | −.001 (−0.1, 6/16) | .192 (.223) | .088 | .056 |
| C | fs2 | 3 | .678 | +.019 | −.000 (−0.0, 6/16) | .252 (.238) | .062 | .030 |
| C | fs2 | 10 | .678 | +.004 | −.015 (−1.8, 4/16) | .270 (.238) | .051 | .045 |
| c15dd30 | fs0 | 3 | .259 | +.027 | +.004 (0.9, 7/16) | .230 (.247) | .081 | .044 |
| c15dd30 | fs0 | 10 | .266 | +.017 | −.005 (−1.0, 6/16) | .238 (.247) | .077 | .050 |
| c15dd30 | fs1 | 3 | .356 | +.033 | +.001 (0.2, 8/16) | .258 (.259) | .079 | .095 |
| c15dd30 | fs1 | 10 | .334 | +.029 | −.003 (−0.6, 7/16) | .248 (.259) | .078 | .078 |
| c15dd30 | fs2 | 3 | .169 | −.046 | +.001 (0.0, 8/16) | .436 (.439) | −.029 | .605 |
| c15dd30 | fs2 | 10 | .175 | −.048 | −.001 (−0.1, 7/16) | .464 (.439) | −.030 | .667 |
| ru100dd40 | fs0 | 3 | .219 | +.064 | −.046 (−5.6, 1/16) | .409 (.381) | .052 | .266 |
| ru100dd40 | fs0 | 10 | .184 | +.031 | −.079 (−5.8, 1/16) | .361 (.381) | .056 | .141 |
| ru100dd40 | fs1 | 3 | .259 | +.023 | +.003 (0.2, 10/16) | .414 (.452) | .036 | .438 |
| ru100dd40 | fs1 | 10 | .278 | +.011 | −.009 (−0.5, 8/16) | .372 (.452) | .038 | .359 |
| ru100dd40 | fs2 | 3 | .222 | −.059 | +.007 (0.8, 7/16) | .536 (.534) | −.091 | .838 |
| ru100dd40 | fs2 | 10 | .262 | −.050 | +.016 (1.4, 10/16) | .538 (.534) | −.085 | .852 |

Against the control (cell C × fs0 of sweep A, lead +.029, losers .167):
×3 on fs0 in cell C is −.002 a year (t −0.9, ahead 6 of 16; −.001 in
2005–12, −.003 in 2013–20), losers −0.2 points, and its picks' share
inside the region is .006 — zero in every year but 2008 (.10), the
control's pattern exactly. ×10 is −.006 (t −1.4, 7 of 16; −.011 and
−.000 by half), losers −0.6 points, region .006.

Importances: at ×3 the cell-C forest on fs0 is the control's to the
third digit (`vol_12m_rank` .196 against .198, `vol_36m_rank` .131
against .126, then `ocf_trend_4q_rank`, `conservative_score_rank`). At
×10 `dist_5y_high_rank` (.078) and `price_vs_5y_avg_rank` (.065) move
to third and fourth place — the region's own columns win splits they
never won — and the picks' share inside the region is still .006. The
'doubled without a crash' forest on fs0 keeps `ret_1m_rank` first
(.122 against .128 unemphasized) and adds `price_vs_5y_avg_rank` (.046)
and `dist_5y_high_rank` (.040). The compact-set forest on 'a real gain
without a crash' at ×10 is `ocf_yield` (.156), `ocf_yield_5y_avg`
(.129), `earnings_yield_5y_peak` (.064): the yields, no history z-score
above .03.

### Reading of the emphasis sweeps against decision 79

- **79(a) held for ×3, and its rival failed.** Lead −.002, losers −0.2
  points, region share +0.0 points against a rival bar of +10 points
  and +.01 of lead. The region's columns did not win splits at ×3.
  For ×10 the prediction was half right: the lead moved further the
  same way (−.006), but losers fell 0.6 points instead of rising 3 or
  more. With the region near 45% of the late folds' training weight,
  the forest's prior did not become "fallen": it found the region's
  columns and used them to say no. The picks' share inside the region
  stayed at the control's .006.
- **79(b) held in cell C and was right for the wrong reason in
  'doubled without a crash'.** In cell C every change against the
  twin is inside noise (|t| ≤ 1.8). In 'doubled without a crash' the
  lead fell on fs0, not on fs1 or fs2: the one-month-reversal forest
  loses .046 a year at ×3 and .079 at ×10 (t −5.6 and −5.8, ahead in 1
  year of 16), while the fs1 and fs2 arms move inside noise. The
  region's rows erode the reversal cell's lead on the set that has the
  reversal columns, because the forest spends splits on the region's
  own columns (`price_vs_5y_avg_rank`, `dist_5y_high_rank`) and buys
  more of it (.27 of picks at ×3); its losers stay at 36–41%.
- **Where the forest does buy the region, the region loses.** The
  compact set on the two harder cells puts 60–85% of its picks inside
  the region, with or without emphasis, and those arms are the worst
  in the table: lead −.05 to −.06 a year, 44–54% losers, 39–58% of
  picks lose half, picks' CAGR −.03 to −.09. Emphasis moves them by
  less than noise. The arms that pick from the region are not finding
  the stocks that recover; they are finding the region.
- **Emphasis is not a lever here.** Across 18 arms, 16 move against
  their twin by less than 2 se; the two that move are the reversal
  forest, downward. No emphasis arm passes rule 74.4 against the
  control. The closest is fs1 at ×3 in cell C: lead +.031 (+.002
  against the control, ahead 8 of 16) with 3.9 points more losers.
  What the universe sweep adds: whether the region's own rows, trained
  on alone, carry any lead over in-region peers (79(c)).

### The region as a universe (`forest_region_universe_3y`, 6 runs, folds 2008–2020)

The candidate's forest trained and read on the region's rows alone
(`[[universe]]`: the 100k floor, `dist_5y_high <= -0.4`,
`ocf_positive_frac_20q >= 0.9`). Peers are now in-region stocks of the
same size. Training weight inside the region: 588 (fold 2008) to 2,810
(fold 2020), against 12,692–37,097 for the whole liquid set; 900–4,350
test rows a year. The same forest configuration, so leaves of 72 are
large against these fits.

What the region's rows did, all of them, against all liquid rows
(test-row means, 2008–2020):

| rows | n/yr | cell C rate | CAGR mean | CAGR median | losers | lost half | doubled | run-up ≥100% | vol |
|---|---|---|---|---|---|---|---|---|---|
| region | 2,144 | .405 | .019 | .048 | .407 | .403 | .185 | .335 | .552 |
| all liquid | 12,217 | .457 | .034 | .063 | .371 | .338 | .159 | .298 | .497 |

By year the region's mean CAGR is .090, .184, .095, .106, .096 in
2008–2012, then −.078, −.117, −.042, −.024, −.186, −.051 in 2013–2018,
.021 in 2019 and .147 in 2020; the liquid set's is −.042 to +.145 and
never below −.042 after 2007. The region has more doublers and more
losers than the market: wider tails, lower mean. It pays after a crash
(2009, 2020) and loses through the long rise (2013–2018). It is a bet
on the market's recovery, not a pool of mispriced survivors.

| cell | set | p@20 (base) | lead over in-region peers (ahead) | losers (peers) | picks' CAGR (peers') | doubled (peers) | stocks/yr |
|---|---|---|---|---|---|---|---|
| C | fs0 | .650 (.405) | +.040 (10/13) | .331 (.403) | .062 (.022) | .117 (.145) | 30.5 |
| C | fs1 | .569 | +.044 (fs1 − fs0 +.004, t 0.2, 8/13) | .331 (.396) | .071 (.027) | .152 (.151) | 28.7 |
| C | fs2 | .527 | −.011 (−.051 vs fs0, t −3.5, 2/13) | .387 (.400) | .018 (.029) | .092 (.149) | 25.0 |
| ru100dd40 | fs0 | .296 (.237) | +.051 (9/13) | .344 (.411) | .062 (.011) | .200 (.173) | 31.7 |
| ru100dd40 | fs1 | .323 | +.039 (−.002 vs fs0, 8/13) | .350 (.411) | .054 (.016) | .192 (.173) | 29.0 |
| ru100dd40 | fs2 | .285 | −.070 (−.110 vs fs0, t −2.5) | .527 (.461) | −.087 (−.017) | .194 (.187) | 26.2 |

Cell C on fs0 by year: lead +.010, −.010, +.020, +.092, +.049, +.102,
+.038, +.091, +.029, +.139, +.059, −.016, −.078 (2008–2020); losers .30,
.23, .18, .13, .18, .30, .63, .35, .35, .58, .53, .35, .23. The lead is
largest in the years the region lost most (2013, 2015, 2017: the forest
picks the in-region stocks that fall least), and the picks still lose
money in 2014 and 2017.

Against the control's picks (cell C × fs0 on all liquid rows, same 13
years): the control's picks earn .121 a year with 11% losers; the
in-region forest's earn .062 (−.059, t −3.4, ahead in 2 of 13) with 33%
losers (+22 points, t 5.0). The in-region picks double more often (.117
against .063) and so do their peers (.145 against .136): the doublers
are the region's, not the forest's.

Importances inside the region: fs0 `dist_5y_high_rank` .161,
`price_vs_5y_avg_rank` .095, `vol_12m_rank` .072, `vol_36m_rank` .062,
`dist_52w_high_rank` .055 — how far fallen, then how calm. fs1
`sales_yield_vs_5y_median_rank` .073,
`tangible_book_to_market_vs_5y_median_rank` .065,
`earnings_yield_5y_peak_rank` .039, `ocf_yield_5y_avg_rank` .029: the
valuation-against-own-history columns Carter asked about lead the
forest inside the region, and that forest's lead matches fs0's (+.044
against +.040) at the same losers with a lower p@20 (.569 against .650).

### Reading of the universe sweep against decision 79

- **79(c) held on every count but a tie.** Lead over in-region peers
  positive in 10 of 13 years for cell C on fs0 (the bar was 10), losers
  .331 (bar .30 or more), fs1 and fs2 not ahead of fs0 (fs1 +.004 of
  lead inside noise with a lower p@20; fs2 −.051, t −3.5). The emphasis
  arm (×3, fs0, cell C) has fewer losers than the universe arm in 12 of
  the 13 shared years and the same share (.225) in 2020.
- **The region's forest is decision 63's fallen-stocks finding again, on
  a different region.** Inside a pool of fallen stocks the forest finds
  the ones that fall least, by how far they have fallen and how calm
  they are, and leads its in-region peers by 4 points a year; the pool
  itself earns 2% a year with 40% losers, so the picks earn 6% with 33%
  losers — half the control's return with three times its losers. Trained
  inside the region the forest does not find the doublers: its picks
  double less often than their peers.
- **The own-history valuation columns are real inside the region and
  not enough.** On fs1 they are the top splits and carry fs0's lead.
  That is the first place in this program where the history columns
  lead a forest to the same lead as the price columns. It is a lead
  over a losing peer group.
- **What the region is.** Its rows' mean 3-year CAGR is .019 against
  .034 for all liquid rows, with more losers, more halvings and more
  doublers; it earns in 2009–2012 and 2020 and loses every year from
  2013 to 2018. "Strong history, steep fall, recovers" describes the
  region's good years, not its rows: the recovery is the market's.
  Whether a model can tell the recovering rows from the rest within the
  region is what the subspace, colsample and quantile arms test next,
  on all rows.

### Subspace forests (`forest_subspace_fund_3y`, 12 runs)

Forests that see 5% of the columns at each split (`max_features` 0.05:
5 of 112, 8 of 162, 3 of 77) instead of the candidate's 20%, so that a
weak column must be used when the strong ones are absent. Two shapes:
set0 depth 8, leaves of 30; set1 the candidate's depth 4, leaves of 72.
Trained on every row, read on the same-size screen, paired by year
with the control (cell C × fs0 of sweep A) and, in the reversal cell,
with the sweep A twin of the same set.

| cell | set | shape | p@20 | lead | gain vs control (t, ahead) | losers (+ vs control) | region | picks' CAGR |
|---|---|---|---|---|---|---|---|---|
| C | fs0 | depth 8 | .722 | +.028 | −.001 (−0.2, 7/16) | .189 (+2.2) | .009 | .092 |
| C | fs0 | depth 4 | .634 | +.021 | −.008 (−1.3, 7/16) | .194 (+2.7) | .022 | .087 |
| C | fs1 | depth 8 | .681 | +.023 | −.006 (−0.8, 7/16) | .238 (+7.0) | .058 | .077 |
| C | fs1 | depth 4 | .578 | +.024 | −.005 (−0.5, 4/16) | .228 (+6.1) | .072 | .077 |
| C | fs2 | depth 8 | .650 | +.007 | −.022 (−2.4, 3/16) | .244 (+7.7) | .033 | .056 |
| C | fs2 | depth 4 | .622 | +.010 | −.019 (−2.8, 5/16) | .252 (+8.4) | .030 | .059 |
| ru100dd40 | fs0 | depth 8 | .244 | +.106 | +.077 (3.8, 15/16) | .412 (+24.5) | .339 | .055 |
| ru100dd40 | fs0 | depth 4 | .244 | +.101 | +.072 (4.8, 15/16) | .398 (+23.1) | .344 | .056 |
| ru100dd40 | fs1 | depth 8 | .303 | +.055 | +.026 (1.0, 10/16) | .419 (+25.2) | .459 | .041 |
| ru100dd40 | fs1 | depth 4 | .316 | +.053 | +.024 (0.9, 9/16) | .420 (+25.3) | .522 | .041 |
| ru100dd40 | fs2 | depth 8 | .231 | −.042 | −.071 (−2.0, 4/16) | .523 (+35.6) | .831 | −.073 |
| ru100dd40 | fs2 | depth 4 | .234 | −.069 | −.098 (−2.7, 4/16) | .538 (+37.0) | .859 | −.098 |

Against the sweep A twins in the reversal cell: fs0 depth 8 −.004 of
lead (t −0.5, 8/16; the twin's lead is +.110) with 3 points more losers
and a third of its picks inside the region; fs1 +.035 and +.033 (t 3.3
and 3.5, ahead 14 and 13 of 16) over its twin's +.020, with 42% losers
(the twin 45%) and half its picks inside the region; fs2 depth 8 +.024
(t 2.5) over a twin at −.066.

Importances flatten as designed: in cell C on fs0 the top column is
`vol_12m_rank` at .060 (depth 8) and .070 (depth 4), against .198 in
the control, and the order is the control's (`vol_36m_rank`,
`max_ret_21d_rank`, `conservative_score_rank`, `ocf_trend_4q_rank`,
`ocf_consistency_4q_rank`). On fs1 the top columns are
`ocf_consistency_4q_rank` .028, `ocf_consistency_8q_rank` .024,
`ocf_trend_4q_rank` .021, `operating_margin_rank` .020: cash-flow
consistency, no history z-score or own-history yield above .02. In the
reversal cell on fs0, `ret_1m_rank` .039, `dist_52w_high_rank` .025,
`max_ret_21d_rank` .020, `ret_6m_rank` .020: the one-month reversal
again, found through 5 columns at a time.

### Reading of the subspace sweep against decision 79

- **79(d) held in substance, with the p@20 clause split.** Depth 8 lost
  .025 of p@20 (the bar was .03–.06) and depth 4 lost .113; the lead is
  inside noise of the control's (−.001 and −.008); losers are 2.2 and
  2.7 points higher (bar 2–4). Depth 8 beats depth 4 on p@20 and not on
  the screen. The rival failed: the picks' share inside the region is
  .009 and .022 against a bar of +10 points.
- **Forcing weak columns into the splits does not change what the
  forest buys.** The same columns lead, each with a third of its former
  weight; the picks are the control's kind of stock at a slightly higher
  loser rate. A column that discriminates in a rare region would have
  shown up here, where the volatility ranks are absent from 19 of 20
  splits; none did.
- **The reversal cell on fs1 is the one arm a subspace forest improved.**
  +.035 a year over its sweep A twin at 3 points fewer losers, picks
  half inside the region. It is still a 42%-losers arm whose picks earn
  4% a year, behind the control's 10%: not a candidate, and it says the
  "doubled without a crash" label has more to learn on fs1 than the
  candidate's forest shape gets at (an aside for the record, not a
  lead to follow in this program).
- No subspace arm passes rule 74.4 against the control on both
  outcomes.
