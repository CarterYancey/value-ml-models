#!/usr/bin/env python
"""Compare two rankings written by ``vml-predict`` over the same inference
dataset: which picks and top rows they share, how far their ranks move,
and which model leg moved them.

The two CSVs must come from the same inference dataset with the same
``--filter`` and selection flags, so that both rankings are over the
same rows; the script refuses otherwise. The usual use is one ranking
from the full deployment refit and one from a refit with a training
cutoff (``vml-train-deploy --train-end``, decision 60). A rank factor
leg fits nothing, so its ranks are identical in both files and the
script reports it as unchanged.

Nothing here is an evaluation: both rankings come from deployment fits
that have no test rows. The report says where two rankings differ, not
which one is better.

    python scripts/compare_predictions.py A.csv B.csv --label-a full --label-b pre2021
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ID_COLUMNS = ("permaticker", "ticker", "sector")


def _read(path: Path) -> tuple[pd.DataFrame, dict]:
    frame = pd.read_csv(path)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    if "permaticker" not in frame.columns or "mean_rank" not in frame.columns:
        raise SystemExit(
            f"{path}: not a combined vml-predict ranking (needs permaticker "
            "and mean_rank columns)"
        )
    frame = frame.reset_index(drop=True)
    frame["position"] = frame.index + 1
    return frame, meta


def _legs(frame: pd.DataFrame) -> list[str]:
    return [c[len("rank_"):] for c in frame.columns if c.startswith("rank_")]


def _check_same_rows(a: pd.DataFrame, b: pd.DataFrame, ma: dict, mb: dict) -> None:
    if ma.get("inference_source") and mb.get("inference_source"):
        if ma["inference_source"] != mb["inference_source"]:
            raise SystemExit(
                "the two rankings score different inference datasets: "
                f"{ma['inference_source']} and {mb['inference_source']}"
            )
    if ma.get("filters") != mb.get("filters"):
        raise SystemExit(
            f"the two rankings used different filters: {ma.get('filters')} "
            f"and {mb.get('filters')}"
        )
    if set(a["permaticker"]) != set(b["permaticker"]):
        raise SystemExit(
            "the two rankings cover different rows "
            f"({len(a)} and {len(b)}); rerun both with the same flags"
        )


def _overlap(a: pd.DataFrame, b: pd.DataFrame, column: str, n: int) -> int:
    top_a = set(a.nsmallest(n, column, keep="first")["permaticker"])
    top_b = set(b.nsmallest(n, column, keep="first")["permaticker"])
    return len(top_a & top_b)


def _md_table(frame: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in frame.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                cells.append("" if pd.isna(v) else floatfmt.format(v))
            else:
                cells.append("" if pd.isna(v) else str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _training_lines(meta: dict, label: str) -> list[str]:
    out = []
    for m in meta.get("models", []):
        name = m.get("column_suffix", "?")
        window = (
            f"labeled rows before {m['train_end']}"
            if m.get("train_end")
            else "all labeled rows"
        )
        last = m.get("last_snapshot_date", "")
        out.append(
            f"| {label} | {name} | {m.get('model', '')} | {window} | {last} | "
            f"{m.get('bundle_run_id', '')} |"
        )
    return out


def compare(path_a: Path, path_b: Path, label_a: str, label_b: str, top: int,
            movers: int) -> str:
    a, ma = _read(path_a)
    b, mb = _read(path_b)
    _check_same_rows(a, b, ma, mb)
    legs = _legs(a)
    if legs != _legs(b):
        raise SystemExit(f"the rankings have different legs: {legs} and {_legs(b)}")

    ids = [c for c in ID_COLUMNS if c in a.columns]
    joined = a[ids + ["position", "mean_rank"] + [f"rank_{l}" for l in legs]
               + [f"score_{l}" for l in legs] + (["pick"] if "pick" in a else [])]
    joined = joined.merge(
        b[["permaticker", "position", "mean_rank"] + [f"rank_{l}" for l in legs]
          + [f"score_{l}" for l in legs] + (["pick"] if "pick" in b else [])],
        on="permaticker", suffixes=(f"_{label_a}", f"_{label_b}"),
    )
    n = len(joined)
    pa, pb = f"position_{label_a}", f"position_{label_b}"

    unchanged = [l for l in legs
                 if (joined[f"rank_{l}_{label_a}"] == joined[f"rank_{l}_{label_b}"]).all()]
    changed = [l for l in legs if l not in unchanged]

    lines = [f"# {label_a} against {label_b}", ""]
    lines.append(
        f"Both rankings cover the same {n} rows of "
        f"`{ma.get('inference_source', path_a.stem)}`"
        + (f" after the filters {ma['filters']}." if ma.get("filters") else ".")
    )
    lines.append("")
    lines.append("| ranking | leg | model | fit on | last snapshot fit | bundle run |")
    lines.append("|---|---|---|---|---|---|")
    lines += _training_lines(ma, label_a) + _training_lines(mb, label_b)
    lines.append("")
    if unchanged:
        lines.append(
            "Legs with identical ranks in both files: "
            + ", ".join(f"`{l}`" for l in unchanged)
            + ". Legs that differ: "
            + (", ".join(f"`{l}`" for l in changed) if changed else "none")
            + "."
        )
        lines.append("")

    # --- picks
    if "pick" in a.columns and "pick" in b.columns:
        for label, this, other, pos_this, pos_other, pick_this, pick_other in (
            (label_a, a, b, pa, pb, f"pick_{label_a}", f"pick_{label_b}"),
            (label_b, b, a, pb, pa, f"pick_{label_b}", f"pick_{label_a}"),
        ):
            picks = joined[joined[pick_this].notna()].sort_values(pick_this)
            table = pd.DataFrame({
                "pick": picks[pick_this].astype(int),
                **({"ticker": picks["ticker"]} if "ticker" in picks else {}),
                **({"sector": picks["sector"]} if "sector" in picks else {}),
                f"position under {label}": picks[pos_this].astype(int),
                f"position under {label_a if label == label_b else label_b}":
                    picks[pos_other].astype(int),
                f"pick under {label_a if label == label_b else label_b}":
                    picks[pick_other].map(lambda v: "" if pd.isna(v) else str(int(v))),
            })
            for l in changed:
                table[f"{l} rank, {label}"] = picks[f"rank_{l}_{label}"].astype(int)
                table[f"{l} rank, {label_a if label == label_b else label_b}"] = (
                    picks[f"rank_{l}_{label_a if label == label_b else label_b}"].astype(int)
                )
                table[f"{l} score, {label}"] = picks[f"score_{l}_{label}"]
                table[f"{l} score, {label_a if label == label_b else label_b}"] = (
                    picks[f"score_{l}_{label_a if label == label_b else label_b}"]
                )
            lines.append(f"## The picks under {label}")
            lines.append("")
            lines.append(_md_table(table))
            lines.append("")
        shared = set(a.loc[a["pick"].notna(), "permaticker"]) & set(
            b.loc[b["pick"].notna(), "permaticker"])
        n_a = int(a["pick"].notna().sum())
        lines.append(f"The two lists share {len(shared)} of {n_a} picks.")
        lines.append("")

    # --- overlap and rank agreement
    lines.append("## How far the rankings agree")
    lines.append("")
    rows = []
    for k in (10, 20, 50, 100, 200):
        if k > n:
            break
        row = {"top": k, "shared by mean rank": _overlap(a, b, "mean_rank", k)}
        for l in changed:
            row[f"shared by {l} rank"] = _overlap(a, b, f"rank_{l}", k)
        rows.append(row)
    lines.append(_md_table(pd.DataFrame(rows)))
    lines.append("")
    corr_rows = [{"column": "mean_rank",
                  "Spearman correlation": joined[f"mean_rank_{label_a}"].corr(
                      joined[f"mean_rank_{label_b}"], method="spearman")}]
    for l in changed:
        corr_rows.append({
            "column": f"rank_{l}",
            "Spearman correlation": joined[f"rank_{l}_{label_a}"].corr(
                joined[f"rank_{l}_{label_b}"], method="spearman"),
        })
    lines.append(_md_table(pd.DataFrame(corr_rows)))
    lines.append("")

    # --- where the changed leg moved most, among the rows near the top
    for l in changed:
        near_top = joined[(joined[pa] <= top) | (joined[pb] <= top)].copy()
        near_top["move"] = (near_top[f"rank_{l}_{label_b}"] - near_top[f"rank_{l}_{label_a}"])
        near_top = near_top.reindex(near_top["move"].abs().sort_values(ascending=False).index)
        table = pd.DataFrame({
            **({"ticker": near_top["ticker"]} if "ticker" in near_top else {}),
            **({"sector": near_top["sector"]} if "sector" in near_top else {}),
            f"position {label_a}": near_top[pa].astype(int),
            f"position {label_b}": near_top[pb].astype(int),
            f"{l} rank {label_a}": near_top[f"rank_{l}_{label_a}"].astype(int),
            f"{l} rank {label_b}": near_top[f"rank_{l}_{label_b}"].astype(int),
            f"{l} score {label_a}": near_top[f"score_{l}_{label_a}"],
            f"{l} score {label_b}": near_top[f"score_{l}_{label_b}"],
        }).head(movers)
        lines.append(
            f"## Largest moves of `{l}` among the top {top} of either ranking"
        )
        lines.append("")
        lines.append(
            f"A positive move means `{label_b}` ranks the stock lower "
            f"(a larger rank number) than `{label_a}` does."
        )
        lines.append("")
        table.insert(len(table.columns), "move", near_top["move"].head(movers).astype(int))
        lines.append(_md_table(table))
        lines.append("")

    # --- sector mix of the top rows
    if "sector" in joined.columns:
        mix = pd.DataFrame({
            label_a: joined[joined[pa] <= top]["sector"].value_counts(),
            label_b: joined[joined[pb] <= top]["sector"].value_counts(),
        }).fillna(0).astype(int).sort_values(label_a, ascending=False)
        mix.index.name = "sector"
        lines.append(f"## Sectors of the top {top} by mean rank")
        lines.append("")
        lines.append(_md_table(mix.reset_index()))
        lines.append("")

    lines.append(
        "Both rankings are deployment scores with no test rows. This report "
        "says where they differ, and nothing about which is better."
    )
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("ranking_a", type=Path)
    parser.add_argument("ranking_b", type=Path)
    parser.add_argument("--label-a", default="A")
    parser.add_argument("--label-b", default="B")
    parser.add_argument("--top", type=int, default=50,
                        help="rows near the top to inspect (default 50)")
    parser.add_argument("--movers", type=int, default=15,
                        help="how many of the largest moves to list (default 15)")
    parser.add_argument("--out", type=Path, default=None,
                        help="write the markdown report here instead of stdout")
    args = parser.parse_args(argv)
    report = compare(args.ranking_a, args.ranking_b, args.label_a, args.label_b,
                     args.top, args.movers)
    if args.out:
        args.out.write_text(report + "\n")
        print(f"wrote {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
