# Backtests with a sector cap

Detail behind the [logbook](../logbook.md) entry for the capped
backtests of 2026-09-29. Decision 7 of the
[decision log](2026-09-29-decisions.md); follows the
[first backtests](2026-09-29-first-backtests.md).

**Simulated, cost-adjusted paper results, not live performance, and
not results of record.** `dataset_v1.4`, `prices_v1.0`, fold
definitions `split_folds.parquet` of `dataset_v1.4`. Six backtest
configurations have been tried on `dataset_v1.4`; all six are in the
table below.

## What ran, and how it was checked

- Code: `max_per_group` at selection, branch
  `claude/backtest-sector-cap` (commit `ca719a8`), merged into the
  lab branch. 458 tests pass (446 before, 12 added).
- The uncapped `bt_nonloser_dd30_top10` was run again after the
  merge: the same config hash (`058c78752aa3032d`) and the same
  figures to the last digit. The change does nothing when the cap is
  not set.
- Three capped backtests, the template of decision 6 with one line
  added. Same bundles as before (cell C run `53ceedd93e6d`, cell A
  run `df10b2ee396f`). The combination of the two bundles was not
  repeated: uncapped it was the same portfolio as either alone.

## Results

Deposits 192,000 in each leg, buys 2005–2020, valued 2023-12-29.

| backtest | cap per sector | final value | money-weighted | time-weighted CAGR | worst drawdown | 2007 | 2008 |
|---|---|---|---|---|---|---|---|
| cell C | none | 518,612 | 8.70% | 7.90% | −63.4% | −20.7% | −44.7% |
| cell A | none | 534,517 | 8.96% | 7.65% | −64.1% | −20.4% | −48.3% |
| C and A, mean rank | none | 541,571 | 9.07% | 7.72% | −64.8% | −22.4% | −46.7% |
| **cell C** | **2** | **633,757** | **10.40%** | **9.74%** | **−46.1%** | −4.5% | −29.8% |
| cell A | 2 | 605,182 | 10.01% | 8.73% | −49.0% | −7.1% | −31.6% |
| cell C | 1 | 650,980 | 10.63% | 9.69% | −42.8% | +1.0% | −28.9% |
| SPY, same deposits | | 732,110 | 11.62% | 9.58% | −52.9% | +7.3% | −43.2% |

Cell C, cap 2, by year (time-weighted):

| year | portfolio | SPY | excess | | year | portfolio | SPY | excess |
|---|---|---|---|---|---|---|---|---|
| 2005 | 10.3% | 6.5% | +3.8 | | 2015 | 4.2% | 4.5% | −0.3 |
| 2006 | 16.5% | 12.7% | +3.9 | | 2016 | 11.0% | 6.5% | +4.5 |
| 2007 | −4.5% | 7.3% | −11.8 | | 2017 | 19.4% | 22.9% | −3.5 |
| 2008 | −29.8% | −43.2% | +13.4 | | 2018 | 5.9% | 7.5% | −1.6 |
| 2009 | 30.8% | 39.1% | −8.3 | | 2019 | 16.4% | 13.8% | +2.6 |
| 2010 | 26.9% | 10.9% | +16.1 | | 2020 | 3.5% | 19.8% | −16.3 |
| 2011 | 13.6% | 5.3% | +8.3 | | 2021 | 15.5% | 24.8% | −9.4 |
| 2012 | 16.9% | 15.6% | +1.3 | | 2022 | 4.2% | −8.2% | +12.4 |
| 2013 | 17.6% | 30.4% | −12.9 | | 2023 | 2.4% | 19.0% | −16.6 |
| 2014 | 20.5% | 16.2% | +4.3 | | | | | |

Ahead of SPY in 10 of 19 years, and in both of SPY's down years
(2008 by 13.4 points, 2022 by 12.4). Behind by 9 points or more in
2007, 2013, 2020, 2021 and 2023.

What was bought, cell C with cap 2: utilities 0.20 of buys, real
estate 0.16, consumer defensive 0.15, industrials 0.13, energy 0.11,
healthcare 0.08, consumer cyclical 0.07, the other four sectors 0.10
together. 6 to 9 sectors in every year; 18–30 distinct stocks a
year. With cap 1: ten sectors at 0.08–0.10 each.

## Against the predictions in the configs

| prediction | measured | matched? |
|---|---|---|
| C cap 2: 2007 within 10 points of SPY | 11.8 behind | **no**, by 1.8 |
| C cap 2: worst drawdown shallower than −63.4% and within 3 points of SPY's | −46.1%, 6.8 points shallower than SPY's | yes |
| C cap 2: final value above 518,612 | 633,757 | yes |
| C cap 2: at least 5 sectors every year | 6 to 9 | yes |
| A cap 2: 2007 within 10 points, shallower drawdown, higher final value | 14.4 behind; −49.0%; 605,182 | 2007 **no**; the others yes |
| A cap 2: the two cells differ by more than the 4.5% they differed uncapped | 4.7% on final value, 1.0 point on time-weighted CAGR (0.25 uncapped) | yes, barely on final value |
| C cap 1: final value and drawdown between cap 2's and SPY's | final value between (650,980); drawdown −42.8%, shallower than both | final value yes; drawdown **no**, better than predicted |
| C cap 1: fewer than 10 buys in some months | 55 of 192 months | yes |

## Measured

1. **Sector concentration was the reason for the deep drawdown.**
   The same models with at most two buys a sector: worst drawdown
   −46% against −63%, and 2007–08 turn from 29.5 points behind SPY
   over the two years to 1.6 ahead (cell C). Rival (a) of the first
   note, tested and kept.
2. **Capped, the portfolio compounds at SPY's rate with a shallower
   drawdown:** time-weighted 9.7% against 9.6%, drawdown −46%
   against −53% (cell C, cap 2 and cap 1).
3. **It still ends 11–13% below SPY in money** (633,757 and 650,980
   against 732,110). Deposits are equal each month, so most of the
   money is at work in the later years, and the portfolio's good
   years were early: it gained on SPY in 2005–06, 2008 and 2010–12
   and lost in 2013, 2020, 2021 and 2023.
4. **The shape is the thesis's:** less lost in market falls, less
   gained in strong rises. SPY's five best years in the window
   (2009, 2013, 2017, 2021, 2023; 19–39%) are all years the
   portfolio lagged, by 3.5 to 16.6 points.
5. **Cell C is ahead of cell A once capped** (time-weighted 9.7%
   against 8.7%, drawdown −46% against −49%); uncapped they were the
   same portfolio. One path each: a difference of one point a year
   is not a ranking.
6. **A tighter cap did not cost return.** One per sector: the same
   time-weighted CAGR as two, a drawdown 3.3 points shallower.
   Technology and healthcare, 3% and 8% of buys at cap 2, are 9–10%
   each at cap 1.

## Caveats

- Six backtests on the same sixteen years, three of them chosen
  after seeing the first three. The cap was decided on the sector
  table, not on returns, and its values (2 and 1) were fixed before
  the runs; the improvement is still in-sample to those years.
- One path per configuration, and 2007–08 carries much of the
  difference between capped and uncapped.
- Whole shares with 100 a pick (1,000 a month over 10 picks): a
  stock priced above its budget is not bought. 55–69 of 192 months
  bought fewer than 10 stocks in the capped runs (25–33 uncapped).
  The template was not changed to avoid it; it biases the portfolio
  towards lower-priced shares and leaves a little cash idle.
- Valuation after 2020 is outcome, not selection, but it overlaps
  the holdout era and is context.

## What it might mean (hypotheses, not tested)

- *Where the missing upside is.* The models rank on calm. Within a
  sector the cap lets through the two calmest stocks, which are not
  chosen for growth, value or momentum. Rivals for what would add
  upside without giving the losers back: (a) a second ranking beside
  the forest's (value, momentum or quality), so that a pick has to
  be calm and something else; (b) a sell discipline, so that money
  does not sit for years in stocks that no longer qualify; (c)
  nothing available in these columns does, and the portfolio is what
  these features can offer. Decision 8 tests (a).
