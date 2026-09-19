from src.config.config import Config, ConfigFileError
from src.config.paths import resource_path
from src.game import Game
import sys


try:
    configs = Config()
    if len(sys.argv) == 1:
        configs.load_config(resource_path("src/assets/default_conf.json"))
    else:
        configs.load_config(sys.argv[1])
except ConfigFileError as e:
    print(e)
    sys.exit(1)

game = Game(configs)
game.run()