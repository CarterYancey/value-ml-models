"""`vml-experiments`: what exists, what has run, and where to start.

The answer to "have I already tried this?", "which config is closest to
what I want?", and "what did that run score?" without grepping TOML files
or re-reading the docs. It joins the configs in `experiments/` with the
local results ledger (`experiments/results.csv`) by config hash.

Usage:
    vml-experiments                       # every config, run status joined
    vml-experiments list --model lightgbm --label beat_spy
    vml-experiments runs                  # ledger view: everything ever run
    vml-experiments show experiments/forest_3y_beat_spy.toml
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

import pandas as pd

from harness.config import ExperimentConfig
from harness.errors import ConfigError
from harness.results import ResultsStore

DEFAULT_EXPERIMENTS = Path("experiments")
DEFAULT_RESULTS = Path("experiments/results.csv")

#: metric shown as the headline in listings, first match wins
_HEADLINE_PREFIXES = ("precision_at_", "recall_at_prec_")


def _print_table(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        print("(nothing found)")
        return
    cells = [[str(r.get(c, "")) for c in columns] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells))
              for i, c in enumerate(columns)]
    print("  ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print("  ".join("-" * w for w in widths))
    for row in cells:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)))


def _is_sweep(raw: dict) -> bool:
    return "cells" in raw or "grid" in raw or "sets" in raw


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


def _headline_metric(metrics: dict) -> str:
    for prefix in _HEADLINE_PREFIXES:
        keys = sorted(k for k in metrics if k.startswith(prefix)
                      and isinstance(metrics[k], (int, float)))
        if keys:
            v = metrics[keys[0]]
            return f"{keys[0]}={v:.3f}" if v == v else ""
    return ""


def _last_run_info(results: pd.DataFrame, config_hash: str) -> dict:
    if results.empty:
        return {"runs": 0, "last_run": "", "last_status": "", "headline": ""}
    sel = results[results["config_hash"] == config_hash]
    if sel.empty:
        return {"runs": 0, "last_run": "", "last_status": "", "headline": ""}
    runs = sel["run_id"].nunique()
    last = sel.iloc[-1]
    headline = ""
    completed = sel[(sel["status"] == "completed") & (sel["metrics_json"] != "")]
    if not completed.empty:
        last_run_rows = completed[
            completed["run_id"] == completed.iloc[-1]["run_id"]
        ]
        fold_metrics = pd.DataFrame(
            [json.loads(m) for m in last_run_rows["metrics_json"]]
        )
        headline = _headline_metric(
            fold_metrics.mean(numeric_only=True).to_dict()
        )
        if headline:
            headline += " (fold mean)"
    return {
        "runs": runs,
        "last_run": str(last["logged_utc"])[:10],
        "last_status": last["status"],
        "headline": headline,
    }


def _scan_configs(experiments_dir: Path) -> list[dict]:
    entries = []
    for path in sorted(experiments_dir.rglob("*.toml")):
        try:
            with open(path, "rb") as fh:
                raw = tomllib.load(fh)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            entries.append({"path": path, "error": f"unreadable: {exc}"})
            continue
        if _is_sweep(raw):
            cells = raw.get("cells", [])
            entries.append({
                "path": path,
                "kind": "sweep",
                "name": raw.get("name", path.stem),
                "model": (raw.get("model", {}) or {}).get("name", "?"),
                "label": f"{len(cells)} cells" if cells else "?",
                "dataset": raw.get("dataset_version", "?"),
            })
            continue
        if set(raw) <= {"name", "top_k", "score_thresholds",
                        "precision_targets"}:
            entries.append({
                "path": path,
                "kind": "sweep",  # rendered like a non-experiment row
                "name": raw.get("name", path.stem),
                "model": "-",
                "label": "[eval config] for vml-eval",
                "dataset": "-",
            })
            continue
        try:
            config = ExperimentConfig.from_dict(raw, source=str(path))
        except ConfigError as exc:
            entries.append({"path": path, "error": str(exc)})
            continue
        entries.append({"path": path, "kind": "experiment", "config": config})
    return entries


def _matches(entry: dict, args) -> bool:
    config = entry.get("config")
    hay_parts = [str(entry["path"])]
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


def cmd_list(args) -> int:
    results = ResultsStore(Path(args.results)).load()
    rows = []
    for entry in _scan_configs(Path(args.experiments_dir)):
        if "error" in entry:
            rows.append({"config": str(entry["path"]),
                         "model": "!", "cell": entry["error"][:60]})
            continue
        if not _matches(entry, args):
            continue
        if entry["kind"] == "sweep":
            rows.append({
                "config": str(entry["path"]),
                "model": entry["model"],
                "cell": f"[sweep] {entry['label']}",
                "dataset": entry["dataset"],
            })
            continue
        c = entry["config"]
        info = _last_run_info(results, c.config_hash)
        rows.append({
            "config": str(entry["path"]),
            "model": c.model_name,
            "cell": f"{c.label} ({c.scheme})",
            "features": _features_summary(c),
            "dataset": c.dataset_version
            + (f" (min {c.min_dataset_version})" if c.min_dataset_version
               else ""),
            "runs": info["runs"] or "",
            "last_run": info["last_run"],
            "status": info["last_status"],
            "headline": info["headline"],
        })
    _print_table(rows, ["config", "model", "cell", "features", "dataset",
                        "runs", "last_run", "status", "headline"])
    return 0


def cmd_runs(args) -> int:
    results = ResultsStore(Path(args.results)).load()
    if results.empty:
        print(f"no runs logged in {args.results}")
        return 0
    rows = []
    for experiment, grp in results.groupby("experiment", sort=False):
        last = grp.iloc[-1]
        info = _last_run_info(results, last["config_hash"])
        rows.append({
            "experiment": experiment,
            "model": last["model"],
            "cell": f"{last['label']} ({last['scheme']})",
            "dataset": last["dataset_version"],
            "runs": grp["run_id"].nunique(),
            "last_run": str(last["logged_utc"])[:10],
            "status": last["status"],
            "headline": info["headline"],
            "config": last["config_path"],
        })
    rows.sort(key=lambda r: r["last_run"], reverse=True)
    _print_table(rows, ["experiment", "model", "cell", "dataset", "runs",
                        "last_run", "status", "headline", "config"])
    return 0


def cmd_show(args) -> int:
    target = Path(args.target)
    if not target.exists():
        # maybe an experiment name — find its config file by name
        for entry in _scan_configs(Path(args.experiments_dir)):
            c = entry.get("config")
            if c is not None and c.name == args.target:
                target = entry["path"]
                break
        else:
            print(f"no config file or experiment named {args.target!r}")
            return 1
    config = ExperimentConfig.from_file(target)
    print(f"config:        {target}")
    print(f"name:          {config.name}")
    print(f"config hash:   {config.config_hash}")
    print(f"model:         {config.model_name} "
          f"{json.dumps(config.model_params, sort_keys=True)}")
    print(f"cell:          {config.label} — {config.horizon_years}y, "
          f"scheme {config.scheme}")
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

    results = ResultsStore(Path(args.results)).load()
    sel = (results[results["config_hash"] == config.config_hash]
           if not results.empty else results)
    if sel is None or sel.empty:
        print("\nnever run (nothing in the results ledger for this hash)")
        return 0
    print(f"\nruns ({sel['run_id'].nunique()}):")
    rows = []
    for run_id, grp in sel.groupby("run_id", sort=False):
        last = grp.iloc[-1]
        fold_metrics = pd.DataFrame(
            [json.loads(m) for m in grp["metrics_json"] if m]
        )
        headline = (_headline_metric(
            fold_metrics.mean(numeric_only=True).to_dict())
            if not fold_metrics.empty else "")
        rows.append({
            "run_id": run_id,
            "date": str(last["logged_utc"])[:10],
            "status": last["status"],
            "folds": len(grp),
            "headline": headline + (" (fold mean)" if headline else ""),
            "git_sha": str(last["git_sha"])[:10],
        })
    _print_table(rows, ["run_id", "date", "status", "folds", "headline",
                        "git_sha"])
    report = Path("reports") / f"{config.name}.md"
    if report.exists():
        print(f"\nreport: {report}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Browse experiment configs and their run history."
    )
    parser.add_argument("--experiments-dir", default=str(DEFAULT_EXPERIMENTS))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser(
        "list", help="every config under experiments/, run status joined")
    p_list.add_argument("--model", default="",
                        help="substring filter on the model name")
    p_list.add_argument("--label", default="",
                        help="substring filter on the label")
    p_list.add_argument("--grep", default="",
                        help="substring filter across all fields")

    sub.add_parser("runs", help="everything in the results ledger, "
                                "grouped by experiment")

    p_show = sub.add_parser(
        "show", help="one config in full, with its run history")
    p_show.add_argument("target", help="config path or experiment name")

    args = parser.parse_args(argv)
    if args.command in (None, "list"):
        for attr in ("model", "label", "grep"):
            if not hasattr(args, attr):
                setattr(args, attr, "")
        return cmd_list(args)
    if args.command == "runs":
        return cmd_runs(args)
    return cmd_show(args)


if __name__ == "__main__":
    sys.exit(main())
