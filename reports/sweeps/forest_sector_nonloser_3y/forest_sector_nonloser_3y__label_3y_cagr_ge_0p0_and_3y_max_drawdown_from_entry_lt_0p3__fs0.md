# Seed stability — forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0

- sweep: `forest_sector_nonloser_3y` (config `experiments/sweeps/forest_sector_nonloser_3y.toml`)
- dataset version: `dataset_v1.4` (pinned, immutable)
- scheme: `walkforward`, folds: `all`, git `a8e29b94f335c3928224432511860e65fbd45452`
- cell: `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` (3y)
- model family: `random_forest`, params `{"bootstrap": true, "class_weight": 1.0, "criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490, "n_jobs": 8}`
- feature set: `fs0`
- parameter set: `set0` = `{"criterion": "entropy", "max_depth": 4, "max_features": 0.205191, "max_samples": 0.663781, "min_samples_leaf": 72, "n_estimators": 490}`
- seeds: [23, 232, 1776] — 3/3 completed
- pooled `precision_at_20` across seeds: mean 0.7823, std 0.0048, min 0.7781, max 0.7875, 95% CI [0.7704, 0.7941]

**Reading this report.** Each seed is a full walk-forward run of the same configuration; only the model's own randomness (row and column subsampling, tie-breaking) differs between them. The spread here is therefore the part of the number that is chance in the fit — a wide interval, or a `min` far below the `mean`, means the candidate's rank in the sweep is not trustworthy. The interval is a Student-t interval over the completed seeds (n − 1 degrees of freedom): with two or three seeds it is wide by construction, which is the honest width. Everything here is still **model selection on walk-forward folds** — selection-biased, never a final result.

## Pooled metrics across seeds

| metric                                                  | n | mean     | std      | min     | max     | ci95_low   | ci95_high  |
| ------------------------------------------------------- | - | -------- | -------- | ------- | ------- | ---------- | ---------- |
| precision_at_20                                         | 3 | 0.7823   | 0.0048   | 0.7781  | 0.7875  | 0.7704     | 0.7941     |
| recall_at_prec_0.75                                     | 3 | 0.3755   | 0.0012   | 0.3741  | 0.3763  | 0.3724     | 0.3787     |
| n_at_prec_0.75                                          | 3 | 48325    | 160.4961 | 48140   | 48427   | 47926.3056 | 48723.6944 |
| recall_at_prec_0.9                                      | 3 | 0.0937   | 0.0025   | 0.0913  | 0.0963  | 0.0875     | 0.1000     |
| n_at_prec_0.9                                           | 3 | 10050    | 268.9033 | 9790    | 10327   | 9382.0071  | 10717.9929 |
| conf_at_20                                              | 3 | 0.7484   | 0.0003   | 0.7482  | 0.7487  | 0.7478     | 0.7491     |
| recall_at_20                                            | 3 | 0.0026   | 0.0000   | 0.0026  | 0.0026  | 0.0026     | 0.0026     |
| precision_at_50                                         | 3 | 0.7554   | 0.0019   | 0.7538  | 0.7575  | 0.7507     | 0.7602     |
| conf_at_50                                              | 3 | 0.7428   | 0.0004   | 0.7424  | 0.7431  | 0.7418     | 0.7437     |
| recall_at_50                                            | 3 | 0.0063   | 0.0000   | 0.0062  | 0.0063  | 0.0062     | 0.0063     |
| pr_auc                                                  | 3 | 0.5363   | 0.0003   | 0.5359  | 0.5365  | 0.5355     | 0.5371     |
| brier                                                   | 3 | 0.2149   | 0.0001   | 0.2148  | 0.2149  | 0.2147     | 0.2151     |
| base_rate_brier                                         | 3 | 0.2371   | 0.0000   | 0.2371  | 0.2371  | 0.2371     | 0.2371     |
| base_rate                                               | 3 | 0.3866   | 0        | 0.3866  | 0.3866  | 0.3866     | 0.3866     |
| screen_n                                                | 3 | 640      | 0        | 640     | 640     | 640        | 640        |
| screen_precision                                        | 3 | 0.7609   | 0.0041   | 0.7578  | 0.7656  | 0.7507     | 0.7712     |
| screen_n_stocks                                         | 3 | 178.6667 | 2.0817   | 177     | 181     | 173.4955   | 183.8378   |
| screen_top_group_share                                  | 3 | 0.1828   | 0.0016   | 0.1812  | 0.1844  | 0.1789     | 0.1867     |
| screen_mean_label_3y_beat_spy                           | 3 | 0.5302   | 0.0117   | 0.5188  | 0.5422  | 0.5011     | 0.5593     |
| screen_mean_fwd_3y_excess_cagr                          | 3 | 0.0026   | 0.0024   | -0.0002 | 0.0043  | -0.0034    | 0.0087     |
| screen_median_fwd_3y_excess_cagr                        | 3 | 0.0073   | 0.0022   | 0.0053  | 0.0097  | 0.0017     | 0.0129     |
| screen_mean_fwd_3y_cagr                                 | 3 | 0.0984   | 0.0022   | 0.0958  | 0.0998  | 0.0928     | 0.1039     |
| screen_median_fwd_3y_cagr                               | 3 | 0.1142   | 0.0038   | 0.1108  | 0.1182  | 0.1048     | 0.1235     |
| screen_mean_fwd_3y_max_drawdown_from_entry              | 3 | 0.1672   | 0.0011   | 0.1661  | 0.1683  | 0.1645     | 0.1699     |
| screen_median_fwd_3y_max_drawdown_from_entry            | 3 | 0.0836   | 0.0018   | 0.0817  | 0.0852  | 0.0792     | 0.0880     |
| screen_mean_label_3y_cagr_lt_0p0                        | 3 | 0.1646   | 0.0024   | 0.1625  | 0.1672  | 0.1587     | 0.1705     |
| screen_mean_label_3y_cagr_lt_m0p1                       | 3 | 0.0604   | 0.0033   | 0.0578  | 0.0641  | 0.0523     | 0.0685     |
| screen_mean_label_3y_max_drawdown_from_entry_ge_0p4     | 3 | 0.1146   | 0.0048   | 0.1094  | 0.1187  | 0.1027     | 0.1264     |
| screen_mean_label_3y_cagr_ge_0p15                       | 3 | 0.3495   | 0.0079   | 0.3422  | 0.3578  | 0.3299     | 0.3690     |
| screen_mean_label_3y_cagr_ge_0p25                       | 3 | 0.0687   | 0.0054   | 0.0625  | 0.0719  | 0.0553     | 0.0822     |
| screen_mean_label_3y_excess_cagr_ge_0p05                | 3 | 0.3224   | 0.0050   | 0.3187  | 0.3281  | 0.3099     | 0.3349     |
| n_stocks_at_20                                          | 3 | 14.0833  | 0.0722   | 14      | 14.1250 | 13.9041    | 14.2626    |
| pick_mean_label_3y_beat_spy_at_20                       | 3 | 0.4625   | 0.0031   | 0.4594  | 0.4656  | 0.4547     | 0.4703     |
| pick_mean_fwd_3y_excess_cagr_at_20                      | 3 | -0.0109  | 0.0025   | -0.0136 | -0.0086 | -0.0172    | -0.0047    |
| pick_median_fwd_3y_excess_cagr_at_20                    | 3 | -0.0096  | 0.0008   | -0.0102 | -0.0087 | -0.0116    | -0.0076    |
| pick_mean_fwd_3y_cagr_at_20                             | 3 | 0.0827   | 0.0026   | 0.0800  | 0.0852  | 0.0763     | 0.0891     |
| pick_median_fwd_3y_cagr_at_20                           | 3 | 0.0989   | 0.0004   | 0.0986  | 0.0994  | 0.0979     | 0.0999     |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_20          | 3 | 0.1581   | 0.0046   | 0.1554  | 0.1634  | 0.1467     | 0.1696     |
| pick_median_fwd_3y_max_drawdown_from_entry_at_20        | 3 | 0.0727   | 0.0023   | 0.0704  | 0.0749  | 0.0671     | 0.0783     |
| pick_mean_label_3y_cagr_lt_0p0_at_20                    | 3 | 0.1313   | 0.0063   | 0.1250  | 0.1375  | 0.1157     | 0.1468     |
| pick_mean_label_3y_cagr_lt_m0p1_at_20                   | 3 | 0.0583   | 0.0090   | 0.0531  | 0.0688  | 0.0359     | 0.0807     |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20 | 3 | 0.0958   | 0.0110   | 0.0844  | 0.1062  | 0.0686     | 0.1231     |
| pick_mean_label_3y_cagr_ge_0p15_at_20                   | 3 | 0.2646   | 0.0065   | 0.2594  | 0.2719  | 0.2484     | 0.2807     |
| pick_mean_label_3y_cagr_ge_0p25_at_20                   | 3 | 0.0323   | 0.0095   | 0.0219  | 0.0406  | 0.0086     | 0.0560     |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_20            | 3 | 0.2906   | 0.0063   | 0.2844  | 0.2969  | 0.2751     | 0.3062     |
| all_mean_label_3y_beat_spy                              | 3 | 0.3630   | 0        | 0.3630  | 0.3630  | 0.3630     | 0.3630     |
| all_mean_fwd_3y_excess_cagr                             | 3 | -0.1056  | 0        | -0.1056 | -0.1056 | -0.1056    | -0.1056    |
| all_median_fwd_3y_excess_cagr                           | 3 | -0.0730  | 0        | -0.0730 | -0.0730 | -0.0730    | -0.0730    |
| all_mean_fwd_3y_cagr                                    | 3 | -0.0133  | 0        | -0.0133 | -0.0133 | -0.0133    | -0.0133    |
| all_median_fwd_3y_cagr                                  | 3 | 0.0174   | 0        | 0.0174  | 0.0174  | 0.0174     | 0.0174     |
| all_mean_fwd_3y_max_drawdown_from_entry                 | 3 | 0.4413   | 0        | 0.4413  | 0.4413  | 0.4413     | 0.4413     |
| all_median_fwd_3y_max_drawdown_from_entry               | 3 | 0.4033   | 0        | 0.4033  | 0.4033  | 0.4033     | 0.4033     |
| all_mean_label_3y_cagr_lt_0p0                           | 3 | 0.4568   | 0.0000   | 0.4568  | 0.4568  | 0.4568     | 0.4568     |
| all_mean_label_3y_cagr_lt_m0p1                          | 3 | 0.3223   | 0        | 0.3223  | 0.3223  | 0.3223     | 0.3223     |
| all_mean_label_3y_max_drawdown_from_entry_ge_0p4        | 3 | 0.5034   | 0        | 0.5034  | 0.5034  | 0.5034     | 0.5034     |
| all_mean_label_3y_cagr_ge_0p15                          | 3 | 0.2674   | 0        | 0.2674  | 0.2674  | 0.2674     | 0.2674     |
| all_mean_label_3y_cagr_ge_0p25                          | 3 | 0.1469   | 0        | 0.1469  | 0.1469  | 0.1469     | 0.1469     |
| all_mean_label_3y_excess_cagr_ge_0p05                   | 3 | 0.2763   | 0        | 0.2763  | 0.2763  | 0.2763     | 0.2763     |

<details><summary>Every other pooled metric</summary>

| metric                                                  | n | mean      | std    | min       | max       | ci95_low  | ci95_high |
| ------------------------------------------------------- | - | --------- | ------ | --------- | --------- | --------- | --------- |
| n_test                                                  | 3 | 256351    | 0      | 256351    | 256351    | 256351    | 256351    |
| effective_n                                             | 3 | 8215.4386 | 0      | 8215.4386 | 8215.4386 | 8215.4386 | 8215.4386 |
| roc_auc                                                 | 3 | 0.6870    | 0.0002 | 0.6868    | 0.6873    | 0.6864    | 0.6876    |
| n_stocks_at_50                                          | 3 | 29.4375   | 0.3802 | 29.1875   | 29.8750   | 28.4931   | 30.3819   |
| pick_mean_label_3y_beat_spy_at_50                       | 3 | 0.4421    | 0.0007 | 0.4412    | 0.4425    | 0.4403    | 0.4439    |
| pick_mean_fwd_3y_excess_cagr_at_50                      | 3 | -0.0138   | 0.0004 | -0.0142   | -0.0134   | -0.0148   | -0.0127   |
| pick_median_fwd_3y_excess_cagr_at_50                    | 3 | -0.0137   | 0.0014 | -0.0146   | -0.0121   | -0.0172   | -0.0102   |
| pick_mean_fwd_3y_cagr_at_50                             | 3 | 0.0818    | 0.0009 | 0.0810    | 0.0828    | 0.0796    | 0.0840    |
| pick_median_fwd_3y_cagr_at_50                           | 3 | 0.1039    | 0.0009 | 0.1034    | 0.1049    | 0.1017    | 0.1061    |
| pick_mean_fwd_3y_max_drawdown_from_entry_at_50          | 3 | 0.1748    | 0.0013 | 0.1736    | 0.1763    | 0.1715    | 0.1782    |
| pick_median_fwd_3y_max_drawdown_from_entry_at_50        | 3 | 0.0770    | 0.0001 | 0.0769    | 0.0770    | 0.0768    | 0.0772    |
| pick_mean_label_3y_cagr_lt_0p0_at_50                    | 3 | 0.1704    | 0.0036 | 0.1663    | 0.1725    | 0.1615    | 0.1794    |
| pick_mean_label_3y_cagr_lt_m0p1_at_50                   | 3 | 0.0758    | 0.0019 | 0.0737    | 0.0775    | 0.0711    | 0.0806    |
| pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_50 | 3 | 0.1271    | 0.0031 | 0.1237    | 0.1300    | 0.1193    | 0.1349    |
| pick_mean_label_3y_cagr_ge_0p15_at_50                   | 3 | 0.2725    | 0.0063 | 0.2662    | 0.2787    | 0.2570    | 0.2880    |
| pick_mean_label_3y_cagr_ge_0p25_at_50                   | 3 | 0.0404    | 0.0019 | 0.0387    | 0.0425    | 0.0357    | 0.0452    |
| pick_mean_label_3y_excess_cagr_ge_0p05_at_50            | 3 | 0.2654    | 0.0044 | 0.2612    | 0.2700    | 0.2545    | 0.2763    |

</details>

## Per-seed pooled values

| seed | status    | precision_at_20 | recall_at_prec_0.75 | n_at_prec_0.75 | recall_at_prec_0.9 | n_at_prec_0.9 | conf_at_20 | recall_at_20 | precision_at_50 | conf_at_50 | recall_at_50 | pr_auc | brier  | base_rate_brier | base_rate | screen_n | screen_precision | screen_n_stocks | screen_top_group_share | screen_mean_label_3y_beat_spy | screen_mean_fwd_3y_excess_cagr | screen_median_fwd_3y_excess_cagr | screen_mean_fwd_3y_cagr | screen_median_fwd_3y_cagr | screen_mean_fwd_3y_max_drawdown_from_entry | screen_median_fwd_3y_max_drawdown_from_entry | screen_mean_label_3y_cagr_lt_0p0 | screen_mean_label_3y_cagr_lt_m0p1 | screen_mean_label_3y_max_drawdown_from_entry_ge_0p4 | screen_mean_label_3y_cagr_ge_0p15 | screen_mean_label_3y_cagr_ge_0p25 | screen_mean_label_3y_excess_cagr_ge_0p05 | n_stocks_at_20 | pick_mean_label_3y_beat_spy_at_20 | pick_mean_fwd_3y_excess_cagr_at_20 | pick_median_fwd_3y_excess_cagr_at_20 | pick_mean_fwd_3y_cagr_at_20 | pick_median_fwd_3y_cagr_at_20 | pick_mean_fwd_3y_max_drawdown_from_entry_at_20 | pick_median_fwd_3y_max_drawdown_from_entry_at_20 | pick_mean_label_3y_cagr_lt_0p0_at_20 | pick_mean_label_3y_cagr_lt_m0p1_at_20 | pick_mean_label_3y_max_drawdown_from_entry_ge_0p4_at_20 | pick_mean_label_3y_cagr_ge_0p15_at_20 | pick_mean_label_3y_cagr_ge_0p25_at_20 | pick_mean_label_3y_excess_cagr_ge_0p05_at_20 | all_mean_label_3y_beat_spy | all_mean_fwd_3y_excess_cagr | all_median_fwd_3y_excess_cagr | all_mean_fwd_3y_cagr | all_median_fwd_3y_cagr | all_mean_fwd_3y_max_drawdown_from_entry | all_median_fwd_3y_max_drawdown_from_entry | all_mean_label_3y_cagr_lt_0p0 | all_mean_label_3y_cagr_lt_m0p1 | all_mean_label_3y_max_drawdown_from_entry_ge_0p4 | all_mean_label_3y_cagr_ge_0p15 | all_mean_label_3y_cagr_ge_0p25 | all_mean_label_3y_excess_cagr_ge_0p05 | report                                                                                               |
| ---- | --------- | --------------- | ------------------- | -------------- | ------------------ | ------------- | ---------- | ------------ | --------------- | ---------- | ------------ | ------ | ------ | --------------- | --------- | -------- | ---------------- | --------------- | ---------------------- | ----------------------------- | ------------------------------ | -------------------------------- | ----------------------- | ------------------------- | ------------------------------------------ | -------------------------------------------- | -------------------------------- | --------------------------------- | --------------------------------------------------- | --------------------------------- | --------------------------------- | ---------------------------------------- | -------------- | --------------------------------- | ---------------------------------- | ------------------------------------ | --------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------------------------ | ------------------------------------ | ------------------------------------- | ------------------------------------------------------- | ------------------------------------- | ------------------------------------- | -------------------------------------------- | -------------------------- | --------------------------- | ----------------------------- | -------------------- | ---------------------- | --------------------------------------- | ----------------------------------------- | ----------------------------- | ------------------------------ | ------------------------------------------------ | ------------------------------ | ------------------------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 23   | completed | 0.7875          | 0.3762              | 48408          | 0.0936             | 10033         | 0.7482     | 0.0026       | 0.7538          | 0.7424     | 0.0062       | 0.5365 | 0.2148 | 0.2371          | 0.3866    | 640      | 0.7656           | 178             | 0.1828                 | 0.5188                        | -0.0002                        | 0.0053                           | 0.0958                  | 0.1108                    | 0.1661                                     | 0.0817                                       | 0.1641                           | 0.0641                            | 0.1187                                              | 0.3422                            | 0.0625                            | 0.3203                                   | 14             | 0.4625                            | -0.0136                            | -0.0087                              | 0.0800                      | 0.0987                        | 0.1554                                         | 0.0727                                           | 0.1250                               | 0.0531                                | 0.0844                                                  | 0.2594                                | 0.0219                                | 0.2844                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0__s23.md   |
| 232  | completed | 0.7781          | 0.3763              | 48427          | 0.0963             | 10327         | 0.7484     | 0.0026       | 0.7550          | 0.7428     | 0.0063       | 0.5365 | 0.2149 | 0.2371          | 0.3866    | 640      | 0.7594           | 181             | 0.1844                 | 0.5422                        | 0.0043                         | 0.0097                           | 0.0998                  | 0.1182                    | 0.1673                                     | 0.0840                                       | 0.1625                           | 0.0594                            | 0.1094                                              | 0.3578                            | 0.0719                            | 0.3281                                   | 14.1250        | 0.4656                            | -0.0086                            | -0.0099                              | 0.0852                      | 0.0986                        | 0.1555                                         | 0.0749                                           | 0.1313                               | 0.0531                                | 0.0969                                                  | 0.2625                                | 0.0344                                | 0.2906                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0__s232.md  |
| 1776 | completed | 0.7812          | 0.3741              | 48140          | 0.0913             | 9790          | 0.7487     | 0.0026       | 0.7575          | 0.7431     | 0.0063       | 0.5359 | 0.2149 | 0.2371          | 0.3866    | 640      | 0.7578           | 177             | 0.1812                 | 0.5297                        | 0.0038                         | 0.0069                           | 0.0995                  | 0.1135                    | 0.1683                                     | 0.0852                                       | 0.1672                           | 0.0578                            | 0.1156                                              | 0.3484                            | 0.0719                            | 0.3187                                   | 14.1250        | 0.4594                            | -0.0105                            | -0.0102                              | 0.0827                      | 0.0994                        | 0.1634                                         | 0.0704                                           | 0.1375                               | 0.0688                                | 0.1062                                                  | 0.2719                                | 0.0406                                | 0.2969                                       | 0.3630                     | -0.1056                     | -0.0730                       | -0.0133              | 0.0174                 | 0.4413                                  | 0.4033                                    | 0.4568                        | 0.3223                         | 0.5034                                           | 0.2674                         | 0.1469                         | 0.2763                                | forest_sector_nonloser_3y__label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3__fs0__s1776.md |

## Era slices across seeds (per test year)

Per-fold metrics under walk-forward are per test year. A candidate whose mean holds up but whose per-year `min` collapses in some eras is seed-fragile exactly where it matters.

| era  | crash | n | precision_at_20 mean | precision_at_20 std | precision_at_20 min | precision_at_20 max |
| ---- | ----- | - | -------------------- | ------------------- | ------------------- | ------------------- |
| 2005 |       | 3 | 0.7000               | 0.0000              | 0.7000              | 0.7000              |
| 2006 |       | 3 | 0.5500               | 0.1323              | 0.4000              | 0.6500              |
| 2007 |       | 3 | 0.2333               | 0.0764              | 0.1500              | 0.3000              |
| 2008 | GFC   | 3 | 0.3833               | 0.0577              | 0.3500              | 0.4500              |
| 2009 | GFC   | 3 | 0.9667               | 0.0577              | 0.9000              | 1                   |
| 2010 |       | 3 | 1                    | 0                   | 1                   | 1                   |
| 2011 |       | 3 | 0.9667               | 0.0289              | 0.9500              | 1                   |
| 2012 |       | 3 | 0.9833               | 0.0289              | 0.9500              | 1                   |
| 2013 |       | 3 | 0.9500               | 0.0000              | 0.9500              | 0.9500              |
| 2014 |       | 3 | 0.8667               | 0.0289              | 0.8500              | 0.9000              |
| 2015 |       | 3 | 0.9667               | 0.0577              | 0.9000              | 1                   |
| 2016 |       | 3 | 0.9167               | 0.0289              | 0.9000              | 0.9500              |
| 2017 |       | 3 | 0.8333               | 0.0577              | 0.8000              | 0.9000              |
| 2018 |       | 3 | 0.9333               | 0.0289              | 0.9000              | 0.9500              |
| 2019 |       | 3 | 0.5333               | 0.1041              | 0.4500              | 0.6500              |
| 2020 | COVID | 3 | 0.7333               | 0.1041              | 0.6500              | 0.8500              |

Per-seed reports (era tables, crash eras, calibration, baselines): `seeds/<run name>.md` in this directory.
