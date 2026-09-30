"""Pick outcomes: what happened to the names a model picked, measured
on outcomes other than the label it was trained on.

Lift over a cell's own base rate says a label is learnable; it cannot
compare two labels, because each is measured against itself. The
question a label has to answer is whether picking by it builds a
portfolio that beats the market, and `vml-backtest` is the instrument
of record for that. This module is the screen in front of it: for the
top-K picks of each test year it reports realized outcomes named in the
config's `pick_outcomes` — a binary label (hit rate, e.g.
`label_3y_beat_spy`) or a continuous outcome column (mean and median,
e.g. `fwd_3y_excess_cagr`) — next to the same statistic over every test
row of the year. It is the no-cost, equal-weight, hold-to-horizon
reading of the picks, taken from the manifest's label columns.

The picks are exactly precision@K's (same ordering, same ties), one row
one pick, unweighted: a portfolio buys K names and each counts once. The
reference over all test rows is unweighted for the same reason — it is
the population the picks were drawn from, not a weighted base rate.

Test rows are median-kind snapshots, up to four per stock per test
year, so K picks can be fewer than K stocks; `n_stocks_at_K` says how
many distinct `permaticker`s the picks hold.

Pick outcomes are report-only. They never enter a fit, never rank a
sweep by default, and a run stays counted in the trial-ledger cell of
the label it trained on (or its `eval_label`).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from eval.metrics import _order_by_score

#: Prediction-frame column prefixes: a binary outcome (hit rate) and a
#: continuous one (mean and median). The kind travels in the column name
#: because frames are concatenated across folds.
BINARY_PREFIX = "outb__"
CONTINUOUS_PREFIX = "outc__"

#: Prediction-frame column holding the entity key of each test row.
STOCK_COLUMN = "permaticker"


def outcome_column(slug: str, binary: bool) -> str:
    return f"{BINARY_PREFIX if binary else CONTINUOUS_PREFIX}{slug}"


def outcome_columns(predictions: pd.DataFrame) -> list[tuple[str, str, bool]]:
    """(frame column, outcome slug, is_binary) for every pick outcome a
    predictions frame carries, in frame order."""
    found = []
    for col in predictions.columns:
        if col.startswith(BINARY_PREFIX):
            found.append((col, col[len(BINARY_PREFIX):], True))
        elif col.startswith(CONTINUOUS_PREFIX):
            found.append((col, col[len(CONTINUOUS_PREFIX):], False))
    return found


def has_pick_outcomes(predictions: pd.DataFrame) -> bool:
    return bool(outcome_columns(predictions))


def _mean(vals: np.ndarray) -> float:
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else math.nan


def _median(vals: np.ndarray) -> float:
    vals = vals[np.isfinite(vals)]
    return float(np.median(vals)) if len(vals) else math.nan


def _top(scores: np.ndarray, k: int) -> np.ndarray:
    if len(scores) == 0 or k <= 0:
        return np.array([], dtype=int)
    return _order_by_score(scores)[: min(k, len(scores))]


def _year_groups(
    predictions: pd.DataFrame, per_year: bool = True
) -> list[pd.DataFrame]:
    if not per_year:
        return [predictions]
    return [g for _, g in predictions.groupby("year", sort=True)]


def _picked_rows(groups: list[pd.DataFrame], k: int) -> pd.DataFrame:
    """The top-k rows of every year, stacked: picks are made per year
    because per-fold model scores are not comparable (eval.era)."""
    picked = [
        g.iloc[_top(g["score"].to_numpy(dtype=float), k)] for g in groups
    ]
    return pd.concat(picked) if picked else pd.DataFrame()


def _stocks_per_year(groups: list[pd.DataFrame], k: int) -> float:
    counts = [
        g.iloc[_top(g["score"].to_numpy(dtype=float), k)][STOCK_COLUMN].nunique()
        for g in groups
        if len(g)
    ]
    return float(np.mean(counts)) if counts else math.nan


def pick_outcome_metrics(
    predictions: pd.DataFrame, top_k=(20, 50), per_year: bool = True
) -> dict:
    """Flat pick-outcome metrics over a predictions frame, picking per
    year. One year in, one year's numbers out; several years in, the
    statistics run over all the years' picks together (and
    `n_stocks_at_K` is the mean per year). `per_year=False` picks once
    over the whole frame instead: a single fold's metrics, whose
    precision@K is taken over the fold's test rows the same way.

    Keys, per outcome `<o>` and per K:
    `pick_mean_<o>_at_K` (the hit rate when `<o>` is binary),
    `pick_median_<o>_at_K` (continuous only), and the reference over
    every test row `all_mean_<o>` / `all_median_<o>`. NULL outcomes are
    left out of a statistic, never counted as misses.
    """
    outcomes = outcome_columns(predictions)
    if not outcomes:
        return {}
    groups = _year_groups(predictions, per_year)
    out: dict = {}
    for col, slug, binary in outcomes:
        vals = predictions[col].to_numpy(dtype=float)
        out[f"all_mean_{slug}"] = _mean(vals)
        if not binary:
            out[f"all_median_{slug}"] = _median(vals)
    for k in top_k:
        picked = _picked_rows(groups, k)
        if STOCK_COLUMN in predictions.columns:
            out[f"n_stocks_at_{k}"] = _stocks_per_year(groups, k)
        for col, slug, binary in outcomes:
            vals = (
                picked[col].to_numpy(dtype=float)
                if len(picked)
                else np.array([], dtype=float)
            )
            out[f"pick_mean_{slug}_at_{k}"] = _mean(vals)
            if not binary:
                out[f"pick_median_{slug}_at_{k}"] = _median(vals)
    return out


def pick_outcome_table(predictions: pd.DataFrame, k: int) -> pd.DataFrame:
    """The per-test-year pick-outcome table for one K, with a pooled row
    (picks made per year, statistics over all picks). Columns per
    outcome: the picks' statistic, then the same statistic over every
    test row of the era."""
    outcomes = outcome_columns(predictions)
    rows = []

    def row(era: str, frame: pd.DataFrame) -> dict:
        m = pick_outcome_metrics(frame, top_k=(k,))
        groups = _year_groups(frame)
        r: dict = {
            "era": era,
            "picks": int(sum(min(k, len(g)) for g in groups)),
        }
        if f"n_stocks_at_{k}" in m:
            r["stocks"] = m[f"n_stocks_at_{k}"]
        for _, slug, binary in outcomes:
            if binary:
                r[f"{slug} hit rate"] = m[f"pick_mean_{slug}_at_{k}"]
                r[f"{slug} all rows"] = m[f"all_mean_{slug}"]
            else:
                r[f"{slug} mean"] = m[f"pick_mean_{slug}_at_{k}"]
                r[f"{slug} median"] = m[f"pick_median_{slug}_at_{k}"]
                r[f"{slug} all rows mean"] = m[f"all_mean_{slug}"]
                r[f"{slug} all rows median"] = m[f"all_median_{slug}"]
        return r

    for year, grp in predictions.groupby("year", sort=True):
        rows.append(row(str(int(year)), grp))
    rows.append(row("pooled", predictions))
    return pd.DataFrame(rows)
