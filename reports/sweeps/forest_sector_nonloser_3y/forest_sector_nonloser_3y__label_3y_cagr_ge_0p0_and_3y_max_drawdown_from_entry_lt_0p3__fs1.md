# Seed stability — forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs1

- sweep: `forest_sector_nonloser_3y` (config `experiments/sweeps/forest_sector_nonloser_3y.toml`)
- dataset version: `dataset_v1.4` (pinned, immutable)
- scheme: `walkforward`, folds: `all`, git `a8e29b94f335c3928224432511860e65fbd45452`
- cell: `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y)
- model family: `random_forest`, params `{"bootstrap": true, "class_weight": 1.0, "criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490, "n_jobs": 8}`
- feature set: `fs1`
- parameter set: `set0` = `{"criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490}`
- seeds: [23, 232, 1776] — 3/3 completed
- pooled `precision_at_20` across seeds: mean 0.7646, std 0.0079, min 0.7562, max 0.7719, 95% CI [0.7450, 0.7841]

**Reading this report.** Each seed is a full walk-forward run of the same configuration; only the model's own randomness (row and column subsampling, tie-breaking) differs between them. The spread here is therefore the part of the number that is chance in the fit — a wide interval, or a `min` far below the `mean`, means the candidate's rank in the sweep is not trustworthy. The interval is a Student-t interval over the completed seeds (n − 1 degrees of freedom): with two or three seeds it is wide by construction, which is the honest width. Everything here is still **model selection on walk-forward folds** — selection-biased, never a final result.

## Pooled metrics across seeds

| metric                                                  | n | mean       | std      | min     | max     | ci95_low   | ci95_high  |
| ------------------------------------------------------- | - | ---------- | -------- | ------- | ------- | ---------- | ---------- |
| precision_at_20                                         | 3 | 0.7646     | 0.0079   | 0.7562  | 0.7719  | 0.7450     | 0.7841     |
| recall_at_prec_0.75                                     | 3 | 0.3758     | 0.0009   | 0.3748  | 0.3764  | 0.3735     | 0.3780     |
| n_at_prec_0.75                                          | 3 | 48360.3333 | 116.7148 | 48227   | 48444   | 48070.3978 | 48650.2689 |
| recall_at_prec_0.9                                      | 3 | 0.0952     | 0.0015   | 0.0934  | 0.0961  | 0.0914     | 0.0991     |
| n_at_prec_0.9                                           | 3 | 10207.6667 | 166.8662 | 10015   | 10306   | 9793.1480  | 10622.1853 |
| conf_at_20                                              | 3 | 0.7507     | 0.0006   | 0.7500  | 0.7511  | 0.7492     | 0.7522     |
| recall_at_20                                            | 3 | 0.0025     | 0.0000   | 0.0025  | 0.0026  | 0.0025     | 0.0026     |
| precision_at_50                                         | 3 | 0.7471     | 0.0044   | 0.7425  | 0.7512  | 0.7362     | 0.7580     |
| conf_at_50                                              | 3 | 0.7449     | 0.0006   | 0.7443  | 0.7454  | 0.7436     | 0.7463     |
| recall_at_50                                            | 3 | 0.0062     | 0.0000   | 0.0062  | 0.0062  | 0.0061     | 0.0063     |
| pr_auc                                                  | 3 | 0.5363     | 0.0001   | 0.5362  | 0.5363  | 0.5360     | 0.5365     |
| brier                                                   | 3 | 0.2149     | 0.0000   | 0.2149  | 0.2149  | 0.2149     | 0.2149     |
| base_rate_brier                                         | 3 | 0.2371     | 0.0000   | 0.2371  | 0.2371  | 0.2371     | 0.2371     |
| base_rate                                               | 3 | 0.3866     | 0        | 0.3866  | 0.3866  | 0.3866     | 0.3866     |
| screen_n                                                | 3 | 640        | 0        | 640     | 640     | 640        | 640        |
| screen_precision                                        | 3 | 0.7578     | 0.0095   | 0.7469  | 0.7641  | 0.7342     | 0.7814     |
| screen_n_stocks                                         | 3 | 182.3333   | 1.5275   | 181     | 184     | 178.5388   | 186.1279   |
| screen_top_group_share                                  | 3 | 0.1786     | 0.0033   | 0.1750  | 0.1812  | 0.1706     | 0.1867     |
| screen_mean_label_3y_beat_spy                           | 3 | 0.5328     | 0.0027   | 0.5312  | 0.5359  | 0.5261     | 0.5395     |
| screen_mean_fwd_3y_excess_cagr                          | 3 | 0.0024     | 0.0003   | 0.0020  | 0.0026  | 0.0016     | 0.0031     |
| screen_median_fwd_3y_excess_cagr                        | 3 | 0.0064     | 0.0005   | 0.0058  | 0.0067  | 0.0051     | 0.0076     |
| screen_mean_fwd_3y_cagr                                 | 3 | 0.0981     | 0.0003   | 0.0978  | 0.0982  | 0.0975     | 0.0987     |
| screen_median_fwd_3y_cagr                               | 3 | 0.1131     | 0.0003   | 0.1127  | 0.1133  | 0.1123     | 0.1138     |
| screen_mean_fwd_3y_max_drawdown_from_entry              | 3 | 0.1671     | 0.0017   | 0.1652  | 0.1685  | 0.1629     | 0.1714     |
| screen_median_fwd_3y_max_drawdown_from_entry            | 3 | 0.0834     | 0.0026   | 0.0814  | 0.0863  | 0.0769     | 0.0899     |
| screen_mean_label_3y_cagr_lt_0p0                        | 3 | 0.1646     | 0.0059   | 0.1578  | 0.1688  | 0.1499     | 0.1793     |
| screen_mean_label_3y_cagr_lt_m0p1                       | 3 | 0.0563     | 0.0016   | 0.0547  | 0.0578  | 0.0524     | 0.0601     |
| screen_mean_label_3y_max_drawdown_from_entry_ge_0p4     | 3 | 0.1125     | 0.0031   | 0.1094  | 0.1156  | 0.1047     | 0.1203     |
| screen_mean_label_3y_cagr_ge_0p15                       | 3 | 0.3490     | 0.0018   | 0.3469  | 0.3500  | 0.3445     | 0.3534     |
| screen_mean_label_3y_cagr_ge_0p25                       | 3 | 0.0646     | 0.0024   | 0.0625  | 0.0672  | 0.0587     | 0.0705     |
| screen_mean_label_3y_excess_cagr_ge_0p05                | 3 | 0.3167     | 0.0039   | 0.3125  | 0.3203  | 0.3069     | 0.3264     |
| n_stocks_at_20                                          | 3 | 13.9792    | 0.2009   | 13.7500 | 14.1250 | 13.4801    | 14.4783    |
| pick_mean_label_3y_beat_spy_at_20                       | 3 | 0.4479     | 0.0110   | 0.4375  | 0.4594  | 0.4207     | 0.4752     |
| pick_mean_fwd_3y_excess_cagr_at_20                      | 3 | -0.0139    | 0.0012   | -0.0153 | -0.0131 | -0.0170    | -0.0108    |
| pick_median_fwd_3y_excess_cagr_at_20                    | 3 | -0.0116    | 0.0029   | -0.0144 | -0.0087 | -0.0187    | -0.0045    |
| pick_mean_fwd_3y_cagr_at_20                             | 3 | 0.0798     | 0.0010   | 0.0787  | 0.0806  | 0.0773     | 0.0824     |
| pick_median_fwd_3y_cagr_at_20                           | 3 | 0.0970     | 0.0022   | 0.0944  | 0.0986  | 0.0914     | 0.1025     |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_20          | 3 | 0.1649     | 0.0027   | 0.1624  | 0.1677  | 0.1583     | 0.1715     |
| pick_median_fwd_3y_max_drawdown_from_entry_at_20        | 3 | 0.0781     | 0.0017   | 0.0761  | 0.0791  | 0.0738     | 0.0824     |
| pick_mean_label_3y_cagr_lt_0p0_at_20                    | 3 | 0.1427     | 0.0065   | 0.1375  | 0.1500  | 0.1265     | 0.1589     |
| pick_mean_label_3y_cagr_lt_m0p1_at_20                   | 3 | 0.0552     | 0.0018   | 0.0531  | 0.0563  | 0.0507     | 0.0597     |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20 | 3 | 0.1062     | 0.0083   | 0.0969  | 0.1125  | 0.0857     | 0.1268     |
| pick_mean_label_3y_cagr_ge_0p15_at_20                   | 3 | 0.2594     | 0.0113   | 0.2469  | 0.2687  | 0.2314     | 0.2874     |
| pick_mean_label_3y_cagr_ge_0p25_at_20                   | 3 | 0.0385     | 0.0018   | 0.0375  | 0.0406  | 0.0341     | 0.0430     |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_20            | 3 | 0.2833     | 0.0048   | 0.2781  | 0.2875  | 0.2715     | 0.2952     |
| all_mean_label_3y_beat_spy                              | 3 | 0.3630     | 0        | 0.3630  | 0.3630  | 0.3630     | 0.3630     |
| all_mean_fwd_3y_excess_cagr                             | 3 | -0.1056    | 0        | -0.1056 | -0.1056 | -0.1056    | -0.1056    |
| all_median_fwd_3y_excess_cagr                           | 3 | -0.0730    | 0        | -0.0730 | -0.0730 | -0.0730    | -0.0730    |
| all_mean_fwd_3y_cagr                                    | 3 | -0.0133    | 0        | -0.0133 | -0.0133 | -0.0133    | -0.0133    |
| all_median_fwd_3y_cagr                                  | 3 | 0.0174     | 0        | 0.0174  | 0.0174  | 0.0174     | 0.0174     |
| all_mean_fwd_3y_max_drawdown_from_entry                 | 3 | 0.4413     | 0        | 0.4413  | 0.4413  | 0.4413     | 0.4413     |
| all_median_fwd_3y_max_drawdown_from_entry               | 3 | 0.4033     | 0        | 0.4033  | 0.4033  | 0.4033     | 0.4033     |
| all_mean_label_3y_cagr_lt_0p0                           | 3 | 0.4568     | 0.0000   | 0.4568  | 0.4568  | 0.4568     | 0.4568     |
| all_mean_label_3y_cagr_lt_m0p1                          | 3 | 0.3223     | 0        | 0.3223  | 0.3223  | 0.3223     | 0.3223     |
| all_mean_label_3y_max_drawdown_from_entry_ge_0p4        | 3 | 0.5034     | 0        | 0.5034  | 0.5034  | 0.5034     | 0.5034     |
| all_mean_label_3y_cagr_ge_0p15                          | 3 | 0.2674     | 0        | 0.2674  | 0.2674  | 0.2674     | 0.2674     |
| all_mean_label_3y_cagr_ge_0p25                          | 3 | 0.1469     | 0        | 0.1469  | 0.1469  | 0.1469     | 0.1469     |
| all_mean_label_3y_excess_cagr_ge_0p05                   | 3 | 0.2763     | 0        | 0.2763  | 0.2763  | 0.2763     | 0.2763     |

<details><summary>Every other pooled metric</summary>

| metric                                                  | n | mean      | std    | min       | max       | ci95_low  | ci95_high |
| ------------------------------------------------------- | - | --------- | ------ | --------- | --------- | --------- | --------- |
| n_test                                                  | 3 | 256351    | 0      | 256351    | 256351    | 256351    | 256351    |
| effective_n                                             | 3 | 8215.4386 | 0      | 8215.4386 | 8215.4386 | 8215.4386 | 8215.4386 |
| roc_auc                                                 | 3 | 0.6871    | 0.0000 | 0.6871    | 0.6871    | 0.6871    | 0.6871    |
| n_stocks_at_50                                          | 3 | 29.2500   | 0.3802 | 28.8125   | 29.5000   | 28.3056   | 30.1944   |
| pick_mean_label_3y_beat_spy_at_50                       | 3 | 0.4383    | 0.0069 | 0.4313    | 0.4450    | 0.4212    | 0.4554    |
| pick_mean_fwd_3y_excess_cagr_at_50                      | 3 | -0.0160   | 0.0015 | -0.0175   | -0.0145   | -0.0197   | -0.0123   |
| pick_median_fwd_3y_excess_cagr_at_50                    | 3 | -0.0141   | 0.0014 | -0.0154   | -0.0126   | -0.0176   | -0.0106   |
| pick_mean_fwd_3y_cagr_at_50                             | 3 | 0.0797    | 0.0015 | 0.0782    | 0.0813    | 0.0759    | 0.0834    |
| pick_median_fwd_3y_cagr_at_50                           | 3 | 0.1017    | 0.0018 | 0.1003    | 0.1037    | 0.0972    | 0.1061    |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_50          | 3 | 0.1795    | 0.0021 | 0.1775    | 0.1816    | 0.1744    | 0.1846    |
| pick_median_fwd_3y_max_drawdown_from_entry_at_50        | 3 | 0.0795    | 0.0008 | 0.0789    | 0.0804    | 0.0775    | 0.0815    |
| pick_mean_label_3y_cagr_lt_0p0_at_50                    | 3 | 0.1783    | 0.0031 | 0.1750    | 0.1812    | 0.1705    | 0.1861    |
| pick_mean_label_3y_cagr_lt_m0p1_at_50                   | 3 | 0.0779    | 0.0007 | 0.0775    | 0.0788    | 0.0761    | 0.0797    |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_50 | 3 | 0.1333    | 0.0036 | 0.1313    | 0.1375    | 0.1244    | 0.1423    |
| pick_mean_label_3y_cagr_ge_0p15_at_50                   | 3 | 0.2742    | 0.0062 | 0.2700    | 0.2812    | 0.2588    | 0.2895    |
| pick_mean_label_3y_cagr_ge_0p25_at_50                   | 3 | 0.0400    | 0.0022 | 0.0387    | 0.0425    | 0.0346    | 0.0454    |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_50            | 3 | 0.2579    | 0.0094 | 0.2487    | 0.2675    | 0.2346    | 0.2812    |

</details>

## Per-seed pooled values

| seed | status    | precision_at_20 | recall_at_prec_0.75 | n_at_prec_0.75 | recall_at_prec_0.9 | n_at_prec_0.9 | conf_at_20 | recall_at_20 | precision_at_50 | conf_at_50 | recall_at_50 | pr_auc | brier  | base_rate_brier | base_rate | screen_n | screen_precision | screen_n_stocks | screen_top_group_share | screen_mean_label_3y_beat_spy | screen_mean_fwd_3y_excess_cagr | screen_median_fwd_3y_excess_cagr | screen_mean_fwd_3y_cagr | screen_median_fwd_3y_cagr | screen_mean_fwd_3y_max_drawdown_from_entry | screen_median_fwd_3y_max_drawdown_from_entry | screen_mean_label_3y_cagr_lt_0p0 | screen_mean_label_3y_cagr_lt_m0p1 | screen_mean_label_3y_max_drawdown_from_entry_ge_0p4 | screen_mean_label_3y_cagr_ge_0p15 | screen_mean_label_3y_cagr_ge_0p25 | screen_mean_label_3y_excess_cagr_ge_0p05 | n_stocks_at_20 | pick_mean_label_3y_beat_spy_at_20 | pick_mean_fwd_3y_excess_cagr_at_20 | pick_median_fwd_3y_excess_cagr_at_20 | pick_mean_fwd_3y_cagr_at_20 | pick_median_fwd_3y_cagr_at_20 | pick_mean_fwd_3y_max_drawdown_from_entry_at_20 | pick_median_fwd_3y_max_drawdown_from_entry_at_20 | pick_mean_label_3y_cagr_lt_0p0_at_20 | pick_mean_label_3y_cagr_lt_m0p1_at_20 | pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20 | pick_mean_label_3y_cagr_ge_0p15_at_20 | pick_mean_label_3y_cagr_ge_0p25_at_20 | pick_mean_label_3y_excess_cagr_ge_0p05_at_20 | all_mean_label_3y_beat_spy | all_mean_fwd_3y_excess_cagr | all_median_fwd_3y_excess_cagr | all_mean_fwd_3y_cagr | all_median_fwd_3y_cagr | all_mean_fwd_3y_max_drawdown_from_entry | all_median_fwd_3y_max_drawdown_from_entry | all_mean_label_3y_cagr_lt_0p0 | all_mean_label_3y_cagr_lt_m0p1 | all_mean_label_3y_max_drawdown_from_entry_ge_0p4 | all_mean_label_3y_cagr_ge_0p15 | all_mean_label_3y_cagr_ge_0p25 | all_mean_label_3y_excess_cagr_ge_0p05 | report                                                                                               |
| ---- | --------- | --------------- | ------------------- | -------------- | ------------------ | ------------- | ---------- | ------------ | --------------- | ---------- | ------------ | ------ | ------ | --------------- | --------- | -------- | ---------------- | --------------- | ---------------------- | ----------------------------- | ------------------------------ | -------------------------------- | ----------------------- | ------------------------- | ------------------------------------------ | -------------------------------------------- | -------------------------------- | --------------------------------- | --------------------------------------------------- | --------------------------------- | --------------------------------- | ---------------------------------------- | -------------- | --------------------------------- | ---------------------------------- | ------------------------------------ | --------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------------------------ | ------------------------------------ | ------------------------------------- | ------------------------------------------------------- | ------------------------------------- | ------------------------------------- | -------------------------------------------- | -------------------------- | --------------------------- | ----------------------------- | -------------------- | ---------------------- | --------------------------------------- | ----------------------------------------- | ----------------------------- | ------------------------------ | ------------------------------------------------ | ------------------------------ | ------------------------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 23   | completed | 0.7656          | 0.3748              | 48227          | 0.0961             | 10306         | 0.7511     | 0.0025       | 0.7475          | 0.7454     | 0.0062       | 0.5363 | 0.2149 | 0.2371          | 0.3866    | 640      | 0.7641           | 181             | 0.1750                 | 0.5359                        | 0.0026                         | 0.0067                           | 0.0982                  | 0.1127                    | 0.1652                                     | 0.0814                                       | 0.1688                           | 0.0563                            | 0.1125                                              | 0.3500                            | 0.0672                            | 0.3172                                   | 13.7500        | 0.4594                            | -0.0132                            | -0.0087                              | 0.0806                      | 0.0986                        | 0.1624                                         | 0.0791                                           | 0.1406                               | 0.0531                                | 0.0969                                                  | 0.2687                                | 0.0406                                | 0.2781                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs1__s23.md   |
| 232  | completed | 0.7562          | 0.3762              | 48410          | 0.0934             | 10015         | 0.7500     | 0.0025       | 0.7512          | 0.7443     | 0.0062       | 0.5363 | 0.2149 | 0.2371          | 0.3866    | 640      | 0.7625           | 184             | 0.1812                 | 0.5312                        | 0.0026                         | 0.0066                           | 0.0982                  | 0.1132                    | 0.1685                                     | 0.0863                                       | 0.1578                           | 0.0578                            | 0.1094                                              | 0.3469                            | 0.0625                            | 0.3203                                   | 14.0625        | 0.4469                            | -0.0131                            | -0.0117                              | 0.0802                      | 0.0979                        | 0.1677                                         | 0.0791                                           | 0.1500                               | 0.0563                                | 0.1125                                                  | 0.2625                                | 0.0375                                | 0.2875                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs1__s232.md  |
| 1776 | completed | 0.7719          | 0.3764              | 48444          | 0.0961             | 10302         | 0.7511     | 0.0026       | 0.7425          | 0.7452     | 0.0062       | 0.5362 | 0.2149 | 0.2371          | 0.3866    | 640      | 0.7469           | 182             | 0.1797                 | 0.5312                        | 0.0020                         | 0.0058                           | 0.0978                  | 0.1133                    | 0.1677                                     | 0.0824                                       | 0.1672                           | 0.0547                            | 0.1156                                              | 0.3500                            | 0.0641                            | 0.3125                                   | 14.1250        | 0.4375                            | -0.0153                            | -0.0144                              | 0.0787                      | 0.0944                        | 0.1645                                         | 0.0761                                           | 0.1375                               | 0.0563                                | 0.1094                                                  | 0.2469                                | 0.0375                                | 0.2844                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs1__s1776.md |

## Era slices across seeds (per test year)

Per-fold metrics under walk-forward are per test year. A candidate whose mean holds up but whose per-year `min` collapses in some eras is seed-fragile exactly where it matters.

| era  | crash | n | precision_at_20 mean | precision_at_20 std | precision_at_20 min | precision_at_20 max |
| ---- | ----- | - | -------------------- | ------------------- | ------------------- | ------------------- |
| 2005 |       | 3 | 0.7167               | 0.0289              | 0.7000              | 0.7500              |
| 2006 |       | 3 | 0.5000               | 0                   | 0.5000              | 0.5000              |
| 2007 |       | 3 | 0.2167               | 0.0289              | 0.2000              | 0.2500              |
| 2008 | GFC   | 3 | 0.3333               | 0.0764              | 0.2500              | 0.4000              |
| 2009 | GFC   | 3 | 0.9333               | 0.0577              | 0.9000              | 1                   |
| 2010 |       | 3 | 0.9833               | 0.0289              | 0.9500              | 1                   |
| 2011 |       | 3 | 0.9500               | 0.0000              | 0.9500              | 0.9500              |
| 2012 |       | 3 | 0.9833               | 0.0289              | 0.9500              | 1                   |
| 2013 |       | 3 | 0.9333               | 0.0289              | 0.9000              | 0.9500              |
| 2014 |       | 3 | 0.8500               | 0                   | 0.8500              | 0.8500              |
| 2015 |       | 3 | 1                    | 0                   | 1                   | 1                   |
| 2016 |       | 3 | 0.9333               | 0.0289              | 0.9000              | 0.9500              |
| 2017 |       | 3 | 0.8333               | 0.0289              | 0.8000              | 0.8500              |
| 2018 |       | 3 | 0.9333               | 0.0289              | 0.9000              | 0.9500              |
| 2019 |       | 3 | 0.5500               | 0.0500              | 0.5000              | 0.6000              |
| 2020 | COVID | 3 | 0.5833               | 0.0289              | 0.5500              | 0.6000              |

Per-seed reports (era tables, crash eras, calibration, baselines): `seeds/<run name>.md` in this directory.
