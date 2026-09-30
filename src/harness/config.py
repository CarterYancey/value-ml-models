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

from harness.calibration import (
    CALIBRATION_METHODS,
    DEFAULT_CALIBRATION_MIN_ROWS,
)
from harness.derived_labels import (
    is_derived_label,
    label_slug,
    normalize_label,
    parse_label_expression,
)
from harness.errors import ConfigError
from harness.families import FEATURE_GROUPS, parse_family_ref
from harness.filters import FilterSpec, describe_filters

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


def parse_dataset_version(version: str) -> tuple[int, ...]:
    """Numeric tuple for a dataset version ("1.1", "v1.1", "dataset_v1.1"
    all parse to (1, 1)) — the comparison behind `min_dataset_version`."""
    v = str(version).strip()
    v = v.removeprefix("dataset_").removeprefix("v")
    try:
        return tuple(int(part) for part in v.split("."))
    except ValueError as exc:
        raise ConfigError(
            f"cannot parse dataset version {version!r} (expected X.Y, "
            "vX.Y, or dataset_vX.Y)"
        ) from exc


def infer_horizon_years(label: str) -> int | None:
    """The horizon a label name carries, or None when it carries none.
    A label expression (harness.derived_labels) carries the one horizon
    all its columns share — mixing horizons is a ConfigError."""
    if is_derived_label(label):
        return parse_label_expression(label).horizon_years
    m = _HORIZON_IN_LABEL.search(label)
    return int(m.group(1)) if m else None


def parse_pick_outcomes(raw, horizon_years: int, source: str) -> tuple[str, ...]:
    """The `pick_outcomes` list of a config, normalized and checked as
    far as a config alone allows: a list of distinct label names or
    label expressions, each carrying a horizon no longer than the
    run's. A shorter window lies inside the run's (every window starts
    at `snapshot_date`), so its outcome is observable on the run's test
    rows; a longer one is not. That the columns exist and sit in the
    manifest's `labels` group is checked against the dataset at run
    time."""
    if isinstance(raw, str) or not isinstance(raw, (list, tuple)):
        raise ConfigError(
            f"config {source}: pick_outcomes must be a list of label "
            f"columns or label expressions, got {raw!r}"
        )
    outcomes = tuple(normalize_label(str(o)) for o in raw)
    dupes = sorted({o for o in outcomes if outcomes.count(o) > 1})
    if dupes:
        raise ConfigError(f"config {source}: pick_outcomes repeats {dupes}")
    for o in outcomes:
        h = infer_horizon_years(o)
        if h is None:
            raise ConfigError(
                f"config {source}: pick outcome {o!r} carries no `{{H}}y` "
                "horizon; outcomes are label columns (label_*, fwd_*) or "
                "label expressions over them"
            )
        if h > horizon_years:
            raise ConfigError(
                f"config {source}: pick outcome {o!r} is a {h}y outcome but "
                f"the run's horizon is {horizon_years}y; its window outlives "
                "the run's, so it is not observable on the run's test rows"
            )
    return outcomes


#: Which rows a `[[universe]]` applies to: "all" trains and evaluates
#: inside the universe; "test" trains on every row and evaluates inside
#: it (the reference arm for a training-time floor, and what an eval
#: config's universe does to a saved bundle).
UNIVERSE_SCOPES = ("all", "test")

SCREEN_PERIODS = ("quarter", "year")
_SCREEN_KEYS = frozenset({"per", "top_k", "max_per_group", "group_column"})


def parse_universe(raw, source: str) -> tuple[FilterSpec, ...]:
    """The `[[universe]]` tables of a config: row filters over feature
    columns, in a canonical order with numeric values as floats, so one
    universe is one hash and one ledger cell however it was spelled.
    That the columns sit in a filterable manifest group is checked
    against the dataset at run time."""
    if raw is None or raw == []:
        return ()
    if not isinstance(raw, list):
        raise ConfigError(
            f"config {source}: universe must be [[universe]] tables of "
            f"column/op/value, got {raw!r}"
        )
    specs = []
    for table in raw:
        spec = FilterSpec.from_table(table, source, "[[universe]]")
        value = spec.value
        if isinstance(value, int) and not isinstance(value, bool):
            spec = FilterSpec(spec.column, spec.op, float(value))
        specs.append(spec)
    canon = [sp.canonical() for sp in specs]
    if len(set(canon)) != len(canon):
        raise ConfigError(f"config {source}: [[universe]] repeats a filter")
    return tuple(sorted(specs, key=lambda sp: sp.canonical()))


def universe_qualifier(universe: tuple[FilterSpec, ...]) -> str:
    """The text a universe adds to a ledger cell's label ("" for none)."""
    if not universe:
        return ""
    return f" [universe: {describe_filters(universe)}]"


def split_cell_label(cell_label: str) -> tuple[str, str]:
    """(label, universe text) of a ledger cell label; the universe text
    is "" for a cell over every row."""
    marker = " [universe: "
    if cell_label.endswith("]") and marker in cell_label:
        label, _, rest = cell_label.partition(marker)
        return label, rest[:-1]
    return cell_label, ""


@dataclass(frozen=True)
class PickScreen:
    """The portfolio screen (eval.picks): the top `top_k` rows of every
    test quarter (or year) by score, at most `max_per_group` of them
    sharing a value of `group_column`. It is the backtest template's
    selection rule applied to the test rows, so a run's report says what
    a capped, periodic portfolio of its picks went on to do. Report-only,
    like `pick_outcomes`, whose outcomes it reports."""

    per: str = "quarter"
    top_k: int = 10
    max_per_group: int | None = None
    group_column: str = "sector"

    @classmethod
    def from_table(cls, table, source: str) -> "PickScreen":
        if not isinstance(table, dict):
            raise ConfigError(f"config {source}: [pick_screen] must be a table")
        unknown = sorted(set(table) - _SCREEN_KEYS)
        if unknown:
            raise ConfigError(
                f"config {source}: unknown [pick_screen] keys {unknown}; "
                f"expected {sorted(_SCREEN_KEYS)}"
            )
        per = str(table.get("per", "quarter"))
        if per not in SCREEN_PERIODS:
            raise ConfigError(
                f"config {source}: [pick_screen] per must be one of "
                f"{list(SCREEN_PERIODS)}, got {per!r}"
            )
        top_k = table.get("top_k", 10)
        cap = table.get("max_per_group")
        for key, value in (("top_k", top_k), ("max_per_group", cap)):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ConfigError(
                    f"config {source}: [pick_screen] {key} must be a "
                    f"positive integer, got {value!r}"
                )
        if "group_column" in table and cap is None:
            raise ConfigError(
                f"config {source}: [pick_screen] group_column is set "
                "without max_per_group; it only names what the cap groups on"
            )
        return cls(
            per=per,
            top_k=int(top_k),
            max_per_group=cap,
            group_column=str(table.get("group_column", "sector")),
        )

    def to_table(self) -> dict:
        table: dict = {"per": self.per, "top_k": self.top_k}
        if self.max_per_group is not None:
            table["max_per_group"] = self.max_per_group
            table["group_column"] = self.group_column
        return table

    def describe(self) -> str:
        text = f"top {self.top_k} per test {self.per}"
        if self.max_per_group is not None:
            text += (
                f", at most {self.max_per_group} per `{self.group_column}`"
            )
        return text


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


def parse_feature_selection(raw: dict, source: str) -> dict:
    """The feature-selection fields of a config mapping — the `[features]`
    table (→ `features`) or the legacy trio, never both. Shared by
    `ExperimentConfig` and the registered-diagnostic configs so any
    experiment's selection can be probed verbatim."""
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
    return {
        "features": features,
        "feature_groups": tuple(raw.get("feature_groups", ())),
        "feature_columns": feature_columns,
        "exclude_feature_columns": tuple(raw.get("exclude_feature_columns", ())),
    }


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
    #: minimum upstream dataset version this config's feature/label needs
    #: (e.g. the trend features exist only from v1.1) — checked against
    #: the loaded dataset's manifest version, empty = no requirement
    min_dataset_version: str = ""
    #: binary label the run is *evaluated* against when `label` is a
    #: continuous target (the regression reframe: train on `fwd_3y_cagr`,
    #: rank by predicted return, measure precision@K against e.g.
    #: `label_3y_cagr_ge_10`). Required for continuous-target models,
    #: forbidden otherwise — enforced by
    #: `models.registry.check_target_labels` at run time.
    eval_label: str = ""
    #: prequential post-hoc calibration of the fold scores: "isotonic",
    #: "platt", or "" (off). Fold Y is calibrated on the pooled
    #: out-of-sample predictions of folds < Y — no local split is
    #: constructed (see harness.calibration). Probabilistic classifiers
    #: only; refused by vml-train-deploy (no history to calibrate on).
    calibration: str = ""
    #: minimum pooled history rows before a fold gets calibrated;
    #: earlier folds report raw scores and are flagged in the report
    calibration_min_rows: int = DEFAULT_CALIBRATION_MIN_ROWS
    #: report-only outcomes of the top-K picks (eval.picks): stored
    #: binary labels, label expressions (hit rate) or continuous outcome
    #: columns (mean and median), all from the manifest's `labels`
    #: group and none at a horizon beyond the run's. Never model inputs;
    #: the run stays counted in its own label's trial-ledger cell.
    pick_outcomes: tuple[str, ...] = ()
    #: row filters over feature columns (`[[universe]]`, harness.filters):
    #: the rows the model is trained and evaluated on, e.g. a liquidity
    #: floor. NULL fails. A universe changes the population the metrics
    #: describe, so it qualifies the ledger cell (`cell_label`).
    universe: tuple[FilterSpec, ...] = ()
    #: "all": train and test rows are filtered; "test": only test rows
    #: (train on everything, evaluate inside the universe)
    universe_scope: str = "all"
    #: the portfolio screen (`[pick_screen]`, see `PickScreen`)
    pick_screen: PickScreen | None = None
    #: config hashes of the bundles whose scores `vml-eval` combined
    #: with this config's by mean rank (harness.evaluate, `blend`). Set
    #: by an evaluation only, never read from a file: it is what makes a
    #: blended evaluation its own configuration in the trial ledger.
    blend: tuple[str, ...] = ()

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
        # label expressions are normalized so one target is one ledger cell
        label = normalize_label(str(raw["label"]))
        horizon = _resolve_horizon(raw, label, source)
        folds = raw.get("folds", "all")
        if folds != "all":
            folds = tuple(int(f) for f in folds)
        selection = parse_feature_selection(raw, source)
        config = cls(
            name=str(raw.get("name", "")),
            dataset_version=raw["dataset_version"],
            scheme=raw["scheme"],
            horizon_years=horizon,
            label=label,
            model_name=model["name"],
            model_params={k: v for k, v in model.items() if k != "name"},
            **selection,
            folds=folds,
            seed=int(raw.get("seed", 0)),
            top_k=tuple(int(k) for k in raw.get("top_k", (20, 50))),
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
            precision_targets=tuple(
                float(p) for p in raw.get("precision_targets", ())
            ),
            min_dataset_version=str(raw.get("min_dataset_version", "")),
            eval_label=normalize_label(str(raw.get("eval_label", ""))),
            calibration=str(raw.get("calibration", "")),
            calibration_min_rows=int(
                raw.get("calibration_min_rows", DEFAULT_CALIBRATION_MIN_ROWS)
            ),
            pick_outcomes=parse_pick_outcomes(
                raw.get("pick_outcomes", ()), horizon, source
            ),
            universe=parse_universe(raw.get("universe"), source),
            universe_scope=str(raw.get("universe_scope", "all")),
            pick_screen=(
                PickScreen.from_table(raw["pick_screen"], source)
                if "pick_screen" in raw
                else None
            ),
        )
        if config.universe_scope not in UNIVERSE_SCOPES:
            raise ConfigError(
                f"config {source}: universe_scope must be one of "
                f"{list(UNIVERSE_SCOPES)}, got {config.universe_scope!r}"
            )
        if "universe_scope" in raw and not config.universe:
            raise ConfigError(
                f"config {source}: universe_scope is set but there is no "
                "[[universe]]"
            )
        if config.calibration and config.calibration not in CALIBRATION_METHODS:
            raise ConfigError(
                f"config {source}: calibration must be one of "
                f"{list(CALIBRATION_METHODS)} or absent (off), "
                f"got {config.calibration!r}"
            )
        if config.calibration_min_rows < 1:
            raise ConfigError(
                f"config {source}: calibration_min_rows must be >= 1, "
                f"got {config.calibration_min_rows}"
            )
        if "calibration_min_rows" in raw and not config.calibration:
            raise ConfigError(
                f"config {source}: calibration_min_rows is set but "
                "calibration is off"
            )
        if config.eval_label:
            if config.eval_label == config.label:
                raise ConfigError(
                    f"config {source}: eval_label equals label "
                    f"({config.label!r}); eval_label is the *binary* cell a "
                    "continuous-target run is measured against"
                )
            ev_horizon = infer_horizon_years(config.eval_label)
            if ev_horizon is not None and ev_horizon != config.horizon_years:
                raise ConfigError(
                    f"config {source}: eval_label {config.eval_label!r} is a "
                    f"{ev_horizon}y label but the config's horizon is "
                    f"{config.horizon_years}y"
                )
        if config.min_dataset_version:
            parse_dataset_version(config.min_dataset_version)  # fail early
            if parse_dataset_version(config.dataset_version) < parse_dataset_version(
                config.min_dataset_version
            ):
                raise ConfigError(
                    f"config {source}: dataset_version "
                    f"{config.dataset_version!r} is below this config's "
                    f"min_dataset_version {config.min_dataset_version!r}"
                )
        if not config.name:
            config = replace(config, name=config.derived_name())
        return config

    def check_dataset_version(self, loaded_version: str) -> None:
        """Refuse to run against a dataset older than the config requires
        (e.g. trend features exist only from v1.1). Called by the runner
        with the manifest's `dataset_version`."""
        if not self.min_dataset_version:
            return
        if parse_dataset_version(loaded_version) < parse_dataset_version(
            self.min_dataset_version
        ):
            raise ConfigError(
                f"dataset {loaded_version!r} is below this config's "
                f"min_dataset_version {self.min_dataset_version!r} — see "
                "data/versions.md for what each dataset version provides"
            )

    @property
    def cell_label(self) -> str:
        """The label this run is counted under in the trial ledger: the
        binary cell it is measured on, qualified by the universe when
        one is set. Metrics inside a universe describe another
        population (other base rates, other baselines), so they are
        another cell, whatever rows the model was trained on."""
        return (self.eval_label or self.label) + universe_qualifier(
            self.universe
        )

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
        label = label_slug(self.label).removeprefix("label_")
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
        if self.min_dataset_version:
            raw["min_dataset_version"] = self.min_dataset_version
        if self.eval_label:
            raw["eval_label"] = self.eval_label
        if self.calibration:
            raw["calibration"] = self.calibration
            raw["calibration_min_rows"] = self.calibration_min_rows
        if self.pick_outcomes:
            raw["pick_outcomes"] = list(self.pick_outcomes)
        if self.universe:
            raw["universe"] = [f.to_table() for f in self.universe]
            if self.universe_scope != "all":
                raw["universe_scope"] = self.universe_scope
        if self.pick_screen is not None:
            raw["pick_screen"] = self.pick_screen.to_table()
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
        if self.min_dataset_version:
            payload["min_dataset_version"] = self.min_dataset_version
        if self.eval_label:
            payload["eval_label"] = self.eval_label
        if self.calibration:
            payload["calibration"] = self.calibration
            payload["calibration_min_rows"] = self.calibration_min_rows
        if self.pick_outcomes:
            payload["pick_outcomes"] = list(self.pick_outcomes)
        if self.universe:
            payload["universe"] = [f.to_table() for f in self.universe]
            if self.universe_scope != "all":
                payload["universe_scope"] = self.universe_scope
        if self.pick_screen is not None:
            payload["pick_screen"] = self.pick_screen.to_table()
        if self.blend:
            payload["blend"] = list(self.blend)
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


def _parse_blend(raw, source: str) -> tuple[str, ...]:
    if isinstance(raw, str) or not isinstance(raw, (list, tuple)):
        raise ConfigError(
            f"eval config {source}: blend must be a list of bundle "
            f"directories, got {raw!r}"
        )
    paths = tuple(str(p) for p in raw)
    if len(set(paths)) != len(paths):
        raise ConfigError(f"eval config {source}: blend repeats a bundle")
    return paths


_EVAL_ALLOWED = frozenset(
    {
        "name", "top_k", "score_thresholds", "precision_targets",
        "pick_outcomes", "pick_screen", "universe", "blend",
    }
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
    #: report-only pick outcomes (eval.picks) as written in the file;
    #: None keeps the bundle's own. They describe the picks and change
    #: nothing about what is evaluated, so an evaluation may set them.
    #: Checked against the bundle's horizon by `evaluate_bundle`.
    pick_outcomes: tuple[str, ...] | None = None
    #: the portfolio screen (report-only, like pick outcomes); None
    #: keeps the bundle's own
    pick_screen: PickScreen | None = None
    #: evaluate the bundle's models inside a universe of test rows. Only
    #: for a bundle trained without one (a bundle's own universe is
    #: pinned): the models are as trained, the rows they are measured
    #: on are fewer, and the evaluation is counted in the
    #: universe-qualified cell.
    universe: tuple[FilterSpec, ...] = ()
    #: other walk-forward bundles (directories) whose fold scores are
    #: combined with the evaluated bundle's by mean rank within each
    #: test quarter: the backtest's `combine = "mean_rank"` on the test
    #: rows, so a two-model candidate can be read on the screen before
    #: it is backtested
    blend: tuple[str, ...] = ()

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
        pick_outcomes = raw.get("pick_outcomes")
        if pick_outcomes is not None and (
            isinstance(pick_outcomes, str)
            or not isinstance(pick_outcomes, (list, tuple))
        ):
            raise ConfigError(
                f"eval config {source}: pick_outcomes must be a list of "
                f"label columns or label expressions, got {pick_outcomes!r}"
            )
        return cls(
            name=raw["name"],
            top_k=tuple(int(k) for k in raw.get("top_k", (20, 50))),
            score_thresholds=tuple(
                float(t) for t in raw.get("score_thresholds", ())
            ),
            precision_targets=tuple(
                float(p) for p in raw.get("precision_targets", ())
            ),
            pick_outcomes=(
                None
                if pick_outcomes is None
                else tuple(str(o) for o in pick_outcomes)
            ),
            pick_screen=(
                PickScreen.from_table(raw["pick_screen"], source)
                if "pick_screen" in raw
                else None
            ),
            universe=parse_universe(raw.get("universe"), source),
            blend=_parse_blend(raw.get("blend", ()), source),
        )
