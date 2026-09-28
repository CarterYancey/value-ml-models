"""Append-only results store: one CSV row per (run, fold) outcome.

Every run appends — completed, failed, or abandoned — so the store is the
trial-count ledger for PBO/deflation accounting. Rows are never rewritten.

A run's per-fold rows are `completed` rows, so they are written only once
every fold has finished (`RunLog`): a run that stops part-way leaves one
`failed` row and no fold rows.
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
            record["logged_utc"] = utc_now()
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

    def model_comparison(
        self,
        dataset_version: str,
        scheme: str,
        horizon_years: int,
        label: str,
        model_names: set[str] | frozenset[str],
    ) -> pd.DataFrame:
        """Fold-averaged metrics of previously completed runs in this cell
        for the given model names — feeds the auto-included baseline
        comparison in every report. Latest run per experiment name."""
        df = self.load()
        if df.empty:
            return pd.DataFrame()
        sel = df[
            (df["status"] == "completed")
            & (df["dataset_version"] == dataset_version)
            & (df["scheme"] == scheme)
            & (df["horizon_years"] == str(horizon_years))
            & (df["label"] == label)
            & (df["model"].isin(model_names))
        ]
        if sel.empty:
            return pd.DataFrame()
        rows = []
        for experiment, grp in sel.groupby("experiment"):
            latest = grp[grp["run_id"] == grp.iloc[-1]["run_id"]]
            metrics = pd.DataFrame(
                [json.loads(m) for m in latest["metrics_json"] if m]
            )
            rows.append(
                {
                    "experiment": experiment,
                    "model": latest.iloc[0]["model"],
                    "folds": len(latest),
                    **metrics.mean(numeric_only=True).to_dict(),
                }
            )
        return pd.DataFrame(rows)


class RunLog:
    """One run's rows, held back until the run's folds have all finished.

    Fold rows carry `status = "completed"`, and every reader takes that
    to mean the run completed. Writing them as each fold finishes leaves
    a stopped run looking like a finished one with fewer folds, so they
    are collected here and written by `commit()` after the last fold.
    `fail()` writes the run's single `failed` row instead and drops the
    collected fold rows."""

    def __init__(self, store: ResultsStore, base_row: dict, n_folds: int = 0):
        self.store = store
        self.base_row = dict(base_row)
        self.n_folds = n_folds
        self._fold_rows: list[dict] = []
        self._committed = False

    def fold_done(self, row: dict) -> None:
        # stamped now, not at commit: per-fold timing stays readable
        self._fold_rows.append(
            {
                **self.base_row,
                "status": "completed",
                "logged_utc": utc_now(),
                **row,
            }
        )

    def commit(self) -> None:
        for row in self._fold_rows:
            self.store.append(row)
        self._fold_rows = []
        self._committed = True

    def fail(self, exc: BaseException) -> None:
        error = f"{type(exc).__name__}: {exc}"
        if not self._committed:
            of = f" of {self.n_folds}" if self.n_folds else ""
            error += f" (stopped after {len(self._fold_rows)}{of} folds)"
            self._fold_rows = []
        self.store.append(
            {**self.base_row, "status": "failed", "error": error}
        )
