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
    raise ConfigError(f"unknown model name {name!r}")


def _reject_extra(name: str, params: dict, allowed: set[str]) -> None:
    extra = set(params) - allowed
    if extra:
        raise ConfigError(f"model {name!r} got unknown params: {sorted(extra)}")
