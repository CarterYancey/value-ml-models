"""Persisted trained models: one bundle per completed training run.

Training and evaluation are distinct tasks. The runner fits one model per
walk-forward fold and saves them together as a bundle; `harness.evaluate`
re-scores a saved bundle under an `EvalConfig` (different top-K, score
thresholds) without refitting. The bundle pins everything scoring depends
on — dataset version, scheme, folds, label, feature columns, seed — so a
later evaluation cannot silently drift from what was trained: each fold's
model is only ever applied to its own fold's test rows.

Two bundle kinds share the layout convention:

- `ModelBundle` (`bundle_kind = "fold_models"`): the per-fold models of a
  walk-forward training run, re-scored by `vml-eval`.
- `DeploymentBundle` (`bundle_kind = "deployment"`): one model refit on
  all labeled rows for shipping (harness.deploy), scored by `vml-predict`.
  It carries no test rows and is never an evaluation artifact.

Bundle layout, one directory per training run (git-ignored — binaries are
artifacts, the provenance to recreate them is the config + results store):

    <models_dir>/<experiment>_<run_id>/
        bundle.json       provenance + the full train config (round-trips
                          through ExperimentConfig.to_raw_dict/from_dict)
        fold_models.pkl   {fold: fitted model}, stdlib pickle
    <models_dir>/<experiment>_deployment_<run_id>/
        bundle.json       provenance, as above, plus train-size stats
        model.pkl         the single fitted model, stdlib pickle
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from harness.config import ExperimentConfig
from harness.errors import HarnessError

#: Bump on any incompatible change to the bundle layout.
BUNDLE_FORMAT = 1

_META_FILE = "bundle.json"
_MODELS_FILE = "fold_models.pkl"


class ModelBundleError(HarnessError):
    """A model bundle directory is missing, malformed, or inconsistent."""


@dataclass(frozen=True)
class ModelBundle:
    train_config: ExperimentConfig
    run_id: str
    git_sha: str
    probabilistic: bool
    feature_columns: tuple[str, ...]
    #: the fitted model for each fold, keyed by fold id
    fold_models: dict[int, object]
    #: {fold: {"n_train_rows": int, "effective_train_size": float}} —
    #: carried into evaluation reports (the eval never sees train rows)
    fold_train_stats: dict[int, dict]

    def __post_init__(self):
        if set(self.fold_models) != set(self.fold_train_stats):
            raise ModelBundleError(
                f"fold models {sorted(self.fold_models)} do not match "
                f"train stats {sorted(self.fold_train_stats)}"
            )

    @property
    def folds(self) -> list[int]:
        return sorted(self.fold_models)

    def save(self, models_dir: str | Path) -> Path:
        out = Path(models_dir) / f"{self.train_config.name}_{self.run_id}"
        out.mkdir(parents=True, exist_ok=True)
        meta = {
            "bundle_format": BUNDLE_FORMAT,
            "bundle_kind": "fold_models",
            "saved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "git_sha": self.git_sha,
            "config_hash": self.train_config.config_hash,
            "probabilistic": self.probabilistic,
            "feature_columns": list(self.feature_columns),
            "train_config": self.train_config.to_raw_dict(),
            "fold_train_stats": {
                str(fold): stats for fold, stats in self.fold_train_stats.items()
            },
        }
        (out / _META_FILE).write_text(json.dumps(meta, indent=2, sort_keys=True))
        with open(out / _MODELS_FILE, "wb") as fh:
            pickle.dump(self.fold_models, fh)
        return out

    @classmethod
    def load(cls, bundle_dir: str | Path) -> "ModelBundle":
        root = Path(bundle_dir)
        if not (root / _META_FILE).exists():
            raise ModelBundleError(
                f"{root} is not a model bundle (missing {_META_FILE!r})"
            )
        meta = json.loads((root / _META_FILE).read_text())
        kind = meta.get("bundle_kind", "fold_models")
        if kind != "fold_models":
            raise ModelBundleError(
                f"{root} is a {kind!r} bundle, not a per-fold training "
                "bundle (deployment bundles are scored with vml-predict)"
            )
        if not (root / _MODELS_FILE).exists():
            raise ModelBundleError(
                f"{root} is not a model bundle (missing {_MODELS_FILE!r})"
            )
        fmt = meta.get("bundle_format")
        if fmt != BUNDLE_FORMAT:
            raise ModelBundleError(
                f"{root} has bundle_format {fmt!r}; this code reads "
                f"{BUNDLE_FORMAT}"
            )
        config = ExperimentConfig.from_dict(
            meta["train_config"], source=str(root / _META_FILE)
        )
        if config.config_hash != meta["config_hash"]:
            raise ModelBundleError(
                f"{root}: embedded train config hashes to "
                f"{config.config_hash}, bundle.json records "
                f"{meta['config_hash']} — the bundle was edited or is corrupt"
            )
        with open(root / _MODELS_FILE, "rb") as fh:
            fold_models = pickle.load(fh)
        return cls(
            train_config=config,
            run_id=meta["run_id"],
            git_sha=meta["git_sha"],
            probabilistic=bool(meta["probabilistic"]),
            feature_columns=tuple(meta["feature_columns"]),
            fold_models={int(f): m for f, m in fold_models.items()},
            fold_train_stats={
                int(f): s for f, s in meta["fold_train_stats"].items()
            },
        )


#: Bump on any incompatible change to the deployment-bundle layout.
DEPLOYMENT_BUNDLE_FORMAT = 1

_DEPLOYMENT_MODEL_FILE = "model.pkl"


@dataclass(frozen=True)
class DeploymentBundle:
    """One model refit on all labeled rows, for shipping (data/manual.md
    §4 rule 7). Carries no folds and no test rows: nothing loaded from
    here is ever an evaluation result — measurement stays with the
    walk-forward `ModelBundle`s."""

    train_config: ExperimentConfig
    run_id: str
    git_sha: str
    probabilistic: bool
    feature_columns: tuple[str, ...]
    model: object
    n_train_rows: int
    #: Σ sample_weight_{H}y over the rows actually fit
    effective_train_size: float

    def save(self, models_dir: str | Path) -> Path:
        out = (
            Path(models_dir)
            / f"{self.train_config.name}_deployment_{self.run_id}"
        )
        out.mkdir(parents=True, exist_ok=True)
        meta = {
            "bundle_format": DEPLOYMENT_BUNDLE_FORMAT,
            "bundle_kind": "deployment",
            "saved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "git_sha": self.git_sha,
            "config_hash": self.train_config.config_hash,
            "probabilistic": self.probabilistic,
            "feature_columns": list(self.feature_columns),
            "train_config": self.train_config.to_raw_dict(),
            "n_train_rows": self.n_train_rows,
            "effective_train_size": self.effective_train_size,
        }
        (out / _META_FILE).write_text(json.dumps(meta, indent=2, sort_keys=True))
        with open(out / _DEPLOYMENT_MODEL_FILE, "wb") as fh:
            pickle.dump(self.model, fh)
        return out

    @classmethod
    def load(cls, bundle_dir: str | Path) -> "DeploymentBundle":
        root = Path(bundle_dir)
        if not (root / _META_FILE).exists():
            raise ModelBundleError(
                f"{root} is not a model bundle (missing {_META_FILE!r})"
            )
        meta = json.loads((root / _META_FILE).read_text())
        kind = meta.get("bundle_kind", "fold_models")
        if kind != "deployment":
            raise ModelBundleError(
                f"{root} is a {kind!r} bundle, not a deployment bundle "
                "(per-fold training bundles are re-scored with vml-eval)"
            )
        fmt = meta.get("bundle_format")
        if fmt != DEPLOYMENT_BUNDLE_FORMAT:
            raise ModelBundleError(
                f"{root} has bundle_format {fmt!r}; this code reads "
                f"{DEPLOYMENT_BUNDLE_FORMAT}"
            )
        if not (root / _DEPLOYMENT_MODEL_FILE).exists():
            raise ModelBundleError(
                f"{root} is not a deployment bundle "
                f"(missing {_DEPLOYMENT_MODEL_FILE!r})"
            )
        config = ExperimentConfig.from_dict(
            meta["train_config"], source=str(root / _META_FILE)
        )
        if config.config_hash != meta["config_hash"]:
            raise ModelBundleError(
                f"{root}: embedded train config hashes to "
                f"{config.config_hash}, bundle.json records "
                f"{meta['config_hash']} — the bundle was edited or is corrupt"
            )
        with open(root / _DEPLOYMENT_MODEL_FILE, "rb") as fh:
            model = pickle.load(fh)
        return cls(
            train_config=config,
            run_id=meta["run_id"],
            git_sha=meta["git_sha"],
            probabilistic=bool(meta["probabilistic"]),
            feature_columns=tuple(meta["feature_columns"]),
            model=model,
            n_train_rows=int(meta["n_train_rows"]),
            effective_train_size=float(meta["effective_train_size"]),
        )
