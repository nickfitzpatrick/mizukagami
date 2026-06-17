---
id: 2026-06-11-rlhf-contract-notes
title: RLHF contract work observations
created: 2026-06-11T20:00:00
updated: 2026-06-11T20:00:00
tags: [rlhf, contract, ai]
---
Doing contract data labeling and preference ranking for model training. The
recurring lesson is that rubric clarity dominates label quality: ambiguous
instructions produce noisy, low-agreement labels no matter how skilled the
annotators are. Tightening the rubric with concrete positive and negative
examples raises inter-annotator agreement more than anything else. Relevant
to how I'd design eval criteria for my own projects.
