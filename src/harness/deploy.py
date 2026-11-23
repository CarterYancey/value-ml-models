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
- ``vml-predict <bundle_dir>... <inference_data>`` scores an inference
  dataset — ``data/datasets/inference_{date}/`` with a `dataset.parquet`
  of today's stocks carrying the feature columns, no labels — writes the
  full ranking to CSV (plus a provenance sidecar JSON), and prints the
  top picks. With several bundle directories it writes one combined CSV
  with a `rank_<model>`/`score_<model>` column pair per bundle so the
  models' views of each stock sit side by side. Scores are only
  comparable across models via the rank columns: each model's score is
  its own probability/margin scale. ``--trends`` carries the
  long-horizon trend context columns (`TREND_COLUMNS`) verbatim from the
  inference data into either CSV. ``--filter``, ``--pick`` and
  ``--max-per-group`` apply a backtest's selection rule to the ranking
  (`screen_rows`, `mark_picks`): row filters before any rank is taken,
  then the first K rows of the ranking with a cap per group, so the
  list that is printed is what the backtest would have bought.
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from harness.config import ExperimentConfig
from harness.dataset import Dataset, feature_matrix
from harness.filters import (
    FILTERABLE_GROUPS,
    FilterSpec,
    apply_filters,
    describe_filters,
)
from harness.errors import ConfigError, DatasetValidationError
from harness.model_store import DeploymentBundle
from harness.results import ResultsStore, git_sha, new_run_id
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_MODELS, DEFAULT_RESULTS
from models.registry import build_model, check_target_labels, model_target

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

#: Long-horizon trend/consistency context columns `vml-predict --trends`
#: carries from the inference data into the output CSV — read-along
#: context for a ranking, copied verbatim from the upstream columns
#: (never derived here).
TREND_COLUMNS = (
    "revenue_trend_20q",
    "tangibles_trend_20q",
    "ocf_trend_20q",
    "div_years_paid_10y",
    "div_cuts_10y",
)


def _carry_columns(
    frame: pd.DataFrame, columns: tuple[str, ...] | list[str]
) -> list[str]:
    """Validate columns to carry verbatim from the inference frame into
    the output CSV; naming a column the frame lacks is an error, not a
    silently thinner CSV."""
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise DatasetValidationError(
            f"inference data lacks columns requested for the output: "
            f"{missing}"
        )
    return list(columns)


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
        check_target_labels(config)
        if config.calibration:
            raise ConfigError(
                "a deployment refit has no out-of-sample history to "
                "calibrate on (prequential calibration lives in the "
                "walk-forward runner); deploy the uncalibrated config — "
                "the ranking is identical. Deployment-time calibration "
                "(fit on the full walk-forward OOS history) is an open "
                "TODO item."
            )
        dataset = Dataset(Path(data_root) / config.dataset_version)
        feature_cols = config.resolve_feature_columns(dataset)
        # All currently-eligible data: fit_data keeps every row whose
        # label is observable — all roles, all kinds, delistings included.
        # Column-projected: the refit needs features + label + weight,
        # not the full-width (string-heavy) frame.
        dataset.check_universe(config.universe)
        refit_frame = dataset.frame(
            list(feature_cols)
            + [
                config.label,
                dataset.sample_weight_column(config.horizon_years),
            ]
            + [f.column for f in config.universe]
        )
        if config.universe and config.universe_scope == "all":
            # the deployed model learns from the rows the selected
            # config learned from: a universe is part of the model
            refit_frame = dataset.apply_universe(refit_frame, config.universe)
        fit = dataset.fit_data(
            refit_frame, config.label, feature_cols, config.horizon_years,
            target=model_target(config.model_name),
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


def _inference_manifest_columns(path: str | Path) -> dict | None:
    """`manifest.json["columns"]` of an inference directory, or None for
    a bare parquet file or a directory without a manifest."""
    manifest = Path(path) / "manifest.json"
    if not manifest.is_file():
        return None
    columns = json.loads(manifest.read_text()).get("columns")
    return columns if isinstance(columns, dict) else None


def screen_rows(
    frame: pd.DataFrame,
    filters: tuple[FilterSpec, ...] | list[FilterSpec],
    inference_path: str | Path,
) -> tuple[pd.DataFrame, dict]:
    """The rows of an inference frame passing every `--filter`, and what
    was left out. The deployment counterpart of a backtest's
    `[[investability]]`: applied before any score is ranked, because
    the backtest ranks its models inside the investable rows and a
    mean of ranks taken over other rows is another ranking. A NULL
    fails. When the inference directory has a manifest the columns
    must be in its filterable groups; a column the data lacks is an
    error either way."""
    filters = tuple(filters)
    if not filters:
        return frame, {}
    declared = _inference_manifest_columns(inference_path)
    if declared is not None:
        allowed = {
            c for g in FILTERABLE_GROUPS for c in declared.get(g, [])
        }
        outside = sorted({f.column for f in filters} - allowed)
        if outside:
            raise ConfigError(
                f"--filter references {outside}, not in the inference "
                f"manifest's {list(FILTERABLE_GROUPS)} groups"
            )
    missing = sorted({f.column for f in filters} - set(frame.columns))
    if missing:
        raise DatasetValidationError(
            f"inference data lacks the filter columns {missing}"
        )
    kept = apply_filters(frame, filters)
    return kept, {
        "filters": describe_filters(filters),
        "n_rows_filtered_out": int(len(frame) - len(kept)),
    }


def _check_selection(
    pick: int | None, max_per_group: int | None, group_column: str
) -> None:
    if pick is None:
        if max_per_group is not None:
            raise ConfigError(
                "--max-per-group caps the picks: it needs --pick K"
            )
        return
    if pick < 1:
        raise ConfigError(f"--pick must be 1 or more, got {pick}")
    if max_per_group is not None and max_per_group < 1:
        raise ConfigError(
            f"--max-per-group must be 1 or more, got {max_per_group}"
        )
    if max_per_group is not None and not group_column:
        raise ConfigError("--max-per-group needs a --group-column")


def mark_picks(
    ranked: pd.DataFrame,
    frame: pd.DataFrame,
    pick: int | None,
    max_per_group: int | None,
    group_column: str,
) -> tuple[pd.DataFrame, dict]:
    """Add a `pick` column to a ranking (best first, sharing `frame`'s
    index): 1..K down the first K rows, skipping a row once
    `max_per_group` of the picks already share its group. The walk is
    the backtest's (`portfolio.strategy.capped_top_k`), so a NULL group
    counts as one group and fewer than K picks come back when the
    groups run out. With a cap the group column is carried into the
    ranking. Without `pick` the ranking is returned unchanged."""
    if pick is None:
        return ranked, {}
    # imported here: portfolio builds on harness, not the reverse
    from portfolio.strategy import capped_top_k

    out = ranked.copy()
    if max_per_group is not None:
        if group_column not in frame.columns:
            raise DatasetValidationError(
                f"inference data lacks the group column {group_column!r}"
            )
        if group_column not in out.columns:
            out[group_column] = frame.loc[out.index, group_column]
        chosen = capped_top_k(
            out.assign(group=out[group_column]), pick, max_per_group
        ).index
    else:
        chosen = out.index[:pick]
    out["pick"] = pd.Series(
        range(1, len(chosen) + 1), index=chosen, dtype="Int64"
    ).reindex(out.index)
    return out, {
        "selection": {
            "pick": int(pick),
            "max_per_group": max_per_group,
            "group_column": group_column if max_per_group else None,
            "n_picked": int(len(chosen)),
        }
    }


def _inside_universe(bundles, frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """The rows of an inference frame inside every bundle's
    `[[universe]]`, and what was left out. A universe is part of the
    model: the fit learned from rows inside it (or was measured on
    them), so the ranking is made over those rows only. A row with a
    NULL in a filter column is outside. The universe's columns must be
    in the inference data."""
    filters = tuple(
        dict.fromkeys(f for b in bundles for f in b.train_config.universe)
    )
    if not filters:
        return frame, {}
    missing = sorted({f.column for f in filters} - set(frame.columns))
    if missing:
        raise DatasetValidationError(
            f"inference data lacks the universe columns {missing}; the "
            f"model's universe is `{describe_filters(filters)}`"
        )
    inside = apply_filters(frame, filters)
    return inside, {
        "universe": describe_filters(filters),
        "n_rows_outside_universe": int(len(frame) - len(inside)),
    }


def _score_frame(bundle: DeploymentBundle, frame: pd.DataFrame):
    """Validate that `frame` carries the bundle's feature columns and
    return the model's scores for every row."""
    missing = sorted(set(bundle.feature_columns) - set(frame.columns))
    if missing:
        raise DatasetValidationError(
            f"inference data lacks feature columns the model was "
            f"trained on: {missing}"
        )
    return bundle.model.predict_scores(
        feature_matrix(frame, bundle.feature_columns)
    )


def predict_with_bundle(
    bundle_dir: str | Path,
    inference_path: str | Path,
    *,
    output_path: str | Path | None = None,
    results_path: str | Path = DEFAULT_RESULTS,
    predictions_dir: str | Path = DEFAULT_PREDICTIONS,
    top_n: int = DEFAULT_TOP_N,
    extra_columns: tuple[str, ...] | list[str] = (),
    filters: tuple[FilterSpec, ...] | list[FilterSpec] = (),
    pick: int | None = None,
    max_per_group: int | None = None,
    group_column: str = "sector",
) -> dict:
    """Score an inference dataset with a deployment bundle. Writes the
    full ranking (score-descending, 1-based `rank`) to CSV plus a
    provenance sidecar `<output>.meta.json`; returns a summary dict with
    the top `top_n` rows. `extra_columns` (e.g. `TREND_COLUMNS` for the
    CLI's `--trends`) are carried verbatim from the inference data into
    the CSV after the score. `filters` leave rows out before ranking
    (`screen_rows`); `pick`, `max_per_group` and `group_column` mark the
    rows a backtest with the same rule would buy (`mark_picks`), which
    the summary returns as `picks`. Raises after logging on failure."""
    _check_selection(pick, max_per_group, group_column)
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
        frame, universe_meta = _inside_universe([bundle], frame)
        frame, filter_meta = screen_rows(frame, filters, inference_path)
        scores = _score_frame(bundle, frame)
        extra = _carry_columns(frame, extra_columns)

        id_cols = [c for c in _ID_COLUMNS if c in frame.columns]
        out = frame[id_cols + extra].copy()
        out["score"] = scores
        out = out.sort_values(
            ["score", "permaticker"], ascending=[False, True], kind="mergesort"
        )
        out, selection_meta = mark_picks(
            out, frame, pick, max_per_group, group_column
        )
        out = out.reset_index(drop=True)
        out.insert(0, "rank", range(1, len(out) + 1))
        selection_cols = [
            c for c in ("pick", group_column)
            if c in out.columns and c not in id_cols + extra
        ] if pick is not None else []
        out = out[["rank"] + selection_cols + id_cols + ["score"] + extra]

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
                    **({"extra_columns": extra} if extra else {}),
                    **universe_meta,
                    **filter_meta,
                    **selection_meta,
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
                    **(
                        {"eval_label": config.eval_label}
                        if config.eval_label
                        else {}
                    ),
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
            **(
                {"picks": out[out["pick"].notna()]}
                if pick is not None
                else {}
            ),
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


def _bundle_column_names(bundles: list[DeploymentBundle]) -> list[str]:
    """One short, unique name per bundle for the combined CSV's column
    suffixes: the config name, with the bundle's run_id appended only
    when two bundles share a config name."""
    names = [b.train_config.name for b in bundles]
    return [
        f"{name}_{bundle.run_id}" if names.count(name) > 1 else name
        for name, bundle in zip(names, bundles)
    ]


def predict_with_bundles(
    bundle_dirs: list[str | Path],
    inference_path: str | Path,
    *,
    output_path: str | Path | None = None,
    results_path: str | Path = DEFAULT_RESULTS,
    predictions_dir: str | Path = DEFAULT_PREDICTIONS,
    top_n: int = DEFAULT_TOP_N,
    extra_columns: tuple[str, ...] | list[str] = (),
    filters: tuple[FilterSpec, ...] | list[FilterSpec] = (),
    pick: int | None = None,
    max_per_group: int | None = None,
    group_column: str = "sector",
) -> dict:
    """Score one inference dataset with several deployment bundles and
    write a single combined CSV: the id columns, `mean_rank` across
    models, a `rank_<model>`/`score_<model>` pair per bundle, ordered
    by `mean_rank`, then any `extra_columns` carried verbatim from the
    inference data (e.g. `TREND_COLUMNS` for the CLI's `--trends`). Each model's scoring is logged to the results store
    as its own inference run, exactly as a single-bundle run would be.
    `filters` leave rows out before any model's rank is taken, so
    `mean_rank` is the backtest's `combine = "mean_rank"` over its
    investable rows; `pick`, `max_per_group` and `group_column` mark
    the rows such a backtest would buy (`mark_picks`), returned as
    `picks`. Returns a summary dict with the top `top_n` rows."""
    _check_selection(pick, max_per_group, group_column)
    bundles = [DeploymentBundle.load(d) for d in bundle_dirs]
    names = _bundle_column_names(bundles)
    store = ResultsStore(results_path)
    sha = git_sha()
    frame, source_name = load_inference_frame(inference_path)
    # the combined ranking is made over the rows inside every model's
    # universe; a model is never asked about a stock it was not fitted
    # or measured on
    frame, universe_meta = _inside_universe(bundles, frame)
    frame, filter_meta = screen_rows(frame, filters, inference_path)
    extra = _carry_columns(frame, extra_columns)

    out = frame[
        [c for c in _ID_COLUMNS if c in frame.columns] + extra
    ].copy()
    run_ids, per_model = [], []
    for bundle_dir, bundle, name in zip(bundle_dirs, bundles, names):
        config = bundle.train_config
        run_id = new_run_id()
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
            scores = _score_frame(bundle, frame)
        except Exception as exc:
            store.append(
                {
                    **base_row,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            raise
        out[f"score_{name}"] = scores
        out[f"rank_{name}"] = (
            out[f"score_{name}"].rank(ascending=False, method="min").astype(int)
        )
        store.append(
            {
                **base_row,
                "status": "completed",
                "fold": source_name,
                "n_test_rows": len(out),
            }
        )
        run_ids.append(run_id)
        per_model.append(
            {
                "column_suffix": name,
                "run_id": run_id,
                "bundle_dir": str(bundle_dir),
                "bundle_run_id": bundle.run_id,
                "config_hash": config.config_hash,
                "trained_on": config.dataset_version,
                "label": config.label,
                **(
                    {"eval_label": config.eval_label}
                    if config.eval_label
                    else {}
                ),
                "horizon_years": config.horizon_years,
                "model": config.model_name,
                "probabilistic": bundle.probabilistic,
            }
        )

    out["mean_rank"] = out[[f"rank_{n}" for n in names]].mean(axis=1)
    out = out.sort_values(
        ["mean_rank", "permaticker"], ascending=[True, True], kind="mergesort"
    )
    out, selection_meta = mark_picks(
        out, frame, pick, max_per_group, group_column
    )
    out = out.reset_index(drop=True)
    id_cols = [c for c in _ID_COLUMNS if c in out.columns]
    selection_cols = [
        c for c in ("pick", group_column)
        if c in out.columns and c not in id_cols + extra
    ] if pick is not None else []
    out = out[
        selection_cols
        + id_cols
        + ["mean_rank"]
        + [c for n in names for c in (f"rank_{n}", f"score_{n}")]
        + extra
    ]

    if output_path is None:
        stem = f"{source_name}__multi__" + "__".join(names)
        if len(stem) > 180:
            stem = f"{source_name}__multi_{len(bundles)}models"
        output_path = Path(predictions_dir) / f"{stem}.csv"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)

    meta_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    meta_path.write_text(
        json.dumps(
            {
                **({"extra_columns": extra} if extra else {}),
                "scored_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "git_sha": sha,
                "inference_source": str(inference_path),
                **universe_meta,
                **filter_meta,
                **selection_meta,
                "n_rows_scored": len(out),
                "models": per_model,
                "note": (
                    "Deployment scores: ranked by models refit on all "
                    "labeled data (data/manual.md §4 rule 7). No test set "
                    "exists for these fits — never report these as "
                    "performance. Scores are per-model scales; compare "
                    "models via the rank_* columns."
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )

    return {
        "run_ids": run_ids,
        "status": "completed",
        "n_rows_scored": len(out),
        "output_path": output_path,
        "meta_path": meta_path,
        "top": out.head(top_n),
        **({"picks": out[out["pick"].notna()]} if pick is not None else {}),
    }


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
        description="Score an inference dataset (today's stocks) with one "
        "or more deployment bundles; write the full ranking to CSV and "
        "print the top picks. Several bundles produce one combined CSV "
        "with a rank_<model>/score_<model> column pair per bundle."
    )
    parser.add_argument(
        "bundles",
        nargs="+",
        metavar="bundle",
        help="path(s) to deployment bundle directories "
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
        "<inference>__<bundle>.csv, or "
        f"{DEFAULT_PREDICTIONS}/<inference>__multi__<names>.csv for "
        "several bundles)",
    )
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument(
        "--top", type=int, default=DEFAULT_TOP_N,
        help=f"how many top-ranked rows to print (default {DEFAULT_TOP_N})",
    )
    parser.add_argument(
        "--trends", action="store_true",
        help="carry the long-horizon trend context columns "
        f"({', '.join(TREND_COLUMNS)}) from the inference data into the "
        "output CSV",
    )
    parser.add_argument(
        "--filter", action="append", default=[], metavar="'COLUMN OP VALUE'",
        help="keep only inference rows passing this filter, before any "
        "rank is taken (repeatable; a NULL fails): the backtest's "
        "[[investability]], e.g. --filter 'dollar_volume_3m_rank >= 0.2'",
    )
    parser.add_argument(
        "--pick", type=int, default=None, metavar="K",
        help="mark the first K rows of the ranking as picks (a `pick` "
        "column, 1..K) and print them instead of the top rows",
    )
    parser.add_argument(
        "--max-per-group", type=int, default=None, metavar="N",
        help="with --pick: skip a row once N of the picks already share "
        "its group (the backtest's [portfolio] max_per_group)",
    )
    parser.add_argument(
        "--group-column", default="sector",
        help="the column --max-per-group counts (default: sector)",
    )
    args = parser.parse_args(argv)
    extra_columns = TREND_COLUMNS if args.trends else ()
    try:
        selection = {
            "filters": [
                FilterSpec.parse(text, "--filter") for text in args.filter
            ],
            "pick": args.pick,
            "max_per_group": args.max_per_group,
            "group_column": args.group_column,
        }
        if len(args.bundles) == 1:
            summary = predict_with_bundle(
                args.bundles[0],
                args.inference,
                output_path=args.output,
                results_path=args.results,
                top_n=args.top,
                extra_columns=extra_columns,
                **selection,
            )
            runs = summary["run_id"]
        else:
            summary = predict_with_bundles(
                args.bundles,
                args.inference,
                output_path=args.output,
                results_path=args.results,
                top_n=args.top,
                extra_columns=extra_columns,
                **selection,
            )
            runs = ", ".join(summary["run_ids"])
    except Exception:
        traceback.print_exc()
        print("inference FAILED (logged to the results store)")
        return 1
    top = summary["top"]
    print(
        f"scored {summary['n_rows_scored']} rows "
        f"(run {runs}); full ranking: {summary['output_path']}"
    )
    print(f"provenance: {summary['meta_path']}")
    order = "score" if len(args.bundles) == 1 else "mean rank"
    if "picks" in summary:
        picks = summary["picks"]
        cap = (
            f", at most {args.max_per_group} per {args.group_column}"
            if args.max_per_group is not None
            else ""
        )
        print(f"\n{len(picks)} picks by {order}{cap}:\n")
        print(picks.to_string(index=False))
        return 0
    print(f"\ntop {len(top)} by {order}:\n")
    print(top.to_string(index=False))
    return 0


def main_train() -> None:
    import sys

    sys.exit(_main_train())


def main_predict() -> None:
    import sys

    sys.exit(_main_predict())
