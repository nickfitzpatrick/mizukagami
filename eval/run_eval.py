"""Score retrieval against eval_set.json (spec §5).

Computes hit_rate@k for retrieval.search() at BOTH stages — keyword (M1) and
embeddings (M3) — and prints the delta. The paraphrase-split gap is the
headline portfolio result.

Run (from eval/):  python run_eval.py [--k 1]
This is hermetic: pure retrieval, no model API calls (the embedding model runs
locally in-process). CI runs it.
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


def score(k: int, stage: str) -> dict:
    retrieval.set_stage(stage)
    items = json.loads(EVAL_SET.read_text(encoding="utf-8"))["items"]
    direct = [i for i in items if i.get("kind") == "direct"]
    paraphrase = [i for i in items if i.get("kind") == "paraphrase"]
    return {
        "overall": _score_items(items, k),
        "direct": _score_items(direct, k),
        "paraphrase": _score_items(paraphrase, k),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=1)
    args = ap.parse_args()
    k = args.k

    kw = score(k, "keyword")
    emb = score(k, "embeddings")

    print(f"hit_rate@{k}    keyword  embeddings   delta")
    for label in ("overall", "direct", "paraphrase"):
        a = kw[label]["hit_rate"]
        b = emb[label]["hit_rate"]
        n = kw[label]["n"]
        print(f"  {label:10s} (n={n:2d})   {a:.2f}      {b:.2f}     {b - a:+.2f}")

    # Non-zero exit only if embeddings retrieval is totally broken, so CI
    # catches regressions without asserting a brittle absolute threshold.
    return 0 if emb["overall"]["hit_rate"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
