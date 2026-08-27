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
- `class_weight` accepts `"balanced"` for heavily imbalanced cells, or a
  positive float `w` (→ `{True: w, False: 1}`) as the precision knob:
  `w < 1` makes false positives relatively more expensive, so leaves are
  only called positive when very pure (see `models.common`). sklearn
  multiplies class weights into the uniqueness weights, which stay
  mandatory.
- The remaining regularizers (`min_weight_fraction_leaf`,
  `min_samples_leaf`, `max_leaf_nodes`, `min_impurity_decrease`,
  `ccp_alpha`, `max_features`) shape how conservative the tree is;
  raising the leaf minima and pruning harder also pushes toward
  fewer, purer positive leaves — precision over recall.
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
from models.common import resolve_class_weight


class DecisionTreeModel:
    """Depth-limited `DecisionTreeClassifier` under the harness protocol."""

    probabilistic = True

    def __init__(
        self,
        max_depth: int,
        min_weight_fraction_leaf: float = 0.01,
        class_weight: str | float | None = None,
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
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ConfigError(
                "decision_tree requires an explicit integer max_depth >= 1; "
                "an unbounded tree is neither interpretable nor honest"
            )
        if not 0.0 <= float(ccp_alpha):
            raise ConfigError(f"ccp_alpha must be >= 0, got {ccp_alpha!r}")
        self.estimator_ = DecisionTreeClassifier(
            max_depth=max_depth,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            class_weight=resolve_class_weight(class_weight),
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
        """Impurity-decrease importances (weighted, normalized) — the
        cheap global view; the extracted rules stay the primary artifact."""
        if self.feature_names_ is None:
            return None
        imp = np.asarray(self.estimator_.feature_importances_, dtype=float)
        return imp if imp.sum() > 0 else None
