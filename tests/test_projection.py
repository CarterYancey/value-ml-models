"""Column-projected split application: fold frames carry only the
columns a run needs (full-width frames copy every string metadata
column and cost tens of GB on real data — the vml-sweep OOM), without
changing what gets trained or validated."""

import numpy as np
import pytest

from harness.dataset import SNAPSHOT_KEY, Dataset
from harness.errors import DatasetValidationError

FEATURES = ["book_to_market_rank", "earnings_yield_rank"]
NEEDED = FEATURES + ["label_3y_beat_spy", "sample_weight_3y"]


def test_dataset_init_does_not_load_the_frame(dataset_dir):
    ds = Dataset(dataset_dir)
    # manifest validation runs against parquet metadata, not a full load
    assert ds._data is None
    assert ds._splits is None


def test_projected_split_carries_only_requested_columns(dataset_dir):
    ds = Dataset(dataset_dir)
    split = ds.apply_split("walkforward", 2016, 3, columns=NEEDED)
    expected = set(SNAPSHOT_KEY) | set(NEEDED) | {"delisted_in_window_3y"}
    assert set(split.train.columns) == expected
    assert set(split.test.columns) == expected
    # ticker and other metadata never entered the frames
    assert "ticker" not in split.train.columns


def test_projected_split_matches_full_width_split(dataset_dir):
    ds = Dataset(dataset_dir)
    full = ds.apply_split("walkforward", 2016, 3)
    narrow = ds.apply_split("walkforward", 2016, 3, columns=NEEDED)
    assert len(full.train) == len(narrow.train)
    assert len(full.test) == len(narrow.test)
    for frame_full, frame_narrow in (
        (full.train, narrow.train),
        (full.test, narrow.test),
    ):
        f = frame_full.sort_values(SNAPSHOT_KEY).reset_index(drop=True)
        n = frame_narrow.sort_values(SNAPSHOT_KEY).reset_index(drop=True)
        for col in NEEDED:
            np.testing.assert_array_equal(
                f[col].to_numpy(), n[col].to_numpy()
            )
    # fit data built from the projected frames is identical
    fit_full = ds.fit_data(full.train, "label_3y_beat_spy", FEATURES, 3)
    fit_narrow = ds.fit_data(narrow.train, "label_3y_beat_spy", FEATURES, 3)
    assert fit_full.effective_size == fit_narrow.effective_size
    assert fit_full.y.sum() == fit_narrow.y.sum()


def test_projection_always_includes_observability_column(dataset_dir):
    """The delisted/label-observability column cannot be projected away —
    test-row validation depends on it."""
    ds = Dataset(dataset_dir)
    split = ds.apply_split("walkforward", 2016, 3, columns=FEATURES)
    assert "delisted_in_window_3y" in split.test.columns


def test_frame_caches_and_rejects_unknown_columns(dataset_dir):
    ds = Dataset(dataset_dir)
    a = ds.frame(FEATURES)
    b = ds.frame(FEATURES)
    assert a is b  # cached per projection
    assert set(SNAPSHOT_KEY) <= set(a.columns)
    with pytest.raises(DatasetValidationError):
        ds.frame(["no_such_column"])


def test_frame_slices_full_load_when_already_paid_for(dataset_dir):
    ds = Dataset(dataset_dir)
    _ = ds.data  # force the full load
    proj = ds.frame(FEATURES)
    assert set(proj.columns) == set(SNAPSHOT_KEY) | set(FEATURES)


def test_split_tags_filtered_read_matches_full_load(dataset_dir):
    ds = Dataset(dataset_dir)
    filtered = ds._split_tags("walkforward", 3)
    full = ds.splits
    expected = full[
        (full["scheme"] == "walkforward") & (full["horizon_years"] == 3)
    ]
    assert len(filtered) == len(expected)
    assert set(filtered["fold"].unique()) == set(expected["fold"].unique())
