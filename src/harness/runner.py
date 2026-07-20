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

from eval.metrics import compute_all
from harness.config import ExperimentConfig
from harness.dataset import Dataset, SplitAccess
from harness.report import write_report
from harness.results import ResultsStore, git_sha, new_run_id
from models.registry import build_model

DEFAULT_DATA_ROOT = Path("data/datasets")
DEFAULT_RESULTS = Path("experiments/results.csv")
DEFAULT_REPORTS = Path("reports")


def run_experiment(
    config: ExperimentConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    config_path: str = "",
    access: SplitAccess = SplitAccess.STANDARD,
) -> dict:
    """Run a config across its folds. Returns a summary dict; raises after
    logging on failure."""
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
        "label": config.label,
        "model": config.model_name,
    }

    try:
        dataset = Dataset(Path(data_root) / config.dataset_version)
        feature_cols = dataset.feature_columns(
            config.feature_groups, config.feature_columns
        )
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
        for fold in folds:
            split = dataset.apply_split(
                config.scheme, fold, config.horizon_years, access=access
            )
            fit = dataset.fit_data(
                split.train, config.label, feature_cols, config.horizon_years
            )
            model = build_model(config.model_name, config.model_params, config.seed)
            model.fit(fit.X, fit.y, sample_weight=fit.sample_weight)

            test_fit = dataset.fit_data(
                split.test, config.label, feature_cols, config.horizon_years
            )
            scores = model.predict_scores(test_fit.X)
            metrics = compute_all(
                test_fit.y,
                scores,
                sample_weight=test_fit.sample_weight,
                top_k=config.top_k,
                probabilistic=model.probabilistic,
            )
            fr = {
                "fold": fold,
                "n_train_rows": len(fit.X),
                "effective_train_size": fit.effective_size,
                "n_test_rows": len(test_fit.X),
                "metrics": metrics,
            }
            fold_results.append(fr)
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

        configurations_tried = store.configurations_tried(
            config.dataset_version, config.scheme, config.horizon_years, config.label
        )
        report_path = write_report(
            path=Path(reports_dir) / f"{config.name}.md",
            config=config,
            run_id=run_id,
            git_sha=sha,
            dataset=dataset,
            fold_results=fold_results,
            configurations_tried=configurations_tried,
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "folds": folds,
            "fold_results": fold_results,
            "configurations_tried": configurations_tried,
            "report_path": report_path,
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
    args = parser.parse_args(argv)
    try:
        summary = run_config_file(
            args.config,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
        )
    except Exception:
        traceback.print_exc()
        print("run FAILED (logged to the results store)")
        return 1
    print(f"run {summary['run_id']} completed over folds {summary['folds']}")
    print(f"report: {summary['report_path']}")
    return 0
