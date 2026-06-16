"""Score retrieval against eval_set.json (spec §5).

Computes hit rate and recall@k for retrieval.search(). Run it once at
stage 1 (keyword) and again at stage 2 (embeddings) and compare.

Run: python run_eval.py [--k 5]
"""

# import json, sys
# sys.path.insert(0, "../backend")
# from retrieval import search
#
# def score(k=5):
#     data = json.load(open("eval_set.json"))
#     hits = 0
#     for item in data["items"]:
#         got = {h["note_id"] for h in search(item["question"], k)}
#         if set(item["expected_note_ids"]) & got:
#             hits += 1
#     n = len(data["items"])
#     print(f"hit_rate@{k}: {hits}/{n} = {hits/n:.2f}")

if __name__ == "__main__":
    print("eval runner — stub. Implement after M1 retrieval (M2).")
