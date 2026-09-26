"""The experiment catalog and promotion flow: headlines are shown against
the best baseline in the same cell, listings group by cell, notes travel
with configs, and promoting stages report + config + provenance."""

import json

import pytest

from harness import catalog, promote
from harness.config import ExperimentConfig
from harness.runner import run_experiment

BASELINE = """
name = "baseline_b2m_rank_3y_beat_spy"
dataset_version = "dataset_v0.0-test"
scheme = "walkforward"
horizon_years = 3
label = "label_3y_beat_spy"
feature_groups = ["ranks"]
seed = 7
top_k = [5]

[model]
name = "rank_factor"
rank_column = "book_to_market_rank"
"""

TREE = """
name = "tree_d2_3y_beat_spy"
dataset_version = "dataset_v0.0-test"
scheme = "walkforward"
horizon_years = 3
label = "label_3y_beat_spy"
feature_groups = ["ranks"]
seed = 7
top_k = [5]

[model]
name = "decision_tree"
max_depth = 2
"""

HOLDOUT = TREE.replace('scheme = "walkforward"', 'scheme = "holdout"').replace(
    'name = "tree_d2_3y_beat_spy"', 'name = "tree_d2_3y_beat_spy_holdout"'
)

PORTFOLIO = """
name = "some_portfolio"
dataset_version = "dataset_v0.0-test"
prices_version = "prices_v0.0-test"
bundles = ["a", "b"]
"""


@pytest.fixture(scope="module")
def workspace(data_root, tmp_path_factory):
    """A tmp experiments dir + ledger + reports with one baseline and one
    tree run in the same cell."""
    root = tmp_path_factory.mktemp("catalog")
    experiments = root / "experiments"
    (experiments / "sub").mkdir(parents=True)
    (experiments / "baseline_b2m.toml").write_text(BASELINE)
    (experiments / "tree.toml").write_text(TREE)
    (experiments / "sub" / "tree_holdout.toml").write_text(HOLDOUT)
    (experiments / "sub" / "portfolio.toml").write_text(PORTFOLIO)
    results = root / "results.csv"
    reports = root / "reports"
    for name in ("baseline_b2m.toml", "tree.toml"):
        path = experiments / name
        run_experiment(
            ExperimentConfig.from_file(path),
            data_root=data_root,
            results_path=results,
            reports_dir=reports,
            config_path=str(path),
        )
    final_evals = root / "final_evals.csv"
    final_evals.write_text(
        "phase,dataset_version,horizon_years,label,experiment,config_hash,"
        "run_id,git_sha,logged_utc,status\n"
        "phase1,dataset_v0.0-test,3,label_3y_beat_spy,tree_d2_3y_beat_spy,"
        "x,y,z,2026-01-01T00:00:00+00:00,completed\n"
    )
    return {
        "root": root,
        "experiments": experiments,
        "results": results,
        "reports": reports,
        "final_evals": final_evals,
    }


def _common(ws):
    return [
        "--experiments-dir", str(ws["experiments"]),
        "--results", str(ws["results"]),
        "--final-evals", str(ws["final_evals"]),
        "--promoted", str(ws["reports"] / "promoted"),
    ]


def test_list_shows_headline_against_best_baseline(workspace, capsys):
    assert catalog.main([*_common(workspace), "list"]) == 0
    out = capsys.readouterr().out
    # grouped by cell, with the cell in a header line, not a column
    assert "== label_3y_beat_spy  ·  3y  ·  walkforward  ·  dataset_v0.0-test" in out
    tree_line = next(ln for ln in out.splitlines() if "tree.toml" in ln)
    assert "p@5=" in tree_line
    assert "b2m_rank" in tree_line  # the best baseline, by short name
    assert "+0." in tree_line or "-0." in tree_line  # a signed lift
    assert "phase1 ✓" in tree_line  # the final-eval record, by name
    base_line = next(ln for ln in out.splitlines() if "baseline_b2m.toml" in ln)
    assert "+0.000" in base_line  # a baseline's lift over itself
    # restricted schemes are flagged; the holdout config never ran
    assert "holdout ⚠ final eval only" in out
    # portfolio configs render as their own kind instead of an error
    assert "[portfolio] vml-backtest" in out and "2 bundles" in out
    assert "lacks required" not in out


def test_list_orders_by_lift_within_a_cell(workspace, capsys):
    catalog.main([*_common(workspace), "list"])
    lines = [ln for ln in capsys.readouterr().out.splitlines()
             if ln.startswith(str(workspace["experiments"]))]
    scored = [ln for ln in lines if "p@5=" in ln]
    lifts = []
    for ln in scored:
        tok = next(t for t in ln.split() if t.startswith(("+0.", "-0.", "+1.")))
        lifts.append(float(tok))
    assert lifts == sorted(lifts, reverse=True)
    # the holdout config is a different cell (scheme differs), so it is
    # its own group; non-experiment rows come last
    order = [next(k for k in ("baseline_b2m", "tree.toml", "tree_holdout",
                              "portfolio") if k in ln) for ln in lines]
    assert order.index("portfolio") == len(order) - 1
    assert scored  # both runs in the shared cell were scored


def test_list_flat_sort_and_filters(workspace, capsys):
    catalog.main([*_common(workspace), "list", "--sort", "path"])
    out = capsys.readouterr().out
    assert "==" not in out
    tree_line = next(ln for ln in out.splitlines() if "tree.toml" in ln)
    assert "label_3y_beat_spy (walkforward)" in tree_line  # cell column filled
    catalog.main([*_common(workspace), "list", "--model", "rank_factor"])
    out = capsys.readouterr().out
    assert "baseline_b2m.toml" in out and "tree.toml" not in out


def test_show_prints_baselines_and_final_evals(workspace, capsys):
    assert catalog.main(
        [*_common(workspace), "show", str(workspace["experiments"] / "tree.toml")]
    ) == 0
    out = capsys.readouterr().out
    assert "baselines in this cell" in out
    assert "baseline_b2m_rank_3y_beat_spy" in out
    assert "final evals (sealed holdout): phase1 ✓" in out


def test_show_by_experiment_name(workspace, capsys):
    assert catalog.main([*_common(workspace), "show", "tree_d2_3y_beat_spy"]) == 0
    assert "tree.toml" in capsys.readouterr().out


def test_set_note_keeps_the_config_hash(tmp_path):
    path = tmp_path / "c.toml"
    path.write_text(TREE)
    before = ExperimentConfig.from_file(path).config_hash
    promote.set_note(path, 'depth 2 "beats" b2m\nby a bit')
    text = path.read_text()
    assert text.splitlines()[1].startswith("name = ")
    assert text.splitlines()[2] == 'note = "depth 2 \\"beats\\" b2m\\nby a bit"'
    assert ExperimentConfig.from_file(path).config_hash == before
    # replacing an existing note
    promote.set_note(path, "second thoughts")
    assert path.read_text().count("note = ") == 1
    assert "second thoughts" in path.read_text()
    # a config without a name gets the note before the first table
    path.write_text(TREE.replace('name = "tree_d2_3y_beat_spy"\n', ""))
    promote.set_note(path, "anonymous")
    lines = path.read_text().splitlines()
    assert lines.index('note = "anonymous"') < lines.index("[model]")
    ExperimentConfig.from_file(path)  # still parses


def test_note_shows_in_listing(workspace, capsys):
    promote.set_note(workspace["experiments"] / "tree.toml",
                     "shallow tree, first real lift over b2m")
    catalog.main([*_common(workspace), "list", "--grep", "shallow tree"])
    out = capsys.readouterr().out
    assert "tree.toml" in out and "shallow tree, first real lift" in out
    assert "baseline_b2m.toml" not in out


def test_promote_copies_config_and_writes_index(workspace):
    ws = workspace
    dest = promote.promote(
        "tree_d2_3y_beat_spy",
        reports_dir=ws["reports"],
        note="promoted with a note",
        experiments_dir=ws["experiments"],
        results_path=ws["results"],
        git=False,
    )
    assert dest == ws["reports"] / "promoted" / "tree_d2_3y_beat_spy"
    names = {p.name for p in dest.iterdir()}
    assert {"tree_d2_3y_beat_spy.md", "config.toml", "promoted.json"} <= names
    meta = json.loads((dest / "promoted.json").read_text())
    assert meta["config_path"] == str(ws["experiments"] / "tree.toml")
    assert meta["experiment"] == "tree_d2_3y_beat_spy"
    assert meta["label"] == "label_3y_beat_spy" and meta["scheme"] == "walkforward"
    assert meta["headline"].startswith("p@5=")
    assert "b2m_rank" in meta["baseline"]
    assert meta["lift"][0] in "+-"
    assert meta["note"] == "promoted with a note"
    assert meta["run_id"] and meta["config_hash"]
    # the source config carries the note, the snapshot too
    assert 'note = "promoted with a note"' in (ws["experiments"] / "tree.toml").read_text()
    assert 'note = "promoted with a note"' in (dest / "config.toml").read_text()
    # the index
    index = (ws["reports"] / "promoted" / "README.md").read_text()
    assert "| [tree_d2_3y_beat_spy](tree_d2_3y_beat_spy/tree_d2_3y_beat_spy.md) |" in index
    assert "promoted with a note" in index
    assert "label_3y_beat_spy · 3y · walkforward" in index
    # re-promoting without --force is refused
    with pytest.raises(SystemExit, match="--force"):
        promote.promote("tree_d2_3y_beat_spy", reports_dir=ws["reports"],
                        experiments_dir=ws["experiments"],
                        results_path=ws["results"], git=False)


def test_listing_marks_promoted(workspace, capsys):
    catalog.main([*_common(workspace), "list"])
    tree_line = next(ln for ln in capsys.readouterr().out.splitlines()
                     if "tree.toml" in ln)
    assert "★" in tree_line


def test_index_handles_legacy_promoted_dirs(tmp_path):
    promoted = tmp_path / "promoted"
    (promoted / "old").mkdir(parents=True)
    (promoted / "old" / "old.md").write_text(
        "# Experiment report — old\n\n- run id: `abc`\n"
        "- dataset version: `1.0` (pinned, immutable)\n- config hash: `h`\n"
        "- model: `decision_tree` params `{}`\n"
        "- label: `label_2y_cagr_ge_0` — horizon 2y, scheme `walkforward`\n"
    )
    (promoted / "brief_only").mkdir()
    (promoted / "brief_only" / "upstream_brief.md").write_text("# brief\n")
    promote.write_index(promoted)
    index = (promoted / "README.md").read_text()
    assert "| [old](old/old.md) | label_2y_cagr_ge_0 · 2y · walkforward | decision_tree | 1.0 |" in index
    assert "[brief_only](brief_only/upstream_brief.md)" in index
