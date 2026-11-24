"""The writing check: CLAUDE.md "Writing" as a program.

Carter reads this repository's records after weeks away and found them
unreadable (2026-11-24). The second round of corrections showed that a
written rule does not stop the habits that cause it: fragments without
a finite verb, shorthand coined on the spot ("in money"), aphorisms
("the gain is the band, not the selection"), clauses hidden in
parentheses. This module turns the rules into checks that point at a
sentence, so the repository can refuse text instead of asking for care.

Three callers use it:

- ``vml-writing`` (this module's ``main``) checks files or text.
- ``scripts/hooks/writing_hook.py`` runs it from Claude Code's ``Stop``
  hook on every reply and from ``PostToolUse`` on text written to the
  docs.
- ``vml-logbook add`` and ``vml-promote --note`` refuse an entry or a
  note that fails.

The checks that need part-of-speech tags (fragment, noun stack, passive
voice) use spaCy's ``en_core_web_sm`` when it is installed
(``uv pip install -e '.[writing]'`` and
``python -m spacy download en_core_web_sm``). Without it those checks
are skipped and the report says so. The phrase denylist lives in
``docs/writing_denylist.toml``: every phrase Carter has objected to goes
there with the date and the quote, so a correction never regresses.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

MAX_WORDS = 25
NUMBERS_WARN = 2
NUMBERS_ERROR = 3
FINITE_TAGS = {"VBZ", "VBP", "VBD", "MD"}
NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
NOUN_STACK = 4

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DENYLIST = REPO_ROOT / "docs" / "writing_denylist.toml"

# A "severity" is "error" (the text is refused) or "warning" (reported,
# never refused). Which check has which severity is fixed here.
SEVERITY = {
    "fragment": "error",
    "semicolon": "error",
    "long": "error",
    "parenthetical": "error",
    "numbers": "error",      # NUMBERS_ERROR and above; NUMBERS_WARN is a warning
    "denylist": "error",
    "aphorism": "error",
    "pronoun": "error",
    "dash": "error",
    "noun_stack": "warning",
    "passive": "warning",
}


@dataclass
class Finding:
    check: str
    message: str
    sentence: str
    line: int
    severity: str
    path: str = ""

    def format(self) -> str:
        where = f"{self.path}:{self.line}" if self.path else f"line {self.line}"
        return f'{where}: [{self.check}] {self.message}: "{self.sentence}"'


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)   # checks not run, with why

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    def format(self, warnings: bool = True) -> str:
        lines = [f.format() for f in self.errors]
        if warnings:
            lines += [f.format() for f in self.warnings]
        for s in self.skipped:
            lines.append(f"skipped: {s}")
        return "\n".join(lines)


# --------------------------------------------------------------------------
# denylist

@dataclass
class DenyEntry:
    pattern: re.Pattern
    source: str
    why: str


def load_denylist(path: Path | None = None) -> list[DenyEntry]:
    """Read ``docs/writing_denylist.toml``: ``[[phrase]]`` tables with
    ``pattern`` (a regex, matched case-insensitively, word-bounded when it
    starts or ends with a word character), ``since``, ``quote`` and ``why``."""
    path = Path(path or os.environ.get("VML_WRITING_DENYLIST") or DEFAULT_DENYLIST)
    if not path.exists():
        return []
    data = tomllib.loads(path.read_text())
    out: list[DenyEntry] = []
    for entry in data.get("phrase", []):
        pat = entry["pattern"]
        if re.match(r"\w", pat):
            pat = r"\b" + pat
        if re.search(r"\w$", pat):
            pat = pat + r"\b"
        out.append(DenyEntry(
            pattern=re.compile(pat, re.IGNORECASE),
            source=f'{entry.get("since", "")}: "{entry.get("quote", "")}"'.strip(": "),
            why=entry.get("why", ""),
        ))
    return out


# --------------------------------------------------------------------------
# markdown -> paragraphs of prose

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^\s*#{1,6}\s")
_TABLE = re.compile(r"^\s*\|")
_RULE = re.compile(r"^\s*([-*_]\s*){3,}$")
_LINKDEF = re.compile(r"^\s*\[[^\]]+\]:\s*\S+")
_LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(\[[ xX]\]\s+)?")
_QUOTE = re.compile(r"^\s*>\s?")
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_URL = re.compile(r"https?://\S+")
_BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_EM = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])|(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_HTML = re.compile(r"</?[a-zA-Z][^>]*>")
_CODE_TOKEN = "Code"


def _inline(text: str) -> str:
    text = _INLINE_CODE.sub(_CODE_TOKEN, text)
    text = _IMAGE.sub(r"\1", text)
    text = _LINK.sub(r"\1", text)
    text = _URL.sub("URL", text)
    text = _BOLD.sub(lambda m: m.group(1) or m.group(2), text)
    text = _EM.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = _HTML.sub("", text)
    return text


def paragraphs(markdown: str) -> list[tuple[int, str, bool]]:
    """Return ``(first_line_number, prose, completes_a_colon)`` for each
    paragraph or list item. The flag is true for a list item that follows a
    paragraph ending in a colon: such items complete that sentence ("It
    refuses nine things:" followed by the nine), so they need no verb.

    Code fences, tables, headings, horizontal rules, link definitions and
    HTML comments are dropped. Inline code becomes the word "Code" so a
    path or an expression never reads as a sentence and its digits never
    count as numbers. A line that ends with a colon closes its paragraph,
    so a label such as "Kept short on purpose:" is checked on its own."""
    text = _COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), markdown)
    lines = text.splitlines()
    out: list[tuple[int, str, bool]] = []
    buf: list[str] = []
    start = 0
    in_fence = False
    front = 0
    is_item = False
    after_colon = False     # the last flushed paragraph ended with a colon
    in_enum = False         # inside a list that follows such a paragraph

    def flush() -> None:
        nonlocal buf, after_colon, in_enum, is_item
        if buf:
            joined = _inline(" ".join(s.strip() for s in buf).strip())
            if joined:
                if is_item:
                    in_enum = in_enum or after_colon
                else:
                    in_enum = False
                out.append((start, joined, is_item and in_enum))
                after_colon = joined.endswith(":")
        buf = []
        is_item = False

    for i, raw in enumerate(lines, start=1):
        if i == 1 and raw.strip() == "---":
            front = 1
            continue
        if front == 1:
            if raw.strip() == "---":
                front = 2
            continue
        if _FENCE.match(raw):
            in_fence = not in_fence
            flush()
            continue
        if in_fence:
            continue
        line = raw
        if _HEADING.match(line) or _TABLE.match(line) \
                or _RULE.match(line) or _LINKDEF.match(line):
            flush()
            in_enum = False
            after_colon = False
            continue
        if not line.strip():
            flush()
            continue
        line = _QUOTE.sub("", line)
        m = _LIST.match(line)
        if m:
            flush()
            is_item = True
            line = line[m.end():]
        elif not buf and not line[:1].isspace():
            in_enum = False      # a plain paragraph ends the list
        if not buf:
            start = i
        buf.append(line)
        if line.rstrip().endswith(":"):
            flush()
    flush()
    return out


# --------------------------------------------------------------------------
# sentences

_nlp = None
_nlp_error: str | None = None


def _load_nlp():
    global _nlp, _nlp_error
    if _nlp is not None or _nlp_error is not None:
        return _nlp
    try:
        import spacy  # type: ignore
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    except Exception as exc:  # ImportError or OSError (model missing)
        _nlp_error = (
            "spaCy or en_core_web_sm is not installed, so the fragment, "
            "noun-stack and passive-voice checks did not run. Install with "
            "`uv pip install -e '.[writing]'` and "
            "`python -m spacy download en_core_web_sm`. "
            f"({type(exc).__name__}: {exc})"
        )
    return _nlp


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])|(?<=:)\s*$")


def _split_plain(text: str) -> list[str]:
    parts = [p.strip() for p in _SENT_SPLIT.split(text) if p and p.strip()]
    return parts


@dataclass
class Sentence:
    text: str
    tokens: list  # spaCy tokens, or [] without spaCy


def sentences(paragraph: str) -> list[Sentence]:
    nlp = _load_nlp()
    if nlp is None:
        return [Sentence(t, []) for t in _split_plain(paragraph)]
    doc = nlp(paragraph)
    out = []
    for sent in doc.sents:
        text = sent.text.strip()
        if not text or not re.search(r"\w", text):
            continue
        out.append(Sentence(text, [t for t in sent if not t.is_space]))
    return out


# --------------------------------------------------------------------------
# checks

_WORD = re.compile(r"[A-Za-z][A-Za-z'-]*|\d[\w.,%-]*")
_DATE = re.compile(r"\b\d{4}-\d\d(-\d\d)?\b")
_RANGE = re.compile(r"\b\d{4}\s*[-–]\s*\d{2,4}\b")
_OF = re.compile(r"\b\d+ of (the )?\d+\b")
_LABELS = re.compile(
    r"\b(decisions?|seeds?|cell|top|fold|folds|look|looks|conclusions?|section|§|item|PR|pull request|"
    r"ADR|phase|step|table|figure|line|lines|rank|ranks|v|p@|k ?=|n ?=)\s*#?\d[\d.,]*(\s*(to|and|–|-)\s*\d[\d.,]*)?",
    re.IGNORECASE)
_VERSION = re.compile(r"\bv?\d+\.\d+(\.\d+)?\b(?=[^%]|$)")
_YEAR = re.compile(r"\b(19|20)\d\d(s)?\b")
_UNIT_WORD = re.compile(r"\b\d+-(month|year|day|week|quarter|sector|stock)\b")
_NUMBER = re.compile(r"(?<![\w.])[-+−]?\d[\d,]*(\.\d+)?\s?(%|bps|pts?|points?|se|x)?(?![\w.])")
_PAREN = re.compile(r"\(([^()]*)\)")
_PAREN_OK = re.compile(
    r"^((\w+ )?decisions?\b.*|seeds?\b.*|see\b.*|fold\b.*|look \d+ of \d+|n ?= ?\d+|"
    r"pull request \d+|[\w./-]+\.(md|toml|csv|py|json|txt|parquet)|"
    r"[-+−]?\d[\d.,]*\s?(se|%|bps|pts?|points?|years?|rows?|folds?|runs?|looks?)?|"
    r"\d{4}(-\d\d)?(-\d\d)?|PR ?#?\d+|§ ?[\d.]+|" + _CODE_TOKEN + r"|URL|"
    r"[A-Za-z]+ \d+)$",
    re.IGNORECASE,
)
_APHORISM = [
    re.compile(r"\b(is|are|was|were)\s+(the|a|an|its|their|your)?\s*[\w-]+,\s+not\s+(the|a|an|its|their|your)?\s*[\w-]+", re.I),
    re.compile(r"^(what|whatever|whoever)\s+(is|was|gets|get)\s+\w+(\s+\w+)?\s+(is|are|was|were)\s+\w+", re.I),
    re.compile(r"^\w+\s+stays\s+\w+\.?$", re.I),
]
_PRONOUN = re.compile(r"\b(he|him|his|she|her|hers)\b", re.IGNORECASE)
_DASH = re.compile(r"\s[—–]\s|\s-\s|—")


def _words(text: str) -> list[str]:
    return _WORD.findall(text)


def _count_numbers(text: str) -> int:
    """Count the measurements in a sentence. Dates, year ranges, "13 of 16",
    labels such as "decision 58" or "seed 23", version strings and
    "12-month" are not measurements and are not counted."""
    text = _DATE.sub(" ", text)
    text = _RANGE.sub(" ", text)
    text = _OF.sub(" ", text)
    text = _LABELS.sub(" ", text)
    text = _UNIT_WORD.sub(" ", text)
    text = _YEAR.sub(" ", text)
    text = re.sub(r"\bv\d+\.\d+(\.\d+)?\b", " ", text)
    return len(_NUMBER.findall(text))


def _fragment_level(sent: Sentence) -> str | None:
    """"error" for a sentence with no verb at all, "warning" for one with a
    participle or an infinitive but no finite verb, None for a sentence.

    The small tagger reads some verbs as plural nouns ("the backtest
    charges 35 bps"). A noun followed directly by a plural noun in a
    sentence of five or more words is read as that mistake, not as a
    fragment, so the check stays quiet rather than wrong."""
    toks = sent.tokens
    if not toks:
        return None
    words = [t for t in toks if not t.is_punct]
    if len(words) < 2:
        return None          # "Done." or "Yes." answers a person
    if all(t.text in (_CODE_TOKEN, "URL") or t.is_punct or t.like_num for t in toks):
        return None
    if any(t.tag_ in FINITE_TAGS for t in toks):
        return None
    root = next((t for t in toks if t.dep_ == "ROOT"), None)
    if root is not None and root.tag_ == "VB":
        head_idx = words.index(root) if root in words else 99
        if head_idx <= 2:
            return None          # an imperative
    if any(t.tag_.startswith("VB") for t in toks):
        return "warning"
    if len(words) >= 5:
        for a, b in zip(words, words[1:]):
            if a.tag_ in ("NN", "NNP") and b.tag_ == "NNS":
                return None      # probably a mis-tagged verb
    return "error"


def _noun_stack(sent: Sentence) -> str | None:
    run: list[str] = []
    for t in sent.tokens:
        if t.tag_ in NOUN_TAGS and t.text not in (_CODE_TOKEN, "URL"):
            run.append(t.text)
            if len(run) >= NOUN_STACK:
                return " ".join(run)
        else:
            run = []
    return None


def _passive(sent: Sentence) -> bool:
    return any(t.dep_ in ("nsubjpass", "auxpass") for t in sent.tokens)


def check_text(text: str, *, denylist: list[DenyEntry] | None = None,
               path: str = "", skip: Iterable[str] = ()) -> Report:
    """Check markdown or plain text. ``skip`` names checks not to run."""
    skip = set(skip)
    deny = load_denylist() if denylist is None else denylist
    report = Report()
    nlp = _load_nlp()
    if nlp is None and _nlp_error:
        report.skipped.append(_nlp_error)

    def add(check: str, msg: str, sent: str, line: int, severity: str | None = None) -> None:
        if check in skip:
            return
        report.findings.append(Finding(
            check, msg, sent if len(sent) <= 160 else sent[:157] + "...",
            line, severity or SEVERITY[check], path,
        ))

    for line, para, completes in paragraphs(text):
        for sent in sentences(para):
            s = sent.text
            words = _words(s)
            if ";" in s:
                add("semicolon", "a semicolon joins two sentences", s, line)
            if len(words) > MAX_WORDS:
                add("long", f"{len(words)} words, the limit is {MAX_WORDS}", s, line)
            for m in _PAREN.finditer(s):
                inner = m.group(1).strip()
                if len(_words(inner)) >= 2 and not _PAREN_OK.match(inner):
                    add("parenthetical", f"a clause hidden in parentheses: ({inner})", s, line)
            n = _count_numbers(s)
            if n >= NUMBERS_ERROR:
                add("numbers", f"{n} measurements in one sentence; use a table", s, line)
            elif n == NUMBERS_WARN:
                add("numbers", f"{n} measurements in one sentence", s, line, "warning")
            for d in deny:
                m = d.pattern.search(s)
                if m:
                    add("denylist", f'"{m.group(0)}" is on the denylist ({d.source}): {d.why}', s, line)
            for pat in _APHORISM:
                if pat.search(s):
                    add("aphorism", "an aphorism; say what was measured and what it means", s, line)
                    break
            if _PRONOUN.search(s):
                add("pronoun", "use the name or they/them; nobody here has stated other pronouns", s, line)
            if _DASH.search(s):
                add("dash", "a dash joins clauses; write two sentences or use a comma", s, line)
            if sent.tokens:
                level = None if completes else _fragment_level(sent)
                if level:
                    add("fragment", "no finite verb: write a full sentence with a subject and a verb", s, line, level)
                stack = _noun_stack(sent)
                if stack:
                    add("noun_stack", f"{NOUN_STACK}+ nouns in a row: {stack}", s, line)
                if _passive(sent):
                    add("passive", "passive voice; say who did it", s, line)
    return report


def check_file(path: Path, **kw) -> Report:
    return check_text(path.read_text(), path=str(path), **kw)


# --------------------------------------------------------------------------
# CLI

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vml-writing",
        description="Check prose against the writing rules in CLAUDE.md. "
        "Exit 1 when an error-level finding exists.",
    )
    parser.add_argument("paths", nargs="*", help="markdown files to check")
    parser.add_argument("--text", action="store_true",
                        help="read one text from stdin instead of files")
    parser.add_argument("--skip", default="", help="comma-separated checks to skip")
    parser.add_argument("--no-warnings", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--denylist", default=None)
    args = parser.parse_args(argv)
    deny = load_denylist(Path(args.denylist)) if args.denylist else None
    skip = [s for s in args.skip.split(",") if s]
    reports: list[Report] = []
    if args.text:
        reports.append(check_text(sys.stdin.read(), denylist=deny, skip=skip))
    else:
        for p in args.paths:
            reports.append(check_file(Path(p), denylist=deny, skip=skip))
    errors = sum(len(r.errors) for r in reports)
    warnings = sum(len(r.warnings) for r in reports)
    if args.json:
        print(json.dumps({
            "errors": errors, "warnings": warnings,
            "findings": [asdict(f) for r in reports for f in r.findings],
            "skipped": sorted({s for r in reports for s in r.skipped}),
        }, indent=1))
    else:
        for r in reports:
            out = r.format(warnings=not args.no_warnings)
            if out:
                print(out)
        print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
