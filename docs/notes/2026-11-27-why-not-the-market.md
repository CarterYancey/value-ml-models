# Why the candidate has not beaten the market (2026-11-27, decision 81)

Carter asked the central question: the models predict their labels at
precision well above the base rate, and the portfolios built from them
have not beaten the market in the backtests. Why, and what has not been
tried? This note holds the evidence behind decision 81 and, when they
have run, the six backtests it ordered.

## Where the numbers come from

Three sources, all on record.

- The candidate's backtest on `dataset_v1.4.1`, buying from 2005 to
  2026-08-21 (`bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_v141`,
  promoted). Its report carries the per-year returns and the tables
  "What the buys went on to do" and "Against the stocks they were chosen
  from". Its equity file gives the monthly returns used for the beta.
- The walk-forward screen of the candidate's forest in cell C on the 112
  old rank columns (sweep A of decision 78 on `dataset_v1.5.1`), read by
  cohort year against SPY's own three-year CAGR, which the dataset
  carries as a label column.
- A survey of the decision logs for every portfolio-level idea that was
  tried or proposed (items 1 to 10 of the survey are summarized in
  decision 81.6 and in the TODO section "Next, after 2026-11-27").

Terms: **lead** is the picks' mean three-year CAGR minus their same-size
peers'. **Losers** is the share of picks whose three-year CAGR was
negative. **Cohort year** is the year the picks were made; their
outcome is measured over the following three years. **TWR** is the
time-weighted return, which treats deposits as external flows. The
**money-weighted CAGR** is what the deposits actually earned.

## 1. Sixteen years ahead, six years behind

The candidate's yearly time-weighted return against SPY's, in points of
excess:

| 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| −3.7 | −5.8 | −4.6 | +11.7 | +4.0 | +15.4 | +4.8 | −1.5 | +11.1 | −4.5 | +6.9 | −0.9 | +0.5 | +2.8 | +7.0 | +3.5 |

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to August |
|---|---|---|---|---|---|
| −8.9 | +2.3 | −3.9 | −11.4 | −14.6 | −13.2 |

| period | candidate TWR | SPY TWR | monthly beta |
|---|---|---|---|
| 2005 to 2020 | 12.4% a year | 9.4% | 0.87 |
| 2021 to 2026 | 7.1% a year | 15.3% | 0.83 |
| whole window | 11.0% (money-weighted 12.2%) | 10.9% (13.2%) | 0.86 |

Over the whole window the portfolio's monthly correlation with SPY is
0.93. In SPY's up months it earned 88% of SPY's gain; in SPY's down
months it suffered 80% of SPY's loss. Its annualized volatility was
15.3% against SPY's 16.5%, and its worst drawdown −41% against −53%.
The money-weighted CAGR is behind SPY's although the time-weighted
return is not, because the monthly deposits make the account largest in
the years it lost.

## 2. The skill is real, and it is loser-avoidance

From the backtest's own reading of its 1,951 buys with a full
three-year window, each buy counted once, against SPY and against the
other candidates of the same month:

| | buys | all candidates (equal-weighted) | same-size candidates |
|---|---|---|---|
| three-year return minus SPY's, a year | +0.66 | −10.29 | −3.80 |
| share that lost money | 23.4% | 44.0% | 32.7% |

The buys led same-size peers by 4.46 points a year and lost money a
third less often. On the walk-forward screen (cell C, 112 old ranks,
2005 to 2020) the picks' realized volatility was 0.248 against the
peers' 0.360 and their drawdown from entry 0.175 against 0.294. The
picks beat SPY in 52.7% of cases against 44.3% for their peers and 38%
for all liquid rows.

## 3. The skill only just covers the structural gap

The buys' lead over SPY decomposes into two terms: how the picks' own
size band did against SPY, and how the picks did against that band.

| term | points a year |
|---|---|
| same-size peers against SPY (the band) | −3.80 |
| buys against same-size peers (the selection) | +4.46 |
| buys against SPY | +0.66 |

The same decomposition on the walk-forward screen, by cohort year
(picks' and peers' three-year CAGR minus SPY's over the same window):

| cohort | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY's 3y CAGR | .03 | −.09 | −.06 | .03 | .16 | .15 | .17 | .16 | .10 | .10 | .12 | .13 | .11 | .17 | .14 | .11 | .096 |
| picks minus SPY | −.02 | +.05 | +.05 | +.05 | +.06 | +.02 | −.02 | −.01 | +.01 | +.03 | −.03 | −.01 | −.01 | −.06 | −.07 | −.04 | .000 |
| peers minus SPY | −.02 | −.01 | .00 | .01 | .00 | −.02 | −.03 | −.03 | −.04 | −.04 | −.05 | −.04 | −.05 | −.06 | −.05 | −.04 | −.030 |
| all liquid rows minus SPY | −.06 | −.07 | −.06 | −.01 | −.01 | −.07 | −.08 | −.07 | −.11 | −.13 | −.12 | −.10 | −.16 | −.14 | −.13 | −.12 | −.090 |

The picks' mean three-year CAGR over the sixteen cohorts is 0.096. SPY's
is 0.096. The picks beat SPY in 7 cohorts of 16: by 3.3 points a year in
the four cohorts of 2005 to 2008, whose windows held the crash, and
behind by 1.1 points in the twelve cohorts of 2009 to 2020, in which
SPY compounded at 10% to 17% a year. The selection's lead over the band
is steady at 3 to 5 points; the band's gap to SPY grows from near zero
in 2005 to 2009 to 4 to 6 points from 2013 on.

## 4. In the 2019 to 2023 cohorts both terms failed

From the backtest's three-year reading by cohort year:

| cohort | buys minus SPY | band minus SPY | buys minus band | buys that lost | band that lost |
|---|---|---|---|---|---|
| 2017 | +2.2 | −7.4 | +9.5 | 19% | 40% |
| 2018 | +4.4 | −5.0 | +9.4 | 4% | 22% |
| 2019 | −4.8 | −5.1 | +0.3 | 13% | 24% |
| 2020 | −2.5 | −2.8 | +0.3 | 24% | 25% |
| 2021 | −13.5 | −11.0 | −2.5 | 47% | 45% |
| 2022 | −8.9 | −10.5 | +1.6 | 29% | 38% |
| 2023 (partial) | −18.1 | −12.1 | −6.0 | 40% | 33% |

Through 2018 the selection led its band by 9 points a year. From 2019
the lead is near zero or negative, and at the same time the band's gap
to SPY widens to 5 to 12 points. The 2021 buys are the worst cohort on
record: 72% had lost money after one year and 47% after three.

The model has no input that says what kind of year it is buying in.
Decision 46 found every forest's scores highest for entries at market
tops. In cell C the forest's precision was 0.40 in 2006 and 0.25 in
2007, when the base rate was 0.26 and 0.18. A row describes a company,
not the market.

## 5. Precision on "not a loser" compresses the return distribution

The label is met by 43% of liquid rows. The forest finds the calmest of
those, and calm cuts both tails. On the screen the picks' doublers
(three-year CAGR of 26% or more) were 5.2% against the peers' 13.6%,
while their losers were 16.7% against 30.0%. A portfolio of stocks that
each earn 8% to 10% with few losses keeps pace with an index earning
13% only when the index falls often enough to give the low-drawdown
portfolio its advantage. From 2005 to 2020 it did; since 2021 it has
not.

## 6. What was proposed and never run

The survey of the decision logs found three portfolio-level ideas that
address the structure directly and were never run as portfolios:

- A cap-weighted book of large caps with the forest's worst scores left
  out, "the index minus the predicted losers" (decision 32.3). The one
  cap-weighted run (decision 26) used a top 10 and became a bet on one
  company.
- Holding cash when little qualifies (decisions 13.2, 43.3). Decision 46
  stopped it before a backtest because a score threshold would buy most
  at tops. No backtest on record has ever held cash.
- A two-stage selection, a safety model first and a return model among
  the survivors (TODO). Gates exist only on the screen.

Also never run: a quarterly buying rhythm, selling at the label's
horizon, a top-20 book, and any beta or up-market/down-market study
before this note.

## 7. The reading, and the experiments

The project has not failed to find skill. It built a low-beta,
equal-weighted portfolio of calm, profitable, mostly large stocks with 4
to 5 points a year of real selection skill against same-size peers, and
asked it to beat a cap-weighted index. That works when the index falls
often and fails when a few giants carry it, and nothing in a row tells
the model which kind of period it is in.

Decision 81 orders six backtests that separate the explanations. E1 to
E4 put the forest's loser-avoidance inside the index's own structure: a
cap-weighted book of the top-decile large caps, with no selection (E1,
the control), with the safer half by the forest's score (E2), the safer
quarter (E3), and E2's names with equal weights (E4). E5 and E6 give the
candidate a reason to buy less when the market is dear: an absolute
earnings-yield floor of 5% and of 8% at the snapshot. The share of
liquid stocks clearing the 5% floor was 10% in 2021 and 17% in 2018,
against 35% to 48% in 2008 and 2009, so the floor acts as a valve on
buying without any market-state input. The predictions are in decision
81.4 and in each config.
