from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.renderer.renderer import Renderer
from src.assets.assetmanager import AssetManager
from src.maze.maze_adapter import MazeAdapter
from src.entities.entities import Pacman, Ghosts
import sys
import pygame

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)
adapter = MazeAdapter(14, 10, 1)
grid = adapter.load()
pygame.display.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 650), pygame.SCALED)
pygame.display.set_caption("Pac-Man")
assets = AssetManager(32)
assets.load()
pacman = Pacman(assets.tile_size, grid)
ghosts = Ghosts(grid, assets.tile_size)
render = Renderer(screen, assets, grid)
try:
    pacman._find_spawn()
except Exception as e:
    print(e)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pacman._set_pacmouvements(event.key)
    pacman._update_pacposition()
    screen.fill("black")
    pacman.eat()
    render._draw_maze()
    render._draw_pacman(pacman)
    render._draw_ghosts(ghosts)
    render._draw_uhd()
    pygame.display.flip()

print("end")