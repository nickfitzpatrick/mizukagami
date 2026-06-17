"""Audit how many content tokens each paraphrase question shares with its
target note. Keeps the eval honest: a 'paraphrase' that shares real vocabulary
is just a keyword query in disguise and inflates the keyword baseline.

Run (from eval/):  python check_overlap.py
Prints shared content tokens per paraphrase item; flags any with > THRESHOLD.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import notes_store  # noqa: E402
import retrieval  # noqa: E402

THRESHOLD = 1  # a paraphrase may share at most this many content tokens


def _content_tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in retrieval._STOP}


def main() -> int:
    notes = {n["id"]: _content_tokens(n["title"] + " " + n["body"])
             for n in notes_store.iter_notes()}
    items = json.loads(
        (Path(__file__).resolve().parent / "eval_set.json").read_text()
    )["items"]

    worst = 0
    for it in items:
        if it["kind"] != "paraphrase":
            continue
        q = _content_tokens(it["question"])
        for tid in it["expected_note_ids"]:
            shared = sorted(q & notes[tid])
            worst = max(worst, len(shared))
            flag = "  <-- LEAK" if len(shared) > THRESHOLD else ""
            print(f"{tid:42s} shared={shared}{flag}")

    print(f"\nmax shared content tokens = {worst} (threshold {THRESHOLD})")
    return 0 if worst <= THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
