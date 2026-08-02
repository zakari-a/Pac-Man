from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.renderer.renderer import Renderer
from src.assets.assetmanager import AssetManager, GhostType
from src.maze.maze_adapter import MazeAdapter
from src.entities.entities import Pacman, Ghost
import sys
import pygame

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)
adapter = MazeAdapter(5, 5, 1)
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
render = Renderer(screen, assets, grid)
render._set_offset()
pacman = Pacman(assets.tile_size, grid)
types = [GhostType.RED, GhostType.BLUE, GhostType.PINK, GhostType.ORANGE]
corners = render._get_corners()
ghosts = [Ghost(types[i], corners[i], grid, assets.tile_size) for i in range(len(types)) ]
try:
    pacman._find_spawn()
except Exception as e:
    print(e)
clock = pygame.time.Clock()
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
    # render._draw_uhd()
    clock.tick(60)
    pygame.display.flip()

print("end")