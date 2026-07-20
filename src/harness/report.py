"""Markdown report for one experiment run.

Every report cites `split_folds.parquet` (the frozen fold definition:
boundaries + role counts), reports effective sample sizes (Σ
sample_weight) cross-checked against `manifest.json["effective_rows"]`,
states the number of configurations tried against the cell, and presents
per-fold (era-sliced) metrics — pooled numbers never stand alone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _fmt(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else f"{v:.4f}"
    return str(v)


def _table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_report(
    *,
    path: str | Path,
    config,
    run_id: str,
    git_sha: str,
    dataset,
    fold_results: list[dict],
    configurations_tried: int,
    era_df: pd.DataFrame | None = None,
    crash_df: pd.DataFrame | None = None,
    baseline_df: pd.DataFrame | None = None,
    calibration_path: Path | None = None,
    artifacts: dict | None = None,
) -> Path:
    """fold_results: [{fold, n_train_rows, effective_train_size,
    n_test_rows, metrics: {...}}, ...]"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sf = dataset.split_folds
    folds_run = [fr["fold"] for fr in fold_results]
    cited = sf[
        (sf["scheme"] == config.scheme)
        & (sf["horizon_years"] == config.horizon_years)
        & (sf["fold"].isin(folds_run))
    ].sort_values("fold")

    manifest_eff = dataset.manifest_effective_rows(config.horizon_years)

    lines: list[str] = []
    lines.append(f"# Experiment report — {config.name}")
    lines.append("")
    lines.append(f"- run id: `{run_id}`")
    lines.append(f"- dataset version: `{dataset.version}` (pinned, immutable)")
    lines.append(f"- config hash: `{config.config_hash}`")
    lines.append(f"- git SHA: `{git_sha}`")
    lines.append(f"- seed: {config.seed}")
    lines.append(f"- model: `{config.model_name}` "
                 f"params `{json.dumps(config.model_params, sort_keys=True)}`")
    lines.append(f"- label: `{config.label}` — horizon {config.horizon_years}y, "
                 f"scheme `{config.scheme}`")
    lines.append(
        f"- **configurations tried against this cell "
        f"(dataset, scheme, horizon, label): {configurations_tried}** "
        "(from the append-only results store; failed runs count)"
    )
    lines.append("")

    lines.append("## Fold definition (cited from `split_folds.parquet`)")
    lines.append("")
    lines.append(
        "Frozen fold manifest for the folds evaluated below — boundaries and "
        "role counts as built upstream; this report is invalid if the folds "
        "are redefined."
    )
    lines.append("")
    cite_cols = [
        c
        for c in [
            "fold", "test_start", "test_end", "embargo_days",
            "n_train", "n_test", "n_purged", "n_embargoed",
        ]
        if c in cited.columns
    ]
    lines.append(_table(cited[cite_cols]))
    lines.append("")

    lines.append("## Effective sample size")
    lines.append("")
    lines.append(
        "Σ `sample_weight_{H}y` over the rows actually fitted — the honest "
        "sample size under overlapping label windows; raw row counts are "
        "shown only for reconciliation."
    )
    lines.append("")
    eff = pd.DataFrame(
        [
            {
                "fold": fr["fold"],
                "train_rows": fr["n_train_rows"],
                "effective_train_size": fr["effective_train_size"],
                "test_rows": fr["n_test_rows"],
            }
            for fr in fold_results
        ]
    )
    lines.append(_table(eff))
    lines.append("")
    if manifest_eff is not None:
        lines.append(
            f"Cross-check: `manifest.json[\"effective_rows\"]` for "
            f"{config.horizon_years}y = {manifest_eff:.1f} (whole dataset; "
            "every per-fold effective size above must be ≤ this)."
        )
        lines.append("")

    lines.append("## Metrics per fold (era-sliced)")
    lines.append("")
    lines.append(
        "One row per walk-forward fold = one test year; pooled numbers are "
        "never presented alone. Brier is reported only for probabilistic "
        "scores; ROC-AUC is logged, never headline."
    )
    lines.append("")
    metric_rows = []
    for fr in fold_results:
        metric_rows.append({"fold": fr["fold"], **fr["metrics"]})
    lines.append(_table(pd.DataFrame(metric_rows)))
    lines.append("")

    if era_df is not None and not era_df.empty:
        lines.append("## Era-sliced metrics (per test year)")
        lines.append("")
        lines.append(
            "Sliced on the calendar year of each test row's "
            "`snapshot_date`. The pooled row is context for the era rows, "
            "never a stand-alone result."
        )
        lines.append("")
        lines.append(_table(era_df))
        lines.append("")

    lines.append("## Crash-era metrics")
    lines.append("")
    if crash_df is not None and not crash_df.empty:
        from eval.era import CORRELATED_PICKS_CAVEAT

        lines.append(
            "Drawdown eras broken out separately — the defensive thesis is "
            "only testable here. " + CORRELATED_PICKS_CAVEAT
        )
        lines.append("")
        lines.append(_table(crash_df))
    else:
        lines.append(
            "No sampled crash era (2000–02, 2008–09, 2020, 2022) falls in "
            "the evaluated test years; the defensive-performance claim is "
            "untested by this run."
        )
    lines.append("")

    if calibration_path is not None:
        lines.append("## Calibration")
        lines.append("")
        lines.append(
            "Reliability curve on pooled test predictions (each fold's "
            "model is refit on its own expanding window). Downstream "
            "ranking trusts these probabilities; single trees are expected "
            "to calibrate poorly (known Phase-1 limitation, PLAN §2)."
        )
        lines.append("")
        lines.append(f"![calibration curve]({Path(calibration_path).name})")
        lines.append("")

    lines.append("## Baseline comparison")
    lines.append("")
    if baseline_df is not None and not baseline_df.empty:
        lines.append(
            "Latest completed baseline runs against this same cell "
            "(dataset, scheme, horizon, label), metrics averaged across "
            "folds. A model that does not clear these is a negative "
            "result, reported as such."
        )
        lines.append("")
        lines.append(_table(baseline_df))
    else:
        lines.append(
            "**No baseline runs recorded for this cell.** Run "
            "`scripts/run_baselines.py` first; a result without its "
            "baselines is not reportable."
        )
    lines.append("")

    if artifacts:
        lines.append("## Interpretability artifacts")
        lines.append("")
        if "rules" in artifacts:
            lines.append(
                f"- extracted rules (one tree per fold): "
                f"[{Path(artifacts['rules']).name}]({Path(artifacts['rules']).name})"
            )
        if "tree_diagram" in artifacts:
            fold_note = (
                f" (fold {artifacts['tree_diagram_fold']}, the widest "
                "training window)"
                if "tree_diagram_fold" in artifacts
                else ""
            )
            name = Path(artifacts["tree_diagram"]).name
            lines.append(f"- tree diagram{fold_note}: [{name}]({name})")
        lines.append("")

    path.write_text("\n".join(lines))
    return path
