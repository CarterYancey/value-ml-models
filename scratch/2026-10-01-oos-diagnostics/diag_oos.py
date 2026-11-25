"""Decision 30 diagnostics: the candidate's picks against the stocks
they were chosen from, per leg, 2005-2026. No fit beyond the cached
year-end refits; no label column is read (outcomes come from the price
panel, the backtest report's own per-buy convention).

Writes CSVs to the scratchpad; nothing is logged to the ledger: no
portfolio is simulated and no configuration is evaluated on a label.
"""
from __future__ import annotations

import itertools
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")

from harness.dataset import Dataset  # noqa: E402
from harness.filters import FilterSpec, apply_filters  # noqa: E402
from portfolio.crosssection import CrossSectionBuilder  # noqa: E402
from portfolio.prices import PricePanel, stock_price_source  # noqa: E402
from portfolio.report import buy_outcomes  # noqa: E402
from portfolio.signals import ModelSet, combine_scores  # noqa: E402
from portfolio.strategy import capped_top_k  # noqa: E402

OUT = Path(sys.argv[1])
BUNDLES = [
    "experiments/models/forest_nonloser_dd30_3y_53ceedd93e6d",
    "experiments/models/factor_mom_12_2_3y_97c0f095cf48",
    "experiments/models/factor_roc_greenblatt_3y_da640394cbba",
]
SHORT = {"forest_nonloser_dd30_3y": "forest", "factor_mom_12_2_3y": "mom",
         "factor_roc_greenblatt_3y": "roc"}
FLOOR = [FilterSpec("dollar_volume_3m_rank", ">=", 0.2)]
END = date(2026, 8, 21)
HORIZONS = (1, 3)
WATCH = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "AVGO", "TSLA",
         "LLY", "COST", "NFLX", "V", "MA", "ORCL", "WMT", "XOM", "UNH",
         "JNJ", "PG", "HD"]

dataset = Dataset(Path("data/datasets/dataset_v1.4"))
panel = PricePanel(Path("data/datasets/prices_v1.0"))
model_set = ModelSet(BUNDLES)
years = list(range(2005, 2027))
model_set.prepare(years, dataset, "refit", 45,
                  refit_cache_dir="experiments/models/refits")
print("provenance:", [(p["fold_years"][0], p["fold_years"][-1],
                       p["policy_years"]) for p in model_set.provenance])
builder = CrossSectionBuilder(dataset, 200)
source = stock_price_source(panel)
dates = panel.month_first_trading_days(date(2005, 1, 1), END)
bench = panel.benchmark
end = pd.Timestamp(END)
legs = [SHORT[n] for n in model_set.names]
score_cols = dict(zip(legs, model_set.score_columns))
combos = [c for r in (1, 2, 3) for c in itertools.combinations(legs, r)]


def outcomes(frame: pd.DataFrame) -> pd.DataFrame:
    """Vectorised `portfolio.report.buy_outcomes`: per (asset, date,
    price) the annualised return over H years and its excess over the
    benchmark's; a stock that stops printing exits at its final print
    and the proceeds ride the benchmark to the horizon."""
    out = frame[["asset", "date", "price"]].copy()
    bidx = bench.index.values
    bval = bench.to_numpy()

    def bench_asof(when):
        i = np.searchsorted(bidx, when, side="right") - 1
        v = np.where(i >= 0, bval[np.clip(i, 0, None)], np.nan)
        return v

    start = bench_asof(out["date"].values)
    for h in HORIZONS:
        out[f"return_{h}y"] = np.nan
        out[f"excess_{h}y"] = np.nan
        out[f"early_exit_{h}y"] = np.nan
    target = {h: (out["date"] + pd.DateOffset(years=h)).values
              for h in HORIZONS}
    pos = {a: np.asarray(ix) for a, ix in
           out.groupby("asset", sort=False).indices.items()}
    cols = {h: [out.columns.get_loc(f"{k}_{h}y")
                for k in ("return", "excess", "early_exit")]
            for h in HORIZONS}
    values = out.to_numpy(dtype=object)
    price = out["price"].to_numpy(dtype=float)
    for asset, ix in pos.items():
        series = panel.series(int(asset))
        if series is None:
            continue
        sidx, sval = series.index.values, series.to_numpy()
        for h in HORIZONS:
            tg = target[h][ix]
            ok = tg <= np.datetime64(end)
            j = np.searchsorted(sidx, tg, side="right") - 1
            ok &= j >= 0
            j = np.clip(j, 0, None)
            exit_price, exit_date = sval[j], sidx[j]
            at_exit, at_target = bench_asof(exit_date), bench_asof(tg)
            total = exit_price / price[ix] * at_target / at_exit
            bench_total = at_target / start[ix]
            ret = total ** (1.0 / h) - 1.0
            exc = total ** (1.0 / h) - bench_total ** (1.0 / h)
            early = ((tg - exit_date) / np.timedelta64(1, "D")) > 30
            c_ret, c_exc, c_early = cols[h]
            values[ix, c_ret] = np.where(ok, ret, np.nan)
            values[ix, c_exc] = np.where(ok, exc, np.nan)
            values[ix, c_early] = np.where(ok, early.astype(float), np.nan)
    res = pd.DataFrame(values, columns=out.columns, index=out.index)
    for h in HORIZONS:
        for k in ("return", "excess", "early_exit"):
            res[f"{k}_{h}y"] = res[f"{k}_{h}y"].astype(float)
    return res


universe_rows, pick_rows, watch_rows = [], [], []
for n, when in enumerate(dates):
    xs = builder.at(when)
    scored = model_set.score(xs, int(when.year))
    inv = apply_filters(scored, FLOOR).copy()
    prices, kept = [], []
    for idx, pt in inv["permaticker"].items():
        q = source.asof(int(pt), when, 3)
        if q is not None:
            prices.append(q[0])
            kept.append(idx)
    # ranks are taken over the investable rows, before the quote screen
    # (the engine's order: combine, then keep the rows with a quote)
    for combo in combos:
        cols = [score_cols[c] for c in combo]
        inv["combined"] = combine_scores(inv, cols, "mean_rank")
        priced = inv.loc[kept].copy()
        priced["price"] = prices
        priced = priced.rename(columns={"permaticker": "asset"})
        priced["group"] = priced["sector"]
        priced = priced.sort_values(["combined", "asset"],
                                    ascending=[False, True], kind="mergesort")
        picks = capped_top_k(priced, 10, 2)
        for _, r in picks.iterrows():
            pick_rows.append({"combo": "+".join(combo), "date": when,
                              "asset": r["asset"], "ticker": r["ticker"],
                              "price": r["price"], "sector": r["sector"],
                              "log_marketcap_rank": r["log_marketcap_rank"]})
        if len(combo) == 3 and when.month == 1 and when.year >= 2019:
            n_inv = len(inv)
            w = inv[inv["ticker"].isin(WATCH)]
            for _, r in w.iterrows():
                row = {"date": when.date(), "ticker": r["ticker"],
                       "n_investable": n_inv,
                       "combined_pos": int((inv["combined"] > r["combined"]).sum()) + 1}
                for leg in legs:
                    sc = inv[score_cols[leg]]
                    row[f"pos_{leg}"] = int((sc > r[score_cols[leg]]).sum()) + 1
                for c in ("vol_36m_rank", "vol_12m_rank", "roc_greenblatt_rank",
                          "mom_12_2_rank", "log_marketcap_rank"):
                    row[c] = r[c]
                watch_rows.append(row)
    u = inv.loc[kept, ["permaticker", "sector", "log_marketcap_rank"]].rename(
        columns={"permaticker": "asset"})
    u["price"] = prices
    u["date"] = when
    for leg in legs:
        u[f"score_{leg}"] = inv.loc[kept, score_cols[leg]].to_numpy()
    universe_rows.append(u)
    if n % 24 == 0:
        print(when.date(), len(xs), len(inv), len(kept), flush=True)

universe = pd.concat(universe_rows, ignore_index=True)
picks = pd.DataFrame(pick_rows)
print("universe rows", len(universe), "pick rows", len(picks), flush=True)

uo = outcomes(universe)
po = outcomes(picks)
universe = pd.concat([universe, uo.drop(columns=["asset", "date", "price"])], axis=1)
picks = pd.concat([picks, po.drop(columns=["asset", "date", "price"])], axis=1)

# check the vectorised outcomes against the report's own function on
# the three-way picks
three = picks[picks["combo"] == "forest+mom+roc"]
fake = three.assign(side="buy", gross=100.0)[["asset", "date", "price", "gross", "side"]]
ref = buy_outcomes(fake, panel, END)
for h in HORIZONS:
    a = three[f"excess_{h}y"].to_numpy()
    b = ref[f"excess_{h}y"].to_numpy()
    both = ~np.isnan(a) & ~np.isnan(b)
    assert (np.isnan(a) == np.isnan(b)).all(), "NaN pattern differs"
    print(f"check {h}y: max abs diff vs buy_outcomes",
          float(np.abs(a[both] - b[both]).max()), "n", int(both.sum()))

universe.to_parquet(OUT / "diag_universe.parquet")
picks.to_parquet(OUT / "diag_picks.parquet")
pd.DataFrame(watch_rows).to_csv(OUT / "diag_watch.csv", index=False)
print("done")
