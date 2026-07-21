"""Phase-1 model: a single depth-limited decision tree (sklearn).

Interpretability is the point (PLAN §2): the fitted tree is exported as
human-readable rules and a diagram by `explain.rules`. The wrapper
implements the harness model protocol — a weighted `fit` that refuses to
run without the horizon's `sample_weight_{H}y`, and `predict_scores`
returning leaf-frequency probabilities.

- Depth is always limited (`max_depth` is required, not defaulted): an
  unbounded tree is neither interpretable nor honest at these sample
  sizes.
- NULLs are meaningful upstream; sklearn's native missing-value support
  routes NaN at each split (no imputation anywhere).
- `class_weight="balanced"` is available for heavily imbalanced cells;
  sklearn multiplies it into the uniqueness weights, which stay mandatory.
- Scores are leaf frequencies: probabilistic in form, but single trees
  are poorly calibrated — a known Phase-1 limitation (PLAN §2), which is
  exactly what the calibration curve in the report makes visible.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from harness.errors import ConfigError, MissingSampleWeightError
from models.baselines import _require_weights


class DecisionTreeModel:
    """Depth-limited `DecisionTreeClassifier` under the harness protocol."""

    probabilistic = True

    def __init__(
        self,
        max_depth: int,
        min_weight_fraction_leaf: float = 0.01,
        class_weight: str | None = None,
        criterion: str = "gini",
        seed: int = 0,
    ):
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                "decision_tree requires an explicit integer max_depth >= 1; "
                "an unbounded tree is neither interpretable nor honest"
            )
        if class_weight not in (None, "balanced"):
            raise ConfigError(
                f"class_weight must be 'balanced' or absent, got {class_weight!r}"
            )
        self.estimator_ = DecisionTreeClassifier(
            max_depth=max_depth,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            class_weight=class_weight,
            criterion=criterion,
            random_state=seed,
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
