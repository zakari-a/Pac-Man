from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.renderer.renderer import Renderer
from src.assets.assetmanager import AssetManager, GhostType
from src.maze.maze_adapter import MazeAdapter
from src.entities.entities import Pacman, Ghost
import sys
import pygame
from enum import Enum

class GameState(Enum):
    PLAYING = 0
    DYING = 1
    GAME_OVER = 2

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)
adapter = MazeAdapter(15, 15, 1)
grid = adapter.load()
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 650), pygame.SCALED)
pygame.display.set_caption("Pac-Man")
rows = len(grid)
cols = len(grid[0])
width, height = screen.get_size()
tile_size = min(width // cols, height // rows)
assets = AssetManager(tile_size)
assets.load()
# print(assets.scared_ghost, len(assets.scared_ghost))
screen.fill("black")
state = GameState.PLAYING
render = Renderer(screen, assets, grid)
render._set_offset()
pacman = Pacman(assets.tile_size, grid, assets)
types = [GhostType.RED, GhostType.BLUE, GhostType.PINK, GhostType.ORANGE]
corners = render._get_corners()
ghosts = [Ghost(types[i], corners[i], grid, assets) for i in range(len(types)) ]
try:
    pacman._find_spawn()
except Exception as e:
    print(e)
clock = pygame.time.Clock()
running = True
rep_quit = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == GameState.PLAYING:
                pacman._set_pacmouvements(event.key)
            if event.key == pygame.K_r and rep_quit:
                state = GameState.PLAYING
                rep_quit = False
                render.mod = len(assets.pacman)
                for ghost in ghosts:
                    ghost._reset()
                pacman._reset()
            elif event.key == pygame.K_q and rep_quit:
                exit()
    screen.fill("black")
    if state != GameState.GAME_OVER:
        render._draw_maze()
    if state == GameState.PLAYING:
        collision, pos = pacman.check_collision(ghosts)
        if collision == 1:
            pacman.death_start = pygame.time.get_ticks()
            state = GameState.DYING
        elif collision == 2:
            found = None
            for ghost in ghosts:
                if ghost.position == pos:
                    found = ghost
            # print(found)
            if found:
                found.alive = False
                found.position = found.base_corner
                found.counter = 0
                found.was_dead = 1
                found.death_start = pygame.time.get_ticks()
        else:
            pacman._update_pacposition()
            pacman.eat(ghosts)
            pacman._go_normal()
        render._draw_pacman(pacman)
        render._draw_ghosts(ghosts, pacman, ghosts[0].position)
        # render._draw_uhd()    
    elif state == GameState.DYING:
        render._draw_pacman_death(pacman)
        state = GameState.GAME_OVER
    elif state == GameState.GAME_OVER:
        rep_quit = True
        render._draw_game_over_screen()
    clock.tick(60)
    pygame.display.flip()
print("end")