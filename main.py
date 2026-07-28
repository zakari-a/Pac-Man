from src.config import load_config
from config.custom_errors import ConfigFileError
import sys


try:
    configs = load_config(sys.argv[-1])
except ConfigFileError as e:
    print(e)
    exit(1)

print(configs)