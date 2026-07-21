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
