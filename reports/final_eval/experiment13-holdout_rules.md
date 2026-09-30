# Extracted tree rules — experiment13-holdout

- dataset version: `1.0`
- config hash: `f9ed15c8cd5f7f3e` — run `bde2efbf6302`, git `3e538762292296d1a53cd3d83eb6feb9eebce253`, seed 8
- label: `label_2y_beat_spy` (2y, scheme `holdout`)

One tree per walk-forward fold (each refit on its expanding window). P(positive) is the leaf's weighted in-sample frequency — rank by it, don't read it as a calibrated forward probability.

## Fold 2022

```
depth <= 10, 75 leaves; P(positive) is weighted in-sample frequency (uncalibrated)

IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank <= 0.2892 AND rnd_to_assets_rank > 0.003508
  THEN P(positive) = 0.881   [weighted n = 958.3, 1.7% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank <= 0.2886 AND dist_52w_high_rank > 0.3611 (or missing) AND rnd_to_assets_rank > 0.003071 (or missing) AND vol_12m_rank <= 0.2978 (or missing)
  THEN P(positive) = 0.810   [weighted n = 642.9, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank <= 0.2892 AND rnd_to_assets_rank <= 0.003508 (or missing) AND vol_36m_rank <= 0.06758 (or missing)
  THEN P(positive) = 0.799   [weighted n = 598.5, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank > 0.2892 (or missing) AND roa_variability_3y_rank <= 0.09316 (or missing)
  THEN P(positive) = 0.741   [weighted n = 644.3, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank <= 0.2892 AND rnd_to_assets_rank <= 0.003508 (or missing) AND vol_36m_rank > 0.06758
  THEN P(positive) = 0.724   [weighted n = 646.5, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank <= 0.2886 AND dist_52w_high_rank > 0.3611 (or missing) AND rnd_to_assets_rank > 0.003071 (or missing) AND vol_12m_rank > 0.2978
  THEN P(positive) = 0.715   [weighted n = 628.9, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank > 0.002078 AND revenue_growth_variability_3y_rank <= 0.2979 (or missing) AND book_to_market_rank > 0.4564 (or missing)
  THEN P(positive) = 0.689   [weighted n = 665.0, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank <= 0.2886 AND dist_52w_high_rank > 0.3611 (or missing) AND rnd_to_assets_rank <= 0.003071
  THEN P(positive) = 0.678   [weighted n = 752.9, 1.3% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank <= 0.002521 AND mom_12_2_rank <= 0.8161 AND ebit_to_ev_rank > 0.6204
  THEN P(positive) = 0.674   [weighted n = 849.4, 1.5% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank > 0.2892 (or missing) AND roa_variability_3y_rank > 0.09316 AND vol_36m_rank <= 0.2516 (or missing)
  THEN P(positive) = 0.673   [weighted n = 625.0, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank > 0.6955 AND roa_variability_3y_rank <= 0.08164 (or missing)
  THEN P(positive) = 0.641   [weighted n = 634.5, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank > 0.002078 AND revenue_growth_variability_3y_rank <= 0.2979 (or missing) AND book_to_market_rank <= 0.4564
  THEN P(positive) = 0.621   [weighted n = 581.2, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank <= 0.2886 AND dist_52w_high_rank <= 0.3611
  THEN P(positive) = 0.618   [weighted n = 929.6, 1.6% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank > 0.5964 AND rnd_to_assets_rank > 0.0006491 (or missing) AND vol_36m_rank <= 0.2875 (or missing) AND zmijewski_rank > 0.4657
  THEN P(positive) = 0.617   [weighted n = 836.2, 1.4% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank <= 0.002521 AND mom_12_2_rank <= 0.8161 AND ebit_to_ev_rank <= 0.6204 (or missing)
  THEN P(positive) = 0.614   [weighted n = 588.0, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank > 0.6174 AND dividend_yield_rank > 0.00208 (or missing) AND beneish_m_rank <= 0.7408
  THEN P(positive) = 0.601   [weighted n = 765.9, 1.3% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank > 0.4654 AND ret_1m_rank > 0.3342 (or missing)
  THEN P(positive) = 0.596   [weighted n = 1036.7, 1.8% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank > 0.6955 AND roa_variability_3y_rank > 0.08164 AND vol_12m_rank <= 0.321 (or missing)
  THEN P(positive) = 0.596   [weighted n = 619.4, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank > 0.002078 AND revenue_growth_variability_3y_rank > 0.2979 AND dividend_yield_rank <= 0.007006
  THEN P(positive) = 0.594   [weighted n = 687.3, 1.2% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank <= 0.7813 AND dividend_yield_rank > 0.002599 (or missing) AND sales_yield_secrank > 0.4539
  THEN P(positive) = 0.587   [weighted n = 849.9, 1.5% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank <= 0.4654 (or missing) AND ret_1m_rank > 0.228 (or missing) AND rnd_to_assets_rank <= 0.002103 (or missing) AND rnd_to_assets_rank > 0.00178 (or missing)
  THEN P(positive) = 0.580   [weighted n = 591.2, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank > 0.002521 (or missing) AND rnd_to_assets_rank > 0.2892 (or missing) AND roa_variability_3y_rank > 0.09316 AND vol_36m_rank > 0.2516
  THEN P(positive) = 0.579   [weighted n = 619.4, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank > 0.6961 AND rnd_to_assets_rank <= 0.002521 AND mom_12_2_rank > 0.8161 (or missing)
  THEN P(positive) = 0.555   [weighted n = 597.6, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank > 0.4654 AND ret_1m_rank <= 0.3342
  THEN P(positive) = 0.549   [weighted n = 585.3, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank <= 0.002078 (or missing) AND gp_to_assets_rank > 0.5918 (or missing)
  THEN P(positive) = 0.543   [weighted n = 782.3, 1.4% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank > 0.002078 AND revenue_growth_variability_3y_rank > 0.2979 AND dividend_yield_rank > 0.007006 (or missing)
  THEN P(positive) = 0.542   [weighted n = 766.7, 1.3% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank <= 0.7813 AND dividend_yield_rank <= 0.002599 AND gp_to_assets_secrank > 0.413 AND ebitda_to_ev_secrank > 0.5092 (or missing)
  THEN P(positive) = 0.540   [weighted n = 618.9, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank > 0.6955 AND roa_variability_3y_rank > 0.08164 AND vol_12m_rank > 0.321
  THEN P(positive) = 0.540   [weighted n = 579.7, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank <= 0.4654 (or missing) AND ret_1m_rank > 0.228 (or missing) AND rnd_to_assets_rank <= 0.002103 (or missing) AND rnd_to_assets_rank <= 0.00178
  THEN P(positive) = 0.535   [weighted n = 695.3, 1.2% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank > 0.5964 AND rnd_to_assets_rank > 0.0006491 (or missing) AND vol_36m_rank <= 0.2875 (or missing) AND zmijewski_rank <= 0.4657 (or missing)
  THEN P(positive) = 0.535   [weighted n = 960.5, 1.7% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank <= 0.7813 AND dividend_yield_rank > 0.002599 (or missing) AND sales_yield_secrank <= 0.4539 (or missing)
  THEN P(positive) = 0.529   [weighted n = 661.7, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank > 0.6174 AND dividend_yield_rank > 0.00208 (or missing) AND beneish_m_rank > 0.7408 (or missing)
  THEN P(positive) = 0.522   [weighted n = 592.7, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank <= 0.5964 (or missing) AND rnd_to_assets_rank > 0.0008012 (or missing) AND piotroski_f_rank > 0.3794
  THEN P(positive) = 0.507   [weighted n = 936.3, 1.6% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank <= 0.6174 (or missing) AND ocf_yield_secrank > 0.6523
  THEN P(positive) = 0.503   [weighted n = 1034.3, 1.8% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank <= 0.4654 (or missing) AND ret_1m_rank > 0.228 (or missing) AND rnd_to_assets_rank > 0.002103
  THEN P(positive) = 0.496   [weighted n = 632.0, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank > 0.6174 AND dividend_yield_rank <= 0.00208
  THEN P(positive) = 0.493   [weighted n = 715.4, 1.2% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank <= 0.7813 AND dividend_yield_rank <= 0.002599 AND gp_to_assets_secrank > 0.413 AND ebitda_to_ev_secrank <= 0.5092
  THEN P(positive) = 0.493   [weighted n = 686.0, 1.2% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank > 0.5964 AND rnd_to_assets_rank > 0.0006491 (or missing) AND vol_36m_rank > 0.2875
  THEN P(positive) = 0.492   [weighted n = 962.9, 1.7% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank > 0.002595
  THEN P(positive) = 0.479   [weighted n = 1010.4, 1.7% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank <= 0.1824 (or missing) AND gp_to_assets_secrank > 0.2163 (or missing)
  THEN P(positive) = 0.476   [weighted n = 1022.8, 1.8% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank > 0.002521 AND rnd_to_assets_rank > 0.2886 (or missing) AND dividend_yield_rank <= 0.002078 (or missing) AND gp_to_assets_rank <= 0.5918
  THEN P(positive) = 0.471   [weighted n = 617.0, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank > 0.4254 (or missing) AND dist_52w_high_rank <= 0.6961 (or missing) AND rnd_to_assets_rank <= 0.002521 (or missing) AND mohanram_g7_rank <= 0.4654 (or missing) AND ret_1m_rank <= 0.228
  THEN P(positive) = 0.468   [weighted n = 580.0, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank <= 0.6174 (or missing) AND ocf_yield_secrank <= 0.6523 (or missing) AND noa_to_assets_rank <= 0.2816 (or missing)
  THEN P(positive) = 0.463   [weighted n = 886.0, 1.5% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank <= 0.7813 AND dividend_yield_rank <= 0.002599 AND gp_to_assets_secrank <= 0.413 (or missing)
  THEN P(positive) = 0.463   [weighted n = 579.6, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank > 0.1928 AND ncav_to_marketcap_rank > 0.6111 AND debt_to_equity_rank <= 0.1794 (or missing)
  THEN P(positive) = 0.461   [weighted n = 580.6, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank > 0.8067
  THEN P(positive) = 0.458   [weighted n = 1084.4, 1.9% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank <= 0.001677 (or missing) AND vol_12m_rank <= 0.9849 AND dividend_yield_rank > 0.001826 (or missing)
  THEN P(positive) = 0.457   [weighted n = 878.2, 1.5% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank > 0.1824 AND dist_52w_high_rank <= 0.6955 (or missing) AND share_count_growth_1y_rank > 0.7813 (or missing)
  THEN P(positive) = 0.452   [weighted n = 837.1, 1.4% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank > 0.5964 AND rnd_to_assets_rank <= 0.0006491
  THEN P(positive) = 0.450   [weighted n = 898.0, 1.6% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank > 0.9097
  THEN P(positive) = 0.444   [weighted n = 1019.6, 1.8% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank <= 0.5964 (or missing) AND rnd_to_assets_rank > 0.0008012 (or missing) AND piotroski_f_rank <= 0.3794 (or missing)
  THEN P(positive) = 0.432   [weighted n = 1135.1, 2.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank <= 0.5964 (or missing) AND rnd_to_assets_rank <= 0.0008012 AND revenue_growth_variability_3y_rank <= 0.682
  THEN P(positive) = 0.422   [weighted n = 1090.8, 1.9% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank > 0.002159 AND dividend_yield_rank > 0.002512
  THEN P(positive) = 0.417   [weighted n = 923.2, 1.6% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank > 0.7846 AND net_margin_secrank > 0.09061 (or missing) AND share_count_growth_1y_rank <= 0.9159 AND gross_margin_rank > 0.4792
  THEN P(positive) = 0.407   [weighted n = 758.5, 1.3% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank > 0.1928 AND ncav_to_marketcap_rank > 0.6111 AND debt_to_equity_rank > 0.1794
  THEN P(positive) = 0.406   [weighted n = 764.2, 1.3% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank > 0.1928 AND ncav_to_marketcap_rank <= 0.6111 (or missing) AND dist_52w_high_rank > 0.5456
  THEN P(positive) = 0.405   [weighted n = 772.7, 1.3% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank > 0.001677 AND book_to_market_rank <= 0.6174 (or missing) AND ocf_yield_secrank <= 0.6523 (or missing) AND noa_to_assets_rank > 0.2816
  THEN P(positive) = 0.400   [weighted n = 944.0, 1.6% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank > 0.001353 (or missing) AND ocf_yield_rank <= 0.4254 AND net_margin_rank <= 0.1824 (or missing) AND gp_to_assets_secrank <= 0.2163
  THEN P(positive) = 0.374   [weighted n = 922.8, 1.6% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank <= 0.1928 (or missing) AND ret_6m_rank <= 0.6935
  THEN P(positive) = 0.372   [weighted n = 655.8, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank <= 0.001677 (or missing) AND vol_12m_rank <= 0.9849 AND dividend_yield_rank <= 0.001826
  THEN P(positive) = 0.357   [weighted n = 634.1, 1.1% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank <= 0.001321 (or missing) AND dist_52w_high_rank <= 0.5964 (or missing) AND rnd_to_assets_rank <= 0.0008012 AND revenue_growth_variability_3y_rank > 0.682 (or missing)
  THEN P(positive) = 0.353   [weighted n = 579.3, 1.0% of training weight]
IF vol_12m_rank <= 0.7015 AND rnd_to_assets_rank <= 0.001353 AND rnd_to_assets_rank > 0.001321
  THEN P(positive) = 0.352   [weighted n = 1106.3, 1.9% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank > 0.7846 AND net_margin_secrank > 0.09061 (or missing) AND share_count_growth_1y_rank <= 0.9159 AND gross_margin_rank <= 0.4792 (or missing)
  THEN P(positive) = 0.350   [weighted n = 638.3, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank > 0.002159 AND dividend_yield_rank <= 0.002512 (or missing) AND net_margin_rank > 0.1374 (or missing)
  THEN P(positive) = 0.333   [weighted n = 600.2, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank > 0.1928 AND ncav_to_marketcap_rank <= 0.6111 (or missing) AND dist_52w_high_rank <= 0.5456 (or missing)
  THEN P(positive) = 0.329   [weighted n = 1128.0, 1.9% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank <= 0.1928 (or missing) AND ret_6m_rank > 0.6935 (or missing) AND log_assets_rank > 0.1578 (or missing)
  THEN P(positive) = 0.325   [weighted n = 870.7, 1.5% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank > 0.7846 AND net_margin_secrank > 0.09061 (or missing) AND share_count_growth_1y_rank > 0.9159 (or missing)
  THEN P(positive) = 0.317   [weighted n = 891.9, 1.5% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank <= 0.002159 (or missing) AND cash_to_assets_rank > 0.5808 (or missing) AND amihud_12m_rank > 0.3156
  THEN P(positive) = 0.316   [weighted n = 581.2, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank > 0.2551 AND rnd_to_assets_rank <= 0.001677 (or missing) AND vol_12m_rank > 0.9849 (or missing)
  THEN P(positive) = 0.303   [weighted n = 708.5, 1.2% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank <= 0.002159 (or missing) AND cash_to_assets_rank > 0.5808 (or missing) AND amihud_12m_rank <= 0.3156 (or missing) AND dollar_volume_3m_rank > 0.5192
  THEN P(positive) = 0.285   [weighted n = 578.9, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank <= 0.7846 (or missing) AND dividend_yield_rank <= 0.002595 (or missing) AND dist_52w_high_rank <= 0.8067 (or missing) AND amihud_12m_rank <= 0.9097 (or missing) AND log_assets_rank <= 0.1928 (or missing) AND ret_6m_rank > 0.6935 (or missing) AND log_assets_rank <= 0.1578
  THEN P(positive) = 0.282   [weighted n = 579.5, 1.0% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank > 0.05233 (or missing) AND fcf_margin_rank <= 0.2551 (or missing) AND ext_financing_to_assets_rank > 0.7846 AND net_margin_secrank <= 0.09061
  THEN P(positive) = 0.277   [weighted n = 1120.9, 1.9% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank <= 0.002159 (or missing) AND cash_to_assets_rank > 0.5808 (or missing) AND amihud_12m_rank <= 0.3156 (or missing) AND dollar_volume_3m_rank <= 0.5192 (or missing)
  THEN P(positive) = 0.255   [weighted n = 612.2, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank > 0.002159 AND dividend_yield_rank <= 0.002512 (or missing) AND net_margin_rank <= 0.1374
  THEN P(positive) = 0.255   [weighted n = 610.6, 1.1% of training weight]
IF vol_12m_rank > 0.7015 (or missing) AND dist_52w_high_rank <= 0.05233 AND rnd_to_assets_rank <= 0.002159 (or missing) AND cash_to_assets_rank <= 0.5808
  THEN P(positive) = 0.215   [weighted n = 1115.6, 1.9% of training weight]
```
