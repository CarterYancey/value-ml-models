"""Metrics of record: precision@K / recall@K, PR-AUC, Brier.

ROC-AUC is logged but never headlined — base rates are extreme in some
label cells. precision@K is unweighted (a portfolio buys K names, each one
counts once); PR-AUC and Brier accept the horizon's sample weights so
overlapping snapshots don't overstate confidence. Brier is only computed
when the model declares its scores are probabilities.
"""

from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _order_by_score(scores: np.ndarray) -> np.ndarray:
    """Indices sorted by score descending, NaN last, stable for ties."""
    s = np.where(np.isnan(scores), -np.inf, scores)
    return np.argsort(-s, kind="stable")


def precision_at_k(y_true, scores, k: int) -> float:
    y = np.asarray(y_true, dtype=float)
    scores = np.asarray(scores, dtype=float)
    if len(y) == 0 or k <= 0:
        return math.nan
    top = _order_by_score(scores)[: min(k, len(y))]
    return float(y[top].mean())


def recall_at_k(y_true, scores, k: int) -> float:
    y = np.asarray(y_true, dtype=float)
    scores = np.asarray(scores, dtype=float)
    positives = y.sum()
    if len(y) == 0 or k <= 0 or positives == 0:
        return math.nan
    top = _order_by_score(scores)[: min(k, len(y))]
    return float(y[top].sum() / positives)


def pr_auc(y_true, scores, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return math.nan
    s = np.asarray(scores, dtype=float)
    s = np.where(np.isnan(s), -np.inf, s)
    return float(average_precision_score(y, s, sample_weight=sample_weight))


def roc_auc(y_true, scores, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return math.nan
    s = np.asarray(scores, dtype=float)
    s = np.where(np.isnan(s), -np.inf, s)
    return float(roc_auc_score(y, s, sample_weight=sample_weight))


def brier(y_true, probs, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0:
        return math.nan
    return float(brier_score_loss(y, np.asarray(probs, dtype=float),
                                  sample_weight=sample_weight))


def base_rate(y_true, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0:
        return math.nan
    if sample_weight is None:
        return float(y.mean())
    return float(np.average(y, weights=np.asarray(sample_weight, dtype=float)))


def calibration_table(y_true, probs, sample_weight=None, n_bins: int = 10):
    """Reliability-curve bins for probabilistic scores.

    Quantile bins on the predicted probability (equal weight per bin
    rather than equal width — base rates are extreme in some cells, so
    fixed-width bins leave most of them empty). Returns a list of dicts:
    mean predicted vs. weighted observed rate per bin, with the bin's
    weight mass. Downstream ranking trusts these probabilities, so this
    table is the honest check on whether 0.7 means 70%.
    """
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(probs, dtype=float)
    w = (
        np.ones(len(y))
        if sample_weight is None
        else np.asarray(sample_weight, dtype=float)
    )
    keep = ~np.isnan(p)
    y, p, w = y[keep], p[keep], w[keep]
    if len(y) == 0:
        return []
    edges = np.unique(np.quantile(p, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 2:  # constant predictor: a single degenerate bin
        edges = np.array([edges[0], edges[0]])
        idx = np.zeros(len(p), dtype=int)
    else:
        idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    rows = []
    for b in range(len(edges) - 1):
        m = idx == b
        if not m.any():
            continue
        rows.append(
            {
                "bin_low": float(edges[b]),
                "bin_high": float(edges[b + 1]),
                "mean_predicted": float(np.average(p[m], weights=w[m])),
                "observed_rate": float(np.average(y[m], weights=w[m])),
                "n_rows": int(m.sum()),
                "effective_n": float(w[m].sum()),
            }
        )
    return rows


def compute_all(y_true, scores, *, sample_weight=None, top_k=(20, 50),
                probabilistic: bool = False) -> dict[str, float]:
    """The standard per-fold metric block logged by the runner."""
    out: dict[str, float] = {
        "n_test": float(len(np.asarray(y_true))),
        "base_rate": base_rate(y_true, sample_weight),
        "pr_auc": pr_auc(y_true, scores, sample_weight),
        "roc_auc": roc_auc(y_true, scores, sample_weight),
        "brier": brier(y_true, scores, sample_weight) if probabilistic else math.nan,
    }
    for k in top_k:
        out[f"precision_at_{k}"] = precision_at_k(y_true, scores, k)
        out[f"recall_at_{k}"] = recall_at_k(y_true, scores, k)
    return out
