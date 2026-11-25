# Seed stability — forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3

- sweep: `forest_fallen50_cellC_seeds_3y` (config `experiments/sweeps/forest_fallen50_cellC_seeds_3y.toml`)
- dataset version: `dataset_v1.4.1` (pinned, immutable)
- scheme: `walkforward`, folds: `(2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020)`, git `f24b95eda15ff2283e1ea10025a00b1f1aac57b0`
- cell: `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y)
- model family: `random_forest`, params `{"bootstrap": true, "class_weight": 1.0, "criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490, "n_jobs": 8}`
- parameter set: `set0` = `{"criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490}`
- seeds: [232, 1776] — 2/2 completed
- pooled `precision_at_20` across seeds: mean 0.5483, std 0.0024, min 0.5467, max 0.5500, 95% CI [0.5272, 0.5695]

**Reading this report.** Each seed is a full walk-forward run of the same configuration; only the model's own randomness (row and column subsampling, tie-breaking) differs between them. The spread here is therefore the part of the number that is chance in the fit — a wide interval, or a `min` far below the `mean`, means the candidate's rank in the sweep is not trustworthy. The interval is a Student-t interval over the completed seeds (n − 1 degrees of freedom): with two or three seeds it is wide by construction, which is the honest width. Everything here is still **model selection on walk-forward folds** — selection-biased, never a final result.

## Pooled metrics across seeds

| metric                                                   | n | mean     | std     | min     | max     | ci95_low  | ci95_high |
| -------------------------------------------------------- | - | -------- | ------- | ------- | ------- | --------- | --------- |
| precision_at_20                                          | 2 | 0.5483   | 0.0024  | 0.5467  | 0.5500  | 0.5272    | 0.5695    |
| recall_at_prec_0.75                                      | 2 | 0.1495   | 0.0050  | 0.1460  | 0.1531  | 0.1042    | 0.1948    |
| n_at_prec_0.75                                           | 2 | 2731     | 89.0955 | 2668    | 2794    | 1930.5091 | 3531.4909 |
| recall_at_prec_0.9                                       | 2 | 0.0084   | 0.0004  | 0.0082  | 0.0087  | 0.0047    | 0.0121    |
| n_at_prec_0.9                                            | 2 | 126.5000 | 6.3640  | 122     | 131     | 69.3221   | 183.6779  |
| conf_at_20                                               | 2 | 0.5672   | 0.0015  | 0.5662  | 0.5683  | 0.5536    | 0.5808    |
| recall_at_20                                             | 2 | 0.0120   | 0.0001  | 0.0119  | 0.0120  | 0.0115    | 0.0124    |
| precision_at_50                                          | 2 | 0.5233   | 0.0009  | 0.5227  | 0.5240  | 0.5149    | 0.5318    |
| conf_at_50                                               | 2 | 0.5532   | 0.0011  | 0.5524  | 0.5540  | 0.5433    | 0.5631    |
| recall_at_50                                             | 2 | 0.0286   | 0.0001  | 0.0285  | 0.0286  | 0.0281    | 0.0290    |
| pr_auc                                                   | 2 | 0.4733   | 0.0006  | 0.4729  | 0.4738  | 0.4679    | 0.4788    |
| brier                                                    | 2 | 0.1961   | 0.0001  | 0.1960  | 0.1962  | 0.1949    | 0.1973    |
| base_rate_brier                                          | 2 | 0.2133   | 0       | 0.2133  | 0.2133  | 0.2133    | 0.2133    |
| base_rate                                                | 2 | 0.3085   | 0       | 0.3085  | 0.3085  | 0.3085    | 0.3085    |
| screen_n                                                 | 2 | 600      | 0       | 600     | 600     | 600       | 600       |
| screen_precision                                         | 2 | 0.4450   | 0.0024  | 0.4433  | 0.4467  | 0.4238    | 0.4662    |
| screen_n_stocks                                          | 2 | 321      | 1.4142  | 320     | 322     | 308.2938  | 333.7062  |
| screen_top_group_share                                   | 2 | 0.1617   | 0.0024  | 0.1600  | 0.1633  | 0.1405    | 0.1828    |
| screen_mean_label_3y_beat_spy                            | 2 | 0.3800   | 0.0047  | 0.3767  | 0.3833  | 0.3376    | 0.4224    |
| screen_mean_fwd_3y_excess_cagr                           | 2 | -0.0630  | 0.0042  | -0.0660 | -0.0600 | -0.1011   | -0.0249   |
| screen_median_fwd_3y_excess_cagr                         | 2 | -0.0442  | 0.0051  | -0.0478 | -0.0406 | -0.0901   | 0.0017    |
| screen_mean_fwd_3y_cagr                                  | 2 | 0.0391   | 0.0043  | 0.0361  | 0.0422  | 0.0004    | 0.0778    |
| screen_median_fwd_3y_cagr                                | 2 | 0.0528   | 0.0060  | 0.0485  | 0.0570  | -0.0011   | 0.1066    |
| screen_mean_fwd_3y_max_drawdown_from_entry               | 2 | 0.3780   | 0.0066  | 0.3734  | 0.3826  | 0.3190    | 0.4370    |
| screen_median_fwd_3y_max_drawdown_from_entry             | 2 | 0.3138   | 0.0018  | 0.3125  | 0.3150  | 0.2979    | 0.3296    |
| screen_mean_label_3y_cagr_lt_0p0                         | 2 | 0.3817   | 0.0071  | 0.3767  | 0.3867  | 0.3181    | 0.4452    |
| screen_mean_label_3y_cagr_lt_m0p1                        | 2 | 0.1958   | 0.0106  | 0.1883  | 0.2033  | 0.1005    | 0.2911    |
| screen_mean_label_3y_max_drawdown_from_entry_ge_0p4      | 2 | 0.4125   | 0.0082  | 0.4067  | 0.4183  | 0.3384    | 0.4866    |
| screen_mean_label_3y_cagr_ge_0p15                        | 2 | 0.2825   | 0.0035  | 0.2800  | 0.2850  | 0.2507    | 0.3143    |
| screen_mean_label_3y_cagr_ge_0p26                        | 2 | 0.1517   | 0.0047  | 0.1483  | 0.1550  | 0.1093    | 0.1940    |
| screen_mean_label_3y_excess_cagr_ge_0p05                 | 2 | 0.2958   | 0.0059  | 0.2917  | 0.3000  | 0.2429    | 0.3488    |
| screen_mean_label_3y_excess_cagr_ge_0p1                  | 2 | 0.2033   | 0.0047  | 0.2000  | 0.2067  | 0.1610    | 0.2457    |
| screen_peer_precision                                    | 2 | 0.3302   | 0.0032  | 0.3280  | 0.3325  | 0.3018    | 0.3587    |
| screen_peer_mean_label_3y_beat_spy                       | 2 | 0.3465   | 0.0017  | 0.3453  | 0.3477  | 0.3309    | 0.3621    |
| screen_peer_mean_fwd_3y_excess_cagr                      | 2 | -0.1185  | 0.0016  | -0.1197 | -0.1174 | -0.1332   | -0.1039   |
| screen_peer_mean_fwd_3y_cagr                             | 2 | -0.0158  | 0.0016  | -0.0169 | -0.0147 | -0.0300   | -0.0016   |
| screen_peer_mean_fwd_3y_max_drawdown_from_entry          | 2 | 0.4768   | 0.0020  | 0.4754  | 0.4782  | 0.4588    | 0.4949    |
| screen_peer_mean_label_3y_cagr_lt_0p0                    | 2 | 0.4636   | 0.0013  | 0.4627  | 0.4645  | 0.4517    | 0.4755    |
| screen_peer_mean_label_3y_cagr_lt_m0p1                   | 2 | 0.3260   | 0.0030  | 0.3239  | 0.3280  | 0.2993    | 0.3526    |
| screen_peer_mean_label_3y_max_drawdown_from_entry_ge_0p4 | 2 | 0.5513   | 0.0038  | 0.5486  | 0.5540  | 0.5174    | 0.5852    |
| screen_peer_mean_label_3y_cagr_ge_0p15                   | 2 | 0.2803   | 0.0006  | 0.2799  | 0.2808  | 0.2747    | 0.2860    |
| screen_peer_mean_label_3y_cagr_ge_0p26                   | 2 | 0.1475   | 0.0018  | 0.1462  | 0.1488  | 0.1310    | 0.1641    |
| screen_peer_mean_label_3y_excess_cagr_ge_0p05            | 2 | 0.2660   | 0.0027  | 0.2641  | 0.2679  | 0.2418    | 0.2902    |
| screen_peer_mean_label_3y_excess_cagr_ge_0p1             | 2 | 0.2003   | 0.0015  | 0.1993  | 0.2014  | 0.1869    | 0.2138    |
| n_stocks_at_20                                           | 2 | 16.3667  | 0.1414  | 16.2667 | 16.4667 | 15.0960   | 17.6373   |
| pick_mean_label_3y_beat_spy_at_20                        | 2 | 0.4233   | 0.0047  | 0.4200  | 0.4267  | 0.3810    | 0.4657    |
| pick_mean_fwd_3y_excess_cagr_at_20                       | 2 | -0.0336  | 0.0015  | -0.0347 | -0.0326 | -0.0474   | -0.0199   |
| pick_median_fwd_3y_excess_cagr_at_20                     | 2 | -0.0338  | 0.0053  | -0.0376 | -0.0301 | -0.0813   | 0.0137    |
| pick_mean_fwd_3y_cagr_at_20                              | 2 | 0.0823   | 0.0008  | 0.0817  | 0.0829  | 0.0750    | 0.0896    |
| pick_median_fwd_3y_cagr_at_20                            | 2 | 0.0766   | 0.0036  | 0.0740  | 0.0792  | 0.0439    | 0.1093    |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_20           | 2 | 0.3253   | 0.0017  | 0.3241  | 0.3265  | 0.3098    | 0.3408    |
| pick_median_fwd_3y_max_drawdown_from_entry_at_20         | 2 | 0.2519   | 0.0057  | 0.2479  | 0.2559  | 0.2007    | 0.3031    |
| pick_mean_label_3y_cagr_lt_0p0_at_20                     | 2 | 0.3150   | 0.0024  | 0.3133  | 0.3167  | 0.2938    | 0.3362    |
| pick_mean_label_3y_cagr_lt_m0p1_at_20                    | 2 | 0.1367   | 0.0047  | 0.1333  | 0.1400  | 0.0943    | 0.1790    |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20  | 2 | 0.3250   | 0.0024  | 0.3233  | 0.3267  | 0.3038    | 0.3462    |
| pick_mean_label_3y_cagr_ge_0p15_at_20                    | 2 | 0.3233   | 0.0094  | 0.3167  | 0.3300  | 0.2386    | 0.4080    |
| pick_mean_label_3y_cagr_ge_0p26_at_20                    | 2 | 0.1967   | 0       | 0.1967  | 0.1967  | 0.1967    | 0.1967    |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_20             | 2 | 0.3517   | 0.0024  | 0.3500  | 0.3533  | 0.3305    | 0.3728    |
| pick_mean_label_3y_excess_cagr_ge_0p1_at_20              | 2 | 0.2200   | 0.0047  | 0.2167  | 0.2233  | 0.1776    | 0.2624    |
| all_mean_label_3y_beat_spy                               | 2 | 0.3437   | 0       | 0.3437  | 0.3437  | 0.3437    | 0.3437    |
| all_mean_fwd_3y_excess_cagr                              | 2 | -0.1506  | 0       | -0.1506 | -0.1506 | -0.1506   | -0.1506   |
| all_median_fwd_3y_excess_cagr                            | 2 | -0.1156  | 0       | -0.1156 | -0.1156 | -0.1156   | -0.1156   |
| all_mean_fwd_3y_cagr                                     | 2 | -0.0413  | 0       | -0.0413 | -0.0413 | -0.0413   | -0.0413   |
| all_median_fwd_3y_cagr                                   | 2 | -0.0019  | 0       | -0.0019 | -0.0019 | -0.0019   | -0.0019   |
| all_mean_fwd_3y_max_drawdown_from_entry                  | 2 | 0.5257   | 0       | 0.5257  | 0.5257  | 0.5257    | 0.5257    |
| all_median_fwd_3y_max_drawdown_from_entry                | 2 | 0.5313   | 0       | 0.5313  | 0.5313  | 0.5313    | 0.5313    |
| all_mean_label_3y_cagr_lt_0p0                            | 2 | 0.5034   | 0       | 0.5034  | 0.5034  | 0.5034    | 0.5034    |
| all_mean_label_3y_cagr_lt_m0p1                           | 2 | 0.3927   | 0       | 0.3927  | 0.3927  | 0.3927    | 0.3927    |
| all_mean_label_3y_max_drawdown_from_entry_ge_0p4         | 2 | 0.6029   | 0       | 0.6029  | 0.6029  | 0.6029    | 0.6029    |
| all_mean_label_3y_cagr_ge_0p15                           | 2 | 0.2978   | 0       | 0.2978  | 0.2978  | 0.2978    | 0.2978    |
| all_mean_label_3y_cagr_ge_0p26                           | 2 | 0.1843   | 0       | 0.1843  | 0.1843  | 0.1843    | 0.1843    |
| all_mean_label_3y_excess_cagr_ge_0p05                    | 2 | 0.2808   | 0       | 0.2808  | 0.2808  | 0.2808    | 0.2808    |
| all_mean_label_3y_excess_cagr_ge_0p1                     | 2 | 0.2229   | 0       | 0.2229  | 0.2229  | 0.2229    | 0.2229    |

<details><summary>Every other pooled metric</summary>

| metric                                                  | n | mean      | std     | min       | max       | ci95_low  | ci95_high |
| ------------------------------------------------------- | - | --------- | ------- | --------- | --------- | --------- | --------- |
| n_test                                                  | 2 | 47013     | 0       | 47013     | 47013     | 47013     | 47013     |
| effective_n                                             | 2 | 1407.8054 | 0       | 1407.8054 | 1407.8054 | 1407.8054 | 1407.8054 |
| roc_auc                                                 | 2 | 0.6812    | 0.0006  | 0.6807    | 0.6816    | 0.6757    | 0.6866    |
| mean_score                                              | 2 | 0.3438    | 0.0002  | 0.3436    | 0.3439    | 0.3423    | 0.3452    |
| year_calib_corr                                         | 2 | 0.3912    | 0.0030  | 0.3890    | 0.3933    | 0.3643    | 0.4180    |
| year_calib_mae                                          | 2 | 0.1190    | 0.0002  | 0.1189    | 0.1192    | 0.1169    | 0.1212    |
| precision_at_thr_0.5                                    | 2 | 0.5286    | 0.0022  | 0.5270    | 0.5302    | 0.5087    | 0.5485    |
| recall_at_thr_0.5                                       | 2 | 0.2378    | 0.0011  | 0.2370    | 0.2386    | 0.2277    | 0.2480    |
| n_at_thr_0.5                                            | 2 | 6180.5000 | 3.5355  | 6178      | 6183      | 6148.7345 | 6212.2655 |
| precision_at_thr_0.6                                    | 2 | 0.6226    | 0.0003  | 0.6224    | 0.6229    | 0.6199    | 0.6254    |
| recall_at_thr_0.6                                       | 2 | 0.0887    | 0.0014  | 0.0877    | 0.0897    | 0.0762    | 0.1012    |
| n_at_thr_0.6                                            | 2 | 1957      | 29.6985 | 1936      | 1978      | 1690.1697 | 2223.8303 |
| precision_at_thr_0.7                                    | 2 | 0.7802    | 0.0191  | 0.7667    | 0.7937    | 0.6087    | 0.9516    |
| recall_at_thr_0.7                                       | 2 | 0.0035    | 0.0002  | 0.0033    | 0.0036    | 0.0016    | 0.0053    |
| n_at_thr_0.7                                            | 2 | 61.5000   | 2.1213  | 60        | 63        | 42.4407   | 80.5593   |
| n_stocks_at_50                                          | 2 | 37.6667   | 0.2828  | 37.4667   | 37.8667   | 35.1254   | 40.2079   |
| pick_mean_label_3y_beat_spy_at_50                       | 2 | 0.4207    | 0.0028  | 0.4187    | 0.4227    | 0.3953    | 0.4461    |
| pick_mean_fwd_3y_excess_cagr_at_50                      | 2 | -0.0475   | 0.0009  | -0.0482   | -0.0468   | -0.0559   | -0.0391   |
| pick_median_fwd_3y_excess_cagr_at_50                    | 2 | -0.0327   | 0.0009  | -0.0333   | -0.0321   | -0.0405   | -0.0249   |
| pick_mean_fwd_3y_cagr_at_50                             | 2 | 0.0676    | 0.0009  | 0.0669    | 0.0682    | 0.0594    | 0.0757    |
| pick_median_fwd_3y_cagr_at_50                           | 2 | 0.0790    | 0.0014  | 0.0780    | 0.0800    | 0.0664    | 0.0916    |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_50          | 2 | 0.3397    | 0.0012  | 0.3389    | 0.3406    | 0.3291    | 0.3504    |
| pick_median_fwd_3y_max_drawdown_from_entry_at_50        | 2 | 0.2528    | 0.0015  | 0.2518    | 0.2539    | 0.2397    | 0.2659    |
| pick_mean_label_3y_cagr_lt_0p0_at_50                    | 2 | 0.3333    | 0.0038  | 0.3307    | 0.3360    | 0.2995    | 0.3672    |
| pick_mean_label_3y_cagr_lt_m0p1_at_50                   | 2 | 0.1753    | 0.0066  | 0.1707    | 0.1800    | 0.1160    | 0.2346    |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_50 | 2 | 0.3260    | 0.0047  | 0.3227    | 0.3293    | 0.2836    | 0.3684    |
| pick_mean_label_3y_cagr_ge_0p15_at_50                   | 2 | 0.3453    | 0.0057  | 0.3413    | 0.3493    | 0.2945    | 0.3962    |
| pick_mean_label_3y_cagr_ge_0p26_at_50                   | 2 | 0.1780    | 0.0009  | 0.1773    | 0.1787    | 0.1695    | 0.1865    |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_50            | 2 | 0.3220    | 0.0009  | 0.3213    | 0.3227    | 0.3135    | 0.3305    |
| pick_mean_label_3y_excess_cagr_ge_0p1_at_50             | 2 | 0.2187    | 0       | 0.2187    | 0.2187    | 0.2187    | 0.2187    |
| thr_n_stocks_at_0.5                                     | 2 | 1648.5000 | 3.5355  | 1646      | 1651      | 1616.7345 | 1680.2655 |
| thr_years_at_0.5                                        | 2 | 13        | 0       | 13        | 13        | 13        | 13        |
| thr_mean_label_3y_beat_spy_at_0.5                       | 2 | 0.5303    | 0.0005  | 0.5299    | 0.5306    | 0.5258    | 0.5348    |
| thr_mean_fwd_3y_excess_cagr_at_0.5                      | 2 | 0.0108    | 0.0014  | 0.0098    | 0.0118    | -0.0020   | 0.0237    |
| thr_median_fwd_3y_excess_cagr_at_0.5                    | 2 | 0.0129    | 0.0004  | 0.0125    | 0.0132    | 0.0089    | 0.0168    |
| thr_mean_fwd_3y_cagr_at_0.5                             | 2 | 0.1381    | 0.0012  | 0.1373    | 0.1390    | 0.1272    | 0.1491    |
| thr_median_fwd_3y_cagr_at_0.5                           | 2 | 0.1402    | 0.0001  | 0.1401    | 0.1403    | 0.1390    | 0.1413    |
| thr_mean_fwd_3y_max_drawdown_from_entry_at_0.5          | 2 | 0.3233    | 0.0016  | 0.3222    | 0.3245    | 0.3086    | 0.3380    |
| thr_median_fwd_3y_max_drawdown_from_entry_at_0.5        | 2 | 0.2594    | 0.0016  | 0.2583    | 0.2605    | 0.2450    | 0.2738    |
| thr_mean_label_3y_cagr_lt_0p0_at_0.5                    | 2 | 0.2422    | 0.0008  | 0.2416    | 0.2428    | 0.2348    | 0.2496    |
| thr_mean_label_3y_cagr_lt_m0p1_at_0.5                   | 2 | 0.1241    | 0.0017  | 0.1229    | 0.1253    | 0.1091    | 0.1391    |
| thr_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_0.5 | 2 | 0.3216    | 0.0026  | 0.3197    | 0.3234    | 0.2983    | 0.3448    |
| thr_mean_label_3y_cagr_ge_0p15_at_0.5                   | 2 | 0.4786    | 0.0000  | 0.4786    | 0.4786    | 0.4782    | 0.4790    |
| thr_mean_label_3y_cagr_ge_0p26_at_0.5                   | 2 | 0.2775    | 0.0002  | 0.2774    | 0.2776    | 0.2761    | 0.2789    |
| thr_mean_label_3y_excess_cagr_ge_0p05_at_0.5            | 2 | 0.4204    | 0.0010  | 0.4197    | 0.4212    | 0.4113    | 0.4296    |
| thr_mean_label_3y_excess_cagr_ge_0p1_at_0.5             | 2 | 0.3218    | 0.0014  | 0.3208    | 0.3228    | 0.3091    | 0.3346    |
| thr_n_stocks_at_0.6                                     | 2 | 780.5000  | 21.9203 | 765       | 796       | 583.5538  | 977.4462  |
| thr_years_at_0.6                                        | 2 | 6.5000    | 0.7071  | 6         | 7         | 0.1469    | 12.8531   |
| thr_mean_label_3y_beat_spy_at_0.6                       | 2 | 0.5981    | 0.0014  | 0.5971    | 0.5991    | 0.5855    | 0.6107    |
| thr_mean_fwd_3y_excess_cagr_at_0.6                      | 2 | 0.0436    | 0.0010  | 0.0428    | 0.0443    | 0.0342    | 0.0529    |
| thr_median_fwd_3y_excess_cagr_at_0.6                    | 2 | 0.0419    | 0.0006  | 0.0415    | 0.0423    | 0.0367    | 0.0471    |
| thr_mean_fwd_3y_cagr_at_0.6                             | 2 | 0.1874    | 0.0015  | 0.1863    | 0.1885    | 0.1736    | 0.2011    |
| thr_median_fwd_3y_cagr_at_0.6                           | 2 | 0.1858    | 0.0013  | 0.1849    | 0.1868    | 0.1738    | 0.1979    |
| thr_mean_fwd_3y_max_drawdown_from_entry_at_0.6          | 2 | 0.2687    | 0.0016  | 0.2675    | 0.2698    | 0.2545    | 0.2828    |
| thr_median_fwd_3y_max_drawdown_from_entry_at_0.6        | 2 | 0.2182    | 0.0006  | 0.2178    | 0.2186    | 0.2129    | 0.2234    |
| thr_mean_label_3y_cagr_lt_0p0_at_0.6                    | 2 | 0.1605    | 0.0010  | 0.1598    | 0.1612    | 0.1516    | 0.1693    |
| thr_mean_label_3y_cagr_lt_m0p1_at_0.6                   | 2 | 0.0644    | 0.0031  | 0.0622    | 0.0666    | 0.0361    | 0.0927    |
| thr_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_0.6 | 2 | 0.2238    | 0.0012  | 0.2230    | 0.2247    | 0.2128    | 0.2349    |
| thr_mean_label_3y_cagr_ge_0p15_at_0.6                   | 2 | 0.5705    | 0.0033  | 0.5682    | 0.5728    | 0.5411    | 0.5998    |
| thr_mean_label_3y_cagr_ge_0p26_at_0.6                   | 2 | 0.3342    | 0.0029  | 0.3321    | 0.3362    | 0.3083    | 0.3600    |
| thr_mean_label_3y_excess_cagr_ge_0p05_at_0.6            | 2 | 0.4775    | 0.0011  | 0.4768    | 0.4783    | 0.4679    | 0.4871    |
| thr_mean_label_3y_excess_cagr_ge_0p1_at_0.6             | 2 | 0.3592    | 0.0011  | 0.3585    | 0.3600    | 0.3498    | 0.3687    |
| thr_n_stocks_at_0.7                                     | 2 | 53        | 0       | 53        | 53        | 53        | 53        |
| thr_years_at_0.7                                        | 2 | 2         | 0       | 2         | 2         | 2         | 2         |
| thr_mean_label_3y_beat_spy_at_0.7                       | 2 | 0.6921    | 0.0584  | 0.6508    | 0.7333    | 0.1677    | 1.2164    |
| thr_mean_fwd_3y_excess_cagr_at_0.7                      | 2 | 0.0700    | 0.0183  | 0.0571    | 0.0830    | -0.0945   | 0.2346    |
| thr_median_fwd_3y_excess_cagr_at_0.7                    | 2 | 0.0679    | 0.0150  | 0.0573    | 0.0785    | -0.0669   | 0.2027    |
| thr_mean_fwd_3y_cagr_at_0.7                             | 2 | 0.2193    | 0.0207  | 0.2047    | 0.2339    | 0.0337    | 0.4049    |
| thr_median_fwd_3y_cagr_at_0.7                           | 2 | 0.2114    | 0.0291  | 0.1909    | 0.2320    | -0.0498   | 0.4727    |
| thr_mean_fwd_3y_max_drawdown_from_entry_at_0.7          | 2 | 0.2542    | 0.0106  | 0.2468    | 0.2617    | 0.1593    | 0.3492    |
| thr_median_fwd_3y_max_drawdown_from_entry_at_0.7        | 2 | 0.2440    | 0.0002  | 0.2438    | 0.2442    | 0.2421    | 0.2459    |
| thr_mean_label_3y_cagr_lt_0p0_at_0.7                    | 2 | 0.0571    | 0.0135  | 0.0476    | 0.0667    | -0.0639   | 0.1782    |
| thr_mean_label_3y_cagr_lt_m0p1_at_0.7                   | 2 | 0.0083    | 0.0118  | 0         | 0.0167    | -0.0976   | 0.1142    |
| thr_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_0.7 | 2 | 0.1063    | 0.0382  | 0.0794    | 0.1333    | -0.2365   | 0.4492    |
| thr_mean_label_3y_cagr_ge_0p15_at_0.7                   | 2 | 0.6595    | 0.0572  | 0.6190    | 0.7000    | 0.1452    | 1.1738    |
| thr_mean_label_3y_cagr_ge_0p26_at_0.7                   | 2 | 0.3508    | 0.0696  | 0.3016    | 0.4000    | -0.2744   | 0.9760    |
| thr_mean_label_3y_excess_cagr_ge_0p05_at_0.7            | 2 | 0.5948    | 0.0780  | 0.5397    | 0.6500    | -0.1060   | 1.2957    |
| thr_mean_label_3y_excess_cagr_ge_0p1_at_0.7             | 2 | 0.3829    | 0.0477  | 0.3492    | 0.4167    | -0.0456   | 0.8115    |

</details>

## Per-seed pooled values

| seed | status    | precision_at_20 | recall_at_prec_0.75 | n_at_prec_0.75 | recall_at_prec_0.9 | n_at_prec_0.9 | conf_at_20 | recall_at_20 | precision_at_50 | conf_at_50 | recall_at_50 | pr_auc | brier  | base_rate_brier | base_rate | screen_n | screen_precision | screen_n_stocks | screen_top_group_share | screen_mean_label_3y_beat_spy | screen_mean_fwd_3y_excess_cagr | screen_median_fwd_3y_excess_cagr | screen_mean_fwd_3y_cagr | screen_median_fwd_3y_cagr | screen_mean_fwd_3y_max_drawdown_from_entry | screen_median_fwd_3y_max_drawdown_from_entry | screen_mean_label_3y_cagr_lt_0p0 | screen_mean_label_3y_cagr_lt_m0p1 | screen_mean_label_3y_max_drawdown_from_entry_ge_0p4 | screen_mean_label_3y_cagr_ge_0p15 | screen_mean_label_3y_cagr_ge_0p26 | screen_mean_label_3y_excess_cagr_ge_0p05 | screen_mean_label_3y_excess_cagr_ge_0p1 | screen_peer_precision | screen_peer_mean_label_3y_beat_spy | screen_peer_mean_fwd_3y_excess_cagr | screen_peer_mean_fwd_3y_cagr | screen_peer_mean_fwd_3y_max_drawdown_from_entry | screen_peer_mean_label_3y_cagr_lt_0p0 | screen_peer_mean_label_3y_cagr_lt_m0p1 | screen_peer_mean_label_3y_max_drawdown_from_entry_ge_0p4 | screen_peer_mean_label_3y_cagr_ge_0p15 | screen_peer_mean_label_3y_cagr_ge_0p26 | screen_peer_mean_label_3y_excess_cagr_ge_0p05 | screen_peer_mean_label_3y_excess_cagr_ge_0p1 | n_stocks_at_20 | pick_mean_label_3y_beat_spy_at_20 | pick_mean_fwd_3y_excess_cagr_at_20 | pick_median_fwd_3y_excess_cagr_at_20 | pick_mean_fwd_3y_cagr_at_20 | pick_median_fwd_3y_cagr_at_20 | pick_mean_fwd_3y_max_drawdown_from_entry_at_20 | pick_median_fwd_3y_max_drawdown_from_entry_at_20 | pick_mean_label_3y_cagr_lt_0p0_at_20 | pick_mean_label_3y_cagr_lt_m0p1_at_20 | pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20 | pick_mean_label_3y_cagr_ge_0p15_at_20 | pick_mean_label_3y_cagr_ge_0p26_at_20 | pick_mean_label_3y_excess_cagr_ge_0p05_at_20 | pick_mean_label_3y_excess_cagr_ge_0p1_at_20 | all_mean_label_3y_beat_spy | all_mean_fwd_3y_excess_cagr | all_median_fwd_3y_excess_cagr | all_mean_fwd_3y_cagr | all_median_fwd_3y_cagr | all_mean_fwd_3y_max_drawdown_from_entry | all_median_fwd_3y_max_drawdown_from_entry | all_mean_label_3y_cagr_lt_0p0 | all_mean_label_3y_cagr_lt_m0p1 | all_mean_label_3y_max_drawdown_from_entry_ge_0p4 | all_mean_label_3y_cagr_ge_0p15 | all_mean_label_3y_cagr_ge_0p26 | all_mean_label_3y_excess_cagr_ge_0p05 | all_mean_label_3y_excess_cagr_ge_0p1 | report                                                                                               |
| ---- | --------- | --------------- | ------------------- | -------------- | ------------------ | ------------- | ---------- | ------------ | --------------- | ---------- | ------------ | ------ | ------ | --------------- | --------- | -------- | ---------------- | --------------- | ---------------------- | ----------------------------- | ------------------------------ | -------------------------------- | ----------------------- | ------------------------- | ------------------------------------------ | -------------------------------------------- | -------------------------------- | --------------------------------- | --------------------------------------------------- | --------------------------------- | --------------------------------- | ---------------------------------------- | --------------------------------------- | --------------------- | ---------------------------------- | ----------------------------------- | ---------------------------- | ----------------------------------------------- | ------------------------------------- | -------------------------------------- | -------------------------------------------------------- | -------------------------------------- | -------------------------------------- | --------------------------------------------- | -------------------------------------------- | -------------- | --------------------------------- | ---------------------------------- | ------------------------------------ | --------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------------------------ | ------------------------------------ | ------------------------------------- | ------------------------------------------------------- | ------------------------------------- | ------------------------------------- | -------------------------------------------- | ------------------------------------------- | -------------------------- | --------------------------- | ----------------------------- | -------------------- | ---------------------- | --------------------------------------- | ----------------------------------------- | ----------------------------- | ------------------------------ | ------------------------------------------------ | ------------------------------ | ------------------------------ | ------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| 232  | completed | 0.5500          | 0.1460              | 2668           | 0.0082             | 122           | 0.5683     | 0.0120       | 0.5240          | 0.5540     | 0.0286       | 0.4729 | 0.1962 | 0.2133          | 0.3085    | 600      | 0.4433           | 322             | 0.1633                 | 0.3767                        | -0.0660                        | -0.0478                          | 0.0361                  | 0.0485                    | 0.3826                                     | 0.3150                                       | 0.3867                           | 0.2033                            | 0.4183                                              | 0.2800                            | 0.1550                            | 0.2917                                   | 0.2000                                  | 0.3280                | 0.3453                             | -0.1197                             | -0.0169                      | 0.4782                                          | 0.4645                                | 0.3280                                 | 0.5540                                                   | 0.2799                                 | 0.1462                                 | 0.2641                                        | 0.1993                                       | 16.2667        | 0.4267                            | -0.0347                            | -0.0376                              | 0.0817                      | 0.0792                        | 0.3241                                         | 0.2479                                           | 0.3167                               | 0.1400                                | 0.3267                                                  | 0.3167                                | 0.1967                                | 0.3533                                       | 0.2167                                      | 0.3437                     | -0.1506                     | -0.1156                       | -0.0413              | -0.0019                | 0.5257                                  | 0.5313                                    | 0.5034                        | 0.3927                         | 0.6029                                           | 0.2978                         | 0.1843                         | 0.2808                                | 0.2229                               | forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s232.md  |
| 1776 | completed | 0.5467          | 0.1531              | 2794           | 0.0087             | 131           | 0.5662     | 0.0119       | 0.5227          | 0.5524     | 0.0285       | 0.4738 | 0.1960 | 0.2133          | 0.3085    | 600      | 0.4467           | 320             | 0.1600                 | 0.3833                        | -0.0600                        | -0.0406                          | 0.0422                  | 0.0570                    | 0.3734                                     | 0.3125                                       | 0.3767                           | 0.1883                            | 0.4067                                              | 0.2850                            | 0.1483                            | 0.3000                                   | 0.2067                                  | 0.3325                | 0.3477                             | -0.1174                             | -0.0147                      | 0.4754                                          | 0.4627                                | 0.3239                                 | 0.5486                                                   | 0.2808                                 | 0.1488                                 | 0.2679                                        | 0.2014                                       | 16.4667        | 0.4200                            | -0.0326                            | -0.0301                              | 0.0829                      | 0.0740                        | 0.3265                                         | 0.2559                                           | 0.3133                               | 0.1333                                | 0.3233                                                  | 0.3300                                | 0.1967                                | 0.3500                                       | 0.2233                                      | 0.3437                     | -0.1506                     | -0.1156                       | -0.0413              | -0.0019                | 0.5257                                  | 0.5313                                    | 0.5034                        | 0.3927                         | 0.6029                                           | 0.2978                         | 0.1843                         | 0.2808                                | 0.2229                               | forest_fallen50_cellC_seeds_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__s1776.md |

## Era slices across seeds (per test year)

Per-fold metrics under walk-forward are per test year. A candidate whose mean holds up but whose per-year `min` collapses in some eras is seed-fragile exactly where it matters.

| era  | crash | n | precision_at_20 mean | precision_at_20 std | precision_at_20 min | precision_at_20 max |
| ---- | ----- | - | -------------------- | ------------------- | ------------------- | ------------------- |
| 2006 |       | 2 | 0.2750               | 0.0354              | 0.2500              | 0.3000              |
| 2007 |       | 2 | 0.0500               | 0                   | 0.0500              | 0.0500              |
| 2008 | GFC   | 2 | 0.7250               | 0.0354              | 0.7000              | 0.7500              |
| 2009 | GFC   | 2 | 0.9000               | 0                   | 0.9000              | 0.9000              |
| 2010 |       | 2 | 0.8250               | 0.1061              | 0.7500              | 0.9000              |
| 2011 |       | 2 | 0.7000               | 0                   | 0.7000              | 0.7000              |
| 2012 |       | 2 | 0.9000               | 0                   | 0.9000              | 0.9000              |
| 2013 |       | 2 | 0.7500               | 0                   | 0.7500              | 0.7500              |
| 2014 |       | 2 | 0.3750               | 0.0354              | 0.3500              | 0.4000              |
| 2015 |       | 2 | 0.4500               | 0                   | 0.4500              | 0.4500              |
| 2016 |       | 2 | 0.5500               | 0.0707              | 0.5000              | 0.6000              |
| 2017 |       | 2 | 0.4750               | 0.0354              | 0.4500              | 0.5000              |
| 2018 |       | 2 | 0.3250               | 0.0354              | 0.3000              | 0.3500              |
| 2019 |       | 2 | 0.1750               | 0.0354              | 0.1500              | 0.2000              |
| 2020 | COVID | 2 | 0.7500               | 0                   | 0.7500              | 0.7500              |

Per-seed reports (era tables, crash eras, calibration, baselines): `seeds/<run name>.md` in this directory.
