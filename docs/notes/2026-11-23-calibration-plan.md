# Calibration: why the forest's confidence fails, and the plan (2026-11-23)

Carter's direction 3 (decision 43): a well-calibrated model is the most
desirable thing. Top K is arbitrary; the rule wanted is **"buy every
stock whose probability is over X"**, which with a calibrated model
buys fewer stocks in risky years and more in good ones. This note is
the research and the plan; the code is on `claude/calibration`.

## What "calibrated" has to mean here

A probability p for a row is calibrated if, among rows scored p, a
share p turn out positive. Over a whole test year that implies
**calibration in the large**: the year's mean score equals the year's
base rate. That is the property the threshold rule needs. If a model's
mean score does not rise and fall with the base rate, "every stock over
X" buys the same number of stocks in a crash year as in a good one,
however well the scores are calibrated *pooled* over years.

Measured here, per run (new, `claude/calibration`):

- `mean_score` beside `base_rate` in every fold and in the era table;
- `year_calib_corr`: the correlation across test years of the mean
  score with the base rate (+1: confidence follows the market; 0: blind
  to it; negative: wrong-footed);
- `year_calib_mae`: the mean absolute gap between them;
- already there: the count and precision of rows at or over each score
  threshold by year (`n_at_thr_*`, `precision_at_thr_*`), which is the
  threshold rule itself. A useful model: precision at or over X at
  least X in most years, and the count falling in the bad years.

## What the record shows (cell C forest, seed 23, 112 ranks)

From `reports/forest_nonloser_dd30_3y.md` and
`forest_nonloser_dd30_isotonic_lag_3y.md` (2005–2020):

| test year | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base rate | .44 | .25 | .16 | .17 | .57 | .53 | .49 | .59 | .49 | .40 | .38 | .54 | .36 | .28 | .24 | .38 |
| conf_at_50 (raw) | .78 | .81 | .84 | .84 | .81 | .75 | .68 | .65 | .67 | .69 | .70 | .73 | .73 | .73 | .74 | .74 |
| rows ≥ 0.6 (raw) | 1276 | 1510 | 4191 | 4804 | 4677 | 2997 | 1356 | 561 | 805 | 1397 | 1898 | 2576 | 2711 | 2588 | 2784 | 2747 |

- The forest's confidence is **not** flat by year (the first guess, in
  decision 43, was that rank inputs would make it flat: wrong). It is
  **negatively** correlated with the year's base rate: −0.58 for its
  top 50. It was most confident for the entries of 2007–08 (base rate
  0.16–0.17) and least for 2011–13 (0.49–0.59, when its top 20 were
  right 95–100% of the time).
- The threshold rule run on it does the opposite of what is wanted:
  4,191 and 4,804 rows over 0.6 in 2007 and 2008, 561 in 2012.
- Prequential isotonic calibration with the honest lag (fold Y fitted
  only on folds f with f + 3 < Y) does not fix it: it calibrates on
  outcomes four or more years old and gave no row 0.5 in 2011–13.

**Why (a hypothesis with a first check):** the inputs are ranks within
the quarter, nearly the same distribution every quarter, so the score
*level* comes from the fit, and a fit's prior is the base rate of its
training window. The newest fully labeled rows of fold Y's window are
the entries of Y − 4 and Y − 5. Across the 16 folds:

| | corr |
|---|---|
| conf_at_50(Y) with base rate(Y) | −0.58 |
| … with base rate(Y − 2) | −0.65 |
| … with base rate(Y − 4) | +0.22 |
| … with base rate(Y − 5) | **+0.63** |
| base rate(Y) with base rate(Y − 3) / (Y − 4) | −0.24 / −0.27 |

The score level echoes the base rate of five years earlier, and the
three-year base rate tends to reverse over three to four years. So the
model is confident after good periods, which tend to precede bad ones.
Eleven to sixteen points: suggestive, not proven.

## What would have to be true for the threshold rule to work

P(stock does well | its features, the year) = the stock's standing
within the year *combined with* the year's level. The model has to get
both:

1. **The standing within the year.** The ranks do this (p@20 0.79
   against a base rate of 0.39), but the fit mixes it with the level
   of the training years.
2. **The level of the coming year.** Nothing a ranks-only model reads
   carries it, and no calibrator fitted on outcomes four years old can
   supply it. It needs inputs that carry the market's state, from which
   the model can learn how the level moves.

## The plan, in order of cost

### Step 1 — measure (code done, `claude/calibration`)

`mean_score`, `year_calib_corr`, `year_calib_mae` in every probabilistic
run, so every later step is judged on the same three numbers and on the
threshold tables.

### Step 2 — separate the two jobs: `year_balance` (code done)

`year_balance = true` reweights each fold's training rows so that
every snapshot year carries the pooled positive share (each year keeps
its total weight; the mandatory sample weights stay inside it). The
model can no longer take the market level of particular past years as
its prior; what is left to learn is which stocks of a year beat the
others. Expected: `year_calib_corr` near 0 (blind to the market, not
wrong-footed), p@20 the same or better (capacity no longer spent on
the era), the count over a threshold nearly constant by year.

This alone does not make the rule buy less in bad years; it removes
the wrong-way signal and gives a clean "standing within the year"
score to which a level can be added.

### Step 3 — give the model the level: raw-level inputs

The dataset's `features` group carries unranked columns whose
cross-section moves with the market: `vol_12m`, `vol_36m`, `beta_12m`,
`book_to_market`, earnings and cash-flow yields, `log_marketcap`,
`dollar_volume_3m`. In 2008 every stock's `vol_12m` is high; in a
bubble every stock's yields are low. A forest on the ranks plus these
can learn "high volatility everywhere → lower base rate" from the
training years. Selecting manifest columns is allowed (invariant 4);
deriving market aggregates (the median `vol_12m` of a date) is not, and
would be the upstream version of this step.

Arms, cell C, inside the 100k floor (where the candidate trades), on
the candidate forest's parameters: {ranks, ranks + level columns} ×
{plain, `year_balance`} = four runs, then the best with isotonic-lag
calibration. Read on `year_calib_corr`, the threshold tables by year,
and p@20 against the ranks-only forest.

**Risk, stated before the run:** the level→base-rate relationship is
learned from at most 2–3 market cycles in the training window (1998
onward); the walk-forward test is the honest check of whether it
carries to the next year. If it does not (`year_calib_corr` not above
+0.3 in walk-forward), the level has to come from upstream market-state
features (research plan item 8) and the rule waits for them.

### Step 4 — honest calibration on top

With the level in the model, prequential isotonic with the label lag
(already built) maps scores to probabilities. Platt (two parameters) is
the safer first choice with so few independent years.

### Step 5 — the portfolio rule

"Every stock over X, at most N positions, cash otherwise" already
exists in the backtest: a per-model `min_score` floor with a large
`top_k`, the engine holding cash when fewer stocks qualify. Run once a
model passes step 3's bar, at two or three values of X fixed before
the run.

### Alternatives considered

- **A peer-relative target** (beat stocks of the same size band): its
  base rate is about one half every year by construction, so it can be
  calibrated across eras easily, but a threshold rule on it buys about
  as many stocks in every year. It solves the calibration problem by
  giving up the market-timing part Carter wants. Upstream; still worth
  having as the within-year score of step 2.
- **Calibrating on partially observed outcomes** (a three-year label of
  2018 entries is already settled by 2020 for a stock that fell 30%):
  would shorten the lag, but needs the price panel, whose only
  registered use is the backtest's outcomes. Carter's call.
- **Recalibrating on the most recent fold only**: the lag is the label's
  horizon, not a choice; no fold newer than Y − 4 has outcomes.

## Decision rule for this branch (fixed before the runs)

A configuration is a calibration candidate if, in walk-forward
2005–2020 inside the 100k floor: `year_calib_corr` ≥ +0.3; p@20 no more
than 0.03 below the ranks-only forest's fold mean; and at a threshold
fixed before the run, precision over the threshold in every half at
least the threshold minus 0.05. A candidate goes to step 5's backtest.

## Result of step 3 (2026-11-23, decision 46)

No arm reached `year_calib_corr` ≥ +0.3 (best +0.07, ranks with
`year_balance`); the 15 level columns made it worse (−0.33 / −0.25),
and every arm's mean score is highest for the 2007–08 entries. The
threshold rule cannot be built on these inputs: tables and readings in
[downside, gates, calibration](2026-11-23-downside-gates-calibration.md)
§3. `year_balance` raised PR-AUC by 0.02–0.03 but not the top picks.

## Upstream request (for Carter to forward)

1. **Market-state columns**, one value per snapshot date, attached to
   every row of that date, built point-in-time upstream next to the
   split machinery:
   - cross-sectional medians (over the investable universe) of
     earnings yield, book to market, `vol_12m`, and of 12-month
     momentum;
   - breadth: the share of stocks above their 200-day average and
     the share at a 52-week high;
   - SPY's trailing 12-month return, volatility and drawdown from its
     high;
   - if a point-in-time source exists: the 10y–3m term spread and a
     corporate credit spread.
   These are aggregates across rows of a date, which is why they cannot
   be derived here (invariant 4).
2. **The peer-relative label**: "beat the stocks of the same
   `log_marketcap_rank` band (and quarter) over H years", the target
   whose base rate is about one half in every year.

With (1), step 3 is rerun with these columns in place of the per-stock
levels, under the same rule. With (2), a within-year probability can be
calibrated across eras (a constant-count rule), and combined with (1)
it is the decomposition the threshold rule needs.
