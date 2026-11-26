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
