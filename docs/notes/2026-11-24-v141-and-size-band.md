# dataset_v1.4.1: the candidate's record on it, and the size band by final value

This note records the session of 2026-11-24, decisions 55 to 58 of the
[decision log](2026-09-29-decisions.md). Terms are defined in
[GLOSSARY.md](../../GLOSSARY.md). Every number here is a walk-forward
or backtest number on `dataset_v1.4.1` unless the line says v1.4.
Numbers on the two versions are never compared as results. Where the
note sets them side by side, it says so and says why.

## 1. What dataset_v1.4.1 is

Carter asked for `dataset_v1.4.1`. Upstream decision 0021 (2026-11-24)
introduced patch versions after the v1.4 rebuild of 2026-11-23 went
unnoticed by the ledger (decision 54). The two manifests give these
facts:

| | `dataset_v1.4` (rebuilt 2026-11-23) | `dataset_v1.4.1` |
|---|---|---|
| created | 2026-11-23T00:59Z | 2026-11-24T06:34Z |
| rows | 1,537,293 | 1,537,293 |
| effective rows, 3y | 48,281 | 48,281 |
| columns | 390 in six groups | the same 390 |
| provenance block | none | raw snapshot 2026-11-21, code commit `6cffa65`, sha256 of every file |
| `dataset.parquet` sha256 | not recorded | `be2b664c6739b93d5b5a7df1d085c09f09575071dd02d1f1426ed1586e052085` |

Upstream built v1.4.1 from the same interim files as the rebuilt v1.4.
Upstream calls the two equivalent up to floating-point noise in the
sample weights, with relative differences near 1e-14. Under CLAUDE.md
they are still two versions, so this session reran what it needed on
v1.4.1 instead of comparing with v1.4.

**Code.** The branch `claude/dataset-provenance` makes every run row,
result record, report header, final-eval row and prediction sidecar
carry `dataset_sha256`. That is the fingerprint upstream's manual,
section 1, asks downstream to log. The 527 tests pass. A ledger file
written under the older header is rewritten with the new column on
the next append, rows unchanged. A manifest without a provenance block
gives an empty string.

## 2. The candidate's legs refit on v1.4.1

The three leg configs were copied with `dataset_version =
"dataset_v1.4.1"` and the suffix `_v141`, nothing else changed. The
configs predicted fold metrics within noise and p@20 within 0.01.

| forest, fold means over 2005–2020 | v1.4 (old build, report of 2026-10-01) | v1.4.1 |
|---|---|---|
| PR-AUC | 0.5854 | 0.5848 |
| p@20 | 0.7875 | 0.7500 |
| p@50 | 0.7538 | 0.7412 |
| base rate | 0.3916 | 0.3928 |
| test rows | 256,351 | 255,042 |

The two columns are different builds, and the v1.4 build no longer
exists on disk. The table is context only and compares no results. The
ranking quality is the same: PR-AUC agrees within 0.001. The p@20
prediction missed. Twenty picks a year over sixteen years is 320
picks, and twelve of them changed label or rank. Six of the twelve
were in 2008, where p@20 fell from 0.45 on the old build to 0.15 on
v1.4.1. Four were in 2006.

The bundles are `forest_nonloser_dd30_3y_v141_f259c702a6a6`,
`factor_mom_12_2_3y_v141_121349f6e682` and
`factor_roc_greenblatt_3y_v141_4457ca01bcfb`.

## 3. Screens on v1.4.1, inside the 100k floor

The table reads the candidate's mean-rank blend against same-size
peers, in 20 bands of `log_marketcap_rank`. The screen takes the top
10 a quarter, at most 2 per sector:

| 2005–12 / 2013–20 | picks | same-size peers |
|---|---|---|
| 3-year excess CAGR over SPY, mean | −0.001 / +0.012 | −0.031 / −0.041 |
| lead over peers | **+0.030 / +0.053** | |
| losers (3-year CAGR below zero) | 0.26 / 0.16 | 0.33 / 0.28 |
| precision on cell C's label | 0.60 / 0.77 | 0.52 / 0.58 |

The picks led their peers in 13 of 16 years. The three years they did
not were 2005, 2019 and 2020.

## 4. The candidate's backtests on v1.4.1

The three runs use the fixed rule on the three v1.4.1 bundles. Nothing
else changed from the October configs. The 2021–26 window is read for
the fixed candidate and its sell variant only (decision 28). The
equity path of the run to 2026 equals the 2005–2020 run's to the cent
through 2020-12-31. I checked 192 month-ends.

| | 2005–2020, valued end 2023 | buy and hold to 2026-08-21 | sell discipline to 2026-08-21 | SPY, same deposits, to 2026 |
|---|---|---|---|---|
| deposits | 192,000 | 260,000 | 260,000 | 260,000 |
| final value | 932,471 | 1,159,740 | 1,294,414 | 1,326,084 |
| TWR | 11.76% | 10.99% | 11.48% | 10.93% |
| MWR | 13.65% | 12.20% | 13.02% | 13.20% |
| worst drawdown | −41.0% | −41.0% | −41.3% | −52.9% |
| costs paid | 1,231 | 1,610 | 15,166 | 0 |
| buys | 1,741 | | | |

The next table gives the yearly return minus SPY's, by calendar year, in points:

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to August |
|---|---|---|---|---|---|---|
| buy and hold | −8.9 | +2.3 | −3.9 | −11.4 | −14.5 | −13.2 |
| sell discipline | −9.2 | +1.2 | −9.5 | −8.7 | −12.6 | −9.9 |

On 2005–2020 the buy-and-hold portfolio was ahead of SPY in 10 of 16
calendar years. It was ahead in both of SPY's down years, by 11.7
points in 2008 and by 2.8 in 2018. In 2022 it fell 16.7% against
SPY's 19.0%.

The next table reads the buys of 2021 to 2023 three years on, under
the buy-and-hold rule:

| buys of | excess over SPY, points a year | buys that lost money | lead over same-size peers, points a year |
|---|---|---|---|
| 2021 | −14.6 | 72% | −6.4 |
| 2022 | +0.2 | 45% | +3.5 |
| 2023 | −4.3 | 26% | +6.0 |

**What this replaces.** The candidate table of 2026-10-01 in
findings.md came from the old v1.4 build. Its final values were
1,193,902 for buy and hold and 1,344,630 with the sell discipline.
Those numbers are retired and are not compared, because the build no
longer exists. The shape of the record is the same on v1.4.1. The
candidate is ahead of SPY by final value through 2020 and behind by
August 2026. The whole shortfall falls in 2021 and 2024–26.

## 5. The size band by final value (decision 55, item 3)

Two backtests ran the candidate's config with one more investability
filter each, on 2005–2020 valued at the end of 2023. Decision 55
wrote the rule first. The arm is carried forward if its TWR beats the
candidate's by more than 0.33, the seed spread, with a drawdown no
deeper.

| | candidate | larger half (`log_marketcap_rank >= 0.5`) | large caps (`>= 0.8`) |
|---|---|---|---|
| TWR | 11.76% | **12.51%** | 12.06% |
| MWR | 13.65% | 14.10% | 13.87% |
| final value on 192,000 | 932,471 | 984,128 | 957,370 |
| worst drawdown | −41.0% | −39.3% | −40.2% |
| buys | 1,741 | 1,756 | 1,759 |
| buys' 3-year excess over SPY, 2005–12 / 2013–20 | +0.039 / +0.009 | +0.043 / +0.010 | +0.050 / +0.024 |
| the size band's own excess over SPY (peers) | +0.041 / −0.011 | +0.041 / −0.009 | +0.031 / −0.007 |
| buys' lead over same-size peers | −0.002 / +0.020 | +0.003 / +0.019 | +0.019 / +0.031 |
| buys that lost money | 0.36 / 0.23 | 0.35 / 0.22 | 0.32 / 0.19 |
| peers that lost money | 0.38 / 0.32 | 0.37 / 0.32 | 0.36 / 0.31 |

The next table pairs each arm with the candidate by year, over 16
years, with the standard error of the mean. The 3-year windows
overlap, so the error is a floor:

| arm minus candidate | yearly portfolio return | buys' lead over same-size peers, by cohort | buys' loser share, by cohort |
|---|---|---|---|
| larger half | +0.72 points, se 0.61, ahead 11 of 16, halves +0.96 / +0.49 | +0.15 points, se 0.63, ahead 10 of 16 | −0.9 points, se 0.8, 7 of 16 |
| large caps | 0.00 points, se 0.97, ahead 9 of 16 | +1.5 points, se 0.7, ahead 12 of 16 | −3.9 points, se 1.6, 4 of 16 |

**What the tables say.**

- The candidate already buys mostly from the larger half. Its peers
  earn what the larger half's peers earn, as the peer row shows. The
  filter changes about one buy in twelve, with 15 more buys and a few
  losers fewer. It adds 0.7 points a year of portfolio return, at
  about 1.2 standard errors. The seeds decide whether that is more
  than noise (decision 57).
- Inside large caps the selection is at its best. The buys lead
  same-size peers by 1.9 and 3.1 points a year in the two halves. Four
  points fewer of them lose money than of the candidate's. Both gaps
  are beyond two standard errors. The final value comes out the same
  because large caps as a group earn less. Their peers' excess over
  SPY is 1 point lower in 2005–12. Decision 55 predicted 1 to 3 points
  *below* the candidate, and that prediction missed. The record now
  says the forest's lead is not confined to the worst quintile of
  large caps once momentum and return on capital are added. Decision
  34 measured the forest alone.
- Neither run beats SPY by a different kind of margin than the
  candidate does. Each shows the same 2005–2020 lead, mostly from the
  same stocks.

**The larger half ran to 2026-08-21.** The run is context under
decision 57, the fixed rule read for one more variant:

| | candidate, buy and hold | larger half, buy and hold | SPY |
|---|---|---|---|
| final value on 260,000 | 1,159,740 | 1,246,400 | 1,326,084 |
| TWR | 10.99% | 11.76% | 10.93% |
| MWR | 12.20% | 12.74% | 13.20% |
| worst drawdown | −41.0% | −39.3% | −52.9% |
| yearly return minus SPY's, 2021 to 2026 | −8.9, +2.3, −3.9, −11.4, −14.5, −13.2 | −8.9, +3.3, −4.5, −10.2, −13.7, −12.9 | |
| ahead of SPY, calendar years 2005–2020 | 10 of 16 | 13 of 16 | |

Decision 57 predicted that this arm trails SPY in 2021–26 by less than
the candidate does. The prediction held in four of the six years, by
0.2 to 1.2 points. The giants that carried the index are in the larger
half, but the rule does not pick them. By final value the larger half
ends 6% behind SPY, where the candidate ends 13% behind. Its buys of
2021 trailed SPY by 11.1 points a year, and 70% of them lost money.
The candidate's buys of 2021 trailed by 14.6 points, with 72% losers.

**The seeds confirm the gap (decision 58).** I refit the forest on
seeds 232 and 1776 on v1.4.1. On each seed I backtested the candidate
and the larger half over 2005–2020.

| seed | candidate TWR / MWR / final / drawdown | larger half TWR / MWR / final / drawdown | gap in TWR | paired yearly return |
|---|---|---|---|---|
| 23 | 11.76 / 13.65 / 932,471 / −41.0 | 12.51 / 14.10 / 984,128 / −39.3 | +0.75 | +0.72, se 0.61, ahead 11 of 16 |
| 232 | 11.86 / 13.72 / 940,636 / −40.5 | 12.56 / 14.20 / 995,841 / −38.6 | +0.70 | +0.76, se 0.46, ahead 10 of 16 |
| 1776 | 12.18 / 13.88 / 959,232 / −41.1 | 12.50 / 14.19 / 994,518 / −39.6 | +0.32 | +0.34, se 0.52, ahead 12 of 16 |

The larger half is above the candidate on every seed in TWR, MWR and
final value, with a drawdown 1.5 to 1.9 points shallower. The mean gap
is +0.59 points of TWR against a candidate seed spread of 0.42. The
buys' lead over same-size peers is the same on every seed within 0.1
point. Between 0.2 and 0.7 points fewer buys lose money. Decision 57's
rule is met. The extra return comes from the larger stocks themselves
and not from better picks among them. The change to the candidate is
proposed to Carter and not made (decision 58).

A first attempt at this chain failed on two copy errors of mine. The
first was a wrong config path, and those four backtests left no ledger
rows. The second overwrote the `[model]` name with the experiment
name, and seven failed rows from it are in the ledger. They count as
trials.

## 6. Decision 41's arms re-read under decision 50 (decision 56)

This re-read ran nothing new. The three backtests of 2026-11-23 ran
the forest alone as top 10, top 5 and score weights. All three ran on
the rebuilt v1.4 within four minutes of each other, starting 06:26
UTC. I read them as paired per-year differences, arm minus top 10.

| arm | yearly portfolio return, 2005–2020 | buys' 3-year lead over same-size peers, by cohort | buys' loser share minus peers' |
|---|---|---|---|
| top 5 a month | −1.55 points a year, se 0.84, ahead 5 of 16, both halves negative | −1.0 point, se 1.0, ahead 5 of 16 | +0.4 points, se 1.5, ahead 8 of 16 |
| score weights | −0.03 points, se 0.05, ahead 5 of 16 | 0.00, se 0.03 | −0.02, se 0.09 |

Decision 42 stands: the top 5 is worse by about 1.8 standard errors
and score weights change nothing measurable.

## 7. The November list

I refit the three deployment bundles on v1.4.1, on 1,395,705 labeled
rows with an effective size of 48,281. Then `vml-predict` ran with the
runbook's flags on `inference_2026-11-20`. That dataset has 3,716
rows, and 15 of them have a stale price. Of the rest, 2,973 pass
Carter's floor. The table lists the ten picks by mean rank, at most
two per sector:

| pick | ticker | sector | forest score | forest rank | momentum rank | return-on-capital rank |
|---|---|---|---|---|---|---|
| 1 | RPRX | Healthcare | 0.677 | 72 | 368 | 35 |
| 2 | KO | Consumer Defensive | 0.688 | 21 | 696 | 123 |
| 3 | EBAY | Consumer Cyclical | 0.628 | 335 | 498 | 18 |
| 4 | CHD | Consumer Defensive | 0.680 | 53 | 773 | 76 |
| 5 | SAIC | Technology | 0.604 | 447 | 352 | 111 |
| 6 | V | Financial Services | 0.680 | 52 | 853 | 15 |
| 7 | HAS | Consumer Cyclical | 0.621 | 369 | 441 | 128 |
| 8 | NDSN | Industrials | 0.671 | 105 | 634 | 202 |
| 9 | WAB | Industrials | 0.661 | 161 | 664 | 133 |
| 10 | PSX | Energy | 0.619 | 378 | 130 | 457 |

One of the ten, RPRX, was in the August dry run's top 10. Four were in
its top 50: EBAY, NDSN, RPRX and WAB. The August list came from a
forest trained on the old v1.4 build and from the snapshots of a
different quarter. Most of the turnover is therefore expected, since
the backtest itself buys ten new names every month. The full ranking
and its sidecar are under `predictions/`. This was a run of the
runbook in the sandbox. It is not a deployment decision. Carter
decides what is bought.
