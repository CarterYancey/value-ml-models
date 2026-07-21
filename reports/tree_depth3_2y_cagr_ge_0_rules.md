# Extracted tree rules — tree_depth3_2y_cagr_ge_0

- dataset version: `1.0`
- config hash: `7f129ded6dda6fab` — run `078055771e36`, git `bbe8af7a060ad8b80f16625731a4aa6df8d841c0`, seed 7
- label: `label_2y_cagr_ge_0` (2y, scheme `walkforward`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2004

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.4367 AND dist_52w_high_rank > 0.8065 AND dollar_volume_3m_rank <= 0.8238 (or missing)
  THEN P(positive) = 0.787   [weighted n = 738.0, 4.5% of training weight]
IF vol_12m_rank <= 0.4367 AND dist_52w_high_rank > 0.8065 AND dollar_volume_3m_rank > 0.8238
  THEN P(positive) = 0.635   [weighted n = 235.5, 1.4% of training weight]
IF vol_12m_rank <= 0.4367 AND dist_52w_high_rank <= 0.8065 (or missing) AND ocf_yield_rank > 0.5145 (or missing)
  THEN P(positive) = 0.600   [weighted n = 2276.3, 13.8% of training weight]
IF vol_12m_rank > 0.4367 (or missing) AND ext_financing_to_assets_rank <= 0.7335 (or missing) AND ffo_to_liabilities_rank > 0.4032
  THEN P(positive) = 0.480   [weighted n = 2635.1, 16.0% of training weight]
IF vol_12m_rank <= 0.4367 AND dist_52w_high_rank <= 0.8065 (or missing) AND ocf_yield_rank <= 0.5145
  THEN P(positive) = 0.441   [weighted n = 792.3, 4.8% of training weight]
IF vol_12m_rank > 0.4367 (or missing) AND ext_financing_to_assets_rank > 0.7335 AND ocf_yield_rank > 0.4345
  THEN P(positive) = 0.407   [weighted n = 488.6, 3.0% of training weight]
IF vol_12m_rank > 0.4367 (or missing) AND ext_financing_to_assets_rank <= 0.7335 (or missing) AND ffo_to_liabilities_rank <= 0.4032 (or missing)
  THEN P(positive) = 0.394   [weighted n = 7519.6, 45.7% of training weight]
IF vol_12m_rank > 0.4367 (or missing) AND ext_financing_to_assets_rank > 0.7335 AND ocf_yield_rank <= 0.4345 (or missing)
  THEN P(positive) = 0.279   [weighted n = 1777.3, 10.8% of training weight]
```

## Fold 2005

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank > 0.8065 AND dividend_yield_rank > 0.9086
  THEN P(positive) = 0.880   [weighted n = 300.5, 1.6% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank > 0.8065 AND dividend_yield_rank <= 0.9086 (or missing)
  THEN P(positive) = 0.741   [weighted n = 1060.1, 5.5% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank <= 0.8065 (or missing) AND ocf_yield_rank > 0.5218
  THEN P(positive) = 0.635   [weighted n = 2644.1, 13.7% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND share_count_growth_1y_rank <= 0.6552 AND roa_variability_3y_rank <= 0.8944
  THEN P(positive) = 0.596   [weighted n = 721.2, 3.7% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank <= 0.8065 (or missing) AND ocf_yield_rank <= 0.5218 (or missing)
  THEN P(positive) = 0.507   [weighted n = 1856.1, 9.7% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND share_count_growth_1y_rank <= 0.6552 AND roa_variability_3y_rank > 0.8944 (or missing)
  THEN P(positive) = 0.462   [weighted n = 3283.6, 17.1% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND share_count_growth_1y_rank > 0.6552 (or missing) AND tangible_book_to_market_rank > 0.1798 (or missing)
  THEN P(positive) = 0.405   [weighted n = 7378.1, 38.4% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND share_count_growth_1y_rank > 0.6552 (or missing) AND tangible_book_to_market_rank <= 0.1798
  THEN P(positive) = 0.308   [weighted n = 1990.1, 10.3% of training weight]
```

## Fold 2006

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.4948 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank > 0.5941
  THEN P(positive) = 0.841   [weighted n = 985.9, 4.5% of training weight]
IF vol_12m_rank <= 0.4948 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank <= 0.5941 (or missing)
  THEN P(positive) = 0.730   [weighted n = 679.1, 3.1% of training weight]
IF vol_12m_rank <= 0.4948 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank <= 0.6984
  THEN P(positive) = 0.726   [weighted n = 1963.6, 9.0% of training weight]
IF vol_12m_rank > 0.4948 (or missing) AND roa_variability_3y_rank <= 0.9038 AND conservative_score_rank > 0.1371
  THEN P(positive) = 0.633   [weighted n = 1311.2, 6.0% of training weight]
IF vol_12m_rank <= 0.4948 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank > 0.6984 (or missing)
  THEN P(positive) = 0.562   [weighted n = 3426.1, 15.7% of training weight]
IF vol_12m_rank > 0.4948 (or missing) AND roa_variability_3y_rank > 0.9038 (or missing) AND dist_52w_high_rank > 0.8078
  THEN P(positive) = 0.545   [weighted n = 980.2, 4.5% of training weight]
IF vol_12m_rank > 0.4948 (or missing) AND roa_variability_3y_rank <= 0.9038 AND conservative_score_rank <= 0.1371 (or missing)
  THEN P(positive) = 0.502   [weighted n = 562.1, 2.6% of training weight]
IF vol_12m_rank > 0.4948 (or missing) AND roa_variability_3y_rank > 0.9038 (or missing) AND dist_52w_high_rank <= 0.8078 (or missing)
  THEN P(positive) = 0.401   [weighted n = 11889.0, 54.5% of training weight]
```

## Fold 2007

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank > 0.5941
  THEN P(positive) = 0.849   [weighted n = 1142.3, 4.7% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank <= 0.5941 (or missing)
  THEN P(positive) = 0.744   [weighted n = 774.7, 3.2% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank <= 0.6936
  THEN P(positive) = 0.724   [weighted n = 2680.0, 11.0% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND roa_variability_3y_rank <= 0.8956 AND ocf_yield_rank > 0.4525
  THEN P(positive) = 0.646   [weighted n = 1265.0, 5.2% of training weight]
IF vol_12m_rank <= 0.4946 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank > 0.6936 (or missing)
  THEN P(positive) = 0.567   [weighted n = 3620.8, 14.8% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND roa_variability_3y_rank > 0.8956 (or missing) AND dist_52w_high_rank > 0.8073
  THEN P(positive) = 0.556   [weighted n = 1055.6, 4.3% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND roa_variability_3y_rank <= 0.8956 AND ocf_yield_rank <= 0.4525 (or missing)
  THEN P(positive) = 0.516   [weighted n = 1363.4, 5.6% of training weight]
IF vol_12m_rank > 0.4946 (or missing) AND roa_variability_3y_rank > 0.8956 (or missing) AND dist_52w_high_rank <= 0.8073 (or missing)
  THEN P(positive) = 0.403   [weighted n = 12497.3, 51.2% of training weight]
```

## Fold 2008

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5208 AND roa_variability_3y_rank <= 0.5244 AND vol_36m_rank <= 0.1095
  THEN P(positive) = 0.865   [weighted n = 976.4, 3.6% of training weight]
IF vol_12m_rank <= 0.5208 AND roa_variability_3y_rank > 0.5244 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.771   [weighted n = 1191.8, 4.4% of training weight]
IF vol_12m_rank <= 0.5208 AND roa_variability_3y_rank <= 0.5244 AND vol_36m_rank > 0.1095 (or missing)
  THEN P(positive) = 0.738   [weighted n = 2940.7, 10.9% of training weight]
IF vol_12m_rank > 0.5208 (or missing) AND roa_variability_3y_rank <= 0.8913 AND ocf_yield_rank > 0.4439
  THEN P(positive) = 0.645   [weighted n = 1479.6, 5.5% of training weight]
IF vol_12m_rank <= 0.5208 AND roa_variability_3y_rank > 0.5244 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.581   [weighted n = 4787.4, 17.7% of training weight]
IF vol_12m_rank > 0.5208 (or missing) AND roa_variability_3y_rank > 0.8913 (or missing) AND dist_52w_high_rank > 0.8073
  THEN P(positive) = 0.565   [weighted n = 1099.1, 4.1% of training weight]
IF vol_12m_rank > 0.5208 (or missing) AND roa_variability_3y_rank <= 0.8913 AND ocf_yield_rank <= 0.4439 (or missing)
  THEN P(positive) = 0.510   [weighted n = 1682.2, 6.2% of training weight]
IF vol_12m_rank > 0.5208 (or missing) AND roa_variability_3y_rank > 0.8913 (or missing) AND dist_52w_high_rank <= 0.8073 (or missing)
  THEN P(positive) = 0.405   [weighted n = 12857.2, 47.6% of training weight]
```

## Fold 2009

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank > 0.5942
  THEN P(positive) = 0.835   [weighted n = 1422.8, 4.8% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.8065 AND earnings_yield_rank <= 0.5942 (or missing)
  THEN P(positive) = 0.741   [weighted n = 1043.0, 3.5% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank <= 0.6847
  THEN P(positive) = 0.691   [weighted n = 4261.4, 14.4% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.3906 AND roa_variability_3y_rank <= 0.88
  THEN P(positive) = 0.610   [weighted n = 1940.6, 6.6% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.8065 (or missing) AND roa_variability_3y_rank > 0.6847 (or missing)
  THEN P(positive) = 0.563   [weighted n = 4385.3, 14.8% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.3906 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.547   [weighted n = 971.5, 3.3% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.3906 AND roa_variability_3y_rank > 0.88 (or missing)
  THEN P(positive) = 0.478   [weighted n = 3162.7, 10.7% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.3906 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.398   [weighted n = 12396.7, 41.9% of training weight]
```

## Fold 2010

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.518 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.898
  THEN P(positive) = 0.839   [weighted n = 686.7, 2.1% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.898 (or missing)
  THEN P(positive) = 0.724   [weighted n = 2347.4, 7.3% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank > 0.458 (or missing)
  THEN P(positive) = 0.609   [weighted n = 6983.4, 21.7% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank > 0.3902 AND dist_52w_high_rank > 0.4322
  THEN P(positive) = 0.566   [weighted n = 2236.6, 7.0% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank <= 0.3902 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.532   [weighted n = 1054.8, 3.3% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank <= 0.458
  THEN P(positive) = 0.493   [weighted n = 2240.5, 7.0% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank > 0.3902 AND dist_52w_high_rank <= 0.4322 (or missing)
  THEN P(positive) = 0.462   [weighted n = 3344.6, 10.4% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank <= 0.3902 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.383   [weighted n = 13229.3, 41.2% of training weight]
```

## Fold 2011

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.518 AND dist_52w_high_rank > 0.8189 AND dividend_yield_rank > 0.898
  THEN P(positive) = 0.837   [weighted n = 631.0, 1.8% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank > 0.8189 AND dividend_yield_rank <= 0.898 (or missing)
  THEN P(positive) = 0.712   [weighted n = 2197.5, 6.4% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank <= 0.8189 (or missing) AND ebitda_to_ev_rank > 0.4563 (or missing)
  THEN P(positive) = 0.605   [weighted n = 8027.0, 23.2% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank > 0.3902 AND dist_52w_high_rank > 0.4322
  THEN P(positive) = 0.557   [weighted n = 2398.1, 6.9% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank <= 0.3902 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.525   [weighted n = 1165.0, 3.4% of training weight]
IF vol_12m_rank <= 0.518 AND dist_52w_high_rank <= 0.8189 (or missing) AND ebitda_to_ev_rank <= 0.4563
  THEN P(positive) = 0.491   [weighted n = 2578.6, 7.5% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank > 0.3902 AND dist_52w_high_rank <= 0.4322 (or missing)
  THEN P(positive) = 0.462   [weighted n = 3648.7, 10.5% of training weight]
IF vol_12m_rank > 0.518 (or missing) AND ocf_yield_rank <= 0.3902 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.382   [weighted n = 13942.9, 40.3% of training weight]
```

## Fold 2012

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.8979
  THEN P(positive) = 0.836   [weighted n = 766.3, 2.1% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.8979 (or missing)
  THEN P(positive) = 0.710   [weighted n = 2977.2, 8.1% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank > 0.4635
  THEN P(positive) = 0.622   [weighted n = 7341.3, 19.9% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.4035 AND ret_6m_rank > 0.1028
  THEN P(positive) = 0.547   [weighted n = 4496.3, 12.2% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.4035 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.531   [weighted n = 1244.5, 3.4% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank <= 0.4635 (or missing)
  THEN P(positive) = 0.519   [weighted n = 3493.1, 9.5% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.4035 AND ret_6m_rank <= 0.1028 (or missing)
  THEN P(positive) = 0.446   [weighted n = 1861.0, 5.1% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.4035 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.388   [weighted n = 14635.9, 39.8% of training weight]
```

## Fold 2013

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.8979
  THEN P(positive) = 0.841   [weighted n = 821.1, 2.1% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.8979 (or missing)
  THEN P(positive) = 0.719   [weighted n = 3163.3, 8.1% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank > 0.4578
  THEN P(positive) = 0.629   [weighted n = 7990.4, 20.5% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.4035 AND roa_variability_3y_rank <= 0.8164
  THEN P(positive) = 0.573   [weighted n = 2938.5, 7.5% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.4035 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.535   [weighted n = 1298.6, 3.3% of training weight]
IF vol_12m_rank <= 0.5207 AND dist_52w_high_rank <= 0.7881 (or missing) AND ebitda_to_ev_rank <= 0.4578 (or missing)
  THEN P(positive) = 0.528   [weighted n = 3688.7, 9.4% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank > 0.4035 AND roa_variability_3y_rank > 0.8164 (or missing)
  THEN P(positive) = 0.479   [weighted n = 3883.2, 9.9% of training weight]
IF vol_12m_rank > 0.5207 (or missing) AND ocf_yield_rank <= 0.4035 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.389   [weighted n = 15262.2, 39.1% of training weight]
```

## Fold 2014

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.7787
  THEN P(positive) = 0.808   [weighted n = 1795.7, 4.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.7787 (or missing)
  THEN P(positive) = 0.708   [weighted n = 2495.5, 6.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank <= 0.6035
  THEN P(positive) = 0.648   [weighted n = 6776.8, 16.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank > 0.6035 (or missing)
  THEN P(positive) = 0.550   [weighted n = 6284.9, 15.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.4036 AND dist_52w_high_rank > 0.133 (or missing)
  THEN P(positive) = 0.544   [weighted n = 5319.3, 12.9% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.4036 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.538   [weighted n = 1327.4, 3.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.4036 AND dist_52w_high_rank <= 0.133
  THEN P(positive) = 0.428   [weighted n = 1561.1, 3.8% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.4036 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.388   [weighted n = 15663.4, 38.0% of training weight]
```

## Fold 2015

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.7788
  THEN P(positive) = 0.816   [weighted n = 1910.9, 4.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.7788 (or missing)
  THEN P(positive) = 0.718   [weighted n = 2633.4, 6.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank <= 0.6035
  THEN P(positive) = 0.664   [weighted n = 7326.5, 16.9% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank > 0.6035 (or missing)
  THEN P(positive) = 0.558   [weighted n = 6508.8, 15.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.3898 AND dist_52w_high_rank > 0.133 (or missing)
  THEN P(positive) = 0.551   [weighted n = 5791.2, 13.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.3898 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.545   [weighted n = 1365.1, 3.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.3898 AND dist_52w_high_rank <= 0.133
  THEN P(positive) = 0.430   [weighted n = 1670.6, 3.9% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.3898 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.393   [weighted n = 16111.1, 37.2% of training weight]
```

## Fold 2016

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank > 0.7788
  THEN P(positive) = 0.818   [weighted n = 1987.7, 4.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.7881 AND dividend_yield_rank <= 0.7788 (or missing)
  THEN P(positive) = 0.723   [weighted n = 2780.6, 6.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank <= 0.6102
  THEN P(positive) = 0.670   [weighted n = 7969.4, 17.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.7881 (or missing) AND roa_variability_3y_rank > 0.6102 (or missing)
  THEN P(positive) = 0.560   [weighted n = 6656.7, 14.7% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.3901 AND dist_52w_high_rank > 0.133 (or missing)
  THEN P(positive) = 0.554   [weighted n = 6089.7, 13.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.3901 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.550   [weighted n = 1424.8, 3.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank > 0.3901 AND dist_52w_high_rank <= 0.133
  THEN P(positive) = 0.428   [weighted n = 1743.9, 3.8% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ocf_yield_rank <= 0.3901 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.395   [weighted n = 16748.1, 36.9% of training weight]
```

## Fold 2017

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank > 0.665 AND vol_36m_rank <= 0.1943
  THEN P(positive) = 0.786   [weighted n = 3439.5, 7.2% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank > 0.665 AND vol_36m_rank > 0.1943 (or missing)
  THEN P(positive) = 0.684   [weighted n = 5243.8, 11.0% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank <= 0.665 (or missing) AND mohanram_g7_rank > 0.09834
  THEN P(positive) = 0.640   [weighted n = 6515.9, 13.7% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank > 0.39 AND dist_52w_high_rank > 0.133 (or missing)
  THEN P(positive) = 0.551   [weighted n = 6839.0, 14.4% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank <= 0.39 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.549   [weighted n = 1520.7, 3.2% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank <= 0.665 (or missing) AND mohanram_g7_rank <= 0.09834 (or missing)
  THEN P(positive) = 0.539   [weighted n = 4399.8, 9.3% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank > 0.39 AND dist_52w_high_rank <= 0.133
  THEN P(positive) = 0.422   [weighted n = 1834.5, 3.9% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank <= 0.39 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.392   [weighted n = 17764.0, 37.4% of training weight]
```

## Fold 2018

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank > 0.665 AND vol_36m_rank <= 0.1943
  THEN P(positive) = 0.788   [weighted n = 3625.6, 7.3% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank > 0.665 AND vol_36m_rank > 0.1943 (or missing)
  THEN P(positive) = 0.684   [weighted n = 5509.0, 11.1% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank <= 0.665 (or missing) AND mohanram_g7_rank > 0.09834
  THEN P(positive) = 0.640   [weighted n = 6924.6, 13.9% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank > 0.3901 AND dist_52w_high_rank > 0.1607 (or missing)
  THEN P(positive) = 0.553   [weighted n = 6771.3, 13.6% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank <= 0.3901 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.551   [weighted n = 1583.3, 3.2% of training weight]
IF vol_12m_rank <= 0.5191 AND dist_52w_high_rank <= 0.665 (or missing) AND mohanram_g7_rank <= 0.09834 (or missing)
  THEN P(positive) = 0.539   [weighted n = 4548.9, 9.1% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank > 0.3901 AND dist_52w_high_rank <= 0.1607
  THEN P(positive) = 0.427   [weighted n = 2299.8, 4.6% of training weight]
IF vol_12m_rank > 0.5191 (or missing) AND ocf_yield_rank <= 0.3901 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.391   [weighted n = 18507.5, 37.2% of training weight]
```

## Fold 2019

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6978 AND vol_36m_rank <= 0.1942
  THEN P(positive) = 0.797   [weighted n = 3459.7, 6.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6978 AND vol_36m_rank > 0.1942 (or missing)
  THEN P(positive) = 0.695   [weighted n = 5079.9, 9.8% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6978 (or missing) AND roa_variability_3y_rank <= 0.6395
  THEN P(positive) = 0.651   [weighted n = 8183.7, 15.8% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND revenue_growth_variability_3y_rank <= 0.7457
  THEN P(positive) = 0.569   [weighted n = 4435.8, 8.5% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6978 (or missing) AND roa_variability_3y_rank > 0.6395 (or missing)
  THEN P(positive) = 0.548   [weighted n = 5777.2, 11.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.544   [weighted n = 1375.8, 2.7% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND revenue_growth_variability_3y_rank > 0.7457 (or missing)
  THEN P(positive) = 0.470   [weighted n = 6313.9, 12.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.388   [weighted n = 17258.0, 33.3% of training weight]
```

## Fold 2020

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.1942
  THEN P(positive) = 0.792   [weighted n = 4008.5, 7.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.1942 (or missing)
  THEN P(positive) = 0.687   [weighted n = 6165.9, 11.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank > 0.819
  THEN P(positive) = 0.669   [weighted n = 920.6, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND roa_variability_3y_rank <= 0.6395
  THEN P(positive) = 0.641   [weighted n = 7882.2, 14.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.544   [weighted n = 1420.8, 2.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND roa_variability_3y_rank > 0.6395 (or missing)
  THEN P(positive) = 0.543   [weighted n = 5465.6, 10.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing)
  THEN P(positive) = 0.493   [weighted n = 10244.2, 19.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.387   [weighted n = 17858.8, 33.1% of training weight]
```

## Fold 2021

```
depth <= 3, 8 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.1943
  THEN P(positive) = 0.787   [weighted n = 4156.8, 7.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.1943 (or missing)
  THEN P(positive) = 0.681   [weighted n = 6371.2, 11.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank > 0.8192
  THEN P(positive) = 0.665   [weighted n = 950.0, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09836
  THEN P(positive) = 0.630   [weighted n = 8594.8, 15.3% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065
  THEN P(positive) = 0.544   [weighted n = 1475.5, 2.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09836 (or missing)
  THEN P(positive) = 0.536   [weighted n = 5380.0, 9.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.8192 (or missing)
  THEN P(positive) = 0.487   [weighted n = 10624.4, 19.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing)
  THEN P(positive) = 0.385   [weighted n = 18454.0, 32.9% of training weight]
```
