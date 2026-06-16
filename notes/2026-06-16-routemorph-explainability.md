---
id: 2026-06-16-routemorph-explainability
title: RouteMorph explainability approach
created: 2026-06-16T10:00:00
updated: 2026-06-16T10:00:00
tags: [routemorph, xai]
---
RouteMorph needs to justify why it ordered stops the way it did. The plan is
to surface per-stop reasoning: time-window pressure, vehicle capacity, and
distance tradeoffs, expressed in plain language through the conversational
interface. The goal is an interpretable routing model, not a black box —
a dispatcher should be able to ask "why is this stop last?" and get an answer.
