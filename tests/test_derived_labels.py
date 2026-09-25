"""Derived labels (harness.derived_labels): label expressions over the
manifest's continuous outcomes, evaluated on the fly by the loader."""

import json

import pytest

from harness.config import ExperimentConfig, infer_horizon_years
from harness.dataset import Dataset
from harness.derived_labels import (
    is_derived_label,
    label_slug,
    normalize_label,
    parse_label_expression,
)
from harness.errors import ConfigError, DatasetValidationError
from harness.results import ResultsStore
from harness.runner import run_experiment
from harness.sweep import SweepConfig

# ------------------------------------------------------------------ parsing


def test_stored_columns_are_not_expressions():
    assert not is_derived_label("label_3y_cagr_ge_10")
    assert not is_derived_label("fwd_3y_cagr")
    assert normalize_label("label_3y_beat_spy") == "label_3y_beat_spy"


def test_canonical_form_ignores_order_spacing_and_duplicates():
    a = normalize_label("fwd_3y_max_drawdown<0.30 & fwd_3y_cagr >= .10")
    b = normalize_label(
        "fwd_3y_cagr>=0.1&fwd_3y_max_drawdown < 0.3 & fwd_3y_cagr >= 0.10"
    )
    assert a == b == "fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3"
    assert normalize_label(a) == a  # idempotent: bundles re-parse it


def test_boolean_terms():
    spec = parse_label_expression(
        "fwd_3y_cagr >= 0.0 & label_3y_beat_spy == TRUE"
    )
    assert spec.name == "fwd_3y_cagr >= 0.0 & label_3y_beat_spy == true"
    assert spec.horizon_years == 3


def test_horizon_inference_takes_the_longest_window():
    assert infer_horizon_years("fwd_5y_excess_cagr > 0") == 5
    mixed = parse_label_expression("fwd_3y_cagr >= 0.1 & fwd_1y_cagr >= 0")
    assert mixed.horizons == (1, 3)
    assert mixed.horizon_years == 3
    assert infer_horizon_years("fwd_1y_cagr >= 0 | fwd_5y_cagr >= 0.1") == 5


def test_or_and_parentheses_normalize_to_a_sum_of_products():
    a = normalize_label(
        "(fwd_3y_cagr >= 0.15 | fwd_3y_excess_cagr >= 0.05) "
        "& fwd_3y_max_drawdown < 0.4"
    )
    b = normalize_label(
        "fwd_3y_max_drawdown < .4 & fwd_3y_excess_cagr >= 0.05 "
        "| fwd_3y_cagr>=0.15&fwd_3y_max_drawdown<0.40"
    )
    assert a == b == (
        "fwd_3y_cagr >= 0.15 & fwd_3y_max_drawdown < 0.4 | "
        "fwd_3y_excess_cagr >= 0.05 & fwd_3y_max_drawdown < 0.4"
    )
    assert normalize_label(a) == a
    # & binds tighter than |
    spec = parse_label_expression(
        "fwd_3y_cagr >= 0 | fwd_3y_cagr < -0.5 & fwd_3y_max_drawdown > 0.9"
    )
    assert sorted(len(c) for c in spec.clauses) == [1, 2]
    # duplicate clauses collapse
    assert normalize_label("fwd_3y_cagr >= 0 | fwd_3y_cagr >= 0.0") == (
        "fwd_3y_cagr >= 0.0"
    )
    assert ExperimentConfig.from_dict(_raw(label=a)).config_hash == (
        ExperimentConfig.from_dict(_raw(label=b)).config_hash
    )


@pytest.mark.parametrize(
    "expr, match",
    [
        ("fwd_3y_cagr >= ten", "not a number"),
        ("fwd_3y_cagr => 0.1", "cannot parse"),
        ("fwd_3y_cagr >= nan", "finite"),
        ("(fwd_3y_cagr >= 0", "unexpected end"),
        ("(fwd_3y_cagr >= 0 fwd_3y_cagr < 1)", "cannot parse"),
        ("fwd_3y_cagr >= 0)", "unexpected"),
        ("fwd_3y_cagr >= 0 &", "unexpected end"),
        ("| fwd_3y_cagr >= 0", "unexpected"),
        ("fwd_3y_cagr >= 0 & & fwd_3y_cagr < 1", "unexpected"),
        ("label_3y_beat_spy > true", "== or !="),
        ("cohort_pct(fwd_3y_cagr) >= 0.9", "cannot parse"),  # removed on purpose
        ("book_to_market >= 1", "horizon"),
    ],
)
def test_malformed_expressions_are_refused(expr, match):
    with pytest.raises(ConfigError, match=match):
        parse_label_expression(expr)


def test_slug_is_filesystem_safe():
    slug = label_slug(
        "fwd_3y_max_drawdown < 0.3 & fwd_3y_cagr > -0.05 | fwd_1y_cagr >= 1"
    )
    assert slug == (
        "label_1y_cagr_ge_1p0_or_3y_cagr_gt_m0p05_and_3y_max_drawdown_lt_0p3"
    )
    assert label_slug("label_3y_beat_spy") == "label_3y_beat_spy"


# --------------------------------------------------------------- configs


def _raw(**overrides) -> dict:
    raw = {
        "name": "test_derived",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "label": "label_3y_cagr_ge_8",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return raw


def test_config_normalizes_label_and_infers_horizon():
    cfg = ExperimentConfig.from_dict(_raw(label="fwd_3y_cagr>=0.08"))
    assert cfg.label == "fwd_3y_cagr >= 0.08"
    assert cfg.horizon_years == 3
    same = ExperimentConfig.from_dict(_raw(label="fwd_3y_cagr >= 0.080"))
    assert same.config_hash == cfg.config_hash
    unnamed = _raw(label="fwd_3y_cagr >= 0.08")
    del unnamed["name"]
    name = ExperimentConfig.from_dict(unnamed).name
    assert all(ch.isalnum() or ch in "_-" for ch in name)


def test_config_roundtrip_keeps_the_label():
    cfg = ExperimentConfig.from_dict(
        _raw(label="fwd_3y_cagr >= 0.1 & label_3y_beat_spy == true")
    )
    again = ExperimentConfig.from_dict(cfg.to_raw_dict())
    assert again.label == cfg.label
    assert again.config_hash == cfg.config_hash


def test_sweep_cells_are_normalized():
    sweep = SweepConfig.from_dict(
        {
            "name": "sw",
            "dataset_version": "dataset_v0.0-test",
            "scheme": "walkforward",
            "cells": [{"label": "fwd_3y_cagr>=0.08"}],
            "feature_groups": ["ranks"],
            "model": {"name": "decision_tree", "max_depth": 2},
        }
    )
    assert tuple(sweep.cells) == ((3, "fwd_3y_cagr >= 0.08", ""),)


# --------------------------------------------------------------- loader


def test_threshold_expression_reproduces_the_stored_rung(dataset_dir):
    ds = Dataset(dataset_dir)
    expr = "fwd_3y_cagr >= 0.08"
    frame = ds.frame([expr, "label_3y_cagr_ge_8"])
    derived, stored = frame[expr], frame["label_3y_cagr_ge_8"]
    assert derived.isna().equals(stored.isna())
    observed = stored.notna()
    assert (derived[observed].astype(bool) == stored[observed].astype(bool)).all()


def test_nulls_propagate_as_unobservable(dataset_dir):
    ds = Dataset(dataset_dir)
    expr = "fwd_3y_cagr >= 0 & label_3y_beat_spy == false"
    frame = ds.frame([expr, "fwd_3y_cagr", "label_3y_beat_spy"])
    unobservable = frame["fwd_3y_cagr"].isna() | frame["label_3y_beat_spy"].isna()
    assert unobservable.any()
    assert frame.loc[unobservable, expr].isna().all()
    obs = frame[~unobservable]
    expected = (obs["fwd_3y_cagr"] >= 0) & ~obs["label_3y_beat_spy"].astype(bool)
    assert (obs[expr].astype(bool) == expected).all()


def test_expressions_are_checked_against_the_manifest(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="labels group"):
        ds.frame(["fwd_3y_max_drawdown < 0.2"])  # not in this dataset
    with pytest.raises(DatasetValidationError, match="labels group"):
        # features are never label sources
        ds.check_label("book_to_market_3y >= 1")
    with pytest.raises(DatasetValidationError, match="labels group"):
        ds.check_label("fwd_5y_cagr >= 0")  # horizon not carried
    with pytest.raises(DatasetValidationError, match="boolean column"):
        ds.frame(["label_3y_beat_spy >= 1"])
    with pytest.raises(DatasetValidationError, match="not a boolean"):
        ds.frame(["fwd_3y_cagr == true"])


def test_fit_data_needs_the_projected_label(dataset_dir):
    ds = Dataset(dataset_dir)
    frame = ds.frame(["book_to_market_rank", "sample_weight_3y"])
    with pytest.raises(DatasetValidationError, match="not a column"):
        ds.fit_data(frame, "fwd_3y_cagr >= 0", ["book_to_market_rank"], 3)


# --------------------------------------------------------------- runner


def test_derived_rung_runs_identically_to_the_stored_rung(data_root, tmp_path):
    results = tmp_path / "results.csv"
    common = dict(data_root=data_root, results_path=results,
                  reports_dir=tmp_path / "reports")
    stored = run_experiment(
        ExperimentConfig.from_dict(_raw(name="stored")), **common
    )
    derived = run_experiment(
        ExperimentConfig.from_dict(_raw(name="derived", label="fwd_3y_cagr >= 0.08")),
        **common,
    )
    assert stored["status"] == derived["status"] == "completed"
    store = ResultsStore(results).load()
    by_exp = {
        exp: [json.loads(m) for m in grp["metrics_json"]]
        for exp, grp in store.groupby("experiment")
    }
    assert by_exp["stored"] == by_exp["derived"]
    assert set(store.loc[store["experiment"] == "derived", "label"]) == {
        "fwd_3y_cagr >= 0.08"
    }


def test_or_semantics_and_null_propagation(dataset_dir):
    ds = Dataset(dataset_dir)
    expr = "fwd_3y_cagr >= 0.3 | label_3y_beat_spy == true & fwd_3y_cagr < 0"
    frame = ds.frame([expr, "fwd_3y_cagr", "label_3y_beat_spy"])
    obs = frame[frame["fwd_3y_cagr"].notna()]
    expected = (obs["fwd_3y_cagr"] >= 0.3) | (
        obs["label_3y_beat_spy"].astype(bool) & (obs["fwd_3y_cagr"] < 0)
    )
    assert (obs[expr].astype(bool) == expected).all()
    assert expected.any() and not expected.all()
    assert frame.loc[frame["fwd_3y_cagr"].isna(), expr].isna().all()


def test_mixed_horizon_label_runs_under_the_longest_horizon(
    dataset_dir, data_root, tmp_path
):
    ds = Dataset(dataset_dir)
    expr = "fwd_3y_cagr >= 0 & fwd_1y_cagr >= -0.1"
    frame = ds.frame([expr, "fwd_3y_cagr", "fwd_1y_cagr"])
    # 3y-observable rows are 1y-observable (the windows nest), so the
    # label is NULL exactly where the governing horizon is
    assert frame[expr].isna().equals(frame["fwd_3y_cagr"].isna())
    # 1y-only rows (3y window past the data) carry no label, not False
    only_1y = frame["fwd_1y_cagr"].notna() & frame["fwd_3y_cagr"].isna()
    assert only_1y.any() and frame.loc[only_1y, expr].isna().all()

    cfg = ExperimentConfig.from_dict(_raw(name="mixed", label=expr))
    assert cfg.horizon_years == 3
    with pytest.raises(ConfigError, match="contradicts"):
        ExperimentConfig.from_dict(_raw(label=expr, horizon_years=1))
    summary = run_experiment(
        cfg, data_root=data_root, results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["status"] == "completed"
    assert summary["folds"] == [2016, 2017]  # the 3y fold calendar
    store = ResultsStore(tmp_path / "results.csv").load()
    assert set(store["horizon_years"].astype(int)) == {3}
    report = (tmp_path / "reports" / "mixed.md").read_text()
    assert "Mixed horizons" in report and "sample_weight_3y" in report
