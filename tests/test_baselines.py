"""Baseline model behavior."""

import numpy as np
import pandas as pd
import pytest

from eval.metrics import base_rate, compute_all, precision_at_k
from models.baselines import (
    MajorityClassBaseline,
    RandomRankingBaseline,
    RankFactorBaseline,
)
from models.registry import build_model
from harness.errors import ConfigError


def _toy():
    X = pd.DataFrame(
        {
            "book_to_market_rank": [0.9, 0.7, np.nan, 0.2, 0.1],
            "earnings_yield_rank": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )
    y = np.array([1, 1, 0, 0, 0])
    w = np.array([1.0, 0.5, 1.0, 1.0, 0.5])
    return X, y, w


def test_majority_class_weighted_prevalence():
    X, y, w = _toy()
    model = MajorityClassBaseline().fit(X, y, sample_weight=w)
    assert model.prevalence_ == pytest.approx(1.5 / 4.0)
    scores = model.predict_scores(X)
    assert (scores == model.prevalence_).all()
    assert model.probabilistic


def test_rank_factor_orders_by_column_nan_last():
    X, y, w = _toy()
    model = RankFactorBaseline("book_to_market_rank").fit(X, y, sample_weight=w)
    scores = model.predict_scores(X)
    order = np.argsort(-scores, kind="stable")
    assert list(order) == [0, 1, 3, 4, 2]  # NaN rank sorts last
    assert precision_at_k(y, scores, 2) == 1.0


def test_rank_factor_requires_column_present():
    X, y, w = _toy()
    with pytest.raises(ConfigError, match="not among"):
        RankFactorBaseline("missing_rank").fit(X, y, sample_weight=w)


def test_random_ranking_is_seeded():
    X, y, w = _toy()
    a = RandomRankingBaseline(seed=7).fit(X, y, sample_weight=w).predict_scores(X)
    b = RandomRankingBaseline(seed=7).fit(X, y, sample_weight=w).predict_scores(X)
    c = RandomRankingBaseline(seed=8).fit(X, y, sample_weight=w).predict_scores(X)
    assert (a == b).all()
    assert not (a == c).all()


def test_registry_builds_all_baselines():
    assert isinstance(build_model("majority_class", {}, 0), MajorityClassBaseline)
    m = build_model("rank_factor", {"rank_column": "x"}, 0)
    assert isinstance(m, RankFactorBaseline) and m.rank_column == "x"
    r = build_model("random_ranking", {}, seed=9)
    assert isinstance(r, RandomRankingBaseline) and r.seed == 9
    with pytest.raises(ConfigError):
        build_model("gradient_boosting_from_the_future", {}, 0)
    with pytest.raises(ConfigError, match="unknown params"):
        build_model("majority_class", {"depth": 3}, 0)


def test_metrics_block():
    X, y, w = _toy()
    scores = np.array([0.9, 0.8, 0.1, 0.2, 0.3])
    m = compute_all(y, scores, sample_weight=w, top_k=(2,), probabilistic=True)
    assert m["precision_at_2"] == 1.0
    assert m["base_rate"] == pytest.approx(base_rate(y, w))
    assert 0 <= m["brier"] <= 1
    assert m["n_test"] == 5
