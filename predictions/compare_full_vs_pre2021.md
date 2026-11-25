# full against pre2021

Both rankings cover the same 2973 rows of `data/datasets/inference_2026-11-20` after the filters dollar_volume_3m_rank >= 0.2.

| ranking | leg | model | fit on | last snapshot fit | bundle run |
|---|---|---|---|---|---|
| full | forest_nonloser_dd30_3y_v141 | random_forest | all labeled rows |  | 1f8d8f9061c7 |
| full | factor_mom_12_2_3y_v141 | rank_factor | all labeled rows |  | a91bf597bad3 |
| full | factor_roc_greenblatt_3y_v141 | rank_factor | all labeled rows |  | d181b5262ffe |
| pre2021 | forest_nonloser_dd30_3y_v141 | random_forest | labeled rows before 2021-01-01 | 2020-12-31 | 78618ab2b645 |
| pre2021 | factor_mom_12_2_3y_v141 | rank_factor | all labeled rows |  | a91bf597bad3 |
| pre2021 | factor_roc_greenblatt_3y_v141 | rank_factor | all labeled rows |  | d181b5262ffe |

Legs with identical ranks in both files: `factor_mom_12_2_3y_v141`, `factor_roc_greenblatt_3y_v141`. Legs that differ: `forest_nonloser_dd30_3y_v141`.

## The picks under full

| pick | ticker | sector | position under full | position under pre2021 | pick under pre2021 | forest_nonloser_dd30_3y_v141 rank, full | forest_nonloser_dd30_3y_v141 rank, pre2021 | forest_nonloser_dd30_3y_v141 score, full | forest_nonloser_dd30_3y_v141 score, pre2021 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RPRX | Healthcare | 1 | 1 | 1 | 72 | 65 | 0.677 | 0.688 |
| 2 | KO | Consumer Defensive | 2 | 3 | 3 | 21 | 20 | 0.688 | 0.697 |
| 3 | EBAY | Consumer Cyclical | 3 | 2 | 2 | 335 | 315 | 0.628 | 0.638 |
| 4 | CHD | Consumer Defensive | 4 | 4 | 4 | 53 | 43 | 0.680 | 0.691 |
| 5 | SAIC | Technology | 5 | 7 | 7 | 447 | 465 | 0.604 | 0.607 |
| 6 | V | Financial Services | 7 | 5 | 5 | 52 | 42 | 0.680 | 0.691 |
| 7 | HAS | Consumer Cyclical | 8 | 6 | 6 | 369 | 358 | 0.621 | 0.627 |
| 8 | NDSN | Industrials | 9 | 9 | 8 | 105 | 109 | 0.671 | 0.678 |
| 9 | WAB | Industrials | 10 | 10 | 9 | 161 | 159 | 0.661 | 0.669 |
| 10 | PSX | Energy | 11 | 12 |  | 378 | 379 | 0.619 | 0.623 |

## The picks under pre2021

| pick | ticker | sector | position under pre2021 | position under full | pick under full | forest_nonloser_dd30_3y_v141 rank, pre2021 | forest_nonloser_dd30_3y_v141 rank, full | forest_nonloser_dd30_3y_v141 score, pre2021 | forest_nonloser_dd30_3y_v141 score, full |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RPRX | Healthcare | 1 | 1 | 1 | 65 | 72 | 0.688 | 0.677 |
| 2 | EBAY | Consumer Cyclical | 2 | 3 | 3 | 315 | 335 | 0.638 | 0.628 |
| 3 | KO | Consumer Defensive | 3 | 2 | 2 | 20 | 21 | 0.697 | 0.688 |
| 4 | CHD | Consumer Defensive | 4 | 4 | 4 | 43 | 53 | 0.691 | 0.680 |
| 5 | V | Financial Services | 5 | 7 | 6 | 42 | 52 | 0.691 | 0.680 |
| 6 | HAS | Consumer Cyclical | 6 | 8 | 7 | 358 | 369 | 0.627 | 0.621 |
| 7 | SAIC | Technology | 7 | 5 | 5 | 465 | 447 | 0.607 | 0.604 |
| 8 | NDSN | Industrials | 9 | 9 | 8 | 109 | 105 | 0.678 | 0.671 |
| 9 | WAB | Industrials | 10 | 10 | 9 | 159 | 161 | 0.669 | 0.661 |
| 10 | JNJ | Healthcare | 11 | 12 |  | 57 | 79 | 0.690 | 0.675 |

The two lists share 9 of 10 picks.

## How far the rankings agree

| top | shared by mean rank | shared by forest_nonloser_dd30_3y_v141 rank |
|---|---|---|
| 10 | 10 | 8 |
| 20 | 17 | 17 |
| 50 | 47 | 39 |
| 100 | 97 | 89 |
| 200 | 195 | 192 |

| column | Spearman correlation |
|---|---|
| mean_rank | 0.998 |
| rank_forest_nonloser_dd30_3y_v141 | 0.991 |

## Largest moves of `forest_nonloser_dd30_3y_v141` among the top 50 of either ranking

A positive move means `pre2021` ranks the stock lower (a larger rank number) than `full` does.

| ticker | sector | position full | position pre2021 | forest_nonloser_dd30_3y_v141 rank full | forest_nonloser_dd30_3y_v141 rank pre2021 | forest_nonloser_dd30_3y_v141 score full | forest_nonloser_dd30_3y_v141 score pre2021 | move |
|---|---|---|---|---|---|---|---|---|
| FFIV | Technology | 31 | 20 | 653 | 577 | 0.575 | 0.589 | -76 |
| FTNT | Technology | 58 | 46 | 972 | 904 | 0.526 | 0.539 | -68 |
| NTAP | Technology | 32 | 24 | 824 | 768 | 0.548 | 0.558 | -56 |
| MPC | Energy | 23 | 16 | 538 | 482 | 0.594 | 0.603 | -56 |
| LNTH | Healthcare | 46 | 54 | 569 | 624 | 0.587 | 0.580 | 55 |
| FTDR | Consumer Cyclical | 29 | 25 | 672 | 633 | 0.571 | 0.578 | -39 |
| FTI | Energy | 54 | 49 | 454 | 416 | 0.603 | 0.614 | -38 |
| DINO | Energy | 42 | 37 | 676 | 639 | 0.571 | 0.577 | -37 |
| EXPD | Industrials | 19 | 26 | 137 | 173 | 0.665 | 0.666 | 36 |
| VLO | Energy | 16 | 13 | 557 | 523 | 0.589 | 0.597 | -34 |
| MTCH | Communication Services | 39 | 35 | 571 | 537 | 0.587 | 0.596 | -34 |
| ADI | Technology | 25 | 34 | 618 | 651 | 0.581 | 0.576 | 33 |
| MSI | Technology | 18 | 15 | 119 | 86 | 0.668 | 0.682 | -33 |
| EXEL | Healthcare | 28 | 27 | 498 | 470 | 0.598 | 0.606 | -28 |
| MA | Financial Services | 34 | 32 | 66 | 44 | 0.678 | 0.691 | -22 |

## Sectors of the top 50 by mean rank

| sector | full | pre2021 |
|---|---|---|
| Industrials | 14 | 14 |
| Healthcare | 8 | 6 |
| Technology | 8 | 10 |
| Energy | 6 | 7 |
| Consumer Defensive | 6 | 5 |
| Consumer Cyclical | 4 | 4 |
| Communication Services | 2 | 2 |
| Financial Services | 2 | 2 |

Both rankings are deployment scores with no test rows. This report says where they differ, and nothing about which is better.
