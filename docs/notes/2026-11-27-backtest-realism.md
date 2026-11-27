# How realistic is the backtest? A first audit (2026-11-27, decision 84)

Carter's direction of 2026-11-27 (decision 83) put one task ahead of the
rest: before decisions rest on backtested performance, check that the
backtest is realistic, and either close each gap or state it as a known
bias with its direction. This note is the first pass. It reads the
engine's code and documentation, measures the one assumption that can be
measured from the records already on disk (the deposit schedule), and
lists what to change.

## What the engine does today

- **Prices.** Every stock is bought and valued at Sharadar's adjusted
  close (`closeadj`), which is adjusted for splits and dividends. The
  benchmark, SPY, uses the same adjusted close from the fund table.
  Holding a fixed number of shares therefore reinvests dividends for both
  legs. This is symmetric and fair.
- **Timing.** A rebalance happens on the first trading day of each
  month. The stocks available that day are those whose latest
  median-kind snapshot belongs to a calendar quarter that had ended
  before the trade date and is at most 200 days old. A snapshot's
  features were point-in-time at its own date, which is inside the
  quarter, so a signal is between one day and about seven months stale.
  That is conservative against a live run, which would score the latest
  filings. The buy is at that day's close. There is no look-ahead on
  fundamentals or prices.
- **Costs.** 35 basis points on each side of every trade, for every
  stock in every year. No commission model, no spread model, no market
  impact. The benchmark pays nothing, and SPY's expense ratio (about 9
  basis points a year) is not charged.
- **Deposits.** 1,000 on the first trading day of every month, flat, for
  21 years. Whole shares only by default, with the remainder in cash
  until next month; the cap-weighted books use fractional shares.
- **Delistings.** A holding that has not printed for 30 days is sold at
  its final print, with the cost applied. That is the upstream
  convention; for a bankruptcy the final print is near zero, for an
  acquisition it is the deal price.
- **Survivorship.** The cross-section is built from the training
  dataset, which keeps every stock that later delisted, so a stock can
  be bought and then die.
- **Taxes.** None. No tax on dividends, none on realized gains at a sale
  or a delisting.
- **Refits.** Years past a bundle's last walk-forward fold are served by
  simulated year-end refits on data whose labels were observable by the
  trade year; this is what a live run would do.

## What the deposit schedule does to the answer

The time-weighted path of a portfolio does not depend on how much is
deposited when, as long as the trades scale with the account, which is
exact for the fractional-share books and very nearly so for the
candidate. So the final value under any deposit schedule can be
computed from the recorded path without re-running anything. Five
schedules, each totalling 260,000 over 2005 to 2026:

| portfolio | flat 1,000 a month | growing 3% a year | growing 6% a year | all of it in January 2005 | flat to 2020, nothing after |
|---|---|---|---|---|---|
| SPY | 1,322,527 | 1,185,169 | 1,058,392 | 2,454,110 | 1,645,844 |
| the candidate | 1,156,293 | 1,014,208 | 886,541 | 2,482,002 | 1,459,982 |
| E1: large caps, cap-weighted, no model | 1,416,740 | 1,260,253 | 1,117,529 | 2,940,160 | 1,773,195 |
| E10: the blend's top 50, cap-weighted | 1,252,049 | 1,110,623 | 982,513 | 2,947,854 | 1,568,463 |
| E11: E10 with an earnings yield of 5% or more | 1,270,710 | 1,129,258 | 1,001,451 | 3,066,122 | 1,585,427 |

The same table as a ratio to SPY:

| portfolio | flat | growing 3% | growing 6% | lump sum in 2005 | flat to 2020 |
|---|---|---|---|---|---|
| the candidate | 0.874 | 0.856 | 0.838 | 1.011 | 0.887 |
| E1 | 1.071 | 1.063 | 1.056 | 1.198 | 1.077 |
| E10 | 0.947 | 0.937 | 0.928 | 1.201 | 0.953 |
| E11 | 0.961 | 0.953 | 0.946 | 1.249 | 0.963 |

(The flat column differs from the engine's own figures by about 0.3%
because the engine's path includes the whole-share cash remainder and
this reconstruction does not.)

The ranking of the portfolios against SPY does not change with the
schedule, but the size of the gap does, and its sign for the candidate
and E11 depends on when the money arrives. With all the money invested
at the start, the candidate ends 1% ahead of SPY and E11 25% ahead; with
contributions that grow with income, which is how most people invest,
both end further behind than the flat schedule says, because an even
larger share of the money is exposed to 2021 to 2026. "More money than
SPY" is a statement about the deposit schedule as much as about the
portfolio, and the flat 1,000 a month sits in the middle of the range.

## Known biases and their direction

| assumption | effect on the strategy against SPY | size |
|---|---|---|
| no SPY expense ratio | flatters SPY | about 2% of SPY's final value over 21 years |
| 35 basis points a side on every stock | hurts the strategy; too high for large caps after 2010, too low for small caps before | 0.4% of deposits for a hold-to-horizon book, so small; decisive for any sell discipline (decision 82) |
| no market impact | flatters the strategy in small caps; irrelevant for the cap-weighted large-cap books at these sizes | unknown, small at 1,000 a month |
| signals up to seven months stale | hurts the strategy | unknown; a live run would be fresher |
| no taxes | both legs untaxed; hold-to-horizon books and SPY are alike, a sell discipline is not | dividend tax of roughly 0.3 to 0.5 points a year on both legs; realized gains only where there are sales |
| delisting at the final print | neutral by construction | |
| whole shares at 1,000 a month | hurts the candidate slightly in later years (fewer buys, cash remainder) | within 2% of final value (the fractional run of 2026-11-24) |
| flat deposits | neither; shifts weight toward whichever period comes last | shown above |

## What to change

1. The report should show the final value under several deposit
   schedules, computed from the time-weighted path, beside the flat
   schedule's figure, so that no reader takes one schedule's final value
   for the result. This is a report change with no re-run.
2. The engine should accept a deposit that grows at a yearly rate
   (`deposit_growth_per_year`), so that a schedule closer to a
   household's can be the run's own schedule when Carter wants it.
3. The benchmark should be able to carry an expense ratio
   (`benchmark_expense_bps_per_year`), off by default, so that the
   comparison with an index fund rather than an index can be made.
4. Taxes stay out of the engine for now and in the caveats: they do not
   separate hold-to-horizon books from SPY, and they are one more reason
   not to run a sell discipline in a taxable account.
5. Costs stay at 35 basis points a side. A cost model by size and era is
   a later task.

Items 1 to 3 are decision 84's code, on a topic branch with tests.
