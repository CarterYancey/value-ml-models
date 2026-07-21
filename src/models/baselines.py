"""Trivial baselines every reported result must be compared against.

All three implement the harness model protocol: a weighted `fit` (which
refuses to run without sample weights — the guardrail applies to baselines
too) and `predict_scores` returning a per-row ranking score, higher =
more likely positive. `probabilistic` declares whether scores are
calibrated probabilities (Brier is only meaningful when they are).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from harness.errors import ConfigError, MissingSampleWeightError


def _require_weights(sample_weight) -> np.ndarray:
    if sample_weight is None:
        raise MissingSampleWeightError(
            "fit called without sample weights; pass the horizon's "
            "sample_weight_{H}y"
        )
    w = np.asarray(sample_weight, dtype=float)
    if len(w) == 0 or np.isnan(w).any():
        raise MissingSampleWeightError("sample weights are empty or contain NaN")
    return w


class MajorityClassBaseline:
    """Predict the (weighted) majority class; score every row with the
    weighted positive prevalence, so its Brier score is that of the best
    constant predictor."""

    probabilistic = True

    def __init__(self):
        self.prevalence_: float | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        y = np.asarray(y, dtype=float)
        self.prevalence_ = float(np.average(y, weights=w))
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if self.prevalence_ is None:
            raise RuntimeError("fit before predict")
        return np.full(len(X), self.prevalence_)


class RankFactorBaseline:
    """Rank by a single upstream rank column (e.g. `book_to_market_rank`,
    `earnings_yield_rank`). No parameters are learned; `fit` only records
    the training prevalence for reference and enforces the weight
    guardrail. NULL ranks (rank guard, missing raw value) sort last."""

    probabilistic = False

    def __init__(self, rank_column: str, higher_is_better: bool = True):
        if not rank_column:
            raise ConfigError("rank_factor baseline requires a rank_column")
        self.rank_column = rank_column
        self.higher_is_better = higher_is_better
        self.prevalence_: float | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        if self.rank_column not in X.columns:
            raise ConfigError(
                f"rank column {self.rank_column!r} not among the selected "
                "feature columns"
            )
        self.prevalence_ = float(np.average(np.asarray(y, dtype=float), weights=w))
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        raw = X[self.rank_column].to_numpy(dtype=float)
        scores = raw if self.higher_is_better else -raw
        # NULL rank = not rankable at that snapshot; sort last, don't invent.
        return np.where(np.isnan(scores), -np.inf, scores)


class RandomRankingBaseline:
    """Seeded uniform-random scores — the floor for every ranking metric."""

    probabilistic = False

    def __init__(self, seed: int = 0):
        self.seed = seed

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        _require_weights(sample_weight)
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        return rng.uniform(size=len(X))
