"""Decision-tree model: weighted fit required, depth limited, NaN-native,
scores are probabilities; rule extraction and diagram rendering work on a
fitted tree."""

import numpy as np
import pandas as pd
import pytest

from explain.rules import extract_leaf_rules, render_tree_diagram, rules_text
from harness.errors import ConfigError, MissingSampleWeightError
from models.registry import build_model
from models.tree import DecisionTreeModel


def _toy_data(n=400, seed=0, with_nan=False):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame(
        {
            "book_to_market_rank": rng.uniform(0, 1, n),
            "earnings_yield_rank": rng.uniform(0, 1, n),
        }
    )
    y = (X["book_to_market_rank"] + 0.2 * rng.normal(size=n) > 0.6).to_numpy()
    if with_nan:
        X.loc[X.index[: n // 5], "earnings_yield_rank"] = np.nan
    w = rng.uniform(0.2, 1.0, n)
    return X, y, w


def test_registry_builds_tree_and_requires_max_depth():
    model = build_model("decision_tree", {"max_depth": 3}, seed=7)
    assert isinstance(model, DecisionTreeModel)
    with pytest.raises(ConfigError, match="max_depth"):
        build_model("decision_tree", {}, seed=7)
    with pytest.raises(ConfigError):
        build_model("decision_tree", {"max_depth": 3, "bogus": 1}, seed=7)


def test_fit_refuses_missing_weights():
    X, y, _ = _toy_data()
    with pytest.raises(MissingSampleWeightError):
        DecisionTreeModel(max_depth=3).fit(X, y)


def test_depth_limit_and_probability_scores():
    X, y, w = _toy_data()
    model = DecisionTreeModel(max_depth=3, seed=1).fit(X, y, sample_weight=w)
    assert model.estimator_.get_depth() <= 3
    scores = model.predict_scores(X)
    assert scores.min() >= 0.0 and scores.max() <= 1.0
    # the signal is book_to_market_rank; high-b2m rows should outscore low
    hi = scores[X["book_to_market_rank"] > 0.8].mean()
    lo = scores[X["book_to_market_rank"] < 0.4].mean()
    assert hi > lo


def test_nan_features_handled_natively():
    X, y, w = _toy_data(with_nan=True)
    model = DecisionTreeModel(max_depth=3, seed=1).fit(X, y, sample_weight=w)
    scores = model.predict_scores(X)
    assert not np.isnan(scores).any()


def test_balanced_class_weight_accepted():
    X, y, w = _toy_data()
    model = DecisionTreeModel(max_depth=2, class_weight="balanced", seed=1)
    model.fit(X, y, sample_weight=w)
    assert model.predict_scores(X).shape == (len(X),)


def test_single_class_cell_degenerates_gracefully():
    X, y, w = _toy_data()
    model = DecisionTreeModel(max_depth=2, seed=1)
    model.fit(X, np.zeros(len(X), dtype=bool), sample_weight=w)
    assert (model.predict_scores(X) == 0.0).all()


def test_rule_extraction_covers_all_weight_and_reads_sanely():
    X, y, w = _toy_data()
    model = DecisionTreeModel(max_depth=3, seed=1).fit(X, y, sample_weight=w)
    rules = extract_leaf_rules(model.estimator_, list(X.columns))
    assert len(rules) == model.estimator_.get_n_leaves()
    assert abs(sum(r.weight_share for r in rules) - 1.0) < 1e-9
    # sorted best-first
    probs = [r.p_positive for r in rules]
    assert probs == sorted(probs, reverse=True)
    text = rules_text(model.estimator_, list(X.columns))
    assert "book_to_market_rank" in text
    assert "P(positive)" in text
    assert "uncalibrated" in text


def test_nan_routing_is_stated_in_rules():
    X, y, w = _toy_data(with_nan=True)
    model = DecisionTreeModel(max_depth=3, seed=1).fit(X, y, sample_weight=w)
    text = rules_text(model.estimator_, list(X.columns))
    # every split condition states which side missing values follow
    assert "(or missing)" in text


def test_tree_diagram_renders(tmp_path):
    X, y, w = _toy_data()
    model = DecisionTreeModel(max_depth=2, seed=1).fit(X, y, sample_weight=w)
    out = render_tree_diagram(model.estimator_, list(X.columns), tmp_path / "t.png")
    assert out.exists() and out.stat().st_size > 0
