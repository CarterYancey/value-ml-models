"""Metrics of record: precision@K / recall@K, PR-AUC, Brier.

ROC-AUC is logged but never headlined — base rates are extreme in some
label cells. precision@K is unweighted (a portfolio buys K names, each one
counts once); the same goes for precision/recall at a score threshold (the
rule buys every name clearing the bar, each one counts once). PR-AUC and
Brier accept the horizon's sample weights so overlapping snapshots don't
overstate confidence. Brier is only computed when the model declares its
scores are probabilities.
"""

from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _order_by_score(scores: np.ndarray) -> np.ndarray:
    """Indices sorted by score descending, NaN last, stable for ties."""
    s = np.where(np.isnan(scores), -np.inf, scores)
    return np.argsort(-s, kind="stable")


def _finite_scores(scores) -> np.ndarray:
    """Map non-finite scores to just below the finite minimum.

    Models legitimately emit non-finite scores for unrankable rows (NaN
    inputs, the rank baselines' -inf for NULL ranks = "sort last");
    sklearn's ranking metrics refuse anything non-finite. Clamping to
    below the finite minimum preserves the ranking order exactly.
    """
    s = np.asarray(scores, dtype=float)
    finite = np.isfinite(s)
    if finite.all():
        return s
    if not finite.any():
        return np.zeros(len(s))
    return np.where(finite, s, s[finite].min() - 1.0)


def precision_at_k(y_true, scores, k: int) -> float:
    y = np.asarray(y_true, dtype=float)
    scores = np.asarray(scores, dtype=float)
    if len(y) == 0 or k <= 0:
        return math.nan
    top = _order_by_score(scores)[: min(k, len(y))]
    return float(y[top].mean())


def hits_at_k(y_true, scores, k: int) -> tuple[float, int]:
    """(number of true positives among the top-k picks, picks actually
    made). The building block for pooling top-K metrics across years
    *by picking per year* — scores from different folds' models are not
    comparable, so a global top-K over pooled scores would just take the
    hottest-scoring fold's picks."""
    y = np.asarray(y_true, dtype=float)
    scores = np.asarray(scores, dtype=float)
    if len(y) == 0 or k <= 0:
        return (0.0, 0)
    top = _order_by_score(scores)[: min(k, len(y))]
    return (float(y[top].sum()), int(len(top)))


def confidence_at_k(scores, k: int) -> float:
    """Mean score of the top-k picks — "how confident was the model in
    the names it actually picked". NaN when nothing rankable."""
    s = np.asarray(scores, dtype=float)
    if len(s) == 0 or k <= 0:
        return math.nan
    top = _order_by_score(s)[: min(k, len(s))]
    vals = s[top]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else math.nan


def recall_at_k(y_true, scores, k: int) -> float:
    y = np.asarray(y_true, dtype=float)
    scores = np.asarray(scores, dtype=float)
    positives = y.sum()
    if len(y) == 0 or k <= 0 or positives == 0:
        return math.nan
    top = _order_by_score(scores)[: min(k, len(y))]
    return float(y[top].sum() / positives)


def _at_threshold(scores, threshold: float) -> np.ndarray:
    """Selection mask for "score >= threshold". Non-finite scores mean
    unrankable rows (see _finite_scores) and never clear the bar."""
    s = np.asarray(scores, dtype=float)
    return np.isfinite(s) & (s >= threshold)


def threshold_tag(threshold: float) -> str:
    """Stable metric-key suffix for a threshold (0.5 -> "0.5")."""
    return format(float(threshold), "g")


def precision_at_threshold(y_true, scores, threshold: float) -> float:
    """Precision of the rule "select every name scoring >= threshold".

    NaN when nothing clears the threshold: an empty selection makes no
    claims, so its precision is undefined rather than zero. n_at_threshold
    is recorded alongside so the empty case is visible, not silent.
    """
    y = np.asarray(y_true, dtype=float)
    sel = _at_threshold(scores, threshold)
    if len(y) == 0 or not sel.any():
        return math.nan
    return float(y[sel].mean())


def recall_at_threshold(y_true, scores, threshold: float) -> float:
    """Share of positives clearing the threshold. A threshold nothing
    meets recalls 0.0 of the existing positives; NaN only when there are
    no positives to recall."""
    y = np.asarray(y_true, dtype=float)
    positives = y.sum()
    if len(y) == 0 or positives == 0:
        return math.nan
    return float(y[_at_threshold(scores, threshold)].sum() / positives)


def n_at_threshold(scores, threshold: float) -> int:
    """How many samples cleared the threshold — the selection size the
    precision/recall above are computed on (0 when never met)."""
    return int(_at_threshold(scores, threshold).sum())


def recall_at_precision(y_true, scores, target: float) -> dict:
    """Best achievable recall subject to a precision floor, and the score
    threshold that achieves it.

    This is the project's headline trade-off (high precision even at low
    recall) made directly tunable: sweep model hyperparameters and read
    off which configuration recalls the most positives while keeping the
    rule "select every name scoring >= t" at precision >= `target`.

    Selection-rule semantics, like the other threshold metrics: each
    selected name counts once (unweighted), a rule takes all score ties
    together, and non-finite scores are unrankable and never selected —
    though every positive, rankable or not, stays in the recall
    denominator. Returns `{"recall", "threshold", "n_selected"}`;
    recall 0.0 / NaN threshold when no non-empty selection reaches the
    floor, all-NaN when there are no positives to recall.
    """
    y = np.asarray(y_true, dtype=float)
    s = np.asarray(scores, dtype=float)
    total_pos = y.sum()
    if len(y) == 0 or total_pos == 0:
        return {"recall": math.nan, "threshold": math.nan, "n_selected": math.nan}
    finite = np.isfinite(s)
    empty = {"recall": 0.0, "threshold": math.nan, "n_selected": 0}
    if not finite.any():
        return empty
    ys, ss = y[finite], s[finite]
    order = np.argsort(-ss, kind="stable")
    ys, ss = ys[order], ss[order]
    cum_pos = np.cumsum(ys)
    n_sel = np.arange(1, len(ys) + 1)
    # only cut where "score >= t" is a real rule: at the end of tie groups
    cut = np.ones(len(ss), dtype=bool)
    cut[:-1] = ss[:-1] > ss[1:]
    ok = cut & (cum_pos / n_sel >= target)
    if not ok.any():
        return empty
    # recall is nondecreasing down the ranking; among the qualifying cuts
    # with maximal recall, take the tightest (fewest picks, most precise)
    ok_idx = np.flatnonzero(ok)
    best = ok_idx[cum_pos[ok_idx] == cum_pos[ok_idx].max()][0]
    return {
        "recall": float(cum_pos[best] / total_pos),
        "threshold": float(ss[best]),
        "n_selected": int(n_sel[best]),
    }


def outcome_at_k(outcome, scores, k: int) -> float:
    """Mean realized continuous outcome (e.g. forward CAGR) of the top-k
    picks — "what did the picks actually return". Unweighted like
    precision@K: a portfolio buys K names, each counts once."""
    o = np.asarray(outcome, dtype=float)
    s = np.asarray(scores, dtype=float)
    if len(o) == 0 or k <= 0:
        return math.nan
    top = _order_by_score(s)[: min(k, len(o))]
    vals = o[top]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else math.nan


def spearman_ic(outcome, scores) -> float:
    """Spearman rank correlation between predicted and realized outcomes
    — the information coefficient. Rank-based, so it ignores the score
    scale and is robust to the extreme-return tail; unweighted. NaN with
    fewer than 3 finite pairs or a constant side."""
    from scipy.stats import spearmanr

    o = np.asarray(outcome, dtype=float)
    s = np.asarray(scores, dtype=float)
    keep = np.isfinite(o) & np.isfinite(s)
    if keep.sum() < 3:
        return math.nan
    o, s = o[keep], s[keep]
    if len(np.unique(o)) < 2 or len(np.unique(s)) < 2:
        return math.nan
    return float(spearmanr(o, s).statistic)


def weighted_mae(outcome, scores, sample_weight=None) -> float:
    """Weighted mean absolute error of predicted vs. realized outcome —
    a fit diagnostic only (dominated by the noise mass the strategy never
    touches), logged, never headlined. Quantile-objective scores predict
    a quantile, not the mean, so their MAE is expected to be biased."""
    o = np.asarray(outcome, dtype=float)
    s = np.asarray(scores, dtype=float)
    w = (
        np.ones(len(o))
        if sample_weight is None
        else np.asarray(sample_weight, dtype=float)
    )
    keep = np.isfinite(o) & np.isfinite(s)
    if not keep.any():
        return math.nan
    return float(np.average(np.abs(o[keep] - s[keep]), weights=w[keep]))


def weighted_r2(outcome, scores, sample_weight=None) -> float:
    """Weighted R² of predicted vs. realized outcome — same status as
    MAE: a fit diagnostic. Near-zero (even negative) R² on stock returns
    is normal and says nothing about whether the top of the ranking is
    good; that is what fwd_at_K and the precision frame measure."""
    o = np.asarray(outcome, dtype=float)
    s = np.asarray(scores, dtype=float)
    w = (
        np.ones(len(o))
        if sample_weight is None
        else np.asarray(sample_weight, dtype=float)
    )
    keep = np.isfinite(o) & np.isfinite(s)
    if not keep.any():
        return math.nan
    o, s, w = o[keep], s[keep], w[keep]
    ss_res = float(np.average((o - s) ** 2, weights=w))
    ss_tot = float(np.average((o - np.average(o, weights=w)) ** 2, weights=w))
    if ss_tot == 0:
        return math.nan
    return 1.0 - ss_res / ss_tot


def regression_diagnostics(
    outcome, scores, *, top_k=(20, 50), sample_weight=None
) -> dict[str, float]:
    """The per-fold diagnostic block for continuous-target models,
    computed against the realized continuous outcome (the training
    label's column on the test rows). fwd_at_K and spearman_ic are the
    readable ones; MAE/R² are logged for fit debugging only."""
    out = {
        "spearman_ic": spearman_ic(outcome, scores),
        "mae": weighted_mae(outcome, scores, sample_weight),
        "r2": weighted_r2(outcome, scores, sample_weight),
    }
    for k in top_k:
        out[f"fwd_at_{k}"] = outcome_at_k(outcome, scores, k)
    return out


def pr_auc(y_true, scores, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return math.nan
    s = _finite_scores(scores)
    return float(average_precision_score(y, s, sample_weight=sample_weight))


def roc_auc(y_true, scores, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return math.nan
    s = _finite_scores(scores)
    return float(roc_auc_score(y, s, sample_weight=sample_weight))


def brier(y_true, probs, sample_weight=None) -> float:
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0:
        return math.nan
    return float(brier_score_loss(y, np.asarray(probs, dtype=float),
                                  sample_weight=sample_weight))


def base_rate_brier(y_true, sample_weight=None) -> float:
    """Brier score of the no-skill predictor that always emits the
    (weighted) base rate — the reference `brier` must beat to show any
    skill. Equals p̄(1−p̄) under the weighted base rate p̄."""
    y = np.asarray(y_true, dtype=float)
    p = base_rate(y, sample_weight)
    if math.isnan(p):
        return math.nan
    return brier(y, np.full(len(y), p), sample_weight)


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
    keep = np.isfinite(p)
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
                score_thresholds=(), precision_targets=(),
                probabilistic: bool = False) -> dict[str, float]:
    """The standard per-fold metric block logged by the runner."""
    out: dict[str, float] = {
        "n_test": float(len(np.asarray(y_true))),
        "base_rate": base_rate(y_true, sample_weight),
        "pr_auc": pr_auc(y_true, scores, sample_weight),
        "roc_auc": roc_auc(y_true, scores, sample_weight),
        "brier": brier(y_true, scores, sample_weight) if probabilistic else math.nan,
        "base_rate_brier": (
            base_rate_brier(y_true, sample_weight) if probabilistic else math.nan
        ),
    }
    for k in top_k:
        out[f"precision_at_{k}"] = precision_at_k(y_true, scores, k)
        out[f"conf_at_{k}"] = confidence_at_k(scores, k)
        out[f"recall_at_{k}"] = recall_at_k(y_true, scores, k)
    for t in score_thresholds:
        tag = threshold_tag(t)
        out[f"precision_at_thr_{tag}"] = precision_at_threshold(y_true, scores, t)
        out[f"recall_at_thr_{tag}"] = recall_at_threshold(y_true, scores, t)
        out[f"n_at_thr_{tag}"] = float(n_at_threshold(scores, t))
    for p in precision_targets:
        tag = threshold_tag(p)
        rap = recall_at_precision(y_true, scores, p)
        out[f"recall_at_prec_{tag}"] = rap["recall"]
        out[f"thr_for_prec_{tag}"] = rap["threshold"]
        out[f"n_at_prec_{tag}"] = float(rap["n_selected"])
    return out
