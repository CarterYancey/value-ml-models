"""Derived binary labels: thresholds re-derived from the continuous outcomes.

Upstream stores the continuous outcomes (`fwd_{H}_cagr`, `_excess_cagr`,
`_max_drawdown{,_from_entry}`, ...) precisely so binary targets can be
derived downstream without a dataset rebuild (data/manual.md §3,
data/labels.md). A config names such a target as a *label expression*
wherever it would name a stored `label_*` column:

    label = "fwd_3y_cagr >= 0.12"
    label = "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"
    label = "fwd_3y_excess_cagr > 0 & fwd_1y_max_drawdown_from_entry < 0.1"
    label = "(fwd_3y_cagr >= 0.15 | fwd_3y_excess_cagr >= 0.05) & fwd_3y_max_drawdown < 0.4"

Grammar (deliberately tiny, parsed — never `eval`'d; `&` binds tighter
than `|`, parentheses group):

    expr      := term ("|" term)*
    term      := atom ("&" atom)*
    atom      := "(" expr ")" | condition
    condition := column op literal
    op        := ">=" | ">" | "<=" | "<" | "==" | "!="
    literal   := number | true | false

- `column` must be declared in the manifest `labels` group (checked by
  `Dataset.derived_label`) and carry a `{H}y` horizon token.
- **Mixed horizons are allowed; the longest one governs.** Every
  horizon's window starts at `snapshot_date`, so a shorter window lies
  inside the longest and the union of the windows *is* the longest
  window. The label therefore takes that horizon's split tags (a train
  row's `snapshot + H_max + E < test_start` holds a fortiori for every
  shorter H, and a test row observable at H_max is observable at all of
  them), its `sample_weight_{H_max}y` (uniqueness is a property of the
  window) and its observability marker. `horizon_years` is inferred as
  that maximum; the cost is that a `1y & 3y` label runs on the 3y fold
  calendar, not the 1y one.
- Every label is a function of its own row only. Cross-sectional
  outcome ranks (data/manual.md's "top decile of the cohort") are
  deliberately not offered: such a label depends on cohort peers whose
  windows close later than the row's own, which the upstream per-row
  purge/embargo does not cover — an upstream label if ever wanted.
  `label_{H}_beat_spy` / `fwd_{H}_excess_cagr` thresholds are the
  era-neutral targets here.
- NULL propagates, under `|` too: a row where any referenced column is
  NULL gets a NULL label (unobservable, not False — data/manual.md §3),
  so the row is dropped from the fit exactly like a stored label's
  NULL rows. Three-valued `TRUE OR NULL = TRUE` is deliberately not
  used: within a horizon every column is NULL together, so the rows
  where it would differ are exactly those outside the label's (longest)
  window, which the tags already exclude.

The expression is normalized to a canonical sum of products (each
`&`-clause's conditions sorted, duplicate conditions and clauses
dropped, clauses sorted, literals in shortest round-trip form), so the
same target always lands in the same trial-ledger cell whatever order,
spacing or bracketing a config used. The stored rungs stay
expressible: `fwd_3y_cagr >= 0.1` is the definition of
`label_3y_cagr_ge_10` (inclusive thresholds, labels.md).

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
#: the expression tokens; anything between them is a condition
_TOKEN = re.compile(r"\(|\)|&|\||[^()&|]+")
#: characters no manifest column name contains — their presence is what
#: marks a label as an expression rather than a stored column
_EXPRESSION_CHARS = frozenset("<>=!&|()")


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

    @property
    def horizon_years(self) -> int:
        m = _HORIZON.search(self.column)
        if m is None:
            raise ConfigError(
                f"label expression: column {self.column!r} carries no "
                "`{H}y` horizon token; derived labels are built from the "
                "per-horizon outcome columns only"
            )
        return int(m.group(1))

    def canonical(self) -> str:
        return f"{self.column} {self.op} {self.literal}"

    def slug(self) -> str:
        col = self.column.removeprefix("fwd_")
        lit = self.literal.replace("-", "m").replace(".", "p")
        return f"{col}_{_OP_SLUG[self.op]}_{lit}"


#: one `&`-clause: conditions in canonical order
Clause = tuple[Condition, ...]


@dataclass(frozen=True)
class DerivedLabel:
    """A parsed label expression in canonical sum-of-products form: the
    label is true where any clause has every condition true."""

    clauses: tuple[Clause, ...]

    @property
    def name(self) -> str:
        """The canonical expression — the label's identity everywhere
        (config hash, results ledger cell, frame column name)."""
        return " | ".join(
            " & ".join(c.canonical() for c in clause) for clause in self.clauses
        )

    @property
    def conditions(self) -> tuple[Condition, ...]:
        """Every distinct condition, in canonical order."""
        seen = {c.canonical(): c for clause in self.clauses for c in clause}
        return tuple(seen[k] for k in sorted(seen))

    @property
    def source_columns(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(c.column for c in self.conditions))

    @property
    def horizons(self) -> tuple[int, ...]:
        """Every horizon the expression references, ascending."""
        return tuple(sorted({c.horizon_years for c in self.conditions}))

    @property
    def horizon_years(self) -> int:
        """The governing horizon: the longest window referenced (see the
        module docstring — the union of the windows is that window)."""
        return self.horizons[-1]

    def slug(self) -> str:
        """A filesystem-safe rendering for derived experiment names."""
        return "label_" + "_or_".join(
            "_and_".join(c.slug() for c in clause) for clause in self.clauses
        )


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


def _parse_condition(text: str, expr: str) -> Condition:
    m = _CONDITION.match(text)
    if m is None:
        raise ConfigError(
            f"label expression {expr!r}: cannot parse condition "
            f"{text.strip()!r}; expected `column OP literal` with OP in "
            f"{list(_OPS)}, conditions joined by `&` / `|`, grouped by "
            "parentheses"
        )
    column = m.group("column")
    op = m.group("op")
    value = _parse_literal(m.group("literal"), expr)
    if isinstance(value, bool) and op not in ("==", "!="):
        raise ConfigError(
            f"label expression {expr!r}: true/false only compare with "
            "== or !="
        )
    cond = Condition(column, op, value)
    cond.horizon_years  # a column without a horizon token fails here
    return cond


class _Parser:
    """Recursive descent over the token stream, building the sum of
    products directly: a clause list is the DNF of the subexpression."""

    def __init__(self, expr: str):
        self.expr = expr
        self.tokens = [t for t in _TOKEN.findall(expr) if t.strip()]
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise ConfigError(
                f"label expression {self.expr!r}: unexpected end of "
                "expression"
            )
        self.pos += 1
        return tok

    def parse(self) -> list[list[Condition]]:
        clauses = self.expr_()
        if self.peek() is not None:
            raise ConfigError(
                f"label expression {self.expr!r}: unexpected {self.peek()!r}"
            )
        return clauses

    def expr_(self) -> list[list[Condition]]:
        clauses = self.term()
        while self.peek() == "|":
            self.take()
            clauses += self.term()
        return clauses

    def term(self) -> list[list[Condition]]:
        clauses = self.atom()
        while self.peek() == "&":
            self.take()
            right = self.atom()
            clauses = [left + r for left in clauses for r in right]
        return clauses

    def atom(self) -> list[list[Condition]]:
        tok = self.take()
        if tok == "(":
            clauses = self.expr_()
            if self.take() != ")":
                raise ConfigError(
                    f"label expression {self.expr!r}: missing ')'"
                )
            return clauses
        if tok in ("&", "|", ")"):
            raise ConfigError(
                f"label expression {self.expr!r}: unexpected {tok!r}"
            )
        return [[_parse_condition(tok, self.expr)]]


def parse_label_expression(expr: str) -> DerivedLabel:
    """Parse and validate the syntax of a label expression, returning
    its canonical sum of products. Column existence and types are
    checked against a manifest by `Dataset.derived_label`."""
    raw_clauses = _Parser(expr).parse()
    canon: dict[str, Clause] = {}
    for clause in raw_clauses:
        unique = {c.canonical(): c for c in clause}
        ordered = tuple(unique[k] for k in sorted(unique))
        canon[" & ".join(c.canonical() for c in ordered)] = ordered
    return DerivedLabel(tuple(canon[k] for k in sorted(canon)))


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
