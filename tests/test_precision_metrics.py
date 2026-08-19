"""recall_at_precision: best recall subject to a precision floor —
selection-rule semantics (unweighted, ties taken together, non-finite
scores unrankable but positives always counted in the denominator)."""

import math

import numpy as np

from eval.metrics import compute_all, recall_at_precision


def test_perfect_top_of_ranking():
    y = [1, 1, 1, 0, 0, 0, 0, 0]
    s = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
    out = recall_at_precision(y, s, 1.0)
    assert out["recall"] == 1.0
    assert out["threshold"] == 0.7
    assert out["n_selected"] == 3


def test_tightest_threshold_at_max_recall():
    # k=3 gives precision 1.0 recall 1.0; k=5 gives precision 0.6, same
    # recall — the tighter rule must be reported
    y = [1, 1, 1, 0, 0, 0, 0, 0]
    s = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
    out = recall_at_precision(y, s, 0.6)
    assert out["recall"] == 1.0
    assert out["threshold"] == 0.7
    assert out["n_selected"] == 3


def test_partial_recall_under_floor():
    # taking 1 → p=1.0 r=1/3; taking 2 → p=0.5; taking 4 → p=0.5;
    # floor 0.9 is only met by the top pick
    y = [1, 0, 1, 1]
    s = [0.9, 0.8, 0.7, 0.6]
    out = recall_at_precision(y, s, 0.9)
    assert out["recall"] == 1 / 3
    assert out["threshold"] == 0.9
    assert out["n_selected"] == 1


def test_ties_are_taken_together():
    # the two 0.9-scores tie: no rule can select only the first, so the
    # floor 0.9 is unreachable
    y = [1, 0, 1]
    s = [0.9, 0.9, 0.5]
    out = recall_at_precision(y, s, 0.9)
    assert out["recall"] == 0.0
    assert math.isnan(out["threshold"])
    assert out["n_selected"] == 0


def test_unrankable_positive_stays_in_denominator():
    y = [1, 0, 1]
    s = [0.9, 0.2, np.nan]
    out = recall_at_precision(y, s, 0.9)
    assert out["recall"] == 0.5
    assert out["n_selected"] == 1


def test_no_positives_is_nan():
    out = recall_at_precision([0, 0], [0.9, 0.1], 0.5)
    assert math.isnan(out["recall"])
    assert math.isnan(out["threshold"])


def test_all_scores_nonfinite_is_empty_selection():
    out = recall_at_precision([1, 0], [np.nan, np.nan], 0.5)
    assert out["recall"] == 0.0
    assert out["n_selected"] == 0


def test_compute_all_emits_precision_target_keys():
    y = [1, 1, 0, 0, 1, 0]
    s = [0.9, 0.8, 0.7, 0.3, 0.6, 0.1]
    out = compute_all(
        y, s, top_k=(2,), precision_targets=(0.75, 0.9), probabilistic=True
    )
    for tag in ("0.75", "0.9"):
        assert f"recall_at_prec_{tag}" in out
        assert f"thr_for_prec_{tag}" in out
        assert f"n_at_prec_{tag}" in out
    # floor 0.9: only the all-positive top-2 qualifies (r = 2/3);
    # floor 0.75: top-4 has p = 3/4 and catches every positive (r = 1)
    assert out["recall_at_prec_0.9"] == 2 / 3
    assert out["n_at_prec_0.9"] == 2.0
    assert out["recall_at_prec_0.75"] == 1.0
    assert out["n_at_prec_0.75"] == 4.0
