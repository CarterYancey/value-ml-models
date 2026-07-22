"""Report figures (matplotlib, Agg backend): calibration and the
discrimination curves (precision–recall, ROC).

The calibration plot is part of the honest-evaluation checklist whenever
probabilities are used downstream — portfolio construction ranks by
predicted probability, so "does 0.7 mean 70%?" is a first-class result.
The PR and ROC curves are the shape behind the headline PR-AUC / ROC-AUC:
PR is read against the base rate (the no-skill line moves with prevalence,
which is extreme in some label cells), ROC against the chance diagonal.
All three are score-only — they depend on `(y_true, score)` alone — so a
re-evaluation of a saved model reuses the training run's figures rather
than redrawing identical curves.
"""

from __future__ import annotations

import numpy as np  # noqa: E402

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from eval import metrics  # noqa: E402
from eval.metrics import calibration_table  # noqa: E402


def _finite_binary(y_true, scores, sample_weight):
    """(y, s, w) ready for a weighted sklearn curve, or None when the
    curve is undefined (empty, or a single class present). Non-finite
    scores are clamped below the finite minimum — the same "sort last"
    treatment the ranking metrics use — so rank baselines' -inf rows plot
    without crashing sklearn."""
    y = np.asarray(y_true, dtype=float)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return None
    s = metrics._finite_scores(scores)
    w = None if sample_weight is None else np.asarray(sample_weight, dtype=float)
    return y, s, w


def render_calibration_plot(
    y_true,
    probs,
    sample_weight=None,
    *,
    path: str | Path,
    title: str = "Calibration (reliability curve)",
    n_bins: int = 10,
) -> Path | None:
    """Reliability curve PNG; returns None when there is nothing to plot."""
    bins = calibration_table(y_true, probs, sample_weight, n_bins=n_bins)
    if not bins:
        return None
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pred = [b["mean_predicted"] for b in bins]
    obs = [b["observed_rate"] for b in bins]
    eff = [b["effective_n"] for b in bins]

    fig, (ax, ax_hist) = plt.subplots(
        2, 1, figsize=(6, 7), height_ratios=[3, 1], sharex=True
    )
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="perfect")
    ax.plot(pred, obs, marker="o", linewidth=1.5, label="model")
    ax.set_ylabel("observed positive rate (weighted)")
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax_hist.bar(pred, eff, width=0.02)
    ax_hist.set_xlabel("mean predicted probability (quantile bins)")
    ax_hist.set_ylabel("Σ weight")

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def render_pr_curve(
    y_true,
    scores,
    sample_weight=None,
    *,
    path: str | Path,
    title: str = "Precision–Recall curve",
) -> Path | None:
    """Weighted precision–recall curve PNG with the base-rate no-skill
    line; returns None when there is nothing to plot (empty or one class).
    ROC-AUC is never headlined here (base rates are extreme), so PR is the
    curve to read."""
    from sklearn.metrics import precision_recall_curve

    prepared = _finite_binary(y_true, scores, sample_weight)
    if prepared is None:
        return None
    y, s, w = prepared
    precision, recall, _ = precision_recall_curve(y, s, sample_weight=w)
    ap = metrics.pr_auc(y_true, scores, sample_weight)
    base = metrics.base_rate(y_true, sample_weight)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, linewidth=1.5, label=f"model (PR-AUC={ap:.3f})")
    ax.axhline(
        base, linestyle="--", linewidth=1,
        label=f"no-skill = base rate {base:.3f}",
    )
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def render_roc_curve(
    y_true,
    scores,
    sample_weight=None,
    *,
    path: str | Path,
    title: str = "ROC curve",
) -> Path | None:
    """Weighted ROC curve PNG with the chance diagonal; returns None when
    there is nothing to plot. Logged, never headlined (CLAUDE.md): PR-AUC
    is the metric of record."""
    from sklearn.metrics import roc_curve

    prepared = _finite_binary(y_true, scores, sample_weight)
    if prepared is None:
        return None
    y, s, w = prepared
    fpr, tpr, _ = roc_curve(y, s, sample_weight=w)
    auc = metrics.roc_auc(y_true, scores, sample_weight)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, linewidth=1.5, label=f"model (ROC-AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="chance")
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
