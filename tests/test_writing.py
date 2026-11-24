"""The writing check refuses the sentences Carter quoted and accepts plain ones."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from harness import writing

ROOT = Path(__file__).resolve().parents[1]
HAS_NLP = writing._load_nlp() is not None

# Sentences Carter quoted on 2026-11-24 as unreadable, with the check that
# must catch each one. The test is the record: a phrase that gets through
# again is a regression.
QUOTED = [
    ("Three legs refit, two screens, three backtests.", {"fragment"}),
    ("The size band in money.", {"fragment", "denylist"}),
    ("The picture is unchanged in kind.", {"denylist"}),
    ("The gain is the band, not the selection.", {"aphorism", "denylist"}),
    ("The money was the same as the candidate's, but 4 points fewer buys lost money.",
     {"denylist"}),
    ("Not carried forward on money.", {"fragment", "denylist"}),
    ("What is bought is yours.", {"aphorism", "denylist"}),
    ("Kept short on purpose:", {"denylist"}),
    ("The lead holds (Carter's reading).", {"parenthetical", "denylist"}),
    ("The holdout number is biased (20 looks; the counts are part of every holdout number).",
     {"parenthetical", "semicolon"}),
    ("The peers' excess was +0.046 / +0.059 / −0.016 for 2005–12 / 2013–20 / 2021–23.",
     {"numbers"}),
    ("He expects the bubble to deflate.", {"pronoun"}),
    ("Closed stays closed.", {"aphorism", "denylist"}),
]

CLEAN = [
    "I refit the three legs on dataset_v1.4.1 and ran the two screens.",
    "Restricting the candidate to the larger half raised the final value on all three seeds.",
    "Carter reads the years from 2021 to 2026 as a bubble that deflates.",
    "Run `vml-queue status` before you start.",
    "The filter is proposed to Carter as a change to the candidate (decision 58).",
    "The sell discipline ended at 1,294,414 on deposits of 260,000.",
    "Never edit a config that has run.",
]


@pytest.mark.parametrize("sentence,checks", QUOTED)
def test_quoted_sentences_fail(sentence, checks):
    report = writing.check_text(sentence)
    found = {f.check for f in report.errors}
    needed = checks if HAS_NLP else checks - {"fragment"}
    assert needed & found, f"{sentence!r}: wanted {needed}, got {found}"
    assert report.errors


@pytest.mark.parametrize("sentence", CLEAN)
def test_clean_sentences_pass(sentence):
    report = writing.check_text(sentence)
    assert not report.errors, report.format()


def test_markdown_structure_is_not_prose():
    text = (
        "# Heading without a verb\n\n"
        "| col | 1 | 2 |\n|---|---|---|\n| a | 3 | 4 |\n\n"
        "```\nfragment in code; with 1 2 3 4 numbers\n```\n\n"
        "The table above holds the numbers.\n"
    )
    report = writing.check_text(text)
    assert not report.errors, report.format()


def test_inline_code_hides_digits_and_paths():
    text = "The filter `log_marketcap_rank >= 0.5` keeps the larger half at 35 bps."
    report = writing.check_text(text)
    assert not [f for f in report.errors if f.check == "numbers"], report.format()


def test_list_items_are_checked_one_by_one():
    text = "- I merged the branch.\n- Larger-half filter for Carter.\n"
    report = writing.check_text(text)
    lines = {f.line for f in report.errors}
    if HAS_NLP:
        assert lines == {2}, report.format()


def test_denylist_is_loaded_from_docs():
    deny = writing.load_denylist()
    assert any(d.pattern.pattern.startswith(r"\bin money") for d in deny)
    for d in deny:
        assert d.why, d.pattern.pattern


def test_cli_text_mode(tmp_path):
    cmd = [sys.executable, "-m", "harness.writing", "--text", "--json"]
    env = {"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"}
    proc = subprocess.run(cmd, input="The size band in money.", text=True,
                          capture_output=True, env=env, cwd=ROOT)
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["errors"] >= 1


def test_list_items_completing_a_colon_need_no_verb():
    text = "It refuses three things:\n\n1. a semicolon,\n2. a dash,\n3. a fragment.\n\nA plain paragraph follows.\n\n- Larger-half filter for Carter.\n"
    report = writing.check_text(text)
    frags = [f for f in report.errors if f.check == "fragment"]
    if HAS_NLP:
        assert [f.line for f in frags] == [9], report.format()
