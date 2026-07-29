from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.renderer.renderer import Renderer
from src.assets.assetmanager import AssetManager
from src.maze.maze_adapter import MazeAdapter
import sys
import pygame

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)
adapter = MazeAdapter(30, 20, 1)
grid = adapter.load()
pygame.display.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 650), pygame.SCALED)
pygame.display.set_caption("Pac-Man")
assets = AssetManager(32)
assets.load()
render = Renderer(screen, assets, grid)
running = True
while running:
    screen.fill("grey")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    render._draw_maze()
    pygame.display.flip()

print("end")