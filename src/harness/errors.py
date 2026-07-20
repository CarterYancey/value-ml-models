"""Harness errors.

The guardrails from TODO §1 are raised as exceptions, never left as
conventions: sealed-holdout access, diagnostic-scheme access, and fitting
without the horizon's uniqueness weight are all hard errors.
"""


class HarnessError(Exception):
    """Base class for all harness errors."""


class DatasetValidationError(HarnessError):
    """A versioned dataset directory failed validation on load."""


class SplitApplicationError(HarnessError):
    """A (scheme, fold, horizon) selection is invalid or inconsistent."""


class HoldoutAccessError(HarnessError):
    """The sealed `holdout` scheme was requested outside the dedicated
    final-eval script. It is evaluated once per phase; results seen there
    never flow back into selection."""


class DiagnosticSchemeError(HarnessError):
    """A diagnostic-only scheme (`entity_holdout`, `random_kfold`) was
    requested outside the registered-experiment runner. `random_kfold` is
    deliberately leaky; neither may inform model selection or reported
    performance."""


class MissingSampleWeightError(HarnessError):
    """A fit was attempted without the horizon's `sample_weight_{H}y`.
    Overlapping label windows make unweighted fits silently overconfident."""


class ConfigError(HarnessError):
    """An experiment config file is malformed or references unknown
    columns/models."""
