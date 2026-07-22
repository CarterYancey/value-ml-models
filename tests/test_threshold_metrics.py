"""Precision/recall over a score threshold: the "buy everything scoring
>= t" rule, its never-met edge case, and the config/era-table wiring."""

import math

import numpy as np
import pandas as pd

from eval.era import era_table
from eval.metrics import (
    compute_all,
    n_at_threshold,
    precision_at_threshold,
    recall_at_threshold,
    threshold_tag,
)
from harness.config import ExperimentConfig

Y = np.array([1.0, 0.0, 1.0, 0.0, 0.0])
S = np.array([0.9, 0.8, 0.6, 0.4, 0.2])


def test_threshold_metrics_basic():
    # threshold 0.5 selects scores {0.9, 0.8, 0.6}: 2 of 3 positive,
    # catching 2 of the 2 positives
    assert precision_at_threshold(Y, S, 0.5) == 2 / 3
    assert recall_at_threshold(Y, S, 0.5) == 1.0
    assert n_at_threshold(S, 0.5) == 3
    # the comparison is inclusive: 0.6 clears a 0.6 threshold
    assert n_at_threshold(S, 0.6) == 3


def test_threshold_never_met():
    # precision is 0/0 — undefined, not zero; recall of the existing
    # positives is genuinely 0; the recorded selection size shows why
    assert math.isnan(precision_at_threshold(Y, S, 0.95))
    assert recall_at_threshold(Y, S, 0.95) == 0.0
    assert n_at_threshold(S, 0.95) == 0


def test_threshold_degenerate_inputs():
    assert math.isnan(precision_at_threshold([], [], 0.5))
    assert math.isnan(recall_at_threshold([], [], 0.5))
    # no positives to recall
    assert math.isnan(recall_at_threshold([0.0, 0.0], [0.9, 0.9], 0.5))
    # non-finite scores are unrankable rows and never clear the bar
    s = np.array([np.nan, -np.inf, np.inf, 0.7])
    assert n_at_threshold(s, 0.5) == 1
    assert precision_at_threshold([0.0, 1.0, 1.0, 1.0], s, 0.5) == 1.0


def test_compute_all_records_threshold_block():
    out = compute_all(Y, S, top_k=(2,), score_thresholds=(0.5, 0.95))
    assert out["precision_at_thr_0.5"] == 2 / 3
    assert out["recall_at_thr_0.5"] == 1.0
    assert out["n_at_thr_0.5"] == 3.0
    assert math.isnan(out["precision_at_thr_0.95"])
    assert out["recall_at_thr_0.95"] == 0.0
    assert out["n_at_thr_0.95"] == 0.0
    # default stays threshold-free
    assert not any("thr" in k for k in compute_all(Y, S, top_k=(2,)))


def test_threshold_tag_is_stable():
    assert threshold_tag(0.5) == "0.5"
    assert threshold_tag(0.50) == "0.5"
    assert threshold_tag(1) == "1"


def test_era_table_carries_threshold_columns():
    rng = np.random.default_rng(0)
    n = 40
    pred = pd.concat(
        [
            pd.DataFrame(
                {
                    "fold": i,
                    "year": year,
                    "y_true": (rng.uniform(size=n) < 0.3).astype(float),
                    "score": rng.uniform(size=n),
                    "sample_weight": rng.uniform(0.2, 1.0, n),
                }
            )
            for i, year in enumerate([2016, 2017])
        ],
        ignore_index=True,
    )
    table = era_table(pred, top_k=(10,), score_thresholds=(0.5, 2.0))
    for col in ("precision_at_thr_0.5", "recall_at_thr_0.5", "n_at_thr_0.5"):
        assert col in table.columns
    # scores are U(0,1): the 2.0 threshold is never met in any era
    assert (table["n_at_thr_2"] == 0).all()
    assert table["precision_at_thr_2"].isna().all()
    assert (table["recall_at_thr_2"] == 0.0).all()


def test_config_parses_thresholds_and_preserves_old_hashes():
    raw = {
        "name": "t",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "model": {"name": "majority_class"},
    }
    plain = ExperimentConfig.from_dict(raw)
    assert plain.score_thresholds == ()
    # a config predating the field keeps its hash — the trial ledger
    # counts distinct hashes, so unchanged configs must not re-count
    assert "score_thresholds" not in plain.canonical_json()

    with_thr = ExperimentConfig.from_dict({**raw, "score_thresholds": [0.5, 0.7]})
    assert with_thr.score_thresholds == (0.5, 0.7)
    assert with_thr.config_hash != plain.config_hash
