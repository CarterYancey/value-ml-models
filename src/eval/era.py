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

def crash_label(year: int) -> str | None:
    """Short crash-era tag for a calendar year ("GFC", "COVID", ...), or
    None outside the sampled drawdown eras — used to mark crash years
    inline in the era table."""
    for name, (start, end) in CRASH_ERAS.items():
        if start <= int(year) <= end:
            return name.rsplit(" ", 1)[0]
    return None


#: Columns a predictions frame must carry (one row per test-set row).
#: Continuous-target runs additionally carry an `outcome` column (the
#: realized continuous label, e.g. fwd_3y_cagr) which unlocks the
#: outcome-based diagnostics (fwd_at_K, spearman_ic, mae, r2).
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
        "base_rate_brier": (
            metrics.base_rate_brier(y, w) if probabilistic else math.nan
        ),
    }
    for k in top_k:
        row[f"precision_at_{k}"] = metrics.precision_at_k(y, s, k)
        row[f"conf_at_{k}"] = metrics.confidence_at_k(s, k)
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
    if "outcome" in grp.columns:
        o = grp["outcome"].to_numpy(dtype=float)
        row["spearman_ic"] = metrics.spearman_ic(o, s)
        row["mae"] = metrics.weighted_mae(o, s, w)
        row["r2"] = metrics.weighted_r2(o, s, w)
        for k in top_k:
            row[f"fwd_at_{k}"] = metrics.outcome_at_k(o, s, k)
    return row


def _pooled_metric_row(
    predictions: pd.DataFrame, top_k, score_thresholds, probabilistic: bool,
    precision_targets=(),
) -> dict:
    """Pooled metrics over several test years, picking per year.

    Scores come from a different model per fold, so they are not
    comparable across years: a global top-K over pooled scores just takes
    whichever fold's model scores hottest (observed in practice — the
    pooled precision@K used to equal one fold's). Instead, the ranking
    metrics (top-K and the precision-floor family) select per year and
    aggregate the picks: precision = Σ hits / Σ picks, recall uses all
    positives. Row-wise metrics (base rate, Brier, threshold rules on
    absolute scores) pool directly; PR/ROC-AUC are still computed on the
    pooled scores and inherit the comparability caveat — context only.
    """
    y = predictions["y_true"].to_numpy(dtype=float)
    s = predictions["score"].to_numpy(dtype=float)
    w = predictions["sample_weight"].to_numpy(dtype=float)
    groups = [g for _, g in predictions.groupby("year", sort=True)]
    total_pos = y.sum()

    row: dict = {
        "n_test": len(predictions),
        "effective_n": float(w.sum()),
        "base_rate": metrics.base_rate(y, w),
        "pr_auc": metrics.pr_auc(y, s, w),
        "roc_auc": metrics.roc_auc(y, s, w),
        "brier": metrics.brier(y, s, w) if probabilistic else math.nan,
        "base_rate_brier": (
            metrics.base_rate_brier(y, w) if probabilistic else math.nan
        ),
    }
    for k in top_k:
        hits = picks = 0.0
        conf_sum = 0.0
        conf_picks = 0
        for grp in groups:
            gy = grp["y_true"].to_numpy(dtype=float)
            gs = grp["score"].to_numpy(dtype=float)
            h, p = metrics.hits_at_k(gy, gs, k)
            hits += h
            picks += p
            c = metrics.confidence_at_k(gs, k)
            if not math.isnan(c):
                conf_sum += c * p
                conf_picks += p
        row[f"precision_at_{k}"] = hits / picks if picks else math.nan
        row[f"conf_at_{k}"] = conf_sum / conf_picks if conf_picks else math.nan
        row[f"recall_at_{k}"] = hits / total_pos if total_pos else math.nan
    for t in score_thresholds:
        tag = metrics.threshold_tag(t)
        row[f"precision_at_thr_{tag}"] = metrics.precision_at_threshold(y, s, t)
        row[f"recall_at_thr_{tag}"] = metrics.recall_at_threshold(y, s, t)
        row[f"n_at_thr_{tag}"] = metrics.n_at_threshold(s, t)
    for p in precision_targets:
        tag = metrics.threshold_tag(p)
        hits = 0.0
        n_sel = 0
        any_defined = False
        for grp in groups:
            gy = grp["y_true"].to_numpy(dtype=float)
            gs = grp["score"].to_numpy(dtype=float)
            rap = metrics.recall_at_precision(gy, gs, p)
            if isinstance(rap["recall"], float) and math.isnan(rap["recall"]):
                continue  # no positives that year — nothing to recall
            any_defined = True
            hits += rap["recall"] * gy.sum()
            n_sel += int(rap["n_selected"])
        if not any_defined or total_pos == 0:
            row[f"recall_at_prec_{tag}"] = math.nan
            row[f"n_at_prec_{tag}"] = math.nan
        else:
            row[f"recall_at_prec_{tag}"] = hits / total_pos
            row[f"n_at_prec_{tag}"] = n_sel
    if "outcome" in predictions.columns:
        o = predictions["outcome"].to_numpy(dtype=float)
        # picks per year, like every other ranking metric; the pooled IC
        # is the mean of per-year ICs (per-fold scores aren't comparable,
        # so a pooled-rank correlation would be meaningless)
        ics = []
        for grp in groups:
            ic = metrics.spearman_ic(
                grp["outcome"].to_numpy(dtype=float),
                grp["score"].to_numpy(dtype=float),
            )
            if not math.isnan(ic):
                ics.append(ic)
        row["spearman_ic"] = float(np.mean(ics)) if ics else math.nan
        row["mae"] = metrics.weighted_mae(o, s, w)
        row["r2"] = metrics.weighted_r2(o, s, w)
        for k in top_k:
            total = picks = 0.0
            for grp in groups:
                go = grp["outcome"].to_numpy(dtype=float)
                gs = grp["score"].to_numpy(dtype=float)
                mean_k = metrics.outcome_at_k(go, gs, k)
                if math.isnan(mean_k):
                    continue
                n_picks = min(k, len(grp))
                total += mean_k * n_picks
                picks += n_picks
            row[f"fwd_at_{k}"] = total / picks if picks else math.nan
    return row


def pooled_metrics(
    predictions: pd.DataFrame, top_k=(20, 50), score_thresholds=(),
    probabilistic: bool = False, precision_targets=()
) -> dict:
    """The pooled metric block (per-year picks, see `_pooled_metric_row`)
    as a flat dict — what the runner returns and sweeps rank by."""
    _check_predictions(predictions)
    return _pooled_metric_row(
        predictions, top_k, score_thresholds, probabilistic, precision_targets
    )


#: Probability bars the confidence profile reports for probabilistic models.
CONFIDENCE_LEVELS = (0.9, 0.8, 0.7, 0.6, 0.5)

#: Per-year pick sizes the confidence profile always reports.
CONFIDENCE_TIERS = (5, 10, 20, 50)


def confidence_profile(
    predictions: pd.DataFrame, probabilistic: bool = False
) -> pd.DataFrame:
    """"How many high-confidence picks did the model make, how confident
    was it, and how precise were they?" — answered without guessing a
    score threshold in the config.

    One row per selection rule, pooled over the test years:

    - `top N/yr`: the model's N most-confident names each year (picks
      aggregated per year, since per-fold scores aren't comparable);
    - `score ≥ p` (probabilistic models only): every name the model
      scored at or above p, pooled row-wise — the model's own
      high-confidence call count at each probability bar.
    """
    _check_predictions(predictions)
    y = predictions["y_true"].to_numpy(dtype=float)
    s = predictions["score"].to_numpy(dtype=float)
    groups = [g for _, g in predictions.groupby("year", sort=True)]
    n_years = len(groups)
    rows = []
    for k in CONFIDENCE_TIERS:
        hits = picks = 0.0
        conf_sum = 0.0
        conf_picks = 0
        for grp in groups:
            gy = grp["y_true"].to_numpy(dtype=float)
            gs = grp["score"].to_numpy(dtype=float)
            h, p = metrics.hits_at_k(gy, gs, k)
            hits += h
            picks += p
            c = metrics.confidence_at_k(gs, k)
            if not math.isnan(c):
                conf_sum += c * p
                conf_picks += p
        rows.append(
            {
                "selection": f"top {k}/yr",
                "n_picks": int(picks),
                "picks_per_year": round(picks / n_years, 1) if n_years else math.nan,
                "mean_score": conf_sum / conf_picks if conf_picks else math.nan,
                "precision": hits / picks if picks else math.nan,
                "hits": int(hits),
            }
        )
    if probabilistic:
        for level in CONFIDENCE_LEVELS:
            sel = np.isfinite(s) & (s >= level)
            n = int(sel.sum())
            rows.append(
                {
                    "selection": f"score >= {metrics.threshold_tag(level)}",
                    "n_picks": n,
                    "picks_per_year": round(n / n_years, 1) if n_years else math.nan,
                    "mean_score": float(s[sel].mean()) if n else math.nan,
                    "precision": float(y[sel].mean()) if n else math.nan,
                    "hits": int(y[sel].sum()) if n else 0,
                }
            )
    return pd.DataFrame(rows)


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
            **_pooled_metric_row(predictions, top_k, score_thresholds,
                                 probabilistic, precision_targets),
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
        # multi-year eras pool with per-year picks, same as the pooled row
        # — the GFC spans two folds' models, whose scores don't compare
        row = {
            "era": name,
            **_pooled_metric_row(grp, top_k, score_thresholds, probabilistic,
                                 precision_targets),
        }
        for k in top_k:
            picks = sum(
                min(k, len(g)) for _, g in grp.groupby("year", sort=True)
            )
            p = row[f"precision_at_{k}"]
            if picks == 0 or math.isnan(p):
                row[f"precision_at_{k}_ci95"] = "—"
                continue
            lo, hi = wilson_interval(p * picks, picks)
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
    fold: int, years: np.ndarray, y_true, scores, sample_weight,
    outcome=None,
) -> pd.DataFrame:
    """One fold's test predictions in the standard frame layout.

    `outcome` (continuous-target runs only) is the realized continuous
    label on the same rows; its presence turns on the outcome-based
    diagnostics in the era/pooled tables."""
    frame = pd.DataFrame(
        {
            "fold": fold,
            "year": np.asarray(years, dtype=int),
            "y_true": np.asarray(y_true, dtype=float),
            "score": np.asarray(scores, dtype=float),
            "sample_weight": np.asarray(sample_weight, dtype=float),
        }
    )
    if outcome is not None:
        frame["outcome"] = np.asarray(outcome, dtype=float)
    return frame
