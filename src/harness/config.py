"""Experiment config schema: one TOML file per experiment in `experiments/`.

A config pins everything needed to reproduce a run: dataset version,
scheme/folds/horizon, label column, feature-set selector (manifest groups,
optionally narrowed to explicit columns), model + params, seed. The
config's canonical-JSON SHA-256 is the identity logged with every run.

`EvalConfig` is the deliberately tiny companion for re-scoring a saved
model bundle (harness.evaluate): it may change how metrics are computed,
never what was trained or which rows are tested.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from harness.errors import ConfigError

_REQUIRED = ("name", "dataset_version", "scheme", "horizon_years", "label", "model")


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    dataset_version: str
    scheme: str
    horizon_years: int
    label: str
    model_name: str
    model_params: dict = field(default_factory=dict)
    #: manifest column groups to draw features from
    feature_groups: tuple[str, ...] = ()
    #: optional explicit subset of the selected groups' columns
    feature_columns: tuple[str, ...] | None = None
    #: "all" (every fold in split_folds for scheme+horizon) or explicit list
    folds: tuple[int, ...] | str = "all"
    seed: int = 0
    #: K values for precision@K / recall@K
    top_k: tuple[int, ...] = (20, 50)
    #: score thresholds for precision/recall over "score >= t" selections
    #: (empty = don't record threshold metrics)
    score_thresholds: tuple[float, ...] = ()

    @classmethod
    def from_file(cls, path: str | Path) -> "ExperimentConfig":
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"cannot read config {path}: {exc}") from exc
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<dict>") -> "ExperimentConfig":
        missing = [k for k in _REQUIRED if k not in raw]
        if missing:
            raise ConfigError(f"config {source} lacks required fields: {missing}")
        model = raw["model"]
        if not isinstance(model, dict) or "name" not in model:
            raise ConfigError(f"config {source}: [model] must be a table with a name")
        folds = raw.get("folds", "all")
        if folds != "all":
            folds = tuple(int(f) for f in folds)
        feature_columns = raw.get("feature_columns")
        if feature_columns is not None:
            feature_columns = tuple(feature_columns)
        return cls(
            name=raw["name"],
            dataset_version=raw["dataset_version"],
            scheme=raw["scheme"],
            horizon_years=int(raw["horizon_years"]),
            label=raw["label"],
            model_name=model["name"],
            model_params={k: v for k, v in model.items() if k != "name"},
            feature_groups=tuple(raw.get("feature_groups", ())),
            feature_columns=feature_columns,
            folds=folds,
            seed=int(raw.get("seed", 0)),
            top_k=tuple(int(k) for k in raw.get("top_k", (20, 50))),
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
        )

    def to_raw_dict(self) -> dict:
        """The config as the mapping `from_dict` accepts — the round-trip
        used to embed a train config inside a saved model bundle."""
        raw = {
            "name": self.name,
            "dataset_version": self.dataset_version,
            "scheme": self.scheme,
            "horizon_years": self.horizon_years,
            "label": self.label,
            "model": {"name": self.model_name, **self.model_params},
            "feature_groups": list(self.feature_groups),
            "folds": self.folds if self.folds == "all" else list(self.folds),
            "seed": self.seed,
            "top_k": list(self.top_k),
            "score_thresholds": list(self.score_thresholds),
        }
        if self.feature_columns is not None:
            raw["feature_columns"] = list(self.feature_columns)
        return raw

    def canonical_json(self) -> str:
        payload = {
            "name": self.name,
            "dataset_version": self.dataset_version,
            "scheme": self.scheme,
            "horizon_years": self.horizon_years,
            "label": self.label,
            "model_name": self.model_name,
            "model_params": self.model_params,
            "feature_groups": list(self.feature_groups),
            "feature_columns": (
                None if self.feature_columns is None else list(self.feature_columns)
            ),
            "folds": self.folds if self.folds == "all" else list(self.folds),
            "seed": self.seed,
            "top_k": list(self.top_k),
        }
        # Only serialized when set: the config hash is the identity in the
        # trial ledger, and configs predating this field must keep theirs.
        if self.score_thresholds:
            payload["score_thresholds"] = list(self.score_thresholds)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @property
    def config_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()[:16]


_EVAL_ALLOWED = frozenset({"name", "top_k", "score_thresholds"})


@dataclass(frozen=True)
class EvalConfig:
    """Metric parameters for re-scoring a saved model bundle.

    Only evaluation criteria live here. Anything that would change what
    gets evaluated — dataset version, scheme, folds, label, features —
    stays pinned inside the bundle, and naming such a field in an eval
    config is an error rather than a silent no-op.
    """

    name: str
    top_k: tuple[int, ...] = (20, 50)
    score_thresholds: tuple[float, ...] = ()

    @classmethod
    def from_file(cls, path: str | Path) -> "EvalConfig":
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"cannot read eval config {path}: {exc}") from exc
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<dict>") -> "EvalConfig":
        unknown = sorted(set(raw) - _EVAL_ALLOWED)
        if unknown:
            raise ConfigError(
                f"eval config {source} has fields an evaluation may not set: "
                f"{unknown} (an eval config changes metric parameters only; "
                "everything else is pinned by the model bundle)"
            )
        if "name" not in raw:
            raise ConfigError(f"eval config {source} lacks a name")
        return cls(
            name=raw["name"],
            top_k=tuple(int(k) for k in raw.get("top_k", (20, 50))),
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
        )
