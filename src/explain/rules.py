"""Human-readable rules and diagrams from a fitted decision tree.

Rules like "book_to_market_rank > 0.83 → 62% probability of meeting the
criteria" are the point of Phase 1 (PLAN §2: explainability first). The
extracted rules are a first-class artifact, written into `reports/` and
checked in alongside the evaluation report.

NaN routing is part of the rule: upstream NULLs are meaningful, sklearn
routes them per split, and each condition states which side missing
values follow.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, plot_tree  # noqa: E402


@dataclass(frozen=True)
class LeafRule:
    """One root-to-leaf path with its training evidence."""

    conditions: tuple[str, ...]
    p_positive: float
    weighted_n: float
    weight_share: float  # fraction of total training weight in this leaf

    def format(self) -> str:
        cond = " AND ".join(self.conditions) if self.conditions else "(always)"
        return (
            f"IF {cond}\n"
            f"  THEN P(positive) = {self.p_positive:.3f}   "
            f"[weighted n = {self.weighted_n:.1f}, "
            f"{100 * self.weight_share:.1f}% of training weight]"
        )


def extract_leaf_rules(
    clf: DecisionTreeClassifier, feature_names: list[str]
) -> list[LeafRule]:
    """All leaf rules, sorted by P(positive) descending."""
    tree = clf.tree_
    classes = list(clf.classes_)
    pos_idx = classes.index(True) if True in classes else None
    total_weight = float(tree.weighted_n_node_samples[0])

    rules: list[LeafRule] = []

    def walk(node: int, conditions: tuple[str, ...]) -> None:
        left, right = tree.children_left[node], tree.children_right[node]
        if left == -1:  # leaf
            value = tree.value[node][0]
            total = float(value.sum())
            p = float(value[pos_idx]) / total if pos_idx is not None and total else 0.0
            w = float(tree.weighted_n_node_samples[node])
            rules.append(
                LeafRule(
                    conditions=conditions,
                    p_positive=p,
                    weighted_n=w,
                    weight_share=w / total_weight if total_weight else 0.0,
                )
            )
            return
        feat = feature_names[tree.feature[node]]
        thr = float(tree.threshold[node])
        nan_left = bool(tree.missing_go_to_left[node])
        left_cond = f"{feat} <= {thr:.4g}" + (" (or missing)" if nan_left else "")
        right_cond = f"{feat} > {thr:.4g}" + ("" if nan_left else " (or missing)")
        walk(left, conditions + (left_cond,))
        walk(right, conditions + (right_cond,))

    walk(0, ())
    return sorted(rules, key=lambda r: r.p_positive, reverse=True)


def rules_text(clf: DecisionTreeClassifier, feature_names: list[str]) -> str:
    """One rules block for a fitted tree, leaves sorted best-first.

    P(positive) is the leaf's weighted training frequency — an
    in-sample, uncalibrated number. Rank by it; do not read it as a
    forward probability (see the report's calibration curve).
    """
    rules = extract_leaf_rules(clf, feature_names)
    header = (
        f"depth <= {clf.get_depth()}, {clf.get_n_leaves()} leaves; "
        "P(positive) is weighted in-sample frequency (uncalibrated)"
    )
    return "\n".join([header, ""] + [r.format() for r in rules])


def render_tree_diagram(
    clf: DecisionTreeClassifier,
    feature_names: list[str],
    path: str | Path,
) -> Path:
    """Render the fitted tree to a PNG via matplotlib."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n_leaves = clf.get_n_leaves()
    fig, ax = plt.subplots(
        figsize=(max(8, 2.2 * n_leaves), max(5, 2.0 * clf.get_depth()))
    )
    plot_tree(
        clf,
        feature_names=feature_names,
        class_names=["positive" if c else "negative" for c in clf.classes_],
        filled=True,
        impurity=False,
        proportion=True,
        rounded=True,
        fontsize=8,
        ax=ax,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
