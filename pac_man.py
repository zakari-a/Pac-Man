from src.config.config import Config, ConfigFileError
from src.game import Game
import sys


try:
    configs = Config()
    configs.load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)

game = Game(configs)
game.run()
