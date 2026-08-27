"""Build a versioned price panel (`data/datasets/prices_vX.Y/`) from the
upstream raw Sharadar tables — the same price source the labels use.

The upstream contract (sharadar-dataset README §2/§6): labels are
computed from `SEP.closeadj` (total-return adjusted — splits and
dividends), the benchmark comes from `SFP` (SPY adjusted close), the
canonical entity key is `permaticker`, and `ticker` is a join key only,
resolved through `TICKERS`. This script applies exactly those
conventions to extract forward price *paths* for the Phase-4 backtest:

    python scripts/build_price_panel.py <raw_dir> <dataset_vX.Y> \
        --out-version prices_v1.0

where `<raw_dir>` is the upstream `data/raw/` directory (or a symlink to
it, e.g. `data/raw -> ~/radarash-dataset/data/raw`) containing
`SEP.parquet`, `SFP.parquet`, and `TICKERS.parquet`, and `<dataset_vX.Y>`
is the pinned dataset whose permatickers define the panel universe.

**This is the one sanctioned read of raw Sharadar tables in this repo**,
and it is narrow by construction: the output carries `(permaticker,
date, closeadj)` and nothing else. Price paths after a trade date are
the *outcome* a backtest measures — the same role `closeadj` plays in
the upstream label build — not features. The ban on raw-table joins
(CLAUDE.md) protects the feature side, where the easy joins leak the
future; nothing this script produces can enter a model input or a
screen (`portfolio.crosssection` carries feature/rank columns only, and
`portfolio.signals` validates filters against the manifest).

The output directory is immutable once built (rerun with a bumped
`--out-version`, or `--force` to rebuild explicitly), records its full
provenance (raw-file metadata, mapping/cleaning counts, universe
coverage) in `manifest.json`, and is validated through
`portfolio.prices.PricePanel` before the script reports success.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from harness.dataset import Dataset  # noqa: E402
from harness.errors import DatasetValidationError  # noqa: E402
from harness.results import git_sha  # noqa: E402
from portfolio.prices import PricePanel  # noqa: E402

RAW_FILES = ("SEP.parquet", "SFP.parquet", "TICKERS.parquet")
DEFAULT_BENCHMARK = "SPY"


def load_ticker_map(
    raw_dir: Path, universe: set[int]
) -> tuple[pd.DataFrame, dict]:
    """`ticker -> permaticker` for the dataset universe, from TICKERS.

    Prefers the SEP table's rows when TICKERS carries a `table` column.
    A ticker mapping to more than one universe permaticker is ambiguous
    (ticker reuse) and is dropped, counted, and reported — silently
    picking one would stitch two companies' price series together.
    """
    tickers = pd.read_parquet(raw_dir / "TICKERS.parquet")
    for col in ("ticker", "permaticker"):
        if col not in tickers.columns:
            raise DatasetValidationError(
                f"{raw_dir}/TICKERS.parquet lacks column {col!r}"
            )
    if "table" in tickers.columns and (tickers["table"] == "SEP").any():
        tickers = tickers[tickers["table"] == "SEP"]
    mapping = tickers[["ticker", "permaticker"]].dropna().copy()
    mapping["permaticker"] = pd.to_numeric(
        mapping["permaticker"], errors="coerce"
    )
    mapping = mapping.dropna()
    mapping["permaticker"] = mapping["permaticker"].astype("int64")
    mapping = mapping[mapping["permaticker"].isin(universe)]
    mapping = mapping.drop_duplicates()

    counts = mapping.groupby("ticker")["permaticker"].nunique()
    ambiguous = sorted(counts[counts > 1].index)
    if ambiguous:
        mapping = mapping[~mapping["ticker"].isin(ambiguous)]
    stats = {
        "universe_permatickers": len(universe),
        "mapped_tickers": int(mapping["ticker"].nunique()),
        "mapped_permatickers": int(mapping["permaticker"].nunique()),
        "ambiguous_tickers_dropped": len(ambiguous),
    }
    return mapping, stats


def extract_prices(
    raw_dir: Path,
    mapping: pd.DataFrame,
    start: str | None,
) -> tuple[pd.DataFrame, dict]:
    """(permaticker, date, closeadj) from SEP for the mapped tickers,
    cleaned: non-positive/NULL closes and duplicate (permaticker, date)
    rows dropped — and counted, never silent."""
    sep = pd.read_parquet(
        raw_dir / "SEP.parquet", columns=["ticker", "date", "closeadj"]
    )
    sep = sep[sep["ticker"].isin(set(mapping["ticker"]))]
    prices = sep.merge(mapping, on="ticker", how="inner")
    del sep
    prices = prices[["permaticker", "date", "closeadj"]]
    prices["date"] = pd.to_datetime(prices["date"])
    if start:
        prices = prices[prices["date"] >= pd.Timestamp(start)]

    bad = prices["closeadj"].isna() | (prices["closeadj"] <= 0)
    n_bad = int(bad.sum())
    prices = prices[~bad]
    prices = prices.sort_values(
        ["permaticker", "date"], kind="mergesort"
    )
    dup = prices.duplicated(["permaticker", "date"], keep="last")
    n_dup = int(dup.sum())
    prices = prices[~dup]
    stats = {
        "rows": len(prices),
        "permatickers_with_prices": int(prices["permaticker"].nunique()),
        "dropped_nonpositive_close": n_bad,
        "dropped_duplicate_rows": n_dup,
        "first_date": str(prices["date"].min().date()) if len(prices) else None,
        "last_date": str(prices["date"].max().date()) if len(prices) else None,
    }
    return prices.reset_index(drop=True), stats


def extract_benchmark(
    raw_dir: Path, symbol: str, start: str | None
) -> pd.DataFrame:
    """The benchmark's (date, closeadj) series from SFP — same adjusted
    price the `beat_spy` labels are computed against."""
    sfp = pd.read_parquet(
        raw_dir / "SFP.parquet", columns=["ticker", "date", "closeadj"]
    )
    bench = sfp[sfp["ticker"] == symbol][["date", "closeadj"]].copy()
    if bench.empty:
        raise DatasetValidationError(
            f"{raw_dir}/SFP.parquet has no rows for benchmark {symbol!r}"
        )
    bench["date"] = pd.to_datetime(bench["date"])
    if start:
        bench = bench[bench["date"] >= pd.Timestamp(start)]
    bench = bench[bench["closeadj"].notna() & (bench["closeadj"] > 0)]
    bench = bench.sort_values("date", kind="mergesort")
    bench = bench[~bench.duplicated("date", keep="last")]
    return bench.reset_index(drop=True)


def _raw_provenance(raw_dir: Path) -> dict:
    """Embed the upstream ingest metadata (SEP.meta.json etc.) so the
    panel records exactly which raw pulls it came from."""
    out = {}
    for name in ("SEP", "SFP", "TICKERS"):
        meta = raw_dir / f"{name}.meta.json"
        if meta.exists():
            try:
                out[name] = json.loads(meta.read_text())
            except json.JSONDecodeError:
                out[name] = {"error": "unparseable meta.json"}
    return out


def build_price_panel(
    raw_dir: str | Path,
    dataset_dir: str | Path,
    out_dir: str | Path,
    *,
    benchmark: str = DEFAULT_BENCHMARK,
    start: str | None = None,
    force: bool = False,
) -> Path:
    raw_dir, out_dir = Path(raw_dir), Path(out_dir)
    missing = [f for f in RAW_FILES if not (raw_dir / f).exists()]
    if missing:
        raise DatasetValidationError(
            f"raw directory {raw_dir} is missing {missing} (expected the "
            "upstream data/raw/ layout)"
        )
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise DatasetValidationError(
            f"{out_dir} already exists; a price panel is immutable once "
            "built — bump --out-version, or pass --force to rebuild it "
            "explicitly"
        )

    dataset = Dataset(dataset_dir)
    universe = {int(p) for p in dataset.data["permaticker"].unique()}

    mapping, map_stats = load_ticker_map(raw_dir, universe)
    prices, price_stats = extract_prices(raw_dir, mapping, start)
    if prices.empty:
        raise DatasetValidationError(
            "no SEP price rows survived mapping/cleaning — wrong raw "
            "directory or dataset?"
        )
    bench = extract_benchmark(raw_dir, benchmark, start)

    covered = price_stats["permatickers_with_prices"]
    coverage = covered / len(universe) if universe else 0.0

    out_dir.mkdir(parents=True, exist_ok=True)
    prices.to_parquet(out_dir / "prices.parquet", index=False)
    bench.to_parquet(out_dir / "benchmark.parquet", index=False)
    manifest = {
        "prices_version": out_dir.name,
        "benchmark": benchmark,
        "created_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "built_by_git_sha": git_sha(),
        "universe_dataset": dataset.version,
        "universe_dataset_dir": str(dataset_dir),
        "start": start,
        "universe_coverage": round(coverage, 4),
        "benchmark_rows": len(bench),
        "benchmark_first_date": str(bench["date"].min().date()),
        "benchmark_last_date": str(bench["date"].max().date()),
        **map_stats,
        **price_stats,
        "raw_provenance": _raw_provenance(raw_dir),
        "note": (
            "Extracted from raw SEP/SFP closeadj (total-return adjusted) "
            "— the labels' price source. Outcome price paths only: "
            "nothing here may be used as a model feature or screen."
        ),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True)
    )

    # acceptance test: the panel must load under the consumer's contract
    PricePanel(out_dir)
    return out_dir


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract a versioned backtest price panel from the "
        "upstream raw Sharadar tables (SEP prices + SFP benchmark, "
        "resolved to permatickers via TICKERS), restricted to a pinned "
        "dataset's permaticker universe."
    )
    parser.add_argument(
        "raw_dir",
        help="upstream data/raw directory (or symlink) containing "
        "SEP.parquet, SFP.parquet, TICKERS.parquet",
    )
    parser.add_argument(
        "dataset",
        help="dataset version directory name (e.g. dataset_v1.1) whose "
        "permatickers define the panel universe",
    )
    parser.add_argument(
        "--out-version",
        default="prices_v1.0",
        help="output directory name under --data-root (default "
        "prices_v1.0)",
    )
    parser.add_argument("--data-root", default="data/datasets")
    parser.add_argument(
        "--benchmark", default=DEFAULT_BENCHMARK,
        help=f"benchmark ticker in SFP (default {DEFAULT_BENCHMARK})",
    )
    parser.add_argument(
        "--start", default=None,
        help="drop prices before this date (ISO); default keeps all",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="rebuild an existing panel directory in place",
    )
    args = parser.parse_args(argv)
    out = build_price_panel(
        args.raw_dir,
        Path(args.data_root) / args.dataset,
        Path(args.data_root) / args.out_version,
        benchmark=args.benchmark,
        start=args.start,
        force=args.force,
    )
    manifest = json.loads((out / "manifest.json").read_text())
    print(f"price panel built: {out}")
    print(
        f"  {manifest['rows']} price rows, "
        f"{manifest['permatickers_with_prices']}/"
        f"{manifest['universe_permatickers']} universe permatickers "
        f"covered ({manifest['universe_coverage']:.1%}), "
        f"{manifest['first_date']} → {manifest['last_date']}"
    )
    print(
        f"  benchmark {manifest['benchmark']}: "
        f"{manifest['benchmark_rows']} rows, "
        f"{manifest['benchmark_first_date']} → "
        f"{manifest['benchmark_last_date']}"
    )
    print(
        f"  dropped: {manifest['dropped_nonpositive_close']} non-positive "
        f"closes, {manifest['dropped_duplicate_rows']} duplicates, "
        f"{manifest['ambiguous_tickers_dropped']} ambiguous tickers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
