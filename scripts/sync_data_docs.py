#!/usr/bin/env python3
"""Sync the dataset documentation in data/ from the upstream builder repo.

The .md files under data/ (manual, dataset, labels, splits, features) are
*copies* of the upstream `radarash-dataset` docs — this repo needs them
committed for context (agents must not have to pull the whole upstream
repo), but they drift silently as the builder evolves. This script makes
the copy explicit and checkable:

- `sync` copies the docs from a local upstream checkout and records
  provenance (upstream commit, branch, dirty flag, per-file hashes) in
  `data/upstream.json`, which is committed alongside the docs.
- `--check` compares without copying and exits non-zero on drift — cheap
  enough to run at the start of any modeling session (or in CI where the
  upstream checkout exists).

The upstream checkout is found from, in order: `--upstream`, the
`VML_UPSTREAM_ROOT` environment variable, or the target of the
`data/datasets/dataset_*` symlinks (they already point into the upstream
working tree). Each doc is searched for under `docs/`, `data/`, and the
upstream root, so upstream layout changes don't break the sync.

Dataset *version* requirements are a separate mechanism: configs declare
`min_dataset_version` (see data/versions.md), which the harness enforces
against the loaded manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
PROVENANCE = DATA_DIR / "upstream.json"

#: The docs this repo mirrors, and where upstream may keep them.
DOC_FILES = ("manual.md", "dataset.md", "labels.md", "splits.md",
             "features.md")
UPSTREAM_CANDIDATE_DIRS = ("docs", "data", ".")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(upstream: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(upstream), *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def find_upstream(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("VML_UPSTREAM_ROOT")
    if env:
        return Path(env).expanduser()
    datasets = DATA_DIR / "datasets"
    if datasets.is_dir():
        for entry in sorted(datasets.iterdir()):
            if entry.is_symlink():
                target = entry.resolve()
                # .../<upstream>/data/datasets/dataset_vX.Y -> <upstream>
                for parent in target.parents:
                    if (parent / ".git").exists():
                        return parent
    raise SystemExit(
        "cannot locate the upstream radarash-dataset checkout: pass "
        "--upstream, set VML_UPSTREAM_ROOT, or symlink a dataset under "
        "data/datasets/ into the upstream working tree"
    )


def locate_doc(upstream: Path, name: str) -> Path | None:
    for d in UPSTREAM_CANDIDATE_DIRS:
        candidate = upstream / d / name
        if candidate.is_file():
            return candidate
    return None


def upstream_state(upstream: Path) -> dict:
    try:
        commit = _git(upstream, "rev-parse", "HEAD")
        branch = _git(upstream, "rev-parse", "--abbrev-ref", "HEAD")
        dirty = bool(_git(upstream, "status", "--porcelain"))
    except (OSError, subprocess.CalledProcessError):
        commit, branch, dirty = "unknown", "unknown", True
    return {"commit": commit, "branch": branch, "dirty": dirty}


def run(upstream: Path, check_only: bool) -> int:
    drift: list[str] = []
    missing: list[str] = []
    files: dict[str, dict] = {}
    for name in DOC_FILES:
        src = locate_doc(upstream, name)
        local = DATA_DIR / name
        if src is None:
            missing.append(name)
            continue
        src_hash = _sha256(src)
        local_hash = _sha256(local) if local.exists() else None
        files[name] = {
            "upstream_path": str(src.relative_to(upstream)),
            "sha256": src_hash,
        }
        if src_hash != local_hash:
            drift.append(name)
            if not check_only:
                local.write_bytes(src.read_bytes())

    state = upstream_state(upstream)
    if len(missing) == len(DOC_FILES):
        print(f"ERROR: none of {list(DOC_FILES)} found under {upstream} "
              f"(searched {list(UPSTREAM_CANDIDATE_DIRS)}) — wrong "
              "checkout, or upstream is on a branch without the docs?")
        return 2
    if missing:
        print(f"WARNING: not found upstream (kept as-is locally): {missing}")
    if check_only:
        if drift:
            print(f"DRIFT: local copies differ from upstream: {drift}")
            print(f"(upstream {upstream} @ {state['commit'][:10]}"
                  f"{' +dirty' if state['dirty'] else ''} — run "
                  "scripts/sync_data_docs.py to sync)")
            return 1
        print(f"data/ docs match upstream {upstream} @ {state['commit'][:10]}"
              f"{' +dirty' if state['dirty'] else ''}")
        return 0

    provenance = {
        "upstream_repo": "https://github.com/CarterYancey/radarash-dataset",
        "upstream_root": str(upstream),
        "upstream_commit": state["commit"],
        "upstream_branch": state["branch"],
        "upstream_dirty": state["dirty"],
        "synced_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": files,
    }
    PROVENANCE.write_text(json.dumps(provenance, indent=2) + "\n")
    if drift:
        print(f"synced from upstream @ {state['commit'][:10]}"
              f"{' +dirty' if state['dirty'] else ''}: {drift}")
    else:
        print(f"already in sync with upstream @ {state['commit'][:10]}"
              f"{' +dirty' if state['dirty'] else ''}")
    print(f"provenance written to {PROVENANCE.relative_to(REPO_ROOT)}")
    if state["dirty"]:
        print("NOTE: upstream working tree is dirty — the recorded commit "
              "does not fully identify the doc content; commit upstream "
              "and re-sync for clean provenance.")
    if drift:
        print(f"now: git add data/ && git commit  (docs: {drift})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync (or check) data/*.md against the upstream "
        "radarash-dataset checkout."
    )
    parser.add_argument("--upstream",
                        help="path to the upstream working tree")
    parser.add_argument("--check", action="store_true",
                        help="report drift without copying; exit 1 on drift")
    args = parser.parse_args(argv)
    upstream = find_upstream(args.upstream)
    if not upstream.is_dir():
        raise SystemExit(f"upstream checkout not found: {upstream}")
    return run(upstream, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
