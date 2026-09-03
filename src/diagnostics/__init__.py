"""Registered diagnostics (data/manual.md §7, PLAN §7).

Diagnostic only — never model selection, never reported performance.
The diagnostic schemes (`entity_holdout`, `random_kfold`) are opened
solely by `scripts/run_diagnostic.py`, the single grant site of
`SplitAccess.REGISTERED_DIAGNOSTIC`; the library functions here default
to STANDARD access and refuse the diagnostic tags on their own.

- `era_probe`: the era-identifiability probe — predict the calendar year
  of a snapshot from its features alone (raw vs. rank sets).
"""
