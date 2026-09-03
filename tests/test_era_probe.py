"""Era-identifiability probe (registered diagnostic): runs end to end on
the miniature dataset under the diagnostic schemes, refuses everything
else, logs under the pseudo-label, and its metrics are what they say.

The fixture's features are iid noise, so the probe is expected to sit at
chance here — the tests assert structure, never skill."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from diagnostics import era_metrics as em  # noqa: E402
from diagnostics.era_probe import (  # noqa: E402
    SNAPSHOT_YEAR_LABEL,
    EraProbeConfig,
    require_numeric_features,
    run_era_probe,
    snapshot_year,
)
from diagnostics.probe_models import build_probe_model  # noqa: E402
from explain.rules import extract_leaf_rules_multiclass  # noqa: E402
from harness.config import ExperimentConfig  # noqa: E402
from harness.dataset import Dataset, SplitAccess  # noqa: E402
from harness.errors import (  # noqa: E402
    ConfigError,
    DiagnosticSchemeError,
    MissingSampleWeightError,
)
from harness.results import ResultsStore  # noqa: E402
from run_diagnostic import main as diagnostic_main  # noqa: E402
from run_diagnostic import run_era_probe_command  # noqa: E402

TREE_CONFIG = """
diagnostic = "era_probe"
name = "probe_tree_test"
dataset_version = "dataset_v0.0-test"
scheme = "entity_holdout"
horizon_years = 3
seed = 7
report_min_year = 2014

[features]
groups = ["features", "ranks"]

[model]
name = "decision_tree"
max_depth = 2
"""


def _raw(**overrides) -> dict:
    raw = {
        "diagnostic": "era_probe",
        "name": "probe_test",
        "dataset_version": "dataset_v0.0-test",
        "scheme": "entity_holdout",
        "horizon_years": 3,
        "feature_groups": ["ranks"],
        "seed": 7,
        "model": {"name": "decision_tree", "max_depth": 2},
    }
    raw.update(overrides)
    return raw


# ------------------------------------------------------------ end to end


def test_probe_runs_end_to_end_entity_holdout(data_root, tmp_path):
    config_path = tmp_path / "probe_tree_test.toml"
    config_path.write_text(TREE_CONFIG)
    results = tmp_path / "results.csv"
    reports = tmp_path / "reports"
    summary = run_era_probe_command(
        config_path, data_root=data_root, results_path=results, reports_dir=reports
    )
    assert summary["status"] == "completed"
    assert summary["folds"] == [0]

    store = ResultsStore(results).load()
    assert len(store) == 1
    row = store.iloc[0]
    assert row["status"] == "completed"
    assert row["scheme"] == "entity_holdout"
    assert row["label"] == SNAPSHOT_YEAR_LABEL
    assert row["model"] == "decision_tree"
    metrics = json.loads(row["metrics_json"])
    assert metrics["k_train"] == 8  # 2010–2017 pre-holdout
    assert metrics["baseline_chance_uniform"] == pytest.approx(1 / 8)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert metrics["n_test_years_unseen_in_train"] == 0
    assert "baseline_majority_accuracy" in metrics

    report = (reports / "probe_tree_test.md").read_text()
    assert "DIAGNOSTIC ONLY" in report
    assert "split_folds.parquet" in report
    assert "Effective sample size" in report
    assert "configurations tried" in report
    assert "| 2015 |" in report  # per-year slice
    assert "year ≥ 2014" in report  # post-burn-in block
    for suffix in ("_confusion.png", "_importance.png", "_rules.md", "_tree.png"):
        assert (reports / f"probe_tree_test{suffix}").exists(), suffix
    rules = (reports / "probe_tree_test_rules.md").read_text()
    assert "THEN year = 20" in rules
    assert "DIAGNOSTIC ONLY" in rules

    # a walk-forward cell's trial count is untouched by probe rows
    assert store["scheme"].eq("walkforward").sum() == 0


def test_probe_lightgbm_arm(data_root, tmp_path):
    pytest.importorskip("lightgbm")
    config = EraProbeConfig.from_dict(
        _raw(name="probe_lgbm_test",
             model={"name": "lightgbm", "n_estimators": 10})
    )
    summary = run_era_probe(
        config,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
        access=SplitAccess.REGISTERED_DIAGNOSTIC,
    )
    assert summary["status"] == "completed"
    assert summary["artifacts"]["importance_kind"] == "gain"
    assert "rules" not in summary["artifacts"]  # not a single tree


def test_probe_xgboost_arm_and_forest_knobs(data_root, tmp_path):
    pytest.importorskip("xgboost")
    config = EraProbeConfig.from_dict(
        _raw(name="probe_xgb_test",
             model={"name": "xgboost", "n_estimators": 10, "max_depth": 2,
                    "class_weight": "balanced"})
    )
    summary = run_era_probe(
        config, data_root=data_root, results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports", access=SplitAccess.REGISTERED_DIAGNOSTIC,
    )
    assert summary["status"] == "completed"
    assert summary["fold_results"][0]["metrics"]["k_train"] == 8
    forest = build_probe_model(
        "random_forest",
        {"n_estimators": 5, "max_samples": 0.5, "n_jobs": 1, "max_depth": 2},
        seed=0,
    )
    X = pd.DataFrame({"a": np.linspace(0, 1, 40)})
    y = np.repeat([2010, 2011, 2012, 2013], 10)
    forest.fit(X, y, sample_weight=np.ones(40))
    proba = forest.predict_proba(X)
    assert proba.shape == (40, 4)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0)
    with pytest.raises(ConfigError):
        build_probe_model("lightgbm", {"device": "tpu"}, seed=0)


def test_probe_random_kfold_is_flagged_leaky(data_root, tmp_path):
    config_path = tmp_path / "probe_kfold.toml"
    config_path.write_text(
        TREE_CONFIG.replace('scheme = "entity_holdout"', 'scheme = "random_kfold"')
        .replace("probe_tree_test", "probe_kfold_test")
    )
    summary = run_era_probe_command(
        config_path,
        data_root=data_root,
        results_path=tmp_path / "results.csv",
        reports_dir=tmp_path / "reports",
    )
    assert summary["status"] == "completed"
    report = Path(summary["report_path"]).read_text()
    assert "deliberately leaky" in report


def test_cli_main_runs_and_prints(data_root, tmp_path, capsys):
    config_path = tmp_path / "probe_tree_test.toml"
    config_path.write_text(TREE_CONFIG)
    rc = diagnostic_main(
        [
            "era-probe", str(config_path),
            "--data-root", str(data_root),
            "--results", str(tmp_path / "results.csv"),
            "--reports-dir", str(tmp_path / "reports"),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "DIAGNOSTIC ONLY" in out
    assert "majority-year" in out


# ------------------------------------------------------------ guardrails


def test_library_path_never_grants_access(data_root, tmp_path):
    config = EraProbeConfig.from_dict(_raw())
    results = tmp_path / "results.csv"
    with pytest.raises(DiagnosticSchemeError):
        run_era_probe(
            config, data_root=data_root, results_path=results,
            reports_dir=tmp_path / "reports",
        )  # default access is STANDARD
    store = ResultsStore(results).load()
    assert len(store) == 1
    assert store.iloc[0]["status"] == "failed"
    assert "DiagnosticSchemeError" in store.iloc[0]["error"]


@pytest.mark.parametrize("scheme", ["walkforward", "holdout"])
def test_config_refuses_non_diagnostic_schemes(scheme):
    with pytest.raises(DiagnosticSchemeError):
        EraProbeConfig.from_dict(_raw(scheme=scheme))


def test_config_requires_horizon_and_rejects_experiment_keys():
    raw = _raw()
    del raw["horizon_years"]
    with pytest.raises(ConfigError, match="horizon_years"):
        EraProbeConfig.from_dict(raw)
    with pytest.raises(ConfigError, match="label"):
        EraProbeConfig.from_dict(_raw(label="label_3y_beat_spy"))
    with pytest.raises(ConfigError, match="diagnostic"):
        EraProbeConfig.from_dict(_raw(diagnostic="leakage_gap"))
    with pytest.raises(ConfigError):
        EraProbeConfig.from_dict(_raw(model={"name": "majority_class"}))


def test_config_defaults_scheme_and_derives_name():
    raw = _raw()
    del raw["scheme"]
    del raw["name"]
    config = EraProbeConfig.from_dict(raw)
    assert config.scheme == "entity_holdout"
    assert config.name.startswith("era_probe_decision_tree_ranks_3y_")


def test_probe_hash_distinct_from_experiment_hash():
    raw = _raw()
    probe = EraProbeConfig.from_dict(raw)
    exp_raw = {k: v for k, v in raw.items() if k != "diagnostic"}
    exp_raw["label"] = "label_3y_beat_spy"
    experiment = ExperimentConfig.from_dict(exp_raw)
    assert probe.config_hash != experiment.config_hash
    assert probe.to_experiment_config().label == SNAPSHOT_YEAR_LABEL


def test_non_numeric_columns_refused():
    X = pd.DataFrame({"a": [1.0, 2.0], "s": ["x", "y"], "b": [True, False]})
    with pytest.raises(ConfigError, match=r"\['s'\].*exclude_columns"):
        require_numeric_features(X)
    require_numeric_features(X[["a", "b"]])  # bool is fine


def test_observable_fit_rows_shares_the_weight_guardrail(dataset_dir):
    ds = Dataset(dataset_dir)
    frame = ds.data.copy()
    rows, w = ds.observable_fit_rows(frame, 3)
    assert len(rows) == len(w)
    assert rows["delisted_in_window_3y"].notna().all()
    assert np.array_equal(snapshot_year(rows),
                          pd.to_datetime(rows["snapshot_date"]).dt.year)
    # a NULL weight on an observable row is refused, exactly as fit_data does
    idx = rows.index[0]
    frame.loc[idx, "sample_weight_3y"] = np.nan
    with pytest.raises(MissingSampleWeightError):
        ds.observable_fit_rows(frame, 3)


def test_probe_models_require_weights_and_handle_one_class():
    X = pd.DataFrame({"a": [0.1, 0.9, 0.5, np.nan]})
    model = build_probe_model("decision_tree", {"max_depth": 1}, seed=0)
    with pytest.raises(MissingSampleWeightError):
        model.fit(X, [2010, 2011, 2010, 2011])
    model.fit(X, [2010, 2010, 2010, 2010], sample_weight=np.ones(4))
    assert list(model.classes_) == [2010]
    proba = model.predict_proba(X)
    assert proba.shape == (4, 1) and (proba == 1).all()
    assert model.feature_importances().sum() == 0
    with pytest.raises(ConfigError):
        build_probe_model("decision_tree", {"max_depth": 1, "class_weight": 0.5},
                          seed=0)
    with pytest.raises(ConfigError):
        build_probe_model("decision_tree", {}, seed=0)  # max_depth mandatory


# --------------------------------------------------------------- metrics


def test_metrics_on_hand_arrays():
    y_train = np.array([2010, 2010, 2011, 2012, 2012, 2012])
    w_train = np.ones(6)
    y = np.array([2010, 2011, 2012, 2013])
    w = np.array([1.0, 1.0, 2.0, 1.0])
    classes = np.union1d(y_train, y)
    p_model = np.array([[.7, .2, .1], [.2, .5, .3], [.1, .1, .8], [.3, .3, .4]])
    p = em.align_proba(p_model, np.array([2010, 2011, 2012]), classes)
    assert p.shape == (4, 4)
    np.testing.assert_allclose(p.sum(axis=1), 1.0)
    assert (p[:, 3] == 0).all()  # 2013 never seen by the model
    with pytest.raises(ValueError):
        em.align_proba(p_model, np.array([2010, 2011, 2099]), classes)

    y_pred = em.predict_year(p, classes)
    assert list(y_pred) == [2010, 2011, 2012, 2012]
    assert em.weighted_accuracy(y, y_pred, w) == pytest.approx(4 / 5)
    assert em.within_one_year_accuracy(y, y_pred, w) == pytest.approx(1.0)
    assert em.weighted_mae_years(y, y_pred, w) == pytest.approx(1 / 5)
    assert 0.0 <= em.macro_f1(y, y_pred, classes, w) <= 1.0
    assert em.weighted_log_loss(y, p, classes, w) > 0

    b = em.baseline_metrics(y_train, w_train, y, w, classes)
    assert b["baseline_chance_uniform"] == pytest.approx(1 / 3)
    assert b["baseline_majority_year"] == 2012
    assert b["baseline_prior_expected_accuracy"] == pytest.approx(
        (2 / 6) ** 2 + (1 / 6) ** 2 + (3 / 6) ** 2
    )
    assert b["baseline_majority_accuracy"] == pytest.approx(2 / 5)

    h = em.headline_metrics(y, p, classes, w, y_train, w_train)
    assert h["k_train"] == 3 and h["k_test"] == 4
    assert h["n_test_years_unseen_in_train"] == 1

    table = em.per_year_table(y, y_pred, w, classes, np.unique(y_train))
    assert list(table["year"]) == [2010, 2011, 2012, 2013]
    assert not table.set_index("year").loc[2013, "in_train"]
    assert np.isnan(table.set_index("year").loc[2013, "precision"])
    assert table.set_index("year").loc[2013, "most_confused_with"] == 2012
    assert table["test_weight_share"].sum() == pytest.approx(1.0)

    cm = em.confusion_matrix_weighted(y, y_pred, classes, w)
    assert cm.to_numpy().sum() == pytest.approx(w.sum())
    assert cm.loc[2013, 2012] == 1.0

    assert em.min_year_slice(y, p, w, classes, 2012)["n_test"] == 2
    assert em.min_year_slice(y, p, w, classes, 2020) is None


def test_multiclass_rules_extraction():
    rng = np.random.default_rng(0)
    X = pd.DataFrame({"f": rng.normal(size=90)})
    y = np.where(X["f"] < -0.5, 2008, np.where(X["f"] < 0.5, 2009, 2010))
    clf = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
    rules = extract_leaf_rules_multiclass(clf, ["f"], target_name="year")
    assert rules  # purest first
    assert rules[0].purity >= rules[-1].purity
    assert all(0.0 <= r.purity <= 1.0 for r in rules)
    assert all(r.predicted_class in {"2008", "2009", "2010"} for r in rules)
    assert sum(r.weight_share for r in rules) == pytest.approx(1.0)
    assert "THEN year = " in rules[0].format()
