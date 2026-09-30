# First backtests of the compounder forests

Detail behind the [logbook](../logbook.md) entries for the candidate
runs and the three backtests of 2026-09-29. Decisions 5 and 6 of the
[decision log](2026-09-29-decisions.md).

**Simulated, cost-adjusted paper results, not live performance, and
not results of record.** `dataset_v1.4`, `prices_v1.0`, fold
definitions `split_folds.parquet` of `dataset_v1.4`. Three backtest
configurations have been tried on `dataset_v1.4`, all reported here.
Before them the two cells had 80 (A) and 8 (C) walk-forward
configurations.

## What ran, and how it was checked

- `forest_nonloser_dd30_3y` (cell C, run `53ceedd93e6d`, config
  `087f2d7dfea489b2`) and `forest_cagr10_dd20_3y` (cell A, run
  `df10b2ee396f`), git `319144c`, through `vml-run`, fold bundles
  saved. Cell C's p@20 is 0.7875, the value of the sweep's seed-23
  run of the same model (0.788).
- Three backtests, one template (decision 6): top 10 of the month's
  cross-section by score, equal weights, buy and hold, 1,000
  deposited monthly into each leg, 35 bps a side,
  `dollar_volume_3m >= 100000`, buys 2005-01 to 2020-12, valued
  2023-12-29. Every trade year is inside the walk-forward folds; no
  refit was used. The investability filter leaves 3,153 of 4,052
  stocks in the mean monthly cross-section.
- Sectors of the buys were read from `dataset.parquet` (the `sector`
  column of each bought stock's latest median snapshot on or before
  the trade date, joined on `permaticker`). A description of the
  trades; nothing was selected on it.

## Results

| backtest | bundles | final value | money-weighted | time-weighted CAGR | worst drawdown | costs |
|---|---|---|---|---|---|---|
| `bt_nonloser_dd30_top10` | cell C | 518,612 | 8.70% | 7.90% | −63.4% | 1,442 |
| `bt_cagr10_dd20_top10` | cell A | 534,517 | 8.96% | 7.65% | −64.1% | 1,409 |
| `bt_nonloser_and_cagr10_top10` | C and A, mean rank | 541,571 | 9.07% | 7.72% | −64.8% | 1,513 |
| SPY, same deposits | | 732,110 | 11.62% | 9.58% | −52.9% | 0 |

Deposits 192,000 in each leg. Per year, time-weighted, cell C's
portfolio (the other two are within 5 points of it in every year but
2009, where cell A's made 55.9%):

| year | portfolio | SPY | excess | | year | portfolio | SPY | excess |
|---|---|---|---|---|---|---|---|---|
| 2005 | 11.0% | 6.5% | +4.5 | | 2015 | 3.6% | 4.5% | −0.9 |
| 2006 | 34.0% | 12.7% | +21.4 | | 2016 | 10.0% | 6.5% | +3.5 |
| 2007 | −20.7% | 7.3% | −28.0 | | 2017 | 17.1% | 22.9% | −5.8 |
| 2008 | −44.7% | −43.2% | −1.5 | | 2018 | 5.0% | 7.5% | −2.5 |
| 2009 | 45.4% | 39.1% | +6.4 | | 2019 | 15.4% | 13.8% | +1.6 |
| 2010 | 27.1% | 10.9% | +16.2 | | 2020 | −0.4% | 19.8% | −20.1 |
| 2011 | 14.3% | 5.3% | +8.9 | | 2021 | 14.5% | 24.8% | −10.3 |
| 2012 | 16.3% | 15.6% | +0.7 | | 2022 | 4.8% | −8.2% | +13.0 |
| 2013 | 12.2% | 30.4% | −18.2 | | 2023 | −1.5% | 19.0% | −20.5 |
| 2014 | 23.6% | 16.2% | +7.4 | | | | | |

Ahead of SPY in 10 of 19 years. The five years it lost by 18 points
or more (2007, 2013, 2020, 2023 and, by 10, 2021) cost more than the
ten gained.

## What was bought

Share of buys by sector, 2005–2020, against the sectors' share of
median-kind rows in the dataset over the same years:

| sector | cell C's buys | cell A's buys | universe |
|---|---|---|---|
| Utilities | 0.49 | 0.36 | 0.03 |
| Real Estate | 0.27 | 0.34 | 0.06 |
| Consumer Defensive | 0.07 | 0.06 | 0.05 |
| Energy | 0.06 | 0.08 | 0.08 |
| Industrials | 0.06 | 0.08 | 0.15 |
| Healthcare | 0.03 | 0.03 | 0.19 |
| Technology | under 0.03 | under 0.03 | 0.19 |

Cell C's portfolio by year: the largest sector among the year's
buys, its share, and the number of sectors bought:

| year | largest sector | share | sectors | | year | largest sector | share | sectors |
|---|---|---|---|---|---|---|---|---|
| 2005 | Real Estate | 1.00 | 1 | | 2013 | Utilities | 0.55 | 8 |
| 2006 | Real Estate | 1.00 | 1 | | 2014 | Utilities | 0.65 | 5 |
| 2007 | Real Estate | 0.92 | 4 | | 2015 | Consumer Defensive | 0.28 | 7 |
| 2008 | Real Estate | 0.46 | 4 | | 2016 | Utilities | 0.61 | 6 |
| 2009 | Utilities | 0.78 | 3 | | 2017 | Utilities | 0.46 | 6 |
| 2010 | Utilities | 0.80 | 4 | | 2018 | Utilities | 0.73 | 6 |
| 2011 | Utilities | 0.65 | 4 | | 2019 | Utilities | 0.83 | 3 |
| 2012 | Utilities | 0.57 | 4 | | 2020 | Utilities | 0.61 | 5 |

Of the 2005–07 buys, a quarter were mortgage REITs and the rest
residential, industrial, office, retail and diversified REITs.
20–30 distinct stocks were bought in each year.

## Against the predictions in the configs

| prediction | measured | matched? |
|---|---|---|
| C ends within 15% of SPY's final value | 29% below | **no** |
| C's worst drawdown is shallower than SPY's | −63.4% against −52.9% | **no** |
| C gains on SPY in 2007–09 and loses in 2017–20 | 2007 −28.0, 2008 −1.5, 2009 +6.4; 2017–20: −5.8, −2.5, +1.6, −20.1 | **no** for 2007–08, yes for 2017–20 |
| costs under 0.5% a year | 1,442 on 192,000 deposited over 16 years | yes |
| A within 15% of SPY and within 10% of C | 27% below SPY; 3% above C | no, yes |
| A has a deeper worst drawdown than C | −64.1% against −63.4% | yes, by 0.7 points |
| the two together land between the two alone | final value above both, drawdown deeper than both, by 1% and 0.7 points | no, within noise |

## Measured

1. **The three portfolios are one portfolio.** Final values within
   4.5% of each other, worst drawdowns within 1.4 points, yearly
   returns within 5 points. The two labels and their combination
   choose from the same stocks.
2. **They end 26–29% below SPY with a deeper drawdown.** On the
   screen the same models' picks matched SPY on the median with a
   third of the average stock's drawdown.
3. **The models are sector selectors.** Half of all buys are
   utilities and a quarter real estate, sectors that make up 3% and
   6% of the universe. Every buy of 2005 and 2006 was a REIT, and
   92% of 2007's. The portfolio lost 20.7% in 2007 while SPY gained
   7.3%, and 44.7% in 2008.
4. **The precision figures of the screen were not wrong, and did
   not show this.** Cell C's p@20 is 0.15–0.60 for entry years
   2006–08, which the era table showed as "crash-window years at the
   base rate". The backtest shows what was behind it: not a
   market-wide fall catching calm stocks, but a single sector bought
   at the top. "Distinct stocks among the picks" counted 9–18 stocks
   and could not see that they were one sector.
5. **The score was highest where the model was most wrong.** Mean
   score of the picks 0.81–0.84 in 2006–08 and 0.65–0.69 in 2011–13,
   when precision was 1.0. A fixed score threshold selects the
   pre-crash years: `score >= 0.8` has a pooled precision of 0.42
   over 597 rows, against 0.79 for the top 20 of each year. Selection
   by a fixed score is not the route to higher precision with these
   models; a threshold relative to the year's scores might be.

## What it might mean (hypotheses, not tested)

- *Why the screen and the backtest disagree.* Rivals: (a) sector
  concentration: three-year outcomes of one sector's stocks are one
  observation, not twenty, so the median of the picks says little
  about the portfolio's path; (b) timing: the screen's picks are the
  top rows of a whole test year, the backtest buys the top 10 of
  each month, and holds beyond three years; (c) the investability
  filter removes picks the screen counted. A sector cap in the
  backtest separates (a) from the others: if capped portfolios lose
  the 2007–08 hole and the drawdown falls below SPY's, it is (a).
- *Why utilities and REITs.* They are the calmest sectors, and the
  forests rank on `vol_12m_rank` and `vol_36m_rank`, which are
  ranked across the whole market, not within a sector. A utility of
  average calm outranks the calmest technology stock.

## Decision

A sector cap at selection (decision 7 of the
[decision log](2026-09-29-decisions.md)), built on a feature branch,
and the three backtests repeated with it. The template's other
values do not change.
