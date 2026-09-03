"""Era-identifiability probe (registered diagnostic, data/manual.md §7).

Predict the calendar year of a snapshot — `year(snapshot_date)` — from
the feature columns alone, under an entity-disjoint split
(`entity_holdout`: train = permaticker buckets 1–4, all snapshot kinds;
test = bucket-0 median rows), so the probe cannot win by memorising
firms. Two arms are the point: the raw `features` group versus the
`ranks` group (percent ranks within (quarter, kind) are uniform per
quarter by construction, so era signal there is joint structure or
nullity, not level). Beating the majority-year and train-prior baselines
settles "you can't tell what date a sample comes from" negatively — and
says how much of an entity-holdout return model's score could be era
timing rather than stock selection.

Diagnostic only: never model selection, never reported performance.

Design points:
- The target is derived from `key_meta` (`snapshot_date`), not the
  label matrix. Invariant 4 (no feature engineering) is about features;
  no feature is derived here — the same columns the ordinary runner
  would fit are fed verbatim.
- Rows are the horizon's label-observable rows and the fit is weighted
  by `sample_weight_{H}y`, exactly as any experiment at that horizon
  (`Dataset.observable_fit_rows` shares `fit_data`'s weight guardrail).
  `horizon_years` is therefore mandatory: it selects the tag set and the
  weight column.
- `random_kfold` is accepted as the deliberately leaky upper bound
  (same firms, overlapping windows in train and test). `walkforward`
  is refused: one test year per fold makes the probe degenerate.
  `holdout` is sealed.
- Non-numeric feature columns are refused, not dropped, so the config
  hash describes exactly what was probed; exclude them in the config.
- `access` defaults to STANDARD: this module never opens the diagnostic
  tags by itself. `scripts/run_diagnostic.py` is the single grant site.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from diagnostics.era_metrics import (
    align_proba,
    confusion_matrix_weighted,
    headline_metrics,
    min_year_slice,
    per_year_table,
    predict_year,
    render_confusion_heatmap,
    render_importance_bar,
)
from diagnostics.probe_models import PROBE_MODELS, build_probe_model
from explain.rules import render_tree_diagram, rules_text_multiclass
from harness.config import (
    ExperimentConfig,
    FeatureSpec,
    parse_dataset_version,
    parse_feature_selection,
)
from harness.dataset import DIAGNOSTIC_SCHEMES, Dataset, SplitAccess
from harness.errors import ConfigError, DiagnosticSchemeError
from harness.results import ResultsStore, git_sha, new_run_id
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_RESULTS

#: Pseudo-label the probe logs under in the results store. Ledger queries
#: filter on (scheme, label), so probe rows never enter a walk-forward
#: cell's trial count or baseline table.
SNAPSHOT_YEAR_LABEL = "snapshot_year"
DIAGNOSTIC_KIND = "era_probe"
DEFAULT_DIAGNOSTIC_REPORTS = Path("reports/diagnostics")
DEFAULT_SCHEME = "entity_holdout"

_REQUIRED = ("dataset_version", "horizon_years", "model")
_ALLOWED_KEYS = frozenset(
    {
        "diagnostic",
        "name",
        "dataset_version",
        "scheme",
        "horizon_years",
        "folds",
        "seed",
        "min_dataset_version",
        "report_min_year",
        "model",
        "features",
        "feature_groups",
        "feature_columns",
        "exclude_feature_columns",
    }
)


@dataclass(frozen=True)
class EraProbeConfig:
    """One probe = one TOML in `experiments/diagnostics/`."""

    name: str
    dataset_version: str
    scheme: str
    horizon_years: int
    model_name: str
    model_params: dict = field(default_factory=dict)
    features: FeatureSpec | None = None
    feature_groups: tuple[str, ...] = ()
    feature_columns: tuple[str, ...] | None = None
    exclude_feature_columns: tuple[str, ...] = ()
    folds: tuple[int, ...] | str = "all"
    seed: int = 0
    min_dataset_version: str = ""
    #: post-burn-in slice reported alongside the full result (early years
    #: are identifiable from nullity alone — data/manual.md §8)
    report_min_year: int | None = None

    # --------------------------------------------------------- parsing

    @classmethod
    def from_file(cls, path: str | Path) -> "EraProbeConfig":
        path = Path(path)
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"cannot read config {path}: {exc}") from exc
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: dict, source: str = "<dict>") -> "EraProbeConfig":
        unknown = sorted(set(raw) - _ALLOWED_KEYS)
        if unknown:
            raise ConfigError(
                f"config {source}: unknown era-probe keys {unknown} (a "
                "`label`/`top_k` here is an experiment config pasted in; "
                "the probe's target is always the snapshot year)"
            )
        missing = [k for k in _REQUIRED if k not in raw]
        if missing:
            raise ConfigError(f"config {source} lacks required fields: {missing}")
        kind = raw.get("diagnostic", DIAGNOSTIC_KIND)
        if kind != DIAGNOSTIC_KIND:
            raise ConfigError(
                f"config {source}: diagnostic = {kind!r} is not "
                f"{DIAGNOSTIC_KIND!r}"
            )
        model = raw["model"]
        if not isinstance(model, dict) or "name" not in model:
            raise ConfigError(f"config {source}: [model] must be a table with a name")
        if model["name"] not in PROBE_MODELS:
            raise ConfigError(
                f"config {source}: model {model['name']!r} is not a probe "
                f"model; the era probe supports {list(PROBE_MODELS)} (its "
                "trivial baselines are computed by the probe itself)"
            )
        scheme = str(raw.get("scheme", DEFAULT_SCHEME))
        if scheme not in DIAGNOSTIC_SCHEMES:
            raise DiagnosticSchemeError(
                f"config {source}: the era probe runs only under the "
                f"diagnostic schemes {sorted(DIAGNOSTIC_SCHEMES)}, got "
                f"{scheme!r} (walkforward has one test year per fold — "
                "degenerate; holdout is sealed)"
            )
        folds = raw.get("folds", "all")
        if folds != "all":
            folds = tuple(int(f) for f in folds)
        report_min_year = raw.get("report_min_year")
        if report_min_year is not None:
            report_min_year = int(report_min_year)
        selection = parse_feature_selection(raw, source)
        if selection["features"] is None and not (
            selection["feature_groups"] or selection["feature_columns"]
        ):
            raise ConfigError(
                f"config {source}: no feature selection (a [features] table "
                "or feature_groups)"
            )
        config = cls(
            name=str(raw.get("name", "")),
            dataset_version=str(raw["dataset_version"]),
            scheme=scheme,
            horizon_years=int(raw["horizon_years"]),
            model_name=model["name"],
            model_params={k: v for k, v in model.items() if k != "name"},
            folds=folds,
            seed=int(raw.get("seed", 0)),
            min_dataset_version=str(raw.get("min_dataset_version", "")),
            report_min_year=report_min_year,
            **selection,
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

    # ------------------------------------------------------ delegation

    def to_experiment_config(self) -> ExperimentConfig:
        """The probe as the harness sees it (label = the pseudo-label):
        used for feature resolution and the dataset-version check, never
        for running — the ordinary runner would refuse the scheme."""
        return ExperimentConfig(
            name=self.name,
            dataset_version=self.dataset_version,
            scheme=self.scheme,
            horizon_years=self.horizon_years,
            label=SNAPSHOT_YEAR_LABEL,
            model_name=self.model_name,
            model_params=self.model_params,
            features=self.features,
            feature_groups=self.feature_groups,
            feature_columns=self.feature_columns,
            exclude_feature_columns=self.exclude_feature_columns,
            folds=self.folds,
            seed=self.seed,
            min_dataset_version=self.min_dataset_version,
        )

    def resolve_feature_columns(self, dataset: Dataset) -> list[str]:
        return self.to_experiment_config().resolve_feature_columns(dataset)

    def check_dataset_version(self, loaded_version: str) -> None:
        self.to_experiment_config().check_dataset_version(loaded_version)

    # -------------------------------------------------------- identity

    def feature_summary(self) -> str:
        if self.features is not None:
            parts = list(self.features.groups) + list(self.features.families)
            feat = "+".join(parts) if parts else "columns"
            n_ex = len(self.features.exclude_columns) + len(
                self.features.exclude_families
            )
            return f"{feat}" + (f" minus {n_ex} exclusion(s)" if n_ex else "")
        feat = "+".join(self.feature_groups) or "columns"
        if self.exclude_feature_columns:
            feat += f" minus {len(self.exclude_feature_columns)} exclusion(s)"
        return feat

    def to_raw_dict(self) -> dict:
        raw: dict = {
            "diagnostic": DIAGNOSTIC_KIND,
            "name": self.name,
            "dataset_version": self.dataset_version,
            "scheme": self.scheme,
            "horizon_years": self.horizon_years,
            "model": {"name": self.model_name, **self.model_params},
            "folds": self.folds if self.folds == "all" else list(self.folds),
            "seed": self.seed,
        }
        if self.min_dataset_version:
            raw["min_dataset_version"] = self.min_dataset_version
        if self.report_min_year is not None:
            raw["report_min_year"] = self.report_min_year
        if self.features is not None:
            raw["features"] = self.features.to_table()
        else:
            raw["feature_groups"] = list(self.feature_groups)
            if self.feature_columns is not None:
                raw["feature_columns"] = list(self.feature_columns)
            if self.exclude_feature_columns:
                raw["exclude_feature_columns"] = list(self.exclude_feature_columns)
        return raw

    def _canonical_payload(self) -> dict:
        # `diagnostic` is part of the identity: a probe hash can never
        # collide with an experiment hash over the same body
        payload = self.to_raw_dict()
        payload["model_name"] = self.model_name
        payload["model_params"] = self.model_params
        del payload["model"]
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
        payload = self._canonical_payload()
        del payload["name"]
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:8]

    def derived_name(self) -> str:
        if self.features is not None:
            tags = list(self.features.groups) + [
                f.replace("/", "-") for f in self.features.families
            ]
            feat = "-".join(tags) if tags else "cols"
        else:
            feat = "-".join(self.feature_groups) or "cols"
        return (
            f"era_probe_{self.model_name}_{feat}_{self.horizon_years}y_"
            f"{self.identity_hash}"
        )


# ------------------------------------------------------------------ data


def snapshot_year(frame: pd.DataFrame) -> np.ndarray:
    """The probe's target: calendar year of `snapshot_date` (stored
    upstream as date objects — normalised the same way the runner's era
    slicing does). A target from `key_meta`, not a feature."""
    return pd.to_datetime(frame["snapshot_date"]).dt.year.to_numpy(dtype=int)


def require_numeric_features(X: pd.DataFrame) -> None:
    """Refuse non-numeric feature columns by name. Auto-dropping would
    make the fitted feature set depend on parquet dtypes rather than on
    the config; the exclusion belongs in `[features].exclude_columns`."""
    bad = [
        c
        for c in X.columns
        if not (
            pd.api.types.is_numeric_dtype(X[c]) or pd.api.types.is_bool_dtype(X[c])
        )
    ]
    if bad:
        raise ConfigError(
            f"{len(bad)} selected feature column(s) are not numeric: {bad}; "
            "tree models cannot consume them and the probe does not encode "
            "them — exclude them via [features].exclude_columns (dates such "
            "as fund_datekey are trivial era leaks in any case)"
        )


# ------------------------------------------------------------------- run


def run_era_probe(
    config: EraProbeConfig,
    *,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    reports_dir: str | Path = DEFAULT_DIAGNOSTIC_REPORTS,
    config_path: str = "",
    access: SplitAccess = SplitAccess.STANDARD,
) -> dict:
    """Run the probe across its folds; log every fold (completed or
    failed) to the results store under the pseudo-label; write the
    report. Raises after logging on failure. With the default STANDARD
    access the diagnostic tags are refused — only
    `scripts/run_diagnostic.py` passes REGISTERED_DIAGNOSTIC."""
    from diagnostics.era_report import write_era_probe_report

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
        "label": SNAPSHOT_YEAR_LABEL,
        "model": config.model_name,
    }
    try:
        dataset = Dataset(Path(data_root) / config.dataset_version)
        config.check_dataset_version(dataset.version)
        feature_cols = config.resolve_feature_columns(dataset)
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
        collected: list[dict] = []
        importances: list[pd.Series] = []
        importance_kind = "impurity"
        fold_rules: list[tuple[int, str]] = []
        last_tree: tuple[int, DecisionTreeClassifier, list[str]] | None = None
        for fold in folds:
            split = dataset.apply_split(
                config.scheme, fold, config.horizon_years, access=access
            )
            train_rows, w_train = dataset.observable_fit_rows(
                split.train, config.horizon_years
            )
            test_rows, w_test = dataset.observable_fit_rows(
                split.test, config.horizon_years
            )
            X_train = train_rows[feature_cols]
            X_test = test_rows[feature_cols]
            require_numeric_features(X_train)
            y_train = snapshot_year(train_rows)
            y_test = snapshot_year(test_rows)
            classes = np.union1d(y_train, y_test).astype(int)

            model = build_probe_model(
                config.model_name, config.model_params, seed=config.seed
            )
            model.fit(X_train, y_train, sample_weight=w_train)
            proba = align_proba(model.predict_proba(X_test), model.classes_, classes)
            metrics = headline_metrics(
                y_test, proba, classes, w_test, y_train, w_train
            )
            fold_results.append(
                {
                    "fold": fold,
                    "n_train_rows": int(len(X_train)),
                    "effective_train_size": float(w_train.sum()),
                    "n_test_rows": int(len(X_test)),
                    "effective_test_size": float(w_test.sum()),
                    "train_years": [int(y) for y in np.unique(y_train)],
                    "metrics": metrics,
                }
            )
            collected.append(
                {
                    "fold": fold,
                    "y_true": y_test,
                    "proba": proba,
                    "classes": classes,
                    "w": w_test,
                    "y_train": y_train,
                    "w_train": w_train,
                }
            )
            importances.append(model.feature_importances())
            importance_kind = getattr(model, "importance_kind", importance_kind)
            estimator = getattr(model, "estimator_", None)
            if (
                isinstance(estimator, DecisionTreeClassifier)
                and model.constant_class_ is None
            ):
                names = [str(c) for c in model.classes_]
                fold_rules.append(
                    (fold, rules_text_multiclass(
                        estimator, feature_cols, class_names=names,
                        target_name="year",
                    ))
                )
                last_tree = (fold, estimator, names)
            store.append(
                {
                    **base_row,
                    "status": "completed",
                    "fold": fold,
                    "n_train_rows": len(X_train),
                    "effective_train_size": f"{float(w_train.sum()):.4f}",
                    "n_test_rows": len(X_test),
                    "metrics_json": metrics,
                }
            )

        # ------------------------------------------------ pooled view
        # each test row belongs to exactly one fold, so pooling is a
        # partition (never double counting); the prior pools train rows
        all_classes = np.unique(
            np.concatenate([c["classes"] for c in collected])
        ).astype(int)
        y_true = np.concatenate([c["y_true"] for c in collected])
        w = np.concatenate([c["w"] for c in collected])
        proba = np.vstack(
            [align_proba(c["proba"], c["classes"], all_classes) for c in collected]
        )
        y_train_all = np.concatenate([c["y_train"] for c in collected])
        w_train_all = np.concatenate([c["w_train"] for c in collected])
        y_pred = predict_year(proba, all_classes)
        pooled = headline_metrics(
            y_true, proba, all_classes, w, y_train_all, w_train_all
        )
        per_year = per_year_table(
            y_true, y_pred, w, all_classes, np.unique(y_train_all)
        )
        cm = confusion_matrix_weighted(y_true, y_pred, all_classes, w)
        min_year_block = (
            None
            if config.report_min_year is None
            else min_year_slice(y_true, proba, w, all_classes, config.report_min_year)
        )
        mean_importance = (
            pd.concat(importances, axis=1).fillna(0.0).mean(axis=1)
            .sort_values(ascending=False)
        )
        mean_importance.name = "importance"

        reports_dir = Path(reports_dir)
        artifacts: dict = {
            "confusion": render_confusion_heatmap(
                cm, path=reports_dir / f"{config.name}_confusion.png",
                title=f"{config.name}: year confusion (row-normalised, Σw)",
            ),
            "importance": render_importance_bar(
                mean_importance,
                path=reports_dir / f"{config.name}_importance.png",
                title=f"{config.name}: top feature importances ({importance_kind})",
            ),
            "importance_kind": importance_kind,
        }
        if fold_rules:
            artifacts["rules"] = _write_rules_file(
                reports_dir / f"{config.name}_rules.md",
                config, run_id, sha, dataset.version, fold_rules,
            )
        if last_tree is not None:
            diagram_fold, estimator, names = last_tree
            artifacts["tree_diagram"] = render_tree_diagram(
                estimator, feature_cols, reports_dir / f"{config.name}_tree.png",
                class_names=names,
            )
            artifacts["tree_diagram_fold"] = diagram_fold

        configurations_tried = store.configurations_tried(
            config.dataset_version, config.scheme, config.horizon_years,
            SNAPSHOT_YEAR_LABEL,
        )
        report_path = write_era_probe_report(
            path=reports_dir / f"{config.name}.md",
            config=config,
            run_id=run_id,
            git_sha=sha,
            dataset=dataset,
            feature_cols=feature_cols,
            fold_results=fold_results,
            pooled=pooled,
            per_year_df=per_year,
            min_year_block=min_year_block,
            importances=mean_importance,
            configurations_tried=configurations_tried,
            artifacts=artifacts,
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "folds": folds,
            "fold_results": fold_results,
            "pooled_metrics": pooled,
            "per_year": per_year,
            "configurations_tried": configurations_tried,
            "report_path": report_path,
            "artifacts": artifacts,
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


def _write_rules_file(
    path: Path,
    config: EraProbeConfig,
    run_id: str,
    sha: str,
    dataset_version: str,
    fold_rules: list[tuple[int, str]],
) -> Path:
    """Rule-extraction artifact for the tree arm: which feature
    thresholds identify which years."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Extracted tree rules — {config.name} (era probe, DIAGNOSTIC ONLY)",
        "",
        f"- dataset version: `{dataset_version}`",
        f"- config hash: `{config.config_hash}` — run `{run_id}`, "
        f"git `{sha}`, seed {config.seed}",
        f"- target: `{SNAPSHOT_YEAR_LABEL}` = year(snapshot_date); "
        f"weights `sample_weight_{config.horizon_years}y`; "
        f"scheme `{config.scheme}`",
        "",
        "One tree per fold. Each leaf names the year it predicts and its "
        "purity (weighted in-sample share of that year) — read the "
        "conditions as *what identifies the era*, not as a forecast.",
    ]
    for fold, text in fold_rules:
        lines += ["", f"## Fold {fold}", "", "```", text, "```"]
    path.write_text("\n".join(lines) + "\n")
    return path


def run_config_file(path: str | Path, **kwargs) -> dict:
    config = EraProbeConfig.from_file(path)
    return run_era_probe(config, config_path=str(path), **kwargs)
