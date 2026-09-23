*This project has been created as part of the 42 curriculum by ylamaoui, zael-has.*

## Description

This project is a full recreation of the classic 1980 arcade game **Pac-Man**, built in Python 
with `pygame`. The player navigates a generated maze, eating pacgums for points while avoiding 
four autonomous ghosts, each with a distinct chasing personality. Eating a super-pacgum 
temporarily turns the ghosts frightened and edible, letting the player eat them back for bonus 
points.

The goal of the project was not only to reproduce the original gameplay, but to do so with a 
clean, modular, testable architecture, robust error handling, and a genuine understanding of the 
algorithms involved (maze representation, tile-based movement, pathfinding, collision detection).

## Instructions

### Compilation
- `make install` — install dependencies
- `make run` — launch the game
- `make debug` — launch the game under `pdb`
- `make clean` — remove `__pycache__` and cache files
- `make lint` — run `flake8` and `mypy`

### Installation
```bash
make install
```

### Usage and Execution
You can use both:

```
make run
```

```bash
python3 pac-man.py config.json
```
The program takes exactly one argument: a path to a JSON configuration file. Any error in the 
config file (missing file, invalid values, missing keys) is handled gracefully with a clear 
message — the game will never crash with a raw traceback due to a bad config.

## Resources

- [Pygame documentation](https://www.pygame.org/docs/) — window/surface management, sprite blitting, input handling, timing.
- [Breadth-First Search overview](https://en.wikipedia.org/wiki/Breadth-first_search) — used as the basis for ghost pathfinding.
- Classic Pac-Man ghost AI write-ups (Blinky/Pinky/Inky/Clyde targeting behavior) — used as inspiration for the four ghost personalities.
- 42 `A-Maze-ing` project subject — interface used to generate the underlying maze.
- [Pac-Man Wiki](https://pacman.fandom.com/wiki/Pac-Man_Wiki) — reference for original game mechanics, scoring, and behavior.


### AI usage

- Correcting orthography, grammar, and syntax within the README documentation.
- Concept clarification.
- README structure improvement.

## Configuration

The configuration file is a JSON file that additionally supports `#`-prefixed comment lines, which are stripped before parsing.
Missing or invalid keys are replaced with safe defaults, unknown keys are ignored, and every case is logged — the game never 
crashes on a malformed config.

| Key | Description | Default |
|---|---|---|
| `highscore_filename` | File used to persist the highscore table | `highscores.json` |
| `lives` | Starting number of lives | `3` |
| `points_per_pacgum` | Score gained per pacgum eaten | `10` |
| `points_per_super_pacgum` | Score gained per super-pacgum eaten | `50` |
| `points_per_ghost` | Score gained per edible ghost eaten | `200` |
| `seed` | Seed used to generate the first level's maze | `42` |
| `level_max_time` | Time limit per level, in seconds | `90` |
| `levels` | List of `{width, height}` objects, one per level | 10 levels, 15×15 to 24×24 |

## Highscore

Highscores are stored persistently in a JSON file on disk (`highscores.json`), loaded once at game start and rewritten every 
time a new score is saved. The system keeps only the **top 10** entries, sorted by score descending, each storing a player 
name and score.
We chose a flat JSON file because the requirement is small in scope (10 entries, simple read/write), and JSON keeps the format 
human-readable and easly portable between machines without any external dependency. Player names are limited to 10 
alphanumeric/space characters and validated at entry time; scores are always non-negative integers since they can only increase
during gameplay.

## Maze Generation

The maze itself is produced by the assigned `A-Maze-ing` package, used exactly as provided and never modified. Our adapter 
(`MazeAdapter`) wraps its output and converts it into our own tile representation.

The generator's output represents each cell as a single value describing which of its 4 sides are open. Our renderer and gameplay
logic, however, need walls to be **their own addressable cells**, distinct from open floor, so that a wall can be looked up, drawn,
and collided with directly. To achieve this, the adapter expands the generator's `width × height` grid into a
`(2×width+1) × (2×height+1)` grid: original cells land on the even-numbered rows/columns, and the odd-numbered rows/columns in between 
become explicit wall-or-opening cells based on the generator's connectivity data.

If maze generation fails for any reason, the error is caught and reported cleanly rather than crashing the game.

## Implementation

At a high level, the game works in three layers that run every frame: state (what mode is the game in — menu, playing, paused, etc.), 
logic (where are things, did anything just happen), and rendering (draw the current state to the screen).

State and flow. The game uses a simple state machine (GameState) for menu, gameplay, pause, instructions, highscores, and
end screens. Each frame, Game checks the current state and lets that screen handle its own input and drawing. This keeps
things like menu navigation and in-game movement fully separate, and makes adding a new screen easy — just one more state,
one more handler.

Maze and level setup. Each level asks MazeAdapter to generate a maze using the external A-Maze-ing package, then converts
it into our own tile grid. The tile size is computed to fit that maze into the window, so the same code works for any maze size.

Movement. Pac-Man and the ghosts move in small pixel steps instead of jumping tile to tile, which makes motion feel smooth.
The catch: a character's speed doesn't always divide evenly into a tile's size, so a plain "move N pixels a frame" can overshoot
a turn. To fix this, every frame we check how close the character is to the next tile boundary, and shrink that frame's movement
if needed so it always lands exactly on the boundary, never past it. This keeps movement smooth at any speed while making sure
turns — which only work when a character is exactly grid-aligned — always get a clean moment to happen.

Ghost behavior. Ghosts find their way using pathfinding (breadth-first search) instead of just moving toward whatever looks
closest in a straight line, since a straight-line guess doesn't understand walls and gets confused near obstacles. The four
ghosts don't all target the same thing — one chases directly, one aims ahead of Pac-Man, one switches between chasing and
retreating, and one mirrors another ghost — so they spread out instead of clumping together. Eating a super-pacgum makes
ghosts flee away; eating one sends it home for a short cooldown before it goes back to being dangerous.

Collision. Instead of checking if Pac-Man and a ghost are in the same maze cell — which can miss real hits when both are
moving fast — we check if their actual on-screen boxes overlap, shrunk a bit to match the visible sprite rather than the
full tile. This makes hits feel accurate to what's actually on screen.

Rendering. Each wall isn't one big image per tile — it's a small piece centered in the tile, with thin connector pieces added
toward any neighboring wall. This avoids the visible double-border seam you'd get from two full bordered tiles sitting side by
side, so the maze looks like one connected structure instead of a grid of separate tiles.


## General Software Architecture

      ├── src/game.py (Game)  – owns the main loop and the current GameState
      ├── src/game_view/     – menu, pause, instructions, highscores, and banner screens
      ├── src/renderer/      – draws the maze, and in-game entities
      ├── src/assets/         – loads and slices sprite sheets into usable frames
      ├── src/maze/          – MazeAdapter: wraps the external maze generator
      ├── src/mazegenerator/  – the assigned, unmodified A-Maze-ing package
      ├── src/entities/      – Pacman and Ghost: position, movement, collision
      └── src/config/        – loads and validates the JSON configuration file


## Project Management

See the [`project-management/`](./project-management) directory for the team's timeline, technical decision log, risk analysis,
team organization, acceptance test plan, and a record of the main blocking points encountered during development.