from src.config.config import Config, ConfigFileError
from src.config.paths import resource_path
from src.game import Game
import sys


try:
    configs = Config()
    if len(sys.argv) != 2:
        raise ConfigFileError("The program needs only 1 arguments")

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        configs.load_config(resource_path("src/config/default_conf.json"))
    configs.load_config(sys.argv[1])

except (ConfigFileError, Exception) as e:
    print(e)
    sys.exit(1)

game = Game(configs)
game.run()