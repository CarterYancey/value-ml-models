# full against pre2018

Both rankings cover the same 2973 rows of `data/datasets/inference_2026-11-20` after the filters dollar_volume_3m_rank >= 0.2.

| ranking | leg | model | fit on | last snapshot fit | bundle run |
|---|---|---|---|---|---|
| full | forest_nonloser_dd30_3y_v141 | random_forest | all labeled rows |  | 1f8d8f9061c7 |
| full | factor_mom_12_2_3y_v141 | rank_factor | all labeled rows |  | a91bf597bad3 |
| full | factor_roc_greenblatt_3y_v141 | rank_factor | all labeled rows |  | d181b5262ffe |
| pre2018 | forest_nonloser_dd30_3y_v141 | random_forest | labeled rows before 2018-01-01 | 2017-12-29 | 521b533a479c |
| pre2018 | factor_mom_12_2_3y_v141 | rank_factor | all labeled rows |  | a91bf597bad3 |
| pre2018 | factor_roc_greenblatt_3y_v141 | rank_factor | all labeled rows |  | d181b5262ffe |

Legs with identical ranks in both files: `factor_mom_12_2_3y_v141`, `factor_roc_greenblatt_3y_v141`. Legs that differ: `forest_nonloser_dd30_3y_v141`.

## The picks under full

| pick | ticker | sector | position under full | position under pre2018 | pick under pre2018 | forest_nonloser_dd30_3y_v141 rank, full | forest_nonloser_dd30_3y_v141 rank, pre2018 | forest_nonloser_dd30_3y_v141 score, full | forest_nonloser_dd30_3y_v141 score, pre2018 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RPRX | Healthcare | 1 | 1 | 1 | 72 | 100 | 0.677 | 0.703 |
| 2 | KO | Consumer Defensive | 2 | 3 | 3 | 21 | 36 | 0.688 | 0.717 |
| 3 | EBAY | Consumer Cyclical | 3 | 2 | 2 | 335 | 327 | 0.628 | 0.655 |
| 4 | CHD | Consumer Defensive | 4 | 4 | 4 | 53 | 57 | 0.680 | 0.712 |
| 5 | SAIC | Technology | 5 | 5 | 5 | 447 | 453 | 0.604 | 0.630 |
| 6 | V | Financial Services | 7 | 6 | 6 | 52 | 84 | 0.680 | 0.706 |
| 7 | HAS | Consumer Cyclical | 8 | 12 |  | 369 | 434 | 0.621 | 0.634 |
| 8 | NDSN | Industrials | 9 | 10 | 9 | 105 | 160 | 0.671 | 0.692 |
| 9 | WAB | Industrials | 10 | 13 |  | 161 | 218 | 0.661 | 0.681 |
| 10 | PSX | Energy | 11 | 9 | 8 | 378 | 402 | 0.619 | 0.639 |

## The picks under pre2018

| pick | ticker | sector | position under pre2018 | position under full | pick under full | forest_nonloser_dd30_3y_v141 rank, pre2018 | forest_nonloser_dd30_3y_v141 rank, full | forest_nonloser_dd30_3y_v141 score, pre2018 | forest_nonloser_dd30_3y_v141 score, full |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RPRX | Healthcare | 1 | 1 | 1 | 100 | 72 | 0.703 | 0.677 |
| 2 | EBAY | Consumer Cyclical | 2 | 3 | 3 | 327 | 335 | 0.655 | 0.628 |
| 3 | KO | Consumer Defensive | 3 | 2 | 2 | 36 | 21 | 0.717 | 0.688 |
| 4 | CHD | Consumer Defensive | 4 | 4 | 4 | 57 | 53 | 0.712 | 0.680 |
| 5 | SAIC | Technology | 5 | 5 | 5 | 453 | 447 | 0.630 | 0.604 |
| 6 | V | Financial Services | 6 | 7 | 6 | 84 | 52 | 0.706 | 0.680 |
| 7 | JNJ | Healthcare | 8 | 12 |  | 70 | 79 | 0.709 | 0.675 |
| 8 | PSX | Energy | 9 | 11 | 10 | 402 | 378 | 0.639 | 0.619 |
| 9 | NDSN | Industrials | 10 | 9 | 8 | 160 | 105 | 0.692 | 0.671 |
| 10 | ADP | Industrials | 11 | 13 |  | 56 | 50 | 0.712 | 0.680 |

The two lists share 8 of 10 picks.

## How far the rankings agree

| top | shared by mean rank | shared by forest_nonloser_dd30_3y_v141 rank |
|---|---|---|
| 10 | 8 | 8 |
| 20 | 18 | 16 |
| 50 | 49 | 39 |
| 100 | 97 | 85 |
| 200 | 193 | 183 |

| column | Spearman correlation |
|---|---|
| mean_rank | 0.998 |
| rank_forest_nonloser_dd30_3y_v141 | 0.993 |

## Largest moves of `forest_nonloser_dd30_3y_v141` among the top 50 of either ranking

A positive move means `pre2018` ranks the stock lower (a larger rank number) than `full` does.

| ticker | sector | position full | position pre2018 | forest_nonloser_dd30_3y_v141 rank full | forest_nonloser_dd30_3y_v141 rank pre2018 | forest_nonloser_dd30_3y_v141 score full | forest_nonloser_dd30_3y_v141 score pre2018 | move |
|---|---|---|---|---|---|---|---|---|
| LNTH | Healthcare | 46 | 56 | 569 | 650 | 0.587 | 0.599 | 81 |
| AME | Industrials | 40 | 48 | 102 | 167 | 0.671 | 0.690 | 65 |
| HAS | Consumer Cyclical | 8 | 12 | 369 | 434 | 0.621 | 0.634 | 65 |
| EXPD | Industrials | 19 | 25 | 137 | 200 | 0.665 | 0.684 | 63 |
| WAB | Industrials | 10 | 13 | 161 | 218 | 0.661 | 0.681 | 57 |
| NDSN | Industrials | 9 | 10 | 105 | 160 | 0.671 | 0.692 | 55 |
| OPLN | Consumer Cyclical | 24 | 29 | 325 | 375 | 0.629 | 0.643 | 50 |
| CTAS | Industrials | 38 | 42 | 29 | 76 | 0.685 | 0.708 | 47 |
| WTS | Industrials | 47 | 50 | 152 | 196 | 0.663 | 0.685 | 44 |
| INSW | Energy | 33 | 40 | 584 | 628 | 0.586 | 0.604 | 44 |
| DMLP | Energy | 43 | 47 | 122 | 166 | 0.667 | 0.690 | 44 |
| ADI | Technology | 25 | 33 | 618 | 659 | 0.581 | 0.597 | 41 |
| PM | Consumer Defensive | 6 | 7 | 100 | 140 | 0.671 | 0.695 | 40 |
| BMY | Healthcare | 20 | 22 | 210 | 250 | 0.652 | 0.673 | 40 |
| GIC | Industrials | 41 | 34 | 363 | 326 | 0.622 | 0.655 | -37 |

## Sectors of the top 50 by mean rank

| sector | full | pre2018 |
|---|---|---|
| Industrials | 14 | 14 |
| Healthcare | 8 | 7 |
| Technology | 8 | 9 |
| Energy | 6 | 6 |
| Consumer Defensive | 6 | 6 |
| Consumer Cyclical | 4 | 4 |
| Communication Services | 2 | 2 |
| Financial Services | 2 | 2 |

Both rankings are deployment scores with no test rows. This report says where they differ, and nothing about which is better.
