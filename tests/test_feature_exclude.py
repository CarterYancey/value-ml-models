"""Feature blacklist (`exclude_feature_columns`): the tool for "a whole
manifest group minus its unusable columns". Applied after any whitelist;
naming an absent column is an error (a silently ignored exclusion would
leave an unwanted column in the model)."""

import pytest

from harness.config import ExperimentConfig
from harness.dataset import Dataset
from harness.errors import DatasetValidationError
from harness.model_store import ModelBundle
from harness.runner import run_experiment
from harness.sweep import SweepConfig

VERSION = "dataset_v0.0-test"


# --- dataset layer ------------------------------------------------------


def test_exclude_removes_columns(dataset_dir):
    ds = Dataset(dataset_dir)
    assert ds.feature_columns(["features"]) == ["book_to_market", "earnings_yield"]
    assert ds.feature_columns(["features"], exclude=["earnings_yield"]) == [
        "book_to_market"
    ]


def test_exclude_applies_after_whitelist(dataset_dir):
    ds = Dataset(dataset_dir)
    cols = ds.feature_columns(
        ["features", "ranks"],
        subset=["book_to_market", "book_to_market_rank"],
        exclude=["book_to_market"],
    )
    assert cols == ["book_to_market_rank"]


def test_exclude_of_absent_column_is_an_error(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="excluded feature columns"):
        ds.feature_columns(["features"], exclude=["not_a_column"])
    # absent because the whitelist already removed it — still an error
    with pytest.raises(DatasetValidationError, match="excluded feature columns"):
        ds.feature_columns(
            ["features"], subset=["book_to_market"], exclude=["earnings_yield"]
        )


def test_excluding_everything_is_an_error(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="left no columns"):
        ds.feature_columns(
            ["features"], exclude=["book_to_market", "earnings_yield"]
        )


# --- config layer -------------------------------------------------------


def _config(**overrides):
    raw = {
        "name": "excl_test",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["features"],
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


def test_config_roundtrip_and_hash():
    base = _config()
    excl = _config(exclude_feature_columns=["earnings_yield"])
    assert excl.exclude_feature_columns == ("earnings_yield",)
    # round-trips through the bundle-embedding dict form
    assert ExperimentConfig.from_dict(excl.to_raw_dict()) == excl
    assert "exclude_feature_columns" not in base.to_raw_dict()
    # hash-stable for configs predating the field; distinct when set
    assert "exclude_feature_columns" not in base.canonical_json()
    assert base.config_hash != excl.config_hash


# --- runner end-to-end --------------------------------------------------


def test_runner_fits_on_reduced_columns(data_root, tmp_path):
    config = _config(exclude_feature_columns=["earnings_yield"])
    summary = run_experiment(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    assert summary["status"] == "completed"
    bundle = ModelBundle.load(summary["model_bundle"])
    assert bundle.feature_columns == ("book_to_market",)


# --- sweep layer --------------------------------------------------------


def test_sweep_feature_sets_carry_exclusions():
    sweep = SweepConfig.from_dict(
        {
            "name": "excl_sweep",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "cells": [{"horizon_years": 3, "label": "label_3y_beat_spy"}],
            "model": {"name": "decision_tree"},
            "grid": {"max_depth": [2]},
            "feature_sets": [
                {"groups": ["features"], "exclude": ["earnings_yield"]},
                {"groups": ["features"]},
            ],
        }
    )
    runs = sweep.expand()
    assert len(runs) == 2
    assert runs[0].config.exclude_feature_columns == ("earnings_yield",)
    assert runs[1].config.exclude_feature_columns == ()


def test_sweep_top_level_exclude_flows_into_every_run():
    sweep = SweepConfig.from_dict(
        {
            "name": "excl_sweep",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "cells": [{"horizon_years": 3, "label": "label_3y_beat_spy"}],
            "model": {"name": "decision_tree"},
            "grid": {"max_depth": [2, 3]},
            "feature_groups": ["features"],
            "exclude_feature_columns": ["earnings_yield"],
        }
    )
    assert all(
        r.config.exclude_feature_columns == ("earnings_yield",)
        for r in sweep.expand()
    )
