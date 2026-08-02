from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.renderer.renderer import Renderer
from src.assets.assetmanager import AssetManager, GhostType
from src.maze.maze_adapter import MazeAdapter
from src.characters.player import PacMan
from src.characters.ghost import Ghost
import sys
import pygame

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)
adapter = MazeAdapter(15, 15, 1)
grid = adapter.load()
pygame.display.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 650), pygame.SCALED)
pygame.display.set_caption("Pac-Man")
rows = len(grid)
cols = len(grid[0])
width, height = screen.get_size()
tile_size = min(width // cols, height // rows)
assets = AssetManager(tile_size)
assets.load()
render = Renderer(screen, assets, grid, adapter.spawn)

ghost_type = [GhostType.RED, GhostType.BLUE, GhostType.ORANGE, GhostType.PINK]
ghosts = []
for i in range(4):
    x, y = adapter.corners[i]
    ghosts.append(Ghost(x, y, ghost_type[i], adapter.corners[i], grid))

player = PacMan(render.spawn[0], render.spawn[1])

try:
    render._find_spawn()
except Exception as e:
    print(e)
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            player._set_pacmouvements(event.key)
    for ghost in ghosts:
        ghost.move(grid, (player.x, player.y), player.direction)
    player.move(grid)
    screen.fill("black")
    render._draw_maze()
    render._draw_pacman(player)
    render._draw_ghosts(ghosts)
    clock.tick(60)
    pygame.display.flip()


print("end")