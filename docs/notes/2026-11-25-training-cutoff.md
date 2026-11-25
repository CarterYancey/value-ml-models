# A deployable candidate that does not train on the recent years

This note records the session of 2026-11-25, decision 60 of the
[decision log](2026-09-29-decisions.md). Terms are defined in
[GLOSSARY.md](../../GLOSSARY.md). Every number here is a deployment
score on `dataset_v1.4.1` and `inference_2026-11-20`. A deployment fit
has no test rows, so nothing here is an evaluation. The note says where
two rankings differ and nothing about which is better.

## 1. The question

The candidate leads SPY on 2005–2020 and trails it on 2021–2026. Carter
reads 2021–26 as a bubble that deflates. The deployed candidate is
refit on every labeled row, and the labeled rows of `dataset_v1.4.1`
run to 2023-11-20. So the deployed forest has learned from snapshots
taken inside the years Carter distrusts. Carter asked how the forecasts
on the current inference dataset would change if the deployable
candidate did not train on the past five years.

Only one leg of the candidate trains. Momentum and return on capital
are rank factors, so their ranks are the same in every ranking below.
The comparison is therefore between forests, read through the blend.

## 2. What was built

`vml-train-deploy --train-end DATE` fits only the labeled rows whose
`snapshot_date` is before the date. This is the training cutoff. It
reads no split tag and no label, and it removes only the most recent
rows, as the backtest's year-end refits do. The cutoff is recorded in
the bundle, in the ledger row's `fold` and in every prediction sidecar.
`scripts/compare_predictions.py` compares two `vml-predict` rankings
over the same rows.

"The past five years" has two readings, so I ran both.

| forest | what it has not seen | labeled rows | effective size | last snapshot fit | bundle run |
|---|---|---|---|---|---|
| the deployed forest | nothing: the runbook's refit of 2026-11-24 | 1,395,705 | 48,281 | 2023-11-20 | `1f8d8f9061c7` |
| cutoff 2021-01-01 | no snapshot taken in 2021 or later. A snapshot of 2018–2020 keeps its label, whose window runs into 2021–2023. | 1,243,122 | 42,943 | 2020-12-31 | `78618ab2b645` |
| cutoff 2018-01-01 | no snapshot whose three-year window reaches into 2021. This forest has seen no price from 2021 on. | 1,110,024 | 38,636 | 2017-12-29 | `521b533a479c` |

The ledger rows are `labeled_before_2021-01-01` and
`labeled_before_2018-01-01` under scheme `deployment`, at git
`9f452a5`. The counts match a direct count of the parquet.

## 3. The three rankings

Each ranking ran the runbook's command on `inference_2026-11-20`, with
the floor `dollar_volume_3m_rank >= 0.2`, ten picks and at most two per
sector. All three rank the same 2,973 rows. The deployed forest's run
reproduces the November list of 2026-11-24 exactly.

| pick | the deployed forest | cutoff 2021 | cutoff 2018 |
|---|---|---|---|
| 1 | RPRX | RPRX | RPRX |
| 2 | KO | EBAY | EBAY |
| 3 | EBAY | KO | KO |
| 4 | CHD | CHD | CHD |
| 5 | SAIC | V | SAIC |
| 6 | V | HAS | V |
| 7 | HAS | SAIC | JNJ |
| 8 | NDSN | NDSN | PSX |
| 9 | WAB | WAB | NDSN |
| 10 | PSX | JNJ | ADP |

How far each cutoff ranking agrees with the deployed one:

| | cutoff 2021 | cutoff 2018 |
|---|---|---|
| picks shared with the deployed list | 9 of 10 | 8 of 10 |
| top 50 by mean rank, shared | 47 | 49 |
| top 100 by mean rank, shared | 97 | 97 |
| Spearman correlation of the mean rank | 0.998 | 0.998 |
| forest alone, top 50 shared | 39 | 39 |
| forest alone, Spearman correlation | 0.991 | 0.993 |

The stocks that change sit at the edge of the list. Under the deployed
ranking JNJ is at position 12 and ADP at 13. Under the cutoff rankings
PSX is at position 12, HAS at 12 and WAB at 13.

| change | leaves the list | enters the list |
|---|---|---|
| cutoff 2021 | PSX | JNJ |
| cutoff 2018 | HAS, WAB | JNJ, ADP |

The cutoff forests give higher scores to the same stocks.

| forest | scores of its ten picks |
|---|---|
| the deployed forest | 0.60 to 0.69 |
| cutoff 2021 | 0.61 to 0.70 |
| cutoff 2018 | 0.63 to 0.72 |

A hypothesis for the level is this. The snapshots of 2021–2023 met the
label less often than earlier ones. A forest that has seen them then
scores every stock lower. The level does not change a ranking.

The largest moves of the forest among the top 50 of either ranking are
these. A positive move means the cutoff forest ranks the stock lower.

| cutoff | stocks | forest rank, deployed | forest rank, cutoff |
|---|---|---|---|
| 2021 | FFIV, NTAP, MPC | 653, 824, 538 | 577, 768, 482 |
| 2018 | NDSN, WAB, AME, EXPD, CTAS | 105, 161, 102, 137, 29 | 160, 218, 167, 200, 76 |

The 2018 forest ranks the Industrials in the list a few dozen places
lower than the deployed forest does. Every move is within about 80
places out of 2,973. The sector mix of the top 50 is the same within
two stocks under all three forests.

## 4. Reading

**What was measured.** On 2026-11-20 the deployed list and the
cutoff-2021 list differ in one pick of ten. The cutoff-2018 list
differs in two. The mean rank over 2,973 stocks has a Spearman
correlation of 0.998 with the deployed ranking under either cutoff.

**What it might mean.** Two hypotheses, which the data here cannot
separate:

1. The blend is two thirds rank factors, which do not train, so the
   forest can move the list only a little. The forest alone shares 39
   of its top 50 with the deployed forest, where the blend shares 47
   or 49.
2. The forest's rules are stable. The snapshots of 2021–2023 add 11%
   of the effective size. A shallow forest with a large minimum leaf
   changes little for them. Its parameters are in
   `experiments/forest_nonloser_dd30_3y_v141.toml`.

**The backtest gives context.** The backtest refits the forest at each
year end on the rows whose three-year window is complete 45 days
before January 1. So the forest that traded 2021 through 2023 had seen
no snapshot after late 2017. The forest that traded 2026 had seen none
after late 2022. The shortfall against SPY in 2021–26 was produced by
forests that had not trained on most of those years. As far as the
backtest can tell, training on the recent years is not what made the
candidate trail SPY. That reading is consistent with Carter's: those
years rewarded stocks the candidate does not pick.

**What this cannot say.** It compares rankings on one day and says
nothing about which forest will do better. Choosing between the
deployed forest and a cutoff forest on these numbers would be a
selection with no outcome behind it. Paper trading both is the only
evidence that would separate them.

## 5. What Carter decides

- Carter decides whether paper trading uses the deployed forest or a
  cutoff forest, and which date. The runbook's refit command would
  gain `--train-end`.
- A third paper portfolio, C, could hold the cutoff-2021 list. If
  November is typical it differs from portfolio A by about one pick a
  month. Carter decides whether to keep it.

## 6. Files

- The two cutoff bundles are git-ignored. They are
  `experiments/models/forest_nonloser_dd30_3y_v141_deployment_78618ab2b645`
  and `experiments/models/forest_nonloser_dd30_3y_v141_deployment_521b533a479c`.
- The three rankings and their sidecars are on the lab branch
  `claude/lab-2026-11-25`. Their names are
  `predictions/inference_2026-11-20__candidate_full_v141.csv`,
  `..._pre2021_v141.csv` and `..._pre2018_v141.csv`.
- The two comparison reports are on the same branch, as
  `predictions/compare_full_vs_pre2021.md` and
  `predictions/compare_full_vs_pre2018.md`.
- The code is on `claude/deploy-train-end`, on top of `claude/fix-docs`.
