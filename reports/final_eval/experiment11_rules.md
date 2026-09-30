# Extracted tree rules — experiment11

- dataset version: `1.0`
- config hash: `77e2629f49d8d1f7` — run `8db6f3a12152`, git `3e538762292296d1a53cd3d83eb6feb9eebce253`, seed 8
- label: `label_2y_cagr_ge_0` (2y, scheme `holdout`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2022

```
depth <= 5, 27 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2816 AND dist_52w_high_rank > 0.8487 AND vol_36m_rank <= 0.07182
  THEN P(positive) = 0.851   [weighted n = 969.8, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2816 AND dist_52w_high_rank > 0.8487 AND vol_36m_rank > 0.07182 (or missing)
  THEN P(positive) = 0.793   [weighted n = 1494.2, 2.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2816 (or missing) AND dist_52w_high_rank > 0.8226 AND dist_52w_high_rank > 0.9422
  THEN P(positive) = 0.778   [weighted n = 638.5, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2816 AND dist_52w_high_rank <= 0.8487 (or missing) AND mohanram_g7_rank > 0.09952
  THEN P(positive) = 0.760   [weighted n = 2606.6, 4.5% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank > 0.002283
  THEN P(positive) = 0.730   [weighted n = 1307.4, 2.3% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2816 (or missing) AND dist_52w_high_rank > 0.8226 AND dist_52w_high_rank <= 0.9422 (or missing)
  THEN P(positive) = 0.703   [weighted n = 1529.0, 2.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2816 (or missing) AND dist_52w_high_rank <= 0.8226 (or missing) AND revenue_growth_variability_3y_rank <= 0.6837
  THEN P(positive) = 0.678   [weighted n = 1334.3, 2.3% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2816 AND dist_52w_high_rank <= 0.8487 (or missing) AND mohanram_g7_rank <= 0.09952 (or missing)
  THEN P(positive) = 0.674   [weighted n = 791.6, 1.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank > 0.819
  THEN P(positive) = 0.667   [weighted n = 969.1, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank <= 0.002283 (or missing)
  THEN P(positive) = 0.657   [weighted n = 1884.5, 3.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing)
  THEN P(positive) = 0.629   [weighted n = 3494.2, 6.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank <= 0.2674
  THEN P(positive) = 0.602   [weighted n = 1484.1, 2.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065 AND book_to_market_rank > 0.07926
  THEN P(positive) = 0.597   [weighted n = 921.1, 1.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2816 (or missing) AND dist_52w_high_rank <= 0.8226 (or missing) AND revenue_growth_variability_3y_rank > 0.6837 (or missing)
  THEN P(positive) = 0.596   [weighted n = 1669.8, 2.9% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank <= 0.001803
  THEN P(positive) = 0.566   [weighted n = 2288.0, 3.9% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing)
  THEN P(positive) = 0.563   [weighted n = 4085.2, 7.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank > 0.2674 (or missing)
  THEN P(positive) = 0.535   [weighted n = 2515.1, 4.3% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank <= 0.3946 AND gp_to_assets_secrank > 0.2175
  THEN P(positive) = 0.518   [weighted n = 901.0, 1.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065 AND book_to_market_rank <= 0.07926 (or missing)
  THEN P(positive) = 0.475   [weighted n = 607.4, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634
  THEN P(positive) = 0.474   [weighted n = 4199.3, 7.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727
  THEN P(positive) = 0.440   [weighted n = 6750.4, 11.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank <= 0.1201
  THEN P(positive) = 0.436   [weighted n = 671.1, 1.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank <= 0.3946 AND gp_to_assets_secrank <= 0.2175 (or missing)
  THEN P(positive) = 0.423   [weighted n = 600.0, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank > 0.7634 (or missing)
  THEN P(positive) = 0.399   [weighted n = 2058.0, 3.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing)
  THEN P(positive) = 0.384   [weighted n = 6883.8, 11.9% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank > 0.2615
  THEN P(positive) = 0.375   [weighted n = 2610.3, 4.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank <= 0.2615 (or missing)
  THEN P(positive) = 0.297   [weighted n = 2809.8, 4.8% of training weight]
```
