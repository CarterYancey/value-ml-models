"""Historical analogues: stocks that looked like today's picks, and what
happened to them.

Given deployment bundles and an inference dataset, `vml-analogues` takes
the picks (the same selection `vml-predict` makes, or named tickers) and
for each one lists the labeled historical rows most similar to it *as
the models see it*, with their realized outcomes.

Similarity is defined per model and averaged across the models of a
blend:

- **a tree model** (forest, single tree, LightGBM, XGBoost): the share
  of trees in which the historical row lands in the same leaf as the
  pick. This uses the model's own split thresholds and NULL routing: no
  distance metric to choose, no imputation, no scaling. For a single
  tree it is 1 (same rule) or 0;
- **a rank factor** (a single column wrapped as a model): one minus the
  distance between the two values of the column, as a share of the
  column's range (rank columns run 0..1). NULL matches NULL; NULL
  against a value is 0.

The pool is the dataset version the bundles were trained on: median-kind
rows whose outcome over the longest bundle horizon is observable, every
era, delisted rows included (a delisted analogue is exactly the history
this is for). One row per stock is listed (its most similar snapshot),
and the pick's own history is left out unless asked for.

**Explanation, not evaluation.** A deployment model was fitted on these
very rows: the rows that share a pick's leaves are the rows that made
those leaves, so their outcome rate is in-sample by construction and is
not an accuracy or a probability for the pick. Nothing produced here is
ever a model input (CLAUDE.md invariant 4). Inference ranks are pooled
over one day's cross-section where training ranks are within a quarter;
the comparison is as close as the two can be, not exact.
"""

from __future__ import annotations

import json
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from harness.dataset import Dataset, feature_matrix
from harness.deploy import (
    DEFAULT_PREDICTIONS,
    load_inference_frame,
    predict_with_bundle,
    predict_with_bundles,
    _bundle_column_names,
)
from harness.errors import ConfigError, DatasetValidationError
from harness.filters import FilterSpec
from harness.model_store import DeploymentBundle
from harness.results import git_sha
from harness.runner import DEFAULT_DATA_ROOT, DEFAULT_RESULTS

#: analogues listed per pick by default
DEFAULT_ANALOGUES = 15
#: pool rows scored per `apply` call: rows x trees leaf ids are held
#: only for one chunk at a time, never for the whole pool
CHUNK_ROWS = 50_000
#: how many of a pick's most-used split features are shown
PATH_FEATURES = 6
#: outcome columns shown per horizon, when the manifest has them
_OUTCOMES = ("cagr", "excess_cagr", "max_drawdown_from_entry")


# ------------------------------------------------------------ similarity


def leaf_ids(model, X: pd.DataFrame) -> np.ndarray | None:
    """(rows, trees) leaf ids of a fitted tree model, or None when the
    model has no leaves (a rank factor, a constant model)."""
    estimator = getattr(model, "estimator_", None)
    names = getattr(model, "feature_names_", None)
    if estimator is None or names is None:
        return None
    if getattr(model, "constant_score_", None) is not None:
        return None
    if getattr(model, "constant_class_", None) is not None:
        return None
    frame = X[names]
    if hasattr(estimator, "booster_"):  # LightGBM
        leaves = estimator.booster_.predict(frame, pred_leaf=True)
    elif hasattr(estimator, "apply"):  # sklearn tree/forest, XGBoost
        leaves = estimator.apply(frame)
    else:
        return None
    leaves = np.asarray(leaves)
    return leaves.reshape(len(frame), -1)


def leaf_similarity(
    model, queries: pd.DataFrame, pool: pd.DataFrame,
    chunk_rows: int = CHUNK_ROWS,
) -> np.ndarray | None:
    """(queries, pool rows) share of trees in which a pool row shares
    the query's leaf; None for a model without leaves. The pool is
    streamed in chunks."""
    q = leaf_ids(model, queries)
    if q is None:
        return None
    out = np.empty((len(queries), len(pool)), dtype=np.float32)
    for start in range(0, len(pool), chunk_rows):
        chunk = leaf_ids(model, pool.iloc[start:start + chunk_rows])
        for i in range(len(queries)):
            out[i, start:start + len(chunk)] = (chunk == q[i]).mean(axis=1)
    return out


def rank_similarity(
    column_q: np.ndarray, column_pool: np.ndarray, scale: float
) -> np.ndarray:
    """(queries, pool rows) closeness on one column: 1 - |difference| /
    scale, floored at 0. NULL matches NULL (1); NULL against a value
    is 0."""
    q = np.asarray(column_q, dtype=float)[:, None]
    p = np.asarray(column_pool, dtype=float)[None, :]
    with np.errstate(invalid="ignore"):
        sim = 1.0 - np.abs(q - p) / scale
    sim = np.clip(sim, 0.0, 1.0)
    both_null = np.isnan(q) & np.isnan(p)
    one_null = np.isnan(q) ^ np.isnan(p)
    sim = np.where(both_null, 1.0, np.where(one_null, 0.0, sim))
    return sim.astype(np.float32)


def path_features(model, queries: pd.DataFrame) -> list[list[tuple[str, float]]]:
    """For each query row, the features its decision paths split on,
    with the share of trees that use each, most used first (sklearn
    trees and forests). Empty lists for other models."""
    estimator = getattr(model, "estimator_", None)
    names = getattr(model, "feature_names_", None)
    empty = [[] for _ in range(len(queries))]
    if estimator is None or names is None or not hasattr(estimator, "decision_path"):
        return empty
    frame = queries[names]
    trees = getattr(estimator, "estimators_", None)
    try:
        if trees is None:  # a single tree
            indicator = estimator.decision_path(frame)
            node_features = np.asarray(estimator.tree_.feature)
            node_tree = np.zeros(len(node_features), dtype=int)
            n_trees = 1
        else:
            indicator, _ = estimator.decision_path(frame)
            node_features = np.concatenate(
                [np.asarray(t.tree_.feature) for t in trees]
            )
            node_tree = np.concatenate(
                [np.full(t.tree_.node_count, n) for n, t in enumerate(trees)]
            )
            n_trees = len(trees)
    except Exception:
        return empty
    indicator = indicator.tocsr()
    out = []
    for i in range(len(frame)):
        nodes = indicator.indices[indicator.indptr[i]:indicator.indptr[i + 1]]
        # a feature counts once per tree, however often the path splits on it
        used = {
            (int(node_tree[n]), int(node_features[n]))
            for n in nodes
            if node_features[n] >= 0
        }
        counts = Counter(f for _, f in used)
        out.append(
            [(names[f], n / n_trees) for f, n in counts.most_common()]
        )
    return out


# ----------------------------------------------------------------- pool


def _outcome_columns(dataset: Dataset, horizons: list[int]) -> list[str]:
    labels = set(dataset.columns("labels"))
    cols = []
    for h in horizons:
        for key in _OUTCOMES:
            col = f"fwd_{h}y_{key}"
            if col in labels:
                cols.append(col)
        if f"delisted_in_window_{h}y" in labels:
            cols.append(f"delisted_in_window_{h}y")
    return cols


def build_pool(
    dataset: Dataset, bundles: list[DeploymentBundle]
) -> tuple[pd.DataFrame, list[int], list[str]]:
    """(pool frame, horizons shown, outcome columns): the median-kind
    rows whose outcome over the longest bundle horizon is observable,
    with every bundle's feature columns and label."""
    horizon = max(b.train_config.horizon_years for b in bundles)
    horizons = sorted({1, horizon} & set(dataset.horizons_years)) or [horizon]
    outcomes = _outcome_columns(dataset, horizons)
    anchor = f"fwd_{horizon}y_cagr"
    if anchor not in outcomes:
        raise DatasetValidationError(
            f"dataset {dataset.version} has no {anchor!r}: the analogues' "
            "outcomes cannot be read"
        )
    display = [
        c for c in ("ticker", "sector")
        if c in dataset.columns("key_meta") + dataset.columns("features")
    ]
    features = list(
        dict.fromkeys(c for b in bundles for c in b.feature_columns)
    )
    labels = list(dict.fromkeys(b.train_config.label for b in bundles))
    frame = dataset.frame(features + outcomes + display + labels)
    keep = (frame["snapshot_kind"] == "median") & frame[anchor].notna()
    pool = frame[keep].reset_index(drop=True)
    return pool, horizons, outcomes


# ------------------------------------------------------------- analogues


def find_analogues(
    bundles: list[DeploymentBundle],
    names: list[str],
    queries: pd.DataFrame,
    dataset: Dataset,
    *,
    top: int = DEFAULT_ANALOGUES,
    include_self: bool = False,
    chunk_rows: int = CHUNK_ROWS,
) -> dict:
    """The `top` most similar pool rows for every query row (one per
    stock), with per-model and combined similarity and realized
    outcomes. Returns {"analogues": long frame, "summary": one row per
    query, "pool_summary": the same statistics over the whole pool,
    "paths": per query the split features of its decision paths,
    "horizons", "label_columns"}."""
    if top < 1:
        raise ConfigError(f"--top must be 1 or more, got {top}")
    pool, horizons, outcomes = build_pool(dataset, bundles)
    if pool.empty:
        raise DatasetValidationError("the analogue pool is empty")
    ranks = set(dataset.columns("ranks")) | set(dataset.columns("sector_ranks"))

    sims: dict[str, np.ndarray] = {}
    paths: list[list[tuple[str, float]]] = [[] for _ in range(len(queries))]
    for bundle, name in zip(bundles, names):
        cols = list(bundle.feature_columns)
        missing = sorted(set(cols) - set(queries.columns))
        if missing:
            raise DatasetValidationError(
                f"inference data lacks feature columns {name} was trained "
                f"on: {missing}"
            )
        Xq = feature_matrix(queries, cols)
        rank_column = getattr(bundle.model, "rank_column", None)
        if rank_column is not None:
            values = pool[rank_column].to_numpy(dtype=float)
            if rank_column in ranks:
                scale = 1.0
            else:  # a raw column: its 1st-99th percentile range
                lo, hi = np.nanpercentile(values, [1, 99])
                scale = float(hi - lo) or 1.0
            sims[name] = rank_similarity(
                queries[rank_column].to_numpy(dtype=float), values, scale
            )
            continue
        Xp = feature_matrix(pool, cols)
        sim = leaf_similarity(bundle.model, Xq, Xp, chunk_rows)
        if sim is None:
            raise ConfigError(
                f"no similarity is defined for bundle {name} "
                f"({bundle.train_config.model_name}): it has neither "
                "leaves nor a rank column"
            )
        sims[name] = sim
        model_paths = path_features(bundle.model, Xq)
        for i, found in enumerate(model_paths):
            if found and not paths[i]:
                paths[i] = found

    combined = np.mean(np.stack(list(sims.values())), axis=0)
    horizon = max(horizons)
    label_columns = {
        name: b.train_config.label
        for b, name in zip(bundles, names)
        if getattr(b.model, "rank_column", None) is None
    }
    pool_stats = _outcome_summary(pool, horizon, label_columns)
    pool_stats["rows"] = int(len(pool))
    pool_stats["stocks"] = int(pool["permaticker"].nunique())

    stock = pool["permaticker"].to_numpy()
    dates = pd.to_datetime(pool["snapshot_date"]).to_numpy()
    rows, summaries = [], []
    for i in range(len(queries)):
        query = queries.iloc[i]
        score = combined[i].copy()
        if not include_self:
            score[stock == query["permaticker"]] = -1.0
        # best first; among equals the later snapshot, then the stock id
        order = np.lexsort((stock, -dates.astype("int64"), -score))
        seen: set = set()
        chosen = []
        for idx in order:
            if score[idx] < 0:
                break
            if stock[idx] in seen:
                continue
            seen.add(stock[idx])
            chosen.append(idx)
            if len(chosen) >= top:
                break
        picked = pool.iloc[chosen]
        shown = [f for f, _ in paths[i][:PATH_FEATURES]]
        for rank, idx in enumerate(chosen, start=1):
            row = {
                "pick": query.get("ticker", query["permaticker"]),
                "pick_permaticker": query["permaticker"],
                "analogue": rank,
                "ticker": pool["ticker"].iat[idx] if "ticker" in pool else None,
                "permaticker": stock[idx],
                "snapshot_date": pd.Timestamp(dates[idx]).date(),
                "similarity": float(combined[i, idx]),
            }
            for name, sim in sims.items():
                row[f"sim_{name}"] = float(sim[i, idx])
            if "sector" in pool.columns:
                row["sector"] = pool["sector"].iat[idx]
            for col in outcomes:
                row[col] = pool[col].iat[idx]
            for name, label in label_columns.items():
                value = pool[label].iat[idx]
                row[f"label_{name}"] = None if pd.isna(value) else bool(value)
            for f in shown:
                if f in pool.columns:
                    row[f] = pool[f].iat[idx]
            rows.append(row)
        summary = {
            "pick": query.get("ticker", query["permaticker"]),
            "pick_permaticker": query["permaticker"],
            "analogues": len(chosen),
            "mean_similarity": float(combined[i, chosen].mean()) if chosen else float("nan"),
            **_outcome_summary(picked, horizon, label_columns),
            "eras": _era_mix(picked),
        }
        summaries.append(summary)
    return {
        "analogues": pd.DataFrame(rows),
        "summary": pd.DataFrame(summaries),
        "pool_summary": pool_stats,
        "paths": paths,
        "horizons": horizons,
        "outcomes": outcomes,
        "label_columns": label_columns,
        "similarity_columns": [f"sim_{n}" for n in sims],
    }


def _outcome_summary(frame: pd.DataFrame, horizon: int, label_columns: dict) -> dict:
    """What a set of rows went on to do over `horizon` years: the share
    that lost money, mean and median CAGR, mean excess CAGR, the share
    that fell 30% from entry, the share delisted in the window, and
    each tree model's label rate."""
    out: dict = {}
    cagr = frame.get(f"fwd_{horizon}y_cagr")
    if cagr is not None and len(frame):
        vals = cagr.to_numpy(dtype=float)
        out["lost_money"] = float(np.nanmean(vals < 0))
        out["mean_cagr"] = float(np.nanmean(vals))
        out["median_cagr"] = float(np.nanmedian(vals))
    excess = frame.get(f"fwd_{horizon}y_excess_cagr")
    if excess is not None and len(frame):
        out["mean_excess_cagr"] = float(np.nanmean(excess.to_numpy(dtype=float)))
        out["beat_benchmark"] = float(np.nanmean(excess.to_numpy(dtype=float) > 0))
    drawdown = frame.get(f"fwd_{horizon}y_max_drawdown_from_entry")
    if drawdown is not None and len(frame):
        out["fell_30pct"] = float(
            np.nanmean(drawdown.to_numpy(dtype=float) >= 0.3)
        )
    delisted = frame.get(f"delisted_in_window_{horizon}y")
    if delisted is not None and len(frame):
        out["delisted"] = float((delisted.astype(str) != "false").mean())
    for name, label in label_columns.items():
        if label in frame.columns and len(frame):
            out[f"label_rate_{name}"] = float(
                frame[label].astype("boolean").astype(float).mean()
            )
    return out


def _era_mix(frame: pd.DataFrame) -> str:
    """`2005-09: 4, 2010-14: 7, ...` over the analogues' snapshot years."""
    if frame.empty:
        return ""
    years = pd.to_datetime(frame["snapshot_date"]).dt.year
    start = (years // 5) * 5
    counts = start.value_counts().sort_index()
    return ", ".join(f"{int(s)}-{str(int(s) + 4)[2:]}: {int(n)}" for s, n in counts.items())


# ---------------------------------------------------------------- report


def _pct(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{100.0 * float(v):.1f}%"


def _num(v, digits: int = 3) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)) or pd.isna(v):
        return "—"
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "no"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.{digits}f}"
    return str(v)


def _table(frame: pd.DataFrame) -> str:
    head = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    rule = "| " + " | ".join("---" for _ in frame.columns) + " |"
    body = [
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in frame.itertuples(index=False)
    ]
    return "\n".join([head, rule, *body])


def write_report(
    path: Path,
    result: dict,
    queries: pd.DataFrame,
    ranking: pd.DataFrame,
    names: list[str],
    bundles: list[DeploymentBundle],
    source_name: str,
    dataset: Dataset,
) -> Path:
    horizon = max(result["horizons"])
    pool = result["pool_summary"]
    lines = [
        f"# Historical analogues — {source_name}",
        "",
        "For each pick, the labeled historical rows most similar to it as "
        "the models see it, and what they went on to do. **This is an "
        "explanation, not an evaluation**: the deployment models were "
        "fitted on these very rows, so the analogues' outcome rates are "
        "in-sample by construction. They say what kind of history a pick "
        "resembles; they are not an accuracy or a probability for it.",
        "",
        f"- models: " + "; ".join(
            f"`{n}` ({b.train_config.model_name}"
            + (f", `{b.model.rank_column}`" if getattr(b.model, "rank_column", None) else "")
            + ")" for n, b in zip(names, bundles)
        ),
        f"- similarity: for a tree model the share of trees in which the "
        "row shares the pick's leaf; for a rank factor one minus the "
        "distance on its column; the mean of the models' similarities "
        "orders the list",
        f"- pool: dataset `{dataset.version}`, median-kind rows with a "
        f"{horizon}-year outcome: {pool['rows']:,} rows of "
        f"{pool['stocks']:,} stocks; one row per stock is listed, the "
        "pick's own history left out",
        f"- outcomes are over {horizon} years from the snapshot "
        "(the dataset's label convention: a delisted stock's final price "
        "is carried flat to the horizon)",
        "",
        "## Summary",
        "",
        f"What each pick's analogues went on to do over {horizon} years, "
        "beside the whole pool.",
        "",
    ]
    summary = result["summary"].copy()
    view = pd.DataFrame({"pick": summary["pick"]})
    view["analogues"] = summary["analogues"]
    view["mean similarity"] = summary["mean_similarity"].map(lambda v: _num(v, 2))
    labels = {
        "lost_money": "lost money", "median_cagr": "median CAGR",
        "mean_cagr": "mean CAGR", "mean_excess_cagr": "mean excess CAGR",
        "beat_benchmark": "beat the benchmark", "fell_30pct": "fell 30% from entry",
        "delisted": "delisted",
    }
    for key, title in labels.items():
        if key in summary.columns:
            view[title] = summary[key].map(_pct)
    for name in result["label_columns"]:
        key = f"label_rate_{name}"
        if key in summary.columns:
            view[f"`{name}` label true"] = summary[key].map(_pct)
    pool_row = {"pick": "*whole pool*", "analogues": pool["rows"], "mean similarity": "—"}
    for key, title in labels.items():
        if title in view.columns:
            pool_row[title] = _pct(pool.get(key))
    for name in result["label_columns"]:
        title = f"`{name}` label true"
        if title in view.columns:
            pool_row[title] = _pct(pool.get(f"label_rate_{name}"))
    view = pd.concat([view, pd.DataFrame([pool_row])], ignore_index=True)
    lines += [_table(view), ""]

    analogues = result["analogues"]
    rank_cols = [c for c in ranking.columns if c.startswith(("rank_", "score_"))]
    for i in range(len(queries)):
        query = queries.iloc[i]
        ticker = query.get("ticker", query["permaticker"])
        lines += [f"## {ticker}", ""]
        info = ranking[ranking["permaticker"] == query["permaticker"]]
        facts = []
        if "sector" in queries.columns:
            facts.append(f"sector {query['sector']}")
        if not info.empty:
            r = info.iloc[0]
            if "pick" in info.columns and pd.notna(r.get("pick")):
                facts.append(f"pick {int(r['pick'])}")
            if "mean_rank" in info.columns:
                facts.append(f"mean rank {float(r['mean_rank']):.1f} of {len(ranking):,}")
            elif "rank" in info.columns:
                facts.append(f"rank {int(r['rank'])} of {len(ranking):,}")
            for c in rank_cols:
                if c.startswith("rank_"):
                    facts.append(f"{c[5:]}: rank {int(r[c])}")
        if facts:
            lines += ["; ".join(facts) + ".", ""]
        used = result["paths"][i][:PATH_FEATURES]
        if used:
            lines += [
                "What the tree model split on along this stock's paths "
                "(share of trees), with the stock's value:",
                "",
                _table(pd.DataFrame({
                    "feature": [f for f, _ in used],
                    "share of trees": [_pct(s) for _, s in used],
                    f"{ticker}": [_num(query.get(f)) for f, _ in used],
                })),
                "",
            ]
        mine = analogues[analogues["pick_permaticker"] == query["permaticker"]]
        if mine.empty:
            lines += ["No analogues.", ""]
            continue
        summary_row = result["summary"].iloc[i]
        lines += [f"Analogues by era: {summary_row['eras']}.", ""]
        cols = ["analogue", "ticker", "snapshot_date", "similarity"]
        cols += result["similarity_columns"]
        if "sector" in mine.columns:
            cols.append("sector")
        # the report shows the short horizon's return and the long
        # horizon in full; the CSV has every outcome column
        cols += [
            c for c in result["outcomes"]
            if c.startswith(f"fwd_{horizon}y_")
            or c == f"delisted_in_window_{horizon}y"
            or (c.endswith("y_cagr") and not c.startswith(f"fwd_{horizon}y_"))
        ]
        cols += [f"label_{n}" for n in result["label_columns"]]
        cols += [f for f, _ in used if f in mine.columns]
        table = mine[[c for c in cols if c in mine.columns]].copy()
        for c in table.columns:
            if c.startswith("fwd_"):
                table[c] = table[c].map(_pct)
            elif c in ("similarity", *result["similarity_columns"]):
                table[c] = table[c].map(lambda v: _num(v, 2))
            elif c not in ("analogue", "ticker", "snapshot_date", "sector"):
                table[c] = table[c].map(_num)
        lines += [_table(table), ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    return path


# ------------------------------------------------------------------- run


def run_analogues(
    bundle_dirs: list[str | Path],
    inference_path: str | Path,
    *,
    tickers: list[str] | None = None,
    filters: list[FilterSpec] | tuple = (),
    pick: int | None = None,
    max_per_group: int | None = None,
    group_column: str = "sector",
    top: int = DEFAULT_ANALOGUES,
    include_self: bool = False,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    results_path: str | Path = DEFAULT_RESULTS,
    predictions_dir: str | Path = DEFAULT_PREDICTIONS,
) -> dict:
    """Rank the inference data as `vml-predict` does, take the picks (or
    the named tickers) and write their historical analogues: a report
    (`.md`), every analogue row (`.csv`) and a provenance sidecar."""
    if not tickers and pick is None:
        raise ConfigError(
            "name the stocks to explain: --pick K (the list vml-predict "
            "would buy) or --tickers A,B"
        )
    bundles = [DeploymentBundle.load(d) for d in bundle_dirs]
    names = _bundle_column_names(bundles)
    versions = sorted({b.train_config.dataset_version for b in bundles})
    if len(versions) != 1:
        raise ConfigError(
            f"the bundles were trained on different dataset versions: {versions}"
        )
    common = dict(
        results_path=results_path, predictions_dir=predictions_dir,
        top_n=10 ** 9, filters=list(filters), pick=pick,
        max_per_group=max_per_group, group_column=group_column,
    )
    if len(bundle_dirs) == 1:
        ranked = predict_with_bundle(bundle_dirs[0], inference_path, **common)
    else:
        ranked = predict_with_bundles(list(bundle_dirs), inference_path, **common)
    ranking = ranked["top"]
    frame, source_name = load_inference_frame(inference_path)
    if tickers:
        wanted = [t.strip() for t in tickers if t.strip()]
        if "ticker" not in ranking.columns:
            raise DatasetValidationError(
                "the inference data has no `ticker` column to match "
                "--tickers on"
            )
        chosen = ranking[ranking["ticker"].isin(wanted)]
        absent = sorted(set(wanted) - set(chosen["ticker"]))
        if absent:
            raise ConfigError(
                f"not in the ranking (absent from the inference data, or "
                f"outside the universe or the filters): {absent}"
            )
    else:
        chosen = ranked["picks"]
    order = list(chosen["permaticker"])
    queries = (
        frame[frame["permaticker"].isin(order)]
        .drop_duplicates("permaticker")
        .set_index("permaticker")
        .loc[order]
        .reset_index()
    )
    dataset = Dataset(Path(data_root) / versions[0])
    result = find_analogues(
        bundles, names, queries, dataset, top=top, include_self=include_self
    )
    stem = Path(ranked["output_path"]).with_suffix("")
    out_csv = Path(f"{stem}__analogues.csv")
    out_md = Path(f"{stem}__analogues.md")
    result["analogues"].to_csv(out_csv, index=False)
    write_report(
        out_md, result, queries, ranking, names, bundles, source_name, dataset
    )
    meta = {
        "scored_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": git_sha(),
        "inference_source": str(inference_path),
        "dataset_version": versions[0],
        "bundles": [str(d) for d in bundle_dirs],
        "method": {
            n: ("rank column " + b.model.rank_column)
            if getattr(b.model, "rank_column", None)
            else "shared leaves (share of trees)"
            for n, b in zip(names, bundles)
        },
        "picks": [str(t) for t in result["summary"]["pick"]],
        "analogues_per_pick": top,
        "include_self": include_self,
        "pool": result["pool_summary"],
        "ranking": str(ranked["output_path"]),
        "note": (
            "Explanation, not evaluation: the deployment models were "
            "fitted on the pool rows, so analogue outcome rates are "
            "in-sample. Never a model input."
        ),
    }
    meta_path = Path(f"{out_csv}.meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True, default=str))
    return {
        **result,
        "report_path": out_md,
        "csv_path": out_csv,
        "meta_path": meta_path,
        "ranking_path": ranked["output_path"],
    }


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Historical analogues of today's picks: the labeled "
        "rows most similar to each pick as the models see it (shared "
        "leaves for tree models, closeness on the column for rank "
        "factors), and what they went on to do. Explanation, not "
        "evaluation."
    )
    parser.add_argument("bundles", nargs="+", metavar="bundle",
                        help="deployment bundle directories, as for vml-predict")
    parser.add_argument("inference", help="inference dataset directory or parquet")
    parser.add_argument("--tickers", default=None,
                        help="comma-separated tickers to explain instead of the picks")
    parser.add_argument("--filter", action="append", default=[],
                        metavar="'COLUMN OP VALUE'", help="as for vml-predict")
    parser.add_argument("--pick", type=int, default=None, metavar="K",
                        help="explain the K picks vml-predict would mark")
    parser.add_argument("--max-per-group", type=int, default=None, metavar="N")
    parser.add_argument("--group-column", default="sector")
    parser.add_argument("--top", type=int, default=DEFAULT_ANALOGUES,
                        help=f"analogues listed per pick (default {DEFAULT_ANALOGUES})")
    parser.add_argument("--include-self", action="store_true",
                        help="keep the pick's own past snapshots in its list")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--predictions-dir", default=str(DEFAULT_PREDICTIONS))
    args = parser.parse_args(argv)
    try:
        out = run_analogues(
            args.bundles, args.inference,
            tickers=args.tickers.split(",") if args.tickers else None,
            filters=[FilterSpec.parse(t, "--filter") for t in args.filter],
            pick=args.pick, max_per_group=args.max_per_group,
            group_column=args.group_column, top=args.top,
            include_self=args.include_self, data_root=args.data_root,
            results_path=args.results, predictions_dir=args.predictions_dir,
        )
    except Exception:
        traceback.print_exc()
        print("analogues FAILED")
        return 1
    print(f"analogues of {len(out['summary'])} picks: {out['report_path']}")
    print(f"every analogue row: {out['csv_path']}")
    view = out["summary"].drop(columns=["pick_permaticker"], errors="ignore")
    print(view.round(3).to_string(index=False))
    print("\nExplanation, not evaluation: the models were fitted on these rows.")
    return 0


def main() -> None:
    import sys

    sys.exit(_main())


if __name__ == "__main__":
    main()
