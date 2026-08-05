import pygame
from enum import Enum


class GhostType(Enum):
    RED = 0
    BLUE = 1
    PINK = 2
    ORANGE = 3

class AssetManager():
    def __init__(self, tile_size):
        self.wall_tiles: dict[int, pygame.Surface] = {}

        self.pacman: list[pygame.Surface] = []
        self.pacman_death: list[pygame.Surface] = []

        self.ghosts: dict[GhostType, list[pygame.Surface]] = {}
        self.scared_ghost: list[list[pygame.Surface]] = []
        self.ghost_eyes: pygame.Surface
        self.death_eyes: pygame.Surface

        self.pacgum: pygame.Surface
        self.super_pacgum: pygame.Surface
        self.tile_size = tile_size

    def _load_walls(self) -> None:
        spritesheet = pygame.image.load("src/assets/wall_assets.png").convert_alpha()
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
        spritesheet = pygame.image.load("src/assets/pacman_assets.png").convert_alpha()
        tmpr = []
        for i in range(4):
            frame = spritesheet.subsurface(
                pygame.Rect(i * 32, 0, 32, 32)).copy()
            d_frame = spritesheet.subsurface(
                pygame.Rect(i * 32, 32, 32, 32)).copy()
            if i != 3:
                tmp = spritesheet.subsurface(
                pygame.Rect(i * 32, 64, 32, 32)).copy()
                tmpr.append(tmp)
            self.pacman.append(frame)
            self.pacman_death.append(d_frame)
        for _ in tmpr:
            self.pacman_death.append(_)

    def _load_ghosts(self) -> None:
        spritesheet = pygame.image.load("src/assets/ghosts_assets.png").convert_alpha()
        types = [GhostType.RED, GhostType.BLUE, GhostType.PINK, GhostType.ORANGE]
        for row_idx, row in enumerate(types):
            frames = []
            for col in range(4):
                frames.append(spritesheet.subsurface(
                pygame.Rect(col * 32, row_idx * 32, 32, 32)).copy())
            self.ghosts[row] = frames
        
        for row in range(8, 10):
            for col in range(4):
                self.scared_ghost.append(spritesheet.subsurface(
                    pygame.Rect(col * 32, row * 32, 32, 32)).copy())

        self.ghost_eyes = spritesheet.subsurface(
            pygame.Rect(0, 320, 16, 16)).copy()


    def _load_items(self) -> None:
        spritesheet = pygame.image.load("src/assets/items_assets.png")
        self.pacgum = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(0, 16, 16, 16)).copy()
        )
        self.super_pacgum = spritesheet.subsurface(
            pygame.Rect(pygame.Rect(16, 16, 16, 16)).copy()
        )

    def load(self) -> None:
        self._load_walls()
        self._load_pacman()
        self._load_ghosts()
        self._load_items()


if __name__=="__main__":
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode(
        (1280, 720), pygame.SCALED)
    pygame.display.set_caption("Pac-Man")

    assets = AssetManager(32)
    assets.load()
    print(assets.pacman)
    print(assets.pacman_death)
    print(assets.wall_tiles)
    print(assets.ghosts)
    print(assets.ghost_eyes)
    print(assets.scared_ghost)
    print(assets.pacgum)
    print(assets.super_pacgum)