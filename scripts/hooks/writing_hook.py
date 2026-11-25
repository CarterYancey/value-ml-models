"""Claude Code hook: refuse a reply or a doc edit that fails the writing check.

Wired in `.claude/settings.json` for two events.

- ``Stop``: reads the transcript, takes every assistant text block of the
  turn that is ending, and runs ``harness.writing.check_text`` on it.
  Error-level findings block the stop with ``{"decision": "block"}`` and
  the findings as the reason, so the model rewrites before the user sees
  the message. ``stop_hook_active`` plus a per-session counter cap the
  rewrites at ``MAX_ROUNDS`` so a false positive cannot loop forever.
- ``PostToolUse`` on ``Write|Edit``: checks the text just written
  (``content`` or ``new_string``) when the file is one of the prose
  records (see ``prose_path``). Old text in the file is not re-checked,
  so legacy paragraphs never block an edit next to them.

Run it by hand to see what it would say:
``echo '{"hook_event_name":"Stop","transcript_path":"..."}' | python scripts/hooks/writing_hook.py``
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))

from harness import writing  # noqa: E402

MAX_ROUNDS = 3
PROSE_DIRS = ("docs/",)
PROSE_FILES = ("TODO.md", "README.md", "PLAN.md", "CLAUDE.md")
NOT_PROSE = ("docs/logbook.md", "GLOSSARY.md", "data/")
STATE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "vml-writing"


def prose_path(path: str) -> bool:
    rel = os.path.relpath(path, ROOT) if os.path.isabs(path) else path
    rel = rel.replace(os.sep, "/")
    if not rel.endswith(".md") or any(rel.startswith(n) or rel == n for n in NOT_PROSE):
        return False
    return rel in PROSE_FILES or any(rel.startswith(d) for d in PROSE_DIRS)


def last_turn_text(transcript: Path) -> str:
    """Concatenate the assistant text blocks after the last human message."""
    entries = []
    for line in transcript.read_text().splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    start = 0
    for i, e in enumerate(entries):
        if e.get("type") != "user" or e.get("isMeta"):
            continue        # isMeta: text the harness injected, not the person
        content = (e.get("message") or {}).get("content")
        if isinstance(content, list):
            if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
                continue
            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        if not isinstance(content, str):
            continue
        if content.lstrip().startswith(("<system-reminder>", "[Request interrupted")):
            continue
        start = i
    texts = []
    for e in entries[start:]:
        if e.get("type") != "assistant":
            continue
        for c in (e.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "text" and c.get("text"):
                texts.append(c["text"])
    return "\n\n".join(texts)


def _rounds(session: str, reset: bool = False) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    f = STATE_DIR / f"{session or 'default'}.rounds"
    if reset:
        f.unlink(missing_ok=True)
        return 0
    n = int(f.read_text() or 0) + 1 if f.exists() else 1
    f.write_text(str(n))
    return n


def on_stop(payload: dict) -> dict:
    path = payload.get("transcript_path")
    if not path or not Path(path).exists():
        return {}
    text = last_turn_text(Path(path))
    if not text.strip():
        return {}
    report = writing.check_text(text)
    session = payload.get("session_id", "")
    if not report.errors:
        _rounds(session, reset=True)
        out = {}
        if report.skipped:
            out["systemMessage"] = "writing check: " + report.skipped[0]
        return out
    if not payload.get("stop_hook_active"):
        _rounds(session, reset=True)      # a fresh turn: start counting again
    rounds = _rounds(session)
    body = report.format(warnings=False)
    if rounds > MAX_ROUNDS:
        _rounds(session, reset=True)
        return {"systemMessage": (
            f"writing check: {len(report.errors)} error(s) remain after "
            f"{MAX_ROUNDS} rewrites. The reply is shown as written.\n{body}")}
    return {
        "decision": "block",
        "reason": (
            f"The writing check found {len(report.errors)} error(s) in your reply "
            f"(round {rounds} of {MAX_ROUNDS}). Rewrite the whole reply so every "
            "sentence has a subject and a finite verb, no shorthand from the "
            "denylist, no aphorism, no clause in parentheses, no semicolon and at "
            f"most {writing.MAX_WORDS} words. Test a draft with "
            "`vml-writing --text <<'EOF' ... EOF`.\n" + body
        ),
    }


def on_post_tool_use(payload: dict) -> dict:
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if not path or not prose_path(path):
        return {}
    text = tool_input.get("content") or tool_input.get("new_string") or ""
    if not text.strip():
        return {}
    report = writing.check_text(text, path=os.path.relpath(path, ROOT) if os.path.isabs(path) else path)
    if not report.errors:
        return {}
    return {
        "decision": "block",
        "reason": (
            f"The writing check found {len(report.errors)} error(s) in the text just "
            f"written to {path}. Fix these sentences in the file now.\n"
            + report.format(warnings=False)
        ),
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    event = payload.get("hook_event_name")
    if event == "Stop":
        out = on_stop(payload)
    elif event == "PostToolUse" and payload.get("tool_name") in ("Write", "Edit"):
        out = on_post_tool_use(payload)
    else:
        out = {}
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
