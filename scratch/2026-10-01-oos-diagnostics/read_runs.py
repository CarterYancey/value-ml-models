"""Like read_ledger.py but with a compact column set and a filter on
the run name; prints the two halves of 2005-2020 side by side."""
import sys, json
import pandas as pd
sys.path.insert(0, "scratch/2026-10-01-oos-diagnostics")
from read_ledger import load, shorten
pd.set_option("display.width", 260); pd.set_option("display.max_columns", 60); pd.set_option("display.max_colwidth", 60)
prefixes = [a for a in sys.argv[1:] if not a.startswith("--")]
must = [a[2:] for a in sys.argv[1:] if a.startswith("--")]
df = load(prefixes)
df["run"] = df["experiment"].map(lambda e: shorten(e, prefixes))
for m in must:
    df = df[df["run"].str.contains(m)]
num = ["base", "p@20", "prauc", "scr_prec", "peer_prec", "scr_ex", "all_ex", "peer_ex", "lead", "lead_peers", "scr_lost", "peer_lost", "all_lost", "scr_win25", "top_grp"]
for c in num: df[c] = pd.to_numeric(df[c], errors="coerce")
out = {}
for name, (a, b) in {"05-12": (2005, 2012), "13-20": (2013, 2020)}.items():
    sub = df[(df.fold >= a) & (df.fold <= b)]
    out[name] = sub.groupby("run")[num].mean()
t = out["05-12"].join(out["13-20"], lsuffix=" A", rsuffix=" B")
cols = []
for c in ["base", "p@20", "prauc", "scr_prec", "peer_prec", "scr_ex", "peer_ex", "lead_peers", "lead", "scr_lost", "peer_lost", "scr_win25"]:
    cols += [c + " A", c + " B"]
print("A = entries of 2005-12, B = 2013-20")
print(t[cols].round(3).to_string())
