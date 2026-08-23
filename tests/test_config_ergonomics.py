"""Config ergonomics: derived default names, horizon inference from the
label, and hierarchical feature selection (groups ⊃ families ⊃ columns)."""

import pytest

from harness.config import ExperimentConfig, FeatureSpec, infer_horizon_years
from harness.dataset import Dataset
from harness.errors import ConfigError, DatasetValidationError
from harness.model_store import ModelBundle
from harness.runner import run_experiment
from harness.sweep import SweepConfig

VERSION = "dataset_v0.0-test"


def _raw(**overrides):
    raw = {
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return raw


# --- default name -------------------------------------------------------


def test_omitted_name_is_derived():
    cfg = ExperimentConfig.from_dict(_raw())
    assert cfg.name == f"decision_tree_ranks_3y_beat_spy_{cfg.identity_hash}"
    assert len(cfg.identity_hash) == 8


def test_derived_name_changes_with_content():
    base = ExperimentConfig.from_dict(_raw())
    edited = ExperimentConfig.from_dict(_raw(model={"name": "decision_tree", "max_depth": 4}))
    seeded = ExperimentConfig.from_dict(_raw(seed=1))
    assert len({base.name, edited.name, seeded.name}) == 3


def test_derived_name_ignores_the_name_itself():
    # the same content under an explicit name embeds the same identity hash
    anon = ExperimentConfig.from_dict(_raw())
    named = ExperimentConfig.from_dict(_raw(name="my_experiment"))
    assert named.name == "my_experiment"
    assert anon.identity_hash == named.identity_hash


def test_explicit_name_still_respected_and_roundtrips():
    cfg = ExperimentConfig.from_dict(_raw(name="explicit"))
    assert ExperimentConfig.from_dict(cfg.to_raw_dict()) == cfg


def test_derived_name_roundtrips_through_bundle_dict():
    cfg = ExperimentConfig.from_dict(_raw())
    assert ExperimentConfig.from_dict(cfg.to_raw_dict()) == cfg


def test_derived_name_with_features_table_and_families():
    raw = {
        k: v for k, v in _raw().items() if k != "feature_groups"
    } | {"features": {"families": ["ranks/valuation"]}}
    cfg = ExperimentConfig.from_dict(raw)
    assert cfg.name.startswith("decision_tree_ranks-valuation_3y_beat_spy_")


# --- horizon inference --------------------------------------------------


def test_horizon_inferred_from_label():
    assert ExperimentConfig.from_dict(_raw()).horizon_years == 3
    one = ExperimentConfig.from_dict(_raw(label="label_1y_beat_spy"))
    assert one.horizon_years == 1


def test_explicit_horizon_must_agree_with_label():
    cfg = ExperimentConfig.from_dict(_raw(horizon_years=3))
    assert cfg.horizon_years == 3
    with pytest.raises(ConfigError, match="contradicts"):
        ExperimentConfig.from_dict(_raw(horizon_years=1))


def test_uninferrable_label_requires_explicit_horizon():
    with pytest.raises(ConfigError, match="horizon_years must be set"):
        ExperimentConfig.from_dict(_raw(label="label_beat_spy"))


def test_infer_horizon_years_tokenizer():
    assert infer_horizon_years("label_3y_beat_spy") == 3
    assert infer_horizon_years("fwd_1y_cagr") == 1
    assert infer_horizon_years("delisted_in_window_3y") == 3
    assert infer_horizon_years("label_beat_spy") is None
    # `20q` / embedded digits must not be misread as a horizon
    assert infer_horizon_years("revenue_trend_20q") is None


# --- hash stability -----------------------------------------------------


def test_legacy_config_hash_is_unchanged():
    # a fully explicit legacy config must hash exactly as before these
    # fields existed — the trial ledger keys on it
    cfg = ExperimentConfig.from_dict(_raw(name="legacy", horizon_years=3))
    assert "features" not in cfg.canonical_json()
    assert "identity" not in cfg.canonical_json()
    # inferred horizon resolves to the same config, so the same hash
    inferred = ExperimentConfig.from_dict(_raw(name="legacy"))
    assert inferred.config_hash == cfg.config_hash


# --- [features] table parsing -------------------------------------------


def _features_raw(features, **overrides):
    raw = {k: v for k, v in _raw(**overrides).items() if k != "feature_groups"}
    raw["features"] = features
    return raw


def test_features_table_mutually_exclusive_with_legacy_keys():
    raw = _raw() | {"features": {"groups": ["ranks"]}}
    with pytest.raises(ConfigError, match="mixes"):
        ExperimentConfig.from_dict(raw)


def test_features_table_rejects_unknown_keys_and_empty_selection():
    with pytest.raises(ConfigError, match="unknown \\[features\\] keys"):
        ExperimentConfig.from_dict(_features_raw({"group": ["ranks"]}))
    with pytest.raises(ConfigError, match="selects nothing"):
        ExperimentConfig.from_dict(_features_raw({"exclude_columns": ["x"]}))


def test_features_table_rejects_unknown_family_or_group():
    with pytest.raises(ConfigError, match="unknown feature family"):
        ExperimentConfig.from_dict(_features_raw({"families": ["valution"]}))
    with pytest.raises(ConfigError, match="group 'rank'"):
        ExperimentConfig.from_dict(_features_raw({"families": ["rank/valuation"]}))
    with pytest.raises(ConfigError, match="must be within"):
        ExperimentConfig.from_dict(_features_raw({"groups": ["rankings"]}))


def test_features_config_roundtrip_and_distinct_hash():
    cfg = ExperimentConfig.from_dict(
        _features_raw(
            {
                "groups": ["ranks"],
                "exclude_families": ["ranks/valuation"],
                "columns": ["book_to_market"],
            }
        )
    )
    assert ExperimentConfig.from_dict(cfg.to_raw_dict()) == cfg
    legacy = ExperimentConfig.from_dict(_raw())
    assert cfg.config_hash != legacy.config_hash


# --- resolution against the manifest ------------------------------------


def test_family_selects_across_groups(dataset_dir):
    ds = Dataset(dataset_dir)
    spec = FeatureSpec(families=("valuation",))
    # the fixture's four feature columns are all valuation-family; the
    # empty sector_ranks group contributes nothing
    assert ds.select_features(spec) == [
        "book_to_market",
        "earnings_yield",
        "book_to_market_rank",
        "earnings_yield_rank",
    ]


def test_group_qualified_family(dataset_dir):
    ds = Dataset(dataset_dir)
    assert ds.select_features(FeatureSpec(families=("ranks/valuation",))) == [
        "book_to_market_rank",
        "earnings_yield_rank",
    ]


def test_bare_columns_imply_their_parents(dataset_dir):
    ds = Dataset(dataset_dir)
    spec = FeatureSpec(columns=("earnings_yield", "book_to_market_rank"))
    assert ds.select_features(spec) == ["earnings_yield", "book_to_market_rank"]


def test_unknown_column_is_refused(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="not declared"):
        ds.select_features(FeatureSpec(columns=("altman_z",)))


def test_group_with_family_blacklist(dataset_dir):
    ds = Dataset(dataset_dir)
    spec = FeatureSpec(
        groups=("features", "ranks"),
        exclude_families=("features/valuation",),
    )
    assert ds.select_features(spec) == [
        "book_to_market_rank",
        "earnings_yield_rank",
    ]


def test_family_with_column_blacklist(dataset_dir):
    ds = Dataset(dataset_dir)
    spec = FeatureSpec(
        families=("ranks/valuation",), exclude_columns=("earnings_yield_rank",)
    )
    assert ds.select_features(spec) == ["book_to_market_rank"]


def test_blacklist_without_selected_parent_is_an_error(dataset_dir):
    ds = Dataset(dataset_dir)
    # column child: its parent group/family was never selected
    with pytest.raises(DatasetValidationError, match="never selected"):
        ds.select_features(
            FeatureSpec(groups=("ranks",), exclude_columns=("book_to_market",))
        )
    # family child: nothing selected contains it
    with pytest.raises(DatasetValidationError, match="never selected"):
        ds.select_features(
            FeatureSpec(groups=("ranks",), exclude_families=("features/valuation",))
        )


def test_family_absent_from_manifest_is_an_error(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="no columns"):
        ds.select_features(FeatureSpec(families=("solvency",)))


def test_excluding_everything_is_an_error(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="left no columns"):
        ds.select_features(
            FeatureSpec(
                groups=("ranks",), exclude_families=("ranks/valuation",)
            )
        )


# --- sweeps -------------------------------------------------------------


def _sweep_raw(**overrides):
    raw = {
        "name": "erg_sweep",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "cells": [{"label": "label_3y_beat_spy"}],
        "model": {"name": "decision_tree"},
        "grid": {"max_depth": [2, 3]},
        "features": {"families": ["ranks/valuation"]},
    }
    raw.update(overrides)
    return raw


def test_sweep_features_table_flows_into_every_run():
    runs = SweepConfig.from_dict(_sweep_raw()).expand()
    assert len(runs) == 2
    assert all(
        r.config.features == FeatureSpec(families=("ranks/valuation",))
        for r in runs
    )
    # cell horizon inferred from the label
    assert all(r.horizon_years == 3 for r in runs)


def test_sweep_features_array_is_the_feature_axis():
    sweep = SweepConfig.from_dict(
        _sweep_raw(
            features=[
                {"families": ["ranks/valuation"]},
                {"groups": ["ranks"], "exclude_columns": ["earnings_yield_rank"]},
            ],
            grid={"max_depth": [2]},
        )
    )
    runs = sweep.expand()
    assert len(runs) == 2
    assert runs[0].config.features == FeatureSpec(families=("ranks/valuation",))
    assert runs[1].config.features == FeatureSpec(
        groups=("ranks",), exclude_columns=("earnings_yield_rank",)
    )
    # the feature axis shows up in the run names, as with [[feature_sets]]
    assert "fs0" in runs[0].config.name and "fs1" in runs[1].config.name


def test_sweep_features_excludes_other_styles():
    with pytest.raises(ConfigError, match="can't be mixed"):
        SweepConfig.from_dict(_sweep_raw(feature_groups=["ranks"]))
    with pytest.raises(ConfigError, match="can't be mixed"):
        SweepConfig.from_dict(
            _sweep_raw(feature_sets=[{"groups": ["ranks"]}])
        )


def test_sweep_features_entries_are_validated():
    with pytest.raises(ConfigError, match="unknown feature family"):
        SweepConfig.from_dict(
            _sweep_raw(features={"families": ["valution"]})
        )
    with pytest.raises(ConfigError, match="selects nothing"):
        SweepConfig.from_dict(_sweep_raw(features={}))


def test_sweep_cell_horizon_mismatch_is_an_error():
    with pytest.raises(ConfigError, match="contradicts"):
        SweepConfig.from_dict(
            _sweep_raw(
                cells=[{"horizon_years": 1, "label": "label_3y_beat_spy"}]
            )
        )
    with pytest.raises(ConfigError, match="must be set"):
        SweepConfig.from_dict(
            _sweep_raw(cells=[{"label": "label_beat_spy"}])
        )


def test_sweep_with_features_runs_end_to_end(data_root, tmp_path):
    from harness.sweep import run_sweep

    sweep = SweepConfig.from_dict(
        _sweep_raw(
            grid={"max_depth": [2]},
            features={
                "families": ["valuation"],
                "exclude_families": ["features/valuation"],
            },
        )
    )
    result = run_sweep(
        sweep,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert result["n_failed"] == 0
    assert len(result["runs"]) == 1


# --- end-to-end ---------------------------------------------------------


def test_runner_with_features_table_and_derived_everything(data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        _features_raw(
            {"families": ["ranks/valuation"], "exclude_columns": ["earnings_yield_rank"]}
        )
    )
    summary = run_experiment(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    assert summary["status"] == "completed"
    bundle = ModelBundle.load(summary["model_bundle"])
    assert bundle.feature_columns == ("book_to_market_rank",)
    assert bundle.train_config == config
