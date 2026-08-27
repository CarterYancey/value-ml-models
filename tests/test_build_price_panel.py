"""Price-panel builder: raw SEP/SFP/TICKERS in, contract-valid
`prices_vX.Y/` out — mapping through TICKERS, ambiguous tickers dropped
(never silently stitched), cleaning counted, immutability enforced."""

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from harness.errors import DatasetValidationError  # noqa: E402
from portfolio.prices import PricePanel  # noqa: E402
from build_price_panel import build_price_panel  # noqa: E402

DAYS = pd.bdate_range("2015-01-02", "2015-03-31")


def _build_raw(root: Path) -> Path:
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    # AAA -> 100001, BBB -> 100002; AMB maps to two universe
    # permatickers (ticker reuse) and must be dropped; ZZZ maps to a
    # permaticker outside the dataset universe
    tickers = pd.DataFrame(
        [
            {"table": "SEP", "ticker": "AAA", "permaticker": 100001},
            {"table": "SEP", "ticker": "BBB", "permaticker": 100002},
            {"table": "SEP", "ticker": "AMB", "permaticker": 100003},
            {"table": "SEP", "ticker": "AMB", "permaticker": 100004},
            {"table": "SEP", "ticker": "ZZZ", "permaticker": 999999},
            {"table": "SF1", "ticker": "AAA", "permaticker": 100001},
        ]
    )
    tickers.to_parquet(raw / "TICKERS.parquet")

    def stock_rows(ticker, base):
        return pd.DataFrame(
            {
                "ticker": ticker,
                "date": DAYS.date,
                "closeadj": base + 0.01 * pd.RangeIndex(len(DAYS)),
                "close": base,  # extra raw columns are ignored
            }
        )

    sep = pd.concat(
        [
            stock_rows("AAA", 10.0),
            stock_rows("BBB", 20.0),
            stock_rows("AMB", 30.0),
            stock_rows("ZZZ", 40.0),
        ],
        ignore_index=True,
    )
    # a duplicate (ticker, date) row and a non-positive close to clean
    sep = pd.concat(
        [sep, sep.iloc[[0]].assign(closeadj=10.5)], ignore_index=True
    )
    sep.loc[1, "closeadj"] = 0.0
    sep.to_parquet(raw / "SEP.parquet")

    sfp = pd.DataFrame(
        {
            "ticker": ["SPY"] * len(DAYS) + ["QQQ"] * len(DAYS),
            "date": list(DAYS.date) * 2,
            "closeadj": [200.0 + i for i in range(len(DAYS))] * 2,
        }
    )
    sfp.to_parquet(raw / "SFP.parquet")
    (raw / "SEP.meta.json").write_text(json.dumps({"pulled": "2015-04-01"}))
    return raw


def test_builder_produces_contract_valid_panel(data_root, tmp_path):
    raw = _build_raw(tmp_path)
    out = build_price_panel(
        raw, data_root / "dataset_v0.0-test", tmp_path / "prices_v0.0"
    )
    panel = PricePanel(out)  # the contract check
    assert panel.benchmark_name == "SPY"
    # only unambiguous universe tickers survive
    assert panel.permatickers == {100001, 100002}
    series = panel.series(100001)
    assert len(series) == len(DAYS) - 1  # the zero-close row was dropped
    # duplicate kept last: first surviving AAA print is the 10.5 rewrite
    assert series.iloc[0] == pytest.approx(10.5)
    # benchmark holds only SPY, and defines the calendar
    assert len(panel.benchmark) == len(DAYS)
    assert panel.benchmark.iloc[0] == pytest.approx(200.0)

    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["ambiguous_tickers_dropped"] == 1
    assert manifest["dropped_nonpositive_close"] == 1
    assert manifest["dropped_duplicate_rows"] == 1
    assert manifest["permatickers_with_prices"] == 2
    assert manifest["universe_permatickers"] == 6
    assert manifest["raw_provenance"]["SEP"] == {"pulled": "2015-04-01"}


def test_builder_refuses_overwrite_without_force(data_root, tmp_path):
    raw = _build_raw(tmp_path)
    out = tmp_path / "prices_v0.0"
    build_price_panel(raw, data_root / "dataset_v0.0-test", out)
    with pytest.raises(DatasetValidationError, match="immutable"):
        build_price_panel(raw, data_root / "dataset_v0.0-test", out)
    build_price_panel(
        raw, data_root / "dataset_v0.0-test", out, force=True
    )


def test_builder_start_trim_and_missing_benchmark(data_root, tmp_path):
    raw = _build_raw(tmp_path)
    out = build_price_panel(
        raw,
        data_root / "dataset_v0.0-test",
        tmp_path / "prices_trim",
        start="2015-03-01",
    )
    panel = PricePanel(out)
    assert panel.series(100001).index.min() >= pd.Timestamp("2015-03-01")
    with pytest.raises(DatasetValidationError, match="benchmark"):
        build_price_panel(
            raw,
            data_root / "dataset_v0.0-test",
            tmp_path / "prices_nobench",
            benchmark="NOPE",
        )


def test_builder_requires_raw_files(data_root, tmp_path):
    with pytest.raises(DatasetValidationError, match="missing"):
        build_price_panel(
            tmp_path / "empty_raw",
            data_root / "dataset_v0.0-test",
            tmp_path / "prices_x",
        )
