---
id: 2026-06-10-embeddings-vs-keyword
title: Why embeddings beat keyword search
created: 2026-06-10T09:00:00
updated: 2026-06-10T09:00:00
tags: [retrieval, embeddings]
---
Keyword search matches literal tokens, so it misses paraphrase: a query for
"explainability" won't find a note that says "interpretable model." Embeddings
map text to vectors that capture meaning, so semantically related text lands
near each other even with no shared words. This is why semantic retrieval is
the default for serious knowledge tools. Tradeoff: you need an embedding model
and a place to store vectors.
