# Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Movement/collision bugs are hard to reproduce and diagnose (frame-timing-dependent) | High | Medium | Isolated and tested each movement/collision component individually with small, controlled mazes before integrating; traced bugs with concrete pixel-value examples rather than guessing |
| Ghost AI performance degrades on larger mazes (up to 24×24, ~49×49 in the doubled grid) | Low | Medium | Chose BFS over per-ghost repeated searches; BFS cost scales with reachable cell count, which remains small (low thousands) even at maximum configured maze size, and is cheap to run every frame |
| Straight-line-distance ghost AI produces visibly broken/confused behavior near walls | Medium (realized) | Medium | Replaced with BFS-based pathfinding, which is wall-aware by construction |
| Merging two independently developed modules (renderer/entities vs. game engine) introduces integration bugs | High (realized) | High | Reviewed the merged main loop call-by-call after integration; found and fixed duplicate movement/eating calls originating from both halves calling the same update logic |
| Speed/collision behavior not consistent across different configured maze sizes | Medium (realized) | Medium | Derived speed and collision margins as proportions of `tile_size` rather than fixed pixel constants |
| Packaging a pygame app for a public platform may break asset loading due to path differences in a bundled executable | Medium | High | Plan to test the PyInstaller build early, before the submission deadline, rather than only at the end |
| External maze generator package could fail or behave unexpectedly, since it is not our own code | Low | High | `MazeAdapter` wraps all interaction with the generator and handles failure cleanly rather than letting an exception propagate and crash the game |
| Config file could be malformed or incomplete | Medium | High (if unhandled) | Config loader clamps every field to a safe default individually, logs what was defaulted, and never raises an uncaught exception on bad input |