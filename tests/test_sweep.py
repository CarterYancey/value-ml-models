"""Sweep harness: declarative grids expand to ordinary experiment
configs, every expanded run is logged to the trial ledger, one failing
run never stops the sweep, and the summary ranks pooled metrics."""

import json
import math

import pandas as pd
import pytest

from harness.errors import ConfigError
from harness.results import ResultsStore
from harness.seed_report import seed_stats
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


# ---------------------------------------------------------------- [[sets]]


def _sets_dict(**overrides):
    """A sweep whose model params come as whole candidate sets (the
    follow-up to a wide search: re-run its top candidates as units)."""
    raw = _sweep_dict(
        model={"name": "decision_tree"},
        grid={"min_weight_fraction_leaf": [0.01, 0.02]},
        sets=[
            {"max_depth": 2, "class_weight": 0.5},
            {"max_depth": 3, "class_weight": "balanced"},
        ],
    )
    raw["cells"] = raw["cells"][:1]
    raw.update(overrides)
    return raw


def test_sets_are_taken_as_units_and_crossed_with_grid_and_seeds():
    sweep = SweepConfig.from_dict(_sets_dict(seeds=[3, 4]))
    runs = sweep.expand()
    assert len(runs) == 1 * 2 * 2 * 2  # cells x sets x grid x seeds
    for r in runs:
        whole = sweep.param_sets[r.param_set_index]
        # the set travels intact into the run's params ...
        assert all(r.config.model_params[k] == v for k, v in whole.items())
        assert r.set_params == whole
        # ... alongside the grid point crossed with it
        assert r.config.model_params["min_weight_fraction_leaf"] in (0.01, 0.02)
        assert r.grid_params == {
            "min_weight_fraction_leaf":
                r.config.model_params["min_weight_fraction_leaf"]
        }
        assert f"__set{r.param_set_index}__" in r.config.name
    assert {r.param_set_index for r in runs} == {0, 1}
    assert len({r.config.config_hash for r in runs}) == len(runs)


def test_sets_alone_form_the_whole_param_axis():
    raw = _sets_dict(grid={})
    sweep = SweepConfig.from_dict(raw)
    runs = sweep.expand()
    assert len(runs) == 2
    assert [r.config.model_params for r in runs] == list(sweep.param_sets)
    assert all(r.grid_params == {} for r in runs)


def test_single_set_leaves_run_names_unmarked():
    raw = _sets_dict(sets=[{"max_depth": 2}], grid={})
    runs = SweepConfig.from_dict(raw).expand()
    assert len(runs) == 1
    assert "set0" not in runs[0].config.name


def test_no_sets_means_one_implicit_empty_set():
    sweep = SweepConfig.from_dict(_sweep_dict())
    assert sweep.param_sets == ()
    assert sweep.n_param_sets == 1
    runs = sweep.expand()
    assert all(r.param_set_index == 0 and r.set_params == {} for r in runs)
    assert not any("__set" in r.config.name for r in runs)


def test_set_and_fixed_param_collision_rejected():
    raw = _sets_dict(model={"name": "decision_tree", "class_weight": 1.0})
    with pytest.raises(ConfigError, match="both fixed in \\[model\\]"):
        SweepConfig.from_dict(raw)


def test_set_and_grid_param_collision_rejected():
    raw = _sets_dict(grid={"max_depth": [2, 3]})
    with pytest.raises(ConfigError, match="both swept in \\[grid\\]"):
        SweepConfig.from_dict(raw)


def test_set_and_random_param_collision_rejected():
    raw = _sets_dict(
        random={"class_weight": {"low": 0.1, "high": 1.0}}, n_samples=2
    )
    with pytest.raises(ConfigError, match="both in \\[random\\]"):
        SweepConfig.from_dict(raw)


def test_malformed_sets_rejected():
    with pytest.raises(ConfigError, match="duplicate \\[\\[sets\\]\\]"):
        SweepConfig.from_dict(
            _sets_dict(sets=[{"max_depth": 2}, {"max_depth": 2}])
        )
    with pytest.raises(ConfigError, match="is empty"):
        SweepConfig.from_dict(_sets_dict(sets=[{"max_depth": 2}, {}]))
    with pytest.raises(ConfigError, match="array of tables"):
        SweepConfig.from_dict(_sets_dict(sets={"max_depth": 2}))
    with pytest.raises(ConfigError, match="array of tables"):
        SweepConfig.from_dict(_sets_dict(sets=[2, 3]))


def test_sets_misplaced_under_grid_header_rejected(tmp_path):
    # a bare `sets = [...]` below [grid] is TOML for grid.sets — a whole
    # dictionary as a grid value is never what was meant
    lines = [
        'name = "oops"',
        f'dataset_version = "{VERSION}"',
        'scheme = "walkforward"',
        'feature_groups = ["ranks"]',
        "[[cells]]",
        'label = "label_3y_beat_spy"',
        "[model]",
        'name = "decision_tree"',
        "[grid]",
        "class_weight = [1.0, 0.5]",
        "sets = [{max_depth = 2}, {max_depth = 3}]",
    ]
    path = tmp_path / "oops.toml"
    path.write_text("\n".join(lines))
    with pytest.raises(ConfigError, match="grid.sets holds tables"):
        SweepConfig.from_file(path)


def test_sets_are_part_of_the_sweep_identity():
    a = SweepConfig.from_dict(_sets_dict(name=""))
    b = SweepConfig.from_dict(
        _sets_dict(name="", sets=[{"max_depth": 2, "class_weight": 0.25}])
    )
    assert a.identity_hash != b.identity_hash
    assert a.name != b.name


def test_sets_from_toml_both_spellings(tmp_path):
    head = [
        'name = "sets_sweep"',
        f'dataset_version = "{VERSION}"',
        'scheme = "walkforward"',
        'feature_groups = ["ranks"]',
        "precision_targets = [0.5]",
        "seeds = [1, 2]",
    ]
    # one inline table per line — the compact form for pasted candidates
    inline = head + [
        "sets = [",
        '  {max_depth = 2, class_weight = 0.5},',
        '  {max_depth = 3, class_weight = "balanced"},',
        "]",
        "[[cells]]",
        'label = "label_3y_beat_spy"',
        "[model]",
        'name = "decision_tree"',
    ]
    # the array-of-tables form
    tables = head + [
        "[[cells]]",
        'label = "label_3y_beat_spy"',
        "[model]",
        'name = "decision_tree"',
        "[[sets]]",
        "max_depth = 2",
        "class_weight = 0.5",
        "[[sets]]",
        "max_depth = 3",
        'class_weight = "balanced"',
    ]
    parsed = []
    for i, lines in enumerate((inline, tables)):
        path = tmp_path / f"s{i}.toml"
        path.write_text("\n".join(lines))
        parsed.append(SweepConfig.from_file(path))
    assert parsed[0] == parsed[1]
    assert parsed[0].param_sets == (
        {"max_depth": 2, "class_weight": 0.5},
        {"max_depth": 3, "class_weight": "balanced"},
    )
    assert len(parsed[0].expand()) == 2 * 2  # sets x seeds


def test_sets_sweep_runs_end_to_end(data_root, tmp_path):
    sweep = SweepConfig.from_dict(_sets_dict(grid={}, seeds=[3, 4]))
    results = tmp_path / "results.csv"
    out = run_sweep(
        sweep,
        data_root=data_root,
        results_path=results,
        reports_dir=tmp_path / "reports",
        sweep_config_path="sweeps/sets.toml",
    )
    assert out["n_failed"] == 0
    assert len(out["runs"]) == 4
    df = pd.read_csv(out["summary_csv"])
    assert sorted(df["param_set"].unique()) == [0, 1]
    # the set each run took is spelled out in the summary, not just indexed
    spelled = {json.loads(s)["max_depth"] for s in df["set_params"]}
    assert spelled == {2, 3}
    md = out["summary_md"].read_text()
    assert "parameter sets (2, each taken as a unit)" in md
    assert "| param_set |" in md
    # every run in the ledger: 2 sets x 2 seeds x 2 folds
    store = ResultsStore(results).load()
    assert len(store) == 8 and store["config_hash"].nunique() == 4


# ------------------------------------------------ multi-seed aggregation


def test_seed_stats_spread_and_t_interval():
    st = seed_stats([0.5, 0.6, 0.7])
    assert st["n"] == 3
    assert st["mean"] == pytest.approx(0.6)
    assert st["std"] == pytest.approx(0.1)
    assert (st["min"], st["max"]) == (0.5, 0.7)
    # t(0.975, df=2) = 4.303: half-width 4.303 * 0.1 / sqrt(3)
    assert st["ci95_low"] == pytest.approx(0.6 - 4.302653 * 0.1 / 3 ** 0.5, rel=1e-5)
    assert st["ci95_high"] == pytest.approx(0.6 + 4.302653 * 0.1 / 3 ** 0.5, rel=1e-5)
    # one seed: a point, no spread
    one = seed_stats([0.4])
    assert one["n"] == 1 and one["mean"] == 0.4
    assert all(math.isnan(one[k]) for k in ("std", "ci95_low", "ci95_high"))
    # metrics that don't apply (NaN) or aren't numeric are dropped
    assert seed_stats([float("nan"), 0.2, "balanced"])["n"] == 1


def test_candidate_is_the_run_minus_its_seed():
    sweep = SweepConfig.from_dict(_sweep_dict(seeds=[3, 4]))
    runs = sweep.expand()
    for r in runs:
        assert r.config.name == f"{r.candidate}__s{r.seed}"
    # 2 cells x 2 grid points = 4 candidates, each with both seeds
    by_cand = {}
    for r in runs:
        by_cand.setdefault(r.candidate, set()).add(r.seed)
    assert len(by_cand) == 4
    assert all(seeds == {3, 4} for seeds in by_cand.values())
    # single seed: candidate and run coincide, nothing to aggregate
    single = SweepConfig.from_dict(_sweep_dict()).expand()
    assert all(r.candidate == r.config.name for r in single)


def test_single_seed_sweep_writes_no_candidate_reports(data_root, tmp_path):
    raw = _sweep_dict()
    raw["cells"] = raw["cells"][:1]
    out = run_sweep(
        SweepConfig.from_dict(raw),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert out["candidates"] == [] and out["candidate_reports"] == {}
    assert out["summary_seeds_csv"] is None
    sweep_dir = tmp_path / "reports" / "sweeps" / "mini_sweep"
    assert not (sweep_dir / "seeds").exists()
    assert all((sweep_dir / f"{o['run']}.md").exists() for o in out["runs"])


def test_multi_seed_sweep_reports_per_candidate(data_root, tmp_path):
    raw = _sweep_dict(seeds=[3, 4, 5])
    raw["cells"] = raw["cells"][:1]
    sweep = SweepConfig.from_dict(raw)
    reports = tmp_path / "reports"
    out = run_sweep(
        sweep,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=reports,
        sweep_config_path="sweeps/seeds.toml",
    )
    assert out["n_failed"] == 0 and len(out["runs"]) == 6
    sweep_dir = reports / "sweeps" / "mini_sweep"

    # per-seed run reports are detail, under seeds/; the sweep directory
    # holds one seed-stability report per candidate (2 grid points)
    for o in out["runs"]:
        assert (sweep_dir / "seeds" / f"{o['run']}.md").exists()
        assert not (sweep_dir / f"{o['run']}.md").exists()
    assert len(out["candidates"]) == 2
    for cand in out["candidates"]:
        assert cand["completed_seeds"] == [3, 4, 5]
        path = out["candidate_reports"][cand["candidate"]]
        assert path == sweep_dir / f"{cand['candidate']}.md"
        md = path.read_text()
        assert "# Seed stability" in md
        assert "## Pooled metrics across seeds" in md
        assert "## Per-seed pooled values" in md
        assert "## Era slices across seeds" in md
        assert "model selection on walk-forward folds" in md
        # the rank metric's spread is computed over the three seeds
        st = cand["pooled"]["recall_at_prec_0.5"]
        assert st["n"] == 3
        assert st["min"] <= st["mean"] <= st["max"]
        vals = [r["pooled_metrics"]["recall_at_prec_0.5"] for r in cand["runs"]]
        assert st["mean"] == pytest.approx(sum(vals) / 3)
        # era slices: one row per walk-forward fold, each over 3 seeds
        assert sorted(cand["era"]) == [2016, 2017]
        assert cand["era"][2016]["recall_at_prec_0.5"]["n"] == 3

    # the candidate-level CSV carries every metric's statistics ...
    seeds_df = pd.read_csv(out["summary_seeds_csv"])
    assert len(seeds_df) == 2
    for stat in ("n", "mean", "std", "min", "max", "ci95_low", "ci95_high"):
        assert f"recall_at_prec_0.5_{stat}" in seeds_df.columns
    assert (seeds_df["recall_at_prec_0.5_n"] == 3).all()
    assert (seeds_df["seeds_completed"] == "3/3").all()
    means = seeds_df["recall_at_prec_0.5_mean"].tolist()
    assert means == sorted(means, reverse=True)
    # ... the per-run CSV still lists every run ...
    runs_df = pd.read_csv(out["summary_csv"])
    assert len(runs_df) == 6 and "candidate" in runs_df.columns
    # ... and the markdown ranks candidates, not runs
    md = out["summary_md"].read_text()
    assert "## Ranked candidates" in md
    assert "| candidate " in md
    assert "recall_at_prec_0.5_mean" in md and "recall_at_prec_0.5_ci95_low" in md
    assert "only as good as its worst seed" in md
