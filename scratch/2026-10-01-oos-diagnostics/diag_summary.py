import sys
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
OUT = Path(sys.argv[1])
u = pd.read_parquet(OUT / "diag_universe.parquet")
p = pd.read_parquet(OUT / "diag_picks.parquet")
u["year"] = u["date"].dt.year
p["year"] = p["date"].dt.year


def period(y):
    if y <= 2012:
        return "2005-12"
    if y <= 2020:
        return "2013-20"
    return "2021-26"


u["period"] = u["year"].map(period)
p["period"] = p["year"].map(period)


def stats(frame, h):
    seen = frame[frame[f"excess_{h}y"].notna()]
    if seen.empty:
        return pd.Series({"n": 0, "mean_ex": np.nan, "med_ex": np.nan,
                          "beat": np.nan, "lost": np.nan, "mean_ret": np.nan})
    return pd.Series({
        "n": len(seen),
        "mean_ex": seen[f"excess_{h}y"].mean(),
        "med_ex": seen[f"excess_{h}y"].median(),
        "beat": (seen[f"excess_{h}y"] > 0).mean(),
        "lost": (seen[f"return_{h}y"] < 0).mean(),
        "mean_ret": seen[f"return_{h}y"].mean(),
    })


def yearly_mean(frame, h, key="year"):
    """mean over months of the monthly statistic would weight months
    equally; here every row counts once, as in the report."""
    return frame.groupby(key).apply(lambda g: stats(g, h))


for h in (3, 1):
    print(f"\n=== UNIVERSE (all investable candidates), {h}y, by year")
    uy = yearly_mean(u, h)
    print(uy.round(3).to_string())
    print(f"\n=== UNIVERSE {h}y by period")
    print(yearly_mean(u, h, "period").round(3).to_string())

combos = ["forest", "mom", "roc", "forest+mom", "forest+roc", "mom+roc",
          "forest+mom+roc"]
for h in (3, 1):
    uy = yearly_mean(u, h)
    rows = {}
    for c in combos:
        py = yearly_mean(p[p["combo"] == c], h)
        rows[(c, "ex")] = py["mean_ex"]
        rows[(c, "vs_u")] = py["mean_ex"] - uy["mean_ex"]
        rows[(c, "lost")] = py["lost"]
    t = pd.DataFrame(rows)
    t[("universe", "ex")] = uy["mean_ex"]
    t[("universe", "lost")] = uy["lost"]
    print(f"\n=== PICKS by year, {h}y: mean excess over SPY, minus the universe's, share that lost money")
    print((t * 100).round(1).to_string())
    up = yearly_mean(u, h, "period")
    rows = {}
    for c in combos:
        pp = yearly_mean(p[p["combo"] == c], h, "period")
        rows[c] = pd.concat([
            pp["mean_ex"].rename("ex"), (pp["mean_ex"] - up["mean_ex"]).rename("vs_u"),
            pp["med_ex"].rename("med"), pp["beat"].rename("beat"),
            pp["lost"].rename("lost"), (pp["lost"] - up["lost"]).rename("lost_vs_u"),
            pp["n"].rename("n")], axis=1)
    print(f"\n=== PICKS by period, {h}y")
    for c in combos:
        print(c)
        print((rows[c] * [100, 100, 100, 100, 100, 100, 1]).round(1).to_string())
    print("universe")
    print((up[["mean_ex", "med_ex", "beat", "lost"]] * 100).round(1).to_string())

# size: universe by market-cap rank bucket
u["size"] = pd.cut(u["log_marketcap_rank"], [0, 0.5, 0.8, 0.95, 1.0],
                   labels=["<50", "50-80", "80-95", "top5"], include_lowest=True)
for h in (3, 1):
    t = u[u[f"excess_{h}y"].notna()].groupby(["period", "size"], observed=True)[
        f"excess_{h}y"].agg(["mean", "median", "size"])
    print(f"\n=== UNIVERSE by size bucket (log_marketcap_rank), {h}y excess")
    print(t.round(3).to_string())
print("\n=== three-way picks: mean log_marketcap_rank by period")
print(p[p.combo == "forest+mom+roc"].groupby("period")["log_marketcap_rank"].describe().round(3).to_string())
p3 = p[p.combo == "forest+mom+roc"].copy()
p3["size"] = pd.cut(p3["log_marketcap_rank"], [0, 0.5, 0.8, 0.95, 1.0],
                    labels=["<50", "50-80", "80-95", "top5"], include_lowest=True)
print(p3.groupby(["period", "size"], observed=True).agg(
    n=("asset", "size"), ex3=("excess_3y", "mean"), ex1=("excess_1y", "mean")).round(3).to_string())

# universe by forest score quintile within month: is the forest still ordering returns and losers?
u["fq"] = u.groupby("date")["score_forest"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
for h in (3, 1):
    t = u[u[f"excess_{h}y"].notna()].groupby(["period", "fq"]).apply(
        lambda g: pd.Series({"ex": g[f"excess_{h}y"].mean(),
                             "lost": (g[f"return_{h}y"] < 0).mean()}))
    print(f"\n=== UNIVERSE by forest-score decile within month (9 = safest), {h}y: mean excess / lost")
    print(t["ex"].unstack(0).round(3).join(t["lost"].unstack(0).round(3), rsuffix="_lost").to_string())
for leg in ("mom", "roc"):
    s = u[f"score_{leg}"].replace(-np.inf, np.nan)
    u[f"q_{leg}"] = s.groupby(u["date"]).transform(
        lambda x: pd.qcut(x.rank(method="first"), 10, labels=False))
    for h in (3, 1):
        t = u[u[f"excess_{h}y"].notna()].groupby(["period", f"q_{leg}"]).apply(
            lambda g: pd.Series({"ex": g[f"excess_{h}y"].mean(),
                                 "lost": (g[f"return_{h}y"] < 0).mean()}))
        print(f"\n=== UNIVERSE by {leg} decile within month (9 = highest), {h}y: mean excess / lost")
        print(t["ex"].unstack(0).round(3).join(t["lost"].unstack(0).round(3), rsuffix="_lost").to_string())

w = pd.read_csv(OUT / "diag_watch.csv")
print("\n=== where the index's largest members ranked each January (position of n investable; 1 = best)")
for d, g in w.groupby("date"):
    if d >= "2021":
        print(d, "n =", int(g["n_investable"].iloc[0]))
        print(g.drop(columns=["date", "n_investable"]).sort_values("combined_pos").round(2).to_string(index=False))
