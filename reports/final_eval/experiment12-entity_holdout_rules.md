# Extracted tree rules — experiment12-entity_holdout

- dataset version: `1.0`
- config hash: `b6b7493449556222` — run `dfceeac81a9a`, git `3e538762292296d1a53cd3d83eb6feb9eebce253`, seed 7
- label: `label_2y_cagr_ge_8` (2y, scheme `holdout`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2022

```
depth <= 4, 15 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF ocf_yield > 0.04479 AND conservative_score > 1.404 AND dist_52w_high <= -0.0169 (or missing) AND conservative_score > 2.167
  THEN P(positive) = 0.594   [weighted n = 3940.2, 6.8% of training weight]
IF ocf_yield > 0.04479 AND conservative_score > 1.404 AND dist_52w_high <= -0.0169 (or missing) AND conservative_score <= 2.167 (or missing)
  THEN P(positive) = 0.523   [weighted n = 9168.1, 15.8% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score > 1.635 AND dist_52w_high <= -0.0145 (or missing) AND revenue_growth_3y > -0.1533
  THEN P(positive) = 0.469   [weighted n = 1989.9, 3.4% of training weight]
IF ocf_yield > 0.04479 AND conservative_score > 1.404 AND dist_52w_high > -0.0169 AND conservative_score > 2.2
  THEN P(positive) = 0.467   [weighted n = 1467.6, 2.5% of training weight]
IF ocf_yield > 0.04479 AND conservative_score <= 1.404 (or missing) AND dist_52w_high <= -0.02005 (or missing) AND tangible_book_to_market <= 20.42 (or missing)
  THEN P(positive) = 0.454   [weighted n = 8830.3, 15.2% of training weight]
IF ocf_yield > 0.04479 AND conservative_score > 1.404 AND dist_52w_high > -0.0169 AND conservative_score <= 2.2 (or missing)
  THEN P(positive) = 0.390   [weighted n = 2225.5, 3.8% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score > 1.635 AND dist_52w_high <= -0.0145 (or missing) AND revenue_growth_3y <= -0.1533 (or missing)
  THEN P(positive) = 0.384   [weighted n = 590.4, 1.0% of training weight]
IF ocf_yield > 0.04479 AND conservative_score <= 1.404 (or missing) AND dist_52w_high > -0.02005 AND net_debt_to_ebitda > 2.729 (or missing)
  THEN P(positive) = 0.348   [weighted n = 592.1, 1.0% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score <= 1.635 (or missing) AND tangible_book_to_market > 0.1159 (or missing) AND conservative_score > 0.4996 (or missing)
  THEN P(positive) = 0.346   [weighted n = 22195.1, 38.2% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score > 1.635 AND dist_52w_high > -0.0145
  THEN P(positive) = 0.342   [weighted n = 1040.8, 1.8% of training weight]
IF ocf_yield > 0.04479 AND conservative_score <= 1.404 (or missing) AND dist_52w_high > -0.02005 AND net_debt_to_ebitda <= 2.729
  THEN P(positive) = 0.309   [weighted n = 854.6, 1.5% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score <= 1.635 (or missing) AND tangible_book_to_market <= 0.1159 AND tangible_book_to_market > 0.06208 (or missing)
  THEN P(positive) = 0.270   [weighted n = 1295.3, 2.2% of training weight]
IF ocf_yield > 0.04479 AND conservative_score <= 1.404 (or missing) AND dist_52w_high <= -0.02005 (or missing) AND tangible_book_to_market > 20.42
  THEN P(positive) = 0.268   [weighted n = 583.5, 1.0% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score <= 1.635 (or missing) AND tangible_book_to_market > 0.1159 (or missing) AND conservative_score <= 0.4996
  THEN P(positive) = 0.248   [weighted n = 2163.3, 3.7% of training weight]
IF ocf_yield <= 0.04479 (or missing) AND conservative_score <= 1.635 (or missing) AND tangible_book_to_market <= 0.1159 AND tangible_book_to_market <= 0.06208
  THEN P(positive) = 0.207   [weighted n = 1136.9, 2.0% of training weight]
```
