"""Derived binary labels: thresholds re-derived from the continuous outcomes.

Upstream stores the continuous outcomes (`fwd_{H}_cagr`, `_excess_cagr`,
`_max_drawdown{,_from_entry}`, ...) precisely so binary targets can be
derived downstream without a dataset rebuild (data/manual.md §3,
data/labels.md). A config names such a target as a *label expression*
wherever it would name a stored `label_*` column:

    label = "fwd_3y_cagr >= 0.12"
    label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"

Grammar (deliberately tiny, parsed — never `eval`'d):

    expr      := condition ("&" condition)*
    condition := column op literal
    op        := ">=" | ">" | "<=" | "<" | "==" | "!="
    literal   := number | true | false

- `column` must be declared in the manifest `labels` group (checked by
  `Dataset.derived_label`), and every column must carry the same `{H}y`
  horizon — the horizon's sample weight and split tags must fit the
  whole target.
- Every label is a function of its own row only. Cross-sectional
  outcome ranks (data/manual.md's "top decile of the cohort") are
  deliberately not offered: such a label depends on cohort peers whose
  windows close later than the row's own, which the upstream per-row
  purge/embargo does not cover — an upstream label if ever wanted.
  `label_{H}_beat_spy` / `fwd_{H}_excess_cagr` thresholds are the
  era-neutral targets here.
- NULL propagates: a row where any referenced column is NULL gets a NULL
  label (unobservable, not False — data/manual.md §3), so the row is
  dropped from the fit exactly like a stored label's NULL rows.

The expression is normalized to a canonical string (conditions sorted,
literals in shortest round-trip form), so the same target always lands
in the same trial-ledger cell whatever order or spacing a config used.
The stored rungs stay expressible: `fwd_3y_cagr >= 0.1` is the
definition of `label_3y_cagr_ge_10` (inclusive thresholds, labels.md).

This is target construction, not feature engineering (CLAUDE.md
invariant 4): derived labels live outside the manifest feature groups,
so they can never be selected as a model input.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from harness.errors import ConfigError

_OPS = (">=", "<=", "==", "!=", ">", "<")
_OP_SLUG = {">=": "ge", ">": "gt", "<=": "le", "<": "lt", "==": "eq", "!=": "ne"}
_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_CONDITION = re.compile(
    rf"^\s*(?P<column>{_IDENT})"
    r"\s*(?P<op>>=|<=|==|!=|>|<)\s*(?P<literal>\S+)\s*$"
)
_HORIZON = re.compile(r"(?:^|_)(\d+)y(?:_|$)")
#: characters no manifest column name contains — their presence is what
#: marks a label as an expression rather than a stored column
_EXPRESSION_CHARS = frozenset("<>=!&")


def is_derived_label(label: str) -> bool:
    """Whether `label` is a label expression rather than a column name."""
    return any(ch in _EXPRESSION_CHARS for ch in label)


@dataclass(frozen=True)
class Condition:
    column: str
    op: str
    #: float for numeric comparisons, bool for boolean label columns
    value: float | bool

    @property
    def literal(self) -> str:
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        return repr(float(self.value))

    def canonical(self) -> str:
        return f"{self.column} {self.op} {self.literal}"

    def slug(self) -> str:
        col = self.column.removeprefix("fwd_")
        lit = self.literal.replace("-", "m").replace(".", "p")
        return f"{col}_{_OP_SLUG[self.op]}_{lit}"


@dataclass(frozen=True)
class DerivedLabel:
    """A parsed label expression: a conjunction of conditions."""

    conditions: tuple[Condition, ...]

    @property
    def name(self) -> str:
        """The canonical expression — the label's identity everywhere
        (config hash, results ledger cell, frame column name)."""
        return " & ".join(c.canonical() for c in self.conditions)

    @property
    def source_columns(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(c.column for c in self.conditions))

    @property
    def horizon_years(self) -> int:
        horizons = set()
        for col in self.source_columns:
            m = _HORIZON.search(col)
            if m is None:
                raise ConfigError(
                    f"label expression {self.name!r}: column {col!r} "
                    "carries no `{H}y` horizon token; derived labels are "
                    "built from the per-horizon outcome columns only"
                )
            horizons.add(int(m.group(1)))
        if len(horizons) != 1:
            raise ConfigError(
                f"label expression {self.name!r} mixes horizons "
                f"{sorted(horizons)}; a label's sample weight and split "
                "tags are per horizon, so every column must share one"
            )
        return horizons.pop()

    def slug(self) -> str:
        """A filesystem-safe rendering for derived experiment names."""
        return "label_" + "_and_".join(c.slug() for c in self.conditions)


def _parse_literal(text: str, expr: str) -> float | bool:
    low = text.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        value = float(text)
    except ValueError:
        raise ConfigError(
            f"label expression {expr!r}: {text!r} is not a number or "
            "true/false"
        ) from None
    if not math.isfinite(value):
        raise ConfigError(
            f"label expression {expr!r}: literal {text!r} must be finite"
        )
    return value


def parse_label_expression(expr: str) -> DerivedLabel:
    """Parse and validate the syntax of a label expression. Column
    existence and types are checked against a manifest by
    `Dataset.derived_label`."""
    parts = expr.split("&")
    conditions = []
    for part in parts:
        m = _CONDITION.match(part)
        if m is None:
            raise ConfigError(
                f"label expression {expr!r}: cannot parse condition "
                f"{part.strip()!r}; expected `column OP literal` with OP "
                f"in {list(_OPS)}, conditions joined by `&`"
            )
        column = m.group("column")
        op = m.group("op")
        value = _parse_literal(m.group("literal"), expr)
        if isinstance(value, bool) and op not in ("==", "!="):
            raise ConfigError(
                f"label expression {expr!r}: true/false only compare "
                "with == or !="
            )
        conditions.append(Condition(column, op, value))
    unique = tuple(sorted(set(conditions), key=lambda c: c.canonical()))
    label = DerivedLabel(unique)
    label.horizon_years  # mixed/missing horizons fail at parse time
    return label


def normalize_label(label: str) -> str:
    """A label's canonical form: expressions are normalized, stored
    column names pass through unchanged."""
    if is_derived_label(label):
        return parse_label_expression(label).name
    return label


def label_slug(label: str) -> str:
    """A filesystem-safe label rendering for derived experiment names."""
    if is_derived_label(label):
        return parse_label_expression(label).slug()
    return label
