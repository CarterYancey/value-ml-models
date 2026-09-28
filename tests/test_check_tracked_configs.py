"""scripts/check_tracked_configs.py: what a branch may add to the
integration branches, and what --fix takes back out."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_tracked_configs.py"
spec = importlib.util.spec_from_file_location("check_tracked_configs", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def _git(*args):
    subprocess.run(["git", *args], check=True, capture_output=True)


def _write(path, text="x\n"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _git("init", "-q", "-b", "Claude")
    _git("config", "user.email", "t@example.com")
    _git("config", "user.name", "t")
    _write("experiments/example.toml")
    _git("add", "-A")
    _git("commit", "-q", "-m", "base")
    _git("checkout", "-q", "-b", "claude/lab")
    return tmp_path


def _commit_all():
    _git("add", "-A", "-f")
    _git("commit", "-q", "-m", "work")


def test_clean_branch_passes(repo, capsys):
    _write("docs/logbook.md")
    _write("experiments/queue.toml")
    _write("experiments/ledger/sandbox.csv")
    _commit_all()
    assert check.main(["--base", "Claude"]) == 0


def test_working_material_is_reported(repo, capsys):
    _write("experiments/sweeps/scratch.toml")
    _write("reports/sweeps/scratch/scratch_summary.md")
    _write("reports/promoted/kept/report.md")
    _commit_all()
    assert check.main(["--base", "Claude"]) == 1
    out = capsys.readouterr().out
    assert "experiments/sweeps/scratch.toml" in out
    assert "reports/sweeps/scratch/scratch_summary.md" in out
    assert "reports/promoted/kept" not in out
    # what the base already tracks is not this check's business
    assert "example.toml" not in out


def test_promoted_and_kept_configs_pass(repo):
    _write("experiments/sweeps/good.toml")
    _write("experiments/sweeps/good_run.toml")
    _write("experiments/sample.toml")
    _write(
        "reports/promoted/sweep_good/promoted.json",
        json.dumps({"config_path": "experiments/sweeps/good.toml"}),
    )
    _write(
        "reports/promoted/good_run/promoted.json",
        json.dumps({"config_path": "experiments/sweeps/good_run.toml#run__s1"}),
    )
    _write("experiments/KEEP", "# examples\nexperiments/sample.toml\n")
    _commit_all()
    assert check.main(["--base", "Claude"]) == 0


def test_fix_untracks_and_keeps_the_files(repo):
    _write("experiments/sweeps/scratch.toml")
    _write("reports/sweeps/scratch/scratch_summary.md")
    _commit_all()
    assert check.main(["--base", "Claude", "--fix"]) == 0
    _git("commit", "-q", "-m", "clean")
    assert Path("experiments/sweeps/scratch.toml").exists()
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True
    ).stdout.split()
    assert "experiments/sweeps/scratch.toml" not in tracked
    assert check.main(["--base", "Claude"]) == 0
