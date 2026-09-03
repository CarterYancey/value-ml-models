"""Markdown report for one era-probe run (`reports/diagnostics/`).

Leads with what the probe answers and the headline against the trivial
baselines, then the per-year slice (which eras are identifiable), the
post-burn-in view, the confusion and importance figures, and the
provenance appendix every report carries (`split_folds.parquet`
citation, effective sample sizes, configurations tried). The banner
says DIAGNOSTIC ONLY because that is what it is.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from harness.report import markdown_table

_HEADLINE_ROWS = (
    ("accuracy", "accuracy (Σw)", "baseline_majority_accuracy"),
    ("within_1y_accuracy", "within ±1 year", "baseline_majority_within_1y_accuracy"),
    ("mae_years", "MAE (years)", "baseline_majority_mae_years"),
    ("macro_f1", "macro-F1", None),
    ("log_loss", "log-loss", "baseline_prior_log_loss"),
)


def _headline_table(metrics: dict, label: str) -> pd.DataFrame:
    rows = []
    for key, name, majority_key in _HEADLINE_ROWS:
        row = {
            "metric": name,
            label: metrics.get(key),
            "majority year": metrics.get(majority_key) if majority_key else None,
        }
        if key == "accuracy":
            row["uniform chance"] = metrics.get("baseline_chance_uniform")
            row["train prior (Σp²)"] = metrics.get(
                "baseline_prior_expected_accuracy"
            )
        rows.append(row)
    df = pd.DataFrame(rows)
    return df[
        ["metric", label, "majority year", "uniform chance", "train prior (Σp²)"]
    ]


def _rel(path: Path | None, base: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(Path(path).relative_to(base))
    except ValueError:
        return Path(path).name


def write_era_probe_report(
    *,
    path: str | Path,
    config,
    run_id: str,
    git_sha: str,
    dataset,
    feature_cols: list[str],
    fold_results: list[dict],
    pooled: dict,
    per_year_df: pd.DataFrame,
    min_year_block: dict | None,
    importances: pd.Series,
    configurations_tried: int,
    artifacts: dict | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    artifacts = artifacts or {}
    base = path.parent

    sf = dataset.split_folds
    folds_run = [fr["fold"] for fr in fold_results]
    cited = sf[
        (sf["scheme"] == config.scheme)
        & (sf["horizon_years"] == config.horizon_years)
        & (sf["fold"].isin(folds_run))
    ].sort_values("fold")
    manifest_eff = dataset.manifest_effective_rows(config.horizon_years)
    leaky = config.scheme == "random_kfold"

    L: list[str] = []
    L.append(f"# Era-identifiability probe — {config.name}")
    L.append("")
    L.append(
        "**DIAGNOSTIC ONLY.** This run measures whether the feature set "
        "encodes the calendar era — it predicts `year(snapshot_date)` from "
        "features alone. It is never model selection and never reported "
        "performance (data/manual.md §7, PLAN §7). A probe that beats the "
        "majority-year and train-prior baselines means an entity-holdout "
        "return model *can* score by era timing rather than stock "
        "selection; read such models with that in mind."
    )
    if leaky:
        L.append("")
        L.append(
            "**Scheme `random_kfold` — deliberately leaky:** the same firms "
            "and overlapping windows sit in train and test, so this is the "
            "upper bound on identifiability, not the entity-disjoint number."
        )
    L.append("")
    L.append("## Provenance")
    L.append("")
    L.append(f"- run id: `{run_id}`")
    L.append(f"- dataset version: `{dataset.version}` (pinned, immutable)")
    L.append(f"- config hash: `{config.config_hash}`")
    L.append(f"- git SHA: `{git_sha}`")
    L.append(f"- seed: {config.seed}")
    L.append(
        f"- model: `{config.model_name}` params "
        f"`{json.dumps(config.model_params, sort_keys=True)}`"
    )
    L.append(
        f"- scheme `{config.scheme}`, horizon {config.horizon_years}y "
        f"(selects the tag set and `sample_weight_{config.horizon_years}y`; "
        "rows are that horizon's label-observable rows, weighted natively)"
    )
    L.append(
        f"- features: {config.feature_summary()} → {len(feature_cols)} "
        "columns (manifest-selected; no derived columns)"
    )
    L.append(
        "- target: `snapshot_year` = year(`snapshot_date`) from `key_meta` "
        "— a target, not a feature (invariant 4 concerns features)"
    )
    L.append(
        f"- **configurations tried against this probe cell "
        f"(dataset, scheme, horizon, `snapshot_year`): {configurations_tried}** "
        "(from the append-only results store; failed runs count)"
    )
    L.append("")

    # ---------------------------------------------------------- headline
    L.append("## Headline — probe vs. trivial baselines")
    L.append("")
    L.append(
        "Weighted by Σ `sample_weight_{H}y`. *Majority year* predicts the "
        "training set's heaviest year for every row; *train prior (Σp²)* "
        "is the expected accuracy of guessing from the training year "
        "distribution; *uniform chance* is 1/k over the training years. "
        "Snapshot counts grow over the sample, so majority-year is the "
        "baseline that matters."
    )
    L.append("")
    for fr in fold_results:
        m = fr["metrics"]
        L.append(
            f"### Fold {fr['fold']} — {m['n_test']} test rows "
            f"(Σw = {m['effective_n']:.1f}), {m['k_train']} training years"
        )
        L.append("")
        if m.get("k_train", 0) < 2:
            L.append("Degenerate: a single training year — nothing to identify.")
            L.append("")
        L.append(markdown_table(_headline_table(m, "probe")))
        if m.get("n_test_years_unseen_in_train"):
            L.append("")
            L.append(
                f"{m['n_test_years_unseen_in_train']} test year(s) never "
                "appear in training and are unpredictable by construction."
            )
        L.append("")
    if len(fold_results) > 1:
        L.append(
            f"### Pooled over {len(fold_results)} folds — {pooled['n_test']} "
            f"test rows (Σw = {pooled['effective_n']:.1f})"
        )
        L.append("")
        L.append(markdown_table(_headline_table(pooled, "probe")))
        L.append("")

    # ---------------------------------------------------------- per year
    L.append("## Per-year slice — which eras are identifiable")
    L.append("")
    L.append(
        "One row per test year: *recall* is the share of the year's weight "
        "the probe calls correctly (chance ≈ that year's train-prior "
        "share); *precision* the share of calls for that year that are "
        "right (— when the year is never predicted); *most confused with* "
        "names where the misses go. Expect the burn-in years and the "
        "crash years to stand out."
    )
    L.append("")
    L.append(markdown_table(per_year_df))
    L.append("")

    L.append("## Post-burn-in slice")
    L.append("")
    if config.report_min_year is None:
        L.append("Not requested (`report_min_year` unset).")
    elif min_year_block is None:
        L.append(
            f"No test rows at or after {config.report_min_year} — nothing "
            "to slice."
        )
    else:
        b = min_year_block
        L.append(
            f"Test rows with year ≥ {b['min_year']} ({b['n_test']} rows, "
            f"Σw = {b['effective_n']:.1f}), scored by the same model (trained "
            "on all years). Early years are identifiable from nullity alone "
            "(data/manual.md §8), so this is the level-and-structure view."
        )
        L.append("")
        L.append(
            markdown_table(
                pd.DataFrame(
                    [
                        {"metric": "accuracy (Σw)", "probe": b["accuracy"]},
                        {"metric": "within ±1 year", "probe": b["within_1y_accuracy"]},
                        {"metric": "MAE (years)", "probe": b["mae_years"]},
                        {"metric": "log-loss", "probe": b["log_loss"]},
                    ]
                )
            )
        )
    L.append("")

    # ----------------------------------------------------------- figures
    L.append("## What identifies the era")
    L.append("")
    conf = _rel(artifacts.get("confusion"), base)
    if conf:
        L.append(f"![year confusion]({conf})")
        L.append("")
    kind = artifacts.get("importance_kind", "impurity")
    L.append(
        f"Top feature importances ({kind}-based, normalised, averaged over "
        "folds) — the columns the probe leans on to date a row:"
    )
    L.append("")
    top = importances.sort_values(ascending=False).head(20)
    L.append(
        markdown_table(
            pd.DataFrame(
                {"feature": [str(i) for i in top.index], "importance": top.to_numpy()}
            )
        )
    )
    L.append("")
    imp = _rel(artifacts.get("importance"), base)
    if imp:
        L.append(f"![feature importance]({imp})")
        L.append("")
    rules = _rel(artifacts.get("rules"), base)
    if rules:
        L.append(
            f"Extracted rules (tree arm): [{rules}]({rules}) — each leaf "
            "names the year it predicts and the feature thresholds that "
            "get there."
        )
        L.append("")
    diagram = _rel(artifacts.get("tree_diagram"), base)
    if diagram:
        L.append(
            f"Tree diagram (fold {artifacts.get('tree_diagram_fold')}): "
            f"![tree]({diagram})"
        )
        L.append("")

    # ---------------------------------------------------------- appendix
    L.append("## Appendix — provenance & accounting")
    L.append("")
    L.append("### Fold definition (cited from `split_folds.parquet`)")
    L.append("")
    L.append(
        "Frozen fold manifest for the folds evaluated above. Diagnostic "
        "schemes carry NULL period boundaries: folds are permaticker "
        "(`entity_holdout`) or row (`random_kfold`) hash buckets over the "
        "pre-holdout region, not periods; nothing is purged or embargoed. "
        "This report is invalid if the folds are redefined."
    )
    L.append("")
    cite_cols = [
        c
        for c in [
            "fold", "test_start", "test_end", "embargo_days",
            "n_train", "n_test", "n_purged", "n_embargoed",
        ]
        if c in cited.columns
    ]
    L.append(markdown_table(cited[cite_cols]))
    L.append("")
    L.append("### Effective sample size")
    L.append("")
    L.append(
        f"Σ `sample_weight_{config.horizon_years}y` over the rows actually "
        "fitted and scored — the honest sample size under overlapping "
        "windows; raw row counts only for reconciliation."
    )
    L.append("")
    L.append(
        markdown_table(
            pd.DataFrame(
                [
                    {
                        "fold": fr["fold"],
                        "train_rows": fr["n_train_rows"],
                        "effective_train_size": fr["effective_train_size"],
                        "test_rows": fr["n_test_rows"],
                        "effective_test_size": fr["effective_test_size"],
                        "train_years": (
                            f"{fr['train_years'][0]}–{fr['train_years'][-1]}"
                            if fr["train_years"] else "—"
                        ),
                    }
                    for fr in fold_results
                ]
            )
        )
    )
    L.append("")
    if manifest_eff is not None:
        L.append(
            f"Cross-check: `manifest.json[\"effective_rows\"]` for "
            f"{config.horizon_years}y = {manifest_eff:.1f} (whole dataset; "
            "every per-fold effective size above must be ≤ this)."
        )
        L.append("")
    L.append("### Config")
    L.append("")
    L.append("```json")
    L.append(json.dumps(config.to_raw_dict(), indent=2, sort_keys=True))
    L.append("```")
    L.append("")
    path.write_text("\n".join(L))
    return path
