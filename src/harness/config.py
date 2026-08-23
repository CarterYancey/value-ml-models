"""Experiment config schema: one TOML file per experiment in `experiments/`.

A config pins everything needed to reproduce a run: dataset version,
scheme/folds/horizon, label column, feature selection, model + params,
seed. The config's canonical-JSON SHA-256 is the identity logged with
every run.

Ergonomics (each optional, all derived deterministically):

- `name` may be omitted: the default is
  `{model}_{features}_{label}_{content-hash}`, so a copied config with
  any value changed can no longer overwrite the original's artifacts by
  way of a forgotten name.
- `horizon_years` may be omitted when the label carries its horizon
  (`label_3y_beat_spy` → 3); stating both requires them to agree.
- Features are selected hierarchically via a `[features]` table
  (groups ⊃ families ⊃ columns, see `FeatureSpec`); the legacy top-level
  `feature_groups`/`feature_columns`/`exclude_feature_columns` keys keep
  working (and keep their config hashes) but can't be mixed with it.

`EvalConfig` is the deliberately tiny companion for re-scoring a saved
model bundle (harness.evaluate): it may change how metrics are computed,
never what was trained or which rows are tested.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

from harness.errors import ConfigError
from harness.families import FEATURE_GROUPS, parse_family_ref

_REQUIRED = ("dataset_version", "scheme", "label", "model")

#: horizon embedded in a label/column name, e.g. `label_3y_beat_spy`,
#: `fwd_1y_cagr` — the `{H}y` token delimited by `_` or the string ends
_HORIZON_IN_LABEL = re.compile(r"(?:^|_)(\d+)y(?:_|$)")

_LEGACY_FEATURE_KEYS = (
    "feature_groups",
    "feature_columns",
    "exclude_feature_columns",
)
_FEATURES_TABLE_KEYS = frozenset(
    {"groups", "families", "columns", "exclude_columns", "exclude_families"}
)


def infer_horizon_years(label: str) -> int | None:
    """The horizon a label name carries, or None when it carries none."""
    m = _HORIZON_IN_LABEL.search(label)
    return int(m.group(1)) if m else None


@dataclass(frozen=True)
class FeatureSpec:
    """Hierarchical feature selection: groups ⊃ families ⊃ columns.

    The selection is the union of everything named — whole manifest
    `groups`, registry `families` (bare `"valuation"` takes the family in
    every group it appears in; `"ranks/valuation"` only that group's
    variant), and individual `columns` (their group/family membership is
    implied, nothing else to declare). `exclude_*` then subtract from the
    union; every exclusion must remove something actually selected —
    blacklisting a child whose parent was never selected is the one
    inconsistency, and it is an error, not a no-op (a silently ignored
    exclusion would leave an unwanted column in the model, and a typo'd
    one would too). Resolution against a manifest lives in
    `Dataset.select_features`.
    """

    groups: tuple[str, ...] = ()
    families: tuple[str, ...] = ()
    columns: tuple[str, ...] = ()
    exclude_columns: tuple[str, ...] = ()
    exclude_families: tuple[str, ...] = ()

    @classmethod
    def from_table(cls, table: dict, source: str) -> "FeatureSpec":
        if not isinstance(table, dict):
            raise ConfigError(f"config {source}: [features] must be a table")
        unknown = sorted(set(table) - _FEATURES_TABLE_KEYS)
        if unknown:
            raise ConfigError(
                f"config {source}: unknown [features] keys {unknown}; "
                f"expected {sorted(_FEATURES_TABLE_KEYS)}"
            )
        spec = cls(
            groups=tuple(table.get("groups", ())),
            families=tuple(table.get("families", ())),
            columns=tuple(table.get("columns", ())),
            exclude_columns=tuple(table.get("exclude_columns", ())),
            exclude_families=tuple(table.get("exclude_families", ())),
        )
        if not (spec.groups or spec.families or spec.columns):
            raise ConfigError(
                f"config {source}: [features] selects nothing — name at "
                "least one of groups, families, columns"
            )
        bad = [g for g in spec.groups if g not in FEATURE_GROUPS]
        if bad:
            raise ConfigError(
                f"config {source}: [features] groups must be within "
                f"{list(FEATURE_GROUPS)}, got {bad}"
            )
        for ref in spec.families + spec.exclude_families:
            parse_family_ref(ref)  # unknown family/group -> ConfigError
        return spec

    def to_table(self) -> dict:
        table: dict = {}
        for key in (
            "groups", "families", "columns",
            "exclude_columns", "exclude_families",
        ):
            value = getattr(self, key)
            if value:
                table[key] = list(value)
        return table


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
    #: optional explicit subset of the selected groups' columns (whitelist)
    feature_columns: tuple[str, ...] | None = None
    #: columns removed from the selection after any whitelist (blacklist —
    #: "the whole group minus these"); every entry must exist in the
    #: selection or the run refuses, so typos can't silently keep a column
    exclude_feature_columns: tuple[str, ...] = ()
    #: hierarchical selection (the `[features]` table) — mutually
    #: exclusive with the three legacy fields above, which remain for
    #: existing configs and saved bundles
    features: FeatureSpec | None = None
    #: "all" (every fold in split_folds for scheme+horizon) or explicit list
    folds: tuple[int, ...] | str = "all"
    seed: int = 0
    #: K values for precision@K / recall@K
    top_k: tuple[int, ...] = (20, 50)
    #: score thresholds for precision/recall over "score >= t" selections
    #: (empty = don't record threshold metrics)
    score_thresholds: tuple[float, ...] = ()
    #: precision floors: record the best recall (and the threshold
    #: achieving it) subject to precision >= target — the high-precision
    #: strategy's headline trade-off (empty = don't record)
    precision_targets: tuple[float, ...] = ()

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
        label = raw["label"]
        horizon = _resolve_horizon(raw, label, source)
        folds = raw.get("folds", "all")
        if folds != "all":
            folds = tuple(int(f) for f in folds)
        legacy_used = [k for k in _LEGACY_FEATURE_KEYS if k in raw]
        features = None
        if "features" in raw:
            if legacy_used:
                raise ConfigError(
                    f"config {source} mixes the [features] table with the "
                    f"legacy keys {legacy_used}; use one style"
                )
            features = FeatureSpec.from_table(raw["features"], source)
        feature_columns = raw.get("feature_columns")
        if feature_columns is not None:
            feature_columns = tuple(feature_columns)
        config = cls(
            name=str(raw.get("name", "")),
            dataset_version=raw["dataset_version"],
            scheme=raw["scheme"],
            horizon_years=horizon,
            label=label,
            model_name=model["name"],
            model_params={k: v for k, v in model.items() if k != "name"},
            feature_groups=tuple(raw.get("feature_groups", ())),
            feature_columns=feature_columns,
            exclude_feature_columns=tuple(raw.get("exclude_feature_columns", ())),
            features=features,
            folds=folds,
            seed=int(raw.get("seed", 0)),
            top_k=tuple(int(k) for k in raw.get("top_k", (20, 50))),
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
            precision_targets=tuple(
                float(p) for p in raw.get("precision_targets", ())
            ),
        )
        if not config.name:
            config = replace(config, name=config.derived_name())
        return config

    def derived_name(self) -> str:
        """Default experiment name: `{model}_{features}_{label}_{hash}`.

        The hash is over the config's *content* (everything but the name),
        so a copied config with any value changed gets a fresh name instead
        of silently overwriting the original's reports and bundles.
        """
        if self.features is not None:
            tags = list(self.features.groups) + [
                f.replace("/", "-") for f in self.features.families
            ]
            feat = "-".join(tags) if tags else "cols"
        else:
            feat = "-".join(self.feature_groups) or "cols"
        label = self.label.removeprefix("label_")
        return f"{self.model_name}_{feat}_{label}_{self.identity_hash}"

    def resolve_feature_columns(self, dataset) -> list[str]:
        """The concrete feature columns this config selects from a
        `Dataset`, whichever selection style the config uses."""
        if self.features is not None:
            return dataset.select_features(self.features)
        return dataset.feature_columns(
            self.feature_groups,
            self.feature_columns,
            exclude=self.exclude_feature_columns,
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
            "folds": self.folds if self.folds == "all" else list(self.folds),
            "seed": self.seed,
            "top_k": list(self.top_k),
            "score_thresholds": list(self.score_thresholds),
            "precision_targets": list(self.precision_targets),
        }
        if self.features is not None:
            raw["features"] = self.features.to_table()
        else:
            raw["feature_groups"] = list(self.feature_groups)
            if self.feature_columns is not None:
                raw["feature_columns"] = list(self.feature_columns)
            if self.exclude_feature_columns:
                raw["exclude_feature_columns"] = list(
                    self.exclude_feature_columns
                )
        return raw

    def _canonical_payload(self) -> dict:
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
        # trial ledger, and configs predating these fields must keep theirs.
        if self.score_thresholds:
            payload["score_thresholds"] = list(self.score_thresholds)
        if self.precision_targets:
            payload["precision_targets"] = list(self.precision_targets)
        if self.exclude_feature_columns:
            payload["exclude_feature_columns"] = list(self.exclude_feature_columns)
        if self.features is not None:
            payload["features"] = self.features.to_table()
        return payload

    def canonical_json(self) -> str:
        return json.dumps(
            self._canonical_payload(), sort_keys=True, separators=(",", ":")
        )

    @property
    def config_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()[:16]

    @property
    def identity_hash(self) -> str:
        """Hash of the config content with the name left out — what the
        derived default name embeds (the name can't contain a hash of
        itself)."""
        payload = self._canonical_payload()
        del payload["name"]
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:8]


def _resolve_horizon(raw: dict, label: str, source: str) -> int:
    """`horizon_years`, inferred from the label's `{H}y` token when the
    config omits it; a config that states both must agree."""
    inferred = infer_horizon_years(label)
    if "horizon_years" in raw:
        horizon = int(raw["horizon_years"])
        if inferred is not None and inferred != horizon:
            raise ConfigError(
                f"config {source}: horizon_years = {horizon} contradicts "
                f"label {label!r} (a {inferred}y label); drop horizon_years "
                "or fix the label"
            )
        return horizon
    if inferred is None:
        raise ConfigError(
            f"config {source}: label {label!r} carries no `{{H}}y` horizon "
            "token, so horizon_years must be set explicitly"
        )
    return inferred


_EVAL_ALLOWED = frozenset(
    {"name", "top_k", "score_thresholds", "precision_targets"}
)


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
    precision_targets: tuple[float, ...] = ()

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
            precision_targets=tuple(
                float(p) for p in raw.get("precision_targets", ())
            ),
        )
