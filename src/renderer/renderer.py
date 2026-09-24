import pygame
from src.maze.maze_adapter import Tile
from src.entities.entities import Pacman, Ghost
from src.assets_manager.assetmanager import AssetManager
from typing import Any


class Renderer:
    """
    A class to handle the rendering of the game elements on the screen.
    """
    def __init__(self, screen: pygame.Surface,
                 assets: AssetManager, grid: list[list[Tile]]):
        """Initializes the Renderer with the screen, assets, and grid.
        Args:
            screen (pygame.Surface): The surface to render on.
            assets (AssetManager): The asset manager containing game assets.
            grid (list[list[Tile]]): The grid representing the maze layout.
        Returns:
            None
        """
        self.screen = screen
        self.grid = grid
        self.tile_size = assets.tile_size
        self.font = pygame.font.SysFont(None, 28)
        self.assets = assets
        self.p_counter = 0
        self.offset_x = 0
        self.offset_y = 0
        self.mod = len(self.assets.pacman)

    def _set_offset(self) -> None:
        """Calculates and sets the offset for centering the maze on the screen.
        Args:
            None
        Returns:
            None
        """
        width = len(self.grid[0]) * self.tile_size
        height = len(self.grid) * self.tile_size
        screen_w, screen_h = self.screen.get_size()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.offset_x = x
        self.offset_y = y

    def _get_mask(self, x: int, y: int, grid: list[list[Tile]]) -> int:
        """Calculates the mask for a wall tile based on its neighboring tiles.
        Args:
            x (int): The x-coordinate of the tile.
            y (int): The y-coordinate of the tile.
            grid (list[list[Tile]]): The grid representing the maze layout.
        Returns:
            int: The mask for the wall tile.
        """
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

    def _draw_maze(self) -> None:
        """Draws the maze on the screen based on the grid layout.
        Args:
            None
        Returns:
            None
        """
        half = self.tile_size // 2
        center_offset = half // 2
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                py = y * self.tile_size + self.offset_y
                px = x * self.tile_size + self.offset_x
                tx = px + center_offset
                ty = py + center_offset
                if cell == Tile.WALL:
                    mask = self._get_mask(x, y, self.grid)
                    self.screen.blit(self.assets.wall_tiles[mask], (tx, ty))
                    if mask & 1:
                        self.screen.blit(
                            self.assets.wall_tiles[5], (tx, ty - half))
                    if mask & 2:
                        self.screen.blit(
                            self.assets.wall_tiles[10], (tx + half, ty))
                    if mask & 4:
                        self.screen.blit(
                            self.assets.wall_tiles[5], (tx, ty + half))
                    if mask & 8:
                        self.screen.blit(
                            self.assets.wall_tiles[10], (tx - half, ty))
                elif cell == Tile.PACGUM:
                    figure = pygame.transform.scale(
                        self.assets.pacgum, (half, half))
                    self.screen.blit(figure, (tx, ty))

                elif cell == Tile.SUPER_PACGUM:
                    figure = pygame.transform.scale(
                        self.assets.super_pacgum, (half, half))
                    self.screen.blit(figure, (tx, ty))
                else:
                    continue

    def _draw_pacman(self, pacman: Pacman) -> None:
        """Draws Pacman on the screen based on its current state and direction.
        Args:
            pacman (Pacman): The pacman entity.
        Returns:
            None
        """
        move = pacman._move_frame()
        if move:
            pacman.counter += 1
        angle = self._get_rotation(
            pacman.direction) if pacman.direction else 0
        rotated = pygame.transform.rotate(
            pacman.state[pacman.counter % self.mod], angle)
        pacman_sprite = pygame.transform.scale(
            rotated, (self.tile_size, self.tile_size))
        x, y = pacman.position
        self.screen.blit(pacman_sprite, (x + self.offset_x, y + self.offset_y))

    def _draw_pacman_death(self, pacman: Pacman) -> None:
        """Draws Pacman's death animation on the screen.
        Args:
            pacman (Pacman): The pacman entity.
        Returns:
            None
        """
        pacman.counter = 0
        self.mod = len(self.assets.pacman_death)
        pacman.state = self.assets.pacman_death
        clock = pygame.time.Clock()
        start = pacman.death_start
        while pygame.time.get_ticks() - start < 1200:
            self.screen.fill("black")
            self._draw_maze()
            if pacman.counter < 6:
                self._draw_pacman(pacman)
            pygame.display.flip()
            clock.tick(60)

    # def _draw_game_over_screen(self) -> None:
    #     font = pygame.font.SysFont(None, 50)
    #     small_font = pygame.font.SysFont(None, 30)
    #     text = font.render("YOU DIED", True, "red")
    #     prompt = small_font.render(
    #         "Press R to Restart or Q to Quit", True, "white")
    #     w, h = self.screen.get_size()
    #     self.screen.blit(text, (w // 2 - text.get_width() // 2, h // 2 - 40))
    #     self.screen.blit(prompt, (w // 2 - prompt.get_width() // 2,
    #                               h // 2 + 20))

    def _get_rotation(self, direction: tuple[int, int]) -> int:
        """Returns the rotation angle based on the direction of movement.
        Args:
            direction (tuple[int, int]): The direction of movement.
        Returns:
            int: The rotation angle.
        """
        if direction == (1, 0):   # limen
            return 0
        elif direction == (0, -1):  # lfo9
            return 90
        elif direction == (-1, 0):  # lisser
            return 180
        elif direction == (0, 1):   # lte7t
            return 270
        return 0

    def _get_corners(self) -> list[tuple[int, int]]:
        """Returns the coordinates of the four corners of the maze.
        Args:
            None
        Returns:
            list[tuple[int, int]]: The coordinates of the four corners.
        """
        h = len(self.grid)
        w = len(self.grid[0])
        t = self.tile_size
        corners = [(t, t), ((w - 2) * t, t),
                   (t, (h - 2) * t), ((w - 2) * t, (h - 2) * t)]
        return corners

    def _draw_ghosts(self, ghosts: list[Ghost], pacman: Pacman,
                     red_pos: tuple[int, int], freeze: bool) -> None:
        """Draws the ghosts on the screen based
        on their current state and position.
        Args:
            ghosts (list[Ghost]): The list of ghost entities.
            pacman (Pacman): The pacman entity.
            red_pos (tuple[int, int]): The position of the red ghost.
            freeze (bool): Whether the game is frozen.
        Returns:
            None
        """
        eye_offset = self.tile_size // 4
        for ghost in ghosts:
            frightened = pacman.super and (ghost.was_dead == 0)
            if frightened:
                figures: Any = self.assets.scared_ghost
            else:
                figures = self.assets.ghosts
            if ghost.alive:
                ghost._update(pacman, red_pos)
                if freeze:
                    ghost._move_frame()
                else:
                    ghost._move()
                if not frightened:
                    scaled_ghosts = pygame.transform.scale(
                        figures[ghost.type][ghost.counter % 4],
                        (self.tile_size, self.tile_size))
                    scaled_eyes = pygame.transform.scale(
                        ghost.eyes, (self.tile_size // 2,
                                     self.tile_size // 2))
                else:
                    scaled_ghosts = pygame.transform.scale(
                        figures[ghost.counter % len(figures)],
                        (self.tile_size, self.tile_size))
                x, y = ghost.position
                self.screen.blit(scaled_ghosts, (x + self.offset_x,
                                                 y + self.offset_y))
                if not frightened:
                    self.screen.blit(scaled_eyes,
                                     (x + eye_offset + self.offset_x,
                                      y + eye_offset + self.offset_y))
