"""Final evaluation on the sealed `holdout` scheme — one look per cell,
every further look disclosed.

This script is the ONLY entry point that is granted FINAL_EVAL split
access (CLAUDE.md hard invariant 2). Everything else in the repo —
runner, baselines, notebooks — is structurally refused the holdout tags.

Point it at the experiment config you selected on walk-forward: the
same config is evaluated on the holdout scheme, in memory — no copied
`*_holdout.toml`. (A config that already says `scheme = "holdout"` runs as
written; the diagnostic schemes are refused.)

What the holdout is for: walk-forward already gives out-of-sample
numbers; the holdout adds the one number nobody *selected on*. It keeps
that meaning only while it is looked at once per cell, so:

- the cell is (label, horizon, holdout window) — the window being the
  test years the holdout fold covers in `split_folds.parquet`, NOT the
  dataset version string: a feature-only dataset bump re-uses the same
  holdout rows and does not re-seal them; only upstream data extending
  the window does, by itself;
- the first completed evaluation in a cell is the sealed look. A second
  one is refused unless `--reopen "reason"` is given — then it runs, the
  reason is logged, and the report, `reports/final_evals.csv` and
  `vml-experiments` all say "holdout look k of N in this cell" from
  then on. Looking N times and keeping the best inflates the number by
  about the top order statistic of N draws (≈ 1.2 standard errors for
  N = 5, on the order of 0.1 in precision@20 over a 3-year holdout), so
  the count is part of the result, never hidden;
- the result is logged whether good or bad — a disappointing holdout
  number is a result, not a do-over.

When to run it: when you would act on the model. If you would not
deploy it yet, walk-forward is where iteration belongs.

Usage:
    python scripts/run_final_eval.py experiments/<config>.toml
    python scripts/run_final_eval.py experiments/<config>.toml \\
        --reopen "new model family after the v1.4 relvalue features"
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from harness.config import ExperimentConfig  # noqa: E402
from harness.dataset import Dataset, SplitAccess  # noqa: E402
from harness.errors import HarnessError  # noqa: E402
from harness.results import git_sha  # noqa: E402
from harness.runner import (  # noqa: E402
    DEFAULT_DATA_ROOT,
    DEFAULT_RESULTS,
    run_experiment,
)

DEFAULT_LEDGER = Path("reports/final_evals.csv")
DEFAULT_FINAL_REPORTS = Path("reports/final_eval")
#: `phase` is the pre-2026-09 key, kept so old rows keep their column;
#: new rows leave it empty. `look` is 1-based within the cell.
LEDGER_FIELDS = [
    "holdout_window",
    "horizon_years",
    "label",
    "look",
    "reopen_reason",
    "experiment",
    "config_hash",
    "dataset_version",
    "run_id",
    "git_sha",
    "logged_utc",
    "status",
    "phase",
]

#: the one scheme a final eval may substitute for holdout
SELECTION_SCHEME = "walkforward"


class HoldoutAlreadyConsumedError(HarnessError):
    """A completed final eval already exists for this cell and no
    `--reopen` reason was given."""


def load_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:  # rows written under an older header
        for f in LEDGER_FIELDS:
            row.setdefault(f, "")
    return rows


def _append_ledger(path: Path, row: dict) -> None:
    """Append under the current header; a ledger written under an older
    header is rewritten with the superset of columns first (rows are
    never dropped or changed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_ledger(path)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for r in existing:
            writer.writerow({f: r.get(f, "") for f in LEDGER_FIELDS})
        writer.writerow({f: row.get(f, "") for f in LEDGER_FIELDS})


def holdout_window(dataset: Dataset, horizon_years: int) -> str:
    """The holdout fold's test window for this horizon, from
    `split_folds.parquet`: `2021-` (open-ended, the usual case) or
    `2021-2023`. This — not the dataset version — identifies the rows."""
    sf = dataset.split_folds
    rows = sf[(sf["scheme"] == "holdout") & (sf["horizon_years"] == horizon_years)]
    if rows.empty:
        raise HarnessError(
            f"split_folds.parquet has no holdout fold for horizon "
            f"{horizon_years}y in {dataset.root}"
        )
    start = pd.Timestamp(rows["test_start"].min())
    end = pd.Timestamp(rows["test_end"].max())
    if pd.isna(end) or end.year >= 9999:
        return f"{start.year}-"
    # test_end is exclusive
    return f"{start.year}-{(end - pd.Timedelta(days=1)).year}"


def cell_of(row: dict) -> tuple[str, str, str]:
    return (str(row.get("holdout_window", "")), str(row.get("horizon_years", "")),
            str(row.get("label", "")))


def looks_in_cell(ledger: list[dict], window: str, horizon_years: int,
                  label: str) -> list[dict]:
    """Completed holdout evaluations of this cell, oldest first. Rows from
    before the window was recorded (legacy `phase` rows) match on label
    and horizon alone: their rows were the same holdout rows unless the
    data was extended, so counting them is the conservative reading."""
    out = []
    for row in ledger:
        if row.get("status") != "completed":
            continue
        if str(row.get("horizon_years")) != str(horizon_years):
            continue
        if row.get("label") != label:
            continue
        if row.get("holdout_window") and row["holdout_window"] != window:
            continue
        out.append(row)
    return out


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


def _describe_looks(looks: list[dict]) -> str:
    parts = []
    for r in looks:
        s = f"{r.get('logged_utc', '')[:10]} {r.get('experiment', '?')} (run {r.get('run_id', '?')})"
        if r.get("reopen_reason"):
            s += f" — reopened: {r['reopen_reason']}"
        elif r.get("phase"):
            s += f" — legacy phase {r['phase']!r}"
        parts.append(s)
    return "\n".join(f"  {i + 1}. {p}" for i, p in enumerate(parts))


def _accounting_section(window: str, horizon: int, label: str, look: int,
                        looks: list[dict], reason: str) -> str:
    lines = [
        "",
        "## Sealed holdout accounting",
        "",
        f"- cell: `{label}` — {horizon}y, holdout window `{window}`",
        f"- **this is holdout look {look} of {len(looks)} in this cell** "
        f"(completed evaluations, all experiments; `reports/final_evals.csv`)",
    ]
    if look == 1:
        lines.append("- the sealed look: nothing in this cell was selected on "
                     "the holdout before this number")
    else:
        lines.append(
            f"- re-opened: {reason}. Numbers in a cell looked at {len(looks)} "
            "times are selection-biased in proportion (best-of-N inflates by "
            "roughly the top order statistic of N draws); read this one "
            "against the earlier looks, not on its own:"
        )
        lines.append("")
        lines.append("```")
        lines.append(_describe_looks(looks))
        lines.append("```")
    lines.append("")
    return "\n".join(lines)


def run_final_eval(
    config_path: str | Path,
    *,
    reopen: str | None = None,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_FINAL_REPORTS,
    ledger_path: str | Path = DEFAULT_LEDGER,
) -> dict:
    config = holdout_variant(ExperimentConfig.from_file(config_path))
    dataset = Dataset(Path(data_root) / config.dataset_version)
    window = holdout_window(dataset, config.horizon_years)
    label = config.eval_label or config.label

    ledger_path = Path(ledger_path)
    ledger = load_ledger(ledger_path)
    prior = looks_in_cell(ledger, window, config.horizon_years, label)
    if prior and not reopen:
        raise HoldoutAlreadyConsumedError(
            f"holdout already evaluated for cell ({label}, "
            f"{config.horizon_years}y, window {window}) — {len(prior)} "
            f"completed look(s):\n{_describe_looks(prior)}\n"
            "The sealed number for this cell is the one you already have. "
            "To look again anyway, pass --reopen \"<why this is a new "
            "candidate>\"; the run is then logged as look "
            f"{len(prior) + 1} and every report in this cell says so."
        )
    if reopen is not None and not reopen.strip():
        raise HarnessError("--reopen needs a reason, not an empty string")
    look = len(prior) + 1

    base = {
        "holdout_window": window,
        "horizon_years": str(config.horizon_years),
        "label": label,
        "look": str(look),
        "reopen_reason": (reopen or "").strip() if prior else "",
        "experiment": config.name,
        "config_hash": config.config_hash,
        "dataset_version": config.dataset_version,
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
    row = {**base, "run_id": summary["run_id"], "status": "completed"}
    _append_ledger(ledger_path, row)
    looks = [*prior, row]
    section = _accounting_section(window, config.horizon_years, label, look,
                                  looks, base["reopen_reason"])
    report_path = Path(summary["report_path"])
    with open(report_path, "a") as fh:
        fh.write(section)
    summary.update({"holdout_window": window, "look": look,
                    "looks_in_cell": len(looks)})
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "config",
        help="the selected experiment's config (walkforward; evaluated on "
        "holdout in memory) or a config with scheme='holdout'",
    )
    parser.add_argument(
        "--reopen", metavar="REASON", default=None,
        help="evaluate a cell whose holdout was already looked at; the "
        "reason is logged and every report in the cell states the look count",
    )
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_FINAL_REPORTS))
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    args = parser.parse_args(argv)
    try:
        summary = run_final_eval(
            args.config,
            reopen=args.reopen,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
            ledger_path=args.ledger,
        )
    except HarnessError as exc:
        print(f"final eval refused/failed: {exc}")
        return 1
    print(
        f"FINAL EVAL COMPLETE — run {summary['run_id']}; holdout look "
        f"{summary['look']} of {summary['looks_in_cell']} in this cell "
        f"(window {summary['holdout_window']}).\n"
        f"report: {summary['report_path']}\n"
        f"ledger: {args.ledger} (tracked — commit it)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
