# Retrieval eval: keyword vs. embeddings (M3)

The point of M3 is not "add embeddings" — it is **measure what embeddings buy
you** on this corpus, honestly. This doc records the before/after.

## Setup

- **Corpus:** 13 markdown notes (`notes/`), the real working notes used through M1–M2.
- **Eval set:** 18 questions (`eval/eval_set.json`), each labeled with the note
  id(s) that *should* be retrieved. Split by `kind`:
  - `direct` (n=10): question shares vocabulary with the target note.
  - `paraphrase` (n=8): question is deliberately reworded to avoid the target's
    words. These are the ones keyword search is expected to miss.
- **Metric:** `hit_rate@k` — fraction of questions where at least one expected
  note appears in the top-k. Reported at **k=1** (the hardest, most honest
  setting: did the single best result get it right?).
- **Stage 1 (keyword):** token-overlap scoring, title weighted 2x.
- **Stage 2 (embeddings):** `all-MiniLM-L6-v2` (sentence-transformers), notes and
  query encoded to unit vectors, ranked by cosine (dot product). Brute-force over
  the whole corpus — at 13 notes a vector DB would be premature.

Both stages are scored by the *same* harness calling the *same* `search(query, k)`
signature; only the implementation behind it changes. Run:

```bash
python eval/run_eval.py --k 1
```

## Results

> NOTE: the keyword row is measured (in CI and locally). The embeddings row is
> produced by running `python eval/run_eval.py --k 1` on a machine with a working
> torch/sentence-transformers install (the CI/dev sandbox cannot install torch).
> Paste the harness output here and replace the `TBD` cells.

| hit_rate@1 | keyword | embeddings | delta |
|------------|:-------:|:----------:|:-----:|
| overall (n=18)    | 0.89 | TBD | TBD |
| direct (n=10)     | 1.00 | TBD | TBD |
| paraphrase (n=8)  | 0.75 | TBD | TBD |

## Reading the result

The headline is the **paraphrase split**, not the overall number. Keyword search
already does well on `direct` questions (it has the words). Where it structurally
cannot win is `paraphrase`: "stop the moss enclosure from staying soggy at the
roots" shares almost no tokens with a note titled *vivarium drainage layer*, yet
they mean the same thing. Embeddings match on meaning, so the lift should
concentrate there.

A caveat worth stating plainly (it is itself an interview point): the keyword
paraphrase baseline is already 0.75, because some paraphrases leak incidental
shared tokens. So the available headroom on this small set is modest. The eval is
a **learning instrument, not a benchmark claim** — n=8 paraphrase questions is too
small to publish a number on. What it demonstrates is the *method*: ship a
baseline, build an eval that targets the baseline's known weakness, measure, then
swap the implementation behind a stable seam and re-measure.

## Decisions made at M3 (spec §9)

- **Embedding model:** local `all-MiniLM-L6-v2`. Runs in-process at $0/call and
  keeps the eval hermetic (no API, no daemon) — the only option consistent with
  the CI constraint and the local-first/open-weight thesis.
- **Vector store:** NumPy matrix cached to `index/embeddings.npz`, keyed by a
  hash of the corpus so it rebuilds when notes change. sqlite-vec / FAISS are the
  documented scale-up path, deliberately deferred (YAGNI at 13 notes).
- **Chunking:** none. Notes fit the model's context window; chunking is the
  upgrade path when a note no longer does.
