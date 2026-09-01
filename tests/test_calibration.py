"""Prequential post-hoc calibration: monotone score->probability maps
fit on earlier folds' out-of-sample predictions only (no local split —
invariant 1 intact), with the earliest fold(s) left raw, and identical
calibrated scores re-derived by vml-eval from a bundle of raw models."""

import math

import numpy as np
import pytest

from harness.calibration import (
    PrequentialCalibration,
    fit_calibrator,
)
from harness.config import EvalConfig, ExperimentConfig
from harness.errors import ConfigError
from harness.evaluate import evaluate_bundle
from harness.runner import run_experiment

VERSION = "dataset_v0.0-test"


def _history(n=2000, seed=0):
    """Overconfident synthetic scores: true P(y=1) is milder than the
    score claims."""
    rng = np.random.default_rng(seed)
    s = rng.uniform(0, 1, n)
    p_true = 0.5 + 0.3 * (s - 0.5)  # shrink toward 0.5
    y = (rng.uniform(0, 1, n) < p_true).astype(float)
    w = rng.uniform(0.2, 1.0, n)
    return s, y, w


# --- fit_calibrator -------------------------------------------------------


@pytest.mark.parametrize("method", ["isotonic", "platt"])
def test_calibrator_is_monotone_and_bounded(method):
    s, y, w = _history()
    cal = fit_calibrator(method, s, y, w)
    grid = np.linspace(0, 1, 101)
    out = cal(grid)
    assert np.all((out >= 0) & (out <= 1))
    assert np.all(np.diff(out) >= -1e-12)  # non-decreasing
    # overconfident input gets pulled toward the base rate
    assert cal(np.array([0.99]))[0] < 0.95
    assert cal(np.array([0.01]))[0] > 0.05
    # NaN (unrankable) stays NaN
    assert math.isnan(cal(np.array([np.nan]))[0])


def test_calibrator_refuses_degenerate_history():
    s, y, w = _history()
    assert fit_calibrator("isotonic", s, np.ones_like(y), w) is None
    assert fit_calibrator("isotonic", np.full_like(s, 0.5), y, w) is None
    with pytest.raises(ConfigError, match="unknown calibration"):
        fit_calibrator("bogus", s, y, w)


# --- the prequential loop -------------------------------------------------


def test_prequential_first_fold_raw_then_calibrated():
    state = PrequentialCalibration("isotonic", min_rows=100)
    s0, y0, w0 = _history(500, seed=1)
    out0 = state.calibrate(2016, s0)
    np.testing.assert_array_equal(out0, s0)  # no history yet -> raw
    state.observe(s0, y0, w0)

    s1, _, _ = _history(500, seed=2)
    out1 = state.calibrate(2017, s1)
    assert not np.array_equal(out1, s1)  # history present -> calibrated
    summary = state.summary()
    assert summary["calibrated_folds"] == [2017]
    assert summary["uncalibrated_folds"] == [2016]


def test_prequential_respects_min_rows():
    state = PrequentialCalibration("platt", min_rows=10_000)
    s, y, w = _history(500)
    state.observe(s, y, w)
    out = state.calibrate(2017, s)
    np.testing.assert_array_equal(out, s)  # below the floor -> raw


# --- config surface -------------------------------------------------------


def _config_dict(**overrides):
    raw = {
        "name": "cal_test",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["features", "ranks"],
        "model": {"name": "decision_tree", "max_depth": 3},
        "top_k": [5],
        "calibration": "isotonic",
        "calibration_min_rows": 10,
    }
    raw.update(overrides)
    return raw


def test_calibration_config_validation():
    with pytest.raises(ConfigError, match="calibration must be one of"):
        ExperimentConfig.from_dict(_config_dict(calibration="sigmoid"))
    with pytest.raises(ConfigError, match="min_rows"):
        ExperimentConfig.from_dict(_config_dict(calibration_min_rows=0))
    raw = _config_dict(calibration="")
    with pytest.raises(ConfigError, match="calibration is off"):
        ExperimentConfig.from_dict(raw)


def test_uncalibrated_configs_keep_their_hash():
    raw = _config_dict()
    del raw["calibration"]
    del raw["calibration_min_rows"]
    config = ExperimentConfig.from_dict(raw)
    assert "calibration" not in config.canonical_json()
    assert "calibration" not in config.to_raw_dict()
    with_it = ExperimentConfig.from_dict(_config_dict())
    assert "calibration" in with_it.canonical_json()
    again = ExperimentConfig.from_dict(with_it.to_raw_dict())
    assert again.config_hash == with_it.config_hash


# --- end to end -----------------------------------------------------------


@pytest.fixture(scope="module")
def calibrated_run(data_root, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("calibrated_run")
    summary = run_experiment(
        ExperimentConfig.from_dict(_config_dict()),
        data_root=data_root,
        results_path=tmp / "results.csv",
        reports_dir=tmp / "reports",
        models_dir=tmp / "models",
    )
    return summary, tmp, data_root


def test_calibrated_run_reports_and_flags_folds(calibrated_run):
    summary, tmp, _ = calibrated_run
    assert summary["status"] == "completed"
    report = summary["report_path"].read_text()
    assert "prequential calibration" in report
    # fixture walkforward folds are 2016, 2017: the first has no history
    assert "raw for lack of" in report
    assert "2017" in report
    # raw-vs-calibrated reliability curves both rendered
    assert (tmp / "reports" / "cal_test_calibration_raw.png").exists()
    assert (tmp / "reports" / "cal_test_calibration.png").exists()
    # calibrated fold's scores are probabilities
    fold_2017 = next(
        fr for fr in summary["fold_results"] if fr["fold"] == 2017
    )
    assert math.isfinite(fold_2017["metrics"]["brier"])


def test_first_fold_matches_uncalibrated_run(calibrated_run, data_root,
                                             tmp_path):
    """Fold 2016 has no history, so its metrics must equal the plain
    uncalibrated run's — calibration changed nothing there."""
    summary, _, _ = calibrated_run
    raw = _config_dict(name="cal_test_off")
    del raw["calibration"]
    del raw["calibration_min_rows"]
    plain = run_experiment(
        ExperimentConfig.from_dict(raw),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    fold = lambda s, f: next(  # noqa: E731
        fr for fr in s["fold_results"] if fr["fold"] == f
    )
    assert (
        fold(summary, 2016)["metrics"] == fold(plain, 2016)["metrics"]
    )


def test_eval_reproduces_calibrated_scores(calibrated_run):
    """vml-eval re-derives the prequential calibration from the bundle's
    raw models: score-dependent metrics must match the training run."""
    summary, tmp, data_root = calibrated_run
    result = evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict({"name": "recheck", "top_k": [5]}),
        data_root=data_root,
        results_path=tmp / "results.csv",
        reports_dir=tmp / "reports",
    )
    for train_fr, eval_fr in zip(
        summary["fold_results"], result["fold_results"]
    ):
        assert train_fr["fold"] == eval_fr["fold"]
        for key in ("brier", "pr_auc", "precision_at_5"):
            t, e = train_fr["metrics"][key], eval_fr["metrics"][key]
            assert (math.isnan(t) and math.isnan(e)) or t == pytest.approx(e)


def test_deploy_refuses_calibrated_config(calibrated_run, data_root,
                                          tmp_path):
    from harness.deploy import train_deployment_model

    with pytest.raises(ConfigError, match="out-of-sample history"):
        train_deployment_model(
            ExperimentConfig.from_dict(_config_dict()),
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            models_dir=tmp_path / "models",
        )


def test_regressor_config_with_calibration_refused(data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        {
            "name": "cal_reg",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": "fwd_3y_cagr",
            "eval_label": "label_3y_cagr_ge_8",
            "feature_groups": ["ranks"],
            "model": {"name": "lightgbm_regressor", "n_estimators": 10},
            "calibration": "isotonic",
            "calibration_min_rows": 10,
        }
    )
    with pytest.raises(ConfigError, match="probabilistic"):
        run_experiment(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
