import pygame
from ..maze.maze_adapter import Tile
from ..assets.assetmanager import GhostType
from typing import Tuple

class Renderer:
    def __init__(self, screen, asset_manager, grid):
        self.screen = screen
        self.assets = asset_manager
        self.grid = grid
        self.tile_size = asset_manager.tile_size
        self.spawn = Tuple[int, int]
        self.direction = None
        self.pac_size = self.tile_size
        self.counter = 0

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

    def _find_spawn(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == Tile.SPAWN:
                    self.spawn = (x * self.tile_size, y * self.tile_size)
                    return
        raise ValueError("No spawn tile found in maze")

    def _draw_maze(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                figure = self.assets.wall_tiles[0]
                cell = self.grid[y][x]
                ty = y * self.tile_size
                tx = x * self.tile_size
                if cell == Tile.WALL:
                    mask = self._get_mask(x, y, self.grid)
                    figure = pygame.transform.scale(self.assets.wall_tiles[mask], (self.tile_size, self.tile_size))
                elif cell == Tile.PACGUM:
                    figure = pygame.transform.scale(self.assets.pacgum, (self.tile_size, self.tile_size))
                elif cell == Tile.SUPER_PACGUM:
                    figure = pygame.transform.scale(self.assets.super_pacgum, (self.tile_size, self.tile_size))
                else:
                    continue
                self.screen.blit(figure, (tx, ty))
    
    def _draw_pacman(self):
        angle = self._get_rotation(self.direction) if self.direction else 0
        rotated = pygame.transform.rotate(self.assets.pacman[self.counter % 4], angle)
        self.counter += 1
        pacman_sprite = pygame.transform.scale(rotated, (self.tile_size, self.tile_size))
        x,y = self.spawn
        # print(x, y)
        self.screen.blit(pacman_sprite, (x, y))
    
    def _set_pacmouvements(self, key):
        if key == pygame.K_UP:
            self.direction = (0, -1)
        elif key == pygame.K_DOWN:
            self.direction = (0, +1)
        elif key == pygame.K_LEFT:
            self.direction = (-1, 0)
        elif key == pygame.K_RIGHT:
            self.direction = (+1, 0)
    
    def _update_pacposition(self):
        if self.direction is None:
            return
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
    
    def _get_corners(self):
        h = len(self.grid)
        w = len(self.grid[0])
        t = self.tile_size
        corners = [(t, t), ((w - 2) * t, t), (t, (h - 2) * t), ((w - 2) * t, (h - 2) * t)]
        return corners
    
    def _get_rotation(self, direction):
        if direction == (1, 0):   # limen
            return 0
        elif direction == (0, -1):  # lfo9
            return 90
        elif direction == (-1, 0):  # lisser
            return 180
        elif direction == (0, 1):   # lte7t
            return 270
        return 0
    
    def _draw_ghosts(self):
        corners = self._get_corners()
        ghosts = self.assets.ghosts
        ghost_lst = [ghosts[GhostType.RED], ghosts[GhostType.BLUE], ghosts[GhostType.PINK], ghosts[GhostType.ORANGE]]
        for i in range(4):
            scaled_ghosts = pygame.transform.scale(ghost_lst[i][1], (self.tile_size, self.tile_size))
            scaled_eyes = pygame.transform.scale(self.assets.ghost_eyes, (self.tile_size, self.tile_size))
            self.screen.blit(scaled_ghosts, corners[i])
            self.screen.blit(scaled_eyes, corners[i])
