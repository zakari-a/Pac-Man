from ..maze.maze_adapter import Tile
from typing import Tuple
import pygame

class Pacman:
    def __init__(self, tilesize, grid):
        self.grid = grid
        self.direction = None
        self.next_direction = None
        self.tile_size = tilesize
        self.pac_size = self.tile_size
        self.spawn = Tuple[int, int]

    def _find_spawn(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == Tile.SPAWN:
                    self.spawn = (x * self.tile_size, y * self.tile_size)
                    return
        raise ValueError("No spawn tile found in maze")
    
    def _update_pacposition(self):
        if self.direction is None and self.next_direction is None:
            return
        x, y = self.spawn
        if (x % self.tile_size == 0 and y % self.tile_size == 0):
            nx, ny = self.next_direction
            tx = (x + nx * self.tile_size) // self.tile_size
            ty = (y + ny * self.tile_size) // self.tile_size
            if self.grid[ty][tx] != Tile.WALL:
                self.direction = self.next_direction
        dx, dy = self.direction
        x, y = self.spawn
        nx = x + dx
        ny = y + dy
        size = self.pac_size
        corners = [(nx, ny), (nx + size - 1, ny), (nx, ny + size - 1), (nx + size - 1, ny + size - 1)]
        for cx, cy in corners:
            if self.grid[cy // self.tile_size][cx // self.tile_size] == Tile.WALL:
                return
        self.spawn = (nx, ny)
    
    def _set_pacmouvements(self, key):
        if key == pygame.K_UP:
            self.next_direction = (0, -1)
        elif key == pygame.K_DOWN:
            self.next_direction = (0, +1)
        elif key == pygame.K_LEFT:
            self.next_direction = (-1, 0)
        elif key == pygame.K_RIGHT:
            self.next_direction = (+1, 0)
    
    def eat(self):
        x, y = self.spawn
        gx = x // self.tile_size
        gy = y // self.tile_size
        char = self.grid[gy][gx]
        if char in [Tile.PACGUM, Tile.SUPER_PACGUM]:
            self.grid[gy][gx] = Tile.EMPTY

class Ghosts:
    def __init__(self, grid, tilesize):
        self.tile_size = tilesize
        self.grid = grid

    def _get_corners(self):
        h = len(self.grid)
        w = len(self.grid[0])
        t = self.tile_size
        corners = [(t, t), ((w - 2) * t, t), (t, (h - 2) * t), ((w - 2) * t, (h - 2) * t)]
        return corners