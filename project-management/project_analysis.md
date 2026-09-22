# Project analysis and technical decisions

A record of the significant design choices made during development, and the reasoning behind each.

## Doubled-resolution maze grid

The external maze generator describes connectivity per cell (which sides are open), but rendering and collision logic need walls
to be their own distinct, individually addressable cells. We expand the generator's `width × height` grid into a `(2w+1) × (2h+1)`
grid, placing original cells on even coordinates and deriving wall/opening cells for the odd coordinates in between. This trades
a larger grid for much simpler downstream rendering and collision code — every grid cell is unambiguously one thing
(wall, floor, pacgum, spawn), with no combined per-cell state to interpret.

## Pixel-based movement instead of cell-based movement

Characters move in continuous pixel increments rather than jumping cell to cell, for smooth, arcade-accurate motion. This introduced a
real challenge: movement speed (pixels/frame) does not necessarily divide evenly into `tile_size`, meaning a naive per-frame step
could overshoot a grid line entirely, permanently breaking wall-aligned turning logic. We solved this with an "overshoot-and-snap"
technique: before moving, we compute the exact distance to the next grid line in the direction of travel, and clamp the step to
that distance if the configured speed would exceed it — guaranteeing exact alignment at any speed value, without needing speed to
be a clean divisor of `tile_size`.

## BFS pathfinding over straight-line-distance heuristic for ghost chasing

An initial implementation had ghosts greedily move toward whichever neighboring cell minimized straight-line (Euclidean) distance
to their target. This heuristic has no awareness of walls, and produced visible oscillation/confusion near obstacles, since a
wall-blocked direction can appear "closer" in a straight line while being much farther by any actual walkable path. We replaced
this with a breadth-first search over the maze grid from the target cell, giving every reachable cell an exact shortest-path
distance; a ghost then simply steps toward whichever neighbor has a strictly smaller recorded distance.

## One-time reversal allowance when a ghost becomes frightened

Excluding a ghost from ever reversing direction avoids oscillation while chasing a moving target (Pac-Man), but a ghost that
becomes frightened while facing away from its home corner may legitimately need to reverse once to head home efficiently.
We track a per-ghost flag that allows exactly one reversal at the moment a ghost becomes frightened, then disallows reversal
again for the rest of that frightened period — since BFS distance to a fixed target strictly decreases every subsequent
step, no further reversal is ever mathematically necessary once the first correction is made.

## AABB collision instead of same-grid-cell collision

An early collision check compared Pac-Man's and each ghost's current grid cell for equality. Because both move in multi-pixel jumps
per frame, it was possible for the two to visually cross paths within a single frame without either landing on the same grid cell on
any given frame, causing missed or seemingly incorrect collisions. We replaced this with an axis-aligned bounding box (AABB) overlap
test on real pixel coordinates, which detects any physical overlap regardless of grid alignment. Hitboxes are additionally shrunk and
re-centered relative to the full tile to better match the visible sprite, since the source art includes transparent padding within
each tile.