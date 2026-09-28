"""One ledger, several files: a store reads its own file, the shards
beside it and the files named in VML_LEDGER_READ, each row once."""

from harness.results import ResultsStore, default_results_path


def _row(run_id, label="label_3y_beat_spy", config_hash="h1"):
    return {
        "run_id": run_id,
        "logged_utc": "2026-01-01T00:00:00+00:00",
        "status": "completed",
        "experiment": "e",
        "config_hash": config_hash,
        "dataset_version": "dataset_v0",
        "scheme": "walkforward",
        "fold": 2016,
        "horizon_years": 3,
        "label": label,
        "model": "m",
    }


def _count(store):
    return store.configurations_tried(
        "dataset_v0", "walkforward", 3, "label_3y_beat_spy"
    )


def test_single_file_is_unchanged(tmp_path):
    store = ResultsStore(tmp_path / "results.csv")
    assert store.load().empty
    store.append(_row("a"))
    assert len(store.load()) == 1
    assert store.ledger_files() == [tmp_path / "results.csv"]


def test_local_ledger_reads_shards(tmp_path):
    local = ResultsStore(tmp_path / "results.csv")
    shard = ResultsStore(tmp_path / "ledger" / "sandbox-1.csv")
    local.append(_row("a", config_hash="h1"))
    shard.append(_row("b", config_hash="h2"))
    assert _count(local) == 2
    # and a shard sees the local ledger and its sibling shards
    other = ResultsStore(tmp_path / "ledger" / "sandbox-2.csv")
    other.append(_row("c", config_hash="h3"))
    assert _count(shard) == 3
    # writes stay in the file the store was opened on
    assert len((tmp_path / "results.csv").read_text().splitlines()) == 2


def test_rows_in_two_files_count_once(tmp_path, monkeypatch):
    host = ResultsStore(tmp_path / "host" / "results.csv")
    host.append(_row("a"))
    shard = ResultsStore(tmp_path / "clone" / "ledger" / "s.csv")
    shard.append(_row("a"))  # the same row, copied
    shard.append(_row("b", config_hash="h2"))
    monkeypatch.setenv("VML_LEDGER_READ", str(tmp_path / "host" / "results.csv"))
    rows = shard.load()
    assert len(rows) == 2
    assert _count(shard) == 2


def test_missing_extra_is_skipped(tmp_path, monkeypatch):
    monkeypatch.setenv("VML_LEDGER_READ", str(tmp_path / "nowhere.csv"))
    store = ResultsStore(tmp_path / "results.csv")
    store.append(_row("a"))
    assert len(store.load()) == 1


def test_default_path_follows_the_environment(monkeypatch):
    monkeypatch.delenv("VML_RESULTS", raising=False)
    assert str(default_results_path()) == "experiments/results.csv"
    monkeypatch.setenv("VML_RESULTS", "experiments/ledger/me.csv")
    assert str(default_results_path()) == "experiments/ledger/me.csv"
