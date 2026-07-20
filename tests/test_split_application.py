"""Split-application semantics against the hand-built splits.parquet:
roles, absence-means-out-of-fold, median-kind observable test rows."""

import pandas as pd
import pytest

from harness.dataset import SNAPSHOT_KEY, Dataset
from harness.errors import SplitApplicationError


@pytest.fixture(scope="module")
def ds(dataset_dir):
    return Dataset(dataset_dir)


def _keys(frame: pd.DataFrame) -> set[tuple]:
    return set(map(tuple, frame[SNAPSHOT_KEY].itertuples(index=False)))


def test_train_is_role_train_only(ds):
    split = ds.apply_split("walkforward", 2016, 3)
    tags = ds.splits
    sel = tags[
        (tags["scheme"] == "walkforward")
        & (tags["fold"] == 2016)
        & (tags["horizon_years"] == 3)
    ]
    expected_train = _keys(sel[sel["role"] == "train"])
    assert _keys(split.train) == expected_train
    # purged/embargoed rows exist in the tags but never reach the train frame
    leaky = _keys(sel[sel["role"].isin(["purged", "embargoed"])])
    assert leaky, "fixture should tag purged/embargoed rows"
    assert not (_keys(split.train) & leaky)


def test_train_includes_all_snapshot_kinds(ds):
    split = ds.apply_split("walkforward", 2016, 3)
    assert set(split.train["snapshot_kind"]) == {"low", "median", "high"}


def test_test_rows_are_median_kind_and_observable(ds):
    split = ds.apply_split("walkforward", 2016, 3)
    assert (split.test["snapshot_kind"] == "median").all()
    assert split.test["delisted_in_window_3y"].notna().all()
    # delisted rows are labeled rows like any other — they may appear
    assert set(split.test["delisted_in_window_3y"]) <= {"false", "delisted"}


def test_absence_means_out_of_fold(ds):
    split = ds.apply_split("walkforward", 2016, 3)
    tags = ds.splits
    sel = tags[
        (tags["scheme"] == "walkforward")
        & (tags["fold"] == 2016)
        & (tags["horizon_years"] == 3)
    ]
    tagged = _keys(sel)
    used = _keys(split.train) | _keys(split.test)
    assert used <= tagged
    # untagged rows (e.g. post-test-window snapshots) appear nowhere
    all_rows = _keys(ds.data)
    assert all_rows - tagged, "fixture should have out-of-fold rows"
    assert not (used & (all_rows - tagged))


def test_unknown_fold_refused(ds):
    with pytest.raises(SplitApplicationError, match="no split tags"):
        ds.apply_split("walkforward", 1999, 3)


def test_folds_listed_from_frozen_manifest(ds):
    assert ds.folds("walkforward", 3) == [2016, 2017]


def test_fold_counts_match_frozen_manifest(ds):
    """The applied split must reproduce split_folds.parquet's counts —
    the report's citation depends on folds not drifting."""
    split = ds.apply_split("walkforward", 2017, 3)
    sf = ds.split_folds
    row = sf[
        (sf["scheme"] == "walkforward")
        & (sf["fold"] == 2017)
        & (sf["horizon_years"] == 3)
    ].iloc[0]
    assert len(split.train) == row["n_train"]
    assert len(split.test) == row["n_test"]


def test_malformed_test_kind_refused(tmp_path):
    from conftest import build_mini_dataset

    root = build_mini_dataset(tmp_path, "dataset_badkind")
    splits = pd.read_parquet(root / "splits.parquet")
    mask = (
        (splits["scheme"] == "walkforward")
        & (splits["fold"] == 2016)
        & (splits["horizon_years"] == 3)
        & (splits["role"] == "train")
        & (splits["snapshot_kind"] == "low")
    )
    splits.loc[mask, "role"] = "test"  # corrupt: low-kind test rows
    splits.to_parquet(root / "splits.parquet")
    ds = Dataset(root)
    with pytest.raises(SplitApplicationError, match="median"):
        ds.apply_split("walkforward", 2016, 3)
