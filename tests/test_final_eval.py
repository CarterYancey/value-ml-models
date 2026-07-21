"""Final-eval script: the only path to the sealed holdout; one completed
evaluation per (phase, cell); results logged whether good or bad."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from harness.errors import HarnessError  # noqa: E402
from harness.results import ResultsStore  # noqa: E402
from run_final_eval import (  # noqa: E402
    HoldoutAlreadyConsumedError,
    run_final_eval,
)

CONFIG = """
name = "final_tree_3y_beat_spy"
dataset_version = "dataset_v0.0-test"
scheme = "holdout"
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
def holdout_config(tmp_path):
    path = tmp_path / "final_tree_3y_beat_spy.toml"
    path.write_text(CONFIG)
    return path


def _paths(tmp_path):
    return dict(
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports" / "final_eval",
        ledger_path=tmp_path / "reports" / "final_evals.csv",
    )


def test_final_eval_runs_holdout_once(data_root, tmp_path, holdout_config):
    kwargs = _paths(tmp_path)
    summary = run_final_eval(
        holdout_config, "phase1", data_root=data_root, **kwargs
    )
    assert summary["status"] == "completed"
    assert summary["folds"] == [2018]
    report = Path(summary["report_path"]).read_text()
    assert "split_folds.parquet" in report

    store = ResultsStore(kwargs["results_path"]).load()
    assert (store["scheme"] == "holdout").all()

    # a consumed holdout cannot be re-sealed
    with pytest.raises(HoldoutAlreadyConsumedError, match="re-sealed"):
        run_final_eval(holdout_config, "phase1", data_root=data_root, **kwargs)

    # a later phase gets its own single evaluation
    summary2 = run_final_eval(
        holdout_config, "phase2", data_root=data_root, **kwargs
    )
    assert summary2["status"] == "completed"


def test_final_eval_refuses_non_holdout_scheme(data_root, tmp_path):
    cfg = tmp_path / "cfg.toml"
    cfg.write_text(CONFIG.replace('scheme = "holdout"', 'scheme = "walkforward"'))
    with pytest.raises(HarnessError, match="holdout"):
        run_final_eval(cfg, "phase1", data_root=data_root, **_paths(tmp_path))


def test_failed_final_eval_is_logged_but_does_not_consume(
    data_root, tmp_path, holdout_config
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
        run_final_eval(bad, "phase1", data_root=data_root, **kwargs)
    ledger = kwargs["ledger_path"].read_text()
    assert "failed" in ledger
    # the failure did not consume the cell for the good config
    summary = run_final_eval(
        holdout_config, "phase1", data_root=data_root, **kwargs
    )
    assert summary["status"] == "completed"
