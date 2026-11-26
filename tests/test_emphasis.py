"""`[emphasis]`: training rows inside a region of feature columns carry
`factor` times their mandatory sample weight (decision 78.6). Test rows
are untouched, the region may read feature columns only, and the
emphasis is part of the config's identity."""

import numpy as np
import pytest

from harness.config import EmphasisSpec, ExperimentConfig, parse_emphasis
from harness.dataset import Dataset, emphasized_weights
from harness.errors import ConfigError
from harness.runner import run_experiment
from harness.sweep import SweepConfig

VERSION = "dataset_v0.0-test"
REGION = {"factor": 3.0, "region": ["book_to_market_rank >= 0.5"]}


def _cfg(**extra):
    raw = {
        "name": "emph",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "random_forest", "n_estimators": 5, "max_depth": 2},
    }
    raw.update(extra)
    return raw


# --- the weights ------------------------------------------------------------


def test_emphasized_weights_multiply_the_region_only():
    w = np.array([1.0, 0.5, 2.0, 0.25])
    inside = np.array([True, False, True, False])
    out = emphasized_weights(w, inside, 3.0)
    assert out.tolist() == [3.0, 0.5, 6.0, 0.25]
    assert w.tolist() == [1.0, 0.5, 2.0, 0.25]  # untouched input
    # the region's share moves from s to s f / (s f + 1 - s)
    s = w[inside].sum() / w.sum()
    assert out[inside].sum() / out.sum() == pytest.approx(3 * s / (3 * s + 1 - s))


# --- the spec ---------------------------------------------------------------


def test_emphasis_spec_parses_strings_and_tables():
    spec = EmphasisSpec.from_table(
        {
            "factor": 3,
            "region": [
                "dist_5y_high <= -0.4",
                {"column": "ocf_positive_frac_20q", "op": ">=", "value": 0.9},
            ],
        },
        "t",
    )
    assert spec.factor == 3.0
    assert [f.describe() for f in spec.region] == [
        "dist_5y_high <= -0.4",
        "ocf_positive_frac_20q >= 0.9",
    ]
    assert spec.describe() == "dist_5y_high <= -0.4 & ocf_positive_frac_20q >= 0.9 x 3"
    # the identity is order-free and the table round-trips
    again = EmphasisSpec.from_table(spec.to_table(), "t")
    assert again == spec
    flipped = EmphasisSpec.from_table(
        {"factor": 3.0, "region": list(reversed(spec.to_table()["region"]))}, "t"
    )
    assert flipped.identity() == spec.identity()
    assert parse_emphasis(None, "t") is None


@pytest.mark.parametrize(
    "table, match",
    [
        ({"factor": 1, "region": ["a >= 1"]}, "changes nothing"),
        ({"factor": 0, "region": ["a >= 1"]}, "positive number"),
        ({"factor": -2, "region": ["a >= 1"]}, "positive number"),
        ({"factor": True, "region": ["a >= 1"]}, "positive number"),
        ({"factor": "3", "region": ["a >= 1"]}, "positive number"),
        ({"factor": 3, "region": []}, "non-empty"),
        ({"factor": 3, "region": "a >= 1"}, "non-empty"),
        ({"factor": 3}, "lacks"),
        ({"region": ["a >= 1"]}, "lacks"),
        ({"factor": 3, "region": ["a >= 1"], "scope": "all"}, "unknown"),
        ({"factor": 3, "region": ["a >= 1", "a >= 1.0"]}, "repeats"),
        ({"factor": 3, "region": ["a ~ 1"]}, "column op value"),
    ],
)
def test_emphasis_spec_refusals(table, match):
    with pytest.raises(ConfigError, match=match):
        EmphasisSpec.from_table(table, "t")
    with pytest.raises(ConfigError):
        ExperimentConfig.from_dict(_cfg(emphasis=table))


def test_emphasis_is_part_of_the_config_identity():
    plain = ExperimentConfig.from_dict(_cfg())
    emph = ExperimentConfig.from_dict(_cfg(emphasis=REGION))
    assert plain.emphasis is None and emph.emphasis is not None
    assert plain.config_hash != emph.config_hash
    other = ExperimentConfig.from_dict(_cfg(emphasis={**REGION, "factor": 10}))
    assert other.config_hash != emph.config_hash
    # the bundle round trip keeps it
    again = ExperimentConfig.from_dict(emph.to_raw_dict())
    assert again.emphasis == emph.emphasis
    assert again.config_hash == emph.config_hash
    # a sweep carries one emphasis into every run
    sweep = SweepConfig.from_dict(
        {
            "name": "emph_sweep",
            "dataset_version": VERSION,
            "scheme": "walkforward",
            "feature_groups": ["ranks"],
            "seeds": [3],
            "cells": [{"horizon_years": 3, "label": "label_3y_beat_spy"}],
            "model": {"name": "decision_tree"},
            "grid": {"max_depth": [2, 3]},
            "emphasis": REGION,
        }
    )
    runs = sweep.expand()
    assert len(runs) == 2
    assert all(r.config.emphasis == emph.emphasis for r in runs)


# --- the fit ----------------------------------------------------------------


def test_fit_data_emphasizes_training_rows_and_reports_the_share(dataset_dir):
    dataset = Dataset(dataset_dir)
    frame = dataset.frame(
        ["book_to_market_rank", "earnings_yield_rank", "label_3y_beat_spy",
         "sample_weight_3y"]
    )
    spec = EmphasisSpec.from_table(REGION, "t")
    plain = dataset.fit_data(
        frame, "label_3y_beat_spy", ["earnings_yield_rank"], 3
    )
    emph = dataset.fit_data(
        frame, "label_3y_beat_spy", ["earnings_yield_rank"], 3, emphasis=spec
    )
    labeled = frame[frame["label_3y_beat_spy"].notna()]
    inside = (labeled["book_to_market_rank"] >= 0.5).fillna(False).to_numpy()
    assert 0 < inside.mean() < 1
    assert emph.sample_weight[inside] == pytest.approx(3 * plain.sample_weight[inside])
    assert emph.sample_weight[~inside] == pytest.approx(plain.sample_weight[~inside])
    # the honest sample size is the mandatory weight, unchanged
    assert emph.effective_size == pytest.approx(plain.effective_size)
    assert plain.emphasis_share is None
    assert emph.emphasis_share == pytest.approx(
        plain.sample_weight[inside].sum() / plain.sample_weight.sum()
    )
    # a NULL in a region column is outside the region
    frame2 = frame.copy()
    frame2.loc[frame2.index[:50], "book_to_market_rank"] = np.nan
    emph2 = dataset.fit_data(
        frame2, "label_3y_beat_spy", ["earnings_yield_rank"], 3, emphasis=spec
    )
    assert emph2.emphasis_share < emph.emphasis_share


def test_emphasized_run_end_to_end(data_root, tmp_path):
    out = run_experiment(
        ExperimentConfig.from_dict(_cfg(emphasis=REGION)),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    shares = [fr["emphasis_train_share"] for fr in out["fold_results"]]
    assert shares and all(0 < s < 1 for s in shares)
    report = out["report_path"].read_text()
    assert "emphasis: training rows with `book_to_market_rank >= 0.5` carry 3x" in report
    assert "emphasis_train_share" in report


def test_emphasis_region_may_not_read_an_outcome(data_root, tmp_path):
    config = ExperimentConfig.from_dict(
        _cfg(emphasis={"factor": 3, "region": ["label_3y_beat_spy == true"]})
    )
    with pytest.raises(ConfigError, match="never be screened on"):
        run_experiment(
            config,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
    with pytest.raises(ConfigError, match="never be screened on"):
        run_experiment(
            ExperimentConfig.from_dict(
                _cfg(emphasis={"factor": 3, "region": ["sample_weight_3y >= 0.5"]})
            ),
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )


def test_deployment_refit_carries_the_emphasis(data_root, tmp_path):
    from harness.deploy import train_deployment_model

    kwargs = dict(
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        models_dir=tmp_path / "models",
    )
    plain = train_deployment_model(ExperimentConfig.from_dict(_cfg()), **kwargs)
    emph = train_deployment_model(
        ExperimentConfig.from_dict(_cfg(name="emph2", emphasis=REGION)), **kwargs
    )
    # every row stays in the fit: emphasis is a weight, not a filter
    assert emph["n_train_rows"] == plain["n_train_rows"]
    assert emph["effective_train_size"] == pytest.approx(plain["effective_train_size"])
