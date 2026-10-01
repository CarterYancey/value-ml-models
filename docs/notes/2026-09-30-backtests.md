# Backtests of 2026-09-30: the quality blend, the three-way blend, a sell discipline

Detail behind the [logbook](../logbook.md) entry of 2026-09-30 for the
backtests. Decisions 21, 23 and 24 of the
[decision log](2026-09-29-decisions.md); follows
[blends and calibration](2026-09-30-blends-and-calibration.md).

**Simulated, cost-adjusted paper results, not live performance, and
not results of record.** `dataset_v1.4`, `prices_v1.0`, fold
definitions `split_folds.parquet` of `dataset_v1.4`. **Twenty-six
backtest configurations have been tried on `dataset_v1.4`**, all on
the same sixteen buy years; thirteen before this session, thirteen in
it. The best of them is read with that in mind.

## The template, and what is judged

Decision 6's template with decision 7's cap: top 10 of the month's
cross-section by combined rank, at most 2 per sector, equal weights,
1,000 deposited a month, 35 bps a side, `dollar_volume_3m >= 100000`,
buys 2005–2020, valued 2023-12-29, whole shares, SPY with the same
deposits. Combination: `mean_rank` of cell C's forest
(`forest_nonloser_dd30_3y`, seeds 23 / 232 / 1776) and the single
factors named in decision 8.

Four criteria, fixed in decision 21 before the new runs: final value
at or above SPY's 732,110; time-weighted CAGR of 10.6% or more (SPY's
9.58% plus a point); worst drawdown at least 5 points shallower than
SPY's −52.9%; a positive mean 3-year excess per buy for the buys of
2005–12 and of 2013–20.

"Per buy" is the table every backtest report now carries
(`claude/backtest-buy-outcomes`): each buy's annualized return over
the three years after its trade date minus SPY's over the same dates,
from the price panel; a stock that stops printing exits at its final
print and the proceeds ride SPY to the horizon; one buy, one vote, no
costs.

## What ran, and how it was checked

- 21 backtests in three chains at git `e2c2e4a`, `c3ff72f`,
  `ba55f7d` and `0b8c053` (the later commits add configs and notes,
  no code). 8 are
  re-runs of earlier configurations for the per-buy table: same
  config hashes, no new configuration, and every headline figure
  reproduced to the cent (forest alone 633,757; with momentum
  711,494; with return on capital 694,945; with earnings yield
  493,413).
- 13 new configurations, each with its prediction in its config.
- The per-buy figures of the four re-runs equal the scratch analysis
  that first computed them (+0.0013, +0.0051, +0.0126, −0.0317).

## Results

| portfolio | seed | final value | time-weighted | money-weighted | worst drawdown | costs | per buy 3y | buys 2005–12 | buys 2013–20 | beat SPY | lost money | criteria |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY, same deposits | | 732,110 | 9.58% | 11.62% | −52.9% | | | | | | | |
| forest alone | 23 | 633,757 | 9.74% | 10.40% | −46.1% | 1,443 | +0.001 | +0.013 | −0.011 | 0.51 | 0.17 | 1 of 4 |
| | 232 | 630,423 | 9.35% | 10.36% | −47.1% | 1,463 | +0.005 | +0.016 | −0.007 | 0.52 | 0.17 | |
| | 1776 | 661,485 | 9.90% | 10.76% | −44.2% | 1,539 | +0.007 | +0.021 | −0.008 | 0.53 | 0.16 | |
| + momentum (decision 10's candidate) | 23 | 711,494 | 11.07% | 11.38% | −47.8% | 1,592 | +0.005 | +0.025 | −0.016 | 0.55 | 0.24 | 2 of 4 |
| | 232 | 764,062 | 11.73% | 11.98% | −46.7% | 1,585 | +0.005 | +0.028 | −0.019 | 0.55 | 0.25 | |
| | 1776 | 717,485 | 11.11% | 11.45% | −48.5% | 1,641 | +0.001 | +0.024 | −0.023 | 0.53 | 0.25 | |
| + return on capital | 23 | 694,945 | 9.65% | 11.18% | −41.2% | 1,045 | +0.013 | +0.013 | +0.012 | 0.57 | 0.18 | 2 of 4 |
| | 232 | 752,267 | 10.18% | 11.85% | −42.4% | 1,105 | +0.019 | +0.023 | +0.014 | 0.59 | 0.16 | 3 of 4 |
| | 1776 | 721,826 | 10.04% | 11.50% | −41.3% | 1,126 | +0.012 | +0.018 | +0.005 | 0.58 | 0.19 | 2 of 4 |
| + earnings yield | 23 | 493,413 | 7.76% | 8.28% | −49.4% | 1,591 | −0.032 | −0.007 | −0.057 | 0.42 | 0.30 | 0 |
| + return on capital, sell discipline | 23 | 800,456 | 10.64% | 12.37% | −38.8% | 2,210 | +0.013 | +0.014 | +0.012 | 0.57 | 0.18 | **4** |
| | 232 | 852,325 | 11.09% | 12.90% | −39.7% | 2,247 | +0.019 | +0.023 | +0.014 | 0.59 | 0.16 | **4** |
| | 1776 | 803,800 | 10.79% | 12.40% | −39.4% | 2,243 | +0.012 | +0.018 | +0.005 | 0.58 | 0.19 | **4** |
| + momentum, sell discipline | 23 | 674,817 | 9.87% | 10.93% | −51.7% | 13,541 | +0.004 | +0.024 | −0.017 | 0.55 | 0.24 | 0 |
| **+ momentum + return on capital** | 23 | 948,956 | 12.24% | 13.79% | −41.2% | 1,206 | +0.025 | +0.034 | +0.016 | 0.61 | 0.20 | **4** |
| | 232 | 959,660 | 12.26% | 13.89% | −41.3% | 1,228 | +0.026 | +0.034 | +0.016 | 0.61 | 0.21 | **4** |
| | 1776 | 949,366 | 12.23% | 13.80% | −42.0% | 1,171 | +0.024 | +0.035 | +0.013 | 0.61 | 0.21 | **4** |
| the same, fractional shares | 23 | 936,540 | 12.12% | 13.68% | −43.0% | 1,199 | +0.021 | +0.031 | +0.011 | 0.60 | 0.20 | **4** |
| the same, sell discipline | 23 | 1,090,591 | 13.14% | 14.96% | −39.5% | 5,007 | +0.024 | +0.034 | +0.013 | 0.61 | 0.20 | **4** |
| | 232 | 1,042,252 | 12.70% | 14.58% | −40.2% | 5,062 | +0.024 | +0.034 | +0.014 | 0.61 | 0.21 | **4** |
| | 1776 | 1,028,085 | 12.66% | 14.46% | −40.5% | 4,899 | +0.024 | +0.035 | +0.012 | 0.61 | 0.21 | **4** |

"Beat SPY" and "lost money" are shares of the buys over the three
years after the trade. Sell discipline: a holding is sold once it is
outside the top 20% of the month's candidates by combined rank, or is
not a candidate (`[sell] max_rank_pct = 0.2`).

Excess over SPY by year, points, time-weighted, seed 23:

| year | SPY | forest alone | + momentum | + return on capital | three-way | three-way, sell | quality, sell |
|---|---|---|---|---|---|---|---|
| 2005 | 6.5% | +3.8 | +8.8 | −4.2 | +1.3 | +1.1 | −4.0 |
| 2006 | 12.7% | +3.9 | +8.1 | −1.2 | −2.9 | −2.6 | −3.1 |
| 2007 | 7.3% | −11.8 | −0.3 | −4.4 | −3.8 | −4.5 | +0.2 |
| 2008 | −43.2% | +13.4 | +2.6 | +11.6 | +9.5 | +10.1 | +10.8 |
| 2009 | 39.1% | −8.3 | +8.4 | −3.8 | +3.3 | +2.2 | −0.9 |
| 2010 | 10.9% | +16.1 | +16.8 | +4.1 | +16.8 | +15.7 | +2.9 |
| 2011 | 5.3% | +8.3 | +6.5 | +3.3 | +6.0 | +11.5 | +3.1 |
| 2012 | 15.6% | +1.3 | −6.2 | −4.8 | −0.2 | −0.0 | −3.4 |
| 2013 | 30.4% | −12.9 | +0.3 | −1.9 | +5.7 | −6.7 | −3.0 |
| 2014 | 16.2% | +4.3 | −1.5 | +3.2 | −3.5 | +3.3 | +0.4 |
| 2015 | 4.5% | −0.3 | −3.3 | +6.3 | +8.0 | +12.6 | +13.7 |
| 2016 | 6.5% | +4.5 | +3.2 | +2.4 | −1.8 | +0.2 | +1.7 |
| 2017 | 22.9% | −3.5 | −4.5 | −3.3 | +0.0 | +1.0 | −3.2 |
| 2018 | 7.5% | −1.6 | +2.0 | −1.3 | +1.5 | +8.6 | +3.7 |
| 2019 | 13.8% | +2.6 | +1.8 | +3.7 | +9.4 | +12.9 | +8.3 |
| 2020 | 19.8% | −16.3 | −7.9 | −8.9 | +2.1 | +0.2 | −6.1 |
| 2021 | 24.8% | −9.4 | −4.8 | −11.4 | −9.5 | −8.2 | −16.1 |
| 2022 | −8.2% | +12.4 | +13.4 | +14.1 | +4.6 | +6.8 | +17.3 |
| 2023 | 19.0% | −16.6 | −16.8 | −14.8 | −2.0 | −4.9 | −14.0 |
| sum 2005–12 | | +26.6 | +44.8 | +0.6 | +29.9 | +33.4 | +5.6 |
| sum 2013–20 | | −23.0 | −9.8 | +0.1 | +21.4 | +32.1 | +15.5 |
| years ahead, of 19 | | 10 | 11 | 8 | 12 | 13 | 10 |

The three-way blend's years on the other two seeds are within 2.5
points of seed 23's in every year (sums +28.4 / +24.8 and +28.9 /
+22.9).

What was bought (seed 23):

| | distinct stocks | delisting liquidations | sales on the rank rule | held at the end | largest holding at the end | five largest | sectors |
|---|---|---|---|---|---|---|---|
| forest alone | 178 | 50 | | 128 | | | utilities 20%, real estate 16%, consumer defensive 15% |
| + return on capital | 94 | 26 | | 68 | FISV 13% | 42% | consumer defensive 22%, industrials 18%, technology 18% |
| the same, sell discipline | 94 | 4 | 69 | 48 | FISV 18% | 52% | |
| three-way | 235 | 65 | | 170 | AAPL 8% | 26% | consumer defensive 17%, industrials 16%, technology 15%, healthcare 15%, consumer cyclical 15%; utilities and real estate 1.4% |
| the same, sell discipline | 241 | 5 | 234 | 63 | | | the same |

Rank-rule sales: 69 in sixteen years for the quality blend (median
3.7 years after the first buy, 29% at a loss), 234 for the three-way
blend (2.0 years, 38%), 413 for the momentum blend (1.0 year, 42%).

## Against the predictions in the configs

| | prediction | measured | matched? |
|---|---|---|---|
| quality blend, seeds 232 and 1776 | time-weighted within 0.7 points of 9.65%, drawdown within 3 points of −41.2%, per buy +0.005 or more | 10.18 and 10.04%; −42.4 and −41.3%; +0.019 and +0.012 | yes |
| three-way blend | between its parents on return (9.65–11.07%), drawdown (−41 to −48%) and per buy | 12.24%, −41.2%, +0.025: above both | **no**, missed upwards |
| quality blend, sell discipline | 0.5 to 1.5 points above buy and hold; costs up to 3 times; drawdown within 3 points | +0.99; 2.1 times; 2.4 points shallower | yes |
| momentum blend, sell discipline | not more than 0.5 above buy and hold; costs 4 times or more | 1.2 below; 8.5 times | yes |
| three-way, seeds | all four criteria; time-weighted within 1.0 of 12.24% | met; 12.26 and 12.23% | yes |
| quality + sell, seeds | final value above SPY's and above the same seed's buy and hold; 10.2–11.2%; drawdown within 3 points | 852,325 and 803,800 (752,267 and 721,826); 11.09 and 10.79%; −39.7 and −39.4% | yes |
| three-way, fractional shares | within 1.0 point and 10% of the whole-share run | 12.12% against 12.24%; 936,540 against 948,956 | yes |
| three-way, sell discipline | costs 3 to 6 times; time-weighted below buy and hold | 4.2 times; 0.9 **above** | costs yes, return **no** |
| three-way + sell, seeds | within 1.0 of 13.14% and above the same seed's buy and hold; four criteria | 12.70 and 12.66% (12.26 and 12.23%); met | yes |

## Measured

1. **Forest, momentum and return on capital together meet all four
   criteria on all three seeds**: 949,000 to 960,000 against SPY's
   732,110 (+30%), 12.2% a year time-weighted against 9.6%, a worst
   drawdown of −41% to −42% against −53%, and +0.024 to +0.026 a year
   per buy over three years, positive for the buys of both halves.
   61% of its buys beat SPY over their first three years and 20% to
   21% lost money.
2. **It does not come from the whole-share rule** (fractional shares:
   12.12%, 936,540) **or from the forest's seed** (the three seeds
   are within 0.03 points a year of each other: two thirds of the
   rank is two deterministic factors).
3. **Its lead is in both halves**, unlike the momentum blend's:
   yearly excess sums to +29.9 points over 2005–12 and +21.4 over
   2013–20 (momentum blend: +44.8 and −9.8). It was ahead of SPY in
   2008 (+9.5) and 2022 (+4.6) and 9.5 points behind in 2021.
4. **The quality blend alone is a steadier, smaller edge**: per buy
   +0.012 to +0.019 on three seeds and positive in both halves on
   each, SPY's rate of return with a drawdown 11 points shallower,
   and a final value between 5% below and 3% above SPY's. It buys 94
   stocks in sixteen years and its five largest holdings are 42% of
   it at the end.
5. **A rank sell discipline helps where the rank is stable and hurts
   where it is not.** Quality blend: +0.75 to +0.99 points a year on
   three seeds, a drawdown 1.9 to 2.7 points shallower, costs doubled, 69
   sales in sixteen years; it lifts the quality blend over all four
   criteria on every seed. Three-way blend: +0.4 to +0.9 points, four
   times the costs, about 15 sales a year. Momentum blend: −1.2
   points, 8.5 times the costs, 413 sales.
6. **Momentum helps only beside quality.** Added to the forest alone
   it gives a time-weighted lead that sits in 2005–11 and a per-buy
   excess of −0.016 to −0.023 for the buys of 2013–20; added to the
   forest with return on capital it doubles the per-buy excess
   (+0.025 against +0.013) in both halves.
7. **The portfolios differ from the forest's in kind.** Return on
   capital is not defined for most real estate companies and is low
   for utilities (the factor ranks a NULL last), so the blends that
   include it hold 1% to 2% in those two sectors where the forest
   alone held 35%.

## What it might mean (hypotheses)

- *Why three rankings beat any two.* Each pair leaves a known hole:
  safe and rising stocks include takeover targets and late-cycle
  cyclicals; safe and profitable ones are steady and few (94 names).
  A stock ranked high on all three is a profitable company that the
  market is currently re-rating and that the forest does not expect
  to fall. Rival: it is the best of 26 looks at sixteen years in
  which low risk, quality and momentum are each known to have paid
  in US stocks; the blend may be no more than their sum over this
  period. Nothing on these years separates the two.
- *Why the screen rated the three-way blend at +0.006 and the
  backtest's buys at +0.025.* The screen enters at the snapshot and
  carries acquired stocks flat
  ([blends note](2026-09-30-blends-and-calibration.md)); it has been
  harsh on every blend with momentum in it. Not resolved.

## Caveats

- Twenty-six configurations, one sixteen-year sample, one price
  path. The criteria were fixed before the thirteen new runs and the
  ingredients before any backtest; that protects against moving the
  goalposts, not against the sample.
- The forest was selected on the same years (80 configurations in
  cell C).
- `sector` is a current-state classification (data/features.md): the
  cap groups stocks by today's sector.
- Costs are 35 bps a side with no market impact; the floor is
  100,000 a day of dollar volume. The three-way blend's buys were
  not checked for how many sit near the floor.
- 2021–23 is outcome of buys made through 2020 and overlaps the
  holdout era: context. Every portfolio trailed SPY in 2021.
- Whole shares leave 86 to 111 of 192 months short of ten buys; the
  fractional run says it does not matter for the three-way blend.
  The other portfolios were not re-run with fractional shares.
- The quality blend's concentration (two holdings a third of the
  portfolio with the sell discipline) is a risk the backtest does
  not price. No position cap exists in the strategy code.
