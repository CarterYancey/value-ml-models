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
from models.gbm import LightGBMModel, LightGBMRegressorModel
from models.tree import DecisionTreeModel

#: Baseline model names every reported result is compared against.
BASELINE_MODELS = frozenset({"majority_class", "rank_factor", "random_ranking"})

#: Models trained on a continuous label column (the regression reframe).
#: Configs using one must set `eval_label` (a binary label from the
#: upstream matrix) so evaluation stays in the precision@K frame.
CONTINUOUS_TARGET_MODELS = frozenset({"lightgbm_regressor"})

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
        "max_samples",
        "n_jobs",
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

_LIGHTGBM_REGRESSOR_PARAMS = (
    _LIGHTGBM_PARAMS - {"class_weight"}
) | {"objective", "alpha", "winsorize"}


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
    if name == "lightgbm_regressor":
        _reject_extra(name, params, allowed=_LIGHTGBM_REGRESSOR_PARAMS)
        return LightGBMRegressorModel(seed=seed, **params)
    raise ConfigError(f"unknown model name {name!r}")


def _reject_extra(name: str, params: dict, allowed: set[str]) -> None:
    extra = set(params) - allowed
    if extra:
        raise ConfigError(f"model {name!r} got unknown params: {sorted(extra)}")


def model_target(name: str) -> str:
    """The label kind a model family consumes: "continuous" for the
    regression reframe, "binary" for every classifier and baseline."""
    return "continuous" if name in CONTINUOUS_TARGET_MODELS else "binary"


def check_target_labels(config) -> None:
    """Refuse the label/model mismatches a config can express.

    A continuous-target model must name the binary `eval_label` its
    ranking is measured against; a classifier must not carry one (it
    would silently change nothing). Called by every fitting entry point
    (runner, deploy) before any data is touched.
    """
    if model_target(config.model_name) == "continuous":
        if not config.eval_label:
            raise ConfigError(
                f"model {config.model_name!r} trains on a continuous "
                f"target ({config.label!r}); the config must set "
                "eval_label to the binary cell the ranking is evaluated "
                "against (e.g. label_3y_cagr_ge_10)"
            )
    elif config.eval_label:
        raise ConfigError(
            f"eval_label is only meaningful for continuous-target models "
            f"({sorted(CONTINUOUS_TARGET_MODELS)}); {config.model_name!r} "
            "is evaluated on its own label"
        )
