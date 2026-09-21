# Project Management

This directory documents how the team planned, tracked, and executed the Pac-Man project.

## Contents

- [`timeline.md`](./timeline.md) — development phases and rough sequencing
- [`team_organization.md`](./team_organization.md) — who worked on what, and how work was split
- [`technical_decisions.md`](./technical_decisions.md) — key technical choices and the reasoning behind them
- [`risk_analysis.md`](./risk_analysis.md) — anticipated risks and how they were mitigated
- [`test_plan.md`](./test_plan.md) — acceptance test plan and manual test results
- [`blocking_points.md`](./blocking_points.md) — significant bugs/blockers encountered and how they were resolved

## Summary

The project was split along natural module boundaries: one teammate owned the configuratiom, game engine/state machine, menus, 
highscores, and cheat mode; the other (this documentation's primary author) owned the maze renderer, sprite/animation system,
Pac-Man and ghost movement logic, collision detection, and ghost AI.

Development proceeded incrementally and was tested continuously rather than built all at once and debugged at the end — each
subsystem (maze rendering, then Pac-Man movement, then collision, then ghost AI, then frightened/eaten states) was built, visually 
verified, and hardened against edge cases before moving to the next, which is reflected in the timeline and blocking-points log.