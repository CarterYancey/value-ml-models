"""Derived labels (harness.derived_labels): label expressions over the
manifest's continuous outcomes, evaluated on the fly by the loader."""

import json

import numpy as np
import pandas as pd
import pytest

from harness.config import ExperimentConfig, infer_horizon_years
from harness.dataset import Dataset, cohort_percent_rank
from harness.derived_labels import (
    COHORT_KEYS,
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


def test_cohort_and_boolean_terms():
    spec = parse_label_expression(
        "cohort_pct( fwd_3y_cagr ) >= 0.9 & label_3y_beat_spy == TRUE"
    )
    assert spec.name == (
        "cohort_pct(fwd_3y_cagr) >= 0.9 & label_3y_beat_spy == true"
    )
    assert spec.cohort_columns == ("fwd_3y_cagr",)
    assert spec.horizon_years == 3


def test_horizon_inference():
    assert infer_horizon_years("fwd_5y_excess_cagr > 0") == 5
    with pytest.raises(ConfigError, match="mixes horizons"):
        parse_label_expression("fwd_3y_cagr >= 0.1 & fwd_5y_cagr >= 0.1")


@pytest.mark.parametrize(
    "expr, match",
    [
        ("fwd_3y_cagr >= ten", "not a number"),
        ("fwd_3y_cagr => 0.1", "cannot parse"),
        ("fwd_3y_cagr >= 0.1 | fwd_3y_cagr < 0", "cannot parse"),
        ("fwd_3y_cagr >= nan", "finite"),
        ("label_3y_beat_spy > true", "== or !="),
        ("cohort_pct(fwd_3y_cagr) >= 90", r"\[0, 1\]"),
        ("cohort_pct(label_3y_beat_spy) == true", "compare it to a number"),
        ("book_to_market >= 1", "horizon"),
    ],
)
def test_malformed_expressions_are_refused(expr, match):
    with pytest.raises(ConfigError, match=match):
        parse_label_expression(expr)


def test_slug_is_filesystem_safe():
    slug = label_slug("cohort_pct(fwd_3y_cagr) >= 0.9 & fwd_3y_cagr > -0.05")
    assert slug == "label_3y_cagr_cpct_ge_0p9_and_3y_cagr_gt_m0p05"
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
        _raw(label="cohort_pct(fwd_3y_cagr) >= 0.9")
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


def test_cohort_percent_rank_matches_percent_rank_semantics():
    data = pd.DataFrame(
        {
            "quarter": ["q1"] * 5 + ["q2"] * 2 + ["q3"],
            "snapshot_kind": ["median"] * 8,
            "x": [0.3, 0.1, 0.1, None, 0.5, 1.0, 2.0, 7.0],
        }
    )
    pct = cohort_percent_rank(data, "x")
    # q1 non-null: 0.1, 0.1, 0.3, 0.5 -> ranks 1, 1, 3, 4 of n=4
    expected = [2 / 3, 0.0, 0.0, np.nan, 1.0, 0.0, 1.0, 0.0]
    np.testing.assert_allclose(pct.to_numpy(dtype=float), expected)


def test_cohort_label_ranks_within_quarter_and_kind(dataset_dir):
    ds = Dataset(dataset_dir)
    expr = "cohort_pct(fwd_3y_cagr) >= 0.5"
    frame = ds.frame([expr, "fwd_3y_cagr", *COHORT_KEYS])
    obs = frame[frame["fwd_3y_cagr"].notna()]
    for _, cohort in obs.groupby(list(COHORT_KEYS)):
        n = len(cohort)
        rank = cohort["fwd_3y_cagr"].rank(method="min")
        pct = (rank - 1) / (n - 1) if n > 1 else rank * 0
        assert (cohort[expr].astype(bool) == (pct >= 0.5)).all()


def test_cohort_purge_drops_train_labels_with_non_train_peers(dataset_dir):
    ds = Dataset(dataset_dir)
    expr = "cohort_pct(fwd_3y_cagr) >= 0.5"
    split = ds.apply_split("walkforward", 2016, 3, columns=[expr])
    # the fixture's cohorts share one snapshot date, so the upstream
    # per-row purge already covers the cohort: nothing more to drop
    assert split.cohort_purged == {expr: 0}

    key = ["permaticker", "snapshot_date", "snapshot_kind"]
    tags = ds._split_tags("walkforward", 3)
    tags = tags[tags["fold"] == 2016].copy()
    meta = ds.frame(list(COHORT_KEYS))
    train_meta = split.train.merge(meta, on=key, how="left")
    victim = train_meta[train_meta[expr].notna()].iloc[0]
    in_cohort = (
        (train_meta["quarter"] == victim["quarter"])
        & (train_meta["snapshot_kind"] == victim["snapshot_kind"])
    ).to_numpy()
    # a cohort peer whose (later) snapshot got it purged upstream
    peer = train_meta[
        in_cohort & (train_meta["permaticker"] != victim["permaticker"]).to_numpy()
    ].iloc[0]
    hit = np.logical_and.reduce([tags[k] == peer[k] for k in key])
    tags.loc[hit, "role"] = "purged"
    keep = ~np.logical_and.reduce([split.train[k] == peer[k] for k in key])
    train = split.train[keep].reset_index(drop=True)
    before = train.copy()
    in_cohort = in_cohort[keep]

    n = ds._cohort_purge(train, tags, ds.derived_label(expr), expr)
    assert n == int((in_cohort & before[expr].notna().to_numpy()).sum()) > 0
    assert train.loc[in_cohort, expr].isna().all()
    # rows of other cohorts keep their labels
    assert train.loc[~in_cohort, expr].equals(before.loc[~in_cohort, expr])


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


def test_cohort_label_run_discloses_the_purge(data_root, tmp_path):
    cfg = ExperimentConfig.from_dict(
        _raw(name="cohort", label="cohort_pct(fwd_3y_cagr) >= 0.9")
    )
    summary = run_experiment(
        cfg, data_root=data_root, results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["status"] == "completed"
    report = (tmp_path / "reports" / "cohort.md").read_text()
    assert "derived label `cohort_pct(fwd_3y_cagr) >= 0.9`" in report
    assert "cohort_purged_train_rows" in report


def test_backtest_refit_waits_for_the_whole_cohort(dataset_dir):
    from types import SimpleNamespace

    from portfolio.signals import _refit_as_of_year

    ds = Dataset(dataset_dir)
    bundle = SimpleNamespace(
        train_config=ExperimentConfig.from_dict(
            _raw(label="cohort_pct(fwd_3y_cagr) >= 0.5")
        ),
        feature_columns=("book_to_market_rank",),
    )
    _, stats = _refit_as_of_year(bundle, ds, 2016, 45)
    # a cohort's label is known once its latest peer's window has closed
    frame = ds.frame(["fwd_3y_cagr", *COHORT_KEYS])
    last = pd.to_datetime(frame["snapshot_date"]).groupby(
        [frame[k] for k in COHORT_KEYS]
    ).transform("max")
    ready = last + pd.DateOffset(years=3) + pd.Timedelta(days=45)
    eligible = frame[(ready <= pd.Timestamp(2016, 1, 1)) & frame["fwd_3y_cagr"].notna()]
    assert stats["n_train_rows"] == len(eligible) > 0
