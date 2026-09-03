"""Multiclass model wrappers for the registered diagnostics.

The harness models (`models/*`) are binary by construction — they cast
the target to bool and score the positive class. The era probe predicts
a calendar year, so it needs the same estimators under a multiclass
protocol:

    fit(X, y, sample_weight)      # weights mandatory, as everywhere
    predict_proba(X) -> (n, k)    # columns aligned to `classes_`
    classes_                      # sorted distinct training targets
    feature_importances()         # pd.Series indexed by feature name

Model names match the binary registry (`decision_tree`, `random_forest`,
`lightgbm`, `xgboost`) and reuse its parameter allowlists (including the
GPU `device` knob, with the same build/device guards), so an experiment's
`[model]` table can be probed verbatim. Nothing here is used by the
ordinary runner. NaN routes natively in every estimator — no imputation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from harness.errors import ConfigError, MissingSampleWeightError
from models import gbm, xgb
from models.baselines import _require_weights
from models.registry import (
    _FOREST_PARAMS,
    _LIGHTGBM_PARAMS,
    _TREE_PARAMS,
    _XGBOOST_PARAMS,
    _reject_extra,
)

PROBE_MODELS = ("decision_tree", "random_forest", "lightgbm", "xgboost")


def _probe_class_weight(class_weight, *, extra_modes: tuple[str, ...] = ()):
    """Only `None` or `"balanced"` (plus estimator-specific modes): the
    binary positive-class weight knob has no meaning for a year target."""
    if class_weight is None:
        return None
    if class_weight in ("balanced", *extra_modes):
        return class_weight
    raise ConfigError(
        f"class_weight {class_weight!r} is not valid for a multiclass probe; "
        f"use None or one of {['balanced', *extra_modes]}"
    )


class _MulticlassBase:
    """Shared fit/predict mechanics; subclasses build `estimator_`."""

    importance_kind = "impurity"

    def __init__(self):
        self.estimator_ = None
        self.feature_names_: list[str] | None = None
        self.classes_: np.ndarray | None = None
        #: set when the training set has a single class — the estimator
        #: is not fitted (LightGBM refuses one-class problems) and every
        #: row is predicted as that class
        self.constant_class_: int | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        if len(w) != len(X):
            raise MissingSampleWeightError(
                f"sample_weight length {len(w)} != rows {len(X)}"
            )
        yi = np.asarray(y, dtype=int)
        if len(yi) != len(X):
            raise ValueError(f"target length {len(yi)} != rows {len(X)}")
        self.feature_names_ = list(X.columns)
        uniq = np.unique(yi)
        if len(uniq) < 2:
            self.constant_class_ = int(uniq[0]) if len(uniq) else None
            self.classes_ = uniq.astype(int)
            return self
        self.constant_class_ = None
        self._fit_estimator(X, yi, w)
        return self

    def _fit_estimator(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray) -> None:
        self.estimator_.fit(X, y, sample_weight=w)
        self.classes_ = np.asarray(self.estimator_.classes_, dtype=int)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.feature_names_ is None or self.classes_ is None:
            raise RuntimeError("fit before predict")
        if self.constant_class_ is not None:
            return np.ones((len(X), 1))
        return np.asarray(
            self.estimator_.predict_proba(X[self.feature_names_]), dtype=float
        )

    def feature_importances(self) -> pd.Series:
        if self.feature_names_ is None:
            raise RuntimeError("fit before importances")
        if self.constant_class_ is not None:
            values = np.zeros(len(self.feature_names_))
        else:
            values = np.asarray(self.estimator_.feature_importances_, dtype=float)
            total = values.sum()
            if total > 0:
                values = values / total  # LightGBM gain is unnormalised
        return pd.Series(values, index=self.feature_names_, name="importance")


class MulticlassTreeModel(_MulticlassBase):
    """Depth-limited `DecisionTreeClassifier`, multiclass; `max_depth` is
    mandatory for the same reason as in `models.tree`: the extracted rules
    are the deliverable (which features identify which years)."""

    def __init__(
        self,
        max_depth: int,
        min_weight_fraction_leaf: float = 0.01,
        class_weight: str | None = None,
        criterion: str = "gini",
        splitter: str = "best",
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        max_features: int | float | str | None = None,
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
        seed: int = 0,
    ):
        super().__init__()
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                "decision_tree requires an explicit integer max_depth >= 1; "
                "an unbounded tree is neither interpretable nor honest"
            )
        self.estimator_ = DecisionTreeClassifier(
            max_depth=max_depth,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            class_weight=_probe_class_weight(class_weight),
            criterion=criterion,
            splitter=splitter,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_decrease=min_impurity_decrease,
            ccp_alpha=ccp_alpha,
            random_state=seed,
        )


class MulticlassForestModel(_MulticlassBase):
    """`RandomForestClassifier`, multiclass."""

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int | None = None,
        min_weight_fraction_leaf: float = 0.0,
        min_samples_leaf: int = 1,
        min_samples_split: int = 2,
        max_features: int | float | str | None = "sqrt",
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
        class_weight: str | None = None,
        criterion: str = "gini",
        bootstrap: bool = True,
        max_samples: float | None = None,
        n_jobs: int = -1,
        seed: int = 0,
    ):
        super().__init__()
        self.estimator_ = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            min_samples_leaf=min_samples_leaf,
            min_samples_split=min_samples_split,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_decrease=min_impurity_decrease,
            ccp_alpha=ccp_alpha,
            class_weight=_probe_class_weight(
                class_weight, extra_modes=("balanced_subsample",)
            ),
            criterion=criterion,
            bootstrap=bootstrap,
            max_samples=max_samples,
            random_state=seed,
            n_jobs=n_jobs,
        )


class MulticlassLightGBMModel(_MulticlassBase):
    """`LGBMClassifier(objective="multiclass")`; importances are split
    gain, normalised to sum to one."""

    importance_kind = "gain"

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
        class_weight: str | None = None,
        device: str = "cpu",
        seed: int = 0,
    ):
        super().__init__()
        self.device = gbm._check_device("lightgbm", device)
        LGBMClassifier = gbm._lgbm_classifier()
        self.estimator_ = LGBMClassifier(
            objective="multiclass",
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
            class_weight=_probe_class_weight(class_weight),
            importance_type="gain",
            device_type=self.device,
            random_state=seed,
            n_jobs=-1,
            verbosity=-1,
        )

    def _fit_estimator(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray) -> None:
        gbm._fit_or_explain_device(self.estimator_, X, y, w, self.device)
        self.classes_ = np.asarray(self.estimator_.classes_, dtype=int)


class MulticlassXGBoostModel(_MulticlassBase):
    """`XGBClassifier(objective="multi:softprob")`. XGBoost wants labels
    0..k-1, so years are encoded at fit and decoded through `classes_`;
    `class_weight = "balanced"` is applied by rescaling the sample
    weights (XGBoost has no class-weight dict). Same `device` guards as
    `models.xgb`."""

    importance_kind = "gain"

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
        class_weight: str | None = None,
        device: str = "cpu",
        seed: int = 0,
    ):
        super().__init__()
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"xgboost n_estimators must be a positive integer, "
                f"got {n_estimators!r}"
            )
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                f"xgboost max_depth must be a positive integer, got {max_depth!r}"
            )
        self.device = xgb._check_device("xgboost", device)
        self.balanced = _probe_class_weight(class_weight) == "balanced"
        self.estimator_ = xgb._xgb_classifier()(
            objective="multi:softprob",
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

    def _fit_estimator(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray) -> None:
        classes, encoded = np.unique(y, return_inverse=True)
        if self.balanced:
            # sklearn's "balanced": n / (k * n_c), here on weight mass
            mass = np.array([w[encoded == i].sum() for i in range(len(classes))])
            w = w * (w.sum() / (len(classes) * mass[encoded]))
        xgb._fit_guarding_device(self.estimator_, X, encoded, w, self.device)
        self.classes_ = classes.astype(int)


def build_probe_model(name: str, params: dict, seed: int):
    """Config `[model]` table → multiclass probe model."""
    if name == "decision_tree":
        _reject_extra(name, params, allowed=_TREE_PARAMS)
        if "max_depth" not in params:
            raise ConfigError(
                "decision_tree requires max_depth in the config; "
                "depth-limiting is not optional"
            )
        return MulticlassTreeModel(seed=seed, **params)
    if name == "random_forest":
        _reject_extra(name, params, allowed=_FOREST_PARAMS)
        return MulticlassForestModel(seed=seed, **params)
    if name == "lightgbm":
        _reject_extra(name, params, allowed=_LIGHTGBM_PARAMS)
        return MulticlassLightGBMModel(seed=seed, **params)
    if name == "xgboost":
        _reject_extra(name, params, allowed=_XGBOOST_PARAMS)
        return MulticlassXGBoostModel(seed=seed, **params)
    raise ConfigError(
        f"unknown probe model {name!r}; the era probe supports "
        f"{list(PROBE_MODELS)} (the trivial baselines are computed by the "
        "probe itself: uniform chance, majority year, train prior)"
    )
