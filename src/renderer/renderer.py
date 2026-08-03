import pygame
from maze.maze_adapter import Tile
from entities.entities import Pacman

class Renderer:
    def __init__(self, screen, assets, grid):
        self.screen = screen
        self.grid = grid
        self.tile_size = assets.tile_size
        self.font = pygame.font.SysFont(None, 28)
        self.assets = assets
        self.p_counter = 0
        self.offset_x = 0
        self.offset_y = 0

    def _set_offset(self):
        width = len(self.grid[0]) * self.tile_size
        height = len(self.grid) * self.tile_size
        screen_w, screen_h = self.screen.get_size()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.offset_x = x
        self.offset_y = y

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

    def _draw_maze(self):
        half = self.tile_size // 2
        center_offset = half // 2
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                figure = self.assets.wall_tiles[0]
                cell = self.grid[y][x]
                py = y * self.tile_size + self.offset_y
                px = x * self.tile_size + self.offset_x
                tx = px + center_offset
                ty = py + center_offset
                if cell == Tile.WALL:
                    mask = self._get_mask(x, y, self.grid)
                    figure = pygame.transform.scale(self.assets.wall_tiles[mask], (half, half))
                    self.screen.blit(figure, (tx, ty))
                    if mask & 1:
                        self.screen.blit(self.assets.wall_tiles[5], (tx, ty - half))
                    if mask & 2:
                        self.screen.blit(self.assets.wall_tiles[10], (tx + half, ty))
                    if mask & 4:
                        self.screen.blit(self.assets.wall_tiles[5], (tx, ty + half))
                    if mask & 8:
                        self.screen.blit(self.assets.wall_tiles[10], (tx - half, ty))
                elif cell == Tile.PACGUM:
                    figure = pygame.transform.scale(self.assets.pacgum, (half, half))
                    self.screen.blit(figure, (tx, ty))
                elif cell == Tile.SUPER_PACGUM:
                    figure = pygame.transform.scale(self.assets.super_pacgum, (half, half))
                    self.screen.blit(figure, (tx, ty))
                else:
                    continue
    
    def _draw_pacman(self, pacman: Pacman, move):
        # move = pacman._move_frame()
        if move:
            pacman.counter += 1
        angle = self._get_rotation(pacman.direction) if pacman.direction else 0
        rotated = pygame.transform.rotate(self.assets.pacman[pacman.counter % 4], angle)
        pacman_sprite = pygame.transform.scale(rotated, (self.tile_size, self.tile_size))
        x,y = pacman.position
        self.screen.blit(pacman_sprite, (x + self.offset_x, y + self.offset_y))
    
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

    def _get_corners(self):
        h = len(self.grid)
        w = len(self.grid[0])
        t = self.tile_size
        corners = [(t, t), ((w - 2) * t, t), (t, (h - 2) * t), ((w - 2) * t, (h - 2) * t)]
        return corners

    def _draw_ghosts(self, ghost):
        eye_offset = self.tile_size // 4
        # for ghost in ghosts:
        # ghost._update()
        figures = self.assets.ghosts
        scaled_ghosts = pygame.transform.scale(figures[ghost.type][ghost.counter % 4], (self.tile_size, self.tile_size))
        scaled_eyes = pygame.transform.scale(self.assets.ghost_eyes, (self.tile_size // 2, self.tile_size // 2))
        x, y = ghost.position
        self.screen.blit(scaled_ghosts, (x + self.offset_x, y + self.offset_y))
        self.screen.blit(scaled_eyes, (x + eye_offset + self.offset_x, y + eye_offset + self.offset_y))
        
    def _draw_uhd(self):
        hud_text = f"Score: 0   Lives: 3   Level: 1   Time: 5s"
        surface = self.font.render(hud_text, True, (255,255,255))
        self.screen.blit(surface, (10 + self.offset_x, 10 + self.offset_y))

    def run(self, pacman, ghosts) -> None:
        self._draw_maze()
        move = pacman._move_frame()
        self._draw_pacman(pacman, move)
        for ghost in ghosts:
            ghost._update()
            self._draw_ghosts(ghost)