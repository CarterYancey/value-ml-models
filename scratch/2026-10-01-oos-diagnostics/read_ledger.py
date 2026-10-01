"""Read runs from the ledger shard by experiment-name prefix: fold-mean
metrics per run, pooled and by entry period (2005-12, 2013-20), with
the screen's lead over the all-rows mean of the same test rows.

    python scratch/2026-10-01-oos-diagnostics/read_ledger.py <prefix> [<prefix> ...]

Working material (lab branch). Every figure is the mean over test
years of the yearly statistic, as in the notes.
"""
import json
import sys

import pandas as pd

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_colwidth", 70)

LEDGER = "experiments/ledger/claude-value-ml-models.csv"
KEYS = {
    "base": "base_rate",
    "p@20": "precision_at_20",
    "prauc": "pr_auc",
    "scr_prec": "screen_precision",
    "scr_ex": "screen_mean_fwd_3y_excess_cagr",
    "all_ex": "all_mean_fwd_3y_excess_cagr",
    "scr_med": "screen_median_fwd_3y_excess_cagr",
    "scr_beat": "screen_mean_label_3y_beat_spy",
    "all_beat": "all_mean_label_3y_beat_spy",
    "scr_lost": "screen_mean_label_3y_cagr_lt_0p0",
    "all_lost": "all_mean_label_3y_cagr_lt_0p0",
    "scr_dd40": "screen_mean_label_3y_max_drawdown_from_entry_ge_0p4",
    "scr_win25": "screen_mean_label_3y_cagr_ge_0p25",
    "all_win25": "all_mean_label_3y_cagr_ge_0p25",
    "top_grp": "screen_top_group_share",
    "stocks": "screen_n_stocks",
}


def load(prefixes):
    df = pd.read_csv(LEDGER, low_memory=False)
    df = df[df["status"] == "completed"]
    df = df[df["experiment"].astype(str).apply(
        lambda e: any(e.startswith(p) for p in prefixes))]
    # the latest run of each experiment name
    last = df.groupby("experiment")["logged_utc"].transform("max")
    latest_run = df[df["logged_utc"] == last].groupby("experiment")["run_id"].last()
    df = df[df.apply(lambda r: latest_run[r["experiment"]] == r["run_id"], axis=1)]
    rows = []
    for _, r in df.iterrows():
        try:
            fold = int(float(r["fold"]))
        except (TypeError, ValueError):
            continue
        m = json.loads(r["metrics_json"])
        row = {"experiment": r["experiment"], "fold": fold}
        for short, key in KEYS.items():
            row[short] = m.get(key)
        rows.append(row)
    out = pd.DataFrame(rows)
    out["lead"] = out["scr_ex"] - out["all_ex"]
    out["lost_gap"] = out["scr_lost"] - out["all_lost"]
    return out


def shorten(name, prefixes):
    for p in sorted(prefixes, key=len, reverse=True):
        if name.startswith(p):
            name = name[len(p):]
            break
    return (name.replace("label_3y_cagr_ge_0p0_and_3y_max_drawdown_from_entry_lt_0p3", "C")
            .replace("label_3y_excess_cagr_gt_0p0_and_3y_max_drawdown_from_entry_lt_0p3", "CS")
            .replace("label_3y_beat_spy", "S")
            .replace("fwd_3y_excess_cagr", "reg")
            .strip("_"))


def main():
    prefixes = sys.argv[1:]
    df = load(prefixes)
    if df.empty:
        print("no rows")
        return
    df["run"] = df["experiment"].map(lambda e: shorten(e, prefixes))
    periods = {"all": (2005, 2020), "05-12": (2005, 2012), "13-20": (2013, 2020)}
    cols = ["base", "p@20", "prauc", "scr_prec", "scr_ex", "all_ex", "lead",
            "scr_beat", "all_beat", "scr_lost", "all_lost", "scr_win25",
            "all_win25", "top_grp", "stocks"]
    print(f"folds per run: {df.groupby('run')['fold'].count().unique().tolist()}")
    for name, (a, b) in periods.items():
        sub = df[(df["fold"] >= a) & (df["fold"] <= b)]
        t = sub.groupby("run")[cols].mean()
        print(f"\n=== {name}")
        print(t.round(3).to_string())


if __name__ == "__main__":
    main()
