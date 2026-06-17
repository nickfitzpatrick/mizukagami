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


def score(k: int = 5) -> dict:
    data = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    items = data["items"]
    hits = 0
    recall_sum = 0.0
    for item in items:
        expected = set(item["expected_note_ids"])
        got = {h["note_id"] for h in retrieval.search(item["question"], k)}
        found = expected & got
        if found:
            hits += 1
        recall_sum += len(found) / len(expected) if expected else 0.0
    n = len(items)
    return {
        "n": n,
        "k": k,
        "hit_rate": hits / n if n else 0.0,
        "recall": recall_sum / n if n else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    r = score(args.k)
    print(
        f"[keyword stage] n={r['n']} k={r['k']} "
        f"hit_rate@{r['k']}={r['hit_rate']:.2f} recall@{r['k']}={r['recall']:.2f}"
    )
    # Non-zero exit if retrieval is totally broken, so CI catches regressions.
    return 0 if r["hit_rate"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
