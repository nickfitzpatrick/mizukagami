"""Score retrieval against eval_set.json (spec §5).

Computes hit_rate@k and recall@k for retrieval.search(). Run at stage 1
(keyword, now) and again at stage 2 (embeddings, M3) and compare — the
delta is the headline portfolio result.

Run (from eval/):  python run_eval.py [--k 5]
This is hermetic: pure retrieval, no model API calls. CI runs it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make backend importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import retrieval  # noqa: E402

EVAL_SET = Path(__file__).resolve().parent / "eval_set.json"


def _score_items(items: list[dict], k: int) -> dict:
    hits = 0
    for item in items:
        expected = set(item["expected_note_ids"])
        got = {h["note_id"] for h in retrieval.search(item["question"], k)}
        if expected & got:
            hits += 1
    n = len(items)
    return {"n": n, "hit_rate": hits / n if n else 0.0}


def score(k: int = 5) -> dict:
    items = json.loads(EVAL_SET.read_text(encoding="utf-8"))["items"]
    direct = [i for i in items if i.get("kind") == "direct"]
    paraphrase = [i for i in items if i.get("kind") == "paraphrase"]
    return {
        "k": k,
        "overall": _score_items(items, k),
        "direct": _score_items(direct, k),
        "paraphrase": _score_items(paraphrase, k),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=1)
    args = ap.parse_args()
    r = score(args.k)
    k = r["k"]
    for label in ("overall", "direct", "paraphrase"):
        s = r[label]
        print(f"[keyword stage] {label:10s} n={s['n']:2d}  hit_rate@{k}={s['hit_rate']:.2f}")
    # Non-zero exit only if retrieval is totally broken, so CI catches regressions.
    return 0 if r["overall"]["hit_rate"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
