from mazegenerator.mazegenerator import MazeGenerator
from enum import Enum
from typing import List


class Tile(Enum):
    WALL = 0
    EMPTY = 1
    PACGUM = 2
    SUPER_PACGUM = 3
    SPAWN = 4


class MazeAdapter():
    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width = width
        self.height = height
        self._generator = MazeGenerator(
            (width, height),
            False,
            (1, 1),
            (width, height),
            seed,
        )
        self.grid: List[List[Tile]] = []

    def load(self) -> List[List[Tile]]:
        adj_h = self.height * 2 + 1
        adj_w = self.width * 2 + 1
        self.grid = [[Tile.WALL for _ in range(adj_w)] for _ in range(adj_h)]
        raw_maze = self._generator._maze

        for y in range(self.height):
            for x in range(self.width):
                val = raw_maze[y][x]
                cy = y * 2 + 1
                cx = x * 2 + 1

                if val == 15:
                    self.grid[cy][cx] = Tile.EMPTY
                    continue

                self.grid[cy][cx] = Tile.PACGUM

                if not (val & 1):
                    self.grid[cy - 1][cx] = Tile.PACGUM
                if not (val & 2):
                    self.grid[cy][cx + 1] = Tile.PACGUM
                if not (val & 4):
                    self.grid[cy + 1][cx] = Tile.PACGUM
                if not (val & 8):
                    self.grid[cy][cx - 1] = Tile.PACGUM

        corners = [
            (1, 1),
            (1, adj_w - 2),
            (adj_h - 2, 1),
            (adj_h - 2, adj_w - 2),
        ]
        for ry, rx in corners:
            self.grid[ry][rx] = Tile.SUPER_PACGUM

        mid_y = (self.height // 2) * 2 + 1
        mid_x = (self.width // 2) * 2 + 1 if self.width % 2 == 1 \
            else (self.width // 2) * 2 - 1
        self.grid[mid_y][mid_x] = Tile.SPAWN

        return self.grid
