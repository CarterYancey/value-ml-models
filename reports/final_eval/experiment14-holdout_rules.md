# Extracted tree rules — experiment14-holdout

- dataset version: `1.0`
- config hash: `93196a10ed201fec` — run `71995d92b0cf`, git `3e538762292296d1a53cd3d83eb6feb9eebce253`, seed 9
- label: `label_2y_cagr_ge_0` (2y, scheme `holdout`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2022

```
depth <= 10, 76 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank > 0.8489 AND vol_36m_rank <= 0.05115
  THEN P(positive) = 0.840   [weighted n = 703.0, 1.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank > 0.8489 AND vol_36m_rank > 0.05115 (or missing) AND tangible_book_to_market_secrank <= 0.363 (or missing)
  THEN P(positive) = 0.800   [weighted n = 844.7, 1.5% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank <= 0.8489 (or missing) AND mohanram_g7_rank > 0.09952 AND ebit_to_ev_rank > 0.5572 AND vol_36m_rank <= 0.1082
  THEN P(positive) = 0.780   [weighted n = 814.4, 1.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank > 0.8216 AND dist_52w_high_rank > 0.9474
  THEN P(positive) = 0.760   [weighted n = 586.3, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank > 0.8489 AND vol_36m_rank > 0.05115 (or missing) AND tangible_book_to_market_secrank > 0.363
  THEN P(positive) = 0.739   [weighted n = 672.0, 1.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank > 0.002283 AND earnings_yield_rank > 0.6988 (or missing)
  THEN P(positive) = 0.736   [weighted n = 635.8, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank <= 0.8489 (or missing) AND mohanram_g7_rank > 0.09952 AND ebit_to_ev_rank > 0.5572 AND vol_36m_rank > 0.1082 (or missing)
  THEN P(positive) = 0.727   [weighted n = 920.3, 1.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank > 0.8216 AND dist_52w_high_rank <= 0.9474 (or missing) AND ocf_yield_rank > 0.4709
  THEN P(positive) = 0.703   [weighted n = 966.2, 1.7% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank <= 0.8489 (or missing) AND mohanram_g7_rank > 0.09952 AND ebit_to_ev_rank <= 0.5572 (or missing)
  THEN P(positive) = 0.692   [weighted n = 583.0, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank <= 0.8216 (or missing) AND revenue_growth_variability_3y_rank <= 0.6878 AND piotroski_f_rank > 0.628 (or missing)
  THEN P(positive) = 0.682   [weighted n = 609.1, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank <= 0.002283 (or missing) AND rnd_to_assets_rank <= 0.00154 (or missing) AND vol_36m_rank <= 0.1146 (or missing)
  THEN P(positive) = 0.680   [weighted n = 585.9, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing) AND asset_turnover_rank > 0.3406 (or missing) AND roa_variability_3y_rank <= 0.4783 (or missing) AND gp_to_assets_rank > 0.6755
  THEN P(positive) = 0.672   [weighted n = 633.1, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank > 0.002283 AND earnings_yield_rank <= 0.6988
  THEN P(positive) = 0.663   [weighted n = 633.7, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank <= 0.2541 AND dist_52w_high_rank <= 0.8489 (or missing) AND mohanram_g7_rank <= 0.09952 (or missing)
  THEN P(positive) = 0.642   [weighted n = 703.4, 1.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank > 0.8216 AND dist_52w_high_rank <= 0.9474 (or missing) AND ocf_yield_rank <= 0.4709 (or missing)
  THEN P(positive) = 0.640   [weighted n = 735.9, 1.3% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank > 0.819
  THEN P(positive) = 0.633   [weighted n = 950.2, 1.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank <= 0.8216 (or missing) AND revenue_growth_variability_3y_rank <= 0.6878 AND piotroski_f_rank <= 0.628
  THEN P(positive) = 0.625   [weighted n = 868.9, 1.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing) AND mom_12_2_rank <= 0.8314 AND rnd_to_assets_rank > 0.001605 (or missing) AND marketcap_to_liabilities_rank <= 0.6735 AND dist_52w_high_rank > 0.3097 (or missing)
  THEN P(positive) = 0.623   [weighted n = 736.2, 1.3% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank <= 0.002283 (or missing) AND rnd_to_assets_rank <= 0.00154 (or missing) AND vol_36m_rank > 0.1146
  THEN P(positive) = 0.616   [weighted n = 677.8, 1.2% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing) AND asset_turnover_rank > 0.3406 (or missing) AND roa_variability_3y_rank <= 0.4783 (or missing) AND gp_to_assets_rank <= 0.6755 (or missing)
  THEN P(positive) = 0.616   [weighted n = 775.4, 1.3% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing) AND asset_turnover_rank > 0.3406 (or missing) AND roa_variability_3y_rank > 0.4783 AND ocf_yield_rank > 0.5426
  THEN P(positive) = 0.616   [weighted n = 597.8, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank <= 0.2674 AND rnd_to_assets_rank > 0.002571
  THEN P(positive) = 0.612   [weighted n = 632.1, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank <= 0.8216 (or missing) AND revenue_growth_variability_3y_rank > 0.6878 (or missing) AND book_to_market_rank > 0.3597 (or missing)
  THEN P(positive) = 0.594   [weighted n = 1071.2, 1.8% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank <= 0.2333 (or missing) AND rnd_to_assets_rank <= 0.002283 (or missing) AND rnd_to_assets_rank > 0.00154
  THEN P(positive) = 0.572   [weighted n = 586.9, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank <= 0.001803 AND dist_52w_high_rank > 0.3746 (or missing) AND capex_to_assets_rank <= 0.6971 (or missing)
  THEN P(positive) = 0.570   [weighted n = 953.8, 1.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065 AND tangible_book_to_market_rank > 0.09501
  THEN P(positive) = 0.569   [weighted n = 791.1, 1.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing) AND mom_12_2_rank <= 0.8314 AND rnd_to_assets_rank > 0.001605 (or missing) AND marketcap_to_liabilities_rank <= 0.6735 AND dist_52w_high_rank <= 0.3097
  THEN P(positive) = 0.561   [weighted n = 618.4, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing) AND asset_turnover_rank > 0.3406 (or missing) AND roa_variability_3y_rank > 0.4783 AND ocf_yield_rank <= 0.5426 (or missing)
  THEN P(positive) = 0.553   [weighted n = 582.9, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank > 0.2674 (or missing) AND ext_financing_to_assets_rank <= 0.6677 AND ret_1m_rank > 0.359 (or missing)
  THEN P(positive) = 0.544   [weighted n = 906.4, 1.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank <= 0.2674 AND rnd_to_assets_rank <= 0.002571 (or missing)
  THEN P(positive) = 0.530   [weighted n = 837.6, 1.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank > 0.001803 (or missing) AND asset_turnover_rank <= 0.3406
  THEN P(positive) = 0.527   [weighted n = 856.9, 1.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank > 0.156 (or missing) AND vol_36m_rank <= 0.638
  THEN P(positive) = 0.518   [weighted n = 611.5, 1.1% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank <= 0.001803 AND dist_52w_high_rank > 0.3746 (or missing) AND capex_to_assets_rank > 0.6971
  THEN P(positive) = 0.518   [weighted n = 699.4, 1.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank > 0.527 AND rnd_to_assets_rank > 0.001803 (or missing) AND gross_margin_rank > 0.6265 (or missing)
  THEN P(positive) = 0.517   [weighted n = 630.5, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing) AND mom_12_2_rank <= 0.8314 AND rnd_to_assets_rank > 0.001605 (or missing) AND marketcap_to_liabilities_rank > 0.6735 (or missing)
  THEN P(positive) = 0.508   [weighted n = 607.1, 1.0% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank > 0.6649 AND vol_36m_rank > 0.2541 (or missing) AND dist_52w_high_rank <= 0.8216 (or missing) AND revenue_growth_variability_3y_rank > 0.6878 (or missing) AND book_to_market_rank <= 0.3597
  THEN P(positive) = 0.507   [weighted n = 643.9, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing) AND mom_12_2_rank <= 0.8314 AND rnd_to_assets_rank <= 0.001605
  THEN P(positive) = 0.499   [weighted n = 1037.0, 1.8% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank > 0.2674 (or missing) AND ext_financing_to_assets_rank <= 0.6677 AND ret_1m_rank <= 0.359
  THEN P(positive) = 0.490   [weighted n = 587.0, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank > 0.156 (or missing) AND vol_36m_rank > 0.638 (or missing) AND ebitda_to_ev_secrank > 0.6673 (or missing)
  THEN P(positive) = 0.481   [weighted n = 1021.2, 1.8% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank <= 0.3946 AND gp_to_assets_secrank > 0.2175
  THEN P(positive) = 0.480   [weighted n = 903.6, 1.6% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank > 0.09831 AND vol_36m_rank > 0.2333 AND rnd_to_assets_rank <= 0.001803 AND dist_52w_high_rank <= 0.3746
  THEN P(positive) = 0.476   [weighted n = 625.1, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank > 0.1201 (or missing) AND mom_12_2_rank > 0.8314 (or missing)
  THEN P(positive) = 0.476   [weighted n = 1070.5, 1.8% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank > 0.3946 (or missing) AND vol_12m_rank > 0.2674 (or missing) AND ext_financing_to_assets_rank > 0.6677 (or missing)
  THEN P(positive) = 0.461   [weighted n = 1022.4, 1.8% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank > 0.527 AND rnd_to_assets_rank > 0.001803 (or missing) AND gross_margin_rank <= 0.6265
  THEN P(positive) = 0.455   [weighted n = 660.6, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank > 0.8065 AND tangible_book_to_market_rank <= 0.09501 (or missing)
  THEN P(positive) = 0.449   [weighted n = 734.9, 1.3% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank <= 0.527 (or missing) AND gp_to_assets_rank > 0.5086
  THEN P(positive) = 0.448   [weighted n = 591.0, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank > 0.156 (or missing) AND vol_36m_rank > 0.638 (or missing) AND ebitda_to_ev_secrank <= 0.6673 AND mom_12_2_rank <= 0.4529 (or missing)
  THEN P(positive) = 0.443   [weighted n = 785.4, 1.4% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank > 0.7964 AND tangible_book_to_market_rank > 0.3924 (or missing) AND ev_to_marketcap_rank <= 0.2087
  THEN P(positive) = 0.438   [weighted n = 707.9, 1.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank > 0.3338 (or missing) AND amihud_12m_rank > 0.9422
  THEN P(positive) = 0.435   [weighted n = 581.2, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank <= 0.527 (or missing) AND gp_to_assets_rank <= 0.5086 (or missing) AND rnd_to_assets_rank <= 0.002437 (or missing)
  THEN P(positive) = 0.431   [weighted n = 865.7, 1.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank > 0.527 AND rnd_to_assets_rank <= 0.001803
  THEN P(positive) = 0.421   [weighted n = 589.6, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank <= 0.156 AND ev_to_marketcap_rank <= 0.6653
  THEN P(positive) = 0.416   [weighted n = 603.6, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank > 0.7634 (or missing) AND dist_52w_high_rank > 0.4346
  THEN P(positive) = 0.409   [weighted n = 751.8, 1.3% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank > 0.3338 (or missing) AND amihud_12m_rank <= 0.9422 (or missing) AND marketcap_to_liabilities_rank > 0.07238 (or missing) AND dist_52w_high_rank > 0.4355
  THEN P(positive) = 0.403   [weighted n = 927.1, 1.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank > 0.7964 AND tangible_book_to_market_rank > 0.3924 (or missing) AND ev_to_marketcap_rank > 0.2087 (or missing) AND amihud_12m_rank > 0.9003
  THEN P(positive) = 0.399   [weighted n = 653.4, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank <= 0.7478 AND dist_52w_high_rank <= 0.1201
  THEN P(positive) = 0.399   [weighted n = 681.4, 1.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank > 0.2615 AND roa_variability_3y_rank <= 0.8855
  THEN P(positive) = 0.391   [weighted n = 839.2, 1.4% of training weight]
IF vol_12m_rank <= 0.5404 AND dist_52w_high_rank <= 0.6649 (or missing) AND mohanram_g7_rank <= 0.09831 (or missing) AND roa_rank <= 0.3946 AND gp_to_assets_secrank <= 0.2175 (or missing)
  THEN P(positive) = 0.387   [weighted n = 610.3, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank > 0.156 (or missing) AND vol_36m_rank > 0.638 (or missing) AND ebitda_to_ev_secrank <= 0.6673 AND mom_12_2_rank > 0.4529
  THEN P(positive) = 0.383   [weighted n = 593.9, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank > 0.3338 (or missing) AND amihud_12m_rank <= 0.9422 (or missing) AND marketcap_to_liabilities_rank > 0.07238 (or missing) AND dist_52w_high_rank <= 0.4355 (or missing) AND ev_to_marketcap_rank <= 0.558 (or missing)
  THEN P(positive) = 0.364   [weighted n = 2745.0, 4.7% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank > 0.7634 (or missing) AND dist_52w_high_rank <= 0.4346 (or missing) AND ret_6m_rank > 0.09672
  THEN P(positive) = 0.364   [weighted n = 765.9, 1.3% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank > 0.2615 AND roa_variability_3y_rank > 0.8855 (or missing) AND gp_to_assets_rank > 0.7263
  THEN P(positive) = 0.355   [weighted n = 693.7, 1.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank <= 0.3338 AND rnd_to_assets_rank <= 0.002438 (or missing)
  THEN P(positive) = 0.352   [weighted n = 997.8, 1.7% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank <= 0.7634 AND dist_52w_high_rank <= 0.156 AND ev_to_marketcap_rank > 0.6653 (or missing)
  THEN P(positive) = 0.351   [weighted n = 623.6, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank <= 0.7964 (or missing) AND book_to_market_rank <= 0.527 (or missing) AND gp_to_assets_rank <= 0.5086 (or missing) AND rnd_to_assets_rank > 0.002437
  THEN P(positive) = 0.327   [weighted n = 669.3, 1.2% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank <= 0.2615 (or missing) AND operating_margin_secrank > 0.08718 (or missing) AND ncav_to_marketcap_rank > 0.7044 (or missing)
  THEN P(positive) = 0.322   [weighted n = 654.6, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank > 0.7964 AND tangible_book_to_market_rank > 0.3924 (or missing) AND ev_to_marketcap_rank > 0.2087 (or missing) AND amihud_12m_rank <= 0.9003 (or missing)
  THEN P(positive) = 0.320   [weighted n = 600.3, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank > 0.3338 (or missing) AND amihud_12m_rank <= 0.9422 (or missing) AND marketcap_to_liabilities_rank > 0.07238 (or missing) AND dist_52w_high_rank <= 0.4355 (or missing) AND ev_to_marketcap_rank > 0.558
  THEN P(positive) = 0.312   [weighted n = 591.6, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank > 0.3007 AND dist_52w_high_rank <= 0.819 (or missing) AND revenue_growth_variability_3y_rank > 0.7478 (or missing) AND share_count_growth_1y_rank > 0.7634 (or missing) AND dist_52w_high_rank <= 0.4346 (or missing) AND ret_6m_rank <= 0.09672 (or missing)
  THEN P(positive) = 0.305   [weighted n = 583.3, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank > 0.09727 AND vol_12m_rank > 0.7964 AND tangible_book_to_market_rank <= 0.3924
  THEN P(positive) = 0.303   [weighted n = 881.4, 1.5% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank > 0.2615 AND roa_variability_3y_rank > 0.8855 (or missing) AND gp_to_assets_rank <= 0.7263 (or missing)
  THEN P(positive) = 0.294   [weighted n = 1141.3, 2.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank <= 0.2615 (or missing) AND operating_margin_secrank > 0.08718 (or missing) AND ncav_to_marketcap_rank <= 0.7044
  THEN P(positive) = 0.274   [weighted n = 948.7, 1.6% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank > 0.3338 (or missing) AND amihud_12m_rank <= 0.9422 (or missing) AND marketcap_to_liabilities_rank <= 0.07238
  THEN P(positive) = 0.272   [weighted n = 610.6, 1.1% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank <= 0.2615 (or missing) AND operating_margin_secrank <= 0.08718 AND tangible_book_to_market_secrank > 0.3613
  THEN P(positive) = 0.270   [weighted n = 591.0, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank <= 0.7912 (or missing) AND ret_6m_rank <= 0.09727 (or missing) AND tangible_book_to_market_secrank <= 0.3338 AND rnd_to_assets_rank > 0.002438
  THEN P(positive) = 0.216   [weighted n = 590.1, 1.0% of training weight]
IF vol_12m_rank > 0.5404 (or missing) AND ffo_to_liabilities_rank <= 0.3007 (or missing) AND dist_52w_high_rank <= 0.8065 (or missing) AND ext_financing_to_assets_rank > 0.7912 AND gp_to_assets_secrank <= 0.2615 (or missing) AND operating_margin_secrank <= 0.08718 AND tangible_book_to_market_secrank <= 0.3613 (or missing)
  THEN P(positive) = 0.205   [weighted n = 717.2, 1.2% of training weight]
```
