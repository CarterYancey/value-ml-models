"""Registered-diagnostic entry point (data/manual.md §7, PLAN §7).

The one place in the repo that grants `SplitAccess.REGISTERED_DIAGNOSTIC`
— the diagnostic schemes (`entity_holdout`, `random_kfold`) are refused
everywhere else. Everything run here is DIAGNOSTIC ONLY: never model
selection, never reported performance. Every run is still logged to the
results store (under its diagnostic scheme and pseudo-label, apart from
the walk-forward trial accounting), and reports land in
`reports/diagnostics/`.

Subcommands:

    era-probe <config.toml>   predict the calendar year from features alone
                              (experiments/diagnostics/era_probe_*.toml)

The leakage-gap experiment (manual.md §7) registers here as a further
subcommand when built.

Usage:
    python scripts/run_diagnostic.py era-probe experiments/diagnostics/era_probe_raw_3y.toml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from diagnostics.era_probe import (  # noqa: E402
    DEFAULT_DIAGNOSTIC_REPORTS,
    EraProbeConfig,
    run_era_probe,
)
from harness.dataset import DIAGNOSTIC_SCHEMES, SplitAccess  # noqa: E402
from harness.errors import HarnessError  # noqa: E402
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_RESULTS  # noqa: E402

BANNER = (
    "DIAGNOSTIC ONLY — registered diagnostic (data/manual.md §7): never "
    "model selection, never reported performance."
)


def run_era_probe_command(
    config_path: str | Path,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_DIAGNOSTIC_REPORTS,
) -> dict:
    config = EraProbeConfig.from_file(config_path)
    if config.scheme not in DIAGNOSTIC_SCHEMES:  # belt and braces
        raise HarnessError(
            f"registered diagnostics run only under {sorted(DIAGNOSTIC_SCHEMES)}, "
            f"config has {config.scheme!r}"
        )
    return run_era_probe(
        config,
        data_root=data_root,
        results_path=results_path,
        reports_dir=reports_dir,
        config_path=str(config_path),
        access=SplitAccess.REGISTERED_DIAGNOSTIC,  # the only grant in the repo
    )


HANDLERS = {"era-probe": run_era_probe_command}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="diagnostic", required=True)
    probe = sub.add_parser(
        "era-probe",
        help="predict the calendar year from features alone (raw vs rank sets)",
    )
    probe.add_argument("config", help="path to an experiments/diagnostics/*.toml")
    probe.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    probe.add_argument("--results", default=str(DEFAULT_RESULTS))
    probe.add_argument("--reports-dir", default=str(DEFAULT_DIAGNOSTIC_REPORTS))
    args = parser.parse_args(argv)

    print(BANNER)
    try:
        summary = HANDLERS[args.diagnostic](
            args.config,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
        )
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    m = summary["pooled_metrics"]
    print(f"run {summary['run_id']}: folds {summary['folds']}")
    print(
        f"  accuracy {m['accuracy']:.3f} vs majority-year "
        f"{m.get('baseline_majority_accuracy', float('nan')):.3f}, "
        f"train prior {m['baseline_prior_expected_accuracy']:.3f}, "
        f"uniform {m['baseline_chance_uniform']:.3f}; "
        f"within ±1y {m['within_1y_accuracy']:.3f}; MAE {m['mae_years']:.2f}y"
    )
    print(f"  report: {summary['report_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
