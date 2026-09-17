from src.mazegenerator.mazegenerator import MazeGenerator
from enum import Enum
# from typing import List, Tuple, Set
import random


class Tile(Enum):
    WALL = 0
    EMPTY = 1
    PACGUM = 2
    SUPER_PACGUM = 3
    SPAWN = 4


class MazeAdapter():
    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width: int = width
        self.height: int = height
        self._generator: MazeGenerator = MazeGenerator(
            (width, height),
            False,
            (1, 1),
            (width, height),
            seed,
        )
        self.grid: list[list[Tile]] = []

    def _remove_pacgum(self, total_pacgums: int, empty_space: set) -> None:
        coords = list(empty_space)
        random.shuffle(coords)
        if total_pacgums > len(coords) - 1:
            total_pacgums = len(coords) - 1
        for i in range(total_pacgums):
            x, y = coords[i]
            if (self.grid[y][x] != Tile.SPAWN
                    and self.grid[y][x] != Tile.SUPER_PACGUM):
                self.grid[y][x] = Tile.PACGUM

    def load(self, total_pacgums: int) -> list[list[Tile]]:
        adj_h: int = self.height * 2 + 1
        adj_w: int = self.width * 2 + 1
        raw_maze: list[list[int]] = self._generator._maze
        empty_space: set[tuple[int, int]] = set()
        self.grid = [[Tile.WALL for _ in range(adj_w)] for _ in range(adj_h)]

        for y in range(self.height):
            for x in range(self.width):
                val = raw_maze[y][x]
                cy = y * 2 + 1
                cx = x * 2 + 1

                if val == 15:
                    self.grid[cy][cx] = Tile.EMPTY
                    continue

                self.grid[cy][cx] = Tile.EMPTY
                empty_space.add((cx, cy))
                if not (val & 1):
                    self.grid[cy - 1][cx] = Tile.EMPTY
                    empty_space.add((cx, cy - 1))
                if not (val & 2):
                    self.grid[cy][cx + 1] = Tile.EMPTY
                    empty_space.add((cx + 1, cy))
                if not (val & 4):
                    self.grid[cy + 1][cx] = Tile.EMPTY
                    empty_space.add((cx, cy + 1))
                if not (val & 8):
                    self.grid[cy][cx - 1] = Tile.EMPTY
                    empty_space.add((cx - 1, cy))

        corners: list[tuple[int, int]] = [
            (1, 1),
            (1, adj_w - 2),
            (adj_h - 2, 1),
            (adj_h - 2, adj_w - 2),
        ]
        for ry, rx in corners:
            self.grid[ry][rx] = Tile.SUPER_PACGUM

        mid_y: int = (self.height // 2) * 2 + 1
        mid_x: int = (self.width // 2) * 2 + 1 if self.width % 2 == 1 \
            else (self.width // 2) * 2 - 1
        self.grid[mid_y][mid_x] = Tile.SPAWN

        for corner in corners:
            empty_space.remove(corner)
        self._remove_pacgum(total_pacgums, set(empty_space))
        return self.grid
