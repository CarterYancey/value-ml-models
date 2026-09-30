"""The run queue, the logbook and checkpoints (harness.lab): what an
unattended session leans on, so its failure modes are the tests."""

import subprocess

import pytest

from harness.errors import ConfigError
from harness.lab import (
    STUB_MARK,
    _split_entries,
    add_entry,
    checkpoint,
    checkpoint_paths,
    load_queue,
    next_item,
    queue_states,
    run_next,
)
from harness.results import ResultsStore

VERSION = "dataset_v0.0-test"

SWEEP = """
name = "{name}"
dataset_version = "dataset_v0.0-test"
scheme = "walkforward"
folds = "all"
feature_groups = ["ranks"]
seeds = [3]
top_k = [5]

[[cells]]
label = "label_3y_beat_spy"

[model]
name = "decision_tree"
min_weight_fraction_leaf = 0.02

[grid]
max_depth = [2, 3]
"""


@pytest.fixture()
def lab(tmp_path, monkeypatch):
    """A git repository with a two-item queue, on a claude/ branch."""
    monkeypatch.chdir(tmp_path)
    for args in (
        ["init", "-q", "-b", "main"],
        ["config", "user.email", "t@example.com"],
        ["config", "user.name", "t"],
        ["commit", "-q", "--allow-empty", "-m", "root"],
        ["checkout", "-q", "-b", "claude/lab-test"],
    ):
        subprocess.run(["git", *args], check=True)
    (tmp_path / ".gitignore").write_text("experiments/**/*.toml\nreports/**\n")
    sweeps = tmp_path / "experiments" / "sweeps"
    sweeps.mkdir(parents=True)
    for name in ("first", "second"):
        (sweeps / f"{name}.toml").write_text(SWEEP.format(name=name))
    (tmp_path / "experiments" / "queue.toml").write_text(
        '[[item]]\nconfig = "experiments/sweeps/first.toml"\nwhy = "a"\n\n'
        '[[item]]\nconfig = "experiments/sweeps/second.toml"\n'
    )
    return {
        "queue_path": "experiments/queue.toml",
        "results_path": "experiments/ledger/test.csv",
        "reports_dir": "reports",
        "logbook": "docs/logbook.md",
    }


def _log():
    return subprocess.run(
        ["git", "log", "--format=%s"], capture_output=True, text=True
    ).stdout.splitlines()


def _tracked():
    return subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True
    ).stdout.split()


def test_queue_runs_in_order_and_stops(lab, data_root):
    states = queue_states(lab["queue_path"], lab["reports_dir"])
    assert [s.state for s in states] == ["pending", "pending"]
    assert next_item(states).name == "first"

    out = run_next(data_root=data_root, **lab)
    assert out["ran"] == "first" and out["n_failed"] == 0
    assert out["remaining"] == 1
    states = queue_states(lab["queue_path"], lab["reports_dir"])
    assert [s.state for s in states] == ["done", "pending"]

    assert run_next(data_root=data_root, **lab)["ran"] == "second"
    assert run_next(data_root=data_root, **lab)["ran"] is None
    # each sweep ran once: 2 runs x 2 folds per sweep
    assert len(ResultsStore(lab["results_path"]).load()) == 8


def test_interrupted_item_is_resumed_not_repeated(lab, data_root, tmp_path):
    run_next(data_root=data_root, **lab)
    rows = len(ResultsStore(lab["results_path"]).load())
    record = sorted((tmp_path / "reports").rglob("*_result.json"))[0]
    record.unlink()
    states = queue_states(lab["queue_path"], lab["reports_dir"])
    assert states[0].state == "partial" and states[0].n_done == 1
    assert run_next(data_root=data_root, **lab)["ran"] == "first"
    assert len(ResultsStore(lab["results_path"]).load()) == rows + rows // 2


def test_run_writes_a_stub_and_a_checkpoint(lab, data_root):
    out = run_next(data_root=data_root, **lab)
    text = open(lab["logbook"]).read()
    assert "· first" in text and STUB_MARK in text
    assert "2 runs" in text and "[summary](" in text
    assert out["checkpoint"]["committed"]
    assert _log()[0].startswith("lab: first, 2 runs")
    tracked = _tracked()
    assert "experiments/ledger/test.csv" in tracked
    assert "docs/logbook.md" in tracked
    # ignored working material that a crash would take with it
    assert "experiments/sweeps/first.toml" in tracked
    assert "reports/sweeps/first/first_summary.csv" in tracked
    assert any(t.endswith("_result.json") for t in tracked)
    # per-run reports and figures stay out
    assert not any(t.endswith(".png") for t in tracked)
    assert not any(
        t.startswith("reports/") and t.endswith(".md")
        and "_summary" not in t for t in tracked
    )


def test_reading_an_entry_replaces_its_stub(lab, data_root):
    run_next(data_root=data_root, **lab)
    add_entry(
        "first", did="ran two depths", got="p@5 0.6 and 0.7",
        concluded="depth does not matter here", next_step="second",
        logbook=lab["logbook"],
    )
    _, entries = _split_entries(open(lab["logbook"]).read())
    assert len(entries) == 1
    assert STUB_MARK not in entries[0]
    assert "- **Concluded:** depth does not matter here" in entries[0]
    # the machine's facts line is kept
    assert "2 runs" in entries[0]


def test_entries_are_newest_first_and_never_dropped(tmp_path):
    book = tmp_path / "logbook.md"
    for name in ("a", "b"):
        add_entry(name, did="d", got="g", concluded="c", logbook=book, day="2026-01-01")
    add_entry("a", did="again", got="g2", concluded="c2", logbook=book, day="2026-01-02")
    _, entries = _split_entries(book.read_text())
    assert [e.splitlines()[0] for e in entries] == [
        "### 2026-01-02 · a", "### 2026-01-01 · b", "### 2026-01-01 · a",
    ]


def test_entry_needs_a_conclusion(tmp_path):
    with pytest.raises(ConfigError, match="concluded"):
        add_entry("a", did="d", got="g", logbook=tmp_path / "logbook.md")


def test_checkpoint_refuses_integration_branches(lab):
    subprocess.run(["git", "checkout", "-q", "main"], check=True)
    with pytest.raises(ConfigError, match="claude/"):
        checkpoint("x", **lab)


def test_checkpoint_with_nothing_new_commits_nothing(lab, data_root):
    run_next(data_root=data_root, **lab)
    n = len(_log())
    out = checkpoint("again", **lab)
    assert not out["committed"] and len(_log()) == n


def test_failed_push_is_reported_not_raised(lab, data_root):
    out = run_next(data_root=data_root, push=True, **lab)
    cp = out["checkpoint"]
    assert cp["committed"] and not cp["pushed"] and cp["push_error"]


def test_local_ledger_is_not_checkpointed(lab):
    paths = checkpoint_paths(
        **{**lab, "results_path": "experiments/results.csv"}
    )
    assert not any(p.name == "results.csv" for p in paths)


def test_queue_refuses_bad_files(tmp_path):
    q = tmp_path / "queue.toml"
    q.write_text('[[item]]\nwhy = "no config"\n')
    with pytest.raises(ConfigError, match="config"):
        load_queue(q)
    q.write_text('[[item]]\nconfig = "a.toml"\n[[item]]\nconfig = "a.toml"\n')
    with pytest.raises(ConfigError, match="twice"):
        load_queue(q)


def test_broken_config_stops_the_queue(lab, data_root, tmp_path):
    (tmp_path / "experiments/sweeps/first.toml").write_text("name = 1\n")
    states = queue_states(lab["queue_path"], lab["reports_dir"])
    assert states[0].state == "broken"
    with pytest.raises(ConfigError, match="do not load"):
        run_next(data_root=data_root, **lab)
