"""Final evaluation on the sealed `holdout` scheme — once per phase.

This script is the ONLY entry point that is granted FINAL_EVAL split
access (CLAUDE.md hard invariant 2). Everything else in the repo —
runner, baselines, notebooks — is structurally refused the holdout tags.

Discipline enforced here, as errors:

- the config must use scheme = "holdout"; nothing else is a final eval;
- one completed evaluation per (phase, dataset version, horizon, label):
  a consumed holdout cannot be re-sealed, so a second attempt is refused
  and the number you already have is the number you report;
- the result is logged to `reports/final_evals.csv` and the ordinary
  results store whether good or bad — a disappointing holdout number is
  a result, not a do-over.

Usage:
    python scripts/run_final_eval.py experiments/<config>.toml --phase phase1
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from harness.config import ExperimentConfig  # noqa: E402
from harness.dataset import SplitAccess  # noqa: E402
from harness.errors import HarnessError  # noqa: E402
from harness.results import git_sha  # noqa: E402
from harness.runner import (  # noqa: E402
    DEFAULT_DATA_ROOT,
    DEFAULT_RESULTS,
    run_experiment,
)

DEFAULT_LEDGER = Path("reports/final_evals.csv")
DEFAULT_FINAL_REPORTS = Path("reports/final_eval")
LEDGER_FIELDS = [
    "phase",
    "dataset_version",
    "horizon_years",
    "label",
    "experiment",
    "config_hash",
    "run_id",
    "git_sha",
    "logged_utc",
    "status",
]


class HoldoutAlreadyConsumedError(HarnessError):
    """A completed final eval already exists for this (phase, cell)."""


def _load_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _append_ledger(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with open(path, "a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow({f: row.get(f, "") for f in LEDGER_FIELDS})


def run_final_eval(
    config_path: str | Path,
    phase: str,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_FINAL_REPORTS,
    ledger_path: str | Path = DEFAULT_LEDGER,
) -> dict:
    config = ExperimentConfig.from_file(config_path)
    if config.scheme != "holdout":
        raise HarnessError(
            f"final eval requires scheme='holdout', config has "
            f"{config.scheme!r}; walk-forward runs go through vml-run"
        )

    ledger_path = Path(ledger_path)
    cell = (phase, config.dataset_version, str(config.horizon_years), config.label)
    for entry in _load_ledger(ledger_path):
        if (
            entry["status"] == "completed"
            and (
                entry["phase"],
                entry["dataset_version"],
                entry["horizon_years"],
                entry["label"],
            )
            == cell
        ):
            raise HoldoutAlreadyConsumedError(
                f"holdout already evaluated for phase={phase!r}, "
                f"cell=({config.dataset_version}, {config.horizon_years}y, "
                f"{config.label}) in run {entry['run_id']}: a consumed "
                "holdout cannot be re-sealed — the number you already have "
                "is the number you report"
            )

    base = {
        "phase": phase,
        "dataset_version": config.dataset_version,
        "horizon_years": str(config.horizon_years),
        "label": config.label,
        "experiment": config.name,
        "config_hash": config.config_hash,
        "git_sha": git_sha(),
        "logged_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        summary = run_experiment(
            config,
            data_root=data_root,
            results_path=results_path,
            reports_dir=reports_dir,
            config_path=str(config_path),
            access=SplitAccess.FINAL_EVAL,
        )
    except Exception:
        # logged (does not consume the holdout: nothing was evaluated)
        _append_ledger(ledger_path, {**base, "status": "failed"})
        raise
    _append_ledger(
        ledger_path, {**base, "run_id": summary["run_id"], "status": "completed"}
    )
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="experiments/*.toml with scheme='holdout'")
    parser.add_argument(
        "--phase", required=True, help="phase this eval concludes, e.g. phase1"
    )
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_FINAL_REPORTS))
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    args = parser.parse_args(argv)
    try:
        summary = run_final_eval(
            args.config,
            args.phase,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
            ledger_path=args.ledger,
        )
    except HarnessError as exc:
        print(f"final eval refused/failed: {exc}")
        return 1
    print(
        f"FINAL EVAL COMPLETE (phase={args.phase}) — run {summary['run_id']}; "
        "this cell's holdout is now consumed for the phase.\n"
        f"report: {summary['report_path']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
