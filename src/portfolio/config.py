"""Backtest strategy config: one TOML file per strategy in
`experiments/portfolios/`.

A config pins everything a portfolio simulation depends on: the model
bundles (walk-forward fold models), the score combination, every filter
(including the investability filter, which must be stated explicitly —
`investability = "none"` is a deliberate, reported choice, never a
default), the portfolio strategy and its sizing, transaction costs
(required — a cost-free backtest is not a result), and the simulation
window. The canonical-JSON SHA-256 is the identity logged with every
run, so backtest configurations count as trials like any other.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

from harness.errors import ConfigError

#: Comparison operators a filter may use. Ordering operators require a
#: numeric value; equality operators also accept strings (e.g. sector).
FILTER_OPS = (">", ">=", "<", "<=", "==", "!=")
_ORDERING_OPS = frozenset({">", ">=", "<", "<="})

COMBINE_MODES = ("product", "mean", "min", "mean_rank")
WEIGHTINGS = ("score", "equal")
MODEL_UPDATE_POLICIES = ("refit", "frozen")


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


@dataclass(frozen=True)
class BacktestConfig:
    name: str
    dataset_version: str
    #: `data/datasets/{prices_version}/` price panel (portfolio.prices)
    prices_version: str
    #: walk-forward ModelBundle directories (never deployment bundles)
    bundles: tuple[str, ...]

    # --- signal -----------------------------------------------------------
    #: how per-model scores collapse into the ranking/sizing score
    combine: str = "product"
    #: every model's score must exceed this (None = no per-model floor);
    #: requires probabilistic bundles — raw margins have no common scale
    min_score: float | None = None
    #: per-model overrides of `min_score`, keyed by bundle config name
    #: ([signal.min_scores] table); validated against the loaded bundles
    min_scores: dict = field(default_factory=dict)
    #: how trade years past a bundle's last walk-forward fold are served:
    #: "refit" — simulated year-end deployment refit on rows whose label
    #: window was observable by Jan 1 (data/manual.md §4 rule 7,
    #: point-in-time); "frozen" — keep the last fold's model
    model_update: str = "refit"
    #: days after `snapshot_date + horizon` before a label counts as
    #: observable for refits (terminal-month averaging + settlement)
    label_lag_days: int = 45
    #: a snapshot older than this at the trade date drops out of the
    #: cross-section (stale fundamentals are not a tradable signal)
    max_staleness_days: int = 200
    #: feature/rank column screens (e.g. revenue_trend_20q > 0)
    filters: tuple[FilterSpec, ...] = ()
    #: the liquidity screen (CLAUDE.md: backtests without one are flagged);
    #: () with investability_none=True is the explicit, reported opt-out
    investability: tuple[FilterSpec, ...] = ()
    investability_none: bool = False

    # --- portfolio --------------------------------------------------------
    strategy: str = "buy_and_hold"
    top_k: int = 25
    weighting: str = "score"
    monthly_cash: float = 1000.0

    # --- execution --------------------------------------------------------
    #: round-trip friction per side, in basis points — required in the
    #: TOML (no default): a backtest without transaction costs is not a
    #: reportable result
    cost_bps: float = 0.0
    benchmark_cost_bps: float = 0.0
    #: a candidate must have printed within this many calendar days of the
    #: trade date to be buyable (0 = must print on the trade date)
    max_quote_age_days: int = 0
    #: a held position whose last print is older than this is treated as
    #: delisted and liquidated at its final print
    delist_after_days: int = 30
    #: whole shares by default (buy budgets round down; the remainder
    #: stays in cash); True restores exact fractional spending
    fractional_shares: bool = False

    # --- window (optional; defaults derived from folds and the panel) ----
    start: date | None = None
    end: date | None = None
    valuation_end: date | None = None

    @classmethod
    def from_file(cls, path: str | Path) -> "BacktestConfig":
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"cannot read backtest config {path}: {exc}") from exc
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<dict>") -> "BacktestConfig":
        for key in ("dataset_version", "prices_version", "bundles"):
            if key not in raw:
                raise ConfigError(
                    f"backtest config {source} lacks required field {key!r}"
                )
        bundles = tuple(str(b) for b in raw["bundles"])
        if not bundles:
            raise ConfigError(f"backtest config {source}: bundles is empty")

        signal = raw.get("signal", {})
        combine = signal.get("combine", "product")
        if combine not in COMBINE_MODES:
            raise ConfigError(
                f"backtest config {source}: combine {combine!r} not in "
                f"{list(COMBINE_MODES)}"
            )
        min_score = signal.get("min_score")
        if min_score is not None:
            min_score = float(min_score)
        min_scores_raw = signal.get("min_scores", {})
        if not isinstance(min_scores_raw, dict):
            raise ConfigError(
                f"backtest config {source}: [signal.min_scores] must be a "
                "table of bundle-name = floor entries"
            )
        min_scores = {str(k): float(v) for k, v in min_scores_raw.items()}
        model_update = signal.get("model_update", "refit")
        if model_update not in MODEL_UPDATE_POLICIES:
            raise ConfigError(
                f"backtest config {source}: model_update {model_update!r} "
                f"not in {list(MODEL_UPDATE_POLICIES)}"
            )

        filters = tuple(
            FilterSpec.from_table(t, source, "[[filters]]")
            for t in raw.get("filters", ())
        )

        inv_raw = raw.get("investability")
        if inv_raw is None:
            raise ConfigError(
                f"backtest config {source} must state an investability "
                "filter: [[investability]] entries, or the explicit "
                'opt-out investability = "none" (there is no upstream '
                "liquidity floor; an unstated filter is not a default)"
            )
        if inv_raw == "none":
            investability, investability_none = (), True
        elif isinstance(inv_raw, list):
            investability = tuple(
                FilterSpec.from_table(t, source, "[[investability]]")
                for t in inv_raw
            )
            if not investability:
                raise ConfigError(
                    f"backtest config {source}: [[investability]] is empty; "
                    'use investability = "none" to opt out explicitly'
                )
            investability_none = False
        else:
            raise ConfigError(
                f"backtest config {source}: investability must be "
                '[[investability]] tables or the string "none"'
            )

        pf = raw.get("portfolio", {})
        weighting = pf.get("weighting", "score")
        if weighting not in WEIGHTINGS:
            raise ConfigError(
                f"backtest config {source}: weighting {weighting!r} not in "
                f"{list(WEIGHTINGS)}"
            )
        if weighting == "score" and combine == "mean_rank":
            raise ConfigError(
                f"backtest config {source}: weighting = 'score' cannot size "
                "on a mean_rank combination (ranks are not weights); use "
                "weighting = 'equal'"
            )
        top_k = int(pf.get("top_k", 25))
        if top_k < 1:
            raise ConfigError(f"backtest config {source}: top_k must be >= 1")
        monthly_cash = float(pf.get("monthly_cash", 1000.0))
        if monthly_cash <= 0:
            raise ConfigError(
                f"backtest config {source}: monthly_cash must be > 0"
            )

        ex = raw.get("execution", {})
        if "cost_bps" not in ex:
            raise ConfigError(
                f"backtest config {source} lacks [execution] cost_bps — "
                "transaction costs must be stated, even as an explicit 0"
            )
        cost_bps = float(ex["cost_bps"])
        if cost_bps < 0:
            raise ConfigError(f"backtest config {source}: cost_bps must be >= 0")

        window = raw.get("window", {})
        def _date(key):
            v = window.get(key)
            if v is None:
                return None
            if not isinstance(v, date):
                raise ConfigError(
                    f"backtest config {source}: window {key} must be a TOML "
                    f"date, got {v!r}"
                )
            return v

        config = cls(
            name=str(raw.get("name", "")),
            dataset_version=str(raw["dataset_version"]),
            prices_version=str(raw["prices_version"]),
            bundles=bundles,
            combine=combine,
            min_score=min_score,
            min_scores=min_scores,
            model_update=model_update,
            label_lag_days=int(signal.get("label_lag_days", 45)),
            max_staleness_days=int(signal.get("max_staleness_days", 200)),
            filters=filters,
            investability=investability,
            investability_none=investability_none,
            strategy=str(pf.get("strategy", "buy_and_hold")),
            top_k=top_k,
            weighting=weighting,
            monthly_cash=monthly_cash,
            cost_bps=cost_bps,
            benchmark_cost_bps=float(ex.get("benchmark_cost_bps", 0.0)),
            max_quote_age_days=int(ex.get("max_quote_age_days", 0)),
            delist_after_days=int(ex.get("delist_after_days", 30)),
            fractional_shares=bool(ex.get("fractional_shares", False)),
            start=_date("start"),
            end=_date("end"),
            valuation_end=_date("valuation_end"),
        )
        if config.max_staleness_days < 1:
            raise ConfigError(
                f"backtest config {source}: max_staleness_days must be >= 1"
            )
        if not config.name:
            config = replace(config, name=config.derived_name())
        return config

    def derived_name(self) -> str:
        return (
            f"portfolio_{self.strategy}_{self.combine}_top{self.top_k}"
            f"_{self.identity_hash}"
        )

    def _canonical_payload(self) -> dict:
        # fields added after the first release are serialized only when
        # they differ from the behavior-preserving default, so existing
        # configs keep their hashes in the trial ledger
        added = {}
        if self.min_scores:
            added["min_scores"] = dict(sorted(self.min_scores.items()))
        if self.model_update != "refit":
            added["model_update"] = self.model_update
        if self.label_lag_days != 45:
            added["label_lag_days"] = self.label_lag_days
        if self.fractional_shares:
            added["fractional_shares"] = True
        return {
            **added,
            "name": self.name,
            "dataset_version": self.dataset_version,
            "prices_version": self.prices_version,
            "bundles": list(self.bundles),
            "combine": self.combine,
            "min_score": self.min_score,
            "max_staleness_days": self.max_staleness_days,
            "filters": [f.to_table() for f in self.filters],
            "investability": (
                "none"
                if self.investability_none
                else [f.to_table() for f in self.investability]
            ),
            "strategy": self.strategy,
            "top_k": self.top_k,
            "weighting": self.weighting,
            "monthly_cash": self.monthly_cash,
            "cost_bps": self.cost_bps,
            "benchmark_cost_bps": self.benchmark_cost_bps,
            "max_quote_age_days": self.max_quote_age_days,
            "delist_after_days": self.delist_after_days,
            "start": self.start.isoformat() if self.start else None,
            "end": self.end.isoformat() if self.end else None,
            "valuation_end": (
                self.valuation_end.isoformat() if self.valuation_end else None
            ),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self._canonical_payload(), sort_keys=True, separators=(",", ":")
        )

    @property
    def config_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()[:16]

    @property
    def identity_hash(self) -> str:
        payload = self._canonical_payload()
        del payload["name"]
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:8]
