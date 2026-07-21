"""Re-evaluate a saved model bundle under an evaluation config.

Training and evaluation are distinct tasks: `vml-run` fits the per-fold
models and saves them as a bundle; `vml-eval` re-scores that bundle with
different metric parameters (top-K, score thresholds) without refitting.
What gets evaluated stays pinned by the bundle — dataset version, scheme,
folds, label, feature columns — so changing evaluation criteria can never
silently change the test rows, and each fold's model is only applied to
its own fold's test set.

An evaluation is itself a run: it appends to the results store under its
own config hash (the train config with the eval's metric parameters
merged in), so threshold shopping counts in the trial ledger like any
other configuration tried. Splits are applied with STANDARD access — a
bundle trained on the sealed holdout is structurally refused here.
"""

from __future__ import annotations

import traceback
from dataclasses import replace
from pathlib import Path

import pandas as pd

from eval.era import collect_predictions
from eval.metrics import compute_all
from harness.config import EvalConfig
from harness.dataset import Dataset, SplitAccess
from harness.errors import DatasetValidationError
from harness.model_store import ModelBundle
from harness.results import ResultsStore, git_sha, new_run_id
from harness.runner import (
    DEFAULT_DATA_ROOT,
    DEFAULT_REPORTS,
    DEFAULT_RESULTS,
    finalize_run,
)


def evaluate_bundle(
    bundle_dir: str | Path,
    eval_config: EvalConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    eval_config_path: str = "",
) -> dict:
    """Score a saved bundle's folds under `eval_config`'s metric
    parameters. Returns a summary dict; raises after logging on failure."""
    bundle = ModelBundle.load(bundle_dir)
    train_config = bundle.train_config
    # the eval run's identity: the pinned train config with the eval's
    # metric parameters merged in — a distinct config hash per (bundle,
    # eval criteria), counted by the trial ledger
    config = replace(
        train_config,
        name=f"{train_config.name}__{eval_config.name}",
        top_k=eval_config.top_k,
        score_thresholds=eval_config.score_thresholds,
    )

    store = ResultsStore(results_path)
    run_id = new_run_id()
    sha = git_sha()
    base_row = {
        "run_id": run_id,
        "experiment": config.name,
        "config_hash": config.config_hash,
        "config_path": eval_config_path,
        "dataset_version": config.dataset_version,
        "git_sha": sha,
        "seed": config.seed,
        "scheme": config.scheme,
        "horizon_years": config.horizon_years,
        "label": config.label,
        "model": config.model_name,
    }

    try:
        # Loaded from the directory the bundle was trained on
        # (train_config.dataset_version is the `dataset_vX.Y` directory
        # name); the manifest's own dataset_version field is a separate
        # build-identity string ("X.Y") and is not expected to match it.
        dataset = Dataset(Path(data_root) / train_config.dataset_version)
        missing = sorted(
            set(bundle.feature_columns) - set(dataset.data.columns)
        )
        if missing:
            raise DatasetValidationError(
                f"bundle feature columns absent from dataset: {missing}"
            )

        fold_results: list[dict] = []
        prediction_frames: list[pd.DataFrame] = []
        for fold in bundle.folds:
            split = dataset.apply_split(
                config.scheme, fold, config.horizon_years,
                access=SplitAccess.STANDARD,
            )
            test_fit = dataset.fit_data(
                split.test, config.label, bundle.feature_columns,
                config.horizon_years,
            )
            model = bundle.fold_models[fold]
            scores = model.predict_scores(test_fit.X)
            metrics = compute_all(
                test_fit.y,
                scores,
                sample_weight=test_fit.sample_weight,
                top_k=config.top_k,
                score_thresholds=config.score_thresholds,
                probabilistic=bundle.probabilistic,
            )
            stats = bundle.fold_train_stats[fold]
            fold_results.append(
                {
                    "fold": fold,
                    "n_train_rows": stats["n_train_rows"],
                    "effective_train_size": stats["effective_train_size"],
                    "n_test_rows": len(test_fit.X),
                    "metrics": metrics,
                }
            )
            test_years = pd.to_datetime(
                split.test.loc[test_fit.X.index, "snapshot_date"]
            ).dt.year.to_numpy()
            prediction_frames.append(
                collect_predictions(
                    fold, test_years, test_fit.y, scores, test_fit.sample_weight
                )
            )
            store.append(
                {
                    **base_row,
                    "status": "completed",
                    "fold": fold,
                    "n_train_rows": stats["n_train_rows"],
                    "effective_train_size": (
                        f"{stats['effective_train_size']:.4f}"
                    ),
                    "n_test_rows": len(test_fit.X),
                    "metrics_json": metrics,
                }
            )

        report_path, configurations_tried = finalize_run(
            config=config,
            run_id=run_id,
            sha=sha,
            dataset=dataset,
            store=store,
            fold_results=fold_results,
            prediction_frames=prediction_frames,
            probabilistic=bundle.probabilistic,
            reports_dir=reports_dir,
            artifacts={"source_bundle": Path(bundle_dir)},
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "folds": bundle.folds,
            "fold_results": fold_results,
            "configurations_tried": configurations_tried,
            "report_path": report_path,
            "source_bundle": Path(bundle_dir),
            "train_run_id": bundle.run_id,
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


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate a saved model bundle under an eval config "
        "(metric parameters only; no refitting)."
    )
    parser.add_argument(
        "bundle", help="path to a saved bundle directory (experiments/models/...)"
    )
    parser.add_argument(
        "eval_config", help="path to an eval-config TOML (name, top_k, "
        "score_thresholds)"
    )
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    args = parser.parse_args(argv)
    try:
        summary = evaluate_bundle(
            args.bundle,
            EvalConfig.from_file(args.eval_config),
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
            eval_config_path=str(args.eval_config),
        )
    except Exception:
        traceback.print_exc()
        print("evaluation FAILED (logged to the results store)")
        return 1
    print(
        f"evaluation {summary['run_id']} completed over folds "
        f"{summary['folds']} (train run {summary['train_run_id']})"
    )
    print(f"report: {summary['report_path']}")
    return 0


def main() -> None:
    import sys

    sys.exit(_main())
