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

Two further readings of the same outcomes, both report-only:

- **the portfolio screen** (`[pick_screen]`): the top K rows of every
  test quarter, at most `max_per_group` of them from one sector. That is
  the backtest template's selection rule applied to the test rows (a
  backtest buys from the latest completed quarter's median snapshots,
  which are the test rows). Top-K-per-year picks count rows, not
  sectors: on 2026-09-29 they showed a forest's picks level with SPY
  while the uncapped portfolio of the same picks was a utilities and
  REIT portfolio with a deeper drawdown than SPY's. The screen shows
  what was picked, by group, beside what it went on to do;
- **selection by score** (`score_thresholds`): every row scored at or
  above a threshold, per year and pooled, with how many names that is.
  Holding nothing in a year is a valid outcome and is shown as such.

Pick outcomes are report-only. They never enter a fit, never rank a
sweep by default, and a run stays counted in the trial-ledger cell of
the label it trained on (or its `eval_label`).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from eval.metrics import _order_by_score, threshold_tag

#: Prediction-frame column prefixes: a binary outcome (hit rate) and a
#: continuous one (mean and median). The kind travels in the column name
#: because frames are concatenated across folds.
BINARY_PREFIX = "outb__"
CONTINUOUS_PREFIX = "outc__"

#: Prediction-frame column holding the entity key of each test row.
STOCK_COLUMN = "permaticker"

#: Prediction-frame columns the portfolio screen reads: the calendar
#: quarter of the row's snapshot ("2014Q3") and the group the cap counts
#: (the config's `group_column`, `sector` by default).
QUARTER_COLUMN = "quarter"
GROUP_COLUMN = "group"

#: the group a row without one is counted in (as in the backtest)
UNKNOWN_GROUP = "unknown"


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


# ------------------------------------------------------------ the screen


def _capped_top(frame: pd.DataFrame, k: int, max_per_group: int | None) -> pd.DataFrame:
    """The first `k` rows of `frame` in score order, skipping a row once
    `max_per_group` of the picks share its group: the backtest's
    `capped_top_k` on a predictions frame."""
    if not len(frame) or k <= 0:
        return frame.iloc[:0]
    ordered = frame.iloc[_order_by_score(frame["score"].to_numpy(dtype=float))]
    if max_per_group is None:
        return ordered.iloc[:k]
    groups = ordered[GROUP_COLUMN].astype(object)
    groups = groups.where(groups.notna(), UNKNOWN_GROUP).to_numpy()
    taken: dict = {}
    keep = []
    for pos, group in enumerate(groups):
        if len(keep) >= k:
            break
        if taken.get(group, 0) >= max_per_group:
            continue
        taken[group] = taken.get(group, 0) + 1
        keep.append(pos)
    return ordered.iloc[keep]


def has_screen_columns(predictions: pd.DataFrame, screen) -> bool:
    """Whether a predictions frame carries what `screen` reads."""
    if screen is None:
        return False
    need = [QUARTER_COLUMN if screen.per == "quarter" else "year"]
    if screen.max_per_group is not None:
        need.append(GROUP_COLUMN)
    return all(c in predictions.columns for c in need)


def screen_picks(predictions: pd.DataFrame, screen) -> pd.DataFrame:
    """The rows the portfolio screen picks: per test quarter (or year),
    the top `screen.top_k` by score under the group cap. Periods are
    picked separately because scores are not comparable between them
    (eval.era), and because a portfolio buys every period."""
    period = QUARTER_COLUMN if screen.per == "quarter" else "year"
    picked = [
        _capped_top(grp, screen.top_k, screen.max_per_group)
        for _, grp in predictions.groupby(period, sort=True)
    ]
    return pd.concat(picked) if picked else predictions.iloc[:0]


def _outcome_stats(prefix: str, rows: pd.DataFrame, outcomes, suffix: str = "") -> dict:
    out: dict = {}
    for col, slug, binary in outcomes:
        vals = (
            rows[col].to_numpy(dtype=float)
            if len(rows)
            else np.array([], dtype=float)
        )
        out[f"{prefix}_mean_{slug}{suffix}"] = _mean(vals)
        if not binary:
            out[f"{prefix}_median_{slug}{suffix}"] = _median(vals)
    return out


def screen_metrics(predictions: pd.DataFrame, screen) -> dict:
    """Flat metrics of the portfolio screen over a predictions frame
    (one fold, or all of them): `screen_n` picks, `screen_precision`
    (the picks' hit rate on the run's own label), `screen_n_stocks`
    distinct stocks, `screen_top_group_share` (the largest group's share
    of the picks, when the frame carries groups), and per pick outcome
    `screen_mean_<o>` / `screen_median_<o>`."""
    if not has_screen_columns(predictions, screen):
        return {}
    picks = screen_picks(predictions, screen)
    out: dict = {
        "screen_n": int(len(picks)),
        "screen_precision": _mean(picks["y_true"].to_numpy(dtype=float)),
    }
    if STOCK_COLUMN in picks.columns:
        out["screen_n_stocks"] = int(picks[STOCK_COLUMN].nunique())
    if GROUP_COLUMN in picks.columns and len(picks):
        groups = picks[GROUP_COLUMN].astype(object)
        groups = groups.where(groups.notna(), UNKNOWN_GROUP)
        out["screen_top_group_share"] = float(
            groups.value_counts(normalize=True).iloc[0]
        )
    out.update(_outcome_stats("screen", picks, outcome_columns(predictions)))
    return out


def screen_table(predictions: pd.DataFrame, screen) -> pd.DataFrame:
    """The screen by test year, with a pooled row: picks, distinct
    stocks, the largest group and its share, precision on the run's
    label, and every pick outcome's statistics over the picks."""
    outcomes = outcome_columns(predictions)
    picks = screen_picks(predictions, screen)

    def row(era: str, frame: pd.DataFrame) -> dict:
        r: dict = {"era": era, "picks": int(len(frame))}
        if STOCK_COLUMN in frame.columns:
            r["stocks"] = int(frame[STOCK_COLUMN].nunique())
        if GROUP_COLUMN in frame.columns:
            groups = frame[GROUP_COLUMN].astype(object)
            groups = groups.where(groups.notna(), UNKNOWN_GROUP)
            counts = groups.value_counts(normalize=True)
            r["largest group"] = str(counts.index[0]) if len(counts) else "—"
            r["its share"] = float(counts.iloc[0]) if len(counts) else math.nan
        r["precision"] = _mean(frame["y_true"].to_numpy(dtype=float))
        for col, slug, binary in outcomes:
            vals = frame[col].to_numpy(dtype=float)
            if binary:
                r[f"{slug} hit rate"] = _mean(vals)
            else:
                r[f"{slug} mean"] = _mean(vals)
                r[f"{slug} median"] = _median(vals)
        return r

    rows = [
        row(str(int(year)), grp) for year, grp in picks.groupby("year", sort=True)
    ]
    rows.append(row("pooled", picks))
    return pd.DataFrame(rows)


def screen_group_table(predictions: pd.DataFrame, screen) -> pd.DataFrame:
    """What the screen picked, by group: each group's share of the picks
    beside its share of all test rows. Empty without a group column."""
    if GROUP_COLUMN not in predictions.columns:
        return pd.DataFrame()
    picks = screen_picks(predictions, screen)

    def shares(frame: pd.DataFrame) -> pd.Series:
        groups = frame[GROUP_COLUMN].astype(object)
        groups = groups.where(groups.notna(), UNKNOWN_GROUP)
        return groups.value_counts(normalize=True)

    picked, universe = shares(picks), shares(predictions)
    table = pd.DataFrame(
        {
            "group": universe.index,
            "share of picks": [float(picked.get(g, 0.0)) for g in universe.index],
            "share of test rows": universe.to_numpy(dtype=float),
        }
    )
    return table.sort_values(
        "share of picks", ascending=False, kind="mergesort"
    ).reset_index(drop=True)


# ------------------------------------------------- selection by score


def threshold_outcome_metrics(predictions: pd.DataFrame, thresholds) -> dict:
    """Pick outcomes of every row scored at or above each threshold,
    pooled: `thr_mean_<o>_at_<tag>` / `thr_median_<o>_at_<tag>`, the
    number of distinct stocks `thr_n_stocks_at_<tag>`, and
    `thr_years_at_<tag>`, the number of test years with at least one
    such row (the rest of the years hold nothing). The count and the
    precision of the selection are the metrics of record
    `n_at_thr_<tag>` and `precision_at_thr_<tag>`."""
    outcomes = outcome_columns(predictions)
    if not outcomes:
        return {}
    scores = predictions["score"].to_numpy(dtype=float)
    out: dict = {}
    for t in thresholds:
        tag = threshold_tag(t)
        sel = predictions[np.isfinite(scores) & (scores >= t)]
        if STOCK_COLUMN in sel.columns:
            out[f"thr_n_stocks_at_{tag}"] = int(sel[STOCK_COLUMN].nunique())
        out[f"thr_years_at_{tag}"] = int(sel["year"].nunique())
        out.update(_outcome_stats("thr", sel, outcomes, suffix=f"_at_{tag}"))
    return out


def threshold_outcome_table(predictions: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Selection by `score >= threshold`, by test year and pooled: how
    many rows and stocks clear the bar, how precise they are on the
    run's label, and what they went on to do. A year with no row at the
    bar is a year in cash and keeps its row."""
    outcomes = outcome_columns(predictions)
    scores = predictions["score"].to_numpy(dtype=float)
    chosen = predictions[np.isfinite(scores) & (scores >= threshold)]

    def row(era: str, frame: pd.DataFrame, n_all: int) -> dict:
        r: dict = {"era": era, "picks": int(len(frame)), "of rows": int(n_all)}
        if STOCK_COLUMN in frame.columns:
            r["stocks"] = int(frame[STOCK_COLUMN].nunique())
        r["precision"] = _mean(frame["y_true"].to_numpy(dtype=float))
        for col, slug, binary in outcomes:
            vals = frame[col].to_numpy(dtype=float)
            if binary:
                r[f"{slug} hit rate"] = _mean(vals)
            else:
                r[f"{slug} mean"] = _mean(vals)
                r[f"{slug} median"] = _median(vals)
        return r

    rows = []
    for year, grp in predictions.groupby("year", sort=True):
        rows.append(row(str(int(year)), chosen[chosen["year"] == year], len(grp)))
    rows.append(row("pooled", chosen, len(predictions)))
    return pd.DataFrame(rows)
