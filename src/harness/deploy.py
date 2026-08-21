"""Deployment: refit on all labeled data, then score today's stocks.

Development answers "does this configuration generalize?" with purged
walk-forward measurement; deployment answers "given a configuration we
already selected, what is the best model we can ship today?". Per the
dataset contract (data/manual.md §4, rule 7), the model that ships is
refit on *all* currently-eligible data — every row whose label is
observable, all snapshot kinds — because the purge/embargo/holdout
discipline constrains measurement, not what the deployed model may learn
from. Accordingly this module never reads split tags at all, and nothing
it produces is an evaluation result: scores from a deployment model have
no test set and must never be reported as performance.

Two entry points:

- ``vml-train-deploy <experiment.toml>`` refits the config's model on all
  labeled rows of its pinned dataset (the config's `scheme`/`folds` are
  measurement settings and are ignored here) and saves a single-model
  `DeploymentBundle`. The run is logged to the results store under scheme
  ``deployment``.
- ``vml-predict <bundle_dir> <inference_data>`` scores an inference
  dataset — ``data/datasets/inference_{date}/`` with a `dataset.parquet`
  of today's stocks carrying the feature columns, no labels — writes the
  full ranking to CSV (plus a provenance sidecar JSON), and prints the
  top picks.
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from harness.config import ExperimentConfig
from harness.dataset import Dataset
from harness.errors import DatasetValidationError
from harness.model_store import DeploymentBundle
from harness.results import ResultsStore, git_sha, new_run_id
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_MODELS, DEFAULT_RESULTS
from models.registry import build_model

#: Where vml-predict writes ranking CSVs by default (git-ignored: scores
#: are data artifacts; the provenance to recreate them is the sidecar
#: JSON + results store).
DEFAULT_PREDICTIONS = Path("predictions")

#: Scheme names recorded in the results store for these runs. Distinct
#: from every split scheme so deployment/inference rows can never be
#: mistaken for (or counted among) walk-forward trials.
DEPLOYMENT_SCHEME = "deployment"
INFERENCE_SCHEME = "inference"

#: How many top-ranked rows vml-predict prints.
DEFAULT_TOP_N = 50

_ID_COLUMNS = ("permaticker", "ticker", "snapshot_date", "snapshot_kind")


def train_deployment_model(
    config: ExperimentConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    models_dir: str | Path = DEFAULT_MODELS,
    config_path: str = "",
) -> dict:
    """Refit `config`'s model on every labeled row of its dataset (all
    snapshot kinds, no split filtering) and save a DeploymentBundle.
    Returns a summary dict; raises after logging on failure."""
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
        "scheme": DEPLOYMENT_SCHEME,
        "fold": "all_labeled",
        "horizon_years": config.horizon_years,
        "label": config.label,
        "model": config.model_name,
    }

    try:
        dataset = Dataset(Path(data_root) / config.dataset_version)
        feature_cols = dataset.feature_columns(
            config.feature_groups,
            config.feature_columns,
            exclude=config.exclude_feature_columns,
        )
        # All currently-eligible data: fit_data keeps every row whose
        # label is observable — all roles, all kinds, delistings included.
        fit = dataset.fit_data(
            dataset.data, config.label, feature_cols, config.horizon_years
        )
        if not len(fit.X):
            raise DatasetValidationError(
                f"dataset {dataset.version} has no labeled rows for "
                f"{config.label!r}; nothing to deploy"
            )
        model = build_model(config.model_name, config.model_params, config.seed)
        model.fit(fit.X, fit.y, sample_weight=fit.sample_weight)

        bundle_path = DeploymentBundle(
            train_config=config,
            run_id=run_id,
            git_sha=sha,
            probabilistic=model.probabilistic,
            feature_columns=tuple(feature_cols),
            model=model,
            n_train_rows=len(fit.X),
            effective_train_size=fit.effective_size,
        ).save(models_dir)

        store.append(
            {
                **base_row,
                "status": "completed",
                "n_train_rows": len(fit.X),
                "effective_train_size": f"{fit.effective_size:.4f}",
            }
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "n_train_rows": len(fit.X),
            "effective_train_size": fit.effective_size,
            "bundle_path": bundle_path,
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


def load_inference_frame(path: str | Path) -> tuple[pd.DataFrame, str]:
    """Load an inference dataset: a `datasets/inference_{date}/` directory
    containing `dataset.parquet` (today's stocks with feature columns), or
    a bare parquet file. Returns (frame, source_name)."""
    p = Path(path)
    if p.is_dir():
        parquet = p / "dataset.parquet"
        if not parquet.exists():
            raise DatasetValidationError(
                f"inference dataset directory {p} has no dataset.parquet"
            )
        name = p.name
    elif p.suffix == ".parquet" and p.exists():
        parquet, name = p, p.stem
    else:
        raise DatasetValidationError(
            f"inference dataset not found: {p} (expected a directory "
            "containing dataset.parquet, or a .parquet file)"
        )
    frame = pd.read_parquet(parquet)
    if "permaticker" not in frame.columns:
        raise DatasetValidationError(
            f"inference data {parquet} lacks the entity key 'permaticker'"
        )
    return frame, name


def predict_with_bundle(
    bundle_dir: str | Path,
    inference_path: str | Path,
    *,
    output_path: str | Path | None = None,
    results_path: str | Path = DEFAULT_RESULTS,
    predictions_dir: str | Path = DEFAULT_PREDICTIONS,
    top_n: int = DEFAULT_TOP_N,
) -> dict:
    """Score an inference dataset with a deployment bundle. Writes the
    full ranking (score-descending, 1-based `rank`) to CSV plus a
    provenance sidecar `<output>.meta.json`; returns a summary dict with
    the top `top_n` rows. Raises after logging on failure."""
    bundle = DeploymentBundle.load(bundle_dir)
    config = bundle.train_config
    store = ResultsStore(results_path)
    run_id = new_run_id()
    sha = git_sha()
    base_row = {
        "run_id": run_id,
        "experiment": f"{config.name}__inference",
        "config_hash": config.config_hash,
        "config_path": str(bundle_dir),
        "dataset_version": config.dataset_version,
        "git_sha": sha,
        "seed": config.seed,
        "scheme": INFERENCE_SCHEME,
        "horizon_years": config.horizon_years,
        "label": config.label,
        "model": config.model_name,
    }

    try:
        frame, source_name = load_inference_frame(inference_path)
        missing = sorted(set(bundle.feature_columns) - set(frame.columns))
        if missing:
            raise DatasetValidationError(
                f"inference data lacks feature columns the model was "
                f"trained on: {missing}"
            )
        scores = bundle.model.predict_scores(
            frame[list(bundle.feature_columns)]
        )

        out = frame[[c for c in _ID_COLUMNS if c in frame.columns]].copy()
        out["score"] = scores
        out = out.sort_values(
            ["score", "permaticker"], ascending=[False, True], kind="mergesort"
        ).reset_index(drop=True)
        out.insert(0, "rank", range(1, len(out) + 1))

        if output_path is None:
            output_path = (
                Path(predictions_dir) / f"{source_name}__{Path(bundle_dir).name}.csv"
            )
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output_path, index=False)

        meta_path = output_path.with_suffix(output_path.suffix + ".meta.json")
        meta_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "scored_utc": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                    "git_sha": sha,
                    "bundle_dir": str(bundle_dir),
                    "bundle_run_id": bundle.run_id,
                    "config_hash": config.config_hash,
                    "trained_on": config.dataset_version,
                    "label": config.label,
                    "horizon_years": config.horizon_years,
                    "model": config.model_name,
                    "probabilistic": bundle.probabilistic,
                    "inference_source": str(inference_path),
                    "n_rows_scored": len(out),
                    "note": (
                        "Deployment scores: ranked by a model refit on all "
                        "labeled data (data/manual.md §4 rule 7). No test "
                        "set exists for this fit — never report these as "
                        "performance."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )

        store.append(
            {
                **base_row,
                "status": "completed",
                "fold": source_name,
                "n_test_rows": len(out),
            }
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "n_rows_scored": len(out),
            "output_path": output_path,
            "meta_path": meta_path,
            "top": out.head(top_n),
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


# ------------------------------------------------------------------- CLIs


def _main_train(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Refit an experiment config's model on ALL labeled "
        "rows of its dataset and save a deployment bundle "
        "(scheme/folds in the config are measurement settings and are "
        "ignored; see data/manual.md §4 rule 7)."
    )
    parser.add_argument("config", help="path to an experiments/*.toml config")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--models-dir", default=str(DEFAULT_MODELS))
    args = parser.parse_args(argv)
    try:
        summary = train_deployment_model(
            ExperimentConfig.from_file(args.config),
            data_root=args.data_root,
            results_path=args.results,
            models_dir=args.models_dir,
            config_path=str(args.config),
        )
    except Exception:
        traceback.print_exc()
        print("deployment training FAILED (logged to the results store)")
        return 1
    print(
        f"deployment training {summary['run_id']} completed: "
        f"{summary['n_train_rows']} labeled rows "
        f"(effective size {summary['effective_train_size']:.1f})"
    )
    print(f"deployment bundle: {summary['bundle_path']} "
          "(score today's stocks with vml-predict)")
    return 0


def _main_predict(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Score an inference dataset (today's stocks) with a "
        "deployment bundle; write the full ranking to CSV and print the "
        "top picks."
    )
    parser.add_argument(
        "bundle",
        help="path to a deployment bundle directory "
        "(experiments/models/<name>_deployment_<run_id>)",
    )
    parser.add_argument(
        "inference",
        help="inference dataset: a data/datasets/inference_{date}/ "
        "directory (containing dataset.parquet) or a .parquet file",
    )
    parser.add_argument(
        "--output", default=None,
        help=f"output CSV path (default: {DEFAULT_PREDICTIONS}/"
        "<inference>__<bundle>.csv)",
    )
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument(
        "--top", type=int, default=DEFAULT_TOP_N,
        help=f"how many top-ranked rows to print (default {DEFAULT_TOP_N})",
    )
    args = parser.parse_args(argv)
    try:
        summary = predict_with_bundle(
            args.bundle,
            args.inference,
            output_path=args.output,
            results_path=args.results,
            top_n=args.top,
        )
    except Exception:
        traceback.print_exc()
        print("inference FAILED (logged to the results store)")
        return 1
    top = summary["top"]
    print(
        f"scored {summary['n_rows_scored']} rows "
        f"(run {summary['run_id']}); full ranking: {summary['output_path']}"
    )
    print(f"provenance: {summary['meta_path']}")
    print(f"\ntop {len(top)} by score:\n")
    print(top.to_string(index=False))
    return 0


def main_train() -> None:
    import sys

    sys.exit(_main_train())


def main_predict() -> None:
    import sys

    sys.exit(_main_predict())
