"""Model bundles and separate evaluation: a training run saves its fitted
fold models; vml-eval re-scores them under new metric parameters without
refitting, logging the evaluation as a run of its own."""

import json

import pytest

from harness.config import EvalConfig, ExperimentConfig
from harness.errors import ConfigError
from harness.evaluate import evaluate_bundle
from harness.model_store import ModelBundle, ModelBundleError
from harness.results import ResultsStore
from harness.runner import run_experiment


def _train_config(**overrides) -> ExperimentConfig:
    raw = {
        "name": "test_tree_3y_beat_spy",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "walkforward",
        "horizon_years": 3,
        "label": "label_3y_beat_spy",
        "feature_groups": ["features", "ranks"],
        "seed": 7,
        "top_k": [5],
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return ExperimentConfig.from_dict(raw)


@pytest.fixture()
def trained(data_root, tmp_path):
    """One completed training run with a saved bundle."""
    paths = {
        "data_root": data_root,
        "results": tmp_path / "results.csv",
        "reports": tmp_path / "reports",
        "models": tmp_path / "models",
    }
    summary = run_experiment(
        _train_config(),
        data_root=data_root,
        results_path=paths["results"],
        reports_dir=paths["reports"],
        models_dir=paths["models"],
        discrimination_curves=True,
    )
    return summary, paths


def test_run_saves_loadable_bundle(trained):
    summary, _ = trained
    bundle_dir = summary["model_bundle"]
    assert bundle_dir is not None and bundle_dir.is_dir()
    assert (bundle_dir / "bundle.json").exists()
    assert (bundle_dir / "fold_models.pkl").exists()

    bundle = ModelBundle.load(bundle_dir)
    assert bundle.folds == summary["folds"] == [2016, 2017]
    assert bundle.run_id == summary["run_id"]
    assert bundle.probabilistic is True
    # the embedded config round-trips to the exact training identity
    assert bundle.train_config == _train_config()
    for fold in bundle.folds:
        assert bundle.fold_train_stats[fold]["n_train_rows"] > 0


def test_no_models_dir_means_no_bundle(data_root, tmp_path):
    summary = run_experiment(
        _train_config(name="test_tree_nosave"),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["model_bundle"] is None


def test_evaluate_bundle_with_new_criteria(trained):
    summary, paths = trained
    eval_cfg = EvalConfig.from_dict(
        {"name": "thr", "top_k": [3], "score_thresholds": [0.5, 0.99]}
    )
    eval_summary = evaluate_bundle(
        summary["model_bundle"],
        eval_cfg,
        data_root=paths["data_root"],
        results_path=paths["results"],
        reports_dir=paths["reports"],
    )
    assert eval_summary["status"] == "completed"
    assert eval_summary["folds"] == summary["folds"]
    assert eval_summary["train_run_id"] == summary["run_id"]

    store = ResultsStore(paths["results"]).load()
    train_rows = store[store["run_id"] == summary["run_id"]]
    eval_rows = store[store["run_id"] == eval_summary["run_id"]]
    assert len(eval_rows) == len(train_rows) == 2
    assert (eval_rows["experiment"] == "test_tree_3y_beat_spy__thr").all()
    # a new evaluation criterion is a new configuration in the ledger
    assert (
        eval_rows.iloc[0]["config_hash"] != train_rows.iloc[0]["config_hash"]
    )
    assert eval_summary["configurations_tried"] == 2

    for (_, tr), (_, ev) in zip(train_rows.iterrows(), eval_rows.iterrows()):
        tm, em = json.loads(tr["metrics_json"]), json.loads(ev["metrics_json"])
        # same saved model on the same fold's test rows: ranking metrics
        # are identical, only the requested metric parameters differ
        assert em["pr_auc"] == tm["pr_auc"]
        assert em["n_test"] == tm["n_test"]
        assert "precision_at_3" in em and "precision_at_3" not in tm
        assert "precision_at_thr_0.5" in em and "n_at_thr_0.99" in em

    report = (paths["reports"] / "test_tree_3y_beat_spy__thr.md").read_text()
    assert "re-evaluation of saved bundle" in report
    assert "precision_at_thr_0.5" in report
    assert "split_folds.parquet" in report


def test_training_run_draws_curves_on_opt_in(trained):
    summary, paths = trained
    reports = paths["reports"]
    # calibration is always drawn (tree is probabilistic); PR and ROC
    # were opted in by the fixture via discrimination_curves=True
    for suffix in ("_pr_curve.png", "_roc_curve.png", "_calibration.png"):
        assert (reports / f"test_tree_3y_beat_spy{suffix}").exists()
    report = (reports / "test_tree_3y_beat_spy.md").read_text()
    assert "Discrimination curves" in report
    assert "![PR curve]" in report and "![ROC curve]" in report


def test_discrimination_curves_are_opt_in(data_root, tmp_path):
    reports = tmp_path / "reports"
    run_experiment(
        _train_config(),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=reports,
    )
    # by default only the calibration figure is drawn
    assert (reports / "test_tree_3y_beat_spy_calibration.png").exists()
    for suffix in ("_pr_curve.png", "_roc_curve.png"):
        assert not (reports / f"test_tree_3y_beat_spy{suffix}").exists()
    report = (reports / "test_tree_3y_beat_spy.md").read_text()
    assert "![PR curve]" not in report and "![ROC curve]" not in report


def test_reeval_does_not_redraw_score_figures(trained):
    summary, paths = trained
    reports = paths["reports"]
    evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict({"name": "thr", "score_thresholds": [0.5]}),
        data_root=paths["data_root"],
        results_path=paths["results"],
        reports_dir=reports,
    )
    stem = "test_tree_3y_beat_spy__thr"
    # score-only figures are the training run's; none are drawn for the eval
    for suffix in ("_pr_curve.png", "_roc_curve.png", "_calibration.png"):
        assert not (reports / f"{stem}{suffix}").exists()
    report = (reports / f"{stem}.md").read_text()
    assert "Not redrawn for this evaluation" in report
    assert "![PR curve]" not in report and "![calibration curve]" not in report


def test_evaluated_holdout_bundle_is_refused(trained, tmp_path):
    # a bundle whose train config points at the sealed scheme cannot be
    # re-scored here: split access stays STANDARD
    from harness.errors import HoldoutAccessError

    summary, paths = trained
    bundle_dir = summary["model_bundle"]
    meta_path = bundle_dir / "bundle.json"
    meta = json.loads(meta_path.read_text())
    meta["train_config"]["scheme"] = "holdout"
    cfg = ExperimentConfig.from_dict(meta["train_config"])
    meta["config_hash"] = cfg.config_hash
    meta_path.write_text(json.dumps(meta))
    with pytest.raises(HoldoutAccessError):
        evaluate_bundle(
            bundle_dir,
            EvalConfig.from_dict({"name": "grab"}),
            data_root=paths["data_root"],
            results_path=tmp_path / "r.csv",
            reports_dir=tmp_path / "reports",
        )
    # the refusal is logged like any failed run
    store = ResultsStore(tmp_path / "r.csv").load()
    assert store.iloc[0]["status"] == "failed"


def test_evaluate_tolerates_version_naming_convention(trained):
    # regression: the bundle pins the directory name `dataset_v0.0-test`
    # while the manifest's dataset_version field is the bare `0.0-test`;
    # evaluation must not treat that expected mismatch as an error
    summary, paths = trained
    from harness.dataset import Dataset

    assert Dataset(paths["data_root"] / "dataset_v0.0-test").version == "0.0-test"
    eval_summary = evaluate_bundle(
        summary["model_bundle"],
        EvalConfig.from_dict({"name": "conv"}),
        data_root=paths["data_root"],
        results_path=paths["results"],
        reports_dir=paths["reports"],
    )
    assert eval_summary["status"] == "completed"


def test_eval_config_rejects_pinned_fields():
    with pytest.raises(ConfigError, match="pinned by the model bundle"):
        EvalConfig.from_dict({"name": "x", "label": "label_3y_beat_spy"})
    with pytest.raises(ConfigError, match="lacks a name"):
        EvalConfig.from_dict({"top_k": [5]})


def test_bundle_refuses_tampered_metadata(trained, tmp_path):
    summary, _ = trained
    bundle_dir = summary["model_bundle"]
    meta_path = bundle_dir / "bundle.json"
    meta = json.loads(meta_path.read_text())
    meta["train_config"]["seed"] = 999
    meta_path.write_text(json.dumps(meta))
    with pytest.raises(ModelBundleError, match="edited or is corrupt"):
        ModelBundle.load(bundle_dir)


def test_load_refuses_non_bundle(tmp_path):
    with pytest.raises(ModelBundleError, match="not a model bundle"):
        ModelBundle.load(tmp_path)


def test_blend_scores_is_mean_rank_within_period():
    import numpy as np

    from harness.evaluate import blend_scores

    a = [0.9, 0.1, 0.5, 0.2, 0.8]
    b = [1.0, 3.0, float("nan"), 5.0, 4.0]
    periods = [1, 1, 1, 2, 2]
    out = blend_scores([a, b], periods)
    # period 1: a ranks 3,1,2 of 3; b ranks 1,2 of 2 (the NaN is skipped)
    assert out[0] == pytest.approx((3 / 3 + 1 / 2) / 2)
    assert out[1] == pytest.approx((1 / 3 + 2 / 2) / 2)
    assert out[2] == pytest.approx(2 / 3)  # ranked on model a alone
    # period 2 is ranked on its own rows
    assert out[3] == pytest.approx((1 / 2 + 2 / 2) / 2)
    assert out[4] == pytest.approx((2 / 2 + 1 / 2) / 2)
    # ties share the better rank; -inf ranks last
    tied = blend_scores([[0.5, 0.5, float("-inf")]], [1, 1, 1])
    assert tied.tolist() == pytest.approx([1.0, 1.0, 1 / 3])


def test_blend_scores_worst_rank():
    from harness.evaluate import blend_scores

    a = [0.1, 0.9, 0.8, 0.5]
    b = [0.9, 0.1, 0.8, 0.5]
    out = blend_scores([a, b], [1, 1, 1, 1], mode="worst_rank")
    # shares a: .25,1,.75,.5  b: 1,.25,.75,.5 -> worst .25,.25,.75,.5
    assert out[2] > out[3] > out[0]
    assert out[0] == pytest.approx(0.25, abs=1e-5)
    assert out[2] == pytest.approx(0.75, abs=1e-5)
    # mean rank orders the same rows differently
    mean = blend_scores([a, b], [1, 1, 1, 1])
    assert mean[0] > mean[3]
    with pytest.raises(Exception, match="unknown blend mode"):
        blend_scores([a], [1, 1, 1, 1], mode="max")


def test_blend_combine_parsing():
    from harness.config import EvalConfig
    from harness.errors import ConfigError

    cfg = EvalConfig.from_dict(
        {"name": "w", "blend": ["x"], "blend_combine": "worst_rank"}
    )
    assert cfg.blend_combine == "worst_rank"
    assert EvalConfig.from_dict({"name": "m", "blend": ["x"]}).blend_combine == "mean_rank"
    with pytest.raises(ConfigError, match="without a blend"):
        EvalConfig.from_dict({"name": "n", "blend_combine": "worst_rank"})
    with pytest.raises(ConfigError, match="not in"):
        EvalConfig.from_dict({"name": "n", "blend": ["x"], "blend_combine": "min"})


def test_blended_evaluation_is_its_own_configuration(
    data_root, wf_bundle_dir, tmp_path
):
    from harness.config import EvalConfig, ExperimentConfig
    from harness.errors import ConfigError
    from harness.evaluate import evaluate_bundle
    from harness.results import ResultsStore
    from harness.runner import run_experiment

    factor = run_experiment(
        ExperimentConfig.from_dict(
            {
                "name": "factor_b2m",
                "dataset_version": "dataset_v0.0-test",
                "scheme": "walkforward",
                "label": "label_3y_beat_spy",
                "feature_groups": ["ranks"],
                "top_k": [5],
                "model": {"name": "rank_factor",
                          "rank_column": "book_to_market_rank"},
            }
        ),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    kwargs = dict(
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    plain = evaluate_bundle(
        wf_bundle_dir, EvalConfig.from_dict({"name": "plain", "top_k": [5]}),
        **kwargs,
    )
    blended = evaluate_bundle(
        wf_bundle_dir,
        EvalConfig.from_dict(
            {"name": "blend", "top_k": [5],
             "blend": [str(factor["model_bundle"])]}
        ),
        **kwargs,
    )
    rows = ResultsStore(tmp_path / "results.csv").load()
    hashes = {
        name: set(rows[rows["run_id"] == s["run_id"]]["config_hash"])
        for name, s in (("plain", plain), ("blend", blended))
    }
    assert hashes["plain"] != hashes["blend"]
    report = blended["report_path"].read_text()
    assert "**blend**" in report and "factor_b2m" in report
    # a ranking: no Brier in a blended evaluation
    assert all(
        "brier" not in fr["metrics"] or fr["metrics"]["brier"] != fr["metrics"]["brier"]
        for fr in blended["fold_results"]
    )
    worst = evaluate_bundle(
        wf_bundle_dir,
        EvalConfig.from_dict(
            {"name": "blend", "top_k": [5],
             "blend": [str(factor["model_bundle"])],
             "blend_combine": "worst_rank"}
        ),
        **kwargs,
    )
    rows = ResultsStore(tmp_path / "results.csv").load()
    worst_hashes = set(rows[rows["run_id"] == worst["run_id"]]["config_hash"])
    # the combination is part of the configuration's identity
    assert worst_hashes.isdisjoint(hashes["blend"])
    assert 'combine = "worst_rank"' in worst["report_path"].read_text()
    with pytest.raises(ConfigError, match="is the evaluated bundle"):
        evaluate_bundle(
            wf_bundle_dir,
            EvalConfig.from_dict({"name": "self", "blend": [str(wf_bundle_dir)]}),
            **kwargs,
        )


def test_gate_mask_and_apply():
    import numpy as np

    from harness.evaluate import apply_gates, gate_mask

    g = [0.1, 0.9, 0.5, 0.3, float("nan"), 0.7]
    periods = [1, 1, 1, 1, 2, 2]
    top = gate_mask(g, periods, "top", 0.5)
    assert top.tolist() == [False, True, True, False, False, True]
    bottom = gate_mask(g, periods, "bottom", 0.5)
    # a period with one scored row: that row is its top and its bottom half
    assert bottom.tolist() == [True, False, False, True, False, True]
    s = apply_gates([5.0, 1.0, 3.0, 4.0, 2.0, 0.0], [top])
    kept = s[top]
    assert kept.tolist() == [1.0, 3.0, 0.0]
    # every gated row ranks below every kept row, in its own order
    assert s[~top].max() < kept.min()
    assert np.argsort(s[~top]).tolist() == np.argsort([5.0, 4.0, 2.0]).tolist()
    assert apply_gates([1.0, 2.0], []).tolist() == [1.0, 2.0]


def test_gate_parsing():
    from harness.config import EvalConfig
    from harness.errors import ConfigError

    cfg = EvalConfig.from_dict(
        {"name": "g", "gate": [{"bundle": "x", "keep": "bottom", "share": 0.7}]}
    )
    assert cfg.gate[0].keep == "bottom" and cfg.gate[0].share == 0.7
    for bad in (
        {"bundle": "x", "keep": "middle"},
        {"bundle": "x", "share": 1.5},
        {"keep": "top"},
        {"bundle": "x", "extra": 1},
    ):
        with pytest.raises(ConfigError):
            EvalConfig.from_dict({"name": "g", "gate": [bad]})


def test_gated_evaluation_end_to_end(data_root, wf_bundle_dir, tmp_path):
    from harness.config import EvalConfig, ExperimentConfig
    from harness.evaluate import evaluate_bundle
    from harness.results import ResultsStore
    from harness.runner import run_experiment

    factor = run_experiment(
        ExperimentConfig.from_dict(
            {
                "name": "factor_gate",
                "dataset_version": "dataset_v0.0-test",
                "scheme": "walkforward",
                "label": "label_3y_beat_spy",
                "feature_groups": ["ranks"],
                "top_k": [5],
                "model": {"name": "rank_factor",
                          "rank_column": "book_to_market_rank"},
            }
        ),
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        models_dir=tmp_path / "models",
    )
    kwargs = dict(
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    plain = evaluate_bundle(
        wf_bundle_dir, EvalConfig.from_dict({"name": "plain", "top_k": [5]}),
        **kwargs,
    )
    gated = evaluate_bundle(
        wf_bundle_dir,
        EvalConfig.from_dict(
            {"name": "gated", "top_k": [5],
             "gate": [{"bundle": str(factor["model_bundle"]),
                       "keep": "top", "share": 0.5}]}
        ),
        **kwargs,
    )
    rows = ResultsStore(tmp_path / "results.csv").load()
    h = lambda s: set(rows[rows["run_id"] == s["run_id"]]["config_hash"])
    assert h(plain).isdisjoint(h(gated))
    report = gated["report_path"].read_text()
    assert "**gate**" in report and "factor_gate" in report
