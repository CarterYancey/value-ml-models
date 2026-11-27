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

## 8. The first round of backtests (E1 to E6)

All six ran on `dataset_v1.4.1` with the candidate's costs, window and
accounting. The candidate's own record is the first row.

| portfolio | final value on 260,000 | SPY | ratio | money-weighted CAGR | TWR | TWR 2005 to 2020 (SPY 9.4%) | TWR 2021 to 2026 (SPY 15.3%) | beta | worst drawdown | buys that lost over 3 years | buys' lead over same-size peers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| the candidate | 1,159,740 | 1,326,084 | 0.875 | 12.20% | 10.99% | 12.4% | 7.1% | 0.86 | −41.0% | 23.4% | +4.5 |
| E1: large caps, cap-weighted, no selection | 1,421,189 | 1,326,614 | 1.071 | 13.72% | 11.87% | 10.5% | 15.6% | 0.93 | −45.9% | 29.9% | 0.0 |
| E2: E1 minus all but the forest's top 50 | 892,693 | 1,326,614 | 0.673 | 10.22% | 9.25% | 8.7% | 10.6% | 0.73 | −45.0% | 19.9% | +0.4 |
| E3: the forest's top 25 | 811,528 | 1,326,614 | 0.612 | 9.48% | 7.41% | 6.2% | 10.7% | 0.84 | −59.8% | 20.2% | 0.0 |
| E4: E2's names, equal weights | 859,492 | 1,326,614 | 0.648 | 9.93% | 9.57% | 10.2% | 7.7% | 0.73 | −44.1% | 19.9% | +0.4 |
| E5: the candidate, earnings yield ≥ 5% | 1,154,700 | 1,326,084 | 0.871 | 12.17% | 11.16% | 11.6% | 9.8% | 0.84 | −39.9% | 24.5% | +2.8 |
| E6: the candidate, earnings yield ≥ 8% | 1,068,807 | 1,326,084 | 0.806 | 11.59% | 11.81% | 11.5% | 12.6% | 0.96 | −46.9% | 26.9% | +4.6 |

Two things about the design came out in the reading. First, the
large-cap universe was mis-sized. Decision 81 counted it from January
snapshots alone, about 100 names, but the backtest's monthly
cross-section holds every stock with a snapshot inside 200 days, about
450 names in the top decile (E1 made 4,400 to 5,400 buys a year). So E2
kept the top 11% of the large caps, not half, and E3 the top 5%. Second,
E2 and E3 used the forest alone, and the forest alone prefers defensive
sectors: E2's buys were 24% consumer staples, 23% utilities and 8% real
estate, where E1's largest sectors were consumer cyclicals, technology,
energy and healthcare at 14% to 16% each. In the candidate, the
return-on-capital leg removes that tilt. Decision 81.6 ordered a second
round with the cut at a quarter and a half of the universe, with and
without the blend.

Third, the valuation floors did not hold cash. The candidate buys ten
stocks a month from about 1,100 liquid names, and at least 10% of them
cleared the 5% floor in every year, so E5 and E6 always found ten. The
floors changed which stocks were bought, not how many. (A separate
check: the candidate's own buys fell from 120 a year to 51 to 85 in 2021
to 2026, because whole shares of expensive stocks do not fit a $100
slot. A fractional-share run on the earlier build ended within 2% of
the whole-share run, so this is not where the shortfall is.)

What the buys of 2017 to 2023 went on to do over three years (return
minus SPY's, in points a year; and the share that lost money):

| cohort | candidate | E1 | E2 | E5 | E6 |
|---|---|---|---|---|---|
| 2017 | +2.2 (19%) | −4.3 (31%) | −2.3 (21%) | −4.1 (36%) | −11.3 (47%) |
| 2018 | +4.4 (4%) | −3.6 (18%) | −3.9 (5%) | +0.1 (10%) | −5.8 (16%) |
| 2019 | −4.8 (13%) | −2.9 (18%) | −5.8 (12%) | −0.1 (9%) | −5.8 (21%) |
| 2020 | −2.5 (24%) | −2.6 (24%) | −5.6 (24%) | −6.3 (28%) | −1.3 (27%) |
| 2021 | −13.5 (47%) | −7.6 (39%) | −3.7 (23%) | −7.0 (48%) | −9.1 (43%) |
| 2022 | −8.9 (29%) | −8.7 (35%) | −11.0 (30%) | −7.3 (29%) | −2.4 (24%) |
| 2023 (partial) | −18.1 (40%) | −10.3 (29%) | −14.0 (24%) | −9.2 (23%) | +0.2 (10%) |

### What the first round showed, against the predictions of 81.4

- **(a) held, and then some.** The cap-weighted large-cap book with no
  model (E1) did not merely track SPY. It beat it: 7% more money, a
  time-weighted return 0.9 points a year higher, 1.1 points higher in
  2005 to 2020 and 0.3 higher in 2021 to 2026, with a drawdown 7 points
  shallower. The structure explains the candidate's recent shortfall in
  full: a cap-weighted book of this dataset's large caps kept pace with
  SPY in 2021 to 2026 (15.6% against 15.3%), where the equal-weighted
  candidate earned 7.1%.
- **(b) failed, in the direction opposite to the hope.** Keeping only
  the forest's favourites inside that book cost 2.6 points a year
  against E1 and 1.7 against SPY, in both periods, with the same
  drawdown. The forest's picks did lose less often (20% of buys against
  30%) and led same-size peers by 0.4 points, but the stocks it left
  out, the volatile large growth names, earned far more than the calm
  defensives it kept. Among large caps, "will not lose money" selects
  the low-return half. The design was also mis-sized and confounded by
  the forest's sector taste; the second round separates those.
- **(c) held.** The top 25 was worse than the top 50 by 1.8 points a
  year and its drawdown was 15 points deeper. Concentration added
  variance and lost return.
- **(d) held.** Equal-weighting E2's names cost 2.9 points a year in
  2021 to 2026 (7.7% against 10.6%) and gained 1.5 in 2005 to 2020. The
  weighting is where the recent gap comes from; the selection is where
  the earlier edge came from.
- **(e) failed on its mechanism and was a draw on its outcome.** The 5%
  floor bought slightly more stocks, not fewer, and held no cash, so it
  did not act as a valve. It did change the picks: the 2021 to 2026
  return rose by 2.7 points a year (9.8% against 7.1%), the drawdown was
  a point shallower, and the 2005 to 2020 return fell 0.8 points. The
  final value is the candidate's to within 0.4%. The buys' lead over
  same-size peers fell from 4.5 to 2.8 points, which is the rival's
  value-trap effect, offset by a better 2021 to 2026. Not a candidate.
- **(f) failed as a prediction and is the most interesting of the six.**
  The 8% floor did not sit in cash either. It earned 12.6% a year in
  2021 to 2026 against the candidate's 7.1%, and 11.5% against 12.4% in
  2005 to 2020. Its buys of 2022 and 2023 lost money 24% and 10% of the
  time, the lowest of any portfolio here. Its final value is 8% below
  the candidate's because its drawdown was 6 points deeper and its path
  through 2008 to 2012 was worse. Its beta is 0.96, so the floor
  replaced calm with cheap. This is one run, on one build, and the rule
  of 81.2 is not met (final value below SPY). It says that a valuation
  floor inside the forest's safe set is a direction, not a result.
- **(g) held: no arm of the six passes the rule of 81.2.** E1 passes it
  without a model, which is the point. The structure can be fixed. What
  the forest adds inside the fixed structure is the second round's
  question.

## 9. The second round: the cut at a quarter and a half, with and without the blend (E7 to E10)

The first round's cut was mis-sized (section 8). These four runs leave
out the worst quarter and the worst half of the roughly 450 large caps
in the monthly cross-section, scored by the forest alone (E7, E8) and by
the candidate's three-leg blend of forest, momentum and return on
capital (E9), and repeat E2's top 50 with the blend (E10). All are
cap-weighted books of the top-decile large caps, like E1.

| portfolio | final value | ratio to SPY | TWR | TWR 2005 to 2020 (SPY 9.4%) | TWR 2021 to 2026 (SPY 15.3%) | beta | worst drawdown | buys that lost | buys' lead over same-size peers |
|---|---|---|---|---|---|---|---|---|---|
| E1: all large caps, cap-weighted | 1,421,189 | 1.071 | 11.87% | 10.5% | 15.6% | 0.93 | −45.9% | 29.9% | 0.0 |
| E7: minus the forest's worst quarter | 1,289,146 | 0.972 | 11.32% | 10.2% | 14.4% | 0.88 | −44.3% | 27.1% | +0.5 |
| E8: minus the forest's worst half | 1,212,377 | 0.914 | 11.12% | 10.4% | 13.1% | 0.81 | −41.9% | 23.2% | +1.3 |
| E9: minus the blend's worst half | 1,325,097 | 0.999 | 11.59% | 10.7% | 13.9% | 0.86 | −42.5% | 24.4% | +1.3 |
| E10: the blend's top 50 | 1,255,864 | 0.947 | 11.88% | 11.6% | 12.7% | 0.79 | −37.4% | 19.9% | +2.6 |
| E2: the forest's top 50 (first round) | 892,693 | 0.673 | 9.25% | 8.7% | 10.6% | 0.62 | −45.0% | 19.9% | +0.4 |
| SPY | 1,326,614 | 1.000 | 10.94% | 9.4% | 15.3% | 1.00 | −52.9% | | |

The betas are the mean of the two periods' monthly betas. The sector
mix: E1's largest sectors were technology 17%, industrials 14%,
healthcare 13% and consumer cyclicals 12%; E9's were industrials 18%,
technology 15%, healthcare 14% and consumer staples 13%; E10's were
staples 23%, industrials 23%, technology 16% and healthcare 15%; E2's
were staples 24% and utilities 23%.

The recent cohorts, over three years (return minus SPY's in points a
year, and the share of buys that lost money):

| cohort | E1 | E7 | E8 | E9 | E10 |
|---|---|---|---|---|---|
| 2021 | −7.6 (39%) | −4.9 (33%) | −4.6 (31%) | −5.2 (32%) | −4.5 (29%) |
| 2022 | −8.7 (35%) | −8.3 (32%) | −9.0 (31%) | −8.4 (31%) | −7.9 (31%) |
| 2023 (partial) | −10.3 (29%) | −10.2 (26%) | −11.5 (25%) | −10.1 (24%) | −12.3 (27%) |
| all buys | −2.6 (30%) | −2.1 (27%) | −1.3 (23%) | −1.3 (24%) | +0.1 (20%) |

### What the second round showed, against the predictions of 81.6

- **(h) missed its bound narrowly, and its rival failed.** Leaving out
  the forest's worst quarter cost 0.55 points a year against E1, just
  outside the predicted 0.5, with a drawdown 1.6 points shallower and
  2.8 points fewer losing buys, inside the predicted 2 to 4. The
  stocks the forest scores lowest among large caps include enough
  winners that removing them costs more than the losers they carry.
- **(i) held.** The worst half cost 0.75 points a year, inside the
  predicted 0 to 1, at a beta of 0.81 between E1's and E2's.
- **(j) held, and its rival failed.** The blend's worst half cost 0.28
  points a year against E1, inside 0.5, and recovered 0.47 of E8's
  loss, so the return-on-capital leg does remove the forest's sector
  tilt inside a cap-weighted book, as it does in the candidate. E9
  ended with SPY's final value to within 0.1%, 7% behind E1. It was not
  ahead of E1 in both periods: 0.2 ahead in 2005 to 2020 and 1.7 behind
  in 2021 to 2026.
- **(k) held.** With the blend, the top 50 earned 2.6 points a year more
  than the forest's top 50 and matched E1's time-weighted return
  exactly: 11.6% against 10.5% in 2005 to 2020, 12.7% against 15.6% in
  2021 to 2026. It ended with 12% less money than E1 because its
  shortfall fell in the years the account was largest, and 5% less than
  SPY. Its drawdown was −37.4% against SPY's −52.9%, its beta 0.79, and
  one buy in five lost money against one in three for E1.
- **The shape of the result.** Inside the index's own structure, every
  cut by the model trades return in 2021 to 2026 for fewer losers and a
  shallower drawdown, and the deeper the cut the larger both sides of
  the trade. The forest alone pays more for the same safety than the
  blend, because it buys defensives. Over 2005 to 2020 the blend's top
  50 beat E1 by 1.1 points a year and SPY by 2.2 with 15 points less
  drawdown, which is the thesis working for sixteen years in the
  cap-weighted structure; in 2021 to 2026 the same book trailed by 2.6
  to 2.9 points because the stocks it leaves out, the volatile large
  growth names, were the ones that carried the index.
- No arm with a model passes the rule of 81.2. E1, with no model,
  passes it.

## 10. The third round: the blend's top 100, and the top 50 with a valuation floor (E11, E12)

| portfolio | final value | ratio to SPY | money-weighted CAGR | TWR | TWR 2005 to 2020 (SPY 9.4%) | TWR 2021 to 2026 (SPY 15.3%) | beta | worst drawdown | buys that lost | buys' lead over same-size peers |
|---|---|---|---|---|---|---|---|---|---|---|
| E10: the blend's top 50, cap-weighted | 1,255,864 | 0.947 | 12.80% | 11.88% | 11.6% | 12.7% | 0.79 | −37.4% | 19.9% | +2.6 |
| E12: the blend's top 100 | 1,227,896 | 0.926 | 12.63% | 11.54% | 11.2% | 12.5% | 0.80 | −39.1% | 21.1% | +2.2 |
| E11: the blend's top 50 among stocks with an earnings yield of 5% or more | 1,274,597 | 0.961 | 12.91% | 12.08% | 11.3% | 14.3% | 0.77 | −36.7% | 21.1% | +1.6 |
| SPY | 1,326,614 | 1.000 | 13.20% | 10.94% | 9.4% | 15.3% | 1.00 | −52.9% | | |

E11's largest sectors were industrials 20%, consumer staples 18%,
healthcare 12% and technology 12%. Its buys of 2021, 2022 and 2023
trailed SPY over three years by 4.7, 11.6 and 9.7 points a year and
lost money 32%, 35% and 22% of the time (E10: 4.5, 7.9 and 12.3 points;
29%, 31% and 27%).

### What the third round showed, against the predictions of 81.7

- **(l) held on return and failed on drawdown, and its rival failed.**
  The valuation floor raised the 2021 to 2026 return by 1.6 points a
  year (14.3% against 12.7%), cost 0.3 points in 2005 to 2020, and made
  the drawdown shallower rather than deeper (−36.7% against −37.4%). The
  final value is 1.5% above E10's. The floor did not remove the names
  that keep pace with SPY; it removed the dear ones among the safe ones,
  and that was where the recent shortfall sat.
- **(m) failed.** The top 100 was below both the top 50 and the top 225
  on final value and return. The depth of the cut is not a smooth
  lever; one run per depth cannot tell order from noise, and the three
  depths sit within 0.35 points a year of one another.
- **E11 is the closest any portfolio has come to the goal.** Over the
  whole window its time-weighted return is 12.08% a year against SPY's
  10.94%, its worst drawdown −36.7% against −52.9%, its beta 0.77, and
  one buy in five lost money against one in three in the cap-weighted
  book without a model. In 2021 to 2026 it trailed SPY by 1.0 point a
  year, against the candidate's 8.2. It ends with 3.9% less money than
  SPY because the deposits make the account largest in the years it
  trailed. Under the rule of 81.2 it passes the 2021 to 2026 clause and
  the drawdown clause and fails the final-value clause. It is one run,
  at one seed, chosen after E6 and E10 had been read, so its number is
  selection-biased, and it goes to three seeds before anything else is
  said about it.

## 11. The answer

**Why the candidate has not beaten the market.** Four reasons, each
measured above, in the order of their weight.

1. **Its structure cannot keep pace with a cap-weighted index when a
   few giants carry it.** A cap-weighted book of this dataset's
   top-decile large caps with no model at all (E1) ended with 7% more
   money than SPY, a drawdown 7 points shallower, and 15.6% a year in
   2021 to 2026 against SPY's 15.3%. The candidate's equal-weighted,
   size-broad book earned 7.1% in those years. The structure, not the
   model, is the first four points of the recent gap.
2. **Its skill is loser-avoidance, and loser-avoidance leaves out the
   volatile winners.** The buys lose money a third less often than their
   peers, and inside the cap-weighted book every cut by the model lowers
   the 2021 to 2026 return while it lowers the drawdown and the losers,
   the deeper the cut the more of both. The stocks the model scores
   lowest among large caps are the ones that carried the index.
3. **It has no input about the market's level.** Its scores are highest
   at tops (decision 46), and its 2021 buys lost money 47% of the time
   over three years. A row describes a company, not the market. An
   absolute earnings-yield floor, a row-level stand-in for "the market
   is dear", recovered 1.6 of the 2.6 points E10 lacked in 2021 to 2026.
4. **The deposits weight the end of the window.** The candidate beat SPY
   by 3 points a year for sixteen years and trailed by 8 for six; the
   money-weighted CAGR counts the six most, because that is when the
   account was largest.

**What the thesis looks like after this.** High precision on a modest
target did beat the market by avoiding losers, for sixteen years that
held two crashes: the candidate by 3 points a year, the cap-weighted
blend's top 50 (E10) by 2.2 points a year with 15 points less drawdown.
It did not beat the market in a six-year stretch in which the index was
carried by the stocks a loser-avoiding model declines to hold. Whether
that stretch is the exception Carter's working assumption says it is
(decision 36) or the new normal, the data cannot say. What the data do
say is that the trade on offer is return in that kind of stretch
against drawdown and losers in every other, and that the terms of the
trade improve when the book is cap-weighted, when the blend rather than
the forest alone makes the cut, and when a valuation floor keeps the
dear names out.

**What to try next, in order.**

1. E11 at the forest's other two seeds (232 and 1776), and E11 with the
   candidate's rank sell discipline, which added 12% of final value to
   the candidate. If the seeds hold within half a point and the sell
   discipline adds what it did before, E11 with the sell discipline
   passes the rule of 81.2 on all three clauses. These are four
   backtests.
2. Carter's decision on the objective. By final money against SPY on
   2026-08-21, inside a mega-cap boom, no loser-avoiding book in this
   program wins, and E11 comes within 4%. By drawdown, losers and
   return per unit of market risk, E11 wins on every reading. The
   program needs to know which of these is the goal, and over what kind
   of period the goal is judged.
3. The upstream market-state columns (the trailing return, volatility
   and drawdown of the market; the cross-sectional median earnings yield
   and book to market; breadth; spreads). The earnings-yield floor is a
   stand-in for them, and it worked; the real columns would let the
   model learn when to buy less rather than have the rule imposed.
4. Not to pursue: deeper cuts (E3), the forest alone in a cap-weighted
   book (E2, E7, E8), fundamentals-only feature sets (decisions 78 to
   80), and threshold-based cash rules on the model's own scores
   (decision 46).
