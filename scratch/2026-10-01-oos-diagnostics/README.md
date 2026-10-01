# Diagnostics of 2026-10-01 (decision 30)

Working material on the lab branch; not for `Claude`. The note that
reads these is docs/notes/2026-10-01-out-of-sample.md.

- `diag_oos.py <out dir>`: for every month of 2005-01 to 2026-08, the
  investable cross-section (`dollar_volume_3m_rank >= 0.2`, a quote
  within 3 days) scored by the candidate's three bundles (fold models
  to 2020, the cached year-end refits after); the capped top 10 of
  every combination of the three legs; and the 1- and 3-year outcome
  of every pick and of every investable candidate, by the backtest
  report's per-buy convention (checked against
  `portfolio.report.buy_outcomes` to 1e-15). No label column is read,
  nothing is fitted beyond the cached refits, nothing is logged to the
  ledger: no portfolio is simulated.
- `diag_summary.py`, `diag_size.py`: the tables (`*.txt`).
- `diag_watch.csv`: where twenty of the index's largest members ranked
  on each leg each January.

Run from the repository root at git `09bb3ac` (code as on `Claude` at
`c669212`), about six minutes, 9 GB.
