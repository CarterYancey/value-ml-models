"""Phase-3 models: gradient-boosted trees (LightGBM), per PLAN §4.

Two wrappers share the harness protocol: `LightGBMModel` (classifier,
scores are positive-class probabilities) and `LightGBMRegressorModel`
(the regression reframe of PLAN §8 — trained on a continuous forward
return like `fwd_3y_cagr`, scores are predicted returns/quantiles used
as a ranking; metrics come from a separate binary `eval_label`).
`fit` refuses to run without the horizon's `sample_weight_{H}y`;
LightGBM handles NaN natively (missing values route at each split) — no
imputation anywhere.

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


def _lgbm_regressor():
    try:
        from lightgbm import LGBMRegressor
    except ImportError as exc:  # pragma: no cover - env without lightgbm
        raise ConfigError(
            "model 'lightgbm_regressor' requires the lightgbm package "
            "(`uv sync` installs it; it is a project dependency)"
        ) from exc
    return LGBMRegressor


def _gain_importances(estimator, n_features: int) -> np.ndarray | None:
    """Normalized gain importances from a fitted LightGBM estimator
    (fraction of total split gain per feature; sums to 1)."""
    booster = getattr(estimator, "booster_", None)
    if booster is None:
        return None
    gains = np.asarray(
        booster.feature_importance(importance_type="gain"), dtype=float
    )
    if len(gains) != n_features or gains.sum() <= 0:
        return None
    return gains / gains.sum()


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

    def feature_importances(self) -> np.ndarray | None:
        if self.feature_names_ is None or self.constant_score_ is not None:
            return None
        return _gain_importances(self.estimator_, len(self.feature_names_))


#: Objectives lightgbm_regressor accepts. `quantile` with a low alpha
#: (e.g. 0.25) ranks by a *pessimistic* return estimate — a natural
#: precision-first ranking; `huber` damps the extreme-return tail that
#: dominates 1y CAGR variance.
REGRESSION_OBJECTIVES = ("regression", "regression_l1", "huber", "quantile")


class LightGBMRegressorModel:
    """`LGBMRegressor` on a continuous forward-return target.

    The regression reframe (PLAN §8): train on `fwd_{H}y_cagr` /
    `fwd_{H}y_excess_cagr`, use the predicted return (or quantile) as
    the ranking score, and evaluate in the same precision@K frame
    against a binary `eval_label` from the upstream label matrix.
    Scores are NOT probabilities (`probabilistic = False`): no Brier or
    calibration, and any `score_thresholds` are on the CAGR scale.

    `winsorize = q` clips the *training* target to its [q, 1-q]
    quantiles, computed on each fold's own training rows only —
    fold-internal by construction, disclosed in the config/report. The
    upstream caveat motivating it: 1y label variance is dominated by a
    few extreme returns. Test-side labels are never touched.
    """

    probabilistic = False
    #: harness marker: this model consumes a continuous label column
    target = "continuous"

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
        objective: str = "regression",
        alpha: float = 0.9,
        winsorize: float = 0.0,
        seed: int = 0,
    ):
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"lightgbm_regressor n_estimators must be a positive "
                f"integer, got {n_estimators!r}"
            )
        if not isinstance(num_leaves, int) or num_leaves < 2:
            raise ConfigError(
                f"lightgbm_regressor num_leaves must be an integer >= 2, "
                f"got {num_leaves!r}"
            )
        if objective not in REGRESSION_OBJECTIVES:
            raise ConfigError(
                f"lightgbm_regressor objective must be one of "
                f"{list(REGRESSION_OBJECTIVES)}, got {objective!r}"
            )
        if not 0.0 < float(alpha) < 1.0:
            raise ConfigError(
                f"lightgbm_regressor alpha must be in (0, 1), got {alpha!r}"
            )
        if not 0.0 <= float(winsorize) < 0.5:
            raise ConfigError(
                f"lightgbm_regressor winsorize must be in [0, 0.5), "
                f"got {winsorize!r}"
            )
        self.winsorize = float(winsorize)
        self.estimator_ = _lgbm_regressor()(
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
            objective=objective,
            alpha=float(alpha),
            random_state=seed,
            n_jobs=-1,
            verbosity=-1,
        )
        self.feature_names_: list[str] | None = None
        #: the training-target clip bounds actually applied (None when
        #: winsorize = 0) — recorded for disclosure
        self.winsor_bounds_: tuple[float, float] | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        if len(w) != len(X):
            raise MissingSampleWeightError(
                f"sample_weight length {len(w)} != rows {len(X)}"
            )
        self.feature_names_ = list(X.columns)
        yf = np.asarray(y, dtype=float)
        if np.isnan(yf).any():
            raise ConfigError(
                "lightgbm_regressor got NaN training targets; unlabeled "
                "rows must be excluded before fit"
            )
        if self.winsorize > 0.0:
            lo, hi = np.quantile(yf, [self.winsorize, 1.0 - self.winsorize])
            self.winsor_bounds_ = (float(lo), float(hi))
            yf = np.clip(yf, lo, hi)
        else:
            self.winsor_bounds_ = None
        self.estimator_.fit(X, yf, sample_weight=w)
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if self.feature_names_ is None:
            raise RuntimeError("fit before predict")
        return np.asarray(
            self.estimator_.predict(X[self.feature_names_]), dtype=float
        )

    def feature_importances(self) -> np.ndarray | None:
        if self.feature_names_ is None:
            return None
        return _gain_importances(self.estimator_, len(self.feature_names_))
