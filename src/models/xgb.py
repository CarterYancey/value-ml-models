"""Phase-3 models: gradient-boosted trees (XGBoost) — the GPU path.

Same harness protocol as the LightGBM wrappers: weighted `fit` that
refuses to run without `sample_weight_{H}y`, native NaN routing (no
imputation), no early stopping (a local validation split would violate
invariant 1 — boosting rounds are tuned across the walk-forward folds).
Two wrappers: `XGBoostModel` (classifier, scores are positive-class
probabilities) and `XGBoostRegressorModel` (the regression reframe —
continuous `fwd_*` targets, binary `eval_label`, quantile objective as
the pessimistic-ranking option).

Why a second boosted family: XGBoost's `device = "cuda"` works straight
from the stock PyPI wheel (no custom build, unlike LightGBM's CUDA
path) and is typically the largest GPU speedup available for this data
shape. Two guarantees around that:

- GPU histogram arithmetic differs slightly from CPU, so `device` is a
  model param — CPU and GPU runs hash as distinct configs and are never
  mixed in the trial ledger (same rule as the LightGBM wrappers).
- XGBoost silently falls back to CPU when no GPU is visible (at
  `verbosity = 0` it does not even warn). Silent fallback would log a
  CPU fit under a cuda config hash, so after every non-cpu fit the
  wrapper reads the fitted booster's own config and refuses with a
  ConfigError if the device that actually trained differs from the one
  the config named.

Precision knob: XGBoost has no per-class weight dict; the numeric
`class_weight` maps to `scale_pos_weight` (positives weighted `w` vs.
1 — identical semantics to `models.common.resolve_class_weight`, and
`w < 1` still makes false positives relatively more expensive).
`"balanced"` computes Σw_neg / Σw_pos from the fold's own training
rows and uniqueness weights (fold-internal, like sklearn's).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from harness.errors import ConfigError, MissingSampleWeightError
from models.baselines import _require_weights
from models.common import resolve_class_weight

#: XGBoost `device` values the wrappers accept. "cuda" works from the
#: stock PyPI wheel — no custom build needed.
XGB_DEVICES = ("cpu", "cuda")

#: config objective -> XGBoost objective. Quantile with a low alpha
#: ranks by a pessimistic return estimate (see the LightGBM regressor);
#: absoluteerror is the robust-loss option against the extreme-return
#: tail.
XGB_REGRESSION_OBJECTIVES = {
    "squarederror": "reg:squarederror",
    "absoluteerror": "reg:absoluteerror",
    "quantile": "reg:quantileerror",
}


def _xgb_classifier():
    try:
        from xgboost import XGBClassifier
    except ImportError as exc:  # pragma: no cover - env without xgboost
        raise ConfigError(
            "model 'xgboost' requires the xgboost package "
            "(`uv sync` installs it; it is a project dependency)"
        ) from exc
    return XGBClassifier


def _xgb_regressor():
    try:
        from xgboost import XGBRegressor
    except ImportError as exc:  # pragma: no cover - env without xgboost
        raise ConfigError(
            "model 'xgboost_regressor' requires the xgboost package "
            "(`uv sync` installs it; it is a project dependency)"
        ) from exc
    return XGBRegressor


def _check_device(model_name: str, device: str) -> str:
    if device not in XGB_DEVICES:
        raise ConfigError(
            f"{model_name} device must be one of {list(XGB_DEVICES)}, "
            f"got {device!r}"
        )
    return device


def _fit_guarding_device(estimator, X, y, w, device: str):
    """`estimator.fit`, refusing XGBoost's silent GPU→CPU fallback.

    A cuda config that actually trained on CPU would be logged under
    the cuda hash — a provenance lie. XGBoost downgrades with at most a
    warning (none at verbosity 0), so the check reads the *fitted*
    booster's saved config: `learner.generic_param.device` records what
    actually trained ("cpu" after a fallback, "cuda"/"cuda:0" on a
    GPU). If a future xgboost stops exposing it, the check skips rather
    than failing good fits."""
    estimator.fit(X, y, sample_weight=w)
    if device == "cpu":
        return
    try:
        config = json.loads(estimator.get_booster().save_config())
        actual = config["learner"]["generic_param"]["device"]
    except (KeyError, TypeError, ValueError):  # pragma: no cover
        return
    if actual != device and not str(actual).startswith(f"{device}:"):
        raise ConfigError(
            f"device = {device!r} was requested but XGBoost actually "
            f"trained on {actual!r} (no usable GPU is visible, and "
            "XGBoost falls back silently) — refusing so a CPU fit is "
            "never logged under a cuda config. Set device = \"cpu\" on "
            "this machine, or fix the CUDA driver/runtime."
        )


class XGBoostModel:
    """`XGBClassifier` (hist) under the harness protocol."""

    probabilistic = True

    def __init__(
        self,
        n_estimators: int = 300,
        learning_rate: float = 0.05,
        max_depth: int = 6,
        min_child_weight: float = 1.0,
        gamma: float = 0.0,
        subsample: float = 1.0,
        colsample_bytree: float = 1.0,
        reg_alpha: float = 0.0,
        reg_lambda: float = 1.0,
        class_weight: str | float | None = None,
        device: str = "cpu",
        seed: int = 0,
    ):
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"xgboost n_estimators must be a positive integer, "
                f"got {n_estimators!r}"
            )
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                f"xgboost max_depth must be a positive integer, "
                f"got {max_depth!r}"
            )
        self.device = _check_device("xgboost", device)
        #: validated once here (same accepted values/errors as every
        #: other classifier); turned into scale_pos_weight at fit time
        self._class_weight = resolve_class_weight(class_weight)
        self.estimator_ = _xgb_classifier()(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            gamma=gamma,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            tree_method="hist",
            device=self.device,
            importance_type="gain",
            random_state=seed,
            n_jobs=-1,
            verbosity=0,
        )
        self.feature_names_: list[str] | None = None
        #: constant score when the training cell is single-class
        #: (XGBoost refuses to fit one-class problems)
        self.constant_score_: float | None = None

    def _scale_pos_weight(self, y: np.ndarray, w: np.ndarray) -> float:
        if self._class_weight is None:
            return 1.0
        if self._class_weight == "balanced":
            pos = float(w[y].sum())
            neg = float(w[~y].sum())
            return neg / pos if pos > 0 else 1.0
        return float(self._class_weight[True])

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
        self.estimator_.set_params(
            scale_pos_weight=self._scale_pos_weight(yb, w)
        )
        _fit_guarding_device(
            self.estimator_, X, yb.astype(int), w, self.device
        )
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if self.feature_names_ is None:
            raise RuntimeError("fit before predict")
        if self.constant_score_ is not None:
            return np.full(len(X), self.constant_score_)
        proba = self.estimator_.predict_proba(X[self.feature_names_])
        classes = list(self.estimator_.classes_)
        return proba[:, classes.index(1)]

    def feature_importances(self) -> np.ndarray | None:
        if self.feature_names_ is None or self.constant_score_ is not None:
            return None
        imp = np.asarray(self.estimator_.feature_importances_, dtype=float)
        return imp if imp.sum() > 0 else None


class XGBoostRegressorModel:
    """`XGBRegressor` on a continuous forward-return target — the
    regression reframe under the harness protocol (see
    `models.gbm.LightGBMRegressorModel`; the semantics of `eval_label`,
    `winsorize`, and quantile ranking are identical)."""

    probabilistic = False
    target = "continuous"

    def __init__(
        self,
        n_estimators: int = 300,
        learning_rate: float = 0.05,
        max_depth: int = 6,
        min_child_weight: float = 1.0,
        gamma: float = 0.0,
        subsample: float = 1.0,
        colsample_bytree: float = 1.0,
        reg_alpha: float = 0.0,
        reg_lambda: float = 1.0,
        objective: str = "squarederror",
        alpha: float = 0.9,
        winsorize: float = 0.0,
        device: str = "cpu",
        seed: int = 0,
    ):
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"xgboost_regressor n_estimators must be a positive "
                f"integer, got {n_estimators!r}"
            )
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                f"xgboost_regressor max_depth must be a positive integer, "
                f"got {max_depth!r}"
            )
        if objective not in XGB_REGRESSION_OBJECTIVES:
            raise ConfigError(
                f"xgboost_regressor objective must be one of "
                f"{sorted(XGB_REGRESSION_OBJECTIVES)}, got {objective!r}"
            )
        if not 0.0 < float(alpha) < 1.0:
            raise ConfigError(
                f"xgboost_regressor alpha must be in (0, 1), got {alpha!r}"
            )
        if not 0.0 <= float(winsorize) < 0.5:
            raise ConfigError(
                f"xgboost_regressor winsorize must be in [0, 0.5), "
                f"got {winsorize!r}"
            )
        self.device = _check_device("xgboost_regressor", device)
        self.winsorize = float(winsorize)
        quantile = objective == "quantile"
        self.estimator_ = _xgb_regressor()(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            gamma=gamma,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            objective=XGB_REGRESSION_OBJECTIVES[objective],
            **({"quantile_alpha": float(alpha)} if quantile else {}),
            tree_method="hist",
            device=self.device,
            importance_type="gain",
            random_state=seed,
            n_jobs=-1,
            verbosity=0,
        )
        self.feature_names_: list[str] | None = None
        #: training-target clip bounds actually applied (None when
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
                "xgboost_regressor got NaN training targets; unlabeled "
                "rows must be excluded before fit"
            )
        if self.winsorize > 0.0:
            lo, hi = np.quantile(yf, [self.winsorize, 1.0 - self.winsorize])
            self.winsor_bounds_ = (float(lo), float(hi))
            yf = np.clip(yf, lo, hi)
        else:
            self.winsor_bounds_ = None
        _fit_guarding_device(self.estimator_, X, yf, w, self.device)
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
        imp = np.asarray(self.estimator_.feature_importances_, dtype=float)
        return imp if imp.sum() > 0 else None
