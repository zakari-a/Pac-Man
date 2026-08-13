from src.config.config import load_config
from src.config.custom_errors import ConfigFileError
from src.game import Game
import sys
import pygame

try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)

game = Game(configs)
game.run()
