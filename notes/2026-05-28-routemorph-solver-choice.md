---
id: 2026-05-28-routemorph-solver-choice
title: RouteMorph solver choice
created: 2026-05-28T15:30:00
updated: 2026-05-28T15:30:00
tags: [routemorph, optimization, capstone]
---
For the last-mile vehicle routing problem we're using a metaheuristic rather
than exact MILP, because the instance sizes (50-200 stops, multiple vehicles,
time windows) make exact solvers too slow for interactive use. Leaning toward
an adaptive large neighborhood search. The tradeoff is no optimality
guarantee, but we get good solutions fast enough for the dispatcher to
iterate in real time.
