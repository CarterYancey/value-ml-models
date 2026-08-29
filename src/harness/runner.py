"""Experiment runner: executes one config, logs everything, writes a report.

Every run — completed or failed — appends to the results store with
dataset version, config hash, git SHA, and seed, so abandoned experiments
still count toward the trial ledger. The runner only ever requests
STANDARD split access: the sealed holdout and the diagnostic schemes are
structurally out of its reach.
"""

from __future__ import annotations

import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from eval.era import (
    collect_predictions,
    confidence_profile,
    crash_era_table,
    era_table,
    pooled_metrics,
)
from eval.metrics import compute_all, regression_diagnostics
from eval.plots import render_calibration_plot, render_pr_curve, render_roc_curve
from explain.rules import render_tree_diagram, rules_text
from harness.config import ExperimentConfig
from harness.dataset import Dataset, SplitAccess
from harness.model_store import ModelBundle
from harness.report import write_report
from harness.results import ResultsStore, git_sha, new_run_id
from models.registry import (
    BASELINE_MODELS,
    build_model,
    check_target_labels,
    model_target,
)

DEFAULT_DATA_ROOT = Path("data/datasets")
DEFAULT_RESULTS = Path("experiments/results.csv")
DEFAULT_REPORTS = Path("reports")
#: Where the CLI saves trained model bundles (git-ignored). Library
#: callers opt in via run_experiment(models_dir=...).
DEFAULT_MODELS = Path("experiments/models")


def run_experiment(
    config: ExperimentConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    config_path: str = "",
    access: SplitAccess = SplitAccess.STANDARD,
    models_dir: str | Path | None = None,
    discrimination_curves: bool = False,
) -> dict:
    """Run a config across its folds. Returns a summary dict; raises after
    logging on failure. With `models_dir` set, the fitted per-fold models
    are saved as a bundle for later re-evaluation (harness.evaluate)."""
    store = ResultsStore(results_path)
    run_id = new_run_id()
    sha = git_sha()
    base_row = {
        "run_id": run_id,
        "experiment": config.name,
        "config_hash": config.config_hash,
        "config_path": config_path,
        "dataset_version": config.dataset_version,
        "git_sha": sha,
        "seed": config.seed,
        "scheme": config.scheme,
        "horizon_years": config.horizon_years,
        # a continuous-target run is a trial against the binary cell it
        # is *measured* on — logging it under fwd_* would dilute the
        # per-cell configurations-tried accounting
        "label": config.eval_label or config.label,
        "model": config.model_name,
    }

    try:
        check_target_labels(config)
        target = model_target(config.model_name)
        # continuous-target runs rank by predicted return but are
        # *measured* against the binary eval_label cell
        eval_label = config.eval_label or config.label
        dataset = Dataset(Path(data_root) / config.dataset_version)
        config.check_dataset_version(dataset.version)
        feature_cols = config.resolve_feature_columns(dataset)
        folds = (
            dataset.folds(config.scheme, config.horizon_years)
            if config.folds == "all"
            else list(config.folds)
        )
        if not folds:
            raise ValueError(
                f"no folds for scheme={config.scheme!r} "
                f"horizon={config.horizon_years}"
            )

        fold_results: list[dict] = []
        prediction_frames: list[pd.DataFrame] = []
        fold_rules: list[tuple[int, str]] = []
        fold_models: dict[int, object] = {}
        fold_train_stats: dict[int, dict] = {}
        last_tree: tuple[int, DecisionTreeClassifier] | None = None
        probabilistic = False
        fold_importances: list[tuple[int, np.ndarray]] = []
        for fold in folds:
            split = dataset.apply_split(
                config.scheme, fold, config.horizon_years, access=access
            )
            fit = dataset.fit_data(
                split.train, config.label, feature_cols, config.horizon_years,
                target=target,
            )
            model = build_model(config.model_name, config.model_params, config.seed)
            model.fit(fit.X, fit.y, sample_weight=fit.sample_weight)

            test_fit = dataset.fit_data(
                split.test, eval_label, feature_cols, config.horizon_years
            )
            scores = model.predict_scores(test_fit.X)
            metrics = compute_all(
                test_fit.y,
                scores,
                sample_weight=test_fit.sample_weight,
                top_k=config.top_k,
                score_thresholds=config.score_thresholds,
                precision_targets=config.precision_targets,
                probabilistic=model.probabilistic,
            )
            outcome = None
            if target == "continuous":
                # the realized continuous label on the same test rows —
                # upstream guarantees it is observable exactly where the
                # binary eval label is
                outcome = split.test.loc[
                    test_fit.X.index, config.label
                ].to_numpy(dtype=float)
                metrics.update(
                    regression_diagnostics(
                        outcome,
                        scores,
                        top_k=config.top_k,
                        sample_weight=test_fit.sample_weight,
                    )
                )
            fr = {
                "fold": fold,
                "n_train_rows": len(fit.X),
                "effective_train_size": fit.effective_size,
                "n_test_rows": len(test_fit.X),
                "metrics": metrics,
            }
            fold_results.append(fr)
            probabilistic = model.probabilistic
            fold_models[fold] = model
            fold_train_stats[fold] = {
                "n_train_rows": len(fit.X),
                "effective_train_size": fit.effective_size,
            }
            # snapshot_date is a parquet DATE upstream (datetime.date
            # objects after read), not a pandas datetime — normalize first
            test_years = pd.to_datetime(
                split.test.loc[test_fit.X.index, "snapshot_date"]
            ).dt.year.to_numpy()
            prediction_frames.append(
                collect_predictions(
                    fold, test_years, test_fit.y, scores,
                    test_fit.sample_weight, outcome=outcome,
                )
            )
            estimator = getattr(model, "estimator_", None)
            if isinstance(estimator, DecisionTreeClassifier):
                fold_rules.append((fold, rules_text(estimator, feature_cols)))
                last_tree = (fold, estimator)
            imp_fn = getattr(model, "feature_importances", None)
            if imp_fn is not None:
                imp = imp_fn()
                if imp is not None:
                    fold_importances.append((fold, imp))
            store.append(
                {
                    **base_row,
                    "status": "completed",
                    "fold": fold,
                    "n_train_rows": len(fit.X),
                    "effective_train_size": f"{fit.effective_size:.4f}",
                    "n_test_rows": len(test_fit.X),
                    "metrics_json": metrics,
                }
            )

        artifacts: dict[str, Path] = {}
        reports_dir = Path(reports_dir)
        if fold_rules:
            artifacts["rules"] = _write_rules_file(
                reports_dir / f"{config.name}_rules.md",
                config, run_id, sha, dataset.version, fold_rules,
            )
        if last_tree is not None:
            diagram_fold, estimator = last_tree
            artifacts["tree_diagram"] = render_tree_diagram(
                estimator, feature_cols, reports_dir / f"{config.name}_tree.png"
            )
            artifacts["tree_diagram_fold"] = diagram_fold
        if fold_importances:
            artifacts["importances"] = _write_importances_file(
                reports_dir / f"{config.name}_importances.csv",
                feature_cols,
                fold_importances,
            )

        bundle_path = None
        if models_dir is not None:
            bundle_path = ModelBundle(
                train_config=config,
                run_id=run_id,
                git_sha=sha,
                probabilistic=probabilistic,
                feature_columns=tuple(feature_cols),
                fold_models=fold_models,
                fold_train_stats=fold_train_stats,
            ).save(models_dir)
            artifacts["model_bundle"] = bundle_path

        report_path, configurations_tried = finalize_run(
            config=config,
            run_id=run_id,
            sha=sha,
            dataset=dataset,
            store=store,
            fold_results=fold_results,
            prediction_frames=prediction_frames,
            probabilistic=probabilistic,
            reports_dir=reports_dir,
            artifacts=artifacts,
            discrimination_curves=discrimination_curves,
        )
        # pooled over all folds' test rows — context for the era slices,
        # and the single number a sweep can rank candidate configs by.
        # Ranking metrics pick per year: per-fold scores aren't comparable
        pooled = pd.concat(prediction_frames, ignore_index=True)
        pooled_block = pooled_metrics(
            pooled,
            top_k=config.top_k,
            score_thresholds=config.score_thresholds,
            precision_targets=config.precision_targets,
            probabilistic=probabilistic,
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "folds": folds,
            "fold_results": fold_results,
            "pooled_metrics": pooled_block,
            "configurations_tried": configurations_tried,
            "report_path": report_path,
            "model_bundle": bundle_path,
        }
    except Exception as exc:
        store.append(
            {
                **base_row,
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        raise


def finalize_run(
    *,
    config: ExperimentConfig,
    run_id: str,
    sha: str,
    dataset: Dataset,
    store: ResultsStore,
    fold_results: list[dict],
    prediction_frames: list[pd.DataFrame],
    probabilistic: bool,
    reports_dir: str | Path,
    artifacts: dict | None = None,
    render_score_figures: bool = True,
    discrimination_curves: bool = False,
) -> tuple[Path, int]:
    """Shared tail of a training run and a bundle re-evaluation: era
    tables, score-only figures, baseline comparison, report. Returns
    (report_path, configurations_tried).

    `render_score_figures=False` skips the score-only figures entirely:
    they depend on `(y_true, score)` alone, so a re-evaluation of a saved
    model would only redraw the training run's identical figures. The
    report then points back to that run instead.

    `discrimination_curves` opts in to the PR/ROC curve PNGs — the
    calibration curve is the figure that gets read, so it is the only one
    drawn by default.
    """
    cell_label = config.eval_label or config.label
    configurations_tried = store.configurations_tried(
        config.dataset_version, config.scheme, config.horizon_years, cell_label
    )
    reports_dir = Path(reports_dir)
    predictions = pd.concat(prediction_frames, ignore_index=True)
    era_df = era_table(
        predictions,
        top_k=config.top_k,
        score_thresholds=config.score_thresholds,
        precision_targets=config.precision_targets,
        probabilistic=probabilistic,
    )
    crash_df = crash_era_table(
        predictions,
        top_k=config.top_k,
        score_thresholds=config.score_thresholds,
        precision_targets=config.precision_targets,
        probabilistic=probabilistic,
    )
    confidence_df = confidence_profile(predictions, probabilistic=probabilistic)

    calibration_path = pr_curve_path = roc_curve_path = None
    if render_score_figures:
        y, s, w = (
            predictions["y_true"], predictions["score"],
            predictions["sample_weight"],
        )
        if discrimination_curves:
            pr_curve_path = render_pr_curve(
                y, s, w,
                path=reports_dir / f"{config.name}_pr_curve.png",
                title=f"{config.name} — precision–recall, pooled over folds",
            )
            roc_curve_path = render_roc_curve(
                y, s, w,
                path=reports_dir / f"{config.name}_roc_curve.png",
                title=f"{config.name} — ROC, pooled over folds",
            )
        if probabilistic:
            calibration_path = render_calibration_plot(
                y, s, w,
                path=reports_dir / f"{config.name}_calibration.png",
                title=f"{config.name} — test calibration, pooled over folds",
            )

    baseline_df = store.model_comparison(
        config.dataset_version,
        config.scheme,
        config.horizon_years,
        cell_label,
        BASELINE_MODELS,
    )

    report_path = write_report(
        path=reports_dir / f"{config.name}.md",
        config=config,
        run_id=run_id,
        git_sha=sha,
        dataset=dataset,
        fold_results=fold_results,
        configurations_tried=configurations_tried,
        era_df=era_df,
        crash_df=crash_df,
        confidence_df=confidence_df,
        baseline_df=baseline_df,
        calibration_path=calibration_path,
        pr_curve_path=pr_curve_path,
        roc_curve_path=roc_curve_path,
        score_figures_rendered=render_score_figures,
        artifacts=artifacts,
    )
    return report_path, configurations_tried


def _write_rules_file(
    path: Path,
    config: ExperimentConfig,
    run_id: str,
    sha: str,
    dataset_version: str,
    fold_rules: list[tuple[int, str]],
) -> Path:
    """Checked-in rule-extraction artifact: one section per fold's tree."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Extracted tree rules — {config.name}",
        "",
        f"- dataset version: `{dataset_version}`",
        f"- config hash: `{config.config_hash}` — run `{run_id}`, "
        f"git `{sha}`, seed {config.seed}",
        f"- label: `{config.label}` ({config.horizon_years}y, "
        f"scheme `{config.scheme}`)",
        "",
        "One tree per walk-forward fold (each refit on its expanding "
        "window). P(positive) is the leaf's weighted in-sample frequency — "
        "rank by it, don't read it as a calibrated forward probability.",
    ]
    for fold, text in fold_rules:
        lines += ["", f"## Fold {fold}", "", "```", text, "```"]
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_importances_file(
    path: Path,
    feature_cols: list[str],
    fold_importances: list[tuple[int, np.ndarray]],
) -> Path:
    """Per-fold feature importances (models that expose them), sorted by
    the cross-fold mean. Impurity/gain importances are known to flatter
    high-cardinality features and say nothing about direction — this is a
    triage artifact for importance-guided feature *subsets* (which then
    count as configurations tried like any other selection), not an
    explanation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"feature": feature_cols})
    for fold, imp in fold_importances:
        df[f"fold_{fold}"] = imp
    fold_cols = [c for c in df.columns if c.startswith("fold_")]
    df.insert(1, "mean_importance", df[fold_cols].mean(axis=1))
    df = df.sort_values(
        "mean_importance", ascending=False, kind="mergesort"
    ).reset_index(drop=True)
    df.to_csv(path, index=False)
    return path


def run_config_file(path: str | Path, **kwargs) -> dict:
    config = ExperimentConfig.from_file(path)
    return run_experiment(config, config_path=str(path), **kwargs)


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run one experiment config through the harness."
    )
    parser.add_argument("config", help="path to an experiments/*.toml config")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument(
        "--models-dir",
        default=str(DEFAULT_MODELS),
        help="where to save the trained model bundle for later vml-eval "
        "(pass --no-save-models to skip)",
    )
    parser.add_argument("--no-save-models", action="store_true")
    parser.add_argument(
        "--curves",
        action="store_true",
        help="also render the PR/ROC curve PNGs (calibration is always "
        "drawn for probabilistic models; the discrimination curves are "
        "opt-in)",
    )
    args = parser.parse_args(argv)
    try:
        summary = run_config_file(
            args.config,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
            models_dir=None if args.no_save_models else args.models_dir,
            discrimination_curves=args.curves,
        )
    except Exception:
        traceback.print_exc()
        print("run FAILED (logged to the results store)")
        return 1
    print(f"run {summary['run_id']} completed over folds {summary['folds']}")
    print(f"report: {summary['report_path']}")
    if summary.get("model_bundle"):
        print(f"model bundle: {summary['model_bundle']} "
              "(re-evaluate with vml-eval)")
    return 0
