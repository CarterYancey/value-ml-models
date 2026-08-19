"""Sweep harness: declarative grids expand to ordinary experiment
configs, every expanded run is logged to the trial ledger, one failing
run never stops the sweep, and the summary ranks pooled metrics."""

import json

import pandas as pd
import pytest

from harness.errors import ConfigError
from harness.results import ResultsStore
from harness.sweep import SweepConfig, run_sweep

VERSION = "dataset_v0.0-test"


def _sweep_dict(**overrides):
    raw = {
        "name": "mini_sweep",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "folds": "all",
        "feature_groups": ["ranks"],
        "seeds": [3],
        "top_k": [5],
        "precision_targets": [0.5],
        "cells": [
            {"horizon_years": 3, "label": "label_3y_beat_spy"},
            {"horizon_years": 3, "label": "label_3y_cagr_ge_8"},
        ],
        "model": {"name": "decision_tree", "min_weight_fraction_leaf": 0.02},
        "grid": {"max_depth": [2, 3]},
    }
    raw.update(overrides)
    return raw


def test_expansion_cells_times_grid_times_seeds():
    sweep = SweepConfig.from_dict(_sweep_dict(seeds=[3, 4]))
    runs = sweep.expand()
    assert len(runs) == 2 * 2 * 2  # cells x grid x seeds
    names = [r.config.name for r in runs]
    assert len(set(names)) == len(names)
    # every expanded config carries the sweep's shared settings
    for r in runs:
        assert r.config.dataset_version == VERSION
        assert r.config.precision_targets == (0.5,)
        assert r.config.model_params["min_weight_fraction_leaf"] == 0.02
        assert r.config.model_params["max_depth"] in (2, 3)
    # distinct grid points get distinct config hashes
    assert len({r.config.config_hash for r in runs}) == len(runs)


def test_expansion_respects_max_runs():
    sweep = SweepConfig.from_dict(_sweep_dict(max_runs=3))
    with pytest.raises(ConfigError, match="max_runs"):
        sweep.expand()


def test_grid_and_fixed_param_collision_rejected():
    raw = _sweep_dict()
    raw["model"]["max_depth"] = 3
    with pytest.raises(ConfigError, match="both fixed"):
        SweepConfig.from_dict(raw)


def test_feature_sets_and_top_level_groups_are_exclusive():
    raw = _sweep_dict(feature_sets=[{"groups": ["ranks"]}])
    with pytest.raises(ConfigError, match="not both"):
        SweepConfig.from_dict(raw)


def test_unknown_fields_rejected():
    with pytest.raises(ConfigError, match="unknown fields"):
        SweepConfig.from_dict(_sweep_dict(train_test_split=0.2))


def test_default_rank_metric_prefers_precision_floor():
    assert (
        SweepConfig.from_dict(_sweep_dict()).rank_metric == "recall_at_prec_0.5"
    )
    assert (
        SweepConfig.from_dict(_sweep_dict(precision_targets=[])).rank_metric
        == "precision_at_5"
    )


def test_sweep_runs_end_to_end(data_root, tmp_path):
    sweep = SweepConfig.from_dict(_sweep_dict())
    results = tmp_path / "results.csv"
    reports = tmp_path / "reports"
    out = run_sweep(
        sweep,
        data_root=data_root,
        results_path=results,
        reports_dir=reports,
        sweep_config_path="sweeps/mini.toml",
    )
    assert out["n_failed"] == 0
    assert len(out["runs"]) == 4
    assert all(o["status"] == "completed" for o in out["runs"])
    # every run produced its own full report in the sweep directory
    sweep_dir = reports / "sweeps" / "mini_sweep"
    for o in out["runs"]:
        assert (sweep_dir / f"{o['run']}.md").exists()
        assert o["pooled_metrics"]["recall_at_prec_0.5"] >= 0.0

    # summary: markdown + csv, ranked by the sweep's metric
    assert out["summary_md"].exists() and out["summary_csv"].exists()
    md = out["summary_md"].read_text()
    assert "model selection on walk-forward folds" in md
    assert "configurations ever tried" in md
    df = pd.read_csv(out["summary_csv"])
    assert len(df) == 4
    ranked = df["recall_at_prec_0.5"].tolist()
    assert ranked == sorted(ranked, reverse=True)

    # the trial ledger saw every run: 4 configs x 2 walk-forward folds
    store = ResultsStore(results).load()
    assert len(store) == 8
    assert (store["status"] == "completed").all()
    assert store["config_hash"].nunique() == 4
    # config_path points back into the sweep file per expanded run
    assert store["config_path"].str.startswith("sweeps/mini.toml#").all()


def test_sweep_isolates_failing_runs(data_root, tmp_path):
    raw = _sweep_dict(grid={"max_depth": [0, 2]})  # 0 → ConfigError at build
    raw["cells"] = raw["cells"][:1]
    sweep = SweepConfig.from_dict(raw)
    results = tmp_path / "results.csv"
    out = run_sweep(
        sweep,
        data_root=data_root,
        results_path=results,
        reports_dir=tmp_path / "reports",
    )
    assert len(out["runs"]) == 2
    assert out["n_failed"] == 1
    statuses = {o["status"] for o in out["runs"]}
    assert statuses == {"completed", "failed"}
    md = out["summary_md"].read_text()
    assert "## Failures" in md
    # the failed run is in the ledger too — failed trials count
    store = ResultsStore(results).load()
    assert (store["status"] == "failed").any()


def test_sweep_from_toml_file(tmp_path):
    raw = _sweep_dict()
    lines = [
        f'name = "{raw["name"]}"',
        f'dataset_version = "{raw["dataset_version"]}"',
        'scheme = "walkforward"',
        'feature_groups = ["ranks"]',
        "precision_targets = [0.5]",
        "[[cells]]",
        "horizon_years = 3",
        'label = "label_3y_beat_spy"',
        "[model]",
        'name = "decision_tree"',
        "[grid]",
        "max_depth = [2, 3]",
    ]
    path = tmp_path / "s.toml"
    path.write_text("\n".join(lines))
    sweep = SweepConfig.from_file(path)
    assert len(sweep.expand()) == 2
    assert sweep.rank_metric == "recall_at_prec_0.5"
    assert json.loads(json.dumps(sweep.base_params)) == {}
