"""Phase-3 models (random forest, LightGBM) and the shared precision
knob: weighted fit mandatory, NaN-native, scores are probabilities,
numeric class_weight trades recall for precision."""

import numpy as np
import pandas as pd
import pytest

from harness.errors import ConfigError, MissingSampleWeightError
from models.common import resolve_class_weight
from models.forest import RandomForestModel
from models.gbm import LightGBMModel
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


# --- resolve_class_weight (the shared precision knob) -----------------


def test_resolve_class_weight_modes():
    assert resolve_class_weight(None) is None
    assert resolve_class_weight(1.0) is None  # explicit no-op grid point
    assert resolve_class_weight(1) is None
    assert resolve_class_weight("balanced") == "balanced"
    assert resolve_class_weight(0.5) == {True: 0.5, False: 1.0}
    assert resolve_class_weight(2) == {True: 2.0, False: 1.0}
    assert (
        resolve_class_weight("balanced_subsample",
                             extra_modes=("balanced_subsample",))
        == "balanced_subsample"
    )


@pytest.mark.parametrize("bad", ["bogus", "balanced_subsample", 0, -1.5, True])
def test_resolve_class_weight_rejects(bad):
    with pytest.raises(ConfigError):
        resolve_class_weight(bad)


def test_numeric_class_weight_is_a_precision_knob():
    """Downweighting positives must shrink predicted positive scores —
    the tree only calls regions positive when they are purer."""
    X, y, w = _toy_data()
    scores = {}
    for cw in (0.25, 4.0):
        m = DecisionTreeModel(max_depth=3, class_weight=cw, seed=1)
        m.fit(X, y, sample_weight=w)
        scores[cw] = m.predict_scores(X).mean()
    assert scores[0.25] < scores[4.0]


# --- extended decision-tree hyperparameters ----------------------------


def test_tree_extended_params_apply():
    X, y, w = _toy_data()
    m = DecisionTreeModel(
        max_depth=6,
        max_leaf_nodes=4,
        min_samples_leaf=10,
        min_impurity_decrease=0.0,
        ccp_alpha=0.001,
        seed=1,
    ).fit(X, y, sample_weight=w)
    assert m.estimator_.get_n_leaves() <= 4


def test_tree_registry_accepts_extended_params():
    m = build_model(
        "decision_tree",
        {
            "max_depth": 4,
            "min_samples_leaf": 5,
            "max_leaf_nodes": 8,
            "ccp_alpha": 0.0,
            "class_weight": 0.5,
        },
        seed=3,
    )
    assert isinstance(m, DecisionTreeModel)
    with pytest.raises(ConfigError):
        build_model("decision_tree", {"max_depth": 4, "n_estimators": 5}, seed=3)


# --- random forest ------------------------------------------------------


def test_forest_fit_predict_signal_and_nan():
    X, y, w = _toy_data(with_nan=True)
    m = RandomForestModel(n_estimators=30, max_depth=5, seed=1)
    m.fit(X, y, sample_weight=w)
    s = m.predict_scores(X)
    assert s.shape == (len(X),)
    assert not np.isnan(s).any()
    assert 0.0 <= s.min() and s.max() <= 1.0
    hi = s[X["book_to_market_rank"] > 0.8].mean()
    lo = s[X["book_to_market_rank"] < 0.4].mean()
    assert hi > lo


def test_forest_requires_weights_and_validates_params():
    X, y, _ = _toy_data()
    with pytest.raises(MissingSampleWeightError):
        RandomForestModel(n_estimators=5).fit(X, y)
    with pytest.raises(ConfigError):
        RandomForestModel(n_estimators=0)
    with pytest.raises(ConfigError):
        RandomForestModel(max_depth=0)
    with pytest.raises(ConfigError):
        RandomForestModel(class_weight="bogus")


def test_forest_registry_and_single_class():
    m = build_model(
        "random_forest",
        {"n_estimators": 10, "class_weight": "balanced_subsample"},
        seed=2,
    )
    assert isinstance(m, RandomForestModel)
    with pytest.raises(ConfigError):
        build_model("random_forest", {"num_leaves": 3}, seed=2)
    X, y, w = _toy_data(n=100)
    m.fit(X, np.zeros(len(X), dtype=bool), sample_weight=w)
    assert (m.predict_scores(X) == 0.0).all()


# --- lightgbm ------------------------------------------------------------


def test_lightgbm_fit_predict_signal_and_nan():
    X, y, w = _toy_data(with_nan=True)
    m = LightGBMModel(n_estimators=50, num_leaves=7, seed=1)
    m.fit(X, y, sample_weight=w)
    s = m.predict_scores(X)
    assert s.shape == (len(X),)
    assert not np.isnan(s).any()
    assert 0.0 <= s.min() and s.max() <= 1.0
    hi = s[X["book_to_market_rank"] > 0.8].mean()
    lo = s[X["book_to_market_rank"] < 0.4].mean()
    assert hi > lo


def test_lightgbm_requires_weights_and_validates_params():
    X, y, _ = _toy_data()
    with pytest.raises(MissingSampleWeightError):
        LightGBMModel(n_estimators=5).fit(X, y)
    with pytest.raises(ConfigError):
        LightGBMModel(n_estimators=0)
    with pytest.raises(ConfigError):
        LightGBMModel(num_leaves=1)


def test_lightgbm_single_class_cell_degenerates_gracefully():
    X, y, w = _toy_data(n=100)
    m = LightGBMModel(n_estimators=5, seed=1)
    m.fit(X, np.ones(len(X), dtype=bool), sample_weight=w)
    assert (m.predict_scores(X) == 1.0).all()
    m.fit(X, np.zeros(len(X), dtype=bool), sample_weight=w)
    assert (m.predict_scores(X) == 0.0).all()


def test_lightgbm_registry_and_numeric_class_weight():
    m = build_model(
        "lightgbm",
        {"n_estimators": 20, "num_leaves": 7, "class_weight": 0.25},
        seed=2,
    )
    assert isinstance(m, LightGBMModel)
    with pytest.raises(ConfigError):
        build_model("lightgbm", {"max_leaf_nodes": 4}, seed=2)
    X, y, w = _toy_data()
    m.fit(X, y, sample_weight=w)
    strict = m.predict_scores(X).mean()
    loose = (
        build_model(
            "lightgbm",
            {"n_estimators": 20, "num_leaves": 7, "class_weight": 4.0},
            seed=2,
        )
        .fit(X, y, sample_weight=w)
        .predict_scores(X)
        .mean()
    )
    assert strict < loose


# --- forest resource knobs (max_samples, n_jobs) ----------------------


def test_forest_max_samples_and_n_jobs():
    X, y, w = _toy_data()
    m = RandomForestModel(
        n_estimators=20, min_samples_leaf=5, max_samples=0.5, n_jobs=2
    )
    m.fit(X, y, sample_weight=w)
    assert len(m.predict_scores(X)) == len(X)
    # 1.0 normalizes to None (sklearn's "full bootstrap")
    assert RandomForestModel(max_samples=1.0).estimator_.max_samples is None


@pytest.mark.parametrize(
    "params",
    [
        {"max_samples": 0.0},
        {"max_samples": 1.5},
        {"max_samples": True},
        {"max_samples": 0.5, "bootstrap": False},
        {"n_jobs": 0},
        {"n_jobs": 1.5},
    ],
)
def test_forest_resource_knob_validation(params):
    with pytest.raises(ConfigError):
        RandomForestModel(**params)


def test_registry_accepts_forest_resource_knobs():
    m = build_model(
        "random_forest",
        {"n_estimators": 10, "max_samples": 0.4, "n_jobs": 2},
        seed=0,
    )
    assert m.estimator_.max_samples == 0.4
    assert m.estimator_.n_jobs == 2


# --- GPU device knob (LightGBM only) ----------------------------------


def test_lightgbm_device_param_flows_and_validates():
    m = LightGBMModel(n_estimators=5, num_leaves=4)  # default cpu
    assert m.estimator_.get_params()["device_type"] == "cpu"
    m = LightGBMModel(n_estimators=5, num_leaves=4, device="cuda")
    assert m.estimator_.get_params()["device_type"] == "cuda"
    with pytest.raises(ConfigError, match="device"):
        LightGBMModel(device="tpu")
    reg = build_model("lightgbm", {"n_estimators": 5, "device": "cuda"}, 0)
    assert reg.estimator_.get_params()["device_type"] == "cuda"


def test_lightgbm_cuda_without_cuda_build_is_actionable():
    """The stock PyPI wheel is CPU-only: asking for cuda must fail with
    the install command, not an opaque LightGBMError."""
    X, y, w = _toy_data()
    m = LightGBMModel(
        n_estimators=5, num_leaves=4, min_child_samples=5, device="cuda"
    )
    with pytest.raises(ConfigError, match="USE_CUDA"):
        m.fit(X, y, sample_weight=w)


def test_lightgbm_regressor_accepts_device():
    from models.gbm import LightGBMRegressorModel

    m = LightGBMRegressorModel(n_estimators=5, device="gpu")
    assert m.estimator_.get_params()["device_type"] == "gpu"
    with pytest.raises(ConfigError, match="unknown params"):
        build_model("random_forest", {"device": "cuda"}, 0)
