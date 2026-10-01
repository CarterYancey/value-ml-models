"""Decision 35: a stand-in for the candidate on 1999-2026, from columns
only (no fitted model exists before 2005): lowest 12-month volatility,
12-month momentum and return on capital by mean rank, the candidate's
selection rule otherwise, every pick read against SPY and against the
same month's candidates of the same size, as diag_oos.py does.

    python scratch/2026-10-01-oos-diagnostics/diag_standin.py <out dir>

Reads feature columns and the price panel. No label, no split tag, no
fit, no portfolio, nothing logged.
"""
from __future__ import annotations

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
from portfolio.report import position_outcomes  # noqa: E402
from portfolio.strategy import capped_top_k  # noqa: E402

OUT = Path(sys.argv[1])
FLOOR = [FilterSpec("dollar_volume_3m_rank", ">=", 0.2)]
START, END = date(1999, 1, 1), date(2026, 8, 21)
# leg -> (column, higher is better)
LEGS = {
    "lowvol": ("vol_12m_rank", False),
    "mom": ("mom_12_2_rank", True),
    "roc": ("roc_greenblatt_rank", True),
}
COMBOS = [("lowvol",), ("lowvol", "roc"), ("lowvol", "mom"),
          ("lowvol", "mom", "roc")]

dataset = Dataset(Path("data/datasets/dataset_v1.4"))
panel = PricePanel(Path("data/datasets/prices_v1.0"))
builder = CrossSectionBuilder(dataset, 200)
source = stock_price_source(panel)
dates = panel.month_first_trading_days(START, END)

universe_rows, pick_rows = [], []
for n, when in enumerate(dates):
    xs = builder.at(when)
    inv = apply_filters(xs, FLOOR).copy()
    if inv.empty:
        continue
    for leg, (col, high) in LEGS.items():
        raw = inv[col].to_numpy(dtype=float)
        score = raw if high else -raw
        # a NULL rank sorts last, as the rank_factor model does
        inv[f"score_{leg}"] = np.where(np.isnan(score), -np.inf, score)
    prices, kept = [], []
    for idx, pt in inv["permaticker"].items():
        q = source.asof(int(pt), when, 3)
        if q is not None:
            prices.append(q[0])
            kept.append(idx)
    for combo in COMBOS:
        ranks = pd.DataFrame({
            leg: inv[f"score_{leg}"].rank(ascending=False, method="min")
            for leg in combo
        })
        inv["combined"] = -ranks.mean(axis=1)
        priced = inv.loc[kept].copy()
        priced["price"] = prices
        priced = priced.rename(columns={"permaticker": "asset"})
        priced["group"] = priced["sector"]
        priced = priced.sort_values(["combined", "asset"],
                                    ascending=[False, True], kind="mergesort")
        picks = capped_top_k(priced, 10, 2)
        out = picks[["asset", "ticker", "price", "sector",
                     "log_marketcap_rank"]].copy()
        out["combo"] = "+".join(combo)
        out["date"] = when
        pick_rows.append(out)
    u = inv.loc[kept, ["permaticker", "log_marketcap_rank"]].rename(
        columns={"permaticker": "asset"})
    u["price"] = prices
    u["date"] = when
    universe_rows.append(u)
    if n % 24 == 0:
        print(when.date(), len(xs), len(inv), len(kept), flush=True)

universe = pd.concat(universe_rows, ignore_index=True)
picks = pd.concat(pick_rows, ignore_index=True)
print("universe rows", len(universe), "pick rows", len(picks), flush=True)
universe = pd.concat([universe, position_outcomes(universe, panel, END)], axis=1)
picks = pd.concat([picks, position_outcomes(picks, panel, END)], axis=1)
universe.to_parquet(OUT / "standin_universe.parquet")
picks.to_parquet(OUT / "standin_picks.parquet")

# ------------------------------------------------------------- tables
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
for f in (universe, picks):
    f["sbin"] = np.minimum(
        np.floor(f["log_marketcap_rank"].fillna(-0.05) * 20), 19).astype(int)
    f["year"] = f["date"].dt.year


def period(y):
    if y <= 1999:
        return "a 1999"
    if y <= 2002:
        return "b 2000-02"
    if y <= 2004:
        return "c 2003-04"
    if y <= 2012:
        return "d 2005-12"
    if y <= 2020:
        return "e 2013-20"
    return "f 2021-26"


for f in (universe, picks):
    f["period"] = f["year"].map(period)

for h in (3, 1):
    exc, ret = f"excess_{h}y", f"return_{h}y"
    seen_u = universe[universe[exc].notna()]
    ref = seen_u.assign(lost=(seen_u[ret] < 0).astype(float)).groupby(
        ["date", "sbin"]).agg(peer_ex=(exc, "mean"), peer_lost=("lost", "mean")).reset_index()
    m = picks[picks[exc].notna()].merge(ref, on=["date", "sbin"], how="left")
    m["lead"] = m[exc] - m["peer_ex"]
    m["lost"] = (m[ret] < 0).astype(float)
    m["beat"] = (m[exc] > 0).astype(float)
    for key in ("period", "year"):
        t = m.groupby(["combo", key]).agg(
            n=("lead", "size"), vs_spy=(exc, "mean"), peers=("peer_ex", "mean"),
            vs_peers=("lead", "mean"), beat_spy=("beat", "mean"),
            lost=("lost", "mean"), peers_lost=("peer_lost", "mean"),
            cap_rank=("log_marketcap_rank", "mean"))
        uu = seen_u.assign(lost=(seen_u[ret] < 0).astype(float)).groupby(key).agg(
            all_ex=(exc, "mean"), all_lost=("lost", "mean"))
        print(f"\n=== {h}y by {key}: the stand-in's picks")
        if key == "year":
            t = t.loc[["lowvol+mom+roc"]]
            t = t[t.index.get_level_values(1) <= 2006]
        print(t.round(3).to_string())
        if key == "period" or h == 1:
            print(uu.round(3).head(12).to_string())
print("done")
