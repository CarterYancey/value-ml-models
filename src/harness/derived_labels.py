"""Derived binary labels: thresholds re-derived from the continuous outcomes.

Upstream stores the continuous outcomes (`fwd_{H}_cagr`, `_excess_cagr`,
`_max_drawdown{,_from_entry}`, ...) precisely so binary targets can be
derived downstream without a dataset rebuild (data/manual.md §3,
data/labels.md). A config names such a target as a *label expression*
wherever it would name a stored `label_*` column:

    label = "fwd_3y_cagr >= 0.12"
    label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"
    label = "cohort_pct(fwd_3y_cagr) >= 0.9"        # top cohort decile

Grammar (deliberately tiny, parsed — never `eval`'d):

    expr      := condition ("&" condition)*
    condition := operand op literal
    operand   := column | "cohort_pct(" column ")"
    op        := ">=" | ">" | "<=" | "<" | "==" | "!="
    literal   := number | true | false

- `column` must be declared in the manifest `labels` group (checked by
  `Dataset.derived_label`), and every column must carry the same `{H}y`
  horizon — the horizon's sample weight and split tags must fit the
  whole target.
- `cohort_pct(c)` is `percent_rank()` of `c` within its cohort
  `(quarter, snapshot_kind)` over every dataset row where `c` is not
  NULL — the era-neutral "top decile of the cohort" of data/manual.md,
  with duckdb's semantics ((rank − 1) / (n − 1), ties at their lowest
  rank, a single-row cohort at 0).
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

#: the cohort a `cohort_pct` term ranks within — one calendar quarter's
#: snapshots of one kind (data/manual.md's era-neutral rank label)
COHORT_KEYS = ("quarter", "snapshot_kind")

_OPS = (">=", "<=", "==", "!=", ">", "<")
_OP_SLUG = {">=": "ge", ">": "gt", "<=": "le", "<": "lt", "==": "eq", "!=": "ne"}
_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_CONDITION = re.compile(
    rf"^\s*(?:cohort_pct\(\s*(?P<cohort>{_IDENT})\s*\)|(?P<column>{_IDENT}))"
    r"\s*(?P<op>>=|<=|==|!=|>|<)\s*(?P<literal>\S+)\s*$"
)
_HORIZON = re.compile(r"(?:^|_)(\d+)y(?:_|$)")
#: characters no manifest column name contains — their presence is what
#: marks a label as an expression rather than a stored column
_EXPRESSION_CHARS = frozenset("<>=!&()")


def is_derived_label(label: str) -> bool:
    """Whether `label` is a label expression rather than a column name."""
    return any(ch in _EXPRESSION_CHARS for ch in label)


@dataclass(frozen=True)
class Condition:
    column: str
    #: the operand is `cohort_pct(column)` rather than the raw column
    cohort: bool
    op: str
    #: float for numeric comparisons, bool for boolean label columns
    value: float | bool

    @property
    def operand(self) -> str:
        return f"cohort_pct({self.column})" if self.cohort else self.column

    @property
    def literal(self) -> str:
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        return repr(float(self.value))

    def canonical(self) -> str:
        return f"{self.operand} {self.op} {self.literal}"

    def slug(self) -> str:
        col = self.column.removeprefix("fwd_")
        if self.cohort:
            col = f"{col}_cpct"
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
    def cohort_columns(self) -> tuple[str, ...]:
        """Columns ranked within a cohort — non-empty means the label of
        one row depends on its cohort peers' outcomes (see
        `Dataset.apply_split`'s cohort purge)."""
        return tuple(
            dict.fromkeys(c.column for c in self.conditions if c.cohort)
        )

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
                f"{part.strip()!r}; expected `column OP literal` or "
                "`cohort_pct(column) OP literal` with OP in "
                f"{list(_OPS)}, conditions joined by `&`"
            )
        cohort = m.group("cohort") is not None
        column = m.group("cohort") or m.group("column")
        op = m.group("op")
        value = _parse_literal(m.group("literal"), expr)
        if isinstance(value, bool):
            if cohort:
                raise ConfigError(
                    f"label expression {expr!r}: cohort_pct() is a "
                    "percentile in [0, 1]; compare it to a number"
                )
            if op not in ("==", "!="):
                raise ConfigError(
                    f"label expression {expr!r}: true/false only compare "
                    "with == or !="
                )
        elif cohort and not 0.0 <= value <= 1.0:
            raise ConfigError(
                f"label expression {expr!r}: cohort_pct() lies in [0, 1], "
                f"so comparing it to {value!r} is constant"
            )
        conditions.append(Condition(column, cohort, op, value))
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
