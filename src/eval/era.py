"""Era-sliced evaluation: per-year metrics and the crash-era breakout.

Pooled numbers are never presented alone (CLAUDE.md invariant 5): a model
that only works 2009–2020 is a bull-market artifact. Crash eras are
first-class — the project's thesis is only testable in drawdowns, of
which the sample has ~4, each mechanically different (PLAN §4 Phase 2).

Uncertainty is reported honestly: precision@K gets a Wilson interval,
and the interval itself is flagged as *optimistic* — top-K picks within
a year are correlated (shared sectors, shared factor bets, overlapping
quarters), so K picks carry the statistical weight of far fewer than K
independent bets. Wide intervals here are the truth, not a presentation
problem.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from eval import metrics

#: Drawdown eras in the sample, each mechanically different.
CRASH_ERAS: dict[str, tuple[int, int]] = {
    "dot-com 2000-02": (2000, 2002),
    "GFC 2008-09": (2008, 2009),
    "COVID 2020": (2020, 2020),
    "rate-shock 2022": (2022, 2022),
}

#: Columns a predictions frame must carry (one row per test-set row).
PREDICTION_COLUMNS = ("fold", "year", "y_true", "score", "sample_weight")

CORRELATED_PICKS_CAVEAT = (
    "Intervals are Wilson 95% on precision@K treating the K picks as "
    "independent; they are not — same-year picks share sectors, factor "
    "bets and overlapping windows, so true uncertainty is wider than "
    "shown."
)


def wilson_interval(successes: float, n: float, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return (math.nan, math.nan)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0.0, center - half), min(1.0, center + half))


def _metric_row(
    grp: pd.DataFrame, top_k, score_thresholds, probabilistic: bool,
    precision_targets=(),
) -> dict:
    y = grp["y_true"].to_numpy(dtype=float)
    s = grp["score"].to_numpy(dtype=float)
    w = grp["sample_weight"].to_numpy(dtype=float)
    row: dict = {
        "n_test": len(grp),
        "effective_n": float(w.sum()),
        "base_rate": metrics.base_rate(y, w),
        "pr_auc": metrics.pr_auc(y, s, w),
        "roc_auc": metrics.roc_auc(y, s, w),
        "brier": metrics.brier(y, s, w) if probabilistic else math.nan,
    }
    for k in top_k:
        row[f"precision_at_{k}"] = metrics.precision_at_k(y, s, k)
        row[f"recall_at_{k}"] = metrics.recall_at_k(y, s, k)
    for t in score_thresholds:
        tag = metrics.threshold_tag(t)
        row[f"precision_at_thr_{tag}"] = metrics.precision_at_threshold(y, s, t)
        row[f"recall_at_thr_{tag}"] = metrics.recall_at_threshold(y, s, t)
        row[f"n_at_thr_{tag}"] = metrics.n_at_threshold(s, t)
    for p in precision_targets:
        tag = metrics.threshold_tag(p)
        rap = metrics.recall_at_precision(y, s, p)
        row[f"recall_at_prec_{tag}"] = rap["recall"]
        row[f"n_at_prec_{tag}"] = rap["n_selected"]
    return row


def era_table(
    predictions: pd.DataFrame, top_k=(20, 50), score_thresholds=(),
    probabilistic: bool = False, precision_targets=()
) -> pd.DataFrame:
    """Per-test-year metrics plus a clearly-marked pooled row.

    `predictions` carries one row per test-set row (PREDICTION_COLUMNS).
    Under walkforward, years and folds coincide; slicing on the year of
    `snapshot_date` keeps this correct for any scheme.
    """
    _check_predictions(predictions)
    rows = []
    for year, grp in predictions.groupby("year", sort=True):
        rows.append(
            {
                "era": str(int(year)),
                **_metric_row(grp, top_k, score_thresholds, probabilistic,
                              precision_targets),
            }
        )
    rows.append(
        {
            "era": "pooled",
            **_metric_row(predictions, top_k, score_thresholds, probabilistic,
                          precision_targets),
        }
    )
    return pd.DataFrame(rows)


def crash_era_table(
    predictions: pd.DataFrame, top_k=(20, 50), score_thresholds=(),
    probabilistic: bool = False, precision_targets=()
) -> pd.DataFrame:
    """Metrics per crash era present in the test years, with Wilson
    intervals on precision@K (see CORRELATED_PICKS_CAVEAT)."""
    _check_predictions(predictions)
    rows = []
    for name, (start, end) in CRASH_ERAS.items():
        grp = predictions[predictions["year"].between(start, end)]
        if grp.empty:
            continue
        row = {
            "era": name,
            **_metric_row(grp, top_k, score_thresholds, probabilistic,
                          precision_targets),
        }
        y = grp["y_true"].to_numpy(dtype=float)
        s = grp["score"].to_numpy(dtype=float)
        for k in top_k:
            kk = min(k, len(y))
            p = row[f"precision_at_{k}"]
            if math.isnan(p):
                row[f"precision_at_{k}_ci95"] = "—"
                continue
            lo, hi = wilson_interval(p * kk, kk)
            row[f"precision_at_{k}_ci95"] = f"[{lo:.2f}, {hi:.2f}]"
        rows.append(row)
    return pd.DataFrame(rows)


def _check_predictions(predictions: pd.DataFrame) -> None:
    missing = [c for c in PREDICTION_COLUMNS if c not in predictions.columns]
    if missing:
        raise ValueError(f"predictions frame lacks columns: {missing}")
    if predictions.empty:
        raise ValueError("predictions frame is empty")


def collect_predictions(
    fold: int, years: np.ndarray, y_true, scores, sample_weight
) -> pd.DataFrame:
    """One fold's test predictions in the standard frame layout."""
    return pd.DataFrame(
        {
            "fold": fold,
            "year": np.asarray(years, dtype=int),
            "y_true": np.asarray(y_true, dtype=float),
            "score": np.asarray(scores, dtype=float),
            "sample_weight": np.asarray(sample_weight, dtype=float),
        }
    )
