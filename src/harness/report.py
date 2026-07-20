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

    path.write_text("\n".join(lines))
    return path
