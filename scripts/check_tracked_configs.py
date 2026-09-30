#!/usr/bin/env python3
"""Keep working material out of the integration branches.

Configs and reports are git-ignored working material: most get written,
run once and forgotten. An agent's lab branch tracks them anyway
(`vml-queue checkpoint` force-adds them) so that a lost sandbox loses
nothing. This script is the other half: it names what a branch adds
that should not reach `Claude` or `main`, and with `--fix` takes it out
of the index (the files stay on disk).

What a branch may add, compared with its base:

- a config under `experiments/` that a promoted result names
  (`reports/promoted/*/promoted.json`, written by `vml-promote`);
- `experiments/queue.toml` and ledger shards (`experiments/ledger/`);
- reports under `reports/promoted/`, `reports/final_eval/`, and
  `reports/final_evals.csv`.

Everything else under `experiments/**/*.toml` and `reports/` is reported.
Files the base already tracks are left alone: examples and earlier
decisions are not this script's to revisit. To keep a config that is
not promoted, as an example, name it in `experiments/KEEP` (one path
per line) in the same change.

    python scripts/check_tracked_configs.py                 # against origin/Claude
    python scripts/check_tracked_configs.py --base origin/main
    python scripts/check_tracked_configs.py --fix           # untrack, keep on disk

Exit status 1 when something is reported and not fixed. Standard
library only, so it runs in CI before anything is installed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

KEEP_FILE = Path("experiments/KEEP")
ALLOWED_REPORT_PREFIXES = ("reports/promoted/", "reports/final_eval/")
ALLOWED_REPORT_FILES = {"reports/final_evals.csv", "reports/.gitkeep"}
ALLOWED_EXPERIMENT_FILES = {"experiments/queue.toml"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def added_files(base: str) -> list[str]:
    """Files tracked at HEAD (or staged) that the merge base with
    `base` does not have."""
    merge_base = git("merge-base", base, "HEAD").strip()
    have = set(git("ls-files").splitlines())
    had = set(git("ls-tree", "-r", "--name-only", merge_base).splitlines())
    return sorted(have - had)


def promoted_configs(root: Path = Path("reports/promoted")) -> set[str]:
    out: set[str] = set()
    for record in root.glob("*/promoted.json"):
        try:
            path = json.loads(record.read_text()).get("config_path", "")
        except (OSError, ValueError):
            continue
        if path:
            # sweep runs record `<sweep file>#<run name>`
            out.add(path.split("#", 1)[0])
    return out


def kept_configs() -> set[str]:
    if not KEEP_FILE.exists():
        return set()
    return {
        line.strip()
        for line in KEEP_FILE.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def unwanted(files: list[str]) -> list[tuple[str, str]]:
    """(path, why) for every added file that is working material."""
    promoted = promoted_configs()
    kept = kept_configs()
    found = []
    for f in files:
        if f.startswith("experiments/") and f.endswith(".toml"):
            if f in ALLOWED_EXPERIMENT_FILES or f in promoted or f in kept:
                continue
            found.append((f, "config not promoted and not in experiments/KEEP"))
        elif f.startswith("reports/"):
            if f in ALLOWED_REPORT_FILES or f.startswith(ALLOWED_REPORT_PREFIXES):
                continue
            found.append((f, "report outside reports/promoted/"))
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", default="origin/Claude")
    parser.add_argument(
        "--fix", action="store_true",
        help="remove what is reported from the index (files stay on disk); "
        "commit the result yourself",
    )
    args = parser.parse_args(argv)
    try:
        found = unwanted(added_files(args.base))
    except subprocess.CalledProcessError as exc:
        print(f"git failed: {exc.stderr.strip()}", file=sys.stderr)
        return 2
    if not found:
        print(f"nothing added since {args.base} that should stay out")
        return 0
    verb = "untracking" if args.fix else "working material added since"
    print(f"{verb} {args.base}:" if not args.fix else f"{verb}:")
    for path, why in found:
        print(f"  {path}  ({why})")
    if args.fix:
        git("rm", "-q", "--cached", "--", *[p for p, _ in found])
        print(
            f"{len(found)} file(s) removed from the index and kept on disk. "
            "Commit to record it."
        )
        return 0
    print(
        f"{len(found)} file(s). Promote what is worth keeping "
        "(vml-promote <name> --note \"...\"), or run with --fix on the "
        "branch that goes into the pull request."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
