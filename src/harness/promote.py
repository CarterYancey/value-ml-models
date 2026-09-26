"""`vml-promote`: mark a result as worth keeping — report, config and
conclusion together, staged for commit in one command.

Everything the harness writes under `reports/` is a working artifact and
git-ignored by default, and so is every new config under `experiments/`
— most runs teach something and then stop mattering. The ones worth
review (an interesting result, a good example) are *promoted*:

- the report and every sibling artifact (`<name>_rules.md`,
  `<name>_*.png`) are copied into `reports/promoted/<name>/`, which IS
  tracked (relative links keep working because the whole set lands in
  one directory), plus a `config.toml` snapshot and a `promoted.json`
  provenance record (run id, config hash, cell, headline vs baseline);
- the config that produced it is force-added to git (it is ignored until
  promoted) and the promoted directory is staged, so `git commit` is all
  that is left;
- `--note "..."` writes the one-line conclusion into the config
  (`note = "..."`, outside the config hash) where `vml-experiments`
  shows it next to the numbers;
- `reports/promoted/README.md`, the index of everything promoted, is
  regenerated: cell, model, headline vs baseline, note, link.

The provenance chain stays intact: a promoted report still cites its run
id, config hash, git SHA and dataset version, and the run remains in the
local results ledger.

Usage:
    vml-promote tree_depth3_2y_cagr_ge_0 --note "depth 3 beats b2m by 0.25"
    vml-promote lgbm_random_search_3y             # a sweep, by its name
    vml-promote --list                            # what could be promoted
    vml-promote --index                           # rebuild the index only
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from harness.catalog import (
    DEFAULT_EXPERIMENTS,
    DEFAULT_RESULTS,
    BaselineLookup,
    config_cell,
    config_note,
    find_config,
    score_columns,
    _fold_mean_metrics,
)
from harness.config import ExperimentConfig
from harness.errors import ConfigError
from harness.results import ResultsStore

DEFAULT_REPORTS = Path("reports")
PROMOTED_DIRNAME = "promoted"
META_FILENAME = "promoted.json"
CONFIG_SNAPSHOT = "config.toml"
INDEX_FILENAME = "README.md"

_REPORT_FIELD = re.compile(r"^- (?P<key>[^:]+): `(?P<value>[^`]*)`")


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


def _is_sweep_summary(report_md: Path) -> bool:
    return (report_md.name.endswith("_summary.md")
            and report_md.parent.parent.name == "sweeps")


def _resolve_report(target: str, reports_dir: Path) -> Path:
    p = Path(target)
    if p.suffix == ".md" and p.exists():
        return p
    candidate = reports_dir / f"{target}.md"
    if candidate.exists():
        return candidate
    sweep = reports_dir / "sweeps" / target / f"{target}_summary.md"
    if sweep.exists():
        return sweep
    raise SystemExit(
        f"no report found for {target!r} (looked for {candidate}, {sweep} "
        "and a literal .md path)"
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
    out += sorted(reports_dir.glob("sweeps/*/*_summary.md"))
    return [p for p in out if promoted not in p.parents]


def _report_header(report_md: Path) -> dict:
    """The `- key: \\`value\\`` provenance lines at the top of a report
    (run id, config hash, dataset version, ...), for the promoted record."""
    out = {}
    try:
        for line in report_md.read_text().splitlines()[:40]:
            m = _REPORT_FIELD.match(line)
            if m:
                key = m.group("key").strip()
                out[key] = m.group("value").strip()
                out[f"_{key}_line"] = line  # the rest, for horizon/scheme
    except OSError:
        pass
    return out


# ----------------------------------------------------------------------
# notes: `note = "..."` written into the config, outside the config hash

def _toml_string(text: str) -> str:
    # a JSON string is a valid TOML basic string for the escapes json
    # emits (\" \\ \n \t \uXXXX)
    return json.dumps(text, ensure_ascii=False)


def set_note(config_path: Path, note: str) -> None:
    """Set the top-level `note` in a TOML config, replacing an existing
    one. The key is not part of `ExperimentConfig`'s canonical payload,
    so the config hash — the ledger identity — is unchanged."""
    text = config_path.read_text()
    lines = text.splitlines()
    new_line = f"note = {_toml_string(note)}"
    for i, line in enumerate(lines):
        if line.startswith("["):  # first table: top-level keys are over
            break
        if re.match(r"^note\s*=", line):
            lines[i] = new_line
            config_path.write_text("\n".join(lines) + "\n")
            return
    # insert after `name = ...` when present, else before the first table
    insert_at = None
    for i, line in enumerate(lines):
        if line.startswith("["):
            break
        if re.match(r"^name\s*=", line):
            insert_at = i + 1
            break
    if insert_at is None:
        insert_at = next((i for i, ln in enumerate(lines) if ln.startswith("[")),
                         len(lines))
    lines.insert(insert_at, new_line)
    config_path.write_text("\n".join(lines) + "\n")
    # must still parse, and still be the same config
    with open(config_path, "rb") as fh:
        tomllib.load(fh)


# ----------------------------------------------------------------------
# locating the config behind a report

def _config_for(name: str, header: dict, experiments_dir: Path,
                store: ResultsStore) -> Path | None:
    """The config that produced report `name`: the ledger's `config_path`
    for that experiment (latest row, must still exist), else a scan of
    `experiments/` by experiment name."""
    df = store.load()
    if not df.empty:
        sel = df[df["experiment"] == name]
        if header.get("config hash"):
            by_hash = df[df["config_hash"] == header["config hash"]]
            if not by_hash.empty:
                sel = by_hash
        for path in reversed(list(sel["config_path"])):
            if path and Path(path).is_file():
                return Path(path)
    return find_config(experiments_dir, name)


def _git(args: list[str], cwd: Path | None = None) -> bool:
    try:
        subprocess.run(["git", *args], cwd=cwd, check=True,
                       capture_output=True, text=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


# ----------------------------------------------------------------------

def promote(
    target: str,
    reports_dir: Path = DEFAULT_REPORTS,
    force: bool = False,
    *,
    note: str | None = None,
    experiments_dir: Path = DEFAULT_EXPERIMENTS,
    results_path: Path = DEFAULT_RESULTS,
    git: bool = True,
) -> Path:
    report_md = _resolve_report(target, reports_dir)
    if _is_sweep_summary(report_md):
        # a sweep promotes its summary (ranking, configurations-tried
        # counts) and the summary CSVs, not the per-run reports: those are
        # candidates, and a candidate worth keeping is promoted by its own
        # report path
        lookup_name = report_md.parent.name
        name = f"sweep_{lookup_name}"
        stem = report_md.stem
        files = [report_md, *(
            p for p in sorted(report_md.parent.iterdir())
            if p.is_file() and p != report_md and p.stem.startswith(stem)
        )]
    else:
        name = lookup_name = report_md.stem
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

    header = _report_header(report_md)
    store = ResultsStore(results_path)
    config_path = _config_for(lookup_name, header, experiments_dir, store)
    meta = {
        "name": name,
        "promoted_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_report": str(report_md),
        "run_id": header.get("run id", ""),
        "config_hash": header.get("config hash", ""),
        "git_sha": header.get("git SHA", ""),
        "dataset_version": header.get("dataset version", ""),
        "config_path": str(config_path) if config_path else "",
        "note": "",
    }
    if config_path is not None:
        if note is not None:
            set_note(config_path, note)
        shutil.copy2(config_path, dest / CONFIG_SNAPSHOT)
        with open(config_path, "rb") as fh:
            raw = tomllib.load(fh)
        meta["note"] = config_note(raw)
        try:
            config = ExperimentConfig.from_dict(raw, source=str(config_path))
        except ConfigError:
            config = None  # a sweep / diagnostic / portfolio config
        if config is not None:
            cell = config_cell(config)
            meta.update({
                "experiment": config.name,
                "model": config.model_name,
                "label": cell[3],
                "horizon_years": cell[2],
                "scheme": cell[1],
                "dataset_version": config.dataset_version,
                "config_hash": config.config_hash,
            })
            meta.update(_scores(store, config, cell, meta["run_id"]))
    elif note is not None:
        meta["note"] = note  # nowhere else to keep it
    meta["files"] = sorted(p.name for p in dest.glob("*.md"))
    (dest / META_FILENAME).write_text(json.dumps(meta, indent=2) + "\n")

    write_index(reports_dir / PROMOTED_DIRNAME)

    if git:
        staged = _git(["add", str(dest)])
        if config_path is not None:
            staged = _git(["add", "-f", str(config_path)]) and staged
        meta["staged"] = staged
    return dest


def _scores(store: ResultsStore, config: ExperimentConfig,
            cell: tuple, run_id: str) -> dict:
    """headline / baseline / lift of the promoted run (the report's run
    id when it is in the ledger, else the config's latest completed run)."""
    df = store.load()
    if df.empty:
        return {}
    sel = df[(df["status"] == "completed") & (df["metrics_json"] != "")]
    rows = sel[sel["run_id"] == run_id] if run_id else sel.iloc[0:0]
    if rows.empty:
        rows = sel[sel["config_hash"] == config.config_hash]
        if rows.empty:
            return {}
        rows = rows[rows["run_id"] == rows.iloc[-1]["run_id"]]
    scores = score_columns(_fold_mean_metrics(rows), cell,
                           BaselineLookup(store))
    return {k: scores[k] for k in ("headline", "baseline", "lift")}


# ----------------------------------------------------------------------
# the index

def _legacy_meta(d: Path) -> dict:
    """A record for a promoted directory predating `promoted.json`,
    from its report header when it has one."""
    meta = {"name": d.name}
    report = d / f"{d.name}.md"
    if report.exists():
        header = _report_header(report)
        meta.update({
            "run_id": header.get("run id", ""),
            "config_hash": header.get("config hash", ""),
            "dataset_version": header.get("dataset version", ""),
        })
        model = header.get("model", "")
        if model:
            meta["model"] = model
        label = header.get("label", "")
        if label:
            meta["label"] = label
            m = re.search(r"horizon (\d+)y, scheme `([^`]+)`",
                          header.get("_label_line", ""))
            if m:
                meta["horizon_years"] = int(m.group(1))
                meta["scheme"] = m.group(2)
    md = sorted(p.name for p in d.glob("*.md"))
    meta["files"] = md
    return meta


def load_promoted(promoted_dir: Path) -> list[dict]:
    out = []
    for d in sorted(p for p in promoted_dir.iterdir() if p.is_dir()):
        meta_path = d / META_FILENAME
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
        else:
            meta = _legacy_meta(d)
        meta["dir"] = d.name
        out.append(meta)
    return out


def _md_cell(s) -> str:
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def render_index(records: list[dict]) -> str:
    lines = [
        "# Promoted results",
        "",
        "Generated by `vml-promote` — do not edit; re-run `vml-promote "
        "--index` to rebuild. One row per promoted directory, newest first. "
        "`lift` is the headline metric minus the best baseline in the same "
        "cell (label, horizon, scheme, dataset version) at promotion time; "
        "numbers across cells are not comparable. Every report cites its "
        "run id, config hash, git SHA and `split_folds.parquet`.",
        "",
        "| promoted | result | cell | model | dataset | headline | baseline "
        "| lift | note |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    records = sorted(records, key=lambda m: m.get("promoted_utc", ""),
                     reverse=True)
    for m in records:
        d = m["dir"]
        files = m.get("files") or [f"{d}.md"]
        report = f"{d}.md" if f"{d}.md" in files else files[0]
        link = f"[{d}]({d}/{report})"
        label = m.get("label", "")
        cell = label
        if m.get("horizon_years"):
            cell += f" · {m['horizon_years']}y"
        if m.get("scheme"):
            cell += f" · {m['scheme']}"
        lines.append("| " + " | ".join(_md_cell(x) for x in (
            (m.get("promoted_utc") or "")[:10],
            link,
            cell,
            m.get("model", ""),
            m.get("dataset_version", ""),
            m.get("headline", ""),
            m.get("baseline", ""),
            m.get("lift", ""),
            m.get("note", ""),
        )) + " |")
    lines.append("")
    return "\n".join(lines)


def write_index(promoted_dir: Path) -> Path:
    promoted_dir.mkdir(parents=True, exist_ok=True)
    path = promoted_dir / INDEX_FILENAME
    path.write_text(render_index(load_promoted(promoted_dir)))
    return path


# ----------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote a generated report (git-ignored working "
        "output) into the tracked reports/promoted/ directory, together "
        "with the config that produced it and your one-line conclusion."
    )
    parser.add_argument(
        "target", nargs="?",
        help="experiment name (reports/<name>.md) or a path to a report "
        "/ sweep _summary.md",
    )
    parser.add_argument("--note", default=None,
                        help="one-line conclusion, written into the config "
                        "as `note = ...` and shown by vml-experiments")
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument("--experiments-dir", default=str(DEFAULT_EXPERIMENTS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--force", action="store_true",
                        help="replace an existing promotion of the same name")
    parser.add_argument("--no-git", action="store_true",
                        help="copy only; do not stage the config and "
                        "promoted directory")
    parser.add_argument("--list", action="store_true",
                        help="list promotable reports and exit")
    parser.add_argument("--index", action="store_true",
                        help="rebuild reports/promoted/README.md and exit")
    args = parser.parse_args(argv)
    reports_dir = Path(args.reports_dir)

    if args.index:
        path = write_index(reports_dir / PROMOTED_DIRNAME)
        print(f"index rebuilt -> {path}")
        return 0
    if args.list or not args.target:
        found = _promotable(reports_dir)
        if not found:
            print(f"nothing promotable under {reports_dir}/")
        for p in found:
            print(p)
        return 0

    dest = promote(
        args.target, reports_dir=reports_dir, force=args.force,
        note=args.note, experiments_dir=Path(args.experiments_dir),
        results_path=Path(args.results), git=not args.no_git,
    )
    files = sorted(p.name for p in dest.iterdir())
    print(f"promoted -> {dest}/ ({len(files)} files)")
    for f in files:
        print(f"  {f}")
    meta = json.loads((dest / META_FILENAME).read_text())
    if meta.get("config_path"):
        print(f"config: {meta['config_path']}"
              + (" (note written)" if args.note is not None else ""))
    else:
        print("config: not found (no ledger row and no experiments/*.toml "
              "with this name) — nothing staged for it")
    if meta.get("headline"):
        print(f"score:  {meta['headline']}  baseline {meta.get('baseline', '')}"
              f"  lift {meta.get('lift', '')}")
    index = reports_dir / PROMOTED_DIRNAME / INDEX_FILENAME
    print(f"index:  {index}")
    if args.no_git:
        print(f"\nnow: git add -f {meta.get('config_path', '')} {dest} "
              f"{index} && git commit")
    elif meta.get("staged"):
        print("\nstaged; now: git commit")
    else:
        print(f"\ngit staging failed — by hand: git add -f "
              f"{meta.get('config_path', '')} {dest} {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
