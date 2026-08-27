"""Per-fold feature-importance artifacts: models that expose
feature_importances() get a reports/<run>_importances.csv (per fold +
cross-fold mean, sorted) and an Interpretability section entry — the
triage list for importance-guided feature subsets."""

import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.runner import run_experiment

VERSION = "dataset_v0.0-test"


def _run(model_table, data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        {
            "name": f"imp_{model_table['name']}",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": "label_3y_beat_spy",
            "feature_groups": ["features", "ranks"],
            "model": model_table,
            "top_k": [5],
        }
    )
    return run_experiment(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )


def test_forest_run_writes_importances_artifact(data_root, tmp_path):
    summary = _run(
        {"name": "random_forest", "n_estimators": 20, "min_samples_leaf": 5},
        data_root,
        tmp_path,
    )
    imp_path = tmp_path / "reports" / "imp_random_forest_importances.csv"
    assert imp_path.exists()
    df = pd.read_csv(imp_path)
    assert list(df.columns[:2]) == ["feature", "mean_importance"]
    # one column per fold (fixture: 2016, 2017), 4 features selected
    assert {"fold_2016", "fold_2017"} <= set(df.columns)
    assert len(df) == 4
    # sorted descending by mean importance, and normalized per fold
    assert df["mean_importance"].is_monotonic_decreasing
    assert df["fold_2016"].sum() == pytest.approx(1.0)
    report = summary["report_path"].read_text()
    assert "imp_random_forest_importances.csv" in report
    assert "Interpretability artifacts" in report


def test_lightgbm_run_writes_importances_artifact(data_root, tmp_path):
    _run(
        {
            "name": "lightgbm",
            "n_estimators": 20,
            "num_leaves": 4,
            "min_child_samples": 5,
        },
        data_root,
        tmp_path,
    )
    imp_path = tmp_path / "reports" / "imp_lightgbm_importances.csv"
    assert imp_path.exists()


def test_baselines_have_no_importances(data_root, tmp_path):
    summary = _run({"name": "majority_class"}, data_root, tmp_path)
    assert not (
        tmp_path / "reports" / "imp_majority_class_importances.csv"
    ).exists()
    assert "importances" not in summary["report_path"].read_text()
