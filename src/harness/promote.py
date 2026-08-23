"""`vml-promote`: mark a generated report as worth keeping.

Everything the harness writes under `reports/` is a working artifact and
git-ignored by default — most runs teach something and then stop
mattering. The ones worth review (an interesting result, a good example)
are *promoted*: copied, with every sibling artifact (`<name>_rules.md`,
`<name>_*.png`), into `reports/promoted/<name>/`, which IS tracked.
Relative links inside the report keep working because the whole artifact
set lands in one directory.

The provenance chain stays intact: a promoted report still cites its run
id, config hash, git SHA and dataset version, and the run remains in the
local results ledger.

Usage:
    vml-promote tree_depth3_2y_cagr_ge_0          # by experiment name
    vml-promote reports/sweeps/grid/_summary.md   # a sweep summary, by path
    vml-promote --list                            # what could be promoted
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_REPORTS = Path("reports")
PROMOTED_DIRNAME = "promoted"


def _artifact_set(report_md: Path) -> list[Path]:
    """The report plus every sibling artifact sharing its name stem."""
    stem = report_md.stem
    files = [report_md]
    for p in sorted(report_md.parent.iterdir()):
        if p == report_md or not p.is_file():
            continue
        if p.name.startswith(f"{stem}_"):
            files.append(p)
    return files


def _resolve_report(target: str, reports_dir: Path) -> Path:
    p = Path(target)
    if p.suffix == ".md" and p.exists():
        return p
    candidate = reports_dir / f"{target}.md"
    if candidate.exists():
        return candidate
    raise SystemExit(
        f"no report found for {target!r} (looked for {candidate} and a "
        "literal .md path)"
    )


def _promotable(reports_dir: Path) -> list[Path]:
    """Top-level generated reports plus sweep summaries, promoted ones
    and their artifact siblings excluded."""
    promoted = reports_dir / PROMOTED_DIRNAME
    out = []
    for p in sorted(reports_dir.glob("*.md")):
        if p.name.endswith("_rules.md"):
            continue
        out.append(p)
    out += sorted(reports_dir.glob("sweeps/*/_summary.md"))
    return [p for p in out if promoted not in p.parents]


def promote(target: str, reports_dir: Path = DEFAULT_REPORTS,
            force: bool = False) -> Path:
    report_md = _resolve_report(target, reports_dir)
    # sweep summaries promote the whole sweep directory name
    if report_md.name == "_summary.md":
        name = f"sweep_{report_md.parent.name}"
        files = [report_md, *(
            p for p in sorted(report_md.parent.iterdir())
            if p.is_file() and p != report_md
        )]
    else:
        name = report_md.stem
        files = _artifact_set(report_md)
    dest = reports_dir / PROMOTED_DIRNAME / name
    if dest.exists() and not force:
        raise SystemExit(
            f"{dest} already exists — re-promote with --force to replace it"
        )
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for f in files:
        shutil.copy2(f, dest / f.name)
    return dest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote a generated report (git-ignored working "
        "output) into the tracked reports/promoted/ directory for review."
    )
    parser.add_argument(
        "target", nargs="?",
        help="experiment name (reports/<name>.md) or a path to a report "
        "/ sweep _summary.md",
    )
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument("--force", action="store_true",
                        help="replace an existing promotion of the same name")
    parser.add_argument("--list", action="store_true",
                        help="list promotable reports and exit")
    args = parser.parse_args(argv)
    reports_dir = Path(args.reports_dir)

    if args.list or not args.target:
        found = _promotable(reports_dir)
        if not found:
            print(f"nothing promotable under {reports_dir}/")
        for p in found:
            print(p)
        return 0

    dest = promote(args.target, reports_dir=reports_dir, force=args.force)
    files = sorted(p.name for p in dest.iterdir())
    print(f"promoted -> {dest}/ ({len(files)} files)")
    for f in files:
        print(f"  {f}")
    print(f"\nnow: git add {dest} && git commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
