"""End-to-end: a decision-tree experiment through the harness produces the
full Phase-2 report — era table, crash-era section, calibration plot,
baseline comparison, and checked-in rule/diagram artifacts."""

from harness.config import ExperimentConfig
from harness.runner import run_experiment


def _config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "test_tree_3y_beat_spy",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "decision_tree", "max_depth": 3},
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


def test_tree_run_produces_full_report_and_artifacts(data_root, tmp_path):
    reports = tmp_path / "reports"
    kwargs = dict(
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=reports,
    )
    # baselines first, so the comparison table has something to cite
    baseline = run_experiment(
        _config(name="test_majority_for_tree", model={"name": "majority_class"}),
        **kwargs,
    )
    assert baseline["status"] == "completed"

    summary = run_experiment(_config(), **kwargs)
    assert summary["status"] == "completed"
    assert summary["folds"] == [2016, 2017]

    report = (reports / "test_tree_3y_beat_spy.md").read_text()

    # era slicing: one row per test year plus a pooled row
    assert "Era-sliced metrics" in report
    assert "| 2016 |" in report and "| 2017 |" in report
    assert "| pooled |" in report

    # crash eras: fixture years contain none; the report must say so
    assert "Crash-era metrics" in report
    assert "untested by this run" in report

    # calibration plot exists and is referenced (tree scores are probabilistic)
    assert "Calibration" in report
    assert (reports / "test_tree_3y_beat_spy_calibration.png").exists()

    # baseline comparison cites the majority run
    assert "Baseline comparison" in report
    assert "test_majority_for_tree" in report

    # rule extraction + diagram, one rules section per fold
    rules = (reports / "test_tree_3y_beat_spy_rules.md").read_text()
    assert "## Fold 2016" in rules and "## Fold 2017" in rules
    assert "P(positive)" in rules
    assert "dataset_v0.0-test" in rules  # reproducibility header
    assert (reports / "test_tree_3y_beat_spy_tree.png").exists()
    assert "Interpretability artifacts" in report


def test_report_without_baselines_flags_it(data_root, tmp_path):
    reports = tmp_path / "reports"
    summary = run_experiment(
        _config(),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=reports,
    )
    assert summary["status"] == "completed"
    report = (reports / "test_tree_3y_beat_spy.md").read_text()
    assert "No baseline runs recorded" in report
