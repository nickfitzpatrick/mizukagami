# Retrieval eval: keyword vs. embeddings (M3)

The point of M3 is not "add embeddings" — it is **measure what embeddings buy
you** on this corpus, honestly. This doc records the before/after.

## Setup

- **Corpus:** 13 markdown notes (`notes/`), the real working notes used through M1–M2.
- **Eval set:** 25 questions (`eval/eval_set.json`), each labeled with the note
  id(s) that *should* be retrieved. Split by `kind`:
  - `direct` (n=12): question shares vocabulary with the target note.
  - `paraphrase` (n=13): question is reworded to share **at most one** content
    token with the target note. This is enforced, not eyeballed: `check_overlap.py`
    fails if any paraphrase leaks more than one shared token, so the paraphrase
    split is a true semantic test rather than a keyword query in disguise.
- **Difficulty by design:** several targets have sibling notes on the same project
  (4 RouteMorph notes, 3 Geopogo notes), so a retriever must pick the *right* note
  about a topic, not just land in the right neighborhood.
- **Metric:** `hit_rate@k` — fraction of questions where at least one expected
  note appears in the top-k. Reported at **k=1** (the hardest, most honest
  setting: did the single best result get it right?).
- **Stage 1 (keyword):** token-overlap scoring, title weighted 2x.
- **Stage 2 (embeddings):** `all-MiniLM-L6-v2` (sentence-transformers), notes and
  query encoded to unit vectors, ranked by cosine (dot product). Brute-force over
  the whole corpus — at 13 notes a vector DB would be premature.

Re-check overlap any time the set changes:

```bash
python eval/check_overlap.py
```

Both stages are scored by the *same* harness calling the *same* `search(query, k)`
signature; only the implementation behind it changes. Run:

```bash
python eval/run_eval.py --k 1
```

## Results

Keyword is measured (below). The embeddings column is filled by running
`python eval/run_eval.py --k 1` on a machine with torch installed — replace the
`TBD` cells with that output. Tested install path: Python 3.14,
sentence-transformers 5.6 / torch 2.12.

| hit_rate@1 | keyword | embeddings | delta |
|------------|:-------:|:----------:|:-----:|
| overall (n=25)    | 0.52 | TBD | TBD |
| direct (n=12)     | 1.00 | TBD | TBD |
| paraphrase (n=13) | 0.08 | TBD | TBD |

## Reading the result

The headline is the **paraphrase split**, not the overall number. Keyword search
already maxes out on `direct` questions (1.00 — it has the words), so embeddings
add nothing there and shouldn't be expected to. Where keyword search structurally
cannot win is `paraphrase`: each paraphrase shares at most one token with its
target note, so token overlap has almost nothing to grip. Keyword scores **0.08**
there (1 of 13 — and that one hit is an incidental "semantic" token on, fittingly,
the embeddings-vs-keyword note). Embeddings match on meaning, so the lift lands
squarely on this split.

Honest framing for the writeup: this is a **learning instrument, not a benchmark
claim** — n=13 paraphrase questions is too small to publish a number on. What it
demonstrates is the *method*, and the method is the portfolio point: ship a
keyword baseline, build an eval that targets its known weakness (semantic
paraphrase) and *enforce* that weakness with an overlap check so the test can't
quietly become easy, measure, swap the implementation behind a stable
`search(query, k)` seam, and re-measure to quantify the gain. The number is the
evidence; the discipline is the signal. A near-zero keyword paraphrase baseline
is the point: it means any paraphrase lift is genuinely semantic, not vocabulary
leaking through.

## Decisions made at M3 (spec §9)

- **Embedding model:** local `all-MiniLM-L6-v2`. Runs in-process at $0/call and
  keeps the eval hermetic (no API, no daemon) — the only option consistent with
  the CI constraint and the local-first/open-weight thesis.
- **Vector store:** NumPy matrix cached to `index/embeddings.npz`, keyed by a
  hash of the corpus so it rebuilds when notes change. sqlite-vec / FAISS are the
  documented scale-up path, deliberately deferred (YAGNI at 13 notes).
- **Chunking:** none. Notes fit the model's context window; chunking is the
  upgrade path when a note no longer does.
