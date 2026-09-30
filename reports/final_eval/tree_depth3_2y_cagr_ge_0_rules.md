# Extracted tree rules — tree_depth3_2y_cagr_ge_0

- dataset version: `1.0`
- config hash: `319daa83f71fd5f0` — run `6e6fb0dc82d1`, git `3e538762292296d1a53cd3d83eb6feb9eebce253`, seed 7
- label: `label_2y_cagr_ge_0` (2y, scheme `holdout`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2022

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2816
  THEN P(positive) = 0.772   [weighted n = 5862.2, 10.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2816 (or missing)
  THEN P(positive) = 0.671   [weighted n = 5171.6, 8.9% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank > 0.819
  THEN P(positive) = 0.667   [weighted n = 969.1, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831
  THEN P(positive) = 0.633   [weighted n = 8974.2, 15.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.548   [weighted n = 1528.5, 2.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing)
  THEN P(positive) = 0.538   [weighted n = 5500.1, 9.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing)
  THEN P(positive) = 0.491   [weighted n = 11013.6, 19.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.390   [weighted n = 19054.3, 32.8% of training weight]
```
