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
from typing import Iterator

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


def _leaf_paths(
    clf: DecisionTreeClassifier, feature_names: list[str]
) -> Iterator[tuple[tuple[str, ...], int]]:
    """Every root-to-leaf path as (conditions, leaf node id), each
    condition stating which side missing values follow."""
    tree = clf.tree_

    def walk(node: int, conditions: tuple[str, ...]):
        left, right = tree.children_left[node], tree.children_right[node]
        if left == -1:  # leaf
            yield conditions, node
            return
        feat = feature_names[tree.feature[node]]
        thr = float(tree.threshold[node])
        nan_left = bool(tree.missing_go_to_left[node])
        left_cond = f"{feat} <= {thr:.4g}" + (" (or missing)" if nan_left else "")
        right_cond = f"{feat} > {thr:.4g}" + ("" if nan_left else " (or missing)")
        yield from walk(left, conditions + (left_cond,))
        yield from walk(right, conditions + (right_cond,))

    yield from walk(0, ())


def extract_leaf_rules(
    clf: DecisionTreeClassifier, feature_names: list[str]
) -> list[LeafRule]:
    """All leaf rules, sorted by P(positive) descending."""
    tree = clf.tree_
    classes = list(clf.classes_)
    pos_idx = classes.index(True) if True in classes else None
    total_weight = float(tree.weighted_n_node_samples[0])

    rules: list[LeafRule] = []
    for conditions, node in _leaf_paths(clf, feature_names):
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
    return sorted(rules, key=lambda r: r.p_positive, reverse=True)


@dataclass(frozen=True)
class MulticlassLeafRule:
    """One root-to-leaf path of a multiclass tree (the registered era
    probe predicts the calendar year): the leaf's majority class, how
    pure it is, and the runners-up."""

    conditions: tuple[str, ...]
    predicted_class: str
    purity: float  # weighted share of the predicted class in the leaf
    weighted_n: float
    weight_share: float  # fraction of total training weight in this leaf
    top_classes: tuple[tuple[str, float], ...]  # (class, share), best first
    target_name: str = "class"

    def format(self) -> str:
        cond = " AND ".join(self.conditions) if self.conditions else "(always)"
        also = ", ".join(f"{c} {s:.2f}" for c, s in self.top_classes[1:])
        also = f"; also {also}" if also else ""
        return (
            f"IF {cond}\n"
            f"  THEN {self.target_name} = {self.predicted_class} "
            f"(purity {self.purity:.2f}{also})   "
            f"[weighted n = {self.weighted_n:.1f}, "
            f"{100 * self.weight_share:.1f}% of training weight]"
        )


def extract_leaf_rules_multiclass(
    clf: DecisionTreeClassifier,
    feature_names: list[str],
    class_names: list[str] | None = None,
    target_name: str = "class",
    n_runners_up: int = 2,
) -> list[MulticlassLeafRule]:
    """All leaf rules of a multiclass tree, sorted by purity descending."""
    tree = clf.tree_
    names = (
        [str(c) for c in clf.classes_] if class_names is None else list(class_names)
    )
    total_weight = float(tree.weighted_n_node_samples[0])

    rules: list[MulticlassLeafRule] = []
    for conditions, node in _leaf_paths(clf, feature_names):
        value = tree.value[node][0]
        total = float(value.sum())
        shares = value / total if total else value
        order = sorted(range(len(names)), key=lambda i: (-shares[i], i))
        top = tuple(
            (names[i], float(shares[i]))
            for i in order[: 1 + n_runners_up]
            if shares[i] > 0
        ) or ((names[order[0]], 0.0),)
        w = float(tree.weighted_n_node_samples[node])
        rules.append(
            MulticlassLeafRule(
                conditions=conditions,
                predicted_class=top[0][0],
                purity=top[0][1],
                weighted_n=w,
                weight_share=w / total_weight if total_weight else 0.0,
                top_classes=top,
                target_name=target_name,
            )
        )
    return sorted(rules, key=lambda r: r.purity, reverse=True)


def rules_text_multiclass(
    clf: DecisionTreeClassifier,
    feature_names: list[str],
    class_names: list[str] | None = None,
    target_name: str = "class",
) -> str:
    """One rules block for a fitted multiclass tree, purest leaves first.
    Purity is the leaf's weighted in-sample class share — uncalibrated."""
    rules = extract_leaf_rules_multiclass(
        clf, feature_names, class_names=class_names, target_name=target_name
    )
    header = (
        f"depth <= {clf.get_depth()}, {clf.get_n_leaves()} leaves; "
        "purity is the weighted in-sample share of the predicted "
        f"{target_name} (uncalibrated)"
    )
    return "\n".join([header, ""] + [r.format() for r in rules])


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
    class_names: list[str] | None = None,
) -> Path:
    """Render the fitted tree to a PNG via matplotlib. Boolean trees are
    labelled positive/negative; other class sets by `class_names` (default
    `str(class)`)."""
    if class_names is None:
        if clf.classes_.dtype == bool:
            class_names = ["positive" if c else "negative" for c in clf.classes_]
        else:
            class_names = [str(c) for c in clf.classes_]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n_leaves = clf.get_n_leaves()
    fig, ax = plt.subplots(
        figsize=(max(8, 2.2 * n_leaves), max(5, 2.0 * clf.get_depth()))
    )
    plot_tree(
        clf,
        feature_names=feature_names,
        class_names=class_names,
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
