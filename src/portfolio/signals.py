"""Scoring a point-in-time cross-section with walk-forward fold models.

A `ModelSet` is the backtest's stand-in for the deployed multi-model
`vml-predict` run: the same bundles' *training configurations*, but the
model applied at a trade date is the walk-forward fold model of the trade
date's year — fitted on an expanding window that ends, purged and
embargoed, before that year begins. Deployment bundles are refused
structurally (`ModelBundle.load` rejects the kind): a model refit on all
labeled history has seen the backtest period, and scoring it there is
leakage, not measurement.

Filters are declared, validated column screens over the feature/rank
groups only — a filter can never reference a label, and a column the
manifest doesn't declare is an error, not an empty screen. NULL fails
every filter: missingness never passes a screen.
"""

from __future__ import annotations

import operator
from pathlib import Path

import pandas as pd

from harness.dataset import SELECTION_SCHEME, Dataset
from harness.errors import ConfigError, DatasetValidationError
from harness.model_store import ModelBundle, ModelBundleError
from portfolio.config import BacktestConfig, FilterSpec

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


class ModelSet:
    """The walk-forward fold models of several training runs, keyed by
    (bundle, trade year)."""

    def __init__(self, bundle_dirs: list[str | Path]):
        if not bundle_dirs:
            raise ConfigError("a backtest needs at least one model bundle")
        self.bundle_dirs = [Path(d) for d in bundle_dirs]
        self.bundles = [ModelBundle.load(d) for d in self.bundle_dirs]
        for d, b in zip(self.bundle_dirs, self.bundles):
            if b.train_config.scheme != SELECTION_SCHEME:
                raise ModelBundleError(
                    f"{d} was trained under scheme "
                    f"{b.train_config.scheme!r}; backtests may only consume "
                    f"{SELECTION_SCHEME!r} fold models"
                )
        self.names = _column_names(self.bundles)

    @property
    def score_columns(self) -> list[str]:
        return [f"score_{n}" for n in self.names]

    def common_fold_years(self) -> list[int]:
        """Trade years every bundle has a fold model for."""
        common = set(self.bundles[0].fold_models)
        for b in self.bundles[1:]:
            common &= set(b.fold_models)
        return sorted(common)

    def validate_against(self, config: BacktestConfig, dataset: Dataset) -> None:
        for d, b in zip(self.bundle_dirs, self.bundles):
            trained_on = b.train_config.dataset_version
            if trained_on != config.dataset_version:
                raise ConfigError(
                    f"bundle {d} was trained on {trained_on!r} but the "
                    f"backtest pins {config.dataset_version!r}; results "
                    "across dataset versions are never compared — retrain "
                    "or re-pin"
                )
            missing = sorted(set(b.feature_columns) - set(dataset.data.columns))
            if missing:
                raise DatasetValidationError(
                    f"dataset {dataset.version} lacks feature columns bundle "
                    f"{d} was trained on: {missing}"
                )
            if config.min_score is not None and not b.probabilistic:
                raise ConfigError(
                    f"min_score is set but bundle {d} is not probabilistic — "
                    "raw margins have no common scale to threshold"
                )
            if config.combine in ("product", "mean", "min") and not b.probabilistic:
                raise ConfigError(
                    f"combine = {config.combine!r} needs probabilistic "
                    f"scores but bundle {d} is not probabilistic; use "
                    "combine = 'mean_rank'"
                )

    def score(self, frame: pd.DataFrame, year: int) -> pd.DataFrame:
        """`frame` plus one `score_<name>` column per bundle, scored by
        each bundle's fold-`year` model."""
        out = frame.copy()
        for d, b, name in zip(self.bundle_dirs, self.bundles, self.names):
            if year not in b.fold_models:
                raise ConfigError(
                    f"bundle {d} has no fold model for trade year {year} "
                    f"(folds: {b.folds}) — the backtest window must stay "
                    "inside every bundle's fold years"
                )
            missing = sorted(set(b.feature_columns) - set(frame.columns))
            if missing:
                raise DatasetValidationError(
                    f"cross-section lacks feature columns bundle {d} needs: "
                    f"{missing}"
                )
            model = b.fold_models[year]
            out[f"score_{name}"] = model.predict_scores(
                frame[list(b.feature_columns)]
            )
        return out


def _column_names(bundles: list[ModelBundle]) -> list[str]:
    """One unique suffix per bundle: the config name, disambiguated by
    run_id when two bundles share one (mirrors vml-predict's CSVs)."""
    names = [b.train_config.name for b in bundles]
    return [
        f"{name}_{b.run_id}" if names.count(name) > 1 else name
        for name, b in zip(names, bundles)
    ]


def validate_filter_columns(
    filters: tuple[FilterSpec, ...], dataset: Dataset, where: str
) -> None:
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


def apply_filters(
    frame: pd.DataFrame, filters: tuple[FilterSpec, ...]
) -> pd.DataFrame:
    """Rows passing every filter. NULL fails: a stock with no value for a
    screened column is screened out, never waved through."""
    if not filters:
        return frame
    mask = pd.Series(True, index=frame.index)
    for f in filters:
        col = frame[f.column]
        mask &= col.notna() & _OPS[f.op](col, f.value)
    return frame[mask]


def apply_min_score(
    frame: pd.DataFrame, score_columns: list[str], min_score: float | None
) -> pd.DataFrame:
    """Rows where every model's score exceeds the floor."""
    if min_score is None:
        return frame
    mask = pd.Series(True, index=frame.index)
    for col in score_columns:
        mask &= frame[col] > min_score
    return frame[mask]


def combine_scores(
    frame: pd.DataFrame, score_columns: list[str], mode: str
) -> pd.Series:
    """Collapse per-model scores into one ranking/sizing score (higher is
    better in every mode). `product` is the AllProb combination: the
    scores are *not* independent, so the product is a conviction ranking,
    not a joint probability — reports say so."""
    scores = frame[score_columns]
    if mode == "product":
        return scores.prod(axis=1)
    if mode == "mean":
        return scores.mean(axis=1)
    if mode == "min":
        return scores.min(axis=1)
    if mode == "mean_rank":
        ranks = pd.DataFrame(
            {c: scores[c].rank(ascending=False, method="min") for c in scores}
        )
        return -ranks.mean(axis=1)
    raise ConfigError(f"unknown combine mode {mode!r}")
