"""Prequential post-hoc calibration (TODO Phase 3, PLAN §2).

Boosted/averaged tree scores rank well but are not honest probabilities.
Calibration learns a monotone map g(score) -> P(positive) — it changes
no ranking (up to ties isotonic's flat steps introduce), so precision@K
and the precision-floor family are essentially untouched; what it buys
is *stable, interpretable thresholds*: `thr_for_prec_*` becomes a
probability you could fix ex ante, and the `score >= p` confidence
tiers mean what they say.

The calibration data problem is solved prequentially, without
constructing any local split (invariant 1 intact): when scoring fold Y,
the pooled out-of-sample test predictions of folds < Y already exist —
each was produced on its own purged, embargoed test year, all strictly
earlier than year Y. The calibrator for fold Y is fit on that history
and applied to fold Y's raw scores; the raw scores then join the
history for later folds. This mirrors exactly what a live deployment
would do (calibrate today's model on all past out-of-sample history).

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
    fold's raw out-of-sample scores in chronological order; it calibrates
    against the folds already seen. Both entry points using this one
    class is what makes a bundle re-evaluation reproduce the training
    run's calibrated scores exactly."""

    def __init__(self, method: str, min_rows: int):
        if method not in CALIBRATION_METHODS:
            raise ConfigError(
                f"unknown calibration method {method!r}; expected one of "
                f"{list(CALIBRATION_METHODS)} or empty (off)"
            )
        self.method = method
        self.min_rows = int(min_rows)
        self._scores: list[np.ndarray] = []
        self._y: list[np.ndarray] = []
        self._w: list[np.ndarray] = []
        #: fold -> True if the fold's scores were calibrated
        self.fold_calibrated: dict[int, bool] = {}

    def history_rows(self) -> int:
        return int(sum(len(s) for s in self._scores))

    def calibrate(self, fold: int, raw_scores) -> np.ndarray:
        """Calibrated scores for one fold, or the raw scores unchanged
        when the pooled history is still below `min_rows` (or cannot
        support a fit). Call in chronological fold order."""
        raw = np.asarray(raw_scores, dtype=float)
        transform = None
        if self.history_rows() >= self.min_rows:
            transform = fit_calibrator(
                self.method,
                np.concatenate(self._scores),
                np.concatenate(self._y),
                np.concatenate(self._w),
            )
        self.fold_calibrated[fold] = transform is not None
        return raw if transform is None else transform(raw)

    def observe(self, raw_scores, y_true, sample_weight) -> None:
        """Add one fold's raw out-of-sample predictions to the history
        (always raw — calibrators map raw scores, never re-calibrated
        ones). Call after `calibrate` for the same fold."""
        self._scores.append(np.asarray(raw_scores, dtype=float))
        self._y.append(np.asarray(y_true, dtype=float))
        self._w.append(np.asarray(sample_weight, dtype=float))

    def summary(self) -> dict:
        """Report fragment: which folds were calibrated, which stayed raw."""
        return {
            "method": self.method,
            "min_rows": self.min_rows,
            "calibrated_folds": sorted(
                f for f, c in self.fold_calibrated.items() if c
            ),
            "uncalibrated_folds": sorted(
                f for f, c in self.fold_calibrated.items() if not c
            ),
        }
