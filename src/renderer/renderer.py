import pygame
from ..maze.maze_adapter import Tile
from ..assets.assetmanager import GhostType
from ..characters.player import PacMan
from typing import Tuple

class Renderer:
    def __init__(self, screen, asset_manager, grid, spawn):
        self.screen = screen
        self.assets = asset_manager
        self.grid = grid
        self.tile_size = asset_manager.tile_size
        self.spawn = spawn
        self.direction = None
        self.pac_size = self.tile_size
        rows = len(grid)
        cols = len(grid[0])
        self.width, self.height = screen.get_size()
        self.offset_x = (self.width - (self.tile_size * cols)) // 2
        self.offset_y = (self.height - (self.tile_size * rows)) // 2


    def _get_mask(self, x: int, y: int, grid: list[list[Tile]]) -> int:
        max_y = len(grid) - 1
        max_x = len(grid[y]) - 1
        score = 0
        if y > 0 and grid[y - 1][x] == Tile.WALL:
            score += 1
        if y < max_y and grid[y + 1][x] == Tile.WALL:
            score += 4
        if x < max_x and grid[y][x + 1] == Tile.WALL:
            score += 2
        if x > 0 and grid[y][x - 1] == Tile.WALL:
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
        half_tile = self.tile_size // 2
        center_offset = (self.tile_size - half_tile) // 2
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                py = y * self.tile_size + self.offset_y
                px = x * self.tile_size + self.offset_x
                if cell == Tile.WALL:
                    mask = self._get_mask(x, y, self.grid)
                    tx = px + center_offset
                    ty = py + center_offset
                    self.screen.blit(
                        self.assets.wall_tiles[mask], (tx, ty)
                    )

                    if mask & 1:
                        self.screen.blit(
                            self.assets.wall_tiles[5], (tx, ty - half_tile)
                        )

                    if mask & 2:
                        self.screen.blit(
                            self.assets.wall_tiles[10], (tx + half_tile, ty)
                        )
                    if mask & 4:
                        self.screen.blit(
                            self.assets.wall_tiles[5], (tx, ty + half_tile)
                        )
                    if mask & 8:
                        self.screen.blit(
                            self.assets.wall_tiles[10], (tx - half_tile, ty)
                        )
                elif cell == Tile.PACGUM:
                    figure = pygame.transform.scale(self.assets.pacgum, (self.tile_size // 2, self.tile_size // 2))
                    self.screen.blit(figure, (px + center_offset, py + center_offset))
                elif cell == Tile.SUPER_PACGUM:
                    figure = pygame.transform.scale(self.assets.super_pacgum, (self.tile_size // 2, self.tile_size // 2))
                    self.screen.blit(figure, (px  + center_offset, py + center_offset))

                else:
                    continue
    
    def _draw_pacman(self, player: PacMan):
        player.update()
        frame = player.get_frame(self.assets.pacman)
        sprite = pygame.transform.scale(frame, (self.tile_size, self.tile_size))
        px = player.x * self.tile_size + self.offset_x
        py = player.y * self.tile_size + self.offset_y
        self.screen.blit(sprite, (px, py))

    
    def _get_corners(self):
        h = len(self.grid)
        w = len(self.grid[0])
        t = self.tile_size
        corners = [(t, t), ((w - 2) * t, t), (t, (h - 2) * t), ((w - 2) * t, (h - 2) * t)]
        return corners

    
    def _draw_ghosts(self, ghosts):
        half_tile = self.tile_size // 2
        center_offset = (self.tile_size - half_tile) // 2
        # corners = self._get_corners()
        ghosts_assets = self.assets.ghosts

        for i in range(4):
            ghosts[i].update()
            frame = ghosts[i].get_frame(ghosts_assets[ghosts[i].type])
            scaled_ghosts = pygame.transform.scale(frame, (self.tile_size, self.tile_size))
            scaled_eyes = pygame.transform.scale(self.assets.ghost_eyes, (half_tile, half_tile))
            x, y = ghosts[i].x, ghosts[i].y
            gx = x * self.tile_size + self.offset_x
            gy = y * self.tile_size + self.offset_y
            self.screen.blit(scaled_ghosts, (gx, gy))
            self.screen.blit(scaled_eyes, (gx + center_offset, gy + center_offset))
