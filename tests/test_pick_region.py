"""`[pick_screen] region`: the share of a selection inside a region of
feature-column filters, reported as the binary pick outcome `in_region`."""
import numpy as np
import pytest

from harness.config import ExperimentConfig, PickScreen
from harness.errors import ConfigError
from harness.runner import run_experiment

VERSION = "dataset_v0.0-test"
SCREEN = {"per": "year", "top_k": 5, "region": ["book_to_market_rank >= 0.5"]}


def _cfg(**extra):
    raw = {
        "name": "region",
        "dataset_version": VERSION,
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "pick_outcomes": ["fwd_3y_cagr"],
        "model": {"name": "random_forest", "n_estimators": 5, "max_depth": 2},
    }
    raw.update(extra)
    return raw


def test_screen_region_parses_strings_and_tables():
    a = PickScreen.from_table(SCREEN, "t")
    b = PickScreen.from_table(
        {"per": "year", "top_k": 5,
         "region": [{"column": "book_to_market_rank", "op": ">=", "value": 0.5}]},
        "t",
    )
    assert a.region == b.region and len(a.region) == 1
    assert a.to_table()["region"] == ["book_to_market_rank >= 0.5"]
    assert "`in_region` = inside `book_to_market_rank >= 0.5`" in a.describe()
    assert "region" not in PickScreen.from_table({"top_k": 5}, "t").to_table()


@pytest.mark.parametrize(
    "region, match",
    [
        ("book_to_market_rank >= 0.5", "non-empty list"),
        ([], "non-empty list"),
        (["book_to_market_rank >= 0.5", "book_to_market_rank >= 0.50"], "repeats"),
        (["book_to_market_rank"], "column op value"),
    ],
)
def test_screen_region_refusals(region, match):
    with pytest.raises(ConfigError, match=match):
        PickScreen.from_table({"top_k": 5, "region": region}, "t")


def test_screen_region_is_part_of_the_config_identity():
    plain = ExperimentConfig.from_dict(_cfg(pick_screen={"per": "year", "top_k": 5}))
    region = ExperimentConfig.from_dict(_cfg(pick_screen=SCREEN))
    assert plain.config_hash != region.config_hash
    spelled = ExperimentConfig.from_dict(
        _cfg(pick_screen={**SCREEN, "region": ["book_to_market_rank >= 0.50"]})
    )
    assert spelled.config_hash == region.config_hash
    again = ExperimentConfig.from_dict(region.to_raw_dict())
    assert again.config_hash == region.config_hash


def test_screen_region_share_is_reported(data_root, tmp_path):
    out = run_experiment(
        ExperimentConfig.from_dict(_cfg(pick_screen=SCREEN)),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    for fr in out["fold_results"]:
        share = fr["metrics"]["screen_mean_in_region"]
        assert 0.0 <= share <= 1.0
        assert 0.0 <= fr["metrics"]["all_mean_in_region"] <= 1.0
    report = out["report_path"].read_text()
    assert "`in_region` is the share of rows inside the screen's region" in report
    assert "in_region" in report


def test_screen_region_matches_a_direct_count(data_root, tmp_path):
    """The region outcome is the filter applied to the test rows: with
    a region every row passes (`book_to_market_rank >= 0`, apart from
    the fixture's NULLs, which count as outside) the share is above the
    NULL-free bound in every fold and pooled, and with a region no row
    passes it is exactly 0."""
    shares = {}
    for name, region in (
        ("all", ["book_to_market_rank >= 0"]),
        ("none", ["book_to_market_rank > 1"]),
    ):
        out = run_experiment(
            ExperimentConfig.from_dict(
                _cfg(name=name, pick_screen={**SCREEN, "region": region})
            ),
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
            models_dir=tmp_path / "models",
        )
        shares[name] = (
            [fr["metrics"]["screen_mean_in_region"] for fr in out["fold_results"]],
            out["pooled_metrics"]["screen_mean_in_region"],
        )
    # the fixture leaves about 5% of book_to_market_rank NULL
    assert all(0.8 <= s <= 1.0 for s in shares["all"][0]) and 0.8 <= shares["all"][1] <= 1.0
    assert all(s == 0.0 for s in shares["none"][0]) and shares["none"][1] == 0.0


def test_screen_region_may_not_read_an_outcome(data_root, tmp_path):
    with pytest.raises(ConfigError, match="never be screened on"):
        run_experiment(
            ExperimentConfig.from_dict(
                _cfg(pick_screen={**SCREEN, "region": ["label_3y_beat_spy == true"]})
            ),
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
