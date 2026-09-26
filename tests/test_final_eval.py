"""Final-eval script: the only path to the sealed holdout; one look per
cell (label, horizon, holdout window), further looks only with a
disclosed --reopen reason; results logged whether good or bad."""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from harness.errors import HarnessError  # noqa: E402
from harness.results import ResultsStore  # noqa: E402
from run_final_eval import (  # noqa: E402
    LEDGER_FIELDS,
    HoldoutAlreadyConsumedError,
    load_ledger,
    run_final_eval,
)

CONFIG = """
name = "final_tree_3y_beat_spy"
dataset_version = "dataset_v0.0-test"
scheme = "walkforward"
folds = "all"
horizon_years = 3
label = "label_3y_beat_spy"
feature_groups = ["ranks"]
seed = 7
top_k = [5]

[model]
name = "decision_tree"
max_depth = 2
"""


@pytest.fixture
def selected_config(tmp_path):
    path = tmp_path / "final_tree_3y_beat_spy.toml"
    path.write_text(CONFIG)
    return path


def _paths(tmp_path):
    return dict(
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports" / "final_eval",
        ledger_path=tmp_path / "reports" / "final_evals.csv",
    )


def test_final_eval_takes_the_walkforward_config_directly(
    data_root, tmp_path, selected_config
):
    """No copied *_holdout.toml: the selection config is evaluated on the
    holdout scheme in memory, under its own name; the first look seals."""
    kwargs = _paths(tmp_path)
    summary = run_final_eval(selected_config, data_root=data_root, **kwargs)
    assert summary["status"] == "completed"
    assert summary["folds"] == [2018]
    assert summary["look"] == 1 and summary["looks_in_cell"] == 1
    assert summary["holdout_window"] == "2018-"
    store = ResultsStore(kwargs["results_path"]).load()
    assert (store["scheme"] == "holdout").all()
    assert (store["experiment"] == "final_tree_3y_beat_spy").all()

    report = Path(summary["report_path"]).read_text()
    assert "split_folds.parquet" in report
    assert "holdout look 1 of 1 in this cell" in report
    assert "the sealed look" in report

    rows = load_ledger(kwargs["ledger_path"])
    assert len(rows) == 1
    assert rows[0]["holdout_window"] == "2018-" and rows[0]["look"] == "1"
    assert rows[0]["reopen_reason"] == "" and rows[0]["phase"] == ""


def test_second_look_refused_without_reopen(data_root, tmp_path, selected_config):
    kwargs = _paths(tmp_path)
    run_final_eval(selected_config, data_root=data_root, **kwargs)
    with pytest.raises(HoldoutAlreadyConsumedError, match="--reopen"):
        run_final_eval(selected_config, data_root=data_root, **kwargs)
    # a *different* model on the same cell is exactly the case the seal is for
    other = tmp_path / "other.toml"
    other.write_text(CONFIG.replace("max_depth = 2", "max_depth = 3")
                     .replace('name = "final_tree_3y_beat_spy"', 'name = "deeper"'))
    with pytest.raises(HoldoutAlreadyConsumedError, match="1 completed look"):
        run_final_eval(other, data_root=data_root, **kwargs)
    assert len(load_ledger(kwargs["ledger_path"])) == 1  # refusals log nothing


def test_reopen_runs_and_discloses_the_look_count(
    data_root, tmp_path, selected_config
):
    kwargs = _paths(tmp_path)
    run_final_eval(selected_config, data_root=data_root, **kwargs)
    other = tmp_path / "other.toml"
    other.write_text(CONFIG.replace("max_depth = 2", "max_depth = 3")
                     .replace('name = "final_tree_3y_beat_spy"', 'name = "deeper"'))
    summary = run_final_eval(
        other, reopen="new model family", data_root=data_root, **kwargs
    )
    assert summary["look"] == 2 and summary["looks_in_cell"] == 2
    report = Path(summary["report_path"]).read_text()
    assert "holdout look 2 of 2 in this cell" in report
    assert "re-opened: new model family" in report
    assert "final_tree_3y_beat_spy" in report  # the earlier look is listed
    rows = load_ledger(kwargs["ledger_path"])
    assert [r["look"] for r in rows] == ["1", "2"]
    assert rows[1]["reopen_reason"] == "new model family"
    # --reopen on an unconsumed cell is just a first look, no reason logged
    fresh = tmp_path / "fresh.toml"
    fresh.write_text(CONFIG.replace("label_3y_beat_spy", "label_3y_cagr_ge_8")
                     .replace('name = "final_tree_3y_beat_spy"', 'name = "fresh"'))
    s = run_final_eval(fresh, reopen="irrelevant", data_root=data_root, **kwargs)
    assert s["look"] == 1
    assert load_ledger(kwargs["ledger_path"])[-1]["reopen_reason"] == ""


def test_reopen_needs_a_reason(data_root, tmp_path, selected_config):
    kwargs = _paths(tmp_path)
    run_final_eval(selected_config, data_root=data_root, **kwargs)
    with pytest.raises(HarnessError, match="reason"):
        run_final_eval(selected_config, reopen="  ", data_root=data_root, **kwargs)


def test_final_eval_refuses_diagnostic_schemes(data_root, tmp_path):
    cfg = tmp_path / "cfg.toml"
    cfg.write_text(
        CONFIG.replace('scheme = "walkforward"', 'scheme = "entity_holdout"')
    )
    with pytest.raises(HarnessError, match="diagnostic"):
        run_final_eval(cfg, data_root=data_root, **_paths(tmp_path))
    assert not _paths(tmp_path)["ledger_path"].exists()


def test_failed_final_eval_is_logged_but_does_not_consume(
    data_root, tmp_path, selected_config
):
    kwargs = _paths(tmp_path)
    # same cell (same label), but the run fails before evaluating anything
    bad = tmp_path / "bad.toml"
    bad.write_text(
        CONFIG.replace(
            'feature_groups = ["ranks"]',
            'feature_groups = ["ranks"]\nfeature_columns = ["nonexistent_rank"]',
        )
    )
    with pytest.raises(Exception):
        run_final_eval(bad, data_root=data_root, **kwargs)
    ledger = kwargs["ledger_path"].read_text()
    assert "failed" in ledger
    # the failure did not consume the cell for the good config
    summary = run_final_eval(selected_config, data_root=data_root, **kwargs)
    assert summary["status"] == "completed" and summary["look"] == 1


def test_legacy_phase_ledger_is_migrated_and_counts_as_a_look(
    data_root, tmp_path, selected_config
):
    """A ledger written under the old `phase` header: its rows keep their
    column, match the cell on label + horizon (window unknown), and the
    file is rewritten under the new header on the next append."""
    kwargs = _paths(tmp_path)
    ledger = kwargs["ledger_path"]
    ledger.parent.mkdir(parents=True)
    with open(ledger, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "phase", "dataset_version", "horizon_years", "label", "experiment",
            "config_hash", "run_id", "git_sha", "logged_utc", "status"])
        w.writeheader()
        w.writerow({"phase": "ex13", "dataset_version": "dataset_v0.0-test",
                    "horizon_years": "3", "label": "label_3y_beat_spy",
                    "experiment": "experiment13", "config_hash": "h",
                    "run_id": "r13", "git_sha": "g",
                    "logged_utc": "2026-07-22T00:00:00+00:00",
                    "status": "completed"})
    with pytest.raises(HoldoutAlreadyConsumedError, match="legacy phase 'ex13'"):
        run_final_eval(selected_config, data_root=data_root, **kwargs)
    summary = run_final_eval(
        selected_config, reopen="first look under the new rule",
        data_root=data_root, **kwargs
    )
    assert summary["look"] == 2
    with open(ledger, newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == LEDGER_FIELDS
        rows = list(reader)
    assert rows[0]["phase"] == "ex13" and rows[0]["holdout_window"] == ""
    assert rows[1]["holdout_window"] == "2018-" and rows[1]["look"] == "2"
