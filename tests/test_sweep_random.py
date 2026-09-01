"""Random search in the sweep harness: [random] distribution specs are
validated, sampling is a pure function of the sweep content +
search_seed, draws cross with the grid and every other axis, and the
summary carries the sampled values."""

import json

import pytest

from harness.errors import ConfigError
from harness.sweep import SweepConfig, run_sweep

VERSION = "dataset_v0.0-test"


def _sweep_dict(**overrides):
    raw = {
        "name": "mini_random_sweep",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "folds": "all",
        "feature_groups": ["ranks"],
        "seeds": [3],
        "top_k": [5],
        "precision_targets": [0.5],
        "cells": [{"horizon_years": 3, "label": "label_3y_beat_spy"}],
        "model": {"name": "decision_tree", "min_weight_fraction_leaf": 0.02},
        "grid": {"class_weight": [1.0, 0.5]},
        "random": {
            "max_depth": {"low": 2, "high": 5, "int": True},
            "ccp_alpha": {"low": 1e-4, "high": 1e-1, "log": True},
        },
        "n_samples": 3,
        "search_seed": 9,
    }
    raw.update(overrides)
    return raw


# --- parsing --------------------------------------------------------------


def test_random_requires_n_samples():
    with pytest.raises(ConfigError, match="n_samples"):
        SweepConfig.from_dict(_sweep_dict(n_samples=0))


def test_n_samples_without_random_rejected():
    raw = _sweep_dict()
    del raw["random"]
    with pytest.raises(ConfigError, match="n_samples is set"):
        SweepConfig.from_dict(raw)


def test_random_collision_with_grid_and_model():
    raw = _sweep_dict()
    raw["random"]["class_weight"] = {"choices": [0.5]}
    with pytest.raises(ConfigError, match="both"):
        SweepConfig.from_dict(raw)
    raw = _sweep_dict()
    raw["random"]["min_weight_fraction_leaf"] = {"low": 0.0, "high": 0.1}
    with pytest.raises(ConfigError, match="both"):
        SweepConfig.from_dict(raw)


@pytest.mark.parametrize(
    "spec, message",
    [
        ({"low": 5, "high": 2}, "low < high"),
        ({"low": 2}, "low and high"),
        ({"low": 0.0, "high": 1.0, "log": True}, "log"),
        ({"low": 1.5, "high": 4.0, "int": True}, "int"),
        ({"choices": []}, "non-empty"),
        ({"choices": [1], "low": 0}, "mixes"),
        ({"low": 1, "high": 4, "step": 1}, "unknown keys"),
        ("not-a-table", "must be a table"),
    ],
)
def test_bad_random_specs_rejected(spec, message):
    raw = _sweep_dict()
    raw["random"] = {"max_depth": spec}
    with pytest.raises(ConfigError, match=message):
        SweepConfig.from_dict(raw)


# --- sampling & expansion -------------------------------------------------


def test_expansion_crosses_grid_and_draws():
    sweep = SweepConfig.from_dict(_sweep_dict())
    runs = sweep.expand()
    assert len(runs) == 1 * 2 * 3  # cells x grid x draws
    # draw index appears in the run name; sampled values land in params
    assert any("__r0" in r.config.name for r in runs)
    for r in runs:
        assert 2 <= r.config.model_params["max_depth"] <= 5
        assert isinstance(r.config.model_params["max_depth"], int)
        assert 1e-4 <= r.config.model_params["ccp_alpha"] <= 1e-1
        assert set(r.sampled_params) == {"max_depth", "ccp_alpha"}


def test_sampling_is_deterministic():
    a = SweepConfig.from_dict(_sweep_dict()).expand()
    b = SweepConfig.from_dict(_sweep_dict()).expand()
    assert [r.config.config_hash for r in a] == [
        r.config.config_hash for r in b
    ]


def test_search_seed_changes_draws_and_identity():
    base = SweepConfig.from_dict(_sweep_dict())
    other = SweepConfig.from_dict(_sweep_dict(search_seed=10))
    assert base.identity_hash != other.identity_hash
    assert base.sample_draws() != other.sample_draws()


def test_gridonly_identity_hash_ignores_random_fields():
    """A sweep with no [random] must keep its historical identity hash —
    the new payload keys are only serialized when a [random] table
    exists (search_seed alone changes nothing)."""
    raw = _sweep_dict()
    del raw["random"]
    del raw["n_samples"]
    del raw["search_seed"]
    plain = SweepConfig.from_dict(raw)
    seeded = SweepConfig.from_dict({**raw, "search_seed": 42})
    assert plain.identity_hash == seeded.identity_hash


def test_choices_draws_stay_within_choices():
    raw = _sweep_dict()
    raw["random"] = {"criterion": {"choices": ["gini", "entropy"]}}
    sweep = SweepConfig.from_dict(raw)
    for draw in sweep.sample_draws():
        assert draw["criterion"] in ("gini", "entropy")


# --- end to end -----------------------------------------------------------


def test_random_sweep_runs_and_summary_carries_draws(data_root, tmp_path):
    raw = _sweep_dict(n_samples=2)
    raw["grid"] = {}
    sweep = SweepConfig.from_dict(raw)
    result = run_sweep(
        sweep,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert result["n_failed"] == 0
    assert len(result["runs"]) == 2
    md = result["summary_md"].read_text()
    assert "random search" in md
    assert "sampled_params" in md
    import pandas as pd

    df = pd.read_csv(result["summary_csv"])
    assert "sampled_params" in df.columns
    sampled = [json.loads(s) for s in df["sampled_params"]]
    assert all({"max_depth", "ccp_alpha"} == set(s) for s in sampled)
