"""Phase-3 model: random forest (sklearn), kept explainable via rules
from its constituent trees' importances + SHAP (PLAN §4 Phase 3).

Same harness protocol as the single tree: weighted `fit` that refuses to
run without `sample_weight_{H}y`, `predict_scores` returning the
positive-class probability. sklearn's forests route NaN natively at each
split (scikit-learn ≥ 1.4) — no imputation anywhere.

Averaging over trees makes forest scores smoother and usually better
ranked than a single tree's leaf frequencies, but they are still not
calibrated probabilities; the calibration curve in the report stays the
honest check. The precision knobs are the same as everywhere else:
a float `class_weight < 1` (see `models.common`), higher leaf minima,
and — forest-specific — more trees with feature subsampling
(`max_features`), which reduces the variance of the top of the ranking.

Resource notes (forests are the RAM-hungry family here): fitted tree
size is ~64 bytes x nodes, and node count grows like
2 x n_rows / min_samples_leaf until max_depth caps it — a deep,
small-leaf forest on a full training window (all three snapshot kinds)
is gigabytes *per fit*, and `n_jobs` parallel builders hold their
in-progress trees simultaneously. `max_samples` (per-tree bootstrap
fraction) cuts both build time and tree size roughly linearly and
decorrelates trees as a bonus; `n_jobs` caps concurrency (default -1 =
every core).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from harness.errors import ConfigError, MissingSampleWeightError
from models.baselines import _require_weights
from models.common import resolve_class_weight


class RandomForestModel:
    """`RandomForestClassifier` under the harness protocol."""

    probabilistic = True

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int | None = None,
        min_weight_fraction_leaf: float = 0.0,
        min_samples_leaf: int = 5,
        min_samples_split: int = 2,
        max_features: int | float | str | None = "sqrt",
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
        class_weight: str | float | None = None,
        criterion: str = "gini",
        bootstrap: bool = True,
        max_samples: float | None = None,
        n_jobs: int = -1,
        seed: int = 0,
    ):
        if not isinstance(n_estimators, int) or n_estimators < 1:
            raise ConfigError(
                f"random_forest n_estimators must be a positive integer, "
                f"got {n_estimators!r}"
            )
        if max_depth is not None and (
            not isinstance(max_depth, int) or max_depth < 1
        ):
            raise ConfigError(
                f"random_forest max_depth must be a positive integer or "
                f"absent (unbounded trees are acceptable in an averaged "
                f"ensemble), got {max_depth!r}"
            )
        if max_samples is not None:
            if isinstance(max_samples, bool) or not isinstance(
                max_samples, (int, float)
            ) or not 0.0 < float(max_samples) <= 1.0:
                raise ConfigError(
                    f"random_forest max_samples must be a fraction in "
                    f"(0, 1] or absent (full bootstrap), got {max_samples!r}"
                )
            if not bootstrap:
                raise ConfigError(
                    "random_forest max_samples requires bootstrap = true"
                )
            max_samples = None if max_samples == 1.0 else float(max_samples)
        if not isinstance(n_jobs, int) or isinstance(n_jobs, bool) or n_jobs == 0:
            raise ConfigError(
                f"random_forest n_jobs must be a nonzero integer "
                f"(-1 = all cores), got {n_jobs!r}"
            )
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
            class_weight=resolve_class_weight(
                class_weight, extra_modes=("balanced_subsample",)
            ),
            criterion=criterion,
            bootstrap=bootstrap,
            max_samples=max_samples,
            random_state=seed,
            n_jobs=n_jobs,
        )
        self.feature_names_: list[str] | None = None

    def fit(self, X: pd.DataFrame, y, sample_weight=None):
        w = _require_weights(sample_weight)
        if len(w) != len(X):
            raise MissingSampleWeightError(
                f"sample_weight length {len(w)} != rows {len(X)}"
            )
        self.feature_names_ = list(X.columns)
        self.estimator_.fit(X, np.asarray(y, dtype=bool), sample_weight=w)
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if self.feature_names_ is None:
            raise RuntimeError("fit before predict")
        proba = self.estimator_.predict_proba(X[self.feature_names_])
        classes = list(self.estimator_.classes_)
        if True not in classes:  # degenerate single-class training cell
            return np.zeros(len(X))
        return proba[:, classes.index(True)]

    def feature_importances(self) -> np.ndarray | None:
        """Mean impurity-decrease importances over the ensemble (weighted,
        normalized) — the forest's answer to "which columns matter", and
        the cheap starting point for importance-guided feature subsets."""
        if self.feature_names_ is None:
            return None
        imp = np.asarray(self.estimator_.feature_importances_, dtype=float)
        return imp if imp.sum() > 0 else None
