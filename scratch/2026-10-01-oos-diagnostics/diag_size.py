import sys
from pathlib import Path
import numpy as np, pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
OUT = Path(sys.argv[1])
u = pd.read_parquet(OUT / "diag_universe.parquet")
p = pd.read_parquet(OUT / "diag_picks.parquet")
def period(y):
    return "2005-12" if y <= 2012 else ("2013-20" if y <= 2020 else "2021-26")
for f in (u, p):
    f["period"] = f["date"].dt.year.map(period)
    f["sbin"] = np.minimum(np.floor(f["log_marketcap_rank"].fillna(-0.05) * 20), 19).astype(int)
# size-matched: month x size bin (20 bins) universe mean
for h in (3, 1):
    ref = u[u[f"excess_{h}y"].notna()].groupby(["date", "sbin"]).agg(
        ref_ex=(f"excess_{h}y", "mean"), ref_lost=(f"return_{h}y", lambda r: (r < 0).mean()),
        ref_n=(f"excess_{h}y", "size")).reset_index()
    m = p.merge(ref, on=["date", "sbin"], how="left")
    m = m[m[f"excess_{h}y"].notna()]
    m["adj"] = m[f"excess_{h}y"] - m["ref_ex"]
    m["lost"] = (m[f"return_{h}y"] < 0).astype(float)
    t = m.groupby(["combo", "period"]).agg(ex=(f"excess_{h}y", "mean"), size_matched=("adj", "mean"),
        ref=("ref_ex", "mean"), lost=("lost", "mean"), ref_lost=("ref_lost", "mean"), n=("adj", "size"),
        cap_rank=("log_marketcap_rank", "mean"))
    print(f"\n=== PICKS, {h}y: mean excess over SPY, the same-month same-size (20 bins) universe mean, and the difference")
    print((t[["ex", "ref", "size_matched", "lost", "ref_lost"]] * 100).round(1).join(t[["n", "cap_rank"]].round(3)).to_string())
    ty = m[m.combo.isin(["forest", "forest+roc", "forest+mom+roc"])].groupby(["combo", m["date"].dt.year])["adj"].mean().unstack(0)
    print(f"\n size-matched excess by year, {h}y"); print((ty * 100).round(1).to_string())

# within large caps: deciles of each leg within month
big = u[u["log_marketcap_rank"] >= 0.8].copy()
for leg in ("forest", "roc", "mom"):
    s = big[f"score_{leg}"].replace(-np.inf, np.nan)
    big[f"q_{leg}"] = s.groupby(big["date"]).transform(lambda x: pd.qcut(x.rank(method="first"), 5, labels=False))
    for h in (3, 1):
        g = big[big[f"excess_{h}y"].notna()]
        t = g.groupby(["period", f"q_{leg}"]).apply(lambda d: pd.Series({
            "ex": d[f"excess_{h}y"].mean(), "lost": (d[f"return_{h}y"] < 0).mean(), "med": d[f"excess_{h}y"].median()}))
        print(f"\n=== LARGE CAPS (cap rank >= 0.8) by {leg} quintile within month (4 = best), {h}y: mean excess, median, lost")
        print((t["ex"].unstack(0) * 100).round(1).join((t["med"].unstack(0) * 100).round(1), rsuffix="_med").join((t["lost"].unstack(0) * 100).round(1), rsuffix="_lost").to_string())
print("\nlarge caps n per month:", big.groupby("date").size().describe().round(0).to_dict())
# all universe by size decile x period for reference: beat rate
for h in (3,):
    g = u[u[f"excess_{h}y"].notna()].copy()
    g["sdec"] = np.minimum((g["log_marketcap_rank"] * 10).astype(int), 9)
    t = g.groupby(["period", "sdec"]).apply(lambda d: pd.Series({"ex": d[f"excess_{h}y"].mean(), "lost": (d[f"return_{h}y"] < 0).mean(), "beat": (d[f"excess_{h}y"] > 0).mean()}))
    print("\n=== UNIVERSE by size decile, 3y: mean excess / lost / beat SPY")
    print((t["ex"].unstack(0) * 100).round(1).join((t["lost"].unstack(0) * 100).round(1), rsuffix="_lost").join((t["beat"].unstack(0) * 100).round(1), rsuffix="_beat").to_string())
