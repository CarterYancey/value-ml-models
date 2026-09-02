"""Seed-stability aggregation for multi-seed sweeps.

A sweep over several seeds fits every candidate (cell × feature set ×
parameter set × grid point × random draw) once per seed. The per-seed
runs are still ordinary experiments — logged, reported, counted in the
trial ledger — but the question a multi-seed sweep asks is different:
*is the candidate's number stable, or is it the luck of one fit?* So the
sweep aggregates each candidate's runs into one seed-stability report
and ranks candidates by their mean across seeds, with the spread beside
it.

Statistics reported per metric, over the seeds that completed:
`n`, `mean`, sample `std` (n − 1), `min`, `max`, and a 95% t-interval
for the mean (`ci95_low` / `ci95_high`, n − 1 degrees of freedom).
With two or three seeds the interval is wide by construction — that is
the honest width, not a defect. The `min` matters as much as the mean:
a candidate is only as good as its worst seed.

None of this changes what the numbers are: model selection on
walk-forward folds, selection-biased, never a final result.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from eval.era import crash_label
from eval.metrics import threshold_tag
from harness.report import _table
from harness.results import git_sha

STAT_COLUMNS = ("n", "mean", "std", "min", "max", "ci95_low", "ci95_high")


def t_critical(dof: int, confidence: float = 0.95) -> float:
    """Two-sided Student-t critical value (scipy ships with scikit-learn;
    no new dependency)."""
    from scipy import stats

    return float(stats.t.ppf(0.5 + confidence / 2, dof))


def seed_stats(values) -> dict:
    """Spread of one metric across seeds. Non-numeric / NaN values are
    dropped (they are metrics that don't apply, e.g. Brier for a
    non-probabilistic model); `n` counts what remained."""
    arr = []
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if not math.isnan(f):
            arr.append(f)
    out = {c: math.nan for c in STAT_COLUMNS}
    out["n"] = len(arr)
    if not arr:
        return out
    a = np.asarray(arr, dtype=float)
    out.update(mean=float(a.mean()), min=float(a.min()), max=float(a.max()))
    if len(a) >= 2:
        std = float(a.std(ddof=1))
        half = t_critical(len(a) - 1) * std / math.sqrt(len(a))
        out.update(
            std=std, ci95_low=out["mean"] - half, ci95_high=out["mean"] + half
        )
    return out


def headline_metrics(sweep, available) -> list[str]:
    """The metrics a sweep's tables lead with, in reading order: the
    rank metric, the precision-floor family, precision@K, PR-AUC, Brier
    against its no-skill reference, the base rate."""
    order = [sweep.rank_metric]
    for p in sweep.precision_targets:
        for prefix in ("recall_at_prec_", "n_at_prec_", "thr_for_prec_"):
            order.append(f"{prefix}{threshold_tag(p)}")
    for k in sweep.top_k:
        order += [f"precision_at_{k}", f"conf_at_{k}", f"recall_at_{k}"]
    order += ["pr_auc", "brier", "base_rate_brier", "base_rate"]
    avail = set(available)
    return list(dict.fromkeys(m for m in order if m in avail))


def aggregate_candidates(outcomes: list[dict]) -> list[dict]:
    """Group a sweep's per-run outcomes by candidate (everything but the
    seed) and compute across-seed statistics for every pooled metric and
    every per-fold metric. Order follows first appearance."""
    groups: dict[str, list[dict]] = {}
    for o in outcomes:
        groups.setdefault(o["candidate"], []).append(o)
    cands = []
    for candidate, runs in groups.items():
        first = runs[0]
        done = [r for r in runs if r["status"] == "completed"]
        metric_names = list(
            dict.fromkeys(m for r in done for m in r["pooled_metrics"])
        )
        pooled = {
            m: seed_stats(r["pooled_metrics"].get(m) for r in done)
            for m in metric_names
        }
        folds = sorted({f for r in done for f in r.get("fold_metrics", {})})
        era = {}
        for fold in folds:
            per_fold = [r["fold_metrics"][fold] for r in done if fold in r.get("fold_metrics", {})]
            names = list(dict.fromkeys(m for fm in per_fold for m in fm))
            era[fold] = {
                m: seed_stats(fm.get(m) for fm in per_fold) for m in names
            }
        cands.append(
            {
                "candidate": candidate,
                "label": first["label"],
                "eval_label": first.get("eval_label", ""),
                "horizon_years": first["horizon_years"],
                "feature_set": first["feature_set"],
                "param_set": first["param_set"],
                "set_params": first["set_params"],
                "grid_params": first["grid_params"],
                "sampled_params": first.get("sampled_params", {}),
                "model_params": first.get("model_params", {}),
                "seeds": [r["seed"] for r in runs],
                "completed_seeds": [r["seed"] for r in done],
                "failed": [r for r in runs if r["status"] != "completed"],
                "pooled": pooled,
                "era": era,
                "runs": runs,
            }
        )
    return cands


def candidate_frame(cands: list[dict], metrics: list[str]) -> pd.DataFrame:
    """One row per candidate: identity columns plus `{metric}_{stat}` for
    every requested metric (the seed-level summary CSV)."""
    rows = []
    for c in cands:
        row = {
            "candidate": c["candidate"],
            "seeds_completed": f"{len(c['completed_seeds'])}/{len(c['seeds'])}",
            "label": c["label"],
            "eval_label": c["eval_label"],
            "horizon_years": c["horizon_years"],
            "feature_set": c["feature_set"],
            "param_set": c["param_set"],
            "set_params": json.dumps(c["set_params"], sort_keys=True),
            "grid_params": json.dumps(c["grid_params"], sort_keys=True),
            "sampled_params": json.dumps(c["sampled_params"], sort_keys=True),
        }
        for m in metrics:
            st = c["pooled"].get(m) or seed_stats(())
            for stat in STAT_COLUMNS:
                row[f"{m}_{stat}"] = st[stat]
        rows.append(row)
    return pd.DataFrame(rows)


def _stats_table(stats_by_metric: dict[str, dict], metrics: list[str]) -> str:
    rows = [{"metric": m, **stats_by_metric[m]} for m in metrics if m in stats_by_metric]
    return _table(pd.DataFrame(rows, columns=["metric", *STAT_COLUMNS]))


def write_candidate_report(
    sweep, cand: dict, sweep_reports: Path, *, sweep_config_path: str = ""
) -> Path:
    """One seed-stability report per candidate, next to the sweep summary."""
    sweep_reports.mkdir(parents=True, exist_ok=True)
    metrics = headline_metrics(sweep, cand["pooled"])
    rest = [m for m in cand["pooled"] if m not in metrics]
    rank = cand["pooled"].get(sweep.rank_metric) or seed_stats(())
    n_done, n_all = len(cand["completed_seeds"]), len(cand["seeds"])

    def fmt(v):
        return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.4f}"

    lines = [
        f"# Seed stability — {cand['candidate']}",
        "",
        f"- sweep: `{sweep.name}` (config `{sweep_config_path or '<inline>'}`)",
        f"- dataset version: `{sweep.dataset_version}` (pinned, immutable)",
        f"- scheme: `{sweep.scheme}`, folds: `{sweep.folds}`, git `{git_sha()}`",
        f"- cell: `{cand['label']}` ({cand['horizon_years']}y)"
        + (f", measured on `{cand['eval_label']}`" if cand["eval_label"] else ""),
        f"- model family: `{sweep.model_name}`, params "
        f"`{json.dumps(cand['model_params'], sort_keys=True)}`",
    ]
    if sweep.n_feature_variants > 1:
        lines.append(f"- feature set: `fs{cand['feature_set']}`")
    if sweep.param_sets:
        lines.append(
            f"- parameter set: `set{cand['param_set']}` = "
            f"`{json.dumps(cand['set_params'], sort_keys=True)}`"
        )
    if cand["grid_params"]:
        lines.append(f"- grid point: `{json.dumps(cand['grid_params'], sort_keys=True)}`")
    if cand["sampled_params"]:
        lines.append(
            f"- random draw: `{json.dumps(cand['sampled_params'], sort_keys=True)}`"
        )
    lines += [
        f"- seeds: {cand['seeds']} — {n_done}/{n_all} completed",
        f"- pooled `{sweep.rank_metric}` across seeds: mean {fmt(rank['mean'])}, "
        f"std {fmt(rank['std'])}, min {fmt(rank['min'])}, max {fmt(rank['max'])}, "
        f"95% CI [{fmt(rank['ci95_low'])}, {fmt(rank['ci95_high'])}]",
        "",
        "**Reading this report.** Each seed is a full walk-forward run of "
        "the same configuration; only the model's own randomness (row and "
        "column subsampling, tie-breaking) differs between them. The "
        "spread here is therefore the part of the number that is chance "
        "in the fit — a wide interval, or a `min` far below the `mean`, "
        "means the candidate's rank in the sweep is not trustworthy. The "
        "interval is a Student-t interval over the completed seeds "
        "(n − 1 degrees of freedom): with two or three seeds it is wide "
        "by construction, which is the honest width. Everything here is "
        "still **model selection on walk-forward folds** — selection-"
        "biased, never a final result.",
        "",
        "## Pooled metrics across seeds",
        "",
        _stats_table(cand["pooled"], metrics),
        "",
    ]
    if rest:
        lines += [
            "<details><summary>Every other pooled metric</summary>",
            "",
            _stats_table(cand["pooled"], rest),
            "",
            "</details>",
            "",
        ]
    per_seed = pd.DataFrame(
        [
            {
                "seed": r["seed"],
                "status": r["status"],
                **{m: r["pooled_metrics"].get(m, math.nan) for m in metrics},
                "report": (
                    Path(r["report_path"]).name if r.get("report_path") else "—"
                ),
            }
            for r in cand["runs"]
        ]
    )
    lines += ["## Per-seed pooled values", "", _table(per_seed), ""]

    era_metrics = [
        m for m in dict.fromkeys(
            [sweep.rank_metric, f"precision_at_{sweep.top_k[0]}"]
        )
        if any(m in fm for fm in cand["era"].values())
    ]
    if cand["era"] and era_metrics:
        rows = []
        for fold, fm in cand["era"].items():
            row = {"era": fold, "crash": crash_label(int(fold)) or ""}
            n_vals = [fm[m]["n"] for m in era_metrics if m in fm]
            row["n"] = max(n_vals) if n_vals else 0
            for m in era_metrics:
                st = fm.get(m) or seed_stats(())
                for stat in ("mean", "std", "min", "max"):
                    row[f"{m} {stat}"] = st[stat]
            rows.append(row)
        lines += [
            "## Era slices across seeds (per test year)",
            "",
            "Per-fold metrics under walk-forward are per test year. A "
            "candidate whose mean holds up but whose per-year `min` "
            "collapses in some eras is seed-fragile exactly where it "
            "matters.",
            "",
            _table(pd.DataFrame(rows)),
            "",
        ]
    if cand["failed"]:
        lines += ["## Failed seeds", ""]
        lines += [f"- seed {r['seed']} (`{r['run']}`): {r['error']}" for r in cand["failed"]]
        lines += [""]
    lines += [
        "Per-seed reports (era tables, crash eras, calibration, baselines): "
        "`seeds/<run name>.md` in this directory.",
        "",
    ]
    path = sweep_reports / f"{cand['candidate']}.md"
    path.write_text("\n".join(lines))
    return path
