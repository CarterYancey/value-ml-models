"""The regression reframe (PLAN §8): continuous-target models train on
fwd_* return columns, rank by predicted return, and are evaluated in the
same precision@K frame against a binary eval_label — with guardrails so
label kinds can never be silently coerced in either direction."""

import math

import numpy as np
import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.dataset import Dataset
from harness.errors import (
    ConfigError,
    DatasetValidationError,
    MissingSampleWeightError,
)
from harness.runner import run_experiment
from models.gbm import LightGBMRegressorModel
from models.registry import build_model, check_target_labels, model_target

VERSION = "dataset_v0.0-test"


def _toy_regression_data(n=400, seed=0):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "book_to_market_rank": rng.uniform(0, 1, n),
            "earnings_yield_rank": rng.uniform(0, 1, n),
        }
    )
    y = 0.3 * X["book_to_market_rank"].to_numpy() + 0.05 * rng.normal(size=n)
    w = rng.uniform(0.2, 1.0, n)
    return X, y, w


# --- the model wrapper ----------------------------------------------------


def test_regressor_fits_and_ranks_signal():
    X, y, w = _toy_regression_data()
    model = LightGBMRegressorModel(
        n_estimators=50, num_leaves=7, min_child_samples=10
    )
    model.fit(X, y, sample_weight=w)
    scores = model.predict_scores(X)
    assert len(scores) == len(X)
    # predicted returns should correlate with the generating factor
    assert np.corrcoef(scores, X["book_to_market_rank"])[0, 1] > 0.5
    assert model.probabilistic is False
    assert model.target == "continuous"


def test_regressor_requires_weights():
    X, y, _ = _toy_regression_data()
    with pytest.raises(MissingSampleWeightError):
        LightGBMRegressorModel().fit(X, y)


def test_regressor_rejects_nan_targets():
    X, y, w = _toy_regression_data()
    y = y.copy()
    y[0] = np.nan
    with pytest.raises(ConfigError, match="NaN"):
        LightGBMRegressorModel().fit(X, y, sample_weight=w)


def test_winsorize_clips_training_target_fold_internally():
    X, y, w = _toy_regression_data()
    y = y.copy()
    y[0] = 40.0  # one absurd outlier
    model = LightGBMRegressorModel(
        n_estimators=20, num_leaves=4, min_child_samples=10, winsorize=0.05
    )
    model.fit(X, y, sample_weight=w)
    lo, hi = model.winsor_bounds_
    assert lo == pytest.approx(np.quantile(y, 0.05))
    assert hi == pytest.approx(np.quantile(y, 0.95))
    assert hi < 40.0
    plain = LightGBMRegressorModel(n_estimators=20)
    plain.fit(X, y, sample_weight=w)
    assert plain.winsor_bounds_ is None


@pytest.mark.parametrize(
    "params, message",
    [
        ({"objective": "poisson"}, "objective"),
        ({"alpha": 0.0}, "alpha"),
        ({"alpha": 1.5}, "alpha"),
        ({"winsorize": 0.5}, "winsorize"),
        ({"winsorize": -0.1}, "winsorize"),
        ({"n_estimators": 0}, "n_estimators"),
    ],
)
def test_regressor_param_validation(params, message):
    with pytest.raises(ConfigError, match=message):
        LightGBMRegressorModel(**params)


def test_registry_builds_regressor_and_rejects_class_weight():
    model = build_model(
        "lightgbm_regressor", {"objective": "quantile", "alpha": 0.25}, seed=1
    )
    assert model.target == "continuous"
    with pytest.raises(ConfigError, match="unknown params"):
        build_model("lightgbm_regressor", {"class_weight": 0.5}, seed=1)


def test_regressor_exposes_feature_importances():
    X, y, w = _toy_regression_data()
    model = LightGBMRegressorModel(
        n_estimators=30, num_leaves=5, min_child_samples=10
    )
    model.fit(X, y, sample_weight=w)
    imp = model.feature_importances()
    assert imp is not None and len(imp) == 2
    assert imp.sum() == pytest.approx(1.0)


# --- config / registry coherence -----------------------------------------


def _config_dict(**overrides):
    raw = {
        "name": "reg_test",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "fwd_3y_cagr",
        "eval_label": "label_3y_cagr_ge_8",
        "feature_groups": ["ranks"],
        "model": {
            "name": "lightgbm_regressor",
            "n_estimators": 20,
            "num_leaves": 4,
            "min_child_samples": 5,
        },
        "top_k": [5],
        "precision_targets": [0.5],
    }
    raw.update(overrides)
    return raw


def test_model_target_partition():
    assert model_target("lightgbm_regressor") == "continuous"
    assert model_target("lightgbm") == "binary"
    assert model_target("decision_tree") == "binary"


def test_check_target_labels_requires_and_forbids_eval_label():
    reg = ExperimentConfig.from_dict(_config_dict())
    check_target_labels(reg)  # coherent: continuous model + eval_label
    with pytest.raises(ConfigError, match="eval_label"):
        check_target_labels(
            ExperimentConfig.from_dict(_config_dict(eval_label=""))
        )
    clf = ExperimentConfig.from_dict(
        _config_dict(
            label="label_3y_beat_spy",
            eval_label="label_3y_cagr_ge_8",
            model={"name": "decision_tree", "max_depth": 3},
        )
    )
    with pytest.raises(ConfigError, match="only meaningful"):
        check_target_labels(clf)


def test_eval_label_config_validation():
    with pytest.raises(ConfigError, match="equals label"):
        ExperimentConfig.from_dict(_config_dict(eval_label="fwd_3y_cagr"))
    with pytest.raises(ConfigError, match="1y label"):
        ExperimentConfig.from_dict(_config_dict(eval_label="label_1y_beat_spy"))


def test_eval_label_absent_keeps_config_hash_stable():
    """Configs that never set eval_label must keep their identity — the
    key is only serialized when non-empty."""
    raw = _config_dict(
        label="label_3y_beat_spy",
        eval_label="",
        model={"name": "decision_tree", "max_depth": 3},
    )
    del raw["eval_label"]
    config = ExperimentConfig.from_dict(raw)
    assert "eval_label" not in config.canonical_json()
    assert "eval_label" not in config.to_raw_dict()
    with_it = ExperimentConfig.from_dict(_config_dict())
    assert "eval_label" in with_it.canonical_json()
    # and it round-trips through the bundle-embedding raw dict
    again = ExperimentConfig.from_dict(with_it.to_raw_dict())
    assert again.eval_label == "label_3y_cagr_ge_8"
    assert again.config_hash == with_it.config_hash


# --- fit_data target guardrails ------------------------------------------


def test_fit_data_refuses_kind_mismatches(dataset_dir):
    ds = Dataset(dataset_dir)
    frame = ds.data
    cols = ["book_to_market_rank"]
    with pytest.raises(DatasetValidationError, match="non-binary"):
        ds.fit_data(frame, "fwd_3y_cagr", cols, 3)  # continuous as binary
    with pytest.raises(DatasetValidationError, match="boolean"):
        ds.fit_data(
            frame, "label_3y_beat_spy", cols, 3, target="continuous"
        )
    fit = ds.fit_data(frame, "fwd_3y_cagr", cols, 3, target="continuous")
    assert fit.y.dtype == float
    assert np.isfinite(fit.y).all()


# --- end to end through the harness --------------------------------------


@pytest.fixture(scope="module")
def regression_summary(data_root, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("regression_run")
    config = ExperimentConfig.from_dict(_config_dict())
    summary = run_experiment(
        config,
        data_root=data_root,
        results_path=tmp / "results.csv",
        reports_dir=tmp / "reports",
        models_dir=tmp / "models",
    )
    return summary, tmp, data_root


def test_regression_run_completes_in_precision_frame(regression_summary):
    summary, tmp, _ = regression_summary
    assert summary["status"] == "completed"
    pooled = summary["pooled_metrics"]
    assert math.isfinite(pooled["precision_at_5"])
    # scores are returns, not probabilities: no Brier
    assert math.isnan(pooled["brier"])
    report = summary["report_path"].read_text()
    assert "regression reframe" in report
    assert "label_3y_cagr_ge_8" in report


def test_regression_run_logged_against_eval_cell(regression_summary):
    summary, tmp, _ = regression_summary
    ledger = pd.read_csv(tmp / "results.csv")
    rows = ledger[ledger["run_id"] == summary["run_id"]]
    assert (rows["label"] == "label_3y_cagr_ge_8").all()


def test_regression_bundle_reevaluates(regression_summary):
    from harness.config import EvalConfig
    from harness.evaluate import evaluate_bundle

    summary, tmp, data_root = regression_summary
    result = evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict({"name": "retop", "top_k": [3]}),
        data_root=data_root,
        results_path=tmp / "results.csv",
        reports_dir=tmp / "reports",
    )
    assert result["status"] == "completed"
    fold_metrics = result["fold_results"][0]["metrics"]
    assert "precision_at_3" in fold_metrics


def test_regression_deployment_refit(regression_summary, data_root, tmp_path):
    from harness.deploy import train_deployment_model

    config = ExperimentConfig.from_dict(_config_dict())
    result = train_deployment_model(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        models_dir=tmp_path / "models",
    )
    assert result["status"] == "completed"
    assert result["n_train_rows"] > 0
