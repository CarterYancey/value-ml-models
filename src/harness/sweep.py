"""Sweep harness: one TOML defines a *grid* of experiments.

Up to now experiments were written one config file at a time. A sweep
config declares ranges instead — several label cells, a model-parameter
grid, alternative feature sets, several seeds — and the harness expands
the cartesian product into ordinary `ExperimentConfig`s and runs each
one through the standard runner (`vml-sweep experiments/sweeps/x.toml`).

Nothing about the honesty machinery is bypassed:

- every expanded run goes through `run_experiment`, so it is logged to
  the append-only results store (failures included) and every run's
  config hash counts in the per-cell `configurations_tried` ledger;
- splits are applied with STANDARD access only — the sealed holdout and
  diagnostic schemes are structurally out of a sweep's reach;
- the sweep summary states how many configurations the sweep tried, and
  ranking by the sweep's `rank_metric` is *model selection on
  walk-forward folds* — the winner's numbers are selection-biased and
  are never a final result (the sealed holdout exists for that).

Per-run reports land in `reports/sweeps/<sweep name>/`; the ranked
summary (markdown + CSV) lands next to them. Model bundles are not
saved by default (a wide sweep would write hundreds) — pass
`--save-models` / `models_dir=` and re-evaluate the winner, or simply
re-run its expanded config through `vml-run`.
"""

from __future__ import annotations

import itertools
import json
import re
import tomllib
import traceback
from dataclasses import dataclass, field, replace
from pathlib import Path

import pandas as pd

from eval.metrics import threshold_tag
from harness.config import ExperimentConfig, FeatureSpec, infer_horizon_years
from harness.errors import ConfigError
from harness.report import _table
from harness.results import ResultsStore, git_sha
from harness.runner import (
    DEFAULT_DATA_ROOT,
    DEFAULT_REPORTS,
    DEFAULT_RESULTS,
    run_experiment,
)

#: hard default ceiling on expanded runs — a sweep that wants more must
#: say so in its own file (max_runs), so trial-count inflation is always
#: an explicit, logged decision
DEFAULT_MAX_RUNS = 200

_SWEEP_REQUIRED = ("name", "dataset_version", "scheme", "cells", "model")

_SWEEP_ALLOWED = frozenset(
    {
        "name",
        "dataset_version",
        "scheme",
        "folds",
        "cells",
        "model",
        "grid",
        "feature_groups",
        "feature_columns",
        "exclude_feature_columns",
        "feature_sets",
        "features",
        "seeds",
        "top_k",
        "score_thresholds",
        "precision_targets",
        "rank_metric",
        "max_runs",
    }
)


@dataclass(frozen=True)
class FeatureSet:
    groups: tuple[str, ...]
    columns: tuple[str, ...] | None = None
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class SweepConfig:
    """A declarative grid of experiments sharing one dataset/scheme."""

    name: str
    dataset_version: str
    scheme: str
    #: (horizon_years, label) cells to sweep — the multi-label axis
    cells: tuple[tuple[int, str], ...]
    model_name: str
    #: params fixed for every run in the sweep ([model] minus name)
    base_params: dict = field(default_factory=dict)
    #: param name -> candidate values ([grid]); cartesian product
    grid: dict[str, tuple] = field(default_factory=dict)
    feature_sets: tuple[FeatureSet, ...] = ()
    #: hierarchical selection(s) (top-level `features`: one `[features]`
    #: table or a `[[features]]` array forming the feature axis) —
    #: mutually exclusive with feature_sets / the legacy top-level keys
    feature_specs: tuple[FeatureSpec, ...] = ()
    folds: tuple[int, ...] | str = "all"
    seeds: tuple[int, ...] = (0,)
    top_k: tuple[int, ...] = (20, 50)
    score_thresholds: tuple[float, ...] = ()
    precision_targets: tuple[float, ...] = ()
    #: pooled metric the summary ranks by; default: recall at the first
    #: precision floor when floors are set, else precision at the first K
    rank_metric: str = ""
    max_runs: int = DEFAULT_MAX_RUNS

    @classmethod
    def from_file(cls, path: str | Path) -> "SweepConfig":
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"cannot read sweep config {path}: {exc}") from exc
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<dict>") -> "SweepConfig":
        unknown = sorted(set(raw) - _SWEEP_ALLOWED)
        if unknown:
            raise ConfigError(f"sweep config {source} has unknown fields: {unknown}")
        missing = [k for k in _SWEEP_REQUIRED if k not in raw]
        if missing:
            raise ConfigError(
                f"sweep config {source} lacks required fields: {missing}"
            )

        cells_raw = raw["cells"]
        if not isinstance(cells_raw, list) or not cells_raw:
            raise ConfigError(
                f"sweep config {source}: [[cells]] must list at least one "
                "{horizon_years, label} table"
            )
        cells = []
        for c in cells_raw:
            if not isinstance(c, dict) or "label" not in c:
                raise ConfigError(
                    f"sweep config {source}: each [[cells]] entry needs a "
                    f"label (and horizon_years when the label carries no "
                    f"horizon token), got {c!r}"
                )
            extra = sorted(set(c) - {"horizon_years", "label"})
            if extra:
                raise ConfigError(
                    f"sweep config {source}: [[cells]] entry has unknown "
                    f"fields {extra}"
                )
            label = str(c["label"])
            inferred = infer_horizon_years(label)
            if "horizon_years" in c:
                horizon = int(c["horizon_years"])
                if inferred is not None and inferred != horizon:
                    raise ConfigError(
                        f"sweep config {source}: cell horizon_years = "
                        f"{horizon} contradicts label {label!r} (a "
                        f"{inferred}y label)"
                    )
            elif inferred is None:
                raise ConfigError(
                    f"sweep config {source}: cell label {label!r} carries "
                    "no `{H}y` horizon token, so horizon_years must be set"
                )
            else:
                horizon = inferred
            cells.append((horizon, label))
        if len(set(cells)) != len(cells):
            raise ConfigError(f"sweep config {source}: duplicate [[cells]] entries")

        model = raw["model"]
        if not isinstance(model, dict) or "name" not in model:
            raise ConfigError(
                f"sweep config {source}: [model] must be a table with a name"
            )
        base_params = {k: v for k, v in model.items() if k != "name"}

        grid_raw = raw.get("grid", {})
        if not isinstance(grid_raw, dict):
            raise ConfigError(f"sweep config {source}: [grid] must be a table")
        grid: dict[str, tuple] = {}
        for key, values in grid_raw.items():
            if not isinstance(values, list) or not values:
                raise ConfigError(
                    f"sweep config {source}: grid.{key} must be a non-empty "
                    "list of candidate values"
                )
            if key in base_params:
                raise ConfigError(
                    f"sweep config {source}: {key!r} is both fixed in [model] "
                    "and swept in [grid]"
                )
            grid[key] = tuple(values)

        legacy_top = [
            k
            for k in (
                "feature_groups", "feature_columns",
                "exclude_feature_columns",
            )
            if k in raw
        ]
        feature_specs: tuple[FeatureSpec, ...] = ()
        if "features" in raw:
            others = legacy_top + (
                ["feature_sets"] if "feature_sets" in raw else []
            )
            if others:
                raise ConfigError(
                    f"sweep config {source}: `features` can't be mixed "
                    f"with {others}; use one selection style"
                )
            f_raw = raw["features"]
            # one [features] table, or a [[features]] array of tables
            # forming the feature axis of the sweep
            if isinstance(f_raw, dict):
                f_raw = [f_raw]
            if not isinstance(f_raw, list) or not f_raw:
                raise ConfigError(
                    f"sweep config {source}: `features` must be a "
                    "[features] table or a [[features]] array of tables"
                )
            feature_specs = tuple(
                FeatureSpec.from_table(entry, source) for entry in f_raw
            )

        fs_raw = raw.get("feature_sets")
        if fs_raw is not None:
            if legacy_top:
                raise ConfigError(
                    f"sweep config {source}: give either top-level "
                    f"{legacy_top} or [[feature_sets]], not both"
                )
            if not isinstance(fs_raw, list) or not fs_raw:
                raise ConfigError(
                    f"sweep config {source}: [[feature_sets]] must list at "
                    "least one {groups[, columns][, exclude]} table"
                )
            feature_sets = []
            for fs in fs_raw:
                extra = sorted(set(fs) - {"groups", "columns", "exclude"})
                if extra or "groups" not in fs:
                    raise ConfigError(
                        f"sweep config {source}: each [[feature_sets]] entry "
                        f"needs groups (and optionally columns, exclude), "
                        f"got {fs!r}"
                    )
                feature_sets.append(
                    FeatureSet(
                        groups=tuple(fs["groups"]),
                        columns=(
                            tuple(fs["columns"]) if "columns" in fs else None
                        ),
                        exclude=tuple(fs.get("exclude", ())),
                    )
                )
        elif feature_specs:
            feature_sets = []
        else:
            feature_sets = [
                FeatureSet(
                    groups=tuple(raw.get("feature_groups", ())),
                    columns=(
                        tuple(raw["feature_columns"])
                        if "feature_columns" in raw
                        else None
                    ),
                    exclude=tuple(raw.get("exclude_feature_columns", ())),
                )
            ]

        folds = raw.get("folds", "all")
        if folds != "all":
            folds = tuple(int(f) for f in folds)
        seeds = tuple(int(s) for s in raw.get("seeds", (0,)))
        if not seeds or len(set(seeds)) != len(seeds):
            raise ConfigError(f"sweep config {source}: seeds must be distinct")

        top_k = tuple(int(k) for k in raw.get("top_k", (20, 50)))
        precision_targets = tuple(
            float(p) for p in raw.get("precision_targets", ())
        )
        rank_metric = str(raw.get("rank_metric", ""))
        if not rank_metric:
            rank_metric = (
                f"recall_at_prec_{threshold_tag(precision_targets[0])}"
                if precision_targets
                else f"precision_at_{top_k[0]}"
            )

        return cls(
            name=str(raw["name"]),
            dataset_version=str(raw["dataset_version"]),
            scheme=str(raw["scheme"]),
            cells=tuple(cells),
            model_name=str(model["name"]),
            base_params=base_params,
            grid=grid,
            feature_sets=tuple(feature_sets),
            feature_specs=feature_specs,
            folds=folds,
            seeds=seeds,
            top_k=top_k,
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
            precision_targets=precision_targets,
            rank_metric=rank_metric,
            max_runs=int(raw.get("max_runs", DEFAULT_MAX_RUNS)),
        )

    # ------------------------------------------------------------------

    @property
    def n_feature_variants(self) -> int:
        """Length of the sweep's feature axis, whichever style defines it."""
        return len(self.feature_specs) or len(self.feature_sets)

    def _feature_fields(self, fs) -> dict:
        """ExperimentConfig field fragment for one feature-axis entry."""
        if isinstance(fs, FeatureSpec):
            return {"features": fs}
        return {
            "feature_groups": fs.groups,
            "feature_columns": fs.columns,
            "exclude_feature_columns": fs.exclude,
        }

    def expand(self) -> list["SweepRun"]:
        """The full cartesian product: cells × feature sets × grid × seeds,
        each as an ordinary ExperimentConfig with a deterministic name."""
        grid_keys = sorted(self.grid)
        combos = [
            dict(zip(grid_keys, values))
            for values in itertools.product(*(self.grid[k] for k in grid_keys))
        ]
        feature_axis = self.feature_specs or self.feature_sets
        runs: list[SweepRun] = []
        for (horizon, label), (fs_idx, fs), combo, seed in itertools.product(
            self.cells,
            enumerate(feature_axis),
            combos,
            self.seeds,
        ):
            config = ExperimentConfig(
                name="",  # filled below, needs the full config for the hash
                dataset_version=self.dataset_version,
                scheme=self.scheme,
                horizon_years=horizon,
                label=label,
                model_name=self.model_name,
                model_params={**self.base_params, **combo},
                **self._feature_fields(fs),
                folds=self.folds,
                seed=seed,
                top_k=self.top_k,
                score_thresholds=self.score_thresholds,
                precision_targets=self.precision_targets,
            )
            name = self._run_name(label, fs_idx, combo, seed, config)
            runs.append(
                SweepRun(
                    config=replace(config, name=name),
                    label=label,
                    horizon_years=horizon,
                    feature_set_index=fs_idx,
                    grid_params=combo,
                    seed=seed,
                )
            )
        names = [r.config.name for r in runs]
        if len(set(names)) != len(names):  # pragma: no cover - defensive
            raise ConfigError(
                f"sweep {self.name}: expanded run names collide; "
                "shorten grid values or rename the sweep"
            )
        if len(runs) > self.max_runs:
            raise ConfigError(
                f"sweep {self.name} expands to {len(runs)} runs, over its "
                f"max_runs = {self.max_runs}. Every run counts in the trial "
                "ledger — raise max_runs in the sweep file only if you mean "
                "to try that many configurations."
            )
        return runs

    def _run_name(
        self, label: str, fs_idx: int, combo: dict, seed: int,
        config: ExperimentConfig,
    ) -> str:
        parts = [self.name, label]
        if self.n_feature_variants > 1:
            parts.append(f"fs{fs_idx}")
        for key in sorted(combo):
            parts.append(f"{_sanitize(key)}-{_sanitize(combo[key])}")
        if len(self.seeds) > 1:
            parts.append(f"s{seed}")
        name = "__".join(parts)
        if len(name) > 120:
            name = f"{name[:96]}--{config.config_hash[:8]}"
        return name


@dataclass(frozen=True)
class SweepRun:
    """One expanded grid point (the config plus its sweep coordinates)."""

    config: ExperimentConfig
    label: str
    horizon_years: int
    feature_set_index: int
    grid_params: dict
    seed: int


def _sanitize(value) -> str:
    return re.sub(r"[^A-Za-z0-9._=-]+", "-", str(value)).strip("-") or "x"


# ----------------------------------------------------------------------


def run_sweep(
    sweep: SweepConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_REPORTS,
    sweep_config_path: str = "",
    models_dir: str | Path | None = None,
) -> dict:
    """Run every expanded config; one run failing never stops the sweep.

    Returns {"runs": [per-run dicts], "summary_md": Path, "summary_csv":
    Path, "n_failed": int}. Each run is logged to the results store by
    `run_experiment` itself (completed or failed), so the trial ledger
    sees the whole sweep regardless of what this function returns.
    """
    runs = sweep.expand()
    sweep_reports = Path(reports_dir) / "sweeps" / sweep.name
    outcomes: list[dict] = []
    for i, run in enumerate(runs, start=1):
        print(f"[{i}/{len(runs)}] {run.config.name}")
        outcome = {
            "run": run.config.name,
            "label": run.label,
            "horizon_years": run.horizon_years,
            "feature_set": run.feature_set_index,
            "seed": run.seed,
            "grid_params": run.grid_params,
            "config_hash": run.config.config_hash,
        }
        try:
            summary = run_experiment(
                run.config,
                data_root=data_root,
                results_path=results_path,
                reports_dir=sweep_reports,
                config_path=(
                    f"{sweep_config_path}#{run.config.name}"
                    if sweep_config_path
                    else run.config.name
                ),
                models_dir=models_dir,
            )
            outcome.update(
                status="completed",
                run_id=summary["run_id"],
                report_path=summary["report_path"],
                pooled_metrics=summary["pooled_metrics"],
            )
        except Exception as exc:
            traceback.print_exc()
            outcome.update(
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
                pooled_metrics={},
            )
        outcomes.append(outcome)

    summary_md, summary_csv = _write_sweep_summary(
        sweep, outcomes, sweep_reports, results_path, sweep_config_path
    )
    return {
        "runs": outcomes,
        "summary_md": summary_md,
        "summary_csv": summary_csv,
        "n_failed": sum(1 for o in outcomes if o["status"] == "failed"),
    }


def _write_sweep_summary(
    sweep: SweepConfig,
    outcomes: list[dict],
    sweep_reports: Path,
    results_path: str | Path,
    sweep_config_path: str,
) -> tuple[Path, Path]:
    """Ranked summary: markdown for reading, CSV with every pooled metric."""
    sweep_reports.mkdir(parents=True, exist_ok=True)
    store = ResultsStore(results_path)

    rows = []
    for o in outcomes:
        rows.append(
            {
                "run": o["run"],
                "status": o["status"],
                "label": o["label"],
                "horizon_years": o["horizon_years"],
                "feature_set": o["feature_set"],
                "seed": o["seed"],
                "grid_params": json.dumps(o["grid_params"], sort_keys=True),
                "config_hash": o["config_hash"],
                **o["pooled_metrics"],
            }
        )
    df = pd.DataFrame(rows)
    if sweep.rank_metric in df.columns:
        df = df.sort_values(
            sweep.rank_metric, ascending=False, na_position="last"
        ).reset_index(drop=True)

    csv_path = sweep_reports / f"{sweep.name}_summary.csv"
    df.to_csv(csv_path, index=False)

    n_failed = sum(1 for o in outcomes if o["status"] == "failed")
    cells = sorted({(o["horizon_years"], o["label"]) for o in outcomes})
    tried_lines = [
        f"- `{label}` ({horizon}y): "
        f"{store.configurations_tried(sweep.dataset_version, sweep.scheme, horizon, label)} "
        "configurations ever tried against this cell (append-only ledger, "
        "failures included)"
        for horizon, label in cells
    ]

    # compact reading table: identity + the metrics that answer the
    # precision-first question; the CSV carries every pooled metric
    metric_cols = [sweep.rank_metric] if sweep.rank_metric in df.columns else []
    for p in sweep.precision_targets:
        for prefix in ("recall_at_prec_", "n_at_prec_", "thr_for_prec_"):
            col = f"{prefix}{threshold_tag(p)}"
            if col in df.columns and col not in metric_cols:
                metric_cols.append(col)
    for extra in (
        f"precision_at_{sweep.top_k[0]}",
        f"recall_at_{sweep.top_k[0]}",
        "pr_auc",
        "base_rate",
    ):
        if extra in df.columns and extra not in metric_cols:
            metric_cols.append(extra)
    id_cols = ["run", "status", "label", "seed", "grid_params"]
    if sweep.n_feature_variants > 1:
        id_cols.insert(3, "feature_set")
    table_df = df[[c for c in id_cols + metric_cols if c in df.columns]]

    lines = [
        f"# Sweep summary — {sweep.name}",
        "",
        f"- sweep config: `{sweep_config_path or '<inline>'}`",
        f"- dataset version: `{sweep.dataset_version}` (pinned, immutable)",
        f"- scheme: `{sweep.scheme}`, folds: `{sweep.folds}`, git `{git_sha()}`",
        f"- model family: `{sweep.model_name}`, fixed params "
        f"`{json.dumps(sweep.base_params, sort_keys=True)}`",
        f"- grid: `{json.dumps({k: list(v) for k, v in sweep.grid.items()}, sort_keys=True)}`",
        f"- expanded runs: {len(outcomes)} ({n_failed} failed), "
        f"seeds {list(sweep.seeds)}",
        f"- ranked by pooled `{sweep.rank_metric}` (higher is better)",
        "",
        "**This ranking is model selection on walk-forward folds.** The "
        "winner's numbers are selection-biased by every configuration "
        "tried below (and before); they are candidates for the sealed "
        "holdout, never final results. Pooled numbers here are for "
        "ranking only — the per-run reports in this directory carry the "
        "era-sliced tables that an honest read requires.",
        "",
        "## Trial ledger",
        "",
        *tried_lines,
        "",
        "## Ranked runs (pooled over folds)",
        "",
        _table(table_df),
        "",
    ]
    failed = [o for o in outcomes if o["status"] == "failed"]
    if failed:
        lines += ["## Failures", ""]
        lines += [f"- `{o['run']}`: {o['error']}" for o in failed]
        lines += [""]
    lines += [
        f"Full pooled metrics for every run: `{csv_path.name}`. Per-run "
        "reports (era slices, crash eras, calibration, baselines): "
        "`<run name>.md` in this directory.",
        "",
    ]
    md_path = sweep_reports / f"{sweep.name}_summary.md"
    md_path.write_text("\n".join(lines))
    return md_path, csv_path


# ----------------------------------------------------------------------


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Expand a sweep config into a grid of experiments and "
        "run them all through the standard harness."
    )
    parser.add_argument("config", help="path to an experiments/sweeps/*.toml")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS))
    parser.add_argument(
        "--save-models",
        metavar="DIR",
        nargs="?",
        const="experiments/models",
        default=None,
        help="save a model bundle per run (off by default: wide sweeps "
        "write many bundles; re-run the winner through vml-run instead)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the expanded run names and exit without training",
    )
    args = parser.parse_args(argv)
    try:
        sweep = SweepConfig.from_file(args.config)
        if args.dry_run:
            for run in sweep.expand():
                print(run.config.name)
            return 0
        result = run_sweep(
            sweep,
            data_root=args.data_root,
            results_path=args.results,
            reports_dir=args.reports_dir,
            sweep_config_path=str(args.config),
            models_dir=args.save_models,
        )
    except Exception:
        traceback.print_exc()
        print("sweep FAILED")
        return 1
    n = len(result["runs"])
    print(
        f"sweep completed: {n - result['n_failed']}/{n} runs succeeded"
        + (f", {result['n_failed']} failed" if result["n_failed"] else "")
    )
    print(f"summary: {result['summary_md']}")
    return 1 if result["n_failed"] == n else 0


def main() -> None:
    import sys

    sys.exit(_main())
