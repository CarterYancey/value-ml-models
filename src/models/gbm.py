"""Phase-3 model: gradient-boosted trees (LightGBM), per PLAN §4.

Harness protocol as everywhere: `fit` refuses to run without the
horizon's `sample_weight_{H}y`; `predict_scores` returns the
positive-class probability. LightGBM handles NaN natively (missing
values route at each split) — no imputation anywhere.

Design notes:
- **No early stopping / no internal validation split.** Early stopping
  needs a held-out set, and carving one out here would mean constructing
  a split locally — a leakage bug by invariant 1. Boosting rounds
  (`n_estimators`) and `learning_rate` are ordinary hyperparameters,
  tuned like everything else across the upstream walk-forward folds.
- Boosted scores are typically over-confident; post-hoc calibration on a
  purged fold is a separate TODO item. Until then the calibration curve
  in the report is the honest check.
- Precision knobs: numeric `class_weight < 1` (see `models.common`)
  makes false positives relatively more expensive; `min_child_weight` /
  `min_child_samples` and stronger regularization (`reg_alpha`,
  `reg_lambda`) push toward fewer, purer positive regions.
- Import is lazy so the rest of the package works where lightgbm isn't
  installed; using `model.name = "lightgbm"` without it is a clear
  ConfigError, not an ImportError at import time.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from harness.errors import ConfigError, MissingSampleWeightError
from models.baselines import _require_weights
from models.common import resolve_class_weight


def _lgbm_classifier():
    try:
        from lightgbm import LGBMClassifier
    except ImportError as exc:  # pragma: no cover - env without lightgbm
        raise ConfigError(
            "model 'lightgbm' requires the lightgbm package "
            "(`uv sync` installs it; it is a project dependency)"
        ) from exc
    return LGBMClassifier


class LightGBMModel:
    """`LGBMClassifier` under the harness protocol."""

    probabilistic = True

    def __init__(
        self,
        n_estimators: int = 200,
        learning_rate: float = 0.05,
        num_leaves: int = 15,
        max_depth: int = -1,
        min_child_samples: int = 20,
        min_child_weight: float = 1e-3,
        subsample: float = 1.0,
        subsample_freq: int = 0,
        colsample_bytree: float = 1.0,
        reg_alpha: float = 0.0,
        reg_lambda: float = 0.0,
        class_weight: str | float | None = None,
        seed: int = 0,
    ):
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"lightgbm n_estimators must be a positive integer, "
                f"got {n_estimators!r}"
            )
        if not isinstance(num_leaves, int) or num_leaves < 2:
            raise ConfigError(
                f"lightgbm num_leaves must be an integer >= 2, "
                f"got {num_leaves!r}"
            )
        self.estimator_ = _lgbm_classifier()(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            max_depth=max_depth,
            min_child_samples=min_child_samples,
            min_child_weight=min_child_weight,
            subsample=subsample,
            subsample_freq=subsample_freq,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            class_weight=resolve_class_weight(class_weight),
            random_state=seed,
            n_jobs=-1,
            verbosity=-1,
        )
        self.feature_names_: list[str] | None = None
        #: constant score when the training cell is single-class (LightGBM
        #: itself refuses to fit one-class problems)
        self.constant_score_: float | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        if len(w) != len(X):
            raise MissingSampleWeightError(
                f"sample_weight length {len(w)} != rows {len(X)}"
            )
        self.feature_names_ = list(X.columns)
        yb = np.asarray(y, dtype=bool)
        if len(np.unique(yb)) < 2:  # degenerate single-class training cell
            self.constant_score_ = 1.0 if yb.all() and len(yb) else 0.0
            return self
        self.constant_score_ = None
        self.estimator_.fit(X, yb, sample_weight=w)
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if self.feature_names_ is None:
            raise RuntimeError("fit before predict")
        if self.constant_score_ is not None:
            return np.full(len(X), self.constant_score_)
        proba = self.estimator_.predict_proba(X[self.feature_names_])
        classes = list(self.estimator_.classes_)
        return proba[:, classes.index(True)]
