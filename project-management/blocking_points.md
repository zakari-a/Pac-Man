# Blocking Points

Significant bugs and blockers encountered during development, and how they were resolved. Kept as an honest record rather than a polished summary, since several of these took multiple iterations to fully fix.

## Rendering

- **Maze appeared incomplete/gapped.** Traced to a coordinate swap in the tile-blit call (`(y, x)` instead of `(x, y)`), combined with a mismatch between the doubled-resolution grid's step size and the rendered sprite size (sprites scaled to half tile size, but the renderer stepping by the full tile size). Fixed by aligning the renderer's step size to the actual sprite scale.
- **Wall pieces showed a visible double-border seam** between adjacent tiles. Root cause: each full-size wall sprite has its own complete border baked into the art, so two adjacent full tiles produce two overlapping borders. Resolved by switching to a "hub and arm" rendering approach — small centered sprites per cell, with thin connector sprites bridging to wall-adjacent neighbors — reducing (not eliminating) border-on-border overlap.
- **Border/edge wall tiles rendered as incorrect shapes** (junction-like nubs instead of clean straight lines). Root cause: the neighbor-bitmask calculation treated the maze's outer boundary as an implicit wall, which was appropriate for the earlier full-tile rendering approach but incorrect for the hub-and-arm approach. Fixed by removing the "treat out-of-bounds as wall" logic once the rendering approach changed.

## Movement

- **Pac-Man could only move in one direction after a bugfix session** — traced to a distance-to-grid-line calculation that returned zero at the exact moment of alignment for two of the four directions (up/left), which incorrectly zeroed out movement speed at every tile boundary in those directions.
- **Movement speed was inconsistent across different maze sizes** — root-caused to speed being derived via integer floor division by a fixed constant, which collapsed to a hard minimum across a wide range of small tile sizes; replaced with `round()`-based scaling to distribute proportional speed more evenly.
- **Movement broke when using floating-point speed values** — grid-index lookups computed from float pixel positions raised type errors, and alignment checks using exact float equality were unreliable due to floating-point rounding. Fixed by explicitly casting to `int` at every pixel→grid-index conversion, and using a small tolerance instead of exact equality for alignment checks.
- **Ghosts oscillated back and forth at their home corner once frightened.** Root cause: once a ghost reaches its target (distance 0), every neighboring cell is farther away, so a naive "always move toward the smallest distance" rule causes it to step away and immediately step back, indefinitely. Fixed by explicitly detecting arrival (distance == 0) and falling back to undirected wandering instead of continuing to seek.

## Collision

- **Ghosts could kill Pac-Man without any visible overlap.** Root cause: collision hitboxes used the full tile size, which included transparent padding around the actual sprite art. Fixed by shrinking and re-centering both hitboxes relative to the visible sprite.
- **Ghosts sometimes passed through Pac-Man without triggering an eat/death event.** Root cause: collision was checked via same-grid-cell comparison, which can be skipped entirely if both characters' per-frame pixel jumps cause them to swap positions across a grid boundary within a single frame. Fixed by switching to pixel-level AABB overlap detection.

## Integration (merging the two team members' modules)

- **Pac-Man and ghosts moved at roughly double their intended speed, and collisions registered without visible contact.** Root cause: both the merged game engine and the pre-existing per-frame update logic independently called the movement-update function, resulting in two position updates per frame. Fixed by auditing the full per-frame call sequence and removing the duplicate calls.
- **Eating a pacgum sometimes had no visible effect on larger maps.** Root cause: two independent "eat" implementations existed after the merge (one in the game engine, one on the `Pacman` entity), checking the player's position at two different points in the frame due to the double-movement bug above, so they frequently disagreed about which cell was being checked. Consolidated into a single `Pacman.eat()` method called exactly once per frame.