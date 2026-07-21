"""Run the full Phase-1 baseline grid: every (horizon, label) cell ×
{majority_class, book_to_market_rank, earnings_yield_rank, random}.

Baselines are computed before any tree is trained; each run goes through
the ordinary harness (same logging, same reports, same guardrails).
Failures are logged to the results store and the grid continues.

Usage:
    python scripts/run_baselines.py dataset_v1.0 [--data-root data/datasets]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from harness.config import ExperimentConfig  # noqa: E402
from harness.dataset import Dataset  # noqa: E402
from harness.errors import HarnessError  # noqa: E402
from harness.runner import (  # noqa: E402
    DEFAULT_DATA_ROOT,
    DEFAULT_REPORTS,
    DEFAULT_RESULTS,
    run_experiment,
)

BASELINES = {
    "majority": {"name": "majority_class"},
    "b2m_rank": {"name": "rank_factor", "rank_column": "book_to_market_rank"},
    "ey_rank": {"name": "rank_factor", "rank_column": "earnings_yield_rank"},
    "random": {"name": "random_ranking"},
}
THRESHOLDS = (0, 5, 8, 10)


def cell_labels(dataset: Dataset, horizon: int) -> list[str]:
    """Label columns for one horizon's cells, verified against the
    manifest labels group (constructed names, never pattern matches)."""
    candidates = [f"label_{horizon}y_cagr_ge_{t}" for t in THRESHOLDS]
    candidates.append(f"label_{horizon}y_beat_spy")
    known = set(dataset.columns("labels"))
    return [c for c in candidates if c in known]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_version")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)

    dataset = Dataset(Path(args.data_root) / args.dataset_version)
    failures = 0
    for horizon in dataset.horizons_years:
        if not dataset.folds("walkforward", horizon):
            print(f"skip  horizon {horizon}y: no walkforward folds")
            continue
        for label in cell_labels(dataset, horizon):
            for tag, model in BASELINES.items():
                config = ExperimentConfig.from_dict(
                    {
                        "name": f"baseline_{tag}_{label}",
                        "dataset_version": args.dataset_version,
                        "scheme": "walkforward",
                        "folds": "all",
                        "horizon_years": horizon,
                        "label": label,
                        "feature_groups": ["ranks"],
                        "seed": args.seed,
                        "top_k": [20, 50],
                        "model": model,
                    }
                )
                try:
                    summary = run_experiment(
                        config,
                        data_root=args.data_root,
                        results_path=args.results,
                        reports_dir=args.reports_dir,
                    )
                    print(f"ok    {config.name} folds={summary['folds']}")
                except (HarnessError, ValueError) as exc:
                    failures += 1
                    print(f"FAIL  {config.name}: {exc} (logged)")
    print(f"done; {failures} failed runs (all logged to {args.results})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
