# Upstream request: the Foamex price path, 2005 to 2007 (for Carter to forward)

Written 2026-11-26 under decision 73 of the
[decision log](2026-11-26-decisions.md). Carter's reading: a 400-fold
return in five months does not happen, so the price series behind it
needs investigation upstream. This note says what was seen, what was
checked here, and what upstream is asked to check. Nothing in this
repo may alter the price (invariant 4; data fixes are upstream changes
that produce a new version).

## What was seen

The backtest `bt_fresh70_forestC_top10_cap2_rankfloor_to2020`
(config `6240023813fd9ee1`, round 6 of the fallen-stock program,
[note](2026-11-25-fallen-stocks.md)) bought Foamex International
(permaticker 123699, ticker `FMXLQ` in the current tables) three times
inside `prices_v1.0`:

| date | adjusted close | unadjusted close | shares bought | cost |
|---|---|---|---|---|
| 2006-01-03 | 0.04 | 0.01 | 2,491 | 99.64 |
| 2006-02-01 | 0.16 | 0.04 | 636 | 101.76 |
| 2006-03-01 | 0.32 | 0.08 | 315 | 100.80 |

By 2006-05-01 the adjusted close was 18.04 (unadjusted 4.51): 451
times the first entry price in four months. The stock fell back to an
adjusted 0.005 by 2009-03-31, when it was delisted in a bankruptcy
liquidation; the backtest sold it there for 17.21 dollars. The
position of 300 dollars turned a 5,700-dollar account into about
67,000 for a time and gave the run a 2006 time-weighted return of
+1,911%, the program's highest TWR beside its lowest final value. That
run is why the TWR left the headline (decision 72).

## What was checked here, all from Sharadar's own tables

- **SEP** (`data/raw/SEP.parquet` upstream). Daily closes from
  2005-12-01 to 2006-06-30 move in steps of one unadjusted cent: 0.04
  to 0.03 in late December 2005, 0.01 to 0.03 through January 2006,
  0.04 to 0.08 in February, 0.06 to 0.15 in March, then 0.17 on
  2006-04-05, 0.25 on 04-13, 0.69 on 04-19, 1.44 on 04-21, 2.00 on
  04-25, 3.28 on 04-28 and 4.51 on 05-01. Volumes run from a few
  thousand to 1.7 million shares a day; 1.29 million shares traded on
  2006-01-27 at 2 cents. `close` is the unadjusted close times 4 and
  `closeadj` equals `close` throughout, so the only adjustment in the
  series is the split below.
- **ACTIONS.** Exchange NASDAQ to OTC on 2005-09-28; ticker `FMXI` to
  `FMXIQ` on 2005-12-01, back to `FMXI` on 2007-01-31, to `FMXL` on
  2007-07-02, to `FMXLQ` on 2009-01-08; a split with value 0.25 (one
  for four) on 2007-05-01; delisted and bankruptcy liquidation on
  2009-03-31 with value 1.30.
- **DAILY.** Market value 1.2 million dollars at the end of September
  2005, 0.7 million in December 2005 and January 2006, 2.0 million in
  February, 3.7 million in March, 80.4 million at the end of April
  2006 and 94 to 136 million through the rest of 2006 and early 2007.
  Enterprise value 754 to 959 million throughout.
- **The public record** of the reorganization (chapter 11 filed
  2005-09-19; equity commitments from the largest shareholders in
  2006; a rights offering at 2.25 dollars a share with a record date
  of 2006-12-29 that raised about 141 million; emergence on 2007-02-12
  with the old shareholders keeping their stock) says the equity
  survived. It does not say what the stock traded at in January 2006.

These agree with one another, but the three price-level facts come
from one vendor and the public record is silent on the price. No
independent quote was checked.

## What upstream is asked to check

1. **An independent price source for `FMXIQ` from October 2005 to
   May 2006.** The most direct is the company's own 10-K for 2006
   (SEC CIK 0000912908), whose market-price section lists quarterly
   high and low prices; a second is any historical quote archive for
   the pink-sheet ticker. If an independent source puts the
   January 2006 price at tens of cents rather than one cent, the
   Sharadar series is wrong by a factor of ten or more.
2. **Whether the price fall across the ticker change of 2005-12-01**
   (`FMXI` to `FMXIQ`, when the close went from 0.12 to 0.16 adjusted
   in November to 0.04 in early January) is a real fall or a join
   between two series on different scales.
3. **Whether the reverse split of 2007-05-01 was applied once.** The
   unadjusted and adjusted closes differ by exactly 4 before it and
   agree after it, which is consistent with one application, but the
   same check against the share count (about 24.5 million shares
   before the rights offering) would confirm it: 0.7 million dollars
   of market value at 1 cent implies 70 million shares, not 24.5.
4. **How many other rows look like this.** A scan of SEP for stocks
   whose unadjusted close was below 5 cents and then rose 50-fold or
   more within six months, with the count by year and the list, would
   say whether this is one path or a class. A documented
   data-quality flag on such paths, or a documented minimum price in
   the upstream universe, would let this repo filter them without
   deriving anything.

## What this repo does meanwhile

- The W70 run of round 6 is read as resting on an unverified price;
  the records that cite it say so (decision 73).
- The CAGR, not the TWR, is the metric of record for a backtest
  (decision 72), which is what kept this one position from deciding
  a headline.
- Whether to add a price floor to the backtest's investability filter
  is Carter's open question (decision 71.3). It is a config change.
