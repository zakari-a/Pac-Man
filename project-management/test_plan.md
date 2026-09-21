# Acceptance Test Plan

Manual test plan covering the features owned by the renderer/entities module. Each was tested by playing the game directly and observing the described behavior across multiple maze sizes (smallest and largest configured levels).

| # | Feature | Test | Expected result | Result |
|---|---|---|---|---|
| 1 | Maze rendering | Load levels of different configured sizes | Maze renders fully connected, no gaps, no floating isolated wall fragments, centered in the window | Pass |
| 2 | Pac-Man movement | Hold each of the 4 directions in an open corridor | Smooth continuous movement, consistent speed across different maze/tile sizes | Pass |
| 3 | Pac-Man turning | Approach a junction and press a perpendicular direction slightly early | Turn is queued and executes as soon as physically possible, without requiring frame-perfect timing | Pass |
| 4 | Wall collision | Attempt to walk into a wall from all 4 directions | Movement stops cleanly at the wall edge, no clipping through | Pass |
| 5 | Pacgum eating | Walk over a pacgum / super-pacgum | Tile is cleared and disappears from render; score increases by the configured amount | Pass |
| 6 | Ghost movement | Observe ghosts over time in an open maze | Ghosts move continuously, respect walls, do not get stuck | Pass |
| 7 | Ghost chase behavior | Compare the 4 ghost types' movement relative to Pac-Man | Each ghost visibly targets a different point (direct, ahead, toggling, reflection-based) rather than all converging identically | Pass |
| 8 | Ghost pathing around obstacles | Position a wall between a ghost and Pac-Man | Ghost paths around it without oscillating/backtracking repeatedly | Pass |
| 9 | Pac-Man/ghost collision (normal) | Let a non-frightened ghost touch Pac-Man | Pac-Man dies, death animation plays, respawns at start position with a life lost | Pass |
| 10 | Super-pacgum power-up | Eat a super-pacgum | All active (non-eaten) ghosts switch to frightened sprite and flee away | Pass |
| 11 | Eating a frightened ghost | Touch a frightened ghost while powered up | Ghost is removed from play, score increases by the configured ghost value, ghost respawns at its corner after the cooldown period as a normal, dangerous ghost | Pass |
| 12 | Power-up expiry | Let the super-pacgum timer run out while ghosts are still frightened | Ghosts revert to normal chase behavior and become dangerous again | Pass |
| 13 | Collision fairness | Observe close near-misses between Pac-Man and a ghost | No death/eat registers unless the visible sprites actually overlap | Pass |
| 14 | HUD | Play through a level | Score, lives, level, and remaining time update live and match actual game state | Pass |
| 15 | Cheat: invincibility (F1) | Toggle F1, walk into a ghost | Pac-Man does not die or lose a life | Pass |
| 16 | Cheat: ghost freeze (F3) | Toggle F3 | All ghosts stop moving in place | Pass |
| 17 | Cheat: super speed (F5) | Toggle F5 | Pac-Man moves noticeably faster | Pass |
| 18 | Cheat: stop time (F6) | Toggle F6 | Level timer stops counting down | Pass |