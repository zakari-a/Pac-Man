import pygame
from ..maze.maze_adapter import Tile
from ..assets.assetmanager import GhostType
from ..entities.entities import Pacman

class Renderer:
    def __init__(self, screen, assets, grid):
        self.screen = screen
        self.grid = grid
        self.tile_size = assets.tile_size
        self.font = pygame.font.SysFont(None, 28)
        self.assets = assets
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
    
    def _draw_pacman(self, pacman: Pacman):
        angle = self._get_rotation(pacman.direction) if pacman.direction else 0
        rotated = pygame.transform.rotate(self.assets.pacman[self.counter % 4], angle)
        self.counter += 1
        pacman_sprite = pygame.transform.scale(rotated, (self.tile_size, self.tile_size))
        x,y = pacman.spawn
        self.screen.blit(pacman_sprite, (x, y))
    
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
    
    def _draw_ghosts(self, ghost):
        corners = ghost._get_corners()
        ghosts = self.assets.ghosts
        ghost_lst = [ghosts[GhostType.RED], ghosts[GhostType.BLUE], ghosts[GhostType.PINK], ghosts[GhostType.ORANGE]]
        for i in range(4):
            scaled_ghosts = pygame.transform.scale(ghost_lst[i][1], (self.tile_size, self.tile_size))
            scaled_eyes = pygame.transform.scale(self.assets.ghost_eyes, (self.tile_size, self.tile_size))
            self.screen.blit(scaled_ghosts, corners[i])
            self.screen.blit(scaled_eyes, corners[i])
    
    def _draw_uhd(self):
        hud_text = f"Score: 0   Lives: 3   Level: 1   Time: 5s"
        surface = self.font.render(hud_text, True, (255,255,255))
        self.screen.blit(surface, (10, 10))