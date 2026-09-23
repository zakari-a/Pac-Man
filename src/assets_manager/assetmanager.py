import pygame
from enum import Enum
from src.config.paths import resource_path
import sys


class GhostType(Enum):
    """Enum representing the different types of ghosts in the game."""
    RED = 0
    BLUE = 1
    PINK = 2
    ORANGE = 3


class AssetManager():
    """Class responsible for loading and managing game
    assets such as images, sprites, and fonts."""
    def __init__(self, tile_size: int):
        """Initialize the AssetManager with the specified
        tile size and load all necessary assets."""
        self.wall_tiles: dict = {}

        self.pacman: list = []
        self.pacman_death: list = []

        self.ghosts: dict = {}
        self.scared_ghost: list = []
        self.ghost_eyes: pygame.Surface
        self.death_eyes: pygame.Surface

        self.pacgum: pygame.Surface
        self.super_pacgum: pygame.Surface
        self.tile_size: int = tile_size
        try:
            self.font_10 = pygame.font.Font(
                resource_path("assets/PressStart2P-Regular.ttf"), 10)
            self.font_15 = pygame.font.Font(
                resource_path("assets/PressStart2P-Regular.ttf"), 15)
            self.font_20 = pygame.font.Font(
                resource_path("assets/PressStart2P-Regular.ttf"), 20)
            self.font_35 = pygame.font.Font(
                resource_path("assets/PressStart2P-Regular.ttf"), 35)
            self.background1 = pygame.image.load(
                resource_path(
                    "assets/menu_backgroud.png")).convert_alpha()
            self.background2 = pygame.image.load(
                resource_path(
                    "assets/commands_background.jpeg")).convert_alpha()
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        self.victory: pygame.Surface
        self.game_over: pygame.Surface
        self.finish: pygame.Surface

    def _load_walls(self) -> None:
        """Load wall tile images from the spritesheet and
        store them in a dictionary."""
        try:
            spritesheet = pygame.image.load(
                resource_path("assets/wall_assets.png")).convert_alpha()
        except FileNotFoundError:
            print("Cant find 'wall_assets.png' in assets")
            sys.exit(1)
        bases = {
            "wall":       spritesheet.subsurface(
                pygame.Rect(64, 48, 16, 16)).copy(),
            "angle":      spritesheet.subsurface(
                pygame.Rect(48, 48, 16, 16)).copy(),
            "end_wall":   spritesheet.subsurface(
                pygame.Rect(176, 64, 16, 16)).copy(),
            "3_ways":     spritesheet.subsurface(
                pygame.Rect(208, 48, 16, 16)).copy(),
            "4_ways":     spritesheet.subsurface(
                pygame.Rect(144, 176, 16, 16)).copy(),
            "alone_wall": spritesheet.subsurface(
                pygame.Rect(128, 192, 16, 16)).copy(),
        }

        mask_map: dict[int, tuple[str, int]] = {
            0:  ("alone_wall", 0),
            1:  ("end_wall", 90),
            2:  ("end_wall", 0),
            3:  ("angle", 90),
            4:  ("end_wall", 270),
            5:  ("wall", 90),
            6:  ("angle", 0),
            7:  ("3_ways", 0),
            8:  ("end_wall", 180),
            9:  ("angle", 180),
            10: ("wall", 0),
            11: ("3_ways", 90),
            12: ("angle", 270),
            13: ("3_ways", 180),
            14: ("3_ways", 270),
            15: ("4_ways", 0),
        }

        small_size = self.tile_size // 2

        for mask, (img_key, angle) in mask_map.items():
            img = bases[img_key]
            if angle != 0:
                img = pygame.transform.rotate(img, angle)
            self.wall_tiles[mask] = pygame.transform.scale(
                img, (small_size, small_size)
            )

    def _load_pacman(self) -> None:
        """Load Pac-Man sprite frames and death animation frames
        from the spritesheet and store them in lists."""
        try:
            spritesheet = pygame.image.load(
                resource_path("assets/pacman_assets.png")).convert_alpha()
        except FileNotFoundError:
            print("Can't find 'pacman_assets.png' in assets")
            sys.exit(1)
        tmpr = []
        for i in range(4):
            frame = spritesheet.subsurface(
                pygame.Rect(i * 32, 0, 32, 32)).copy()
            d_frame = spritesheet.subsurface(
                pygame.Rect(i * 32, 32, 32, 32)).copy()
            if i != 3:
                tmp = spritesheet.subsurface(pygame.Rect(
                    i * 32, 64, 32, 32)).copy()
                tmpr.append(tmp)
            self.pacman.append(frame)
            self.pacman_death.append(d_frame)
        for _ in tmpr:
            self.pacman_death.append(_)

    def _load_ghosts(self) -> None:
        """Load ghost sprite frames, scared ghost frames, and ghost eyes
        from the spritesheet and store them in appropriate data structures."""
        try:
            spritesheet = pygame.image.load(
                resource_path("assets/ghosts_assets.png")).convert_alpha()
        except FileNotFoundError:
            print("Can't find 'ghosts_assets.png' in assets")
            sys.exit(1)

        types = [
            GhostType.RED, GhostType.BLUE, GhostType.PINK, GhostType.ORANGE]
        for row_idx, ghost_type in enumerate(types):
            frames = []
            for col in range(4):
                frames.append(
                    spritesheet.subsurface(
                        pygame.Rect(col * 32, row_idx * 32, 32, 32)).copy())
            self.ghosts[ghost_type] = frames

        for row in range(8, 10):
            for col in range(4):
                self.scared_ghost.append(spritesheet.subsurface(
                    pygame.Rect(col * 32, row * 32, 32, 32)).copy())

        self.ghost_eyes = spritesheet.subsurface(
            pygame.Rect(0, 320, 16, 16)).copy()

    def _load_items(self) -> None:
        """Load item images such as pacgum and super pacgum
        from the spritesheet and store them in appropriate attributes."""
        try:
            spritesheet = pygame.image.load(
                resource_path("assets/items_assets.png")).convert_alpha()
        except FileNotFoundError:
            print("Can't find 'items_assets.png' in assets")
            sys.exit(1)
        self.pacgum = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(0, 16, 16, 16)).copy()
        )
        self.super_pacgum = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(16, 16, 16, 16)).copy()
        )

    def _load_images(self) -> None:
        """Load additional images such as victory, game over,
        and finish banners from the spritesheet."""
        try:
            spritesheet = pygame.image.load(
                resource_path("assets/victory_banner.png")).convert_alpha()
            self.victory = spritesheet.subsurface(
                pygame.Rect(pygame.Rect(40, 325, 1450, 345)).copy()
                )
            spritesheet = pygame.image.load(
                resource_path("assets/banners.png")).convert_alpha()
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        self.game_over = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(80, 140, 1380, 340)).copy()
            )
        self.finish = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(80, 560, 1380, 340)).copy()
            )

    def load(self) -> None:
        """Load all necessary game assets."""
        self._load_walls()
        self._load_pacman()
        self._load_ghosts()
        self._load_items()
        self._load_images()
