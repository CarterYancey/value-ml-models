"""Markdown report for one experiment run.

Structured for how the results actually get read: the era-sliced metrics
table and the high-confidence-picks profile lead, calibration follows,
and the provenance/accounting material every report must still carry
(`split_folds.parquet` citation, effective sample sizes, crash-era
breakout with intervals) lives in an appendix — cited, not headlined.
Pooled numbers never stand alone, and the pooled ranking metrics pick
per year (per-fold model scores aren't comparable — see eval.era).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from eval.era import crash_label

#: Metric families shown in the era table, in reading order. Anything
#: logged but not listed here (roc_auc, recall_at_k, thr_for_prec_*)
#: stays in the results store — logged, never headlined.
_ERA_LEAD = ("n_test", "base_rate")
_ERA_PREFIXES = (
    "precision_at_", "conf_at_", "n_at_prec_", "recall_at_prec_",
    "precision_at_thr_", "recall_at_thr_", "n_at_thr_",
)
_ERA_TAIL = ("brier", "base_rate_brier", "pr_auc")


def _fmt(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else f"{v:.4f}"
    return str(v)


def _table(df: pd.DataFrame) -> str:
    """GitHub-flavored table with cells padded to the column width, so the
    raw markdown reads as an aligned table too (long metric names over
    short values used to make the source unreadable)."""
    cols = list(df.columns)
    cells = [[_fmt(row[c]) for c in cols] for _, row in df.iterrows()]
    widths = [
        max(len(str(c)), *(len(r[i]) for r in cells)) if cells else len(str(c))
        for i, c in enumerate(cols)
    ]
    def line(values):
        return "| " + " | ".join(
            v.ljust(w) for v, w in zip(values, widths)
        ) + " |"
    lines = [
        line([str(c) for c in cols]),
        line(["-" * w for w in widths]),
    ]
    lines += [line(r) for r in cells]
    return "\n".join(lines)


def _era_view(era_df: pd.DataFrame) -> pd.DataFrame:
    """The era table as reported: crash years tagged inline, columns in
    reading order, the logged-only columns left to the results store."""
    df = era_df.copy()
    def tag(era):
        if str(era) == "pooled":
            return "pooled*"
        label = crash_label(int(era)) if str(era).isdigit() else None
        return f"{era} ({label})" if label else str(era)
    df["era"] = df["era"].map(tag)
    ordered = ["era"] + [c for c in _ERA_LEAD if c in df.columns]
    for prefix in _ERA_PREFIXES:
        ordered += [c for c in df.columns if c.startswith(prefix)
                    and c not in ordered]
    ordered += [c for c in _ERA_TAIL if c in df.columns]
    return df[ordered]


def _baseline_view(baseline_df: pd.DataFrame) -> pd.DataFrame:
    """Baseline comparison trimmed to the columns that get read."""
    drop = [c for c in baseline_df.columns
            if c == "roc_auc" or c.startswith("recall_at_")
            or c.startswith("thr_for_prec_") or c.startswith("conf_at_")]
    return baseline_df.drop(columns=drop)


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
    confidence_df: pd.DataFrame | None = None,
    baseline_df: pd.DataFrame | None = None,
    calibration_path: Path | None = None,
    pr_curve_path: Path | None = None,
    roc_curve_path: Path | None = None,
    score_figures_rendered: bool = True,
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
    if getattr(config, "eval_label", ""):
        lines.append(
            f"- **regression reframe**: trained on the continuous target "
            f"`{config.label}`; every metric below is computed against the "
            f"binary cell `{config.eval_label}`. Scores are predicted "
            "returns (a ranking), not probabilities — any score thresholds "
            "are on that scale."
        )
    lines.append(
        f"- **configurations tried against this cell "
        f"(dataset, scheme, horizon, label): {configurations_tried}** "
        "(from the append-only results store; failed runs count)"
    )
    if artifacts and "model_bundle" in artifacts:
        lines.append(
            f"- saved model bundle: `{artifacts['model_bundle']}` "
            "(re-evaluate with `vml-eval`, no refitting)"
        )
    if artifacts and "source_bundle" in artifacts:
        lines.append(
            f"- **re-evaluation of saved bundle** "
            f"`{artifacts['source_bundle']}`: models loaded, not refit — "
            "only the metric parameters differ from the training run"
        )
    lines.append("")

    if era_df is not None and not era_df.empty:
        lines.append("## Era-sliced metrics (one row per test year)")
        lines.append("")
        lines.append(
            "Sliced on the calendar year of each test row's `snapshot_date` "
            "(one walk-forward fold per year); crash eras are tagged inline. "
            "`conf_at_K` is the mean score of the top-K picks; "
            "`base_rate_brier` is the no-skill Brier the model must beat. "
            "\\*The pooled row picks per year — per-fold model scores are "
            "not comparable, so a global top-K would just take the "
            "hottest-scoring fold's picks; it is context for the era rows, "
            "never a stand-alone result. ROC-AUC and recall@K are logged "
            "in the results store, not shown here."
        )
        lines.append("")
        lines.append(_table(_era_view(era_df)))
        lines.append("")
    else:
        lines.append("## Metrics per fold")
        lines.append("")
        lines.append(
            "One row per fold; pooled numbers are never presented alone."
        )
        lines.append("")
        metric_rows = [{"fold": fr["fold"], **fr["metrics"]}
                       for fr in fold_results]
        lines.append(_table(pd.DataFrame(metric_rows)))
        lines.append("")

    if confidence_df is not None and not confidence_df.empty:
        lines.append("## High-confidence picks (pooled)")
        lines.append("")
        lines.append(
            "How many high-confidence calls the model made, how confident "
            "it was, and how precise they were — no pre-chosen score "
            "threshold needed. `top N/yr` rows pick per test year; "
            "`score >= p` rows (probabilistic models) count every name at "
            "or above that probability, pooled."
        )
        lines.append("")
        lines.append(_table(confidence_df))
        lines.append("")

    source_bundle = artifacts.get("source_bundle") if artifacts else None
    if not score_figures_rendered:
        lines.append("## Calibration")
        lines.append("")
        lines.append(
            "Not redrawn for this evaluation: the score-only figures "
            "depend on the model's test scores alone, which this run did "
            "not change — it re-scored the saved model under different "
            "metric parameters. See the training run's report"
            + (f" (bundle `{source_bundle}`)" if source_bundle else "")
            + " for the figures."
        )
        lines.append("")
    elif calibration_path is not None:
        lines.append("## Calibration")
        lines.append("")
        lines.append(
            "Reliability curve on pooled test predictions (each fold's "
            "model is refit on its own expanding window). Downstream "
            "ranking trusts these probabilities; single trees are "
            "expected to calibrate poorly (known Phase-1 limitation, "
            "PLAN §2)."
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
        lines.append(_table(_baseline_view(baseline_df)))
    else:
        lines.append(
            "**No baseline runs recorded for this cell.** Run "
            "`scripts/run_baselines.py` first; a result without its "
            "baselines is not reportable."
        )
    lines.append("")

    if artifacts and (
        "rules" in artifacts
        or "tree_diagram" in artifacts
        or "importances" in artifacts
    ):
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
        if "importances" in artifacts:
            imp_path = Path(artifacts["importances"])
            lines.append(
                f"- per-fold feature importances: [{imp_path.name}]"
                f"({imp_path.name}) — impurity/gain-based, so a triage "
                "list for feature subsets (which count as configurations "
                "tried), not an explanation; the top of the ranking:"
            )
            lines.append("")
            top = pd.read_csv(imp_path).head(10)
            cols = ["feature", "mean_importance"]
            lines.append(_table(top[[c for c in cols if c in top.columns]]))
        lines.append("")

    # ------------------------------------------------- appendix
    lines.append("## Appendix — provenance & accounting")
    lines.append("")
    lines.append(
        "The material every report must carry (honest-evaluation "
        "checklist), kept out of the reading path."
    )
    lines.append("")

    lines.append("### Fold definition (cited from `split_folds.parquet`)")
    lines.append("")
    lines.append(
        "Frozen fold manifest for the folds evaluated above — boundaries "
        "and role counts as built upstream; this report is invalid if the "
        "folds are redefined."
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

    lines.append("### Effective sample size")
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

    lines.append("### Crash-era metrics (with intervals)")
    lines.append("")
    if crash_df is not None and not crash_df.empty:
        from eval.era import CORRELATED_PICKS_CAVEAT

        lines.append(
            "Drawdown eras broken out with uncertainty — the same years "
            "are tagged in the era table above. " + CORRELATED_PICKS_CAVEAT
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

    if score_figures_rendered and (
        pr_curve_path is not None or roc_curve_path is not None
    ):
        lines.append("### Discrimination curves (opt-in)")
        lines.append("")
        lines.append(
            "Pooled over folds (mind the cross-fold score-comparability "
            "caveat). Read precision–recall against the base rate; ROC is "
            "logged against the chance diagonal but never headlined."
        )
        lines.append("")
        if pr_curve_path is not None:
            lines.append(f"![PR curve]({Path(pr_curve_path).name})")
            lines.append("")
        if roc_curve_path is not None:
            lines.append(f"![ROC curve]({Path(roc_curve_path).name})")
            lines.append("")

    path.write_text("\n".join(lines))
    return path
