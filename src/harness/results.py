"""Append-only results store: one CSV row per (run, fold) outcome.

Every run appends — completed, failed, or abandoned — so the store is the
trial-count ledger for PBO/deflation accounting. Rows are never rewritten.
"""

from __future__ import annotations

import csv
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

FIELDS = [
    "run_id",
    "logged_utc",
    "status",  # completed | failed
    "experiment",
    "config_hash",
    "config_path",
    "dataset_version",
    "git_sha",
    "seed",
    "scheme",
    "fold",
    "horizon_years",
    "label",
    "model",
    "n_train_rows",
    "effective_train_size",
    "n_test_rows",
    "metrics_json",
    "error",
]


def git_sha(repo_root: str | Path | None = None) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


class ResultsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, row: dict) -> None:
        unknown = set(row) - set(FIELDS)
        if unknown:
            raise ValueError(f"unknown result fields: {sorted(unknown)}")
        record = {f: row.get(f, "") for f in FIELDS}
        record.setdefault("logged_utc", "")
        if not record["logged_utc"]:
            record["logged_utc"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )
        if isinstance(record["metrics_json"], dict):
            record["metrics_json"] = json.dumps(record["metrics_json"],
                                                sort_keys=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists()
        with open(self.path, "a", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow(record)

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=FIELDS)
        return pd.read_csv(self.path, dtype=str, keep_default_na=False)

    def configurations_tried(
        self, dataset_version: str, scheme: str, horizon_years: int, label: str
    ) -> int:
        """Distinct config hashes ever run against this evaluation cell —
        the number every report must state."""
        df = self.load()
        if df.empty:
            return 0
        sel = df[
            (df["dataset_version"] == dataset_version)
            & (df["scheme"] == scheme)
            & (df["horizon_years"] == str(horizon_years))
            & (df["label"] == label)
        ]
        return int(sel["config_hash"].nunique())
