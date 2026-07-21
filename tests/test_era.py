"""Era slicing, crash-era breakout, calibration table, Wilson intervals."""

import math

import numpy as np
import pandas as pd
import pytest

from eval.era import (
    CRASH_ERAS,
    crash_era_table,
    era_table,
    wilson_interval,
)
from eval.metrics import calibration_table


def _predictions(years, seed=0):
    rng = np.random.default_rng(seed)
    frames = []
    for i, year in enumerate(years):
        n = 60
        y = rng.uniform(size=n) < 0.3
        score = np.clip(0.3 * y + rng.uniform(size=n) * 0.7, 0, 1)
        frames.append(
            pd.DataFrame(
                {
                    "fold": i,
                    "year": year,
                    "y_true": y.astype(float),
                    "score": score,
                    "sample_weight": rng.uniform(0.2, 1.0, n),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def test_era_table_has_one_row_per_year_plus_pooled():
    pred = _predictions([2016, 2017, 2018])
    table = era_table(pred, top_k=(10,), probabilistic=True)
    assert list(table["era"]) == ["2016", "2017", "2018", "pooled"]
    for col in ("n_test", "effective_n", "base_rate", "pr_auc", "brier",
                "precision_at_10", "recall_at_10"):
        assert col in table.columns
    # effective n is Σ weights, strictly below raw counts
    assert (table["effective_n"] < table["n_test"]).all()


def test_era_table_refuses_malformed_frame():
    with pytest.raises(ValueError, match="lacks columns"):
        era_table(pd.DataFrame({"year": [2016]}))


def test_crash_era_breakout_with_ci():
    pred = _predictions([2007, 2008, 2009, 2020, 2021])
    table = crash_era_table(pred, top_k=(10,))
    assert set(table["era"]) == {"GFC 2008-09", "COVID 2020"}
    gfc = table[table["era"] == "GFC 2008-09"].iloc[0]
    assert gfc["n_test"] == 120  # 2008 + 2009 pooled
    ci = gfc["precision_at_10_ci95"]
    assert ci.startswith("[") and "," in ci


def test_crash_era_empty_when_no_crash_years():
    table = crash_era_table(_predictions([2016, 2017]))
    assert table.empty


def test_crash_eras_match_plan():
    assert CRASH_ERAS["dot-com 2000-02"] == (2000, 2002)
    assert CRASH_ERAS["rate-shock 2022"] == (2022, 2022)


def test_wilson_interval_sanity():
    lo, hi = wilson_interval(7, 10)
    assert 0 < lo < 0.7 < hi < 1
    assert math.isnan(wilson_interval(0, 0)[0])
    lo_small, hi_small = wilson_interval(7, 10)
    lo_big, hi_big = wilson_interval(700, 1000)
    assert hi_big - lo_big < hi_small - lo_small  # more n, tighter interval


def test_ranking_metrics_accept_nonfinite_scores():
    # rank baselines emit -inf for NULL-rank rows ("sort last"); models
    # can emit NaN — neither may crash the sklearn-backed metrics
    from eval import metrics

    y = np.array([1.0, 0.0, 1.0, 0.0, 1.0])
    s = np.array([0.9, 0.5, np.nan, -np.inf, 0.7])
    for fn in (metrics.pr_auc, metrics.roc_auc):
        assert math.isfinite(fn(y, s))
    # non-finite scores rank strictly below every finite score
    order = np.argsort(-metrics._finite_scores(s), kind="stable")
    assert list(order[-2:]) == [2, 3]


def test_calibration_table_weighted_bins():
    rng = np.random.default_rng(3)
    p = rng.uniform(size=500)
    y = (rng.uniform(size=500) < p).astype(float)  # perfectly calibrated
    bins = calibration_table(y, p, sample_weight=np.ones(500), n_bins=5)
    assert 1 <= len(bins) <= 5
    for b in bins:
        assert abs(b["mean_predicted"] - b["observed_rate"]) < 0.25
    assert sum(b["n_rows"] for b in bins) == 500


def test_calibration_table_constant_predictor():
    y = np.array([0.0, 1.0, 0.0, 1.0])
    bins = calibration_table(y, np.full(4, 0.5))
    assert len(bins) == 1
    assert bins[0]["observed_rate"] == pytest.approx(0.5)
