"""Hand-built miniature dataset directory for harness tests.

Mirrors the upstream contract (data/dataset.md, data/splits.md) at toy
scale: quarterly snapshots for a handful of permatickers, three snapshot
kinds, horizons {1, 3}, walkforward/holdout/entity_holdout/random_kfold
tags with the documented role semantics, and a manifest with the full
column layout. Built by tests, never by the harness — splits are applied
here, not constructed (the split logic below is *test scaffolding*
replicating the upstream definitions so the harness can be checked
against them).
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PERMATICKERS = [100001, 100002, 100003, 100004, 100005, 100010]
KINDS = ["low", "median", "high"]
FIRST_YEAR, LAST_YEAR = 2010, 2020
LAST_DATA_DATE = date(2021, 6, 30)
EMBARGO_DAYS = 30
HORIZONS = [1, 3]
WALKFORWARD_FOLDS = {3: [2016, 2017]}
HOLDOUT_FOLD = {3: 2018}


def _add_years(d: date, years: int) -> date:
    return d.replace(year=d.year + years)


def _build_dataset_frame() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    for permaticker in PERMATICKERS:
        for year in range(FIRST_YEAR, LAST_YEAR + 1):
            for q, month in enumerate([1, 4, 7, 10]):
                quarter = date(year, month, 1)
                for k, kind in enumerate(KINDS):
                    snapshot_date = quarter + timedelta(days=10 + 25 * k)
                    b2m = float(rng.uniform(0.1, 3.0))
                    ey = float(rng.uniform(-0.1, 0.3))
                    row = {
                        "permaticker": permaticker,
                        "ticker": f"T{permaticker % 1000}",
                        "quarter": pd.Timestamp(quarter),
                        "quarter_trading_days": 63,
                        "snapshot_kind": kind,
                        "snapshot_date": pd.Timestamp(snapshot_date),
                        "entry_closeadj": float(rng.uniform(1, 100)),
                        "book_to_market": b2m,
                        "earnings_yield": ey,
                        # ranks are NULL under the upstream rank guard;
                        # a realistic fixture must include unrankable rows
                        "book_to_market_rank": (
                            None if rng.uniform() < 0.05 else float(rng.uniform(0, 1))
                        ),
                        "earnings_yield_rank": (
                            None if rng.uniform() < 0.05 else float(rng.uniform(0, 1))
                        ),
                    }
                    for h in HORIZONS:
                        observable = _add_years(snapshot_date, h) <= LAST_DATA_DATE
                        if observable:
                            cagr = float(rng.normal(0.05, 0.2))
                            # sprinkle a few delistings; they stay labeled
                            delisted = (
                                "delisted"
                                if rng.uniform() < 0.03
                                else "false"
                            )
                            row[f"fwd_{h}y_cagr"] = cagr
                            row[f"label_{h}y_beat_spy"] = bool(
                                cagr + 0.3 * b2m / 3.0 > 0.08
                            )
                            row[f"label_{h}y_cagr_ge_8"] = bool(cagr >= 0.08)
                            row[f"delisted_in_window_{h}y"] = delisted
                            row[f"sample_weight_{h}y"] = float(
                                rng.uniform(0.2, 1.0)
                            )
                        else:
                            row[f"fwd_{h}y_cagr"] = None
                            row[f"label_{h}y_beat_spy"] = None
                            row[f"label_{h}y_cagr_ge_8"] = None
                            row[f"delisted_in_window_{h}y"] = None
                            row[f"sample_weight_{h}y"] = None
                    rows.append(row)
    return pd.DataFrame(rows)


def _tag_temporal(
    data: pd.DataFrame, scheme: str, fold: int, horizon: int, test_end_year
) -> list[dict]:
    test_start = date(fold, 1, 1)
    test_end = date(test_end_year, 1, 1) if test_end_year else date(9999, 12, 31)
    tags = []
    observable = data[f"delisted_in_window_{horizon}y"].notna()
    for _, r in data.iterrows():
        snap = r["snapshot_date"].date()
        horizon_end = _add_years(snap, horizon)
        embargo_end = horizon_end + timedelta(days=EMBARGO_DAYS)
        role = None
        if embargo_end < test_start:
            role = "train"
        elif horizon_end < test_start <= embargo_end:
            role = "embargoed"
        elif snap < test_start <= horizon_end:
            role = "purged"
        elif (
            test_start <= snap < test_end
            and r["snapshot_kind"] == "median"
            and observable.loc[r.name]
        ):
            role = "test"
        if role:
            tags.append(
                {
                    "scheme": scheme,
                    "fold": fold,
                    "horizon_years": horizon,
                    "permaticker": r["permaticker"],
                    "snapshot_date": r["snapshot_date"],
                    "snapshot_kind": r["snapshot_kind"],
                    "role": role,
                }
            )
    return tags


def _tag_diagnostics(data: pd.DataFrame, horizon: int) -> list[dict]:
    holdout_start = pd.Timestamp(date(HOLDOUT_FOLD[horizon], 1, 1))
    pre = data[data["snapshot_date"] < holdout_start]
    observable = pre[f"delisted_in_window_{horizon}y"].notna()
    tags = []
    for _, r in pre.iterrows():
        entity_test = r["permaticker"] % 5 == 0
        row_test = r.name % 5 == 0
        for scheme, is_test in (
            ("entity_holdout", entity_test),
            ("random_kfold", row_test),
        ):
            if is_test:
                if r["snapshot_kind"] == "median" and observable.loc[r.name]:
                    role = "test"
                else:
                    continue  # absence means out of fold
            else:
                role = "train"
            tags.append(
                {
                    "scheme": scheme,
                    "fold": 0,
                    "horizon_years": horizon,
                    "permaticker": r["permaticker"],
                    "snapshot_date": r["snapshot_date"],
                    "snapshot_kind": r["snapshot_kind"],
                    "role": role,
                }
            )
    return tags


def _build_split_folds(splits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scheme, fold, horizon), grp in splits.groupby(
        ["scheme", "fold", "horizon_years"]
    ):
        counts = grp["role"].value_counts()
        temporal = scheme in ("walkforward", "holdout")
        if temporal:
            test_start = pd.Timestamp(date(fold, 1, 1))
            test_end = (
                pd.Timestamp(date(9999, 12, 31))
                if scheme == "holdout"
                else pd.Timestamp(date(fold + 1, 1, 1))
            )
        else:
            test_start = test_end = pd.NaT
        rows.append(
            {
                "scheme": scheme,
                "fold": fold,
                "horizon_years": horizon,
                "test_start": test_start,
                "test_end": test_end,
                "embargo_days": EMBARGO_DAYS if temporal else None,
                "n_train": int(counts.get("train", 0)),
                "n_test": int(counts.get("test", 0)),
                "n_purged": int(counts.get("purged", 0)),
                "n_embargoed": int(counts.get("embargoed", 0)),
            }
        )
    return pd.DataFrame(rows)


def build_mini_dataset(root: Path, version: str = "dataset_v0.0-test") -> Path:
    """Write a complete miniature dataset directory under root/version."""
    out = root / version
    out.mkdir(parents=True, exist_ok=True)
    data = _build_dataset_frame()

    tags: list[dict] = []
    for horizon, folds in WALKFORWARD_FOLDS.items():
        for fold in folds:
            tags += _tag_temporal(data, "walkforward", fold, horizon, fold + 1)
        tags += _tag_temporal(
            data, "holdout", HOLDOUT_FOLD[horizon], horizon, None
        )
        tags += _tag_diagnostics(data, horizon)
    splits = pd.DataFrame(tags)
    split_folds = _build_split_folds(splits)

    label_cols = []
    weight_cols = []
    for h in HORIZONS:
        label_cols += [
            f"fwd_{h}y_cagr",
            f"label_{h}y_beat_spy",
            f"label_{h}y_cagr_ge_8",
            f"delisted_in_window_{h}y",
        ]
        weight_cols.append(f"sample_weight_{h}y")
    manifest = {
        "dataset_version": version,
        "created_utc": "2026-01-01T00:00:00Z",
        "horizons_years": HORIZONS,
        "params": {"rank_guard": 20, "min_industry_peers": 5},
        "rows": len(data),
        "permatickers": len(PERMATICKERS),
        "effective_rows": {
            f"{h}y": float(data[f"sample_weight_{h}y"].sum()) for h in HORIZONS
        },
        "columns": {
            "key_meta": [
                "permaticker",
                "ticker",
                "quarter",
                "quarter_trading_days",
                "snapshot_kind",
                "snapshot_date",
                "entry_closeadj",
            ],
            "features": ["book_to_market", "earnings_yield"],
            "ranks": ["book_to_market_rank", "earnings_yield_rank"],
            "sector_ranks": [],
            "labels": label_cols,
            "sample_weights": weight_cols,
        },
    }

    data.to_parquet(out / "dataset.parquet")
    splits.to_parquet(out / "splits.parquet")
    split_folds.to_parquet(out / "split_folds.parquet")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return out


@pytest.fixture(scope="session")
def data_root(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("datasets")
    build_mini_dataset(root)
    return root


@pytest.fixture(scope="session")
def dataset_dir(data_root) -> Path:
    return data_root / "dataset_v0.0-test"
