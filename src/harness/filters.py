"""Row predicates over feature columns: `column op value`.

One spec serves every place a config screens rows on what was known at
the snapshot: a backtest's `[[filters]]` and `[[investability]]`
(portfolio.config), and an experiment's `[[universe]]` (harness.config),
the rows a model is trained and evaluated on.

Two rules hold everywhere and are enforced here:

- a filter column must be declared by a filterable manifest group
  (`features`, `ranks`, `sector_ranks`). Labels and sample weights are
  outcomes and are structurally out of reach, and a column the manifest
  does not declare is an error, not an empty screen;
- NULL fails every filter: missingness never passes a screen.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass

import pandas as pd

from harness.errors import ConfigError

#: Comparison operators a filter may use. Ordering operators require a
#: numeric value; equality operators also accept strings (e.g. sector).
FILTER_OPS = (">", ">=", "<", "<=", "==", "!=")
_ORDERING_OPS = frozenset({">", ">=", "<", "<="})

_OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

#: manifest groups a filter may reference — labels and weights are
#: outcomes and structurally out of reach
FILTERABLE_GROUPS = ("features", "ranks", "sector_ranks")


@dataclass(frozen=True)
class FilterSpec:
    """One row predicate over a cross-section column. Rows whose column
    is NULL fail every filter — missingness never passes a screen."""

    column: str
    op: str
    value: float | int | str | bool

    @classmethod
    def from_table(cls, table: dict, source: str, where: str) -> "FilterSpec":
        if not isinstance(table, dict):
            raise ConfigError(
                f"config {source}: each {where} entry must be a table with "
                "column/op/value"
            )
        unknown = sorted(set(table) - {"column", "op", "value"})
        if unknown:
            raise ConfigError(
                f"config {source}: unknown {where} keys {unknown}; expected "
                "column, op, value"
            )
        missing = [k for k in ("column", "op", "value") if k not in table]
        if missing:
            raise ConfigError(
                f"config {source}: {where} entry lacks {missing}"
            )
        op = table["op"]
        if op not in FILTER_OPS:
            raise ConfigError(
                f"config {source}: {where} op {op!r} not in {list(FILTER_OPS)}"
            )
        value = table["value"]
        if op in _ORDERING_OPS and isinstance(value, (str, bool)):
            raise ConfigError(
                f"config {source}: {where} op {op!r} needs a numeric value, "
                f"got {value!r}"
            )
        return cls(column=str(table["column"]), op=op, value=value)

    def to_table(self) -> dict:
        return {"column": self.column, "op": self.op, "value": self.value}

    def describe(self) -> str:
        return f"{self.column} {self.op} {self.value}"

    def canonical(self) -> str:
        """`describe()` with whole floats written as integers, so that
        `100000` and `100000.0` name one filter."""
        value = self.value
        if (
            isinstance(value, float)
            and value.is_integer()
            and abs(value) < 1e15
        ):
            value = int(value)
        return f"{self.column} {self.op} {value}"


def validate_filter_columns(filters, dataset, where: str) -> None:
    """Every filter column must be declared by a filterable manifest
    group — labels and weights are structurally unreachable, and a typo
    is an error rather than an empty screen."""
    allowed = {c for g in FILTERABLE_GROUPS for c in dataset.columns(g)}
    for f in filters:
        if f.column not in allowed:
            raise ConfigError(
                f"{where} filter references {f.column!r}, which is not in "
                f"the manifest's {list(FILTERABLE_GROUPS)} groups (labels "
                "and weights can never be screened on)"
            )


def filter_mask(frame: pd.DataFrame, filters) -> pd.Series:
    """Boolean mask of the rows passing every filter; NULL fails."""
    mask = pd.Series(True, index=frame.index)
    for f in filters:
        col = frame[f.column]
        mask &= col.notna() & _OPS[f.op](col, f.value)
    return mask


def apply_filters(frame: pd.DataFrame, filters) -> pd.DataFrame:
    """Rows passing every filter. NULL fails: a stock with no value for a
    screened column is screened out, never waved through."""
    if not filters:
        return frame
    return frame[filter_mask(frame, filters)]


def describe_filters(filters) -> str:
    """`a >= 1 & b < 2`, in a canonical order: the text that qualifies a
    ledger cell, so two spellings of one universe are one cell."""
    return " & ".join(sorted(f.canonical() for f in filters))
