"""year_balance (training weights) and the year-calibration measures."""

import math

import numpy as np
import pytest

from eval.metrics import mean_score, year_calibration
from harness.config import ExperimentConfig
from harness.dataset import year_balanced_weights
from harness.errors import ConfigError


def _share(w, y, m):
    return w[m & y].sum() / w[m].sum()


def test_year_balanced_weights_equalize_the_positive_share():
    rng = np.random.default_rng(0)
    years = np.repeat([2001, 2002, 2003], [100, 200, 300])
    rates = {2001: 0.1, 2002: 0.5, 2003: 0.8}
    y = np.array([rng.random() < rates[g] for g in years])
    w = rng.uniform(0.2, 1.0, len(y))
    out = year_balanced_weights(w, y, years)
    pooled = w[y].sum() / w.sum()
    for g in (2001, 2002, 2003):
        m = years == g
        # each year now says the same about the prior...
        assert _share(out, y, m) == pytest.approx(pooled)
        # ...and keeps its total weight
        assert out[m].sum() == pytest.approx(w[m].sum())
    assert out.sum() == pytest.approx(w.sum())
    # within a year and class, the uniqueness weights keep their ratios
    m = (years == 2002) & y
    assert (out[m] / w[m]) == pytest.approx(np.full(m.sum(), out[m][0] / w[m][0]))


def test_year_balanced_weights_leave_one_class_years_alone():
    years = np.array([1, 1, 2, 2])
    y = np.array([True, True, True, False])
    w = np.ones(4)
    out = year_balanced_weights(w, y, years)
    assert out[:2].tolist() == [1.0, 1.0]


def test_mean_score_and_year_calibration():
    assert mean_score([0.2, 0.6], [1.0, 3.0]) == pytest.approx(0.5)
    assert math.isnan(mean_score([np.nan], [1.0]))
    following = year_calibration([(0.2, 0.25), (0.5, 0.45), (0.8, 0.7)])
    assert following["year_calib_corr"] == pytest.approx(1.0, abs=0.05)
    assert following["year_calib_mae"] == pytest.approx((0.05 + 0.05 + 0.1) / 3)
    lagging = year_calibration([(0.8, 0.2), (0.5, 0.5), (0.2, 0.8)])
    assert lagging["year_calib_corr"] == pytest.approx(-1.0)
    assert math.isnan(year_calibration([(0.5, 0.5)])["year_calib_corr"])


def _cfg(**extra):
    return {
        "name": "yb",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "model": {"name": "random_forest", "n_estimators": 5, "max_depth": 2},
        **extra,
    }


def test_year_balance_is_part_of_the_config_identity():
    plain = ExperimentConfig.from_dict(_cfg())
    balanced = ExperimentConfig.from_dict(_cfg(year_balance=True))
    assert balanced.year_balance and not plain.year_balance
    assert plain.config_hash != balanced.config_hash
    # off is the default and leaves earlier hashes alone
    assert ExperimentConfig.from_dict(_cfg(year_balance=False)).config_hash == plain.config_hash
    # the bundle round trip keeps it
    again = ExperimentConfig.from_dict(balanced.to_raw_dict())
    assert again.year_balance and again.config_hash == balanced.config_hash
    with pytest.raises(ConfigError, match="year_balance"):
        ExperimentConfig.from_dict(_cfg(year_balance="yes"))


def test_year_balanced_run_end_to_end(data_root, tmp_path):
    from harness.runner import run_experiment

    out = run_experiment(
        ExperimentConfig.from_dict(_cfg(year_balance=True, top_k=[5])),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    report = out["report_path"].read_text()
    assert "mean_score" in report
    assert all(
        np.isfinite(fr["metrics"]["mean_score"]) for fr in out["fold_results"]
    )
