"""Prequential post-hoc calibration (TODO Phase 3, PLAN §2).

Boosted/averaged tree scores rank well but are not honest probabilities.
Calibration learns a monotone map g(score) -> P(positive). It changes
no ranking: an isotonic fit is a step function, and the rows on one
step keep the order of their raw scores (`TIE_BREAK`), so precision@K
and the precision-floor family are the uncalibrated run's. What it buys
is *stable, interpretable thresholds*: `thr_for_prec_*` becomes a
probability you could fix ex ante, and the `score >= p` confidence
tiers mean what they say.

The calibration data problem is solved prequentially, without
constructing any local split (invariant 1 intact): when scoring fold Y,
out-of-sample test predictions of earlier folds already exist, each
produced on its own purged, embargoed test year. The calibrator for
fold Y is fit on the folds **whose outcomes were known before year Y
began** and applied to fold Y's raw scores.

**Which folds those are.** A fold's test rows are the snapshots of one
year, and a label with an H-year horizon is observed H years after its
snapshot: fold f's outcomes are complete at the end of year f + H. So
fold Y may be calibrated on folds f with f + H < Y, and on no later
one (`label_lag_folds = H`). Until 2026-09-30 every fold < Y was used.
For a 3-year label that calibrated the 2008 entries on what the 2005,
2006 and 2007 entries went on to do, which was not known until the end
of 2008, 2009 and 2010: the calibrator had seen the crash the scores
were supposed to be read before. The fit itself (the model, its
ranking, p@K, PR-AUC) was never affected; thresholds on calibrated
scores, Brier and the calibration curve of a calibrated run were. This
is what a live deployment can do: calibrate today's model on the
out-of-sample history whose outcomes have been observed.

Disclosed approximations and limits:

- The history was scored by *earlier folds' models* (each fold refits).
  Prequential calibration assumes the score distribution is reasonably
  stable across refits of the same config — the same assumption a live
  run makes. The report names the method and which folds were
  calibrated.
- The earliest fold(s) have little or no history and stay uncalibrated
  (raw scores) rather than being calibrated on noise; the floor is
  `calibration_min_rows`, and both classes must be present.
- Isotonic (`"isotonic"`) recovers any monotone distortion but needs a
  few thousand rows to be trustworthy; Platt (`"platt"`, a 2-parameter
  sigmoid on the raw score) cannot overfit but assumes the distortion
  is sigmoid-shaped. Both take the mandatory uniqueness weights.
- The strategy trades the extreme right tail, where calibration data is
  thinnest — the top step of an isotonic fit can rest on a handful of
  correlated picks, so calibrated-or-not, top-tier probabilities carry
  wide error bars (same caveat as the crash-era tables).

Deterministic by construction: the calibrators are a pure function of
the fold models and the dataset, so `vml-eval` re-derives identical
calibrated scores from a saved bundle of raw models — nothing new is
persisted. Deployment refits have no out-of-sample history to calibrate
on, so `vml-train-deploy` refuses calibrated configs (see TODO for the
deployment-time design).
"""

from __future__ import annotations

import numpy as np

from harness.errors import ConfigError

#: Accepted `calibration` config values ("" = off).
CALIBRATION_METHODS = ("isotonic", "platt")

#: Default minimum pooled history rows before a fold gets calibrated.
DEFAULT_CALIBRATION_MIN_ROWS = 1000

#: Weight of the raw score in a calibrated score. An isotonic map is a
#: step function: every raw score on one step gets the same calibrated
#: value, and a top-K over tied scores is a top-K in row order. Mixing
#: in a vanishing share of the raw score keeps the raw order within a
#: step and moves no calibrated value by more than this.
TIE_BREAK = 1e-6


def fit_calibrator(method: str, scores, y_true, sample_weight):
    """Fit one monotone score->probability map on out-of-sample history.

    Returns a callable (np.ndarray -> np.ndarray in [0, 1], NaN scores
    stay NaN), or None when the history cannot support a fit (a single
    class, or degenerate scores)."""
    s = np.asarray(scores, dtype=float)
    y = np.asarray(y_true, dtype=float)
    w = np.asarray(sample_weight, dtype=float)
    keep = np.isfinite(s)
    s, y, w = s[keep], y[keep], w[keep]
    if len(s) == 0 or len(np.unique(y)) < 2 or len(np.unique(s)) < 2:
        return None

    if method == "isotonic":
        from sklearn.isotonic import IsotonicRegression

        iso = IsotonicRegression(
            y_min=0.0, y_max=1.0, increasing=True, out_of_bounds="clip"
        )
        iso.fit(s, y, sample_weight=w)

        def transform(raw, iso=iso):
            raw = np.asarray(raw, dtype=float)
            out = np.full(len(raw), np.nan)
            finite = np.isfinite(raw)
            if finite.any():
                out[finite] = iso.predict(raw[finite])
            return out

        return transform

    if method == "platt":
        from sklearn.linear_model import LogisticRegression

        lr = LogisticRegression(C=1e10, solver="lbfgs", max_iter=1000)
        lr.fit(s.reshape(-1, 1), y.astype(int), sample_weight=w)
        positive = list(lr.classes_).index(1)

        def transform(raw, lr=lr, positive=positive):
            raw = np.asarray(raw, dtype=float)
            out = np.full(len(raw), np.nan)
            finite = np.isfinite(raw)
            if finite.any():
                out[finite] = lr.predict_proba(
                    raw[finite].reshape(-1, 1)
                )[:, positive]
            return out

        return transform

    raise ConfigError(
        f"unknown calibration method {method!r}; expected one of "
        f"{list(CALIBRATION_METHODS)} or empty (off)"
    )


class PrequentialCalibration:
    """The shared fold loop for the runner and `vml-eval`: feed it each
    fold's raw out-of-sample scores; it calibrates a fold against the
    earlier folds whose outcomes were known when the fold's year began
    (`label_lag_folds`, the label's horizon in years; see the module
    docstring). Both entry points using this one class is what makes a
    bundle re-evaluation reproduce the training run's calibrated scores
    exactly. Folds are walk-forward test years."""

    def __init__(self, method: str, min_rows: int, label_lag_folds: int):
        if method not in CALIBRATION_METHODS:
            raise ConfigError(
                f"unknown calibration method {method!r}; expected one of "
                f"{list(CALIBRATION_METHODS)} or empty (off)"
            )
        if int(label_lag_folds) < 1:
            raise ConfigError(
                "label_lag_folds is the label's horizon in years and must "
                f"be >= 1, got {label_lag_folds!r}"
            )
        self.method = method
        self.min_rows = int(min_rows)
        self.label_lag_folds = int(label_lag_folds)
        #: fold -> (raw scores, outcomes, weights)
        self._history: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        #: fold -> True if the fold's scores were calibrated
        self.fold_calibrated: dict[int, bool] = {}
        #: fold -> the folds its calibrator was fitted on
        self.fold_history: dict[int, list[int]] = {}

    def usable_folds(self, fold: int) -> list[int]:
        """The observed folds whose outcomes were complete before
        `fold`'s year began: f + label_lag_folds < fold."""
        return sorted(
            f for f in self._history if f + self.label_lag_folds < fold
        )

    def history_rows(self, fold: int) -> int:
        return int(sum(len(self._history[f][0]) for f in self.usable_folds(fold)))

    def calibrate(self, fold: int, raw_scores) -> np.ndarray:
        """Calibrated scores for one fold, or the raw scores unchanged
        when the usable history is still below `min_rows` (or cannot
        support a fit)."""
        raw = np.asarray(raw_scores, dtype=float)
        transform = None
        usable = self.usable_folds(fold)
        if usable and self.history_rows(fold) >= self.min_rows:
            transform = fit_calibrator(
                self.method,
                *(
                    np.concatenate([self._history[f][i] for f in usable])
                    for i in range(3)
                ),
            )
        self.fold_calibrated[fold] = transform is not None
        self.fold_history[fold] = usable if transform is not None else []
        if transform is None:
            return raw
        # rows on one isotonic step keep the order of their raw scores
        return (1.0 - TIE_BREAK) * transform(raw) + TIE_BREAK * raw

    def observe(self, fold: int, raw_scores, y_true, sample_weight) -> None:
        """Record one fold's raw out-of-sample predictions and outcomes
        (always raw — calibrators map raw scores, never re-calibrated
        ones). They enter a later fold's calibrator only once their
        outcomes were observable (`usable_folds`)."""
        self._history[int(fold)] = (
            np.asarray(raw_scores, dtype=float),
            np.asarray(y_true, dtype=float),
            np.asarray(sample_weight, dtype=float),
        )

    def summary(self) -> dict:
        """Report fragment: which folds were calibrated, which stayed raw."""
        return {
            "method": self.method,
            "min_rows": self.min_rows,
            "label_lag_folds": self.label_lag_folds,
            "fold_history": dict(sorted(self.fold_history.items())),
            "calibrated_folds": sorted(
                f for f, c in self.fold_calibrated.items() if c
            ),
            "uncalibrated_folds": sorted(
                f for f, c in self.fold_calibrated.items() if not c
            ),
        }
