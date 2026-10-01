"""`sector` as a model input: a per-row one-hot recoding against a
fixed vocabulary (harness.dataset.CATEGORICAL_FEATURES), carried
unchanged through training, evaluation, the backtest and inference."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from harness.config import ExperimentConfig
from harness.dataset import (
    CATEGORICAL_FEATURES,
    feature_matrix,
    indicator_name,
    model_input_columns,
)
from harness.errors import DatasetValidationError
from harness.runner import run_experiment

SECTORS = CATEGORICAL_FEATURES["sector"]


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a_rank": [0.1, 0.2, 0.3, 0.4],
            "sector": ["Technology", None, "Utilities", "Technology"],
            "b_rank": [0.9, 0.8, np.nan, 0.6],
        }
    )


def test_sector_becomes_indicators_in_place():
    X = feature_matrix(_frame(), ["a_rank", "sector", "b_rank"])
    names = [indicator_name("sector", v) for v in SECTORS]
    assert list(X.columns) == ["a_rank", *names, "b_rank"]
    assert list(X.columns) == model_input_columns(["a_rank", "sector", "b_rank"])
    tech = X["sector=Technology"].tolist()
    assert tech[0] == 1.0 and tech[2] == 0.0 and tech[3] == 1.0
    assert X["sector=Utilities"].tolist()[2] == 1.0
    # one indicator set per row, and a NULL sector is NULL in all of them
    assert X.loc[[0, 2, 3], names].sum(axis=1).tolist() == [1.0, 1.0, 1.0]
    assert X.loc[1, names].isna().all()
    assert all(X[n].dtype == "float64" for n in names)
    # the other columns are untouched
    assert X["a_rank"].tolist() == [0.1, 0.2, 0.3, 0.4]


def test_the_columns_do_not_depend_on_the_frame():
    """A vocabulary learned from the frame would give a test frame with
    one sector other columns than the training frame: the list is fixed."""
    one = feature_matrix(_frame().iloc[[0]], ["sector", "a_rank"])
    all_rows = feature_matrix(_frame(), ["sector", "a_rank"])
    assert list(one.columns) == list(all_rows.columns)
    # no categorical selected: the frame's own columns, unchanged
    plain = feature_matrix(_frame(), ["a_rank", "b_rank"])
    assert list(plain.columns) == ["a_rank", "b_rank"]


def test_unknown_value_and_other_classification_columns_are_refused():
    frame = _frame()
    frame.loc[0, "sector"] = "Conglomerates"
    with pytest.raises(DatasetValidationError, match="outside its vocabulary"):
        feature_matrix(frame, ["sector"])
    sized = _frame().assign(scalemarketcap="6 - Mega")
    with pytest.raises(DatasetValidationError, match="scalemarketcap"):
        feature_matrix(sized, ["a_rank", "scalemarketcap"])


@pytest.fixture()
def sector_root(dataset_dir, tmp_path) -> Path:
    """The miniature dataset with a `sector` feature column: constant
    per stock, one stock without one."""
    root = tmp_path / "datasets"
    out = root / "dataset_v0.0-sector"
    shutil.copytree(dataset_dir, out)
    data = pd.read_parquet(out / "dataset.parquet")
    stocks = sorted(data["permaticker"].unique())
    mapping = {
        pt: (None if i == 0 else SECTORS[i % 4]) for i, pt in enumerate(stocks)
    }
    data["sector"] = data["permaticker"].map(mapping)
    data.to_parquet(out / "dataset.parquet")
    manifest = json.loads((out / "manifest.json").read_text())
    manifest["dataset_version"] = "dataset_v0.0-sector"
    manifest["columns"]["features"].append("sector")
    (out / "manifest.json").write_text(json.dumps(manifest))
    return root


@pytest.mark.parametrize(
    "model",
    [
        {"name": "random_forest", "n_estimators": 20, "max_depth": 3},
        {"name": "lightgbm", "n_estimators": 20, "num_leaves": 4},
        {"name": "xgboost", "n_estimators": 20, "max_depth": 2},
        {"name": "decision_tree", "max_depth": 3},
    ],
    ids=lambda m: m["name"],
)
def test_a_run_with_sector_as_an_input(sector_root, tmp_path, model):
    """Every model family fits and scores with the indicator columns,
    the importances are indexed by them, the bundle keeps the manifest
    name, and the report states the current-state caveat."""
    config = ExperimentConfig.from_dict(
        {
            "name": f"sector_{model['name']}",
            "dataset_version": "dataset_v0.0-sector",
            "scheme": "walkforward",
            "horizon_years": 3,
            "label": "label_3y_beat_spy",
            "model": model,
            "features": {"groups": ["ranks"], "columns": ["sector"]},
        }
    )
    summary = run_experiment(
        config,
        data_root=sector_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    assert summary["status"] == "completed"
    report = Path(summary["report_path"]).read_text()
    assert "categorical model input: `sector`" in report
    assert "current-state" in report
    importances = pd.read_csv(
        tmp_path / "reports" / f"{config.name}_importances.csv"
    )
    assert set(importances["feature"]) == set(
        model_input_columns(["book_to_market_rank", "earnings_yield_rank", "sector"])
    )

    from harness.model_store import ModelBundle

    bundle = ModelBundle.load(summary["model_bundle"])
    assert "sector" in bundle.feature_columns
    data = pd.read_parquet(
        sector_root / "dataset_v0.0-sector" / "dataset.parquet"
    )
    fold_model = next(iter(bundle.fold_models.values()))
    scores = fold_model.predict_scores(
        feature_matrix(data.head(50), bundle.feature_columns)
    )
    assert len(scores) == 50 and np.isfinite(scores).all()
