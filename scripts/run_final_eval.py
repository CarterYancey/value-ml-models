"""Final evaluation on the sealed `holdout` scheme — once per phase.

This script is the ONLY entry point that is granted FINAL_EVAL split
access (CLAUDE.md hard invariant 2). Everything else in the repo —
runner, baselines, notebooks — is structurally refused the holdout tags.

Point it at the experiment config you selected on walk-forward: the
same config is evaluated on the holdout scheme, in memory — no copied
`*_holdout.toml`. (A config that already says `scheme = "holdout"` runs as
written; the diagnostic schemes are refused.)

`--phase` is the roadmap phase the evaluation concludes (PLAN.md §4:
`phase1`, `phase2`, `phase3`, `phase3.5`, `phase4`), not a name for the
experiment. The seal is one completed evaluation per (phase, cell), so a
new phase name is a new look at the holdout — naming phases after
experiments quietly turns the sealed set into a validation set.

Discipline enforced here, as errors:

- the phase must be a roadmap phase (`phaseN` or `phaseN.M`);
- one completed evaluation per (phase, dataset version, horizon, label):
  a consumed holdout cannot be re-sealed, so a second attempt is refused
  and the number you already have is the number you report;
- the result is logged to `reports/final_evals.csv` and the ordinary
  results store whether good or bad — a disappointing holdout number is
  a result, not a do-over.

Usage:
    python scripts/run_final_eval.py experiments/<config>.toml --phase phase3
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import replace
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


#: a roadmap phase (PLAN.md §4): phase1, phase2, phase3, phase3.5, phase4
PHASE_PATTERN = re.compile(r"^phase\d+(\.\d+)?$")

#: the one scheme a final eval may substitute for holdout
SELECTION_SCHEME = "walkforward"


class HoldoutAlreadyConsumedError(HarnessError):
    """A completed final eval already exists for this (phase, cell)."""


class PhaseNameError(HarnessError):
    """`--phase` is not a roadmap phase."""


def check_phase(phase: str) -> str:
    if not PHASE_PATTERN.match(phase):
        raise PhaseNameError(
            f"--phase {phase!r} is not a roadmap phase. The phase is the "
            "PLAN.md §4 phase this evaluation concludes (phase1, phase2, "
            "phase3, phase3.5, phase4), not the experiment's name: the seal "
            "is one holdout evaluation per (phase, cell), so a fresh phase "
            "name per experiment would re-open the holdout every time"
        )
    return phase


def holdout_variant(config: ExperimentConfig) -> ExperimentConfig:
    """The config as it is evaluated: a walk-forward selection config is
    switched to the holdout scheme in memory (same name, so the report
    and ledger rows carry the experiment's name; the config hash differs
    because the scheme is part of it). Diagnostic schemes are refused."""
    if config.scheme == "holdout":
        return config
    if config.scheme != SELECTION_SCHEME:
        raise HarnessError(
            f"final eval takes a {SELECTION_SCHEME!r} config (or one already "
            f"on 'holdout'); {config.scheme!r} is a diagnostic scheme — "
            "scripts/run_diagnostic.py"
        )
    return replace(config, scheme="holdout")


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
    check_phase(phase)
    config = holdout_variant(ExperimentConfig.from_file(config_path))

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
    parser.add_argument(
        "config",
        help="the selected experiment's config (walkforward; evaluated on "
        "holdout in memory) or a config with scheme='holdout'",
    )
    parser.add_argument(
        "--phase", required=True,
        help="the PLAN.md roadmap phase this eval concludes: phase1, "
        "phase2, phase3, phase3.5, phase4 (one eval per phase per cell)",
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
