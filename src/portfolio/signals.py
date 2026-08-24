"""Scoring a point-in-time cross-section with year-resolved models.

A `ModelSet` is the backtest's stand-in for the deployed multi-model
`vml-predict` run: the same bundles' *training configurations*, with the
model applied at a trade date resolved per (bundle, trade year):

- a year the bundle has a walk-forward fold for uses that fold's model —
  fitted on an expanding window that ends, purged and embargoed, before
  the year begins;
- a year past the bundle's last fold (the upstream fold calendar stops
  where test labels stop being observable, but a live portfolio keeps
  trading) is served by the `model_update` policy:
  * ``"refit"`` — a simulated year-end deployment refit: the bundle's
    config refit on every row whose label window was fully observable by
    Jan 1 of the trade year (`snapshot_date + horizon + label_lag_days`).
    This is data/manual.md §4 rule 7 applied point-in-time — it reads no
    split tags, builds no test set, and its scores are only ever inputs
    to the simulation, never label-evaluated;
  * ``"frozen"`` — keep using the last fold's model unchanged.

Static deployment bundles remain refused structurally
(`ModelBundle.load` rejects the kind): a model refit on *all* labeled
history has seen the whole backtest period, and scoring it there is
leakage, not measurement.

Filters are declared, validated column screens over the feature/rank
groups only — a filter can never reference a label, and a column the
manifest doesn't declare is an error, not an empty screen. NULL fails
every filter: missingness never passes a screen.
"""

from __future__ import annotations

import operator
from pathlib import Path

import pandas as pd

from harness.dataset import SELECTION_SCHEME, Dataset
from harness.errors import ConfigError, DatasetValidationError
from harness.model_store import ModelBundle, ModelBundleError
from models.registry import build_model
from portfolio.config import BacktestConfig, FilterSpec

_OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

#: manifest groups a filter may reference — labels and weights are
#: outcomes and structurally out of reach
FILTERABLE_GROUPS = ("features", "ranks", "sector_ranks")


class ModelSet:
    """The walk-forward fold models of several training runs, keyed by
    (bundle, trade year)."""

    def __init__(self, bundle_dirs: list[str | Path]):
        if not bundle_dirs:
            raise ConfigError("a backtest needs at least one model bundle")
        self.bundle_dirs = [Path(d) for d in bundle_dirs]
        self.bundles = [ModelBundle.load(d) for d in self.bundle_dirs]
        for d, b in zip(self.bundle_dirs, self.bundles):
            if b.train_config.scheme != SELECTION_SCHEME:
                raise ModelBundleError(
                    f"{d} was trained under scheme "
                    f"{b.train_config.scheme!r}; backtests may only consume "
                    f"{SELECTION_SCHEME!r} fold models"
                )
        self.names = _column_names(self.bundles)

    @property
    def score_columns(self) -> list[str]:
        return [f"score_{n}" for n in self.names]

    def first_serveable_year(self) -> int:
        """Earliest trade year every bundle can serve: the latest of the
        bundles' first fold years. The upstream fold calendar starts a
        horizon's folds only once the training window is deep enough —
        refitting before that point would sidestep that judgment."""
        return max(min(b.fold_models) for b in self.bundles)

    def prepare(
        self,
        years: list[int],
        dataset: Dataset,
        policy: str,
        label_lag_days: int,
    ) -> None:
        """Resolve the model for every (bundle, trade year) up front:
        fold model where a fold exists, else the `model_update` policy
        (see the module docstring). Populates `self.provenance` (one
        entry per bundle: fold years used, policy-served years, per-year
        refit sizes) for the report."""
        self._year_models: dict[tuple[int, int], object] = {}
        self.provenance: list[dict] = []
        for i, (d, b) in enumerate(zip(self.bundle_dirs, self.bundles)):
            first, last = min(b.fold_models), max(b.fold_models)
            info: dict = {
                "fold_years": [],
                "policy": policy,
                "policy_years": [],
                "refit_stats": {},
            }
            for year in years:
                if year in b.fold_models:
                    self._year_models[(i, year)] = b.fold_models[year]
                    info["fold_years"].append(year)
                elif year > last:
                    if policy == "frozen":
                        self._year_models[(i, year)] = b.fold_models[last]
                    else:
                        model, stats = _refit_as_of_year(
                            b, dataset, year, label_lag_days
                        )
                        self._year_models[(i, year)] = model
                        info["refit_stats"][year] = stats
                    info["policy_years"].append(year)
                else:
                    raise ConfigError(
                        f"bundle {d} cannot serve trade year {year}: its "
                        f"folds span {first}–{last} with a gap or a "
                        "too-early start — narrow the window"
                    )
            self.provenance.append(info)

    def validate_against(self, config: BacktestConfig, dataset: Dataset) -> None:
        unknown = sorted(set(config.min_scores) - set(self.names))
        if unknown:
            raise ConfigError(
                f"[signal.min_scores] names {unknown} match no loaded "
                f"bundle; bundles are keyed by their config names: "
                f"{self.names}"
            )
        any_floor = config.min_score is not None or config.min_scores
        for d, b in zip(self.bundle_dirs, self.bundles):
            trained_on = b.train_config.dataset_version
            if trained_on != config.dataset_version:
                raise ConfigError(
                    f"bundle {d} was trained on {trained_on!r} but the "
                    f"backtest pins {config.dataset_version!r}; results "
                    "across dataset versions are never compared — retrain "
                    "or re-pin"
                )
            missing = sorted(set(b.feature_columns) - set(dataset.data.columns))
            if missing:
                raise DatasetValidationError(
                    f"dataset {dataset.version} lacks feature columns bundle "
                    f"{d} was trained on: {missing}"
                )
            if any_floor and not b.probabilistic:
                raise ConfigError(
                    f"a min_score floor is set but bundle {d} is not "
                    "probabilistic — raw margins have no common scale to "
                    "threshold"
                )
            if config.combine in ("product", "mean", "min") and not b.probabilistic:
                raise ConfigError(
                    f"combine = {config.combine!r} needs probabilistic "
                    f"scores but bundle {d} is not probabilistic; use "
                    "combine = 'mean_rank'"
                )

    def score(self, frame: pd.DataFrame, year: int) -> pd.DataFrame:
        """`frame` plus one `score_<name>` column per bundle, scored by
        each bundle's model for the trade `year` (resolved by
        `prepare`)."""
        if not hasattr(self, "_year_models"):
            raise ConfigError(
                "ModelSet.prepare(...) must run before scoring — models "
                "are resolved per (bundle, trade year)"
            )
        out = frame.copy()
        if out.empty:
            # a cross-section can empty out legitimately (e.g. the
            # dataset's last snapshots age past the staleness cap while
            # the price panel keeps going) — that month simply has no
            # candidates, which is the engine's cash-hold case
            for name in self.names:
                out[f"score_{name}"] = pd.Series(dtype=float)
            return out
        for i, (d, b, name) in enumerate(
            zip(self.bundle_dirs, self.bundles, self.names)
        ):
            model = self._year_models.get((i, year))
            if model is None:
                raise ConfigError(
                    f"bundle {d} has no model resolved for trade year "
                    f"{year} — the year is outside the prepared window"
                )
            missing = sorted(set(b.feature_columns) - set(frame.columns))
            if missing:
                raise DatasetValidationError(
                    f"cross-section lacks feature columns bundle {d} needs: "
                    f"{missing}"
                )
            out[f"score_{name}"] = model.predict_scores(
                frame[list(b.feature_columns)]
            )
        return out


def _refit_as_of_year(
    bundle: ModelBundle, dataset: Dataset, year: int, label_lag_days: int
) -> tuple[object, dict]:
    """A simulated year-end deployment refit for trade `year`: the
    bundle's config refit on every row whose label window was fully
    observable by Jan 1 of `year` — `snapshot_date + horizon +
    label_lag_days` (the lag covers the terminal-month averaging and
    delisting settlement in the upstream label build). This is
    data/manual.md §4 rule 7 applied point-in-time: no split tags are
    read, no test set exists, and the fit's scores are only simulation
    inputs. All snapshot kinds and delisted rows stay in, exactly as in
    deployment training."""
    config = bundle.train_config
    cutoff = pd.Timestamp(year, 1, 1)
    data = dataset.data
    snapshot = pd.to_datetime(data["snapshot_date"])
    observable_by = (
        snapshot
        + pd.DateOffset(years=config.horizon_years)
        + pd.Timedelta(days=label_lag_days)
    )
    eligible = data[observable_by <= cutoff]
    fit = dataset.fit_data(
        eligible,
        config.label,
        list(bundle.feature_columns),
        config.horizon_years,
    )
    if not len(fit.X):
        raise ConfigError(
            f"refit for trade year {year} of {config.name!r} has no rows "
            f"with labels observable by {cutoff.date()} — the window "
            "starts too early for this horizon"
        )
    model = build_model(config.model_name, config.model_params, config.seed)
    model.fit(fit.X, fit.y, sample_weight=fit.sample_weight)
    return model, {
        "n_train_rows": len(fit.X),
        "effective_train_size": fit.effective_size,
        "last_usable_snapshot": str(
            pd.to_datetime(eligible["snapshot_date"]).max().date()
        ),
    }


def _column_names(bundles: list[ModelBundle]) -> list[str]:
    """One unique suffix per bundle: the config name, disambiguated by
    run_id when two bundles share one (mirrors vml-predict's CSVs)."""
    names = [b.train_config.name for b in bundles]
    return [
        f"{name}_{b.run_id}" if names.count(name) > 1 else name
        for name, b in zip(names, bundles)
    ]


def validate_filter_columns(
    filters: tuple[FilterSpec, ...], dataset: Dataset, where: str
) -> None:
    """Every filter column must be declared by a filterable manifest
    group — labels and weights are structurally unreachable, and a typo
    is an error rather than an empty screen."""
    allowed = {c for g in FILTERABLE_GROUPS for c in dataset.columns(g)}
    for f in filters:
        if f.column not in allowed:
            raise ConfigError(
                f"{where} filter references {f.column!r}, which is not in "
                f"the manifest's {list(FILTERABLE_GROUPS)} groups (labels "
                "and weights can never be screened on)"
            )


def apply_filters(
    frame: pd.DataFrame, filters: tuple[FilterSpec, ...]
) -> pd.DataFrame:
    """Rows passing every filter. NULL fails: a stock with no value for a
    screened column is screened out, never waved through."""
    if not filters:
        return frame
    mask = pd.Series(True, index=frame.index)
    for f in filters:
        col = frame[f.column]
        mask &= col.notna() & _OPS[f.op](col, f.value)
    return frame[mask]


def apply_min_score(
    frame: pd.DataFrame, floors: dict[str, float]
) -> pd.DataFrame:
    """Rows where every floored model's score exceeds its floor
    (`floors`: score column -> floor; columns without a floor are not
    screened)."""
    if not floors:
        return frame
    mask = pd.Series(True, index=frame.index)
    for col, floor in floors.items():
        mask &= frame[col] > floor
    return frame[mask]


def score_floors(config: BacktestConfig, names: list[str]) -> dict[str, float]:
    """The per-score-column floors a config declares: the scalar
    `min_score` for every model, overridden per model by
    `[signal.min_scores]` entries (keyed by bundle config name)."""
    floors: dict[str, float] = {}
    for name in names:
        floor = config.min_scores.get(name, config.min_score)
        if floor is not None:
            floors[f"score_{name}"] = float(floor)
    return floors


def combine_scores(
    frame: pd.DataFrame, score_columns: list[str], mode: str
) -> pd.Series:
    """Collapse per-model scores into one ranking/sizing score (higher is
    better in every mode). `product` is the AllProb combination: the
    scores are *not* independent, so the product is a conviction ranking,
    not a joint probability — reports say so."""
    scores = frame[score_columns]
    if mode == "product":
        return scores.prod(axis=1)
    if mode == "mean":
        return scores.mean(axis=1)
    if mode == "min":
        return scores.min(axis=1)
    if mode == "mean_rank":
        ranks = pd.DataFrame(
            {c: scores[c].rank(ascending=False, method="min") for c in scores}
        )
        return -ranks.mean(axis=1)
    raise ConfigError(f"unknown combine mode {mode!r}")
