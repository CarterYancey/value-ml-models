"""Point-in-time monthly cross-sections from a training dataset.

The upstream inference directory is the wrong input for a backtest: it is
survivor-only by construction (data/manual.md §9). `dataset.parquet`
keeps every stock that later delisted, so the honest historical
cross-section at a trade date is built from it:

- **median-kind snapshots only** — the same single-entry-price convention
  evaluation uses; low/high are a training-time gradient;
- **completed quarters only** — a quarter's low/median/high touch dates
  are only knowable once the quarter has ended, so a snapshot becomes
  usable the day after its calendar quarter closes (its features were
  point-in-time at `snapshot_date` all along; this guards the *choice*
  of snapshot, not the features);
- **latest snapshot per permaticker**, capped by `max_staleness_days` —
  a stock that stopped filing ages out of the cross-section instead of
  being carried on stale fundamentals forever;
- **no label columns** — the frame carries key_meta + features + ranks +
  sector_ranks only, so downstream filters and scoring are structurally
  unable to peek at outcomes.

This differs from live inference (which re-ranks a fresh same-day
cross-section) in one disclosed way: features and ranks are up to a
quarter-plus stale, and ranks are relative to the snapshot's own
(quarter, kind) partition rather than the trade date's. Reports carry
that disclosure.
"""

from __future__ import annotations

import pandas as pd

from harness.dataset import Dataset


class CrossSectionBuilder:
    """Reusable builder: pre-filters the dataset once, then serves the
    point-in-time cross-section for any trade date."""

    #: cross-sections carry these manifest groups and nothing else —
    #: labels and sample weights are outcomes and never enter a screen
    GROUPS = ("key_meta", "features", "ranks", "sector_ranks")

    def __init__(self, dataset: Dataset, max_staleness_days: int):
        self.dataset = dataset
        self.max_staleness_days = int(max_staleness_days)
        columns = [c for g in self.GROUPS for c in dataset.columns(g)]
        median = dataset.data.loc[
            dataset.data["snapshot_kind"] == "median", columns
        ].copy()
        median["snapshot_date"] = pd.to_datetime(median["snapshot_date"])
        quarter = pd.to_datetime(median["quarter"])
        median["_quarter_end"] = (
            quarter + pd.DateOffset(months=3) - pd.Timedelta(days=1)
        )
        self._median = median.sort_values(
            ["permaticker", "snapshot_date"], kind="mergesort"
        )

    def at(self, trade_date: pd.Timestamp) -> pd.DataFrame:
        """One row per stock: its latest completed-quarter median snapshot
        as of `trade_date`, no older than `max_staleness_days`."""
        trade_date = pd.Timestamp(trade_date)
        usable = self._median[self._median["_quarter_end"] < trade_date]
        latest = usable.groupby("permaticker", sort=False).tail(1)
        age = (trade_date - latest["snapshot_date"]).dt.days
        fresh = latest[age <= self.max_staleness_days]
        return fresh.drop(columns=["_quarter_end"]).reset_index(drop=True)
