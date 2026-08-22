"""Model registry: config `model.name` → constructor.

The harness builds models only through this registry, so a config file is
the single point where an experiment's model is chosen.
"""

from __future__ import annotations

from harness.errors import ConfigError
from models.baselines import (
    MajorityClassBaseline,
    RandomRankingBaseline,
    RankFactorBaseline,
)
from models.forest import RandomForestModel
from models.gbm import LightGBMModel
from models.tree import DecisionTreeModel

#: Baseline model names every reported result is compared against.
BASELINE_MODELS = frozenset({"majority_class", "rank_factor", "random_ranking"})

_TREE_PARAMS = frozenset(
    {
        "max_depth",
        "min_weight_fraction_leaf",
        "class_weight",
        "criterion",
        "splitter",
        "min_samples_split",
        "min_samples_leaf",
        "max_features",
        "max_leaf_nodes",
        "min_impurity_decrease",
        "ccp_alpha",
    }
)

_FOREST_PARAMS = frozenset(
    {
        "n_estimators",
        "max_depth",
        "min_weight_fraction_leaf",
        "min_samples_leaf",
        "min_samples_split",
        "max_features",
        "max_leaf_nodes",
        "min_impurity_decrease",
        "ccp_alpha",
        "class_weight",
        "criterion",
        "bootstrap",
    }
)

_LIGHTGBM_PARAMS = frozenset(
    {
        "n_estimators",
        "learning_rate",
        "num_leaves",
        "max_depth",
        "min_child_samples",
        "min_child_weight",
        "subsample",
        "subsample_freq",
        "colsample_bytree",
        "reg_alpha",
        "reg_lambda",
        "class_weight",
    }
)


def build_model(name: str, params: dict, seed: int):
    if name == "majority_class":
        _reject_extra(name, params, allowed=set())
        return MajorityClassBaseline()
    if name == "rank_factor":
        _reject_extra(name, params, allowed={"rank_column", "higher_is_better"})
        return RankFactorBaseline(
            rank_column=params.get("rank_column", ""),
            higher_is_better=params.get("higher_is_better", True),
        )
    if name == "random_ranking":
        _reject_extra(name, params, allowed=set())
        return RandomRankingBaseline(seed=seed)
    if name == "decision_tree":
        _reject_extra(name, params, allowed=_TREE_PARAMS)
        if "max_depth" not in params:
            raise ConfigError(
                "decision_tree requires max_depth in the config; "
                "depth-limiting is not optional"
            )
        return DecisionTreeModel(seed=seed, **params)
    if name == "random_forest":
        _reject_extra(name, params, allowed=_FOREST_PARAMS)
        return RandomForestModel(seed=seed, **params)
    if name == "lightgbm":
        _reject_extra(name, params, allowed=_LIGHTGBM_PARAMS)
        return LightGBMModel(seed=seed, **params)
    raise ConfigError(f"unknown model name {name!r}")


def _reject_extra(name: str, params: dict, allowed: set[str]) -> None:
    extra = set(params) - allowed
    if extra:
        raise ConfigError(f"model {name!r} got unknown params: {sorted(extra)}")
