"""Unattended runs: a queue of sweeps, a logbook, and checkpoints.

Built for an agent working through experiments on its own (docs/agents.md),
and usable by hand. Three rules shape it:

- **Nothing waits on a process.** `vml-queue run-next` runs one queued
  sweep and exits. Whoever launched it is woken by the exit, not by
  polling, and decides then what happens next.
- **What was learned is written down before anything else happens.**
  When a sweep ends, a logbook entry is written from the facts alone
  (what ran, how many runs, how many failed), before anyone has read
  the numbers. The reader's conclusion replaces that stub later
  (`vml-logbook add`). A crash between the two loses an interpretation,
  never the record that the sweep ran.
- **A checkpoint is a commit of everything a lost machine would take
  with it:** the ledger shard, the sweep's summary, config copy and
  result records, the logbook and the notes. Configs and reports are
  git-ignored working material, so a checkpoint force-adds them, and it
  refuses to do that anywhere but a `claude/` branch: what reaches
  `Claude` is chosen later (scripts/check_tracked_configs.py).

The queue is `experiments/queue.toml`:

    [[item]]
    config = "experiments/sweeps/baseline_pick_outcomes_3y.toml"
    why = "the single-factor bar for the pick-outcome screen"

An item's state is read from its report directory, never stored: `done`
when every expanded run has a result record under the config's hash and
the summary exists, `partial` when some have, `pending` otherwise. The
first item that is not done is the next one.
"""

from __future__ import annotations

import subprocess
import tomllib
import traceback
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from harness.errors import ConfigError
from harness.results import git_sha
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_REPORTS, DEFAULT_RESULTS
from harness.sweep import SweepConfig, _read_run_record, run_sweep

DEFAULT_QUEUE = Path("experiments/queue.toml")
DEFAULT_LOGBOOK = Path("docs/logbook.md")
NOTES_DIR = Path("docs/notes")

#: branches a checkpoint may commit to: topic branches only
LAB_BRANCH_PREFIX = "claude/"

LOGBOOK_HEADER = """# Logbook

One entry per sweep or run, newest first: what was done, what came out,
what was concluded, what follows. Read this first. Conclusions that
span entries are in [findings.md](findings.md); tables and reasoning
are in the note an entry links to ([notes/](notes/)).

An entry that says **not yet read** was written by the machine when the
sweep ended. Its numbers exist (summary linked) and nobody has drawn a
conclusion from them.

Entries are never edited after the fact except to replace a **not yet
read** stub; a correction is a new entry that names the old one.

<!-- entries -->
"""

ENTRY_MARK = "<!-- entries -->"
STUB_MARK = "**not yet read**"


# --------------------------------------------------------------------------
# queue


@dataclass(frozen=True)
class QueueItem:
    config: Path
    why: str = ""


@dataclass(frozen=True)
class ItemState:
    item: QueueItem
    name: str
    n_runs: int
    n_done: int
    summary: Path
    error: str = ""

    @property
    def state(self) -> str:
        if self.error:
            return "broken"
        if self.n_done >= self.n_runs and self.summary.exists():
            return "done"
        return "partial" if self.n_done else "pending"


def load_queue(path: str | Path = DEFAULT_QUEUE) -> list[QueueItem]:
    path = Path(path)
    try:
        with open(path, "rb") as fh:
            raw = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot read queue {path}: {exc}") from exc
    items = raw.get("item", [])
    if not isinstance(items, list):
        raise ConfigError(f"queue {path}: [[item]] must be a list of tables")
    out = []
    for i, entry in enumerate(items):
        unknown = sorted(set(entry) - {"config", "why"})
        if unknown or "config" not in entry:
            raise ConfigError(
                f"queue {path}: item {i} needs a `config` and may carry a "
                f"`why`; unknown keys {unknown}"
            )
        out.append(QueueItem(Path(entry["config"]), str(entry.get("why", ""))))
    dupes = {str(i.config) for i in out if [j.config for j in out].count(i.config) > 1}
    if dupes:
        raise ConfigError(f"queue {path}: configs listed twice: {sorted(dupes)}")
    return out


def sweep_report_dir(sweep: SweepConfig, reports_dir: str | Path) -> Path:
    return Path(reports_dir) / "sweeps" / sweep.name


def item_state(item: QueueItem, reports_dir: str | Path = DEFAULT_REPORTS) -> ItemState:
    try:
        sweep = SweepConfig.from_file(item.config)
        runs = sweep.expand()
    except Exception as exc:  # a broken config must not hide the rest
        return ItemState(
            item, item.config.stem, 0, 0, Path(), f"{type(exc).__name__}: {exc}"
        )
    root = sweep_report_dir(sweep, reports_dir)
    run_dir = root / "seeds" if len(sweep.seeds) > 1 else root
    done = sum(
        1
        for run in runs
        if _read_run_record(run_dir / f"{run.config.name}_result.json", run)
    )
    return ItemState(
        item, sweep.name, len(runs), done, root / f"{sweep.name}_summary.md"
    )


def queue_states(
    queue_path: str | Path = DEFAULT_QUEUE,
    reports_dir: str | Path = DEFAULT_REPORTS,
) -> list[ItemState]:
    return [item_state(i, reports_dir) for i in load_queue(queue_path)]


def next_item(states: list[ItemState]) -> ItemState | None:
    for s in states:
        if s.state != "done":
            return s
    return None


def format_states(states: list[ItemState]) -> str:
    if not states:
        return "queue is empty"
    width = max(len(s.name) for s in states)
    lines = []
    for s in states:
        progress = s.error if s.error else f"{s.n_done}/{s.n_runs} runs"
        lines.append(f"{s.state:8s} {s.name:{width}s}  {progress}")
        if s.item.why:
            lines.append(f"{'':8s} {'':{width}s}  {s.item.why}")
    nxt = next_item(states)
    lines.append("")
    lines.append(f"next: {nxt.name}" if nxt else "next: nothing, the queue is done")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# logbook


def _entry_heading(name: str, day: str) -> str:
    return f"### {day} · {name}"


def _facts_line(
    *, n_runs, n_failed, dataset_version, cells, sha, summary: Path | None,
    note: Path | None, logbook: Path,
) -> str:
    parts = []
    if n_runs is not None:
        failed = f" ({n_failed} failed)" if n_failed else ""
        parts.append(f"{n_runs} runs{failed}")
    if dataset_version:
        parts.append(f"`{dataset_version}`")
    if cells:
        parts.append(cells)
    if sha:
        parts.append(f"git `{sha[:7]}`")
    for label, target in (("summary", summary), ("note", note)):
        if target:
            parts.append(f"[{label}]({_relative(target, logbook.parent)})")
    return " · ".join(parts)


def _relative(target: Path, start: Path) -> str:
    import os

    return os.path.relpath(target, start).replace(os.sep, "/")


def _split_entries(text: str) -> tuple[str, list[str]]:
    """(everything up to and including the entry mark, the entries)."""
    if ENTRY_MARK not in text:
        raise ConfigError(
            f"logbook lacks its `{ENTRY_MARK}` line; entries go below it"
        )
    head, body = text.split(ENTRY_MARK, 1)
    entries, current = [], []
    for line in body.strip("\n").splitlines():
        if line.startswith("### ") and current:
            entries.append("\n".join(current).strip("\n"))
            current = []
        current.append(line)
    if current and "".join(current).strip():
        entries.append("\n".join(current).strip("\n"))
    return head + ENTRY_MARK + "\n", entries


def add_entry(
    name: str,
    *,
    did: str = "",
    got: str = "",
    concluded: str = "",
    next_step: str = "",
    facts: str = "",
    stub: bool = False,
    day: str | None = None,
    logbook: str | Path = DEFAULT_LOGBOOK,
) -> Path:
    """Write one logbook entry at the top. A **not yet read** stub of
    the same name is replaced by the entry that reads it; any other
    entry of that name stays, and the new one goes above it."""
    logbook = Path(logbook)
    if not logbook.exists():
        logbook.parent.mkdir(parents=True, exist_ok=True)
        logbook.write_text(LOGBOOK_HEADER)
    if not stub and not (did and got and concluded):
        raise ConfigError(
            "a logbook entry states what was done, what came out and what "
            "was concluded (--did, --got, --concluded)"
        )
    head, entries = _split_entries(logbook.read_text())
    day = day or date.today().isoformat()
    lines = [_entry_heading(name, day)]
    if facts:
        lines.append(facts)
    if stub:
        lines.append(f"- {STUB_MARK}: the sweep ended, its numbers are unread.")
    else:
        lines.append(f"- **Did:** {did.strip()}")
        lines.append(f"- **Got:** {got.strip()}")
        lines.append(f"- **Concluded:** {concluded.strip()}")
        if next_step:
            lines.append(f"- **Next:** {next_step.strip()}")
    entry = "\n".join(lines)

    def is_stub_of(e: str) -> bool:
        first = e.splitlines()[0]
        return first.endswith(f"· {name}") and STUB_MARK in e

    if stub and any(is_stub_of(e) for e in entries):
        entries = [entry if is_stub_of(e) else e for e in entries]
    else:
        if not stub and not facts:
            # keep the machine's facts line when replacing its stub
            for e in entries:
                if is_stub_of(e):
                    kept = [
                        l for l in e.splitlines()[1:] if not l.startswith("- ")
                    ]
                    if kept:
                        lines.insert(1, kept[0])
                        entry = "\n".join(lines)
        entries = [entry] + [e for e in entries if not is_stub_of(e)]
    logbook.write_text(head + "\n" + "\n\n".join(entries) + "\n")
    return logbook


def sweep_facts(
    config_path: str | Path,
    *,
    reports_dir: str | Path = DEFAULT_REPORTS,
    logbook: str | Path = DEFAULT_LOGBOOK,
    note: Path | None = None,
    n_failed: int | None = None,
) -> tuple[str, str]:
    """(sweep name, facts line) for a logbook entry about a sweep, read
    from its config and report directory."""
    sweep = SweepConfig.from_file(config_path)
    root = sweep_report_dir(sweep, reports_dir)
    summary = root / f"{sweep.name}_summary.md"
    cells = sorted({label for _, label, _ in sweep.cells})
    cell_text = f"`{cells[0]}`" if len(cells) == 1 else f"{len(cells)} cells"
    if n_failed is None:
        n_failed = 0
        csv_path = root / f"{sweep.name}_summary.csv"
        if csv_path.exists():
            import pandas as pd

            n_failed = int((pd.read_csv(csv_path)["status"] == "failed").sum())
    return sweep.name, _facts_line(
        n_runs=len(sweep.expand()),
        n_failed=n_failed,
        dataset_version=sweep.dataset_version,
        cells=cell_text,
        sha=git_sha(),
        summary=summary if summary.exists() else None,
        note=note,
        logbook=Path(logbook),
    )


# --------------------------------------------------------------------------
# checkpoint


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=check
    )


def current_branch() -> str:
    return _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def checkpoint_paths(
    *,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    queue_path: str | Path = DEFAULT_QUEUE,
    logbook: str | Path = DEFAULT_LOGBOOK,
) -> list[Path]:
    """What a checkpoint commits: text a lost machine would take with
    it. Figures, per-run reports and importances stay working material
    (they are large, and rebuilt by re-running); a result worth keeping
    in full goes through `vml-promote`."""
    paths: list[Path] = []
    results_path = Path(results_path)
    # the local ledger stays local; shards are what travels
    if results_path.parent.name == "ledger" and results_path.exists():
        paths.append(results_path)
    for p in (Path(queue_path), Path(logbook), Path("docs/findings.md")):
        if p.exists():
            paths.append(p)
    if NOTES_DIR.is_dir():
        paths += sorted(NOTES_DIR.glob("*.md"))
    try:
        items = load_queue(queue_path)
    except ConfigError:
        items = []
    for item in items:
        if item.config.exists():
            paths.append(item.config)
        try:
            sweep = SweepConfig.from_file(item.config)
        except Exception:
            continue
        root = sweep_report_dir(sweep, reports_dir)
        if root.is_dir():
            paths += sorted(root.glob(f"{sweep.name}_summary*"))
            paths += sorted(root.glob(f"{sweep.name}_config.toml"))
            paths += sorted(root.rglob("*_result.json"))
    return paths


def checkpoint(
    message: str,
    *,
    push: bool = False,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    queue_path: str | Path = DEFAULT_QUEUE,
    logbook: str | Path = DEFAULT_LOGBOOK,
) -> dict:
    """Commit the checkpoint paths on the current `claude/` branch and,
    with `push`, push it. Returns what happened; a push that fails is
    reported, not raised: the commit is still there to push later."""
    branch = current_branch()
    if not branch.startswith(LAB_BRANCH_PREFIX):
        raise ConfigError(
            f"checkpoints go on `{LAB_BRANCH_PREFIX}*` branches; this is "
            f"{branch!r}. Create one first: git checkout -b "
            f"{LAB_BRANCH_PREFIX}lab-<date>"
        )
    paths = checkpoint_paths(
        results_path=results_path, reports_dir=reports_dir,
        queue_path=queue_path, logbook=logbook,
    )
    if paths:
        _git("add", "-f", "--", *[str(p) for p in paths])
    staged = _git("diff", "--cached", "--name-only").stdout.split()
    out = {"branch": branch, "files": len(staged), "committed": False,
           "pushed": False, "push_error": ""}
    if staged:
        _git("commit", "-q", "-m", message)
        out["committed"] = True
    if push:
        res = _git("push", "-u", "origin", branch, check=False)
        out["pushed"] = res.returncode == 0
        if not out["pushed"]:
            out["push_error"] = (res.stderr or res.stdout).strip()[-400:]
    return out


# --------------------------------------------------------------------------
# run-next


def run_next(
    *,
    queue_path: str | Path = DEFAULT_QUEUE,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    logbook: str | Path = DEFAULT_LOGBOOK,
    do_checkpoint: bool = True,
    push: bool = False,
) -> dict:
    """Run the first queue item that is not done (resuming it if it was
    interrupted), write its logbook stub, checkpoint, and return."""
    states = queue_states(queue_path, reports_dir)
    broken = [s for s in states if s.state == "broken"]
    if broken:
        raise ConfigError(
            "queue has configs that do not load: "
            + "; ".join(f"{s.name}: {s.error}" for s in broken)
        )
    nxt = next_item(states)
    if nxt is None:
        return {"ran": None, "remaining": 0}
    sweep = SweepConfig.from_file(nxt.item.config)
    print(
        f"queue: running {sweep.name} "
        f"({nxt.n_runs - nxt.n_done} of {nxt.n_runs} runs to go)",
        flush=True,
    )
    result = run_sweep(
        sweep,
        data_root=data_root,
        results_path=results_path,
        reports_dir=reports_dir,
        sweep_config_path=str(nxt.item.config),
        resume=True,
    )
    name, facts = sweep_facts(
        nxt.item.config, reports_dir=reports_dir, logbook=logbook,
        n_failed=result["n_failed"],
    )
    add_entry(name, facts=facts, stub=True, logbook=logbook)
    out = {
        "ran": name,
        "n_runs": len(result["runs"]),
        "n_failed": result["n_failed"],
        "summary": result["summary_md"],
        "remaining": sum(
            1 for s in queue_states(queue_path, reports_dir) if s.state != "done"
        ),
    }
    if do_checkpoint:
        try:
            out["checkpoint"] = checkpoint(
                f"lab: {name}, {out['n_runs']} runs "
                f"({out['n_failed']} failed), not yet read",
                push=push, results_path=results_path,
                reports_dir=reports_dir, queue_path=queue_path,
                logbook=logbook,
            )
        except (ConfigError, subprocess.CalledProcessError) as exc:
            # the runs are done and logged; a checkpoint can be retried
            out["checkpoint_error"] = f"{type(exc).__name__}: {exc}"
    return out


# --------------------------------------------------------------------------
# CLIs


def _queue_main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Work through experiments/queue.toml one sweep at a "
        "time (docs/agents.md)."
    )
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--logbook", default=str(DEFAULT_LOGBOOK))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="state of every queued sweep, and the next one")
    run = sub.add_parser(
        "run-next",
        help="run the next sweep that is not done, log it, checkpoint, exit",
    )
    run.add_argument("--push", action="store_true",
                     help="push the checkpoint commit")
    run.add_argument("--no-checkpoint", action="store_true",
                     help="run and log only; commit nothing")
    cp = sub.add_parser("checkpoint", help="commit (and push) what a crash would lose")
    cp.add_argument("-m", "--message", default="lab: checkpoint")
    cp.add_argument("--push", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(format_states(queue_states(args.queue, args.reports_dir)))
            return 0
        if args.command == "checkpoint":
            out = checkpoint(
                args.message, push=args.push, results_path=args.results,
                reports_dir=args.reports_dir, queue_path=args.queue,
                logbook=args.logbook,
            )
            print(_describe_checkpoint(out))
            return 0 if (out["pushed"] or not args.push) else 2
        out = run_next(
            queue_path=args.queue, data_root=args.data_root,
            results_path=args.results, reports_dir=args.reports_dir,
            logbook=args.logbook, do_checkpoint=not args.no_checkpoint,
            push=args.push,
        )
    except Exception:
        traceback.print_exc()
        print("queue FAILED")
        return 1
    if out["ran"] is None:
        print("queue: nothing to run, every item is done")
        return 0
    print(
        f"queue: {out['ran']} finished, {out['n_runs']} runs, "
        f"{out['n_failed']} failed; {out['remaining']} item(s) not done"
    )
    print(f"summary: {out['summary']}")
    if "checkpoint" in out:
        print(_describe_checkpoint(out["checkpoint"]))
    if "checkpoint_error" in out:
        print(f"checkpoint NOT made: {out['checkpoint_error']}")
    return 1 if out["n_failed"] else 0


def _describe_checkpoint(out: dict) -> str:
    text = (
        f"checkpoint: {out['files']} file(s) committed on {out['branch']}"
        if out["committed"]
        else f"checkpoint: nothing new to commit on {out['branch']}"
    )
    if out["pushed"]:
        text += ", pushed"
    elif out["push_error"]:
        text += f"; PUSH FAILED: {out['push_error']}"
    return text


def queue_main() -> None:
    raise SystemExit(_queue_main())


def _logbook_main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Add an entry to docs/logbook.md: what was done, what "
        "came out, what was concluded."
    )
    parser.add_argument("--logbook", default=str(DEFAULT_LOGBOOK))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="write an entry (replaces the sweep's stub)")
    what = add.add_mutually_exclusive_group(required=True)
    what.add_argument("--sweep", help="path to the sweep config the entry is about")
    what.add_argument("--name", help="entry name, for work that is not a sweep")
    add.add_argument("--did", required=True)
    add.add_argument("--got", required=True)
    add.add_argument("--concluded", required=True)
    add.add_argument("--next", dest="next_step", default="")
    add.add_argument("--note", help="path to the detailed note (docs/notes/...)")
    sub.add_parser("unread", help="list entries nobody has read yet")
    args = parser.parse_args(argv)
    try:
        if args.command == "unread":
            _, entries = _split_entries(Path(args.logbook).read_text())
            unread = [e.splitlines()[0][4:] for e in entries if STUB_MARK in e]
            print("\n".join(unread) if unread else "every entry has been read")
            return 0
        note = Path(args.note) if args.note else None
        if note and not note.exists():
            raise ConfigError(f"note {note} does not exist")
        if args.sweep:
            name, facts = sweep_facts(
                args.sweep, reports_dir=args.reports_dir,
                logbook=args.logbook, note=note,
            )
        else:
            name = args.name
            facts = _facts_line(
                n_runs=None, n_failed=0, dataset_version="", cells="",
                sha=git_sha(), summary=None, note=note,
                logbook=Path(args.logbook),
            )
        path = add_entry(
            name, did=args.did, got=args.got, concluded=args.concluded,
            next_step=args.next_step, facts=facts, logbook=args.logbook,
        )
    except Exception:
        traceback.print_exc()
        return 1
    print(f"logbook: entry for {name} written to {path}")
    return 0


def logbook_main() -> None:
    raise SystemExit(_logbook_main())
