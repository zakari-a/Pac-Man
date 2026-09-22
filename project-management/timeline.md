# Timeline

Development proceeded in incremental phases, each one built and visually/functionally verified before moving to the next. Dates are indicative of sequencing rather than a rigid schedule, since the project was worked on iteratively alongside debugging.

| Phase | Scope | Status |
|---|---|---|
| 1. Setup | Repo structure, config loader with comment support and safe-default fallback, Makefile | Done |
| 2. Maze integration | `MazeAdapter` wrapping the external `A-Maze-ing` package, doubled-grid tile representation, isolated-wall cleanup | Done |
| 3. Renderer foundation | Wall autotiling via neighbor bitmask, hub-and-arm rendering to avoid border seams, maze centering/scaling to any maze size | Done |
| 4. Sprite loading | `AssetManager`: wall tiles, Pac-Man frames, ghost frames (per color), scared-ghost frames, eyes, pacgum/super-pacgum sprites | Done |
| 5. Pac-Man movement | Pixel-based movement, direction queueing, wall collision (4-corner check), grid-alignment-gated turning, frame-rate-independent speed scaling ("overshoot-and-snap") | Done |
| 6. Ghost movement (basic) | Static ghosts → random-walk movement with wall collision | Done |
| 7. Ghost AI (chase) | Straight-line-distance heuristic chasing (superseded), then BFS-based pathfinding for accurate wall-aware shortest-path targeting | Done |
| 8. Ghost personalities | Four distinct targeting behaviors (direct chase, ambush-ahead, distance-based toggle, reflection-based) | Done |
| 9. Collision & death | AABB collision detection (replacing same-cell checks), Pac-Man death/respawn, death animation | Done |
| 10. Frightened / eaten ghosts | Super-pacgum power-up state, frightened sprite/flee behavior, eating ghosts for points, eaten-ghost cooldown/respawn, one-time-reversal turning rule | Done |
| 11. HUD & UI screens | Score/lives/level/timer HUD, main menu, pause menu, instructions, game-over, victory, highscore entry screens | Done |
| 12. Integration | Merging the renderer/entities module with the teammate's game engine/state machine, resolving merge-introduced bugs (duplicate movement calls, speed regressions) | Done |
| 13. Documentation & packaging | README, project management docs, PyInstaller packaging, Itch.io/Steam unlisted deployment | Done |