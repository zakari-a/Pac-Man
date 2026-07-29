import pygame
from ..maze.maze_adapter import Tile

class Renderer:
    def __init__(self, screen, asset_manager, grid):
        self.screen = screen
        self.assets = asset_manager
        self.grid = grid
        self.tile_size = asset_manager.tile_size // 2

    def _get_mask(self, x: int, y: int, grid: list[list[Tile]]) -> int:
        max_y = len(grid) - 1
        max_x = len(grid[y]) - 1
        score = 0
        if y > 0 and grid[y - 1][x] == Tile.WALL:
            score += 1
        elif y == 0:
            score += 1
        if y < max_y and grid[y + 1][x] == Tile.WALL:
            score += 4
        elif y == max_y:
            score += 4
        if x < max_x and grid[y][x + 1] == Tile.WALL:
            score += 2
        elif x == max_x:
            score += 2
        if x > 0 and grid[y][x - 1] == Tile.WALL:
            score += 8
        elif x == 0:
            score += 8
        return score

    def _draw_maze(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                figure = self.assets.wall_tiles[0]
                cell = self.grid[y][x]
                ty = y * self.tile_size
                tx = x * self.tile_size
                if cell == Tile.WALL:
                    mask = self._get_mask(x, y, self.grid)
                    figure = self.assets.wall_tiles[mask]
                elif cell == Tile.PACGUM:
                    figure = self.assets.pacgum
                elif cell == Tile.SUPER_PACGUM:
                    figure = self.assets.super_pacgum
                else:
                    continue
                self.screen.blit(figure, (tx, ty))
