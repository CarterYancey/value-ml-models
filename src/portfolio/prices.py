"""Loader for a versioned price panel (`data/datasets/prices_vX.Y/`).

The model dataset deliberately carries no price paths (labels are the
only outcomes), and rebuilding paths here from raw Sharadar tables is the
easy-join leak the contract bans. Backtests therefore consume a separate
versioned artifact, built upstream with the same survivorship discipline
as the labels — this module defines and enforces that contract:

    prices_vX.Y/
    ├── prices.parquet      permaticker, date, closeadj — daily,
    │                       total-return adjusted (splits + dividends),
    │                       every stock ever in the dataset universe,
    │                       carried through its final print (delisted
    │                       stocks included; the series simply ends)
    ├── benchmark.parquet   date, closeadj — the comparison series (SPY),
    │                       same adjustment convention; its dates define
    │                       the trading calendar
    └── manifest.json       {"prices_version", "benchmark", "start_date",
                             "end_date", "rows", "permatickers", ...}

Because `closeadj` is total-return adjusted, holding a fixed share count
implicitly reinvests dividends — the same convention the upstream labels
use. A panel that only covers survivors would silently un-do the
dataset's survivorship discipline, so coverage against the model
dataset's permatickers is reported by the backtest, not assumed.

Until the upstream builder ships this artifact, the file is the request:
anything that validates here can be consumed.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from harness.errors import DatasetValidationError

REQUIRED_FILES = ("prices.parquet", "benchmark.parquet", "manifest.json")
REQUIRED_MANIFEST = ("prices_version", "benchmark")


class PricePanel:
    """A pinned, immutable `prices_vX.Y` directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        if not self.root.is_dir():
            raise DatasetValidationError(
                f"price panel directory not found: {self.root}"
            )
        missing = [f for f in REQUIRED_FILES if not (self.root / f).exists()]
        if missing:
            raise DatasetValidationError(
                f"{self.root} is missing required files: {missing}"
            )
        with open(self.root / "manifest.json") as fh:
            self.manifest: dict = json.load(fh)
        absent = [k for k in REQUIRED_MANIFEST if k not in self.manifest]
        if absent:
            raise DatasetValidationError(
                f"{self.root}/manifest.json lacks fields {absent}"
            )
        self._prices = self._load_prices()
        self._benchmark = self._load_benchmark()
        self._by_stock: dict[int, pd.Series] = {}

    # ------------------------------------------------------------- loading

    def _load_prices(self) -> pd.DataFrame:
        df = pd.read_parquet(self.root / "prices.parquet")
        required = {"permaticker", "date", "closeadj"}
        missing = sorted(required - set(df.columns))
        if missing:
            raise DatasetValidationError(
                f"{self.root}/prices.parquet lacks columns {missing}"
            )
        df = df[["permaticker", "date", "closeadj"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        if df.duplicated(["permaticker", "date"]).any():
            raise DatasetValidationError(
                f"{self.root}/prices.parquet has duplicate "
                "(permaticker, date) rows"
            )
        bad = df["closeadj"].isna() | (df["closeadj"] <= 0)
        if bad.any():
            raise DatasetValidationError(
                f"{self.root}/prices.parquet has {int(bad.sum())} rows with "
                "non-positive or NULL closeadj"
            )
        return df.sort_values(["permaticker", "date"], kind="mergesort")

    def _load_benchmark(self) -> pd.Series:
        df = pd.read_parquet(self.root / "benchmark.parquet")
        missing = sorted({"date", "closeadj"} - set(df.columns))
        if missing:
            raise DatasetValidationError(
                f"{self.root}/benchmark.parquet lacks columns {missing}"
            )
        dates = pd.to_datetime(df["date"])
        if dates.duplicated().any():
            raise DatasetValidationError(
                f"{self.root}/benchmark.parquet has duplicate dates"
            )
        if (df["closeadj"].isna() | (df["closeadj"] <= 0)).any():
            raise DatasetValidationError(
                f"{self.root}/benchmark.parquet has non-positive or NULL "
                "closeadj"
            )
        series = pd.Series(
            df["closeadj"].to_numpy(dtype=float), index=pd.DatetimeIndex(dates)
        ).sort_index()
        if len(series) < 2:
            raise DatasetValidationError(
                f"{self.root}/benchmark.parquet is too short to define a "
                "trading calendar"
            )
        return series

    # -------------------------------------------------------------- access

    @property
    def version(self) -> str:
        return str(self.manifest["prices_version"])

    @property
    def benchmark_name(self) -> str:
        return str(self.manifest["benchmark"])

    @property
    def benchmark(self) -> pd.Series:
        return self._benchmark

    @property
    def trading_days(self) -> pd.DatetimeIndex:
        """The benchmark's dates are the calendar: a day the benchmark
        did not print is not a trading day."""
        return pd.DatetimeIndex(self._benchmark.index)

    @property
    def permatickers(self) -> set[int]:
        return set(int(p) for p in self._prices["permaticker"].unique())

    def series(self, permaticker: int) -> pd.Series | None:
        """The stock's full adjusted-close series (date-indexed,
        ascending), or None if the panel has never seen it."""
        pt = int(permaticker)
        if pt not in self._by_stock:
            sel = self._prices[self._prices["permaticker"] == pt]
            if sel.empty:
                return None
            self._by_stock[pt] = pd.Series(
                sel["closeadj"].to_numpy(dtype=float),
                index=pd.DatetimeIndex(sel["date"]),
            )
        return self._by_stock[pt]

    def month_first_trading_days(
        self, start: date, end: date
    ) -> list[pd.Timestamp]:
        """The first trading day of each calendar month within
        [start, end], per the benchmark calendar."""
        days = self.trading_days
        days = days[(days >= pd.Timestamp(start)) & (days <= pd.Timestamp(end))]
        if len(days) == 0:
            return []
        frame = pd.DataFrame({"d": days})
        firsts = frame.groupby(frame["d"].dt.to_period("M"))["d"].min()
        return [pd.Timestamp(d) for d in firsts]


class SeriesPriceSource:
    """Price lookups over date-indexed series — the engine's only view of
    prices, shared by the stock panel and the benchmark so both legs of a
    comparison run through identical accounting."""

    def __init__(self, series_by_asset):
        """`series_by_asset`: asset -> pd.Series (ascending DatetimeIndex),
        or a callable asset -> pd.Series | None."""
        self._lookup = (
            series_by_asset
            if callable(series_by_asset)
            else lambda a: series_by_asset.get(a)
        )

    def asof(
        self, asset, when: pd.Timestamp, max_age_days: int
    ) -> tuple[float, pd.Timestamp] | None:
        """(price, print_date) of the last print on or before `when`, or
        None when there is no print within `max_age_days` of it."""
        series = self._lookup(asset)
        if series is None or series.empty:
            return None
        idx = series.index.searchsorted(when, side="right") - 1
        if idx < 0:
            return None
        print_date = series.index[idx]
        if (when - print_date) > timedelta(days=max_age_days):
            return None
        return float(series.iloc[idx]), print_date

    def final_print(self, asset) -> tuple[float, pd.Timestamp] | None:
        series = self._lookup(asset)
        if series is None or series.empty:
            return None
        return float(series.iloc[-1]), series.index[-1]


def stock_price_source(panel: PricePanel) -> SeriesPriceSource:
    return SeriesPriceSource(lambda pt: panel.series(pt))


def benchmark_price_source(panel: PricePanel) -> SeriesPriceSource:
    return SeriesPriceSource({panel.benchmark_name: panel.benchmark})
