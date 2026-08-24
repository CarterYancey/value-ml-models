"""The pooled-row fix and the confidence-oriented metrics.

Per-fold models emit incomparable scores, so pooled ranking metrics must
pick per year — a global top-K over pooled scores just returns the
hottest-scoring fold's picks (the bug these tests pin down)."""

import math

import numpy as np
import pandas as pd
import pytest

from eval import metrics
from eval.era import (
    confidence_profile,
    crash_label,
    era_table,
    pooled_metrics,
)
from harness.config import ExperimentConfig, parse_dataset_version
from harness.errors import ConfigError


def _frame(rows):
    return pd.DataFrame(rows, columns=["fold", "year", "y_true", "score",
                                       "sample_weight"])


def _two_year_predictions():
    """Year 1: hot scores (0.9s), all negatives beyond the top pick.
    Year 2: cool scores (0.4s), all positives. A pooled top-K over raw
    scores would pick only year-1 rows."""
    rows = []
    for i in range(10):
        rows.append((2001, 2001, 1.0 if i < 1 else 0.0, 0.9 - i * 0.001, 1.0))
    for i in range(10):
        rows.append((2002, 2002, 1.0, 0.4 - i * 0.001, 1.0))
    return _frame(rows)


def test_pooled_topk_picks_per_year_not_hottest_fold():
    preds = _two_year_predictions()
    pooled = pooled_metrics(preds, top_k=(2,))
    # per-year picks: year 1 contributes 1 hit of 2, year 2 contributes 2
    # of 2 -> 3/4. The broken global pooling gave 1/2 (both picks from the
    # hot year 1).
    assert pooled["precision_at_2"] == pytest.approx(3 / 4)
    broken = metrics.precision_at_k(preds["y_true"], preds["score"], 2)
    assert broken == pytest.approx(1 / 2)


def test_era_table_pooled_row_matches_pooled_metrics():
    preds = _two_year_predictions()
    table = era_table(preds, top_k=(2,))
    pooled_row = table[table["era"] == "pooled"].iloc[0]
    assert pooled_row["precision_at_2"] == pytest.approx(3 / 4)


def test_pooled_precision_target_aggregates_per_year():
    preds = _two_year_predictions()
    pooled = pooled_metrics(preds, precision_targets=(1.0,))
    # year 1: only the top pick is pure (1 hit); year 2: everything is a
    # hit (10). recall = 11/11 positives, n = 1 + 10.
    assert pooled["recall_at_prec_1"] == pytest.approx(1.0)
    assert pooled["n_at_prec_1"] == 11


def test_base_rate_brier_is_no_skill_reference():
    y = np.array([1, 1, 0, 0])
    assert metrics.base_rate_brier(y) == pytest.approx(0.25)
    # weighted: p̄ = 0.75 -> p̄(1-p̄)
    w = np.array([3.0, 3.0, 1.0, 1.0])
    assert metrics.base_rate_brier(y, w) == pytest.approx(0.75 * 0.25)
    assert math.isnan(metrics.base_rate_brier(np.array([])))


def test_confidence_at_k_is_mean_top_score():
    s = np.array([0.9, 0.2, 0.7, np.nan])
    assert metrics.confidence_at_k(s, 2) == pytest.approx(0.8)
    assert math.isnan(metrics.confidence_at_k(np.array([]), 5))


def test_confidence_profile_tiers_and_levels():
    preds = _two_year_predictions()
    prof = confidence_profile(preds, probabilistic=True)
    tiers = prof[prof["selection"] == "top 5/yr"].iloc[0]
    assert tiers["n_picks"] == 10  # 5 per year, 2 years
    assert tiers["picks_per_year"] == 5.0
    lvl = prof[prof["selection"] == "score >= 0.5"].iloc[0]
    # only the ten year-1 scores clear 0.5; one of them is a positive
    assert lvl["n_picks"] == 10
    assert lvl["precision"] == pytest.approx(0.1)
    # non-probabilistic: no score-level rows
    prof2 = confidence_profile(preds, probabilistic=False)
    assert not prof2["selection"].str.startswith("score").any()


def test_crash_label_tags_only_crash_years():
    assert crash_label(2008) == "GFC"
    assert crash_label(2020) == "COVID"
    assert crash_label(2015) is None


def test_min_dataset_version_enforced():
    raw = {
        "dataset_version": "dataset_v1.0",
        "scheme": "walkforward",
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "model": {"name": "decision_tree", "max_depth": 2},
        "min_dataset_version": "1.1",
    }
    with pytest.raises(ConfigError, match="min_dataset_version"):
        ExperimentConfig.from_dict(raw)
    raw["dataset_version"] = "dataset_v1.1"
    config = ExperimentConfig.from_dict(raw)
    config.check_dataset_version("1.1")  # ok
    with pytest.raises(ConfigError, match="min_dataset_version"):
        config.check_dataset_version("1.0")
    # the requirement is part of the config identity
    bare = ExperimentConfig.from_dict(
        {k: v for k, v in raw.items() if k != "min_dataset_version"}
    )
    assert bare.config_hash != config.config_hash


def test_parse_dataset_version_forms():
    assert parse_dataset_version("1.2") == (1, 2)
    assert parse_dataset_version("v1.10") == (1, 10)
    assert parse_dataset_version("dataset_v2.0") == (2, 0)
    assert parse_dataset_version("v1.10") > parse_dataset_version("v1.2")
    with pytest.raises(ConfigError):
        parse_dataset_version("weird")
