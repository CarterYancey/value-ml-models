"""Loader and validation tests against the miniature dataset."""

import json

import pytest

from conftest import build_mini_dataset
from harness.dataset import Dataset
from harness.errors import DatasetValidationError


def test_loads_and_exposes_column_groups(dataset_dir):
    ds = Dataset(dataset_dir)
    assert ds.version == "dataset_v0.0-test"
    assert ds.columns("features") == ["book_to_market", "earnings_yield"]
    assert ds.columns("ranks") == ["book_to_market_rank", "earnings_yield_rank"]
    assert ds.columns("sector_ranks") == []
    assert "label_3y_beat_spy" in ds.columns("labels")
    assert ds.columns("sample_weights") == ["sample_weight_1y", "sample_weight_3y"]


def test_feature_selection_is_manifest_driven(dataset_dir):
    ds = Dataset(dataset_dir)
    cols = ds.feature_columns(["features", "ranks"])
    assert cols == [
        "book_to_market",
        "earnings_yield",
        "book_to_market_rank",
        "earnings_yield_rank",
    ]
    # explicit subset must be contained in the selected groups
    assert ds.feature_columns(["ranks"], ["book_to_market_rank"]) == [
        "book_to_market_rank"
    ]
    with pytest.raises(DatasetValidationError, match="not in selected manifest"):
        ds.feature_columns(["ranks"], ["book_to_market"])
    # labels can never be selected as features
    with pytest.raises(DatasetValidationError, match="feature groups"):
        ds.feature_columns(["labels"])


def test_missing_file_refused(tmp_path):
    root = build_mini_dataset(tmp_path, "dataset_broken")
    (root / "split_folds.parquet").unlink()
    with pytest.raises(DatasetValidationError, match="missing required files"):
        Dataset(root)


def test_row_count_mismatch_refused(tmp_path):
    root = build_mini_dataset(tmp_path, "dataset_rows")
    manifest = json.loads((root / "manifest.json").read_text())
    manifest["rows"] += 1
    (root / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(DatasetValidationError, match="rows"):
        Dataset(root)


def test_unknown_horizon_refused(dataset_dir):
    ds = Dataset(dataset_dir)
    with pytest.raises(DatasetValidationError, match="horizon 5"):
        ds.apply_split("walkforward", 2016, 5)
    with pytest.raises(DatasetValidationError, match="horizon 5"):
        ds.sample_weight_column(5)


def test_manifest_effective_rows_cross_check(dataset_dir):
    ds = Dataset(dataset_dir)
    total = ds.manifest_effective_rows(3)
    assert total is not None
    weights = ds.data["sample_weight_3y"]
    assert weights.sum() == pytest.approx(total)
