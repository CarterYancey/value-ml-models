"""`vml-experiments`: what exists, what has run, and where to start.

The answer to "have I already tried this?", "which config is closest to
what I want?", "what did that run score — *against its baselines*?" and
"what did I conclude?" without grepping TOML files or re-reading reports.
It joins the configs in `experiments/` with the local results ledger
(`experiments/results.csv`) by config hash, with the sealed final-eval
record (`reports/final_evals.csv`) by experiment name, and with the
promoted-report index (`reports/promoted/`).

Listings are grouped by *cell* (label, horizon, scheme) and, inside a
cell, sorted by lift over the best baseline: a global sort across labels
would compare incomparable numbers. Each experiment carries its
free-text `note` — the one-line conclusion written into the config
(`note = "..."`, or `vml-promote <name> --note "..."`).

Usage:
    vml-experiments                       # every config, grouped by cell
    vml-experiments list --model lightgbm --label beat_spy
    vml-experiments list --sort path      # the flat, path-ordered view
    vml-experiments runs                  # ledger view: everything ever run
    vml-experiments show experiments/forest_3y_beat_spy.toml
    vml-experiments sweeps --out reports/sweep_digest.md   # cross-sweep digest
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tomllib
from pathlib import Path

import pandas as pd

from harness.config import ExperimentConfig
from harness.errors import ConfigError
from harness.results import ResultsStore
from models.registry import BASELINE_MODELS

DEFAULT_EXPERIMENTS = Path("experiments")
DEFAULT_RESULTS = Path("experiments/results.csv")
DEFAULT_FINAL_EVALS = Path("reports/final_evals.csv")
DEFAULT_PROMOTED = Path("reports/promoted")

#: metric shown as the headline in listings, first match wins
_HEADLINE_PREFIXES = ("precision_at_", "recall_at_prec_")
#: schemes only the dedicated scripts may evaluate (CLAUDE.md invariant 2
#: and the registered diagnostics)
_RESTRICTED_SCHEMES = {
    "holdout": "final eval only: scripts/run_final_eval.py",
    "entity_holdout": "diagnostic only: scripts/run_diagnostic.py",
    "random_kfold": "diagnostic only, leaky by design",
}
_NOTE_WIDTH = 48


def _print_table(rows: list[dict], columns: list[str],
                 group_key: str | None = None) -> None:
    """Fixed-width table. With `group_key`, rows are printed in runs of
    equal key with a header line before each run (column widths stay
    global so the runs line up)."""
    if not rows:
        print("(nothing found)")
        return
    cells = [[str(r.get(c, "")) for c in columns] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells))
              for i, c in enumerate(columns)]
    print("  ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print("  ".join("-" * w for w in widths))
    current = object()
    for r, row in zip(rows, cells):
        if group_key is not None and r.get(group_key) != current:
            current = r.get(group_key)
            if current:
                print(f"\n== {current}")
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)))


def _is_sweep(raw: dict) -> bool:
    return "cells" in raw or "grid" in raw or "sets" in raw


def _is_portfolio(raw: dict) -> bool:
    return "bundles" in raw or "prices_version" in raw


def _features_summary(config: ExperimentConfig) -> str:
    if config.features is not None:
        parts = list(config.features.groups) + list(config.features.families)
        if config.features.columns:
            parts.append(f"+{len(config.features.columns)}col")
        return ",".join(parts) or "cols"
    s = ",".join(config.feature_groups) or "cols"
    if config.exclude_feature_columns:
        s += f" -{len(config.exclude_feature_columns)}"
    return s


def _cell_key(dataset_version: str, scheme: str, horizon: int | str,
              label: str) -> str:
    """The comparison cell: only runs sharing all four are comparable."""
    return f"{label}  ·  {horizon}y  ·  {_scheme_tag(scheme)}  ·  {dataset_version}"


def config_cell(config: ExperimentConfig) -> tuple[str, str, int, str]:
    """(dataset_version, scheme, horizon, label) the run is *measured*
    on — a regression reframe is charged to its binary `eval_label`."""
    return (config.dataset_version, config.scheme, config.horizon_years,
            config.eval_label or config.label)


def short_metric(key: str) -> str:
    """`precision_at_20` -> `p@20`, `recall_at_prec_0.7` -> `recall@p0.7`."""
    if key.startswith("precision_at_"):
        return "p@" + key[len("precision_at_"):]
    if key.startswith("recall_at_prec_"):
        return "recall@p" + key[len("recall_at_prec_"):]
    return key


def headline_metric(metrics: dict) -> tuple[str, float] | None:
    """(key, value) of the headline metric, or None when there is none."""
    for prefix in _HEADLINE_PREFIXES:
        keys = sorted(k for k in metrics if k.startswith(prefix)
                      and isinstance(metrics[k], (int, float)))
        for k in keys:
            v = metrics[k]
            if v == v:  # not NaN
                return k, float(v)
    return None


def _fold_mean_metrics(rows: pd.DataFrame) -> dict:
    fold_metrics = pd.DataFrame(
        [json.loads(m) for m in rows["metrics_json"] if m]
    )
    if fold_metrics.empty:
        return {}
    return fold_metrics.mean(numeric_only=True).to_dict()


def _short_baseline_name(experiment: str, model: str) -> str:
    """`baseline_b2m_rank_3y_beat_spy` -> `b2m_rank`; falls back to the
    model name for baselines named otherwise."""
    if not experiment.startswith("baseline_"):
        return model
    s = experiment.removeprefix("baseline_")
    s = re.sub(r"_(label_)?\d+y_.*$", "", s)
    return s or model


class BaselineLookup:
    """Best baseline value per (cell, metric key), from the ledger's latest
    completed baseline runs — the same comparison every report embeds."""

    def __init__(self, store: ResultsStore):
        self._store = store
        self._cache: dict[tuple, pd.DataFrame] = {}

    def table(self, cell: tuple[str, str, int | None, str]) -> pd.DataFrame:
        if cell not in self._cache:
            dataset_version, scheme, horizon, label = cell
            if horizon is None:
                self._cache[cell] = pd.DataFrame()
            else:
                self._cache[cell] = self._store.model_comparison(
                    dataset_version, scheme, horizon, label, BASELINE_MODELS
                )
        return self._cache[cell]

    def best(self, cell: tuple[str, str, int, str],
             key: str) -> tuple[float, str] | None:
        """(value, short baseline name) of the best baseline on `key`."""
        table = self.table(cell)
        if table.empty or key not in table.columns:
            return None
        col = pd.to_numeric(table[key], errors="coerce")
        if col.isna().all():
            return None
        i = col.idxmax()
        row = table.loc[i]
        return float(col.loc[i]), _short_baseline_name(
            str(row["experiment"]), str(row["model"])
        )


def score_columns(metrics: dict, cell: tuple[str, str, int, str],
                  baselines: BaselineLookup) -> dict:
    """The headline metric, the best baseline on that same metric, and
    the lift between them, as display strings (all empty when the run
    recorded no headline metric)."""
    out = {"headline": "", "baseline": "", "lift": "", "_lift": None}
    hl = headline_metric(metrics)
    if hl is None:
        return out
    key, value = hl
    out["headline"] = f"{short_metric(key)}={value:.3f}"
    best = baselines.best(cell, key)
    if best is None:
        out["baseline"] = "none run"
        return out
    b_value, b_name = best
    out["baseline"] = f"{b_value:.3f} {b_name}"
    out["lift"] = f"{value - b_value:+.3f}"
    out["_lift"] = value - b_value
    return out


def _last_run_info(results: pd.DataFrame, config_hash: str,
                   cell: tuple[str, str, int, str],
                   baselines: BaselineLookup) -> dict:
    empty = {"runs": 0, "last_run": "", "last_status": "",
             "headline": "", "baseline": "", "lift": "", "_lift": None}
    if results.empty:
        return empty
    sel = results[results["config_hash"] == config_hash]
    if sel.empty:
        return empty
    last = sel.iloc[-1]
    info = {
        **empty,
        "runs": sel["run_id"].nunique(),
        "last_run": str(last["logged_utc"])[:10],
        "last_status": last["status"],
    }
    completed = sel[(sel["status"] == "completed") & (sel["metrics_json"] != "")]
    if not completed.empty:
        last_run_rows = completed[
            completed["run_id"] == completed.iloc[-1]["run_id"]
        ]
        info.update(score_columns(_fold_mean_metrics(last_run_rows), cell,
                                  baselines))
    return info


def load_final_evals(path: Path) -> list[dict]:
    """Rows of the sealed final-eval ledger (empty when it does not exist)."""
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _same_holdout_cell(a: dict, b: dict) -> bool:
    """Same (label, horizon, holdout window); a legacy row without a
    window matches on label + horizon (scripts/run_final_eval.py)."""
    if a.get("label") != b.get("label"):
        return False
    if str(a.get("horizon_years")) != str(b.get("horizon_years")):
        return False
    wa, wb = a.get("holdout_window", ""), b.get("holdout_window", "")
    return not wa or not wb or wa == wb


def final_eval_summary(final_evals: list[dict], config: ExperimentConfig) -> str:
    """`✓ look 2/3` — this experiment's completed holdout evaluations as
    look k of N in their cell (N counts every experiment's looks there,
    so a 2/3 says the cell's numbers are selection-biased); `✗` marks a
    failed attempt. Matched by experiment name: the holdout variant
    hashes differently from the walk-forward config it came from."""
    mine = [r for r in final_evals if r.get("experiment") == config.name
            and r.get("label") in (config.label, config.eval_label)]
    if not mine:
        return ""
    completed = [r for r in final_evals if r.get("status") == "completed"]
    marks = []
    for row in mine:
        if row.get("status") != "completed":
            marks.append("✗")
            continue
        cell = [r for r in completed if _same_holdout_cell(r, row)]
        k = next((i + 1 for i, r in enumerate(cell) if r is row), len(cell))
        marks.append(f"✓ look {k}/{len(cell)}")
    return ", ".join(marks)


def config_note(raw: dict) -> str:
    return " ".join(str(raw.get("note", "")).split())


def _truncate(s: str, width: int) -> str:
    return s if len(s) <= width else s[: width - 1] + "…"


def _scan_configs(experiments_dir: Path) -> list[dict]:
    entries = []
    for path in sorted(experiments_dir.rglob("*.toml")):
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            entries.append({"path": path, "error": f"unreadable: {exc}"})
            continue
        note = config_note(raw)
        if _is_sweep(raw):
            cells = raw.get("cells", [])
            entries.append({
                "path": path,
                "kind": "sweep",
                "name": raw.get("name", path.stem),
                "model": (raw.get("model", {}) or {}).get("name", "?"),
                "label": f"{len(cells)} cells" if cells else "?",
                "dataset": raw.get("dataset_version", "?"),
                "note": note,
            })
            continue
        if "diagnostic" in raw:
            # a registered-diagnostic config (scripts/run_diagnostic.py);
            # not an ExperimentConfig, so parsed only for the listing
            entries.append({
                "path": path,
                "kind": "sweep",  # rendered like a non-experiment row
                "name": raw.get("name", path.stem),
                "model": (raw.get("model", {}) or {}).get("name", "?"),
                "label": (
                    f"{raw['diagnostic']} (scripts/run_diagnostic.py)"
                ),
                "dataset": raw.get("dataset_version", "?"),
                "tag": "diagnostic",
                "note": note,
            })
            continue
        if _is_portfolio(raw):
            # a vml-backtest config: bundles + price panel, no model cell
            entries.append({
                "path": path,
                "kind": "sweep",  # rendered like a non-experiment row
                "name": raw.get("name", path.stem),
                "model": f"{len(raw.get('bundles', []))} bundles",
                "label": "vml-backtest",
                "dataset": raw.get("dataset_version", "?"),
                "tag": "portfolio",
                "note": note,
            })
            continue
        if set(raw) <= {"name", "top_k", "score_thresholds",
                        "precision_targets", "note"}:
            entries.append({
                "path": path,
                "kind": "sweep",  # rendered like a non-experiment row
                "name": raw.get("name", path.stem),
                "model": "-",
                "label": "[eval config] for vml-eval",
                "dataset": "-",
                "note": note,
            })
            continue
        try:
            config = ExperimentConfig.from_dict(raw, source=str(path))
        except ConfigError as exc:
            entries.append({"path": path, "error": str(exc)})
            continue
        entries.append({"path": path, "kind": "experiment", "config": config,
                        "note": note})
    return entries


def find_config(experiments_dir: Path, name: str) -> Path | None:
    """The config file whose experiment name is `name`, if any."""
    for entry in _scan_configs(experiments_dir):
        c = entry.get("config")
        if c is not None and c.name == name:
            return entry["path"]
        if c is None and entry.get("name") == name:
            return entry["path"]
    return None


def _matches(entry: dict, args) -> bool:
    config = entry.get("config")
    hay_parts = [str(entry["path"]), entry.get("note", "")]
    if config is not None:
        hay_parts += [config.name, config.model_name, config.label,
                      config.scheme, _features_summary(config)]
    else:
        hay_parts += [str(entry.get(k, "")) for k in ("name", "model", "label")]
    hay = " ".join(hay_parts).lower()
    if args.model and (
        (config.model_name if config else str(entry.get("model", "")))
        .lower().find(args.model.lower()) < 0
    ):
        return False
    if args.label and (
        (config.label if config else str(entry.get("label", "")))
        .lower().find(args.label.lower()) < 0
    ):
        return False
    if args.grep and args.grep.lower() not in hay:
        return False
    return True


def _scheme_tag(scheme: str) -> str:
    warn = _RESTRICTED_SCHEMES.get(scheme)
    return f"{scheme} ⚠ {warn}" if warn else scheme


def cmd_list(args) -> int:
    store = ResultsStore(Path(args.results))
    results = store.load()
    baselines = BaselineLookup(store)
    final_evals = load_final_evals(Path(args.final_evals))
    promoted = {p.name for p in Path(args.promoted).glob("*/") if p.is_dir()}
    rows = []
    for entry in _scan_configs(Path(args.experiments_dir)):
        if "error" in entry:
            rows.append({"config": str(entry["path"]), "model": "!",
                         "cell": entry["error"][:60], "_group": "unreadable",
                         "_order": (2, 0)})
            continue
        if not _matches(entry, args):
            continue
        if entry["kind"] == "sweep":
            tag = entry.get("tag", "sweep")
            rows.append({
                "config": str(entry["path"]),
                "model": entry["model"],
                "cell": f"[{tag}] {entry['label']}",
                "dataset": entry["dataset"],
                "note": _truncate(entry["note"], _NOTE_WIDTH),
                "_group": f"[{tag}] configs",
                "_order": (1, tag),
            })
            continue
        c = entry["config"]
        cell = config_cell(c)
        info = _last_run_info(results, c.config_hash, cell, baselines)
        lift = info["_lift"]
        rows.append({
            "config": str(entry["path"]),
            "model": c.model_name,
            "cell": f"{c.label} ({_scheme_tag(c.scheme)})",
            "features": _features_summary(c),
            "dataset": c.dataset_version
            + (f" (min {c.min_dataset_version})" if c.min_dataset_version
               else ""),
            "runs": info["runs"] or "",
            "last_run": info["last_run"],
            "status": info["last_status"],
            "headline": info["headline"],
            "baseline": info["baseline"],
            "lift": info["lift"],
            "final_eval": final_eval_summary(final_evals, c),
            "promoted": "★" if c.name in promoted else "",
            "note": _truncate(entry["note"], _NOTE_WIDTH),
            "_group": _cell_key(*cell),
            # within a cell: scored runs first, best lift first; then
            # scored-without-baseline, then never-run
            "_order": (0, _cell_key(*cell),
                       0 if lift is not None else (1 if info["headline"] else 2),
                       -(lift or 0.0), str(entry["path"])),
        })
    columns = ["config", "model", "cell", "features", "dataset", "runs",
               "last_run", "status", "headline", "baseline", "lift",
               "final_eval", "promoted", "note"]
    if args.sort == "cell":
        # the group header carries an experiment's cell; the column keeps
        # the non-experiment rows' descriptions
        rows.sort(key=lambda r: r["_order"])
        for r in rows:
            if r["_order"][0] == 0:
                r["cell"] = ""
        _print_table(rows, columns, group_key="_group")
    else:
        _print_table(rows, columns)
    return 0


def cmd_runs(args) -> int:
    store = ResultsStore(Path(args.results))
    results = store.load()
    if results.empty:
        print(f"no runs logged in {args.results}")
        return 0
    baselines = BaselineLookup(store)
    rows = []
    for experiment, grp in results.groupby("experiment", sort=False):
        last = grp.iloc[-1]
        try:  # backtest / deployment rows carry no horizon: no baseline cell
            horizon = int(last["horizon_years"])
        except (TypeError, ValueError):
            horizon = None
        cell = (str(last["dataset_version"]), str(last["scheme"]), horizon,
                str(last["label"]))
        info = _last_run_info(results, last["config_hash"], cell, baselines)
        rows.append({
            "experiment": experiment,
            "model": last["model"],
            "cell": f"{last['label']} ({last['scheme']})",
            "dataset": last["dataset_version"],
            "runs": grp["run_id"].nunique(),
            "last_run": str(last["logged_utc"])[:10],
            "status": last["status"],
            "headline": info["headline"],
            "baseline": info["baseline"],
            "lift": info["lift"],
            "config": last["config_path"],
        })
    rows.sort(key=lambda r: r["last_run"], reverse=True)
    _print_table(rows, ["experiment", "model", "cell", "dataset", "runs",
                        "last_run", "status", "headline", "baseline", "lift",
                        "config"])
    return 0


def cmd_show(args) -> int:
    target = Path(args.target)
    if not target.exists():
        # maybe an experiment name — find its config file by name
        found = find_config(Path(args.experiments_dir), args.target)
        if found is None:
            print(f"no config file or experiment named {args.target!r}")
            return 1
        target = found
    config = ExperimentConfig.from_file(target)
    with open(target, "rb") as fh:
        note = config_note(tomllib.load(fh))
    print(f"config:        {target}")
    print(f"name:          {config.name}")
    if note:
        print(f"note:          {note}")
    print(f"config hash:   {config.config_hash}")
    print(f"model:         {config.model_name} "
          f"{json.dumps(config.model_params, sort_keys=True)}")
    print(f"cell:          {config.label} — {config.horizon_years}y, "
          f"scheme {_scheme_tag(config.scheme)}")
    print(f"features:      {_features_summary(config)}")
    print(f"dataset:       {config.dataset_version}"
          + (f" (min {config.min_dataset_version})"
             if config.min_dataset_version else ""))
    print(f"seed:          {config.seed}   folds: {config.folds}")
    if config.top_k:
        print(f"top_k:         {list(config.top_k)}")
    if config.precision_targets:
        print(f"prec targets:  {list(config.precision_targets)}")
    if config.score_thresholds:
        print(f"thresholds:    {list(config.score_thresholds)}")

    store = ResultsStore(Path(args.results))
    results = store.load()
    baselines = BaselineLookup(store)
    cell = config_cell(config)
    sel = (results[results["config_hash"] == config.config_hash]
           if not results.empty else results)
    if sel is None or sel.empty:
        print("\nnever run (nothing in the results ledger for this hash)")
    else:
        print(f"\nruns ({sel['run_id'].nunique()}):")
        rows = []
        for run_id, grp in sel.groupby("run_id", sort=False):
            last = grp.iloc[-1]
            scores = score_columns(_fold_mean_metrics(grp), cell, baselines)
            rows.append({
                "run_id": run_id,
                "date": str(last["logged_utc"])[:10],
                "status": last["status"],
                "folds": len(grp),
                "headline": scores["headline"],
                "baseline": scores["baseline"],
                "lift": scores["lift"],
                "git_sha": str(last["git_sha"])[:10],
            })
        _print_table(rows, ["run_id", "date", "status", "folds", "headline",
                            "baseline", "lift", "git_sha"])
    baseline_table = baselines.table(cell)
    if not baseline_table.empty:
        print("\nbaselines in this cell (latest completed run each):")
        rows = []
        for _, b in baseline_table.iterrows():
            hl = headline_metric(b.to_dict())
            rows.append({
                "experiment": b["experiment"],
                "model": b["model"],
                "headline": f"{short_metric(hl[0])}={hl[1]:.3f}" if hl else "",
            })
        _print_table(rows, ["experiment", "model", "headline"])
    else:
        print("\nno baseline runs in this cell — run "
              "scripts/run_baselines.py before reading the numbers above")
    final = final_eval_summary(load_final_evals(Path(args.final_evals)), config)
    if final:
        print(f"\nfinal evals (sealed holdout): {final}")
    report = Path("reports") / f"{config.name}.md"
    if report.exists():
        print(f"\nreport: {report}")
    promoted = Path(args.promoted) / config.name
    if promoted.is_dir():
        print(f"promoted: {promoted}/")
    return 0


# ----------------------------------------------------------------------
# `sweeps`: the cross-sweep digest

DEFAULT_SWEEP_REPORTS = Path("reports/sweeps")
_SWEEP_ID_COLS = {"run", "candidate", "status", "label", "eval_label",
                  "horizon_years", "feature_set", "param_set", "set_params",
                  "seed", "grid_params", "sampled_params", "config_hash"}


def _load_json_col(v) -> dict:
    if isinstance(v, str) and v.strip().startswith("{"):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return {}
    return {}


def _sweep_feature_names(sweep_path: Path | None) -> tuple[list[str], str, str]:
    """(feature-set description per index, dataset_version, model name) from
    a sweep config, or ([], "", "") when the config is gone."""
    if sweep_path is None:
        return [], "", ""
    try:
        from harness.sweep import SweepConfig
        sweep = SweepConfig.from_file(sweep_path)
    except Exception:  # noqa: BLE001 — a stale/unparseable sweep still digests
        try:
            with open(sweep_path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError):
            return [], "", ""
        return ([], str(raw.get("dataset_version", "")),
                str((raw.get("model") or {}).get("name", "")))
    names: list[str] = []
    for spec in sweep.feature_specs:
        parts = list(spec.groups) + list(spec.families)
        if spec.columns:
            parts.append(f"+{len(spec.columns)}col")
        names.append(",".join(parts) or "cols")
    for fs in sweep.feature_sets:
        s = ",".join(fs.groups) or "cols"
        if fs.columns is not None:
            s += f" ({len(fs.columns)} cols)"
        if fs.exclude:
            s += f" -{len(fs.exclude)}"
        names.append(s)
    return names, sweep.dataset_version, sweep.model_name


def load_sweep_runs(sweep_reports: Path, experiments_dir: Path,
                    results: pd.DataFrame) -> list[dict]:
    """Every completed run of every sweep summary CSV under
    `reports/sweeps/`, one flat record each: cell, features (described
    from the sweep config where it still exists), merged params, pooled
    metrics. `dataset_version`/`model` come from the sweep config, else
    from the ledger by config hash."""
    by_hash = {}
    if not results.empty:
        last = results.drop_duplicates("config_hash", keep="last")
        by_hash = last.set_index("config_hash")[
            ["dataset_version", "model"]].to_dict("index")
    out = []
    for csv_path in sorted(sweep_reports.glob("*/*_summary.csv")):
        sweep_name = csv_path.parent.name
        if csv_path.name != f"{sweep_name}_summary.csv":
            continue  # the *_summary_seeds.csv companion
        try:
            df = pd.read_csv(csv_path)
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError):
            continue
        feat_names, ds_version, model = _sweep_feature_names(
            find_config(experiments_dir, sweep_name))
        metric_cols = [c for c in df.columns if c not in _SWEEP_ID_COLS]
        for _, r in df.iterrows():
            if str(r.get("status", "completed")) != "completed":
                continue
            h = by_hash.get(str(r.get("config_hash", "")), {})
            params = {}
            for col in ("set_params", "grid_params", "sampled_params"):
                params.update(_load_json_col(r.get(col)))
            fs_idx = r.get("feature_set")
            try:
                fs_idx = int(fs_idx)
            except (TypeError, ValueError):
                fs_idx = None
            features = (feat_names[fs_idx] if fs_idx is not None
                        and fs_idx < len(feat_names) else
                        (f"set {fs_idx}" if fs_idx is not None else ""))
            metrics = {c: r[c] for c in metric_cols
                       if isinstance(r[c], (int, float)) and r[c] == r[c]}
            label = str(r.get("eval_label") or r.get("label") or "")
            if isinstance(r.get("eval_label"), float):  # NaN
                label = str(r.get("label") or "")
            try:
                horizon = int(r["horizon_years"])
            except (KeyError, TypeError, ValueError):
                horizon = None
            out.append({
                "sweep": sweep_name,
                "run": str(r.get("run", "")),
                "label": label,
                "horizon": horizon,
                "dataset_version": ds_version or str(h.get("dataset_version", "")),
                "model": model or str(h.get("model", "")),
                "features": features,
                "params": params,
                "seed": r.get("seed", ""),
                "metrics": metrics,
            })
    return out


def _pick_metric(metrics: dict, preferred: str) -> tuple[str, float] | None:
    if preferred in metrics:
        return preferred, float(metrics[preferred])
    return headline_metric(metrics)


def _fmt_params(params: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(params.items())) or "-"


def _bin_continuous(by_value: dict[str, list[float]],
                    max_distinct: int = 6) -> dict[str, list[float]]:
    """Random-search axes have one run per sampled value, which says
    nothing; numeric axes with many distinct values are binned into
    quartile ranges so the trend shows."""
    if len(by_value) <= max_distinct:
        return by_value
    try:
        numeric = {float(k): v for k, v in by_value.items()}
    except ValueError:
        return by_value
    keys = sorted(numeric)
    edges = [keys[int(q * (len(keys) - 1))] for q in (0.25, 0.5, 0.75)]
    binned: dict[str, list[float]] = {}
    lo = keys[0]
    for i, hi in enumerate([*edges, keys[-1]]):
        label = f"{lo:g}..{hi:g}"
        for k in keys:
            in_bin = (k <= hi) if i == 0 else (lo < k <= hi)
            if in_bin:
                binned.setdefault(label, []).extend(numeric[k])
        lo = hi
    return binned


def render_sweep_digest(runs: list[dict], baselines: BaselineLookup,
                        metric: str, top: int, label_filter: str = "") -> str:
    """Markdown: per cell, the top runs across every sweep and, for
    features and each swept parameter, the mean metric by value —
    "what wins" — with n. Pooled numbers, so ranking only."""
    lines = [
        "# Sweep digest",
        "",
        f"Every completed run of every sweep summary under `reports/sweeps/`, "
        f"grouped by cell. Metric: `{metric}` where the sweep recorded it, "
        "else the row's headline metric (named per row). Pooled over folds "
        "and **selection-biased** — this ranks candidates, it does not "
        "report results; `lift` is against the best baseline in the cell.",
        "",
    ]
    cells: dict[tuple, list[dict]] = {}
    for r in runs:
        if label_filter and label_filter.lower() not in r["label"].lower():
            continue
        picked = _pick_metric(r["metrics"], metric)
        if picked is None or r["horizon"] is None:
            continue
        r = {**r, "metric_key": picked[0], "value": picked[1]}
        cells.setdefault((r["label"], r["horizon"], r["dataset_version"]),
                         []).append(r)
    if not cells:
        lines.append("_no sweep runs found_")
        return "\n".join(lines) + "\n"
    for (label, horizon, ds), rows in sorted(cells.items()):
        rows.sort(key=lambda r: -r["value"])
        n_sweeps = len({r["sweep"] for r in rows})
        lines.append(f"## {label} · {horizon}y · {ds or 'dataset ?'}")
        lines.append("")
        lines.append(f"{len(rows)} runs from {n_sweeps} sweep(s).")
        key = rows[0]["metric_key"]
        best = baselines.best((ds, "walkforward", horizon, label), key) if ds else None
        if best is not None:
            lines.append(f"Best baseline on `{short_metric(key)}`: "
                         f"{best[0]:.3f} ({best[1]}).")
        else:
            lines.append("No baseline run in this cell — lifts unavailable.")
        lines.append("")
        lines.append("| # | sweep | model | features | params | metric | value | lift | seed |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(rows[:top], 1):
            lift = ""
            if best is not None and r["metric_key"] == key:
                lift = f"{r['value'] - best[0]:+.3f}"
            lines.append(
                f"| {i} | {r['sweep']} | {r['model']} | {r['features'] or '-'} | "
                f"{_fmt_params(r['params'])} | {short_metric(r['metric_key'])} | "
                f"{r['value']:.3f} | {lift} | {r['seed']} |"
            )
        lines.append("")
        # what wins: mean metric by value, for every axis with >= 2 values
        same = [r for r in rows if r["metric_key"] == key]
        axes: dict[str, dict[str, list[float]]] = {}
        for r in same:
            if r["features"]:
                axes.setdefault("features", {}).setdefault(
                    r["features"], []).append(r["value"])
            if r["model"]:
                axes.setdefault("model", {}).setdefault(
                    r["model"], []).append(r["value"])
            for k, v in r["params"].items():
                axes.setdefault(k, {}).setdefault(str(v), []).append(r["value"])
        wins = []
        for axis, by_value in axes.items():
            if len(by_value) < 2:
                continue
            by_value = _bin_continuous(by_value)
            ranked = sorted(((sum(v) / len(v), len(v), val)
                             for val, v in by_value.items()), reverse=True)
            wins.append(f"- **{axis}**: " + "; ".join(
                f"{val} → {m:.3f} (n={n})" for m, n, val in ranked))
        if wins:
            lines.append(f"What wins on `{short_metric(key)}` (mean over runs "
                         "sharing the value; n = runs):")
            lines.append("")
            lines.extend(wins)
            lines.append("")
    return "\n".join(lines) + "\n"


def cmd_sweeps(args) -> int:
    store = ResultsStore(Path(args.results))
    results = store.load()
    runs = load_sweep_runs(Path(args.sweep_reports), Path(args.experiments_dir),
                           results)
    text = render_sweep_digest(runs, BaselineLookup(store), args.metric,
                               args.top, args.label)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
        print(f"digest -> {args.out} ({len(runs)} sweep runs)")
    else:
        print(text, end="")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Browse experiment configs and their run history."
    )
    parser.add_argument("--experiments-dir", default=str(DEFAULT_EXPERIMENTS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--final-evals", default=str(DEFAULT_FINAL_EVALS),
                        help="the sealed final-eval ledger")
    parser.add_argument("--promoted", default=str(DEFAULT_PROMOTED),
                        help="the promoted-reports directory")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser(
        "list", help="every config under experiments/, run status joined")
    p_list.add_argument("--model", default="",
                        help="substring filter on the model name")
    p_list.add_argument("--label", default="",
                        help="substring filter on the label")
    p_list.add_argument("--grep", default="",
                        help="substring filter across all fields (notes too)")
    p_list.add_argument("--sort", choices=("cell", "path"), default="cell",
                        help="'cell' (default) groups by label/horizon/"
                        "scheme and ranks by lift over the best baseline "
                        "inside each group; 'path' is the flat listing")

    sub.add_parser("runs", help="everything in the results ledger, "
                                "grouped by experiment")

    p_show = sub.add_parser(
        "show", help="one config in full, with its run history")
    p_show.add_argument("target", help="config path or experiment name")

    p_sw = sub.add_parser(
        "sweeps", help="cross-sweep digest: per cell, the top runs over "
        "every sweep and what wins per feature set / parameter")
    p_sw.add_argument("--metric", default="precision_at_20",
                      help="pooled metric to rank on where recorded "
                      "(default precision_at_20; else the row's headline)")
    p_sw.add_argument("--top", type=int, default=8,
                      help="rows per cell (default 8)")
    p_sw.add_argument("--label", default="",
                      help="substring filter on the cell label")
    p_sw.add_argument("--sweep-reports", default=str(DEFAULT_SWEEP_REPORTS))
    p_sw.add_argument("--out", default="",
                      help="write the markdown here instead of printing")

    args = parser.parse_args(argv)
    if args.command in (None, "list"):
        for attr, default in (("model", ""), ("label", ""), ("grep", ""),
                              ("sort", "cell")):
            if not hasattr(args, attr):
                setattr(args, attr, default)
        return cmd_list(args)
    if args.command == "runs":
        return cmd_runs(args)
    if args.command == "sweeps":
        return cmd_sweeps(args)
    return cmd_show(args)


if __name__ == "__main__":
    sys.exit(main())
