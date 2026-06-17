---
id: 2026-05-20-routemorph-conversational-interface
title: RouteMorph conversational interface design
created: 2026-05-20T11:00:00
updated: 2026-05-20T11:00:00
tags: [routemorph, ux, capstone]
---
The dispatcher should be able to talk to RouteMorph in plain language: "why
is the Oakland stop before Berkeley?", "reroute around the bridge closure",
"which route has the most slack?". The interface translates these into
queries against the solver's state and returns answers grounded in the
actual optimization variables. This is the conversational layer on top of
the route optimizer, separate from the explainability reasoning itself.
