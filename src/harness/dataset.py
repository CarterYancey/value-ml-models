"""Loader for a versioned dataset directory (`data/datasets/dataset_vX.Y/`).

Implements the contract in data/manual.md:

- column selection is manifest-driven (`manifest.json["columns"]`), never
  name-pattern-matched;
- split tags are applied, never constructed (data/splits.md);
- guardrails are errors, not conventions (see harness.errors).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from harness.errors import (
    DatasetValidationError,
    DiagnosticSchemeError,
    HoldoutAccessError,
    MissingSampleWeightError,
    SplitApplicationError,
)
from harness.families import (
    FEATURE_GROUPS,
    family_group_columns,
    parse_family_ref,
)

SNAPSHOT_KEY = ["permaticker", "snapshot_date", "snapshot_kind"]

COLUMN_GROUPS = (
    "key_meta",
    "features",
    "ranks",
    "sector_ranks",
    "labels",
    "sample_weights",
)

REQUIRED_FILES = (
    "dataset.parquet",
    "splits.parquet",
    "split_folds.parquet",
    "manifest.json",
)

#: The one scheme where model selection may happen.
SELECTION_SCHEME = "walkforward"
SEALED_SCHEMES = frozenset({"holdout"})
DIAGNOSTIC_SCHEMES = frozenset({"entity_holdout", "random_kfold"})
KNOWN_SCHEMES = frozenset({SELECTION_SCHEME}) | SEALED_SCHEMES | DIAGNOSTIC_SCHEMES


class SplitAccess(Enum):
    """Who is asking for a split.

    STANDARD is all ordinary model-selection work and permits only
    `walkforward`. FINAL_EVAL is granted solely by the dedicated
    final-eval script (once per phase); REGISTERED_DIAGNOSTIC solely by
    the registered-experiment runner (data/manual.md §7).
    """

    STANDARD = "standard"
    FINAL_EVAL = "final_eval"
    REGISTERED_DIAGNOSTIC = "registered_diagnostic"


@dataclass(frozen=True)
class SplitFrames:
    """Train/test frames for one (scheme, fold, horizon)."""

    scheme: str
    fold: int
    horizon_years: int
    train: pd.DataFrame
    test: pd.DataFrame


@dataclass(frozen=True)
class FitData:
    """Arrays ready for a weighted fit on one labeled cell."""

    X: pd.DataFrame
    y: np.ndarray
    sample_weight: np.ndarray
    #: Σ sample_weight — the honest sample size to report.
    effective_size: float


class Dataset:
    """A pinned, immutable `dataset_vX.Y` directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._validate_files()
        with open(self.root / "manifest.json") as fh:
            self.manifest: dict = json.load(fh)
        self._data: pd.DataFrame | None = None
        self._splits: pd.DataFrame | None = None
        self._split_folds: pd.DataFrame | None = None
        self._validate_manifest()

    # ------------------------------------------------------------- loading

    def _validate_files(self) -> None:
        if not self.root.is_dir():
            raise DatasetValidationError(f"dataset directory not found: {self.root}")
        missing = [f for f in REQUIRED_FILES if not (self.root / f).exists()]
        if missing:
            raise DatasetValidationError(
                f"{self.root} is missing required files: {missing}"
            )

    def _validate_manifest(self) -> None:
        for field in ("dataset_version", "horizons_years", "rows", "columns"):
            if field not in self.manifest:
                raise DatasetValidationError(f"manifest.json lacks field {field!r}")
        cols = self.manifest["columns"]
        missing_groups = [g for g in COLUMN_GROUPS if g not in cols]
        if missing_groups:
            raise DatasetValidationError(
                f"manifest columns lack groups: {missing_groups}"
            )
        n_rows = len(self.data)
        if n_rows != self.manifest["rows"]:
            raise DatasetValidationError(
                f"manifest declares {self.manifest['rows']} rows but "
                f"dataset.parquet has {n_rows}"
            )
        declared = [c for g in COLUMN_GROUPS for c in cols[g]]
        absent = sorted(set(declared) - set(self.data.columns))
        if absent:
            raise DatasetValidationError(
                f"manifest declares columns absent from dataset.parquet: {absent}"
            )

    @property
    def version(self) -> str:
        return self.manifest["dataset_version"]

    @property
    def horizons_years(self) -> list[int]:
        return list(self.manifest["horizons_years"])

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = pd.read_parquet(self.root / "dataset.parquet")
        return self._data

    @property
    def splits(self) -> pd.DataFrame:
        if self._splits is None:
            self._splits = pd.read_parquet(self.root / "splits.parquet")
        return self._splits

    @property
    def split_folds(self) -> pd.DataFrame:
        if self._split_folds is None:
            self._split_folds = pd.read_parquet(self.root / "split_folds.parquet")
        return self._split_folds

    # ------------------------------------------------------------- columns

    def columns(self, group: str) -> list[str]:
        """Column names of one manifest group, in manifest order."""
        if group not in COLUMN_GROUPS:
            raise DatasetValidationError(
                f"unknown column group {group!r}; expected one of {COLUMN_GROUPS}"
            )
        return list(self.manifest["columns"][group])

    def feature_columns(
        self,
        groups: Sequence[str],
        subset: Sequence[str] | None = None,
        exclude: Sequence[str] = (),
    ) -> list[str]:
        """Feature columns from manifest groups, optionally narrowed to an
        explicit `subset` (whitelist) and/or stripped of `exclude`
        (blacklist, applied after the whitelist). Both must reference
        columns actually present in the selection so far — naming columns
        the manifest doesn't declare is refused, which is what keeps
        name-pattern selection out of the codebase, and it also catches
        typos in an exclusion list (a silently ignored exclusion would
        leave an unwanted column in the model). The blacklist is the tool
        for "a whole group minus its unusable columns" — e.g. `features`
        minus the raw string categoricals and date fields no tree model
        can consume."""
        allowed_groups = {"features", "ranks", "sector_ranks"}
        bad = [g for g in groups if g not in allowed_groups]
        if bad:
            raise DatasetValidationError(
                f"feature groups must be within {sorted(allowed_groups)}, got {bad}"
            )
        cols = [c for g in groups for c in self.columns(g)]
        if subset is not None:
            unknown = sorted(set(subset) - set(cols))
            if unknown:
                raise DatasetValidationError(
                    f"requested feature columns not in selected manifest "
                    f"groups {list(groups)}: {unknown}"
                )
            cols = [c for c in cols if c in set(subset)]
        if exclude:
            unknown = sorted(set(exclude) - set(cols))
            if unknown:
                raise DatasetValidationError(
                    f"excluded feature columns not in the selected columns "
                    f"(groups {list(groups)}): {unknown}"
                )
            cols = [c for c in cols if c not in set(exclude)]
        if groups and not cols:
            raise DatasetValidationError(
                f"feature selection over groups {list(groups)} left no "
                "columns (whitelist/blacklist removed everything)"
            )
        return cols

    def select_features(self, spec) -> list[str]:
        """Resolve a hierarchical `FeatureSpec` (harness.config) against
        the manifest: union of the named groups, families, and columns,
        minus the exclusions. Family membership comes from the registry
        copy in harness.families, but a column enters the selection only
        if the manifest declares it — the manifest stays the sole
        authority on what exists. Every exclusion must remove something
        actually selected: blacklisting a child whose parent was never
        selected is an error, not a no-op."""
        bad = [g for g in spec.groups if g not in FEATURE_GROUPS]
        if bad:
            raise DatasetValidationError(
                f"feature groups must be within {list(FEATURE_GROUPS)}, got {bad}"
            )
        selected: set[str] = set()
        for g in spec.groups:
            selected.update(self.columns(g))
        for ref in spec.families:
            cols = self._family_columns(ref)
            if not cols:
                raise DatasetValidationError(
                    f"feature family {ref!r} has no columns in the "
                    f"{self.version} manifest"
                )
            selected.update(cols)
        declared = {c for g in FEATURE_GROUPS for c in self.columns(g)}
        unknown = sorted(set(spec.columns) - declared)
        if unknown:
            raise DatasetValidationError(
                f"requested feature columns not declared by the manifest's "
                f"feature groups {list(FEATURE_GROUPS)}: {unknown}"
            )
        selected.update(spec.columns)

        for ref in spec.exclude_families:
            cols = set(self._family_columns(ref))
            if not cols & selected:
                raise DatasetValidationError(
                    f"exclude_families entry {ref!r} removes nothing: no "
                    "selected group or family contains it (blacklisting a "
                    "child whose parent was never selected)"
                )
            selected -= cols
        missing = sorted(set(spec.exclude_columns) - selected)
        if missing:
            raise DatasetValidationError(
                f"exclude_columns entries not in the selection: {missing} "
                "(blacklisting a child whose parent was never selected, "
                "or a typo)"
            )
        selected -= set(spec.exclude_columns)

        ordered = [
            c for g in FEATURE_GROUPS for c in self.columns(g) if c in selected
        ]
        if not ordered:
            raise DatasetValidationError(
                "feature selection left no columns (exclusions removed "
                "everything)"
            )
        return ordered

    def _family_columns(self, ref: str) -> list[str]:
        """A family reference's columns as declared by this manifest —
        registry candidates intersected with the manifest groups."""
        group, family = parse_family_ref(ref)
        groups = [group] if group else list(FEATURE_GROUPS)
        cols: list[str] = []
        for g in groups:
            present = set(self.columns(g))
            cols += [c for c in family_group_columns(family, g) if c in present]
        return cols

    def sample_weight_column(self, horizon_years: int) -> str:
        """The `sample_weight_{H}y` column for a horizon, verified against
        the manifest's sample_weights group."""
        self._check_horizon(horizon_years)
        name = f"sample_weight_{horizon_years}y"
        if name not in self.columns("sample_weights"):
            raise MissingSampleWeightError(
                f"manifest sample_weights group has no {name!r}; refusing to "
                "fit without the horizon's uniqueness weight"
            )
        return name

    def _check_horizon(self, horizon_years: int) -> None:
        if horizon_years not in self.horizons_years:
            raise DatasetValidationError(
                f"horizon {horizon_years} not in manifest horizons_years "
                f"{self.horizons_years}"
            )

    def manifest_effective_rows(self, horizon_years: int) -> float | None:
        """Σ sample_weight over the whole dataset, as recorded at build time."""
        eff = self.manifest.get("effective_rows", {})
        return eff.get(f"{horizon_years}y", eff.get(str(horizon_years)))

    # -------------------------------------------------------------- splits

    def folds(self, scheme: str, horizon_years: int) -> list[int]:
        """Fold identifiers for (scheme, horizon), from the frozen manifest."""
        sf = self.split_folds
        sel = sf[(sf["scheme"] == scheme) & (sf["horizon_years"] == horizon_years)]
        return sorted(int(f) for f in sel["fold"].unique())

    def apply_split(
        self,
        scheme: str,
        fold: int,
        horizon_years: int,
        access: SplitAccess = SplitAccess.STANDARD,
    ) -> SplitFrames:
        """Join split tags for (scheme, fold, horizon) and return train/test.

        Enforced here, as errors:
        - scheme access (sealed holdout, diagnostic-only schemes);
        - train rows are `role='train'` only — purged/embargoed rows exist
          to make the boundary cost measurable, not to be trained on;
        - test rows come only from the tags, and are verified to be
          median-kind and label-observable (defense against a malformed
          upstream artifact).
        """
        self._check_scheme_access(scheme, access)
        self._check_horizon(horizon_years)

        tags = self.splits
        sel = tags[
            (tags["scheme"] == scheme)
            & (tags["fold"] == fold)
            & (tags["horizon_years"] == horizon_years)
        ]
        if sel.empty:
            raise SplitApplicationError(
                f"no split tags for scheme={scheme!r} fold={fold} "
                f"horizon={horizon_years}; folds available: "
                f"{self.folds(scheme, horizon_years)}"
            )

        key = SNAPSHOT_KEY
        train_keys = sel.loc[sel["role"] == "train", key]
        test_keys = sel.loc[sel["role"] == "test", key]
        train = self.data.merge(train_keys, on=key, how="inner")
        test = self.data.merge(test_keys, on=key, how="inner")
        if len(train) != len(train_keys) or len(test) != len(test_keys):
            raise SplitApplicationError(
                f"split tags reference snapshots missing from dataset.parquet "
                f"(train {len(train)}/{len(train_keys)}, "
                f"test {len(test)}/{len(test_keys)})"
            )

        self._validate_test_rows(test, horizon_years, scheme, fold)
        return SplitFrames(
            scheme=scheme,
            fold=int(fold),
            horizon_years=horizon_years,
            train=train,
            test=test,
        )

    def _check_scheme_access(self, scheme: str, access: SplitAccess) -> None:
        if scheme not in KNOWN_SCHEMES:
            raise SplitApplicationError(f"unknown split scheme {scheme!r}")
        if scheme in SEALED_SCHEMES and access is not SplitAccess.FINAL_EVAL:
            raise HoldoutAccessError(
                "the `holdout` scheme is sealed: it is evaluated once per "
                "phase by the dedicated final-eval script, never during "
                "development or model selection"
            )
        if scheme in DIAGNOSTIC_SCHEMES and access is not SplitAccess.REGISTERED_DIAGNOSTIC:
            raise DiagnosticSchemeError(
                f"scheme {scheme!r} is diagnostic-only (deliberately leaky in "
                "the random_kfold case) and may only be used by the "
                "registered-experiment runner, never for model selection or "
                "reported performance"
            )

    def _validate_test_rows(
        self, test: pd.DataFrame, horizon_years: int, scheme: str, fold: int
    ) -> None:
        if test.empty:
            return
        non_median = (test["snapshot_kind"] != "median").sum()
        if non_median:
            raise SplitApplicationError(
                f"{non_median} test rows for ({scheme}, {fold}, "
                f"{horizon_years}) are not median-kind; refusing to evaluate "
                "on low/high entry prices"
            )
        observable = f"delisted_in_window_{horizon_years}y"
        if observable in test.columns and test[observable].isna().any():
            raise SplitApplicationError(
                f"test rows for ({scheme}, {fold}, {horizon_years}) include "
                "label-unobservable snapshots"
            )

    # ----------------------------------------------------------------- fit

    def fit_data(
        self,
        frame: pd.DataFrame,
        label: str,
        feature_cols: Sequence[str],
        horizon_years: int,
    ) -> FitData:
        """Assemble (X, y, w) for a weighted fit.

        Rows whose label is NULL (horizon unobservable) carry no target and
        are excluded from the fit — note this is *not* a delisting filter;
        delisted rows are labeled rows like any other and stay in.
        Fitting without the horizon's weight is refused.
        """
        if label not in self.columns("labels"):
            raise DatasetValidationError(
                f"label {label!r} is not in the manifest labels group"
            )
        weight_col = self.sample_weight_column(horizon_years)
        labeled = frame[frame[label].notna()]
        w = labeled[weight_col]
        if w.isna().any():
            raise MissingSampleWeightError(
                f"{int(w.isna().sum())} labeled rows have NULL {weight_col}; "
                "upstream guarantees weights exactly where the label is "
                "observable — refusing to fit"
            )
        return FitData(
            X=labeled[list(feature_cols)],
            y=labeled[label].astype(bool).to_numpy(),
            sample_weight=w.to_numpy(dtype=float),
            effective_size=float(w.sum()),
        )
