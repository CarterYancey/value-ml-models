"""End-to-end runner tests on the miniature dataset: results are logged
(completed and failed), reports cite split_folds.parquet and effective
sample size, holdout configs are refused."""

import json

import pytest

from harness.config import ExperimentConfig
from harness.errors import DatasetValidationError, HoldoutAccessError
from harness.results import ResultsStore
from harness.runner import run_experiment


def _config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "test_majority_3y_beat_spy",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "majority_class"},
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


def test_run_logs_and_reports(data_root, tmp_path):
    results = tmp_path / "results.csv"
    reports = tmp_path / "reports"
    summary = run_experiment(
        _config(),
        data_root=data_root,
        results_path=results,
        reports_dir=reports,
    )
    assert summary["status"] == "completed"
    assert summary["folds"] == [2016, 2017]

    store = ResultsStore(results).load()
    assert len(store) == 2  # one row per fold
    assert set(store["status"]) == {"completed"}
    assert store["git_sha"].nunique() == 1
    assert (store["dataset_version"] == "dataset_v0.0-test").all()
    metrics = json.loads(store.iloc[0]["metrics_json"])
    assert "pr_auc" in metrics and "precision_at_5" in metrics

    report = (reports / "test_majority_3y_beat_spy.md").read_text()
    assert "split_folds.parquet" in report
    assert "Effective sample size" in report
    assert "configurations tried" in report
    assert "era-sliced" in report.lower()


def test_failed_run_is_logged_too(data_root, tmp_path):
    results = tmp_path / "results.csv"
    bad = _config(name="test_bad_label", label="label_3y_nonexistent")
    with pytest.raises(DatasetValidationError):
        run_experiment(
            bad,
            data_root=data_root,
            results_path=results,
            reports_dir=tmp_path / "reports",
        )
    store = ResultsStore(results).load()
    assert len(store) == 1
    assert store.iloc[0]["status"] == "failed"
    assert "DatasetValidationError" in store.iloc[0]["error"]


def test_runner_cannot_touch_holdout(data_root, tmp_path):
    cfg = _config(name="test_holdout_grab", scheme="holdout", folds=[2018])
    with pytest.raises(HoldoutAccessError):
        run_experiment(
            cfg,
            data_root=data_root,
            results_path=tmp_path / "results.csv",
            reports_dir=tmp_path / "reports",
        )
    # the refusal itself is logged
    store = ResultsStore(tmp_path / "results.csv").load()
    assert store.iloc[0]["status"] == "failed"


def test_configurations_tried_counts_distinct_hashes(data_root, tmp_path):
    results = tmp_path / "results.csv"
    kwargs = dict(
        data_root=data_root,
        results_path=results,
        reports_dir=tmp_path / "reports",
    )
    run_experiment(_config(), **kwargs)
    s2 = run_experiment(
        _config(
            name="test_b2m_3y_beat_spy",
            model={"name": "rank_factor", "rank_column": "book_to_market_rank"},
        ),
        **kwargs,
    )
    # two distinct configs against the same (dataset, scheme, horizon, label)
    assert s2["configurations_tried"] == 2


def test_rank_and_random_baselines_run(data_root, tmp_path):
    kwargs = dict(
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    for name, model in [
        (
            "test_ey_rank",
            {"name": "rank_factor", "rank_column": "earnings_yield_rank"},
        ),
        ("test_random", {"name": "random_ranking"}),
    ]:
        summary = run_experiment(_config(name=name, model=model), **kwargs)
        assert summary["status"] == "completed"
        for fr in summary["fold_results"]:
            assert fr["effective_train_size"] < fr["n_train_rows"]


@pytest.mark.parametrize("stop", [KeyboardInterrupt, RuntimeError])
def test_run_stopped_midway_logs_no_completed_rows(
    data_root, tmp_path, monkeypatch, stop
):
    """A run that stops after some folds (Ctrl-C, or an error in a later
    fold) is one failed trial: none of its finished folds may be logged
    as `completed`, or the ledger shows a complete run with fewer folds."""
    import harness.runner as runner

    real = runner.compute_all
    calls = {"n": 0}

    def stop_on_second_fold(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise stop("stopped")
        return real(*args, **kwargs)

    monkeypatch.setattr(runner, "compute_all", stop_on_second_fold)
    results = tmp_path / "results.csv"
    with pytest.raises(stop):
        run_experiment(
            _config(),
            data_root=data_root,
            results_path=results,
            reports_dir=tmp_path / "reports",
        )
    store = ResultsStore(results).load()
    assert list(store["status"]) == ["failed"]
    assert stop.__name__ in store.iloc[0]["error"]
    assert "stopped after 1 of" in store.iloc[0]["error"]
    # the stopped run is still a trial against its cell
    assert ResultsStore(results).configurations_tried(
        "dataset_v0.0-test", "walkforward", 3, "label_3y_beat_spy"
    ) == 1


def test_run_from_a_file_copies_the_file_beside_the_report(data_root, tmp_path):
    from harness.runner import run_config_file

    path = tmp_path / "exp.toml"
    text = (
        "# why this run exists\n"
        'name = "copied_cfg"\n'
        'dataset_version = "dataset_v0.0-test"\n'
        'scheme = "walkforward"\n'
        "horizon_years = 3\n"
        'label = "label_3y_beat_spy"\n'
        'feature_groups = ["ranks"]\n'
        "seed = 7\n"
        "top_k = [5]\n"
        "[model]\n"
        'name = "majority_class"\n'
    )
    path.write_text(text)
    reports = tmp_path / "reports"
    run_config_file(
        path, data_root=data_root, results_path=tmp_path / "results.csv",
        reports_dir=reports,
    )
    assert (reports / "copied_cfg_config.toml").read_text() == text
    record = json.loads((reports / "copied_cfg_config.json").read_text())
    assert record["config"]["label"] == "label_3y_beat_spy"
    assert record["feature_columns"]
