"""Sweep harness: one TOML defines a *grid* (and/or a random search)
of experiments.

Up to now experiments were written one config file at a time. A sweep
config declares ranges instead — several label cells, a model-parameter
grid, alternative feature sets, several seeds — and the harness expands
the cartesian product into ordinary `ExperimentConfig`s and runs each
one through the standard runner (`vml-sweep experiments/sweeps/x.toml`).

Three search styles compose:

- `[grid]`: explicit candidate lists, full cartesian product — right for
  few, coarse axes (class_weight, a feature axis).
- `[[sets]]`: whole parameter dictionaries taken *as a unit* — the
  natural follow-up to a wide search: take its top candidates and
  re-run them across seeds, feature sets, label cells, or a further
  `[grid]` / `[random]` over parameters the sets leave open. A parameter
  appears in at most one of `[model]`, `[grid]`, `[random]`, `[[sets]]`.
- `[random]` + `n_samples`: distributions sampled jointly — right for
  the wide continuous surfaces (learning rate, regularization) where a
  grid either misses or explodes. Each spec is `{low, high}` (uniform;
  `log = true` for log-uniform — scale parameters live on a log scale;
  `int = true` for integers) or `{choices = [...]}`. Sampling is a pure
  function of `search_seed` and the sweep content, so an expansion is
  reproducible and `--dry-run` shows exactly what will run. Random
  draws cross with the grid and every other axis; `max_runs` still
  caps the total.

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

import hashlib
import itertools
import json
import re
import tomllib
import traceback
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd

from eval.metrics import threshold_tag
from harness.calibration import (
    CALIBRATION_METHODS,
    DEFAULT_CALIBRATION_MIN_ROWS,
)
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
from models.registry import model_target

#: hard default ceiling on expanded runs — a sweep that wants more must
#: say so in its own file (max_runs), so trial-count inflation is always
#: an explicit, logged decision
DEFAULT_MAX_RUNS = 200

_SWEEP_REQUIRED = ("dataset_version", "scheme", "cells", "model")

_SWEEP_ALLOWED = frozenset(
    {
        "name",
        "dataset_version",
        "scheme",
        "folds",
        "cells",
        "model",
        "grid",
        "sets",
        "random",
        "n_samples",
        "search_seed",
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
        "calibration",
        "calibration_min_rows",
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
    #: (horizon_years, label, eval_label) cells to sweep — the
    #: multi-label axis; eval_label is "" except for continuous-target
    #: model sweeps (the regression reframe)
    cells: tuple[tuple[int, str, str], ...]
    model_name: str
    #: params fixed for every run in the sweep ([model] minus name)
    base_params: dict = field(default_factory=dict)
    #: param name -> candidate values ([grid]); cartesian product
    grid: dict[str, tuple] = field(default_factory=dict)
    #: whole parameter dictionaries ([[sets]]), each a unit — the
    #: param-set axis, crossed with [grid] / [random] and every other
    #: axis (empty: one implicit empty set)
    param_sets: tuple[dict, ...] = ()
    #: param name -> canonical distribution spec ([random]); one joint
    #: draw per sample, crossed with the grid and every other axis
    random: dict[str, dict] = field(default_factory=dict)
    #: how many joint draws [random] contributes (required with [random])
    n_samples: int = 0
    #: RNG seed the draws are a pure function of (config-content seed,
    #: distinct from the model seeds axis)
    search_seed: int = 0
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
    #: prequential calibration applied to every expanded run ("" = off)
    calibration: str = ""
    calibration_min_rows: int = DEFAULT_CALIBRATION_MIN_ROWS

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
            extra = sorted(set(c) - {"horizon_years", "label", "eval_label"})
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
            eval_label = str(c.get("eval_label", ""))
            if eval_label:
                if eval_label == label:
                    raise ConfigError(
                        f"sweep config {source}: cell eval_label equals "
                        f"label ({label!r}); eval_label is the binary cell "
                        "a continuous-target run is measured against"
                    )
                ev_horizon = infer_horizon_years(eval_label)
                if ev_horizon is not None and ev_horizon != horizon:
                    raise ConfigError(
                        f"sweep config {source}: cell eval_label "
                        f"{eval_label!r} is a {ev_horizon}y label but the "
                        f"cell horizon is {horizon}y"
                    )
            cells.append((horizon, label, eval_label))
        if len(set(cells)) != len(cells):
            raise ConfigError(f"sweep config {source}: duplicate [[cells]] entries")

        model = raw["model"]
        if not isinstance(model, dict) or "name" not in model:
            raise ConfigError(
                f"sweep config {source}: [model] must be a table with a name"
            )
        base_params = {k: v for k, v in model.items() if k != "name"}

        # fail the whole sweep now rather than every expanded run later:
        # continuous-target models need each cell's binary eval_label
        if model_target(str(model["name"])) == "continuous":
            bad = [label for _, label, ev in cells if not ev]
            if bad:
                raise ConfigError(
                    f"sweep config {source}: model {model['name']!r} trains "
                    f"on continuous targets, but cells {bad} set no "
                    "eval_label (the binary cell the ranking is measured "
                    "against)"
                )
        else:
            bad = [ev for _, _, ev in cells if ev]
            if bad:
                raise ConfigError(
                    f"sweep config {source}: eval_label is only meaningful "
                    f"for continuous-target models; {model['name']!r} is "
                    "evaluated on its own label"
                )

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
            if any(isinstance(v, dict) for v in values):
                raise ConfigError(
                    f"sweep config {source}: grid.{key} holds tables, not "
                    "candidate values. Whole parameter dictionaries belong "
                    "in a top-level `sets` — in TOML a bare `sets = [...]` "
                    "written below a [grid] header lands inside [grid]; "
                    "move it above the first table header or use [[sets]]"
                )
            if key in base_params:
                raise ConfigError(
                    f"sweep config {source}: {key!r} is both fixed in [model] "
                    "and swept in [grid]"
                )
            grid[key] = tuple(values)

        sets_raw = raw.get("sets", [])
        if not isinstance(sets_raw, list) or not all(
            isinstance(s, dict) for s in sets_raw
        ):
            raise ConfigError(
                f"sweep config {source}: [[sets]] must be an array of "
                "tables, each one whole parameter dictionary"
            )
        param_sets: list[dict] = []
        for i, entry in enumerate(sets_raw):
            if not entry:
                raise ConfigError(
                    f"sweep config {source}: [[sets]] entry {i} is empty"
                )
            fixed = sorted(set(entry) & set(base_params))
            if fixed:
                raise ConfigError(
                    f"sweep config {source}: {fixed} both fixed in [model] "
                    f"and given in [[sets]] entry {i}"
                )
            swept = sorted(set(entry) & set(grid))
            if swept:
                raise ConfigError(
                    f"sweep config {source}: {swept} both swept in [grid] "
                    f"and given in [[sets]] entry {i}; a parameter belongs "
                    "to one axis"
                )
            param_sets.append(dict(entry))
        canon = [json.dumps(s, sort_keys=True) for s in param_sets]
        if len(set(canon)) != len(canon):
            raise ConfigError(f"sweep config {source}: duplicate [[sets]] entries")
        set_keys = set().union(*param_sets) if param_sets else set()

        random_raw = raw.get("random", {})
        if not isinstance(random_raw, dict):
            raise ConfigError(f"sweep config {source}: [random] must be a table")
        random: dict[str, dict] = {}
        for key, spec in random_raw.items():
            if key in base_params or key in grid or key in set_keys:
                raise ConfigError(
                    f"sweep config {source}: {key!r} is both in [random] and "
                    "fixed/swept elsewhere"
                )
            random[key] = _parse_random_spec(key, spec, source)
        n_samples = int(raw.get("n_samples", 0))
        if random and n_samples < 1:
            raise ConfigError(
                f"sweep config {source}: [random] requires n_samples >= 1 "
                "(how many joint draws to run)"
            )
        if n_samples and not random:
            raise ConfigError(
                f"sweep config {source}: n_samples is set but there is no "
                "[random] table to sample from"
            )

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

        calibration = str(raw.get("calibration", ""))
        if calibration and calibration not in CALIBRATION_METHODS:
            raise ConfigError(
                f"sweep config {source}: calibration must be one of "
                f"{list(CALIBRATION_METHODS)} or absent (off), "
                f"got {calibration!r}"
            )
        if "calibration_min_rows" in raw and not calibration:
            raise ConfigError(
                f"sweep config {source}: calibration_min_rows is set but "
                "calibration is off"
            )
        if calibration and model_target(str(model["name"])) == "continuous":
            raise ConfigError(
                f"sweep config {source}: calibration applies to "
                f"probabilistic classifiers; {model['name']!r} scores are "
                "predicted returns, not probabilities"
            )

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

        sweep = cls(
            name=str(raw.get("name", "")),
            dataset_version=str(raw["dataset_version"]),
            scheme=str(raw["scheme"]),
            cells=tuple(cells),
            model_name=str(model["name"]),
            base_params=base_params,
            grid=grid,
            param_sets=tuple(param_sets),
            random=random,
            n_samples=n_samples,
            search_seed=int(raw.get("search_seed", 0)),
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
            calibration=calibration,
            calibration_min_rows=int(
                raw.get("calibration_min_rows", DEFAULT_CALIBRATION_MIN_ROWS)
            ),
        )
        if not sweep.name:
            sweep = replace(sweep, name=sweep.derived_name())
        return sweep

    def derived_name(self) -> str:
        """Default sweep name: `{model}_sweep_{features}_{labels}_{hash}`.

        Same rationale as `ExperimentConfig.derived_name`: the hash is
        over the sweep's content (everything but the name), so a copied
        sweep file with edited values gets a fresh name — and with it
        fresh run names and a fresh `reports/sweeps/` directory —
        instead of overwriting the original's.
        """
        if self.feature_specs:
            if len(self.feature_specs) == 1:
                spec = self.feature_specs[0]
                tags = list(spec.groups) + [
                    f.replace("/", "-") for f in spec.families
                ]
                feat = "-".join(tags) if tags else "cols"
            else:
                feat = f"{len(self.feature_specs)}fs"
        elif len(self.feature_sets) == 1:
            feat = "-".join(self.feature_sets[0].groups) or "cols"
        else:
            feat = f"{len(self.feature_sets)}fs"
        if len(self.cells) == 1:
            label = self.cells[0][1].removeprefix("label_")
        else:
            label = f"{len(self.cells)}cells"
        return f"{self.model_name}_sweep_{feat}_{label}_{self.identity_hash}"

    @property
    def identity_hash(self) -> str:
        """Hash of the sweep's content with the name left out — what the
        derived default name embeds."""
        if self.feature_specs:
            features = [spec.to_table() for spec in self.feature_specs]
        else:
            features = [
                {
                    "groups": list(fs.groups),
                    "columns": None if fs.columns is None else list(fs.columns),
                    "exclude": list(fs.exclude),
                }
                for fs in self.feature_sets
            ]
        payload = {
            "dataset_version": self.dataset_version,
            "scheme": self.scheme,
            # eval_label-free cells keep their historical 2-element shape
            # so existing sweeps keep their hashes (and derived names)
            "cells": [
                [h, label] if not ev else [h, label, ev]
                for h, label, ev in self.cells
            ],
            "model_name": self.model_name,
            "base_params": self.base_params,
            "grid": {k: list(v) for k, v in self.grid.items()},
            "features": features,
            "folds": self.folds if self.folds == "all" else list(self.folds),
            "seeds": list(self.seeds),
            "top_k": list(self.top_k),
            "score_thresholds": list(self.score_thresholds),
            "precision_targets": list(self.precision_targets),
            "rank_metric": self.rank_metric,
        }
        # like the other optional axes, only present when used, so
        # set-free sweeps keep their hashes (and derived names)
        if self.param_sets:
            payload["sets"] = list(self.param_sets)
        if self.random:
            payload["random"] = {k: self.random[k] for k in sorted(self.random)}
            payload["n_samples"] = self.n_samples
            payload["search_seed"] = self.search_seed
        if self.calibration:
            payload["calibration"] = self.calibration
            payload["calibration_min_rows"] = self.calibration_min_rows
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:8]

    # ------------------------------------------------------------------

    @property
    def n_feature_variants(self) -> int:
        """Length of the sweep's feature axis, whichever style defines it."""
        return len(self.feature_specs) or len(self.feature_sets)

    @property
    def n_param_sets(self) -> int:
        """Length of the param-set axis (1 when no [[sets]] are given)."""
        return max(len(self.param_sets), 1)

    def _feature_fields(self, fs) -> dict:
        """ExperimentConfig field fragment for one feature-axis entry."""
        if isinstance(fs, FeatureSpec):
            return {"features": fs}
        return {
            "feature_groups": fs.groups,
            "feature_columns": fs.columns,
            "exclude_feature_columns": fs.exclude,
        }

    def sample_draws(self) -> list[dict]:
        """The [random] table's joint draws — a pure function of the
        sweep content and `search_seed`, so expansion is reproducible.
        One dict per sample; empty specs yield the single empty draw."""
        if not self.random:
            return [{}]
        rng = np.random.default_rng(self.search_seed)
        draws = []
        for _ in range(self.n_samples):
            draw = {}
            for key in sorted(self.random):
                draw[key] = _sample_param(self.random[key], rng)
            draws.append(draw)
        return draws

    def expand(self) -> list["SweepRun"]:
        """The full cartesian product: cells × feature sets × param sets
        × grid × random draws × seeds, each as an ordinary
        ExperimentConfig with a deterministic name."""
        grid_keys = sorted(self.grid)
        combos = [
            dict(zip(grid_keys, values))
            for values in itertools.product(*(self.grid[k] for k in grid_keys))
        ]
        draws = self.sample_draws()
        feature_axis = self.feature_specs or self.feature_sets
        set_axis = self.param_sets or ({},)
        runs: list[SweepRun] = []
        for (
            (horizon, label, eval_label),
            (fs_idx, fs),
            (set_idx, params),
            combo,
            (draw_idx, draw),
            seed,
        ) in itertools.product(
            self.cells,
            enumerate(feature_axis),
            enumerate(set_axis),
            combos,
            enumerate(draws),
            self.seeds,
        ):
            config = ExperimentConfig(
                name="",  # filled below, needs the full config for the hash
                dataset_version=self.dataset_version,
                scheme=self.scheme,
                horizon_years=horizon,
                label=label,
                eval_label=eval_label,
                model_name=self.model_name,
                model_params={**self.base_params, **params, **combo, **draw},
                **self._feature_fields(fs),
                folds=self.folds,
                seed=seed,
                top_k=self.top_k,
                score_thresholds=self.score_thresholds,
                precision_targets=self.precision_targets,
                calibration=self.calibration,
                calibration_min_rows=self.calibration_min_rows,
            )
            name = self._run_name(
                label, fs_idx, set_idx, combo, draw_idx, seed, config
            )
            runs.append(
                SweepRun(
                    config=replace(config, name=name),
                    label=label,
                    horizon_years=horizon,
                    feature_set_index=fs_idx,
                    grid_params=combo,
                    sampled_params=draw,
                    seed=seed,
                    param_set_index=set_idx,
                    set_params=dict(params),
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
        self, label: str, fs_idx: int, set_idx: int, combo: dict,
        draw_idx: int, seed: int, config: ExperimentConfig,
    ) -> str:
        parts = [self.name, label]
        if self.n_feature_variants > 1:
            parts.append(f"fs{fs_idx}")
        if self.n_param_sets > 1:
            # a set is a whole dictionary — its index names the run; the
            # dictionary itself is in the summary's `set_params` column
            parts.append(f"set{set_idx}")
        for key in sorted(combo):
            parts.append(f"{_sanitize(key)}-{_sanitize(combo[key])}")
        if self.random:
            # sampled values would make unreadable names; the draw index
            # is stable (sampling is deterministic) and the summary CSV
            # carries the actual values
            parts.append(f"r{draw_idx}")
        if len(self.seeds) > 1:
            parts.append(f"s{seed}")
        name = "__".join(parts)
        if len(name) > 120:
            name = f"{name[:96]}--{config.config_hash[:8]}"
        return name


@dataclass(frozen=True)
class SweepRun:
    """One expanded search point (the config plus its sweep coordinates)."""

    config: ExperimentConfig
    label: str
    horizon_years: int
    feature_set_index: int
    grid_params: dict
    seed: int
    #: the [random] draw this run carries (empty for pure-grid sweeps)
    sampled_params: dict = field(default_factory=dict)
    #: index into the sweep's [[sets]] (0 when the sweep has none)
    param_set_index: int = 0
    #: the [[sets]] entry this run took as a unit ({} when none)
    set_params: dict = field(default_factory=dict)


def _sanitize(value) -> str:
    return re.sub(r"[^A-Za-z0-9._=-]+", "-", str(value)).strip("-") or "x"


def _peak_rss_note() -> str:
    """Process peak-RSS suffix for sweep progress lines (a memory
    regression should be visible run by run, not discovered as an OOM
    kill hours in). Empty where the resource module is unavailable."""
    try:
        import resource
        import sys

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (ImportError, OSError):  # pragma: no cover - non-Unix
        return ""
    # ru_maxrss is KB on Linux, bytes on macOS
    divisor = 1e9 if sys.platform == "darwin" else 1e6
    return f"  (peak RSS {peak / divisor:.1f} GB)"


_RANDOM_SPEC_KEYS = frozenset({"low", "high", "log", "int", "choices"})


def _parse_random_spec(key: str, spec, source: str) -> dict:
    """Normalize one [random] entry into its canonical form (what the
    identity hash embeds): `{choices: [...]}` or
    `{low, high, log: bool, int: bool}`."""
    if not isinstance(spec, dict):
        raise ConfigError(
            f"sweep config {source}: random.{key} must be a table "
            "({low, high[, log][, int]} or {choices})"
        )
    unknown = sorted(set(spec) - _RANDOM_SPEC_KEYS)
    if unknown:
        raise ConfigError(
            f"sweep config {source}: random.{key} has unknown keys {unknown}"
        )
    if "choices" in spec:
        extra = sorted(set(spec) - {"choices"})
        if extra:
            raise ConfigError(
                f"sweep config {source}: random.{key} mixes choices with "
                f"{extra}"
            )
        choices = spec["choices"]
        if not isinstance(choices, list) or not choices:
            raise ConfigError(
                f"sweep config {source}: random.{key}.choices must be a "
                "non-empty list"
            )
        return {"choices": list(choices)}
    if "low" not in spec or "high" not in spec:
        raise ConfigError(
            f"sweep config {source}: random.{key} needs low and high "
            "(or choices)"
        )
    low, high = spec["low"], spec["high"]
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               for v in (low, high)):
        raise ConfigError(
            f"sweep config {source}: random.{key} low/high must be numbers"
        )
    if not low < high:
        raise ConfigError(
            f"sweep config {source}: random.{key} needs low < high, "
            f"got [{low}, {high}]"
        )
    log = bool(spec.get("log", False))
    as_int = bool(spec.get("int", False))
    if log and low <= 0:
        raise ConfigError(
            f"sweep config {source}: random.{key} is log-scaled, so low "
            f"must be > 0, got {low}"
        )
    if as_int and not (
        isinstance(low, int) and isinstance(high, int)
    ):
        raise ConfigError(
            f"sweep config {source}: random.{key} has int = true, so low "
            "and high must be integers"
        )
    return {"low": low, "high": high, "log": log, "int": as_int}


def _sample_param(spec: dict, rng: np.random.Generator):
    """One value from a canonical [random] spec. Floats are rounded to 6
    significant digits so configs/names/ledgers stay readable and the
    values round-trip exactly through JSON."""
    if "choices" in spec:
        return spec["choices"][int(rng.integers(len(spec["choices"])))]
    low, high = spec["low"], spec["high"]
    if spec["int"] and not spec["log"]:
        return int(rng.integers(low, high + 1))  # inclusive, uniform
    if spec["log"]:
        value = float(np.exp(rng.uniform(np.log(low), np.log(high))))
    else:
        value = float(rng.uniform(low, high))
    if spec["int"]:
        return int(np.clip(round(value), low, high))
    return float(f"{value:.6g}")


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
        print(f"[{i}/{len(runs)}] {run.config.name}{_peak_rss_note()}")
        outcome = {
            "run": run.config.name,
            "label": run.label,
            "eval_label": run.config.eval_label,
            "horizon_years": run.horizon_years,
            "feature_set": run.feature_set_index,
            "param_set": run.param_set_index,
            "set_params": run.set_params,
            "seed": run.seed,
            "grid_params": run.grid_params,
            "sampled_params": run.sampled_params,
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
                "eval_label": o["eval_label"],
                "horizon_years": o["horizon_years"],
                "feature_set": o["feature_set"],
                "param_set": o["param_set"],
                "set_params": json.dumps(o["set_params"], sort_keys=True),
                "seed": o["seed"],
                "grid_params": json.dumps(o["grid_params"], sort_keys=True),
                "sampled_params": json.dumps(
                    o["sampled_params"], sort_keys=True
                ),
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
    # trial accounting is per *evaluation* cell: a continuous-target run
    # counts against the binary eval_label cell it is measured on
    cells = sorted(
        {(o["horizon_years"], o["eval_label"] or o["label"]) for o in outcomes}
    )
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
    if sweep.param_sets:
        id_cols.insert(4, "param_set")
    if sweep.random:
        id_cols.append("sampled_params")
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
        *(
            [f"- parameter sets ({len(sweep.param_sets)}, each taken as a unit):"]
            + [
                f"  - `set{i}`: `{json.dumps(s, sort_keys=True)}`"
                for i, s in enumerate(sweep.param_sets)
            ]
            if sweep.param_sets
            else []
        ),
        *(
            [
                f"- random search: `{json.dumps(sweep.random, sort_keys=True)}` "
                f"— {sweep.n_samples} joint draws, search_seed "
                f"{sweep.search_seed} (deterministic)"
            ]
            if sweep.random
            else []
        ),
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
