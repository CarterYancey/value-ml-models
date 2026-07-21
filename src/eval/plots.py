"""Report figures (matplotlib, Agg backend): calibration curve.

The calibration plot is part of the honest-evaluation checklist whenever
probabilities are used downstream — portfolio construction ranks by
predicted probability, so "does 0.7 mean 70%?" is a first-class result.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from eval.metrics import calibration_table  # noqa: E402


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
