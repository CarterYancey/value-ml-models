# The "not a loser" forest with a second ranking

Detail behind the [logbook](../logbook.md) entry for the factor
combinations of 2026-09-29. Decision 8 of the
[decision log](2026-09-29-decisions.md); follows the
[capped backtests](2026-09-29-sector-cap-backtests.md).

**Simulated, cost-adjusted paper results, not live performance, and
not results of record.** `dataset_v1.4`, `prices_v1.0`, fold
definitions `split_folds.parquet` of `dataset_v1.4`. **Nine backtest
configurations have been tried on `dataset_v1.4`**, on the same
sixteen buy years; the three below are the seventh to ninth, and the
best of them is read with that in mind.

## What ran, and how it was checked

- Three single factors as fold bundles through `vml-run` (git
  `499884b`), each one more configuration in cell C (12 after them):
  `factor_earnings_yield_3y`, `factor_mom_12_2_3y`,
  `factor_roc_greenblatt_3y`. A rank factor fits nothing.
- Three backtests: cell C's forest (run `53ceedd93e6d`) and one
  factor, `combine = "mean_rank"`, the template of decision 6 with a
  cap of 2 per sector. The factors were named in the decision log
  before any was run in a backtest.
- Mean rank: each model's scores are ranked within the month's
  investable cross-section and the two ranks averaged. A stock with
  no value for the factor is ranked on the forest alone (the mean
  skips the missing rank); not checked how many picks that concerns.

The factors alone, on the screen (top 20 per year, cell C's label):

| factor | p@20 | picks beat SPY | median excess | losers | big losers | big winners | median drawdown |
|---|---|---|---|---|---|---|---|
| earnings yield | 0.16 | 0.22 | −0.22 | 0.63 | 0.52 | 0.12 | 0.59 |
| 12-month momentum | 0.17 | 0.21 | −0.28 | 0.68 | 0.57 | 0.13 | 0.70 |
| return on capital | 0.45 | 0.38 | −0.05 | 0.41 | 0.31 | 0.19 | 0.37 |
| cell C's forest | 0.79 | 0.46 | +0.00 | 0.13 | 0.06 | 0.03 | 0.13 |
| all test rows | 0.39 | 0.36 | −0.07 | 0.45 | 0.32 | 0.15 | 0.39 |

## Results

Deposits 192,000 in each leg, buys 2005–2020, valued 2023-12-29,
cap 2 per sector.

| portfolio | final value | money-weighted | time-weighted CAGR | worst drawdown | years ahead of SPY | distinct stocks bought | delisting liquidations |
|---|---|---|---|---|---|---|---|
| forest alone | 633,757 | 10.40% | 9.74% | −46.1% | 10 of 19 | 178 | 52 |
| forest + value | 493,413 | 8.28% | 7.76% | −49.4% | 7 | | 68 |
| **forest + momentum** | **711,494** | **11.38%** | **11.07%** | **−47.8%** | 11 | 384 | 134 |
| forest + quality | 694,945 | 11.18% | 9.65% | −41.2% | 8 | 94 | 26 |
| SPY, same deposits | 732,110 | 11.62% | 9.58% | −52.9% | | | |

Excess over SPY by year, points, time-weighted:

| year | SPY | forest alone | + value | + momentum | + quality |
|---|---|---|---|---|---|
| 2005 | 6.5% | +3.8 | +5.1 | +8.8 | −4.2 |
| 2006 | 12.7% | +3.9 | −2.3 | +8.1 | −1.2 |
| 2007 | 7.3% | −11.8 | −11.2 | −0.3 | −4.4 |
| 2008 | −43.2% | +13.4 | +8.0 | +2.6 | +11.6 |
| 2009 | 39.1% | −8.3 | −4.6 | +8.4 | −3.8 |
| 2010 | 10.9% | +16.1 | +16.1 | +16.8 | +4.1 |
| 2011 | 5.3% | +8.3 | +3.1 | +6.5 | +3.3 |
| 2012 | 15.6% | +1.3 | −0.2 | −6.2 | −4.8 |
| 2013 | 30.4% | −12.9 | −7.8 | +0.3 | −1.9 |
| 2014 | 16.2% | +4.3 | +3.9 | −1.5 | +3.2 |
| 2015 | 4.5% | −0.3 | −5.1 | −3.3 | +6.3 |
| 2016 | 6.5% | +4.5 | +4.7 | +3.2 | +2.4 |
| 2017 | 22.9% | −3.5 | −6.5 | −4.5 | −3.3 |
| 2018 | 7.5% | −1.6 | −5.2 | +2.0 | −1.3 |
| 2019 | 13.8% | +2.6 | −1.1 | +1.8 | +3.7 |
| 2020 | 19.8% | −16.3 | −27.2 | −7.9 | −8.9 |
| 2021 | 24.8% | −9.4 | −8.7 | −4.8 | −11.4 |
| 2022 | −8.2% | +12.4 | +14.2 | +13.4 | +14.1 |
| 2023 | 19.0% | −16.6 | −17.4 | −16.8 | −14.8 |
| sum 2005–12 | | +26.6 | +13.9 | +44.8 | +0.6 |
| sum 2013–20 | | −23.1 | −44.4 | −9.8 | +0.1 |

Sectors bought: with momentum, eleven sectors between 1% and 14%
(consumer defensive 14%, consumer cyclical 13%, industrials 12%,
real estate 11%, utilities and healthcare 10% each). With quality,
consumer defensive 22%, industrials 18%, technology 18%, healthcare
16%, and under 1% utilities and real estate together. With value,
real estate 18%, utilities 16%, energy 13%.

## Against what decision 8 said would count, and the predictions

What would count: the drawdown within 5 points of −46% and a
time-weighted CAGR of 10.7% or more, the gain not confined to
2005–12.

| | measured | |
|---|---|---|
| forest + momentum | −47.8%; 11.07%; against the forest alone it gains 18.2 points of yearly excess over 2005–12 and 13.2 over 2013–20 | **meets all three** |
| forest + quality | −41.2%; 9.65% | drawdown yes, return no |
| forest + value | −49.4%; 7.76% | return no |

| prediction | measured | matched? |
|---|---|---|
| value: a deeper drawdown and no higher return | −49.4% against −46.1%; 7.76% against 9.74% | yes |
| momentum: a higher return in 2013–20 and a deeper fall in 2008 | yearly excess over 2013–20 −9.8 against −23.1; 2008 −40.6% against −29.8% | yes |
| quality: return within a point a year of the forest alone, drawdown within 3 points | 9.65% against 9.74%; −41.2% against −46.1% | return yes; drawdown **no**, 4.9 points shallower |

## Measured

1. **With momentum the portfolio compounds 1.5 points a year faster
   than SPY** (11.07% against 9.58%) with a worst drawdown 5 points
   shallower, and ends 3% below SPY in money (711,494 against
   732,110). Against the forest alone: 1.3 points a year more, a
   drawdown 1.7 points deeper.
2. **Most of what momentum added is in four years:** 2007 (+11.4
   points against the forest alone), 2009 (+16.7), 2013 (+13.2) and
   2020 (+8.3). It took 10.7 points away in 2008 and 7.5 in 2012.
3. **Momentum alone is the worst factor on the screen** (losers
   0.68, median drawdown 0.70). What helps is momentum *among the
   stocks the forest ranks as safe*, not momentum.
4. **Cheapness among calm stocks made the portfolio worse,** in
   return and in drawdown, and worst where it matters most to the
   money-weighted figure (2020: 27 points behind SPY).
5. **Quality gives the shallowest drawdown of any portfolio so far
   (−41%)** at the forest's rate of return, and a different
   portfolio: technology and healthcare in place of utilities and
   real estate, 94 distinct stocks in sixteen years against 178. Its
   money-weighted return (11.2%) is above its time-weighted one
   (9.65%) because its better years came late.
6. **No portfolio kept up with SPY in 2021 and 2023** (5 to 17
   points behind), and every one was 12 to 14 points ahead in 2022.
7. **With momentum, 134 positions ended in a delisting**, against
   52 for the forest alone: 384 distinct stocks were bought. Calm
   stocks with a high twelve-month return include companies under a
   takeover offer, which trade flat near the offer price until they
   delist. Not checked stock by stock.

## Caveats

- Best of three, ninth of nine, one path. The criterion was fixed
  before the runs and met by one candidate; that protects against
  moving the goalposts, not against the sixteen years being the
  only sixteen years there are.
- The forest is one seed. Decision 9 repeats the forest alone and
  the forest with momentum on the sweep's other two seeds.
- Whole shares at 100 a pick: 84 (momentum) and 108 (quality) of 192
  months bought fewer than 10 stocks. The quality portfolio paid
  1,045 in costs against 1,443–1,592 for the others, so it bought
  less; how much of its low drawdown is unspent cash has not been
  separated (mean cash share of the portfolio is 1% in every run,
  which says little).
- 2021–23 is outcome of buys made through 2020, and overlaps the
  holdout era: context.

## The seed check (decision 9, added later on 2026-09-29)

Cell C's forest with seeds 232 and 1776 (runs `de629f13deec` and
`003a8739d3d5`; p@20 0.778 and 0.781, the sweep's values for those
seeds; fold-mean PR-AUC 0.585 on all three), and the two backtests
repeated with each. Thirteen backtest configurations tried in all.

| portfolio | seed | final value | money-weighted | time-weighted CAGR | worst drawdown |
|---|---|---|---|---|---|
| forest alone, cap 2 | 23 | 633,757 | 10.40% | 9.74% | −46.1% |
| | 232 | 630,423 | 10.36% | 9.35% | −47.1% |
| | 1776 | 661,485 | 10.76% | 9.90% | −44.2% |
| forest + momentum, cap 2 | 23 | 711,494 | 11.38% | 11.07% | −47.8% |
| | 232 | 764,062 | 11.98% | 11.73% | −46.7% |
| | 1776 | 717,485 | 11.45% | 11.11% | −48.5% |
| SPY, same deposits | | 732,110 | 11.62% | 9.58% | −52.9% |

Lead of the momentum portfolio over the forest alone, time-weighted:
1.33, 2.38 and 1.21 points a year. Predicted: within 0.7 points and
3 points of drawdown of seed 23, and a lead of 0.5 or more on both
new seeds. All held (the largest difference from seed 23 is 0.66
points, momentum, seed 232).

The years agree across seeds to within 3 points for the momentum
portfolio (2005 and 2006 excepted: +8.8 / +13.3 / +10.7 and +8.1 /
+7.2 / +6.1 over SPY). On all three seeds it is ahead of SPY in
2005–11 except 2007 (level), behind in 2012, 2017, 2020, 2021 and
2023, and 13–17 points ahead in 2022.

**Measured:** the forest's seed moves a backtest by about half a
point a year and 2–3 points of drawdown. The momentum portfolio's
lead over the forest alone is larger than that on every seed, and
its lead over SPY (1.5 to 2.2 points a year, time-weighted) is three
times the seed spread. In money it ends between 3% below SPY and 4%
above.

**What this does not show:** that the lead holds outside 2005–2023.
The seeds share the data, the years, the template and the choice of
momentum, which was the best of three.
