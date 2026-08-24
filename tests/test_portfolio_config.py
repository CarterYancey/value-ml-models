"""Backtest config schema: required explicitness (costs, investability),
validation, and identity hashing."""

import pytest

from harness.errors import ConfigError
from portfolio.config import BacktestConfig, FilterSpec


def _raw(**overrides) -> dict:
    raw = {
        "name": "bt",
        "dataset_version": "dataset_v0.0-test",
        "prices_version": "prices_v0.0-test",
        "bundles": ["experiments/models/x_run"],
        "investability": "none",
        "execution": {"cost_bps": 20.0},
    }
    raw.update(overrides)
    return raw


def test_minimal_config_parses():
    config = BacktestConfig.from_dict(_raw())
    assert config.combine == "product"
    assert config.top_k == 25
    assert config.investability_none
    assert config.cost_bps == 20.0


def test_cost_bps_is_required():
    with pytest.raises(ConfigError, match="cost_bps"):
        BacktestConfig.from_dict(_raw(execution={}))


def test_investability_must_be_stated():
    raw = _raw()
    del raw["investability"]
    with pytest.raises(ConfigError, match="investability"):
        BacktestConfig.from_dict(raw)


def test_investability_filters_parse():
    config = BacktestConfig.from_dict(
        _raw(
            investability=[
                {"column": "dollar_volume_3m", "op": ">=", "value": 1e5}
            ]
        )
    )
    assert not config.investability_none
    assert config.investability[0].describe() == "dollar_volume_3m >= 100000.0"


def test_score_weighting_refuses_mean_rank():
    with pytest.raises(ConfigError, match="mean_rank"):
        BacktestConfig.from_dict(
            _raw(
                signal={"combine": "mean_rank"},
                portfolio={"weighting": "score"},
            )
        )


def test_filter_op_validation():
    with pytest.raises(ConfigError, match="op"):
        FilterSpec.from_table(
            {"column": "x", "op": "~", "value": 1}, "<t>", "[[filters]]"
        )
    with pytest.raises(ConfigError, match="numeric"):
        FilterSpec.from_table(
            {"column": "x", "op": ">", "value": "abc"}, "<t>", "[[filters]]"
        )


def test_derived_name_and_hash_track_content():
    raw = _raw()
    del raw["name"]
    a = BacktestConfig.from_dict(raw)
    raw_b = _raw(portfolio={"top_k": 10})
    del raw_b["name"]
    b = BacktestConfig.from_dict(raw_b)
    assert a.name.startswith("portfolio_buy_and_hold_product_top25_")
    assert a.name != b.name
    assert a.config_hash != b.config_hash
    # deterministic: the same content re-parses to the same identity
    raw_again = _raw()
    del raw_again["name"]
    assert BacktestConfig.from_dict(raw_again).config_hash == a.config_hash
