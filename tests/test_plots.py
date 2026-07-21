"""Discrimination-curve figures (PR, ROC): drawn when both classes are
present, gracefully skipped otherwise, and unfazed by the non-finite
scores rank baselines emit."""

import numpy as np

from eval.plots import render_pr_curve, render_roc_curve


def _data(seed=0, n=200):
    rng = np.random.default_rng(seed)
    y = (rng.uniform(size=n) < 0.3).astype(float)
    scores = np.clip(0.3 * y + rng.uniform(size=n) * 0.7, 0, 1)
    w = rng.uniform(0.2, 1.0, n)
    return y, scores, w


def test_pr_and_roc_curves_written(tmp_path):
    y, s, w = _data()
    pr = render_pr_curve(y, s, w, path=tmp_path / "pr.png")
    roc = render_roc_curve(y, s, w, path=tmp_path / "roc.png")
    assert pr.exists() and pr.stat().st_size > 0
    assert roc.exists() and roc.stat().st_size > 0


def test_curves_none_for_single_class(tmp_path):
    y = np.zeros(20)
    s = np.linspace(0, 1, 20)
    assert render_pr_curve(y, s, path=tmp_path / "pr.png") is None
    assert render_roc_curve(y, s, path=tmp_path / "roc.png") is None
    assert not (tmp_path / "pr.png").exists()


def test_curves_none_for_empty(tmp_path):
    assert render_pr_curve([], [], path=tmp_path / "pr.png") is None
    assert render_roc_curve([], [], path=tmp_path / "roc.png") is None


def test_curves_tolerate_nonfinite_scores(tmp_path):
    # rank baselines emit -inf for NULL-rank rows; the curves must clamp,
    # not crash (same "sort last" treatment as the ranking metrics)
    y = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 0.0])
    s = np.array([0.9, 0.5, np.nan, -np.inf, 0.7, 0.2])
    assert render_pr_curve(y, s, path=tmp_path / "pr.png") is not None
    assert render_roc_curve(y, s, path=tmp_path / "roc.png") is not None
