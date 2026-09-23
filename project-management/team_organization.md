# Team Organization

## Role split

The project was split along clear module boundaries, agreed early so both teammates could work in parallel with a well-defined
interface between the two halves.

**Teammate A — ylamaoui**
- Maze rendering,autotiling, hub-and-arm wall drawing, centering/scaling.
- Pacman mouvements, rendering, collision and eating behaviour.
- Ghosts mouvements, rendering and behaviour handling based on state.
- Readme and project management.

**Teammate B — zael-has**
- Maze adaptation and sprites loading.
- Game engine, main loop, and state management.
- Level progression and configuration wiring.
- Score, lives, timer tracking and highscore persistence.
- Menus, pause screen, instructions and banners.
- Cheat mode and package management.

## How decisions were made

Interface boundaries between the two halves (e.g., what data `Renderer`/`Pacman`/`Ghost` expose vs. what the game engine
owns and calls) were discussed and agreed before implementation began, so that each side could build independently against
a known contract — for example, `Pacman.eat()` returns the score value earned rather than mutating a score variable
directly, letting the game engine remain the single owner of `score`.

## How issues were handled

When the two halves were merged, several integration bugs surfaced (see [`blocking_points.md`](./blocking_points.md))
— most notably duplicate calls to movement-update functions from both sides of the merge, which caused inconsistent
speed and phantom collisions. These were diagnosed by tracing the actual call sequence of the merged main loop line
by line, rather than guessing, and resolved by consolidating each responsibility (movement, eating, collision) to a
single call site.