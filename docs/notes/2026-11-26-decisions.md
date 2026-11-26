# Decision log, continued from 2026-11-26

This file continues [the decision log begun on 2026-09-29](2026-09-29-decisions.md).
Carter closed that file on 2026-11-26 and asked that nothing more be
added to it. The numbering continues here, and the rules in that
file's header still hold: one numbered entry per decision, newest
last, with the reason and what it rests on. Results are in the
[logbook](../logbook.md) and the notes it links to.

### 73. The Foamex move is not accepted as real; upstream is asked to investigate; the first decision log is closed

*What happened (2026-11-26):* Carter read decision 72 and rejected its
conclusion. A 400-fold return in five months is not something that
happens, whatever the vendor's own record says. He asked for a note
for upstream to investigate further, and that no more entries be added
to the decision log of 2026-09-29.

*What decision 72 rested on, and what it did not.* The check behind
"the move is real" used Sharadar's price table, Sharadar's daily
market value and Sharadar's corporate-action table, which are three
views of one vendor's data, and the public record of the
reorganization, which says the equity survived but not what it traded
at in January 2006. No quote from an independent source was checked.
A 451-fold move from an adjusted close of 4 cents on 2006-01-03 to
18.04 dollars on 2006-05-01, from a price the vendor records to the
nearest cent, is the kind of result that is a data question first and
a finding second (CLAUDE.md, "a surprising positive").

*Decided (Carter):*

1. **The Foamex price path is an open data question for upstream.**
   The sentence "the move is real" in decision 72 is withdrawn. The
   move is recorded as unverified, and the note
   [upstream request: the Foamex price path](2026-11-26-upstream-foamex-price-check.md)
   says what was seen, what was checked here and what upstream is
   asked to check. Until upstream answers, the W70 run of round 6
   rests on an unverified price and every record that cites it says
   so. Nothing in this repo may correct the price (invariant 4 and
   the dataset rule: data fixes are upstream changes).
2. **Decisions are logged in this file from now on.** The log of
   2026-09-29 is closed at decision 72 and is not edited again, not
   even for a pointer; agents.md, GLOSSARY.md and findings.md point
   here instead.
3. **What does not change.** The CAGR stays the metric of record for
   a backtest (decision 72, items 1 and 2). The price-floor question
   (decision 71.3) stands, with one more reason behind it: whether or
   not the Foamex path is right, a filter that admits a 1-cent stock
   admits the one kind of row most likely to carry a data error.
