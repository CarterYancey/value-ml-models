"""Metrics for the era-identifiability probe (multiclass, year target).

Everything is weighted by the horizon's `sample_weight_{H}y` (Σw, never
row counts — overlapping windows make counts dishonest here as
everywhere). `classes` is the sorted union of the years seen in train
and test; `proba` is `(n, k)` aligned to it (`align_proba` zero-fills the
columns of years the model never saw).

Chance is not 1/k: snapshot counts grow over the sample, so the
majority-year and train-prior baselines are the ones a probe must beat.
The per-year table is the era slice invariant 5 requires — for a probe
whose target *is* the era it shows exactly which years are identifiable.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402

_EPS = 1e-15


def _w(sample_weight, n: int) -> np.ndarray:
    w = np.asarray(sample_weight, dtype=float)
    if len(w) != n:
        raise ValueError(f"sample_weight length {len(w)} != {n}")
    return w


def align_proba(
    proba: np.ndarray, model_classes: np.ndarray, classes: np.ndarray
) -> np.ndarray:
    """`(n, len(classes))` probabilities: the model's columns placed on
    the union axis, zero for classes the model never saw. Rows keep
    their sums (a model column absent from `classes` is an error)."""
    proba = np.asarray(proba, dtype=float)
    model_classes = np.asarray(model_classes)
    classes = np.asarray(classes)
    if proba.ndim != 2 or proba.shape[1] != len(model_classes):
        raise ValueError(
            f"proba shape {proba.shape} does not match {len(model_classes)} "
            "model classes"
        )
    out = np.zeros((proba.shape[0], len(classes)))
    index = {int(c): i for i, c in enumerate(classes)}
    for j, c in enumerate(model_classes):
        if int(c) not in index:
            raise ValueError(f"model class {c} not in the union axis {classes}")
        out[:, index[int(c)]] = proba[:, j]
    return out


def predict_year(proba: np.ndarray, classes: np.ndarray) -> np.ndarray:
    """Argmax class per row; ties resolve to the earliest year."""
    proba = np.asarray(proba, dtype=float)
    return np.asarray(classes)[np.argmax(proba, axis=1)]


def weighted_accuracy(y_true, y_pred, sample_weight) -> float:
    y_true = np.asarray(y_true)
    w = _w(sample_weight, len(y_true))
    if w.sum() == 0:
        return float("nan")
    return float(np.sum(w * (y_true == np.asarray(y_pred))) / w.sum())


def within_one_year_accuracy(y_true, y_pred, sample_weight) -> float:
    y_true = np.asarray(y_true, dtype=int)
    w = _w(sample_weight, len(y_true))
    if w.sum() == 0:
        return float("nan")
    close = np.abs(y_true - np.asarray(y_pred, dtype=int)) <= 1
    return float(np.sum(w * close) / w.sum())


def weighted_mae_years(y_true, y_pred, sample_weight) -> float:
    y_true = np.asarray(y_true, dtype=int)
    w = _w(sample_weight, len(y_true))
    if w.sum() == 0:
        return float("nan")
    err = np.abs(y_true - np.asarray(y_pred, dtype=int))
    return float(np.sum(w * err) / w.sum())


def macro_f1(y_true, y_pred, classes, sample_weight) -> float:
    y_true = np.asarray(y_true)
    if len(y_true) == 0:
        return float("nan")
    return float(
        f1_score(
            y_true,
            np.asarray(y_pred),
            labels=list(np.asarray(classes)),
            average="macro",
            sample_weight=_w(sample_weight, len(y_true)),
            zero_division=0,
        )
    )


def weighted_log_loss(y_true, proba, classes, sample_weight, eps=_EPS) -> float:
    """Weighted mean −log p(true class); zero columns cost −log(eps)."""
    y_true = np.asarray(y_true)
    w = _w(sample_weight, len(y_true))
    if w.sum() == 0:
        return float("nan")
    proba = np.clip(np.asarray(proba, dtype=float), eps, 1.0)
    index = {int(c): i for i, c in enumerate(np.asarray(classes))}
    cols = np.array([index[int(y)] for y in y_true])
    p_true = proba[np.arange(len(y_true)), cols]
    return float(np.sum(w * -np.log(p_true)) / w.sum())


def train_prior(y_train, w_train, classes) -> np.ndarray:
    """Weighted class frequencies on the union axis (0 for years absent
    from training)."""
    y_train = np.asarray(y_train)
    w = _w(w_train, len(y_train))
    classes = np.asarray(classes)
    prior = np.array([w[y_train == c].sum() for c in classes], dtype=float)
    total = prior.sum()
    return prior / total if total > 0 else prior


def baseline_metrics(y_train, w_train, y_test, w_test, classes) -> dict:
    """The trivial baselines a probe must beat, all on the test rows."""
    classes = np.asarray(classes)
    y_train = np.asarray(y_train)
    y_test = np.asarray(y_test)
    prior = train_prior(y_train, w_train, classes)
    k_train = int(len(np.unique(y_train)))
    majority = int(classes[int(np.argmax(prior))]) if k_train else None
    w_test = _w(w_test, len(y_test))
    out = {
        "baseline_chance_uniform": 1.0 / k_train if k_train else float("nan"),
        "baseline_majority_year": majority,
        "baseline_prior_expected_accuracy": float(np.sum(prior**2)),
    }
    if majority is not None and len(y_test):
        pred = np.full(len(y_test), majority)
        out["baseline_majority_accuracy"] = weighted_accuracy(y_test, pred, w_test)
        out["baseline_majority_within_1y_accuracy"] = within_one_year_accuracy(
            y_test, pred, w_test
        )
        out["baseline_majority_mae_years"] = weighted_mae_years(
            y_test, pred, w_test
        )
        prior_rows = np.tile(prior, (len(y_test), 1))
        out["baseline_prior_log_loss"] = weighted_log_loss(
            y_test, prior_rows, classes, w_test
        )
    return out


def headline_metrics(
    y_true, proba, classes, sample_weight, y_train, w_train
) -> dict:
    """Flat dict for `metrics_json`: the model's numbers and every
    baseline, on one fold's test rows."""
    classes = np.asarray(classes)
    y_true = np.asarray(y_true)
    w = _w(sample_weight, len(y_true))
    proba = np.asarray(proba, dtype=float)
    y_pred = predict_year(proba, classes)
    train_years = set(int(y) for y in np.unique(np.asarray(y_train)))
    test_years = set(int(y) for y in np.unique(y_true))
    out = {
        "n_test": int(len(y_true)),
        "effective_n": float(w.sum()),
        "k_train": len(train_years),
        "k_test": len(test_years),
        "n_test_years_unseen_in_train": len(test_years - train_years),
        "accuracy": weighted_accuracy(y_true, y_pred, w),
        "within_1y_accuracy": within_one_year_accuracy(y_true, y_pred, w),
        "mae_years": weighted_mae_years(y_true, y_pred, w),
        "macro_f1": macro_f1(y_true, y_pred, classes, w),
        "log_loss": weighted_log_loss(y_true, proba, classes, w),
    }
    out.update(baseline_metrics(y_train, w_train, y_true, w, classes))
    return out


def confusion_matrix_weighted(y_true, y_pred, classes, sample_weight) -> pd.DataFrame:
    """Σw per (true year, predicted year); rows true, columns predicted."""
    classes = [int(c) for c in np.asarray(classes)]
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    w = _w(sample_weight, len(y_true))
    cm = pd.DataFrame(0.0, index=classes, columns=classes)
    for t, p, wi in zip(y_true, y_pred, w):
        cm.loc[t, p] += wi
    cm.index.name = "true_year"
    cm.columns.name = "predicted_year"
    return cm


def per_year_table(y_true, y_pred, sample_weight, classes, train_years) -> pd.DataFrame:
    """The era slice: one row per test year — weighted recall (share of
    the year's rows called correctly), precision of calls for that year
    (NaN when it is never predicted), and which year it is most confused
    with. Years absent from training are unpredictable by construction
    (`in_train = False`)."""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    w = _w(sample_weight, len(y_true))
    train_years = set(int(y) for y in train_years)
    cm = confusion_matrix_weighted(y_true, y_pred, classes, w)
    total = w.sum()
    rows = []
    for year in sorted(set(int(y) for y in np.unique(y_true))):
        mask = y_true == year
        wy = w[mask].sum()
        row_cm = cm.loc[year]
        correct = float(row_cm.get(year, 0.0))
        predicted_total = float(cm[year].sum()) if year in cm.columns else 0.0
        off = row_cm.drop(labels=[year], errors="ignore")
        if len(off) and off.max() > 0:
            confused_with = int(off.idxmax())
            confusion_share = float(off.max() / wy) if wy else float("nan")
        else:
            confused_with, confusion_share = None, 0.0
        rows.append(
            {
                "year": year,
                "in_train": year in train_years,
                "n_test": int(mask.sum()),
                "effective_n": float(wy),
                "test_weight_share": float(wy / total) if total else float("nan"),
                "recall": float(correct / wy) if wy else float("nan"),
                "precision": (
                    float(correct / predicted_total)
                    if predicted_total > 0
                    else float("nan")
                ),
                "most_confused_with": confused_with,
                "confusion_share": confusion_share,
            }
        )
    return pd.DataFrame(rows)


def min_year_slice(y_true, proba, sample_weight, classes, min_year: int) -> dict | None:
    """Headline block restricted to test rows with year >= `min_year`
    (the post-burn-in view: early years are identifiable from nullity
    alone). None when no test row qualifies. Baselines are recomputed on
    the slice with the same prior (the model was trained on all years)."""
    y_true = np.asarray(y_true, dtype=int)
    w = _w(sample_weight, len(y_true))
    proba = np.asarray(proba, dtype=float)
    keep = y_true >= int(min_year)
    if not keep.any():
        return None
    classes = np.asarray(classes)
    y_pred = predict_year(proba[keep], classes)
    return {
        "min_year": int(min_year),
        "n_test": int(keep.sum()),
        "effective_n": float(w[keep].sum()),
        "accuracy": weighted_accuracy(y_true[keep], y_pred, w[keep]),
        "within_1y_accuracy": within_one_year_accuracy(y_true[keep], y_pred, w[keep]),
        "mae_years": weighted_mae_years(y_true[keep], y_pred, w[keep]),
        "log_loss": weighted_log_loss(y_true[keep], proba[keep], classes, w[keep]),
    }


# ------------------------------------------------------------------ figures

_INK = "#3a3a3a"
_MUTED = "#8a8a8a"
_BAR = "#3b6fb6"  # single series: one hue, no legend


def _recessive_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#d0d0d0")
    ax.tick_params(colors=_INK, labelsize=8)


def render_confusion_heatmap(
    cm: pd.DataFrame, *, path: str | Path, title: str = "Year confusion"
) -> Path:
    """Row-normalised confusion heatmap (share of each true year's weight
    assigned to each predicted year): one sequential hue, light→dark."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row_sums = cm.sum(axis=1).replace(0, np.nan)
    norm = cm.div(row_sums, axis=0).fillna(0.0)
    k = len(cm)
    size = max(4.5, 0.42 * k + 1.5)
    fig, ax = plt.subplots(figsize=(size + 1.2, size))
    im = ax.imshow(norm.to_numpy(), cmap="Blues", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(k))
    ax.set_yticks(range(k))
    ax.set_xticklabels([str(c) for c in cm.columns], rotation=90)
    ax.set_yticklabels([str(c) for c in cm.index])
    ax.set_xlabel("predicted year", color=_INK, fontsize=9)
    ax.set_ylabel("true year", color=_INK, fontsize=9)
    ax.set_title(title, color=_INK, fontsize=10, loc="left")
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(colors=_INK, labelsize=8, length=0)
    if k <= 30:  # direct labels where they stay legible
        for i in range(k):
            for j in range(k):
                v = norm.iat[i, j]
                if v >= 0.05:
                    ax.text(
                        j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6.5, color="white" if v > 0.6 else _INK,
                    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("share of true year's weight", color=_INK, fontsize=8)
    cbar.ax.tick_params(colors=_INK, labelsize=7)
    cbar.outline.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def render_importance_bar(
    importances: pd.Series,
    *,
    path: str | Path,
    title: str = "Feature importance",
    top_n: int = 20,
) -> Path:
    """Horizontal bars for the top-N importances (single series)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    top = importances.sort_values(ascending=False).head(top_n)[::-1]
    fig, ax = plt.subplots(figsize=(7, max(3.0, 0.3 * len(top) + 1.2)))
    ax.barh(
        [str(i) for i in top.index], top.to_numpy(), color=_BAR, height=0.6
    )
    for y, v in enumerate(top.to_numpy()):
        ax.text(v, y, f" {v:.3f}", va="center", fontsize=7, color=_INK)
    ax.set_xlim(0, max(float(top.max()) if len(top) else 0.0, 1e-9) * 1.18)
    ax.set_title(title, color=_INK, fontsize=10, loc="left")
    ax.set_xlabel("normalised importance", color=_INK, fontsize=9)
    ax.xaxis.grid(True, color="#e6e6e6", linewidth=0.6)
    ax.set_axisbelow(True)
    _recessive_axes(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
