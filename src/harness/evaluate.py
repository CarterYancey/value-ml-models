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

import numpy as np
import pandas as pd

from eval.era import collect_predictions
from eval.metrics import compute_all, regression_diagnostics
from harness.calibration import PrequentialCalibration
from harness.config import EvalConfig, parse_pick_outcomes
from harness.dataset import Dataset, SplitAccess, feature_matrix
from harness.errors import ConfigError, DatasetValidationError
from harness.model_store import ModelBundle
from harness.results import ResultsStore, RunLog, git_sha, new_run_id
from harness.runner import (
    DEFAULT_DATA_ROOT,
    DEFAULT_REPORTS,
    DEFAULT_RESULTS,
    _pick_outcome_columns,
    check_pick_screen,
    finalize_run,
    report_only_metrics,
    selection_columns,
    universe_rows,
)


def blend_scores(score_arrays, periods) -> np.ndarray:
    """Several models' scores on the same rows as one ranking: within
    each period, every model's scores are ranked as a share of the
    period's rows (the best at 1.0) and the shares averaged. This is
    the backtest's `combine = "mean_rank"` on test rows: a row one model
    has no score for (NaN) is ranked on the others alone, and ties share
    the better rank. Shares, not rank numbers, so that periods of
    different sizes give scores on one scale."""
    frame = pd.DataFrame(
        {i: np.asarray(s, dtype=float) for i, s in enumerate(score_arrays)}
    )
    shares = frame.groupby(np.asarray(periods), sort=False).rank(
        method="max", pct=True
    )
    return shares.mean(axis=1, skipna=True).to_numpy(dtype=float)


def _load_blend(paths, bundle: ModelBundle) -> list[ModelBundle]:
    """The bundles an evaluation blends with `bundle`, checked to be
    measured on the same thing: same dataset version and scheme, and a
    fold model for every fold of `bundle`."""
    others = []
    primary = bundle.train_config
    for path in paths:
        other = ModelBundle.load(path)
        config = other.train_config
        if (config.dataset_version, config.scheme) != (
            primary.dataset_version, primary.scheme
        ):
            raise ConfigError(
                f"blend bundle {path} was trained on "
                f"{config.dataset_version!r} under {config.scheme!r}; the "
                f"evaluated bundle on {primary.dataset_version!r} under "
                f"{primary.scheme!r}"
            )
        missing = sorted(set(bundle.folds) - set(other.folds))
        if missing:
            raise ConfigError(
                f"blend bundle {path} has no model for folds {missing}"
            )
        if config.config_hash == primary.config_hash:
            raise ConfigError(f"blend bundle {path} is the evaluated bundle")
        others.append(other)
    return others


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
    if eval_config.universe and train_config.universe:
        raise ConfigError(
            "the eval config sets a universe but the bundle was trained "
            "with one; a bundle's own universe is pinned"
        )
    blended = _load_blend(eval_config.blend, bundle)
    if blended and train_config.calibration:
        raise ConfigError(
            "a blend is a ranking, not a probability; evaluate the "
            "uncalibrated bundle"
        )
    # a blended score is a mean rank share: nothing to read as a
    # probability, whatever the bundles are
    probabilistic = bundle.probabilistic and not blended
    # the eval run's identity: the pinned train config with the eval's
    # metric parameters merged in — a distinct config hash per (bundle,
    # eval criteria), counted by the trial ledger
    config = replace(
        train_config,
        name=f"{train_config.name}__{eval_config.name}",
        top_k=eval_config.top_k,
        score_thresholds=eval_config.score_thresholds,
        precision_targets=eval_config.precision_targets,
        pick_outcomes=(
            train_config.pick_outcomes
            if eval_config.pick_outcomes is None
            else parse_pick_outcomes(
                eval_config.pick_outcomes,
                train_config.horizon_years,
                eval_config_path or eval_config.name,
            )
        ),
        pick_screen=(
            eval_config.pick_screen
            if eval_config.pick_screen is not None
            else train_config.pick_screen
        ),
        # an eval universe measures the models as trained on fewer test
        # rows: scope "test", counted in the universe-qualified cell
        **(
            {"universe": eval_config.universe, "universe_scope": "test"}
            if eval_config.universe
            else {}
        ),
        blend=tuple(b.train_config.config_hash for b in blended),
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
        # same cell accounting as the runner: continuous-target bundles
        # are trials against their binary eval_label cell
        "label": config.cell_label,
        "model": config.model_name,
    }
    run_log = RunLog(store, base_row)

    try:
        # Loaded from the directory the bundle was trained on
        # (train_config.dataset_version is the `dataset_vX.Y` directory
        # name); the manifest's own dataset_version field is a separate
        # build-identity string ("X.Y") and is not expected to match it.
        dataset = Dataset(Path(data_root) / train_config.dataset_version)
        declared = {
            c
            for group in ("features", "ranks", "sector_ranks")
            for c in dataset.columns(group)
        }
        missing = sorted(set(bundle.feature_columns) - declared)
        if missing:
            raise DatasetValidationError(
                f"bundle feature columns absent from dataset: {missing}"
            )

        fold_results: list[dict] = []
        prediction_frames: list[pd.DataFrame] = []
        # bundles store raw fold models; a calibrated config's scores are
        # re-derived prequentially, identically to the training run
        # (bundle.folds is sorted — chronological under walkforward)
        calib = (
            PrequentialCalibration(
                config.calibration, config.calibration_min_rows
            )
            if config.calibration
            else None
        )
        needed_columns = list(
            dict.fromkeys(
                list(bundle.feature_columns)
                + [c for b in blended for c in b.feature_columns]
                + [config.label]
                + ([config.eval_label] if config.eval_label else [])
                + list(config.pick_outcomes)
                + [dataset.sample_weight_column(config.horizon_years)]
                + selection_columns(config)
            )
        )
        dataset.check_pick_outcomes(config.pick_outcomes, bundle.feature_columns)
        dataset.check_universe(config.universe)
        check_pick_screen(dataset, config.pick_screen)
        run_log.n_folds = len(bundle.folds)
        for fold in bundle.folds:
            split = dataset.apply_split(
                config.scheme, fold, config.horizon_years,
                access=SplitAccess.STANDARD,
                columns=needed_columns,
            )
            # continuous-target bundles are measured against their binary
            # eval_label cell, exactly as in the training run
            _, test_rows = universe_rows(dataset, config, split)
            test_fit = dataset.fit_data(
                test_rows, config.eval_label or config.label,
                bundle.feature_columns, config.horizon_years,
            )
            model = bundle.fold_models[fold]
            scores = model.predict_scores(test_fit.X)
            raw_scores = scores
            if calib is not None:
                scores = calib.calibrate(fold, raw_scores)
            if blended:
                rows = test_rows.loc[test_fit.X.index]
                dates = pd.to_datetime(rows["snapshot_date"])
                scores = blend_scores(
                    [scores]
                    + [
                        b.fold_models[fold].predict_scores(
                            feature_matrix(rows, b.feature_columns)
                        )
                        for b in blended
                    ],
                    periods=(dates.dt.year * 4 + dates.dt.quarter).to_numpy(),
                )
            metrics = compute_all(
                test_fit.y,
                scores,
                sample_weight=test_fit.sample_weight,
                top_k=config.top_k,
                score_thresholds=config.score_thresholds,
                precision_targets=config.precision_targets,
                probabilistic=probabilistic,
            )
            outcome = None
            if config.eval_label:  # continuous-target bundle
                outcome = test_rows.loc[
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
            stats = bundle.fold_train_stats[fold]
            fold_results.append(
                {
                    "fold": fold,
                    "n_train_rows": stats["n_train_rows"],
                    "effective_train_size": stats["effective_train_size"],
                    "n_test_rows": len(test_fit.X),
                    "metrics": metrics,
                    **(
                        {"n_test_rows_all": len(split.test)}
                        if config.universe
                        else {}
                    ),
                }
            )
            test_years = pd.to_datetime(
                test_rows.loc[test_fit.X.index, "snapshot_date"]
            ).dt.year.to_numpy()
            fold_predictions = collect_predictions(
                fold, test_years, test_fit.y, scores,
                test_fit.sample_weight, outcome=outcome,
                **_pick_outcome_columns(dataset, config, test_rows, test_fit),
            )
            prediction_frames.append(fold_predictions)
            # report-only outcomes of this fold's picks; same top-K rows
            # as the fold's precision@K
            metrics.update(report_only_metrics(fold_predictions, config,
                                               per_year=False))
            if calib is not None:
                calib.observe(raw_scores, test_fit.y, test_fit.sample_weight)
            run_log.fold_done(
                {
                    "fold": fold,
                    "n_train_rows": stats["n_train_rows"],
                    "effective_train_size": (
                        f"{stats['effective_train_size']:.4f}"
                    ),
                    "n_test_rows": len(test_fit.X),
                    "metrics_json": metrics,
                }
            )
        run_log.commit()

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
            artifacts={
                "source_bundle": Path(bundle_dir),
                **(
                    {
                        "blend": [
                            f"{b.train_config.name} "
                            f"(`{b.train_config.config_hash}`, run "
                            f"`{b.run_id}`)"
                            for b in blended
                        ]
                    }
                    if blended
                    else {}
                ),
                **(
                    {"calibration": calib.summary()}
                    if calib is not None
                    else {}
                ),
            },
            # calibration and PR/ROC curves are score-only; the scores are
            # identical to the training run, so we don't redraw them
            render_score_figures=False,
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
    except BaseException as exc:
        # BaseException: Ctrl-C and SystemExit stop a run too, and a
        # stopped run is a failed trial, not a shorter completed one
        run_log.fail(exc)
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
        "score_thresholds, precision_targets)"
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
