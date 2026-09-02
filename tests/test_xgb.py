"""XGBoost wrappers under the harness protocol: mandatory weights,
NaN-native, scale_pos_weight as the shared precision knob, quantile
regression reframe, and a hard error instead of XGBoost's silent
GPU-to-CPU fallback (a CPU fit must never be logged under a cuda
config)."""

import math

import numpy as np
import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.errors import ConfigError, MissingSampleWeightError
from harness.runner import run_experiment
from models.registry import build_model, model_target
from models.xgb import XGBoostModel, XGBoostRegressorModel

VERSION = "dataset_v0.0-test"


def _toy_data(n=400, seed=0, with_nan=True):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "book_to_market_rank": rng.uniform(0, 1, n),
            "earnings_yield_rank": rng.uniform(0, 1, n),
        }
    )
    y = (X["book_to_market_rank"] + 0.2 * rng.normal(size=n) > 0.6).to_numpy()
    if with_nan:
        X.loc[X.index[: n // 5], "earnings_yield_rank"] = np.nan
    w = rng.uniform(0.2, 1.0, n)
    return X, y, w


# --- classifier -----------------------------------------------------------


def test_xgb_fits_nan_native_and_scores_probabilities():
    X, y, w = _toy_data()
    model = XGBoostModel(n_estimators=30, max_depth=3)
    model.fit(X, y, sample_weight=w)
    scores = model.predict_scores(X)
    assert len(scores) == len(X)
    assert np.all((scores >= 0) & (scores <= 1))
    assert model.probabilistic is True
    # learns the generating factor
    assert np.corrcoef(scores, X["book_to_market_rank"])[0, 1] > 0.5


def test_xgb_requires_weights():
    X, y, _ = _toy_data()
    with pytest.raises(MissingSampleWeightError):
        XGBoostModel().fit(X, y)


def test_xgb_class_weight_is_the_precision_knob():
    X, y, w = _toy_data()
    means = {}
    for cw in (0.25, 4.0):
        m = XGBoostModel(n_estimators=30, max_depth=3, class_weight=cw)
        m.fit(X, y, sample_weight=w)
        means[cw] = m.predict_scores(X).mean()
    assert means[0.25] < means[4.0]
    # "balanced" is accepted; invalid values use the shared errors
    XGBoostModel(class_weight="balanced").fit(X, y, sample_weight=w)
    with pytest.raises(ConfigError):
        XGBoostModel(class_weight="bogus")
    with pytest.raises(ConfigError):
        XGBoostModel(class_weight=-1.0)


def test_xgb_single_class_cell_constant_score():
    X, _, w = _toy_data()
    m = XGBoostModel(n_estimators=5)
    m.fit(X, np.ones(len(X), dtype=bool), sample_weight=w)
    assert np.all(m.predict_scores(X) == 1.0)
    assert m.feature_importances() is None


def test_xgb_device_validation_and_no_silent_cpu_fallback():
    X, y, w = _toy_data()
    with pytest.raises(ConfigError, match="device"):
        XGBoostModel(device="tpu")
    # this test environment has no GPU: a cuda fit must refuse loudly,
    # not silently train on CPU under a cuda config identity
    m = XGBoostModel(n_estimators=5, device="cuda")
    with pytest.raises(ConfigError, match="actually.*trained on"):
        m.fit(X, y, sample_weight=w)


def test_xgb_feature_importances_normalized():
    X, y, w = _toy_data()
    m = XGBoostModel(n_estimators=30, max_depth=3)
    m.fit(X, y, sample_weight=w)
    imp = m.feature_importances()
    assert imp is not None and len(imp) == 2
    assert imp.sum() == pytest.approx(1.0)


# --- regressor ------------------------------------------------------------


def test_xgb_regressor_quantile_ranks_signal_and_winsorizes():
    rng = np.random.default_rng(1)
    X, _, w = _toy_data(with_nan=False)
    y = 0.3 * X["book_to_market_rank"].to_numpy() + 0.05 * rng.normal(
        size=len(X)
    )
    y[0] = 40.0  # absurd outlier
    m = XGBoostRegressorModel(
        n_estimators=30, max_depth=3, objective="quantile", alpha=0.25,
        winsorize=0.05,
    )
    m.fit(X, y, sample_weight=w)
    lo, hi = m.winsor_bounds_
    assert hi < 40.0
    scores = m.predict_scores(X)
    assert np.corrcoef(scores, X["book_to_market_rank"])[0, 1] > 0.5
    assert m.probabilistic is False
    assert m.target == "continuous"
    assert model_target("xgboost_regressor") == "continuous"


@pytest.mark.parametrize(
    "params, message",
    [
        ({"objective": "poisson"}, "objective"),
        ({"alpha": 0.0}, "alpha"),
        ({"winsorize": 0.7}, "winsorize"),
        ({"n_estimators": 0}, "n_estimators"),
        ({"max_depth": 0}, "max_depth"),
        ({"device": "rocm"}, "device"),
    ],
)
def test_xgb_regressor_param_validation(params, message):
    with pytest.raises(ConfigError, match=message):
        XGBoostRegressorModel(**params)


def test_registry_builds_xgb_and_rejects_cross_family_params():
    m = build_model("xgboost", {"n_estimators": 10, "gamma": 0.1}, seed=1)
    assert isinstance(m, XGBoostModel)
    r = build_model(
        "xgboost_regressor", {"objective": "absoluteerror"}, seed=1
    )
    assert isinstance(r, XGBoostRegressorModel)
    with pytest.raises(ConfigError, match="unknown params"):
        build_model("xgboost", {"num_leaves": 15}, seed=1)  # a lgbm knob
    with pytest.raises(ConfigError, match="unknown params"):
        build_model("xgboost_regressor", {"class_weight": 0.5}, seed=1)


# --- end to end through the harness --------------------------------------


def test_xgb_classifier_run_end_to_end(data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        {
            "name": "xgb_e2e",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": "label_3y_beat_spy",
            "feature_groups": ["ranks"],
            "model": {"name": "xgboost", "n_estimators": 20, "max_depth": 3},
            "top_k": [5],
            "precision_targets": [0.5],
        }
    )
    summary = run_experiment(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["status"] == "completed"
    assert math.isfinite(summary["pooled_metrics"]["precision_at_5"])
    assert math.isfinite(summary["pooled_metrics"]["brier"])
    assert (tmp_path / "reports" / "xgb_e2e_importances.csv").exists()


def test_xgb_regressor_run_end_to_end(data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        {
            "name": "xgb_reg_e2e",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": "fwd_3y_cagr",
            "eval_label": "label_3y_cagr_ge_8",
            "feature_groups": ["ranks"],
            "model": {
                "name": "xgboost_regressor",
                "n_estimators": 20,
                "max_depth": 3,
                "objective": "quantile",
                "alpha": 0.4,
            },
            "top_k": [5],
        }
    )
    summary = run_experiment(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["status"] == "completed"
    pooled = summary["pooled_metrics"]
    assert math.isfinite(pooled["fwd_at_5"])
    assert math.isnan(pooled["brier"])  # returns, not probabilities
    assert "regression reframe" in summary["report_path"].read_text()
