"""Point-in-time cross-section rules against the miniature dataset.

Fixture geometry (tests/conftest.py): quarters start Jan/Apr/Jul/Oct 1;
the median-kind snapshot falls 35 days into each quarter."""

import pandas as pd

from harness.dataset import Dataset
from portfolio.crosssection import CrossSectionBuilder


def _builder(data_root, max_staleness_days=200):
    dataset = Dataset(data_root / "dataset_v0.0-test")
    return CrossSectionBuilder(dataset, max_staleness_days)


def test_latest_completed_quarter_median_snapshot(data_root):
    xs = _builder(data_root).at(pd.Timestamp("2016-02-01"))
    # latest completed quarter at 2016-02-01 is 2015Q4 (ends 2015-12-31);
    # its median snapshot is 2015-11-05, for every stock
    assert len(xs) == 6
    assert xs["permaticker"].is_unique
    assert set(pd.to_datetime(xs["snapshot_date"])) == {
        pd.Timestamp("2015-11-05")
    }


def test_incomplete_quarter_is_invisible(data_root):
    # 2016Q1 ends 2016-03-31: on 2016-03-31 the quarter is not yet
    # complete (its median touch date is not knowable), on 2016-04-01 it is
    builder = _builder(data_root)
    on_end = builder.at(pd.Timestamp("2016-03-31"))
    after = builder.at(pd.Timestamp("2016-04-01"))
    assert set(pd.to_datetime(on_end["snapshot_date"])) == {
        pd.Timestamp("2015-11-05")
    }
    assert set(pd.to_datetime(after["snapshot_date"])) == {
        pd.Timestamp("2016-02-05")
    }


def test_staleness_cap_empties_the_cross_section(data_root):
    # at 2016-02-01 the freshest usable snapshot is 88 days old
    xs = _builder(data_root, max_staleness_days=50).at(
        pd.Timestamp("2016-02-01")
    )
    assert xs.empty


def test_no_labels_no_weights_no_offkind_rows(data_root):
    dataset = Dataset(data_root / "dataset_v0.0-test")
    xs = _builder(data_root).at(pd.Timestamp("2016-02-01"))
    outcome_cols = set(dataset.columns("labels")) | set(
        dataset.columns("sample_weights")
    )
    assert not outcome_cols & set(xs.columns)
    assert set(xs["snapshot_kind"]) == {"median"}
