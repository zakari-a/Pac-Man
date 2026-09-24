from dataclasses import dataclass
from typing import Any
import json


class ConfigFileError(Exception):
    """Custom exception for configuration file errors."""
    pass


@dataclass
class Level:
    """Class representing a game level with specified width and height."""
    width: int
    height: int


DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "seed": 42,
    "lives": 3,
    "pacgum": 42,
    "level_max_time": 90,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "levels":    [
        Level(width=5, height=5),
        Level(width=24, height=24),
        Level(width=18, height=18),
        Level(width=20, height=20),
        Level(width=23, height=23),
        Level(width=15, height=15),
        Level(width=19, height=19),
        Level(width=21, height=21),
        Level(width=17, height=17),
        Level(width=22, height=22)
    ]
}


POSITIVE_FIELDS = {
    "lives",
    "pacgum",
    "points_per_pacgum",
    "points_per_super_pacgum",
    "points_per_ghost",
    "level_max_time",
}


class Config:
    """Class responsible for loading and
    validating game configuration from a JSON file."""
    def __init__(self) -> None:
        """Initialize the Config class with default values."""
        self.highscore_filename: str = ""
        self.lives: int = 0
        self.pacgum: int = 0
        self.points_per_pacgum: int = 0
        self.points_per_super_pacgum: int = 0
        self.points_per_ghost: int = 0
        self.seed: int = 0
        self.level_max_time: int = 0
        self.levels: list[Level] = []

    def remove_comments(self, text: str) -> str:
        """Remove comments from the provided text."""
        clean: list[str] = []
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            elif line.lstrip().startswith("//"):
                continue
            elif line.lstrip().startswith("/*") \
                    and line.lstrip().endswith("*/"):
                continue
            clean.append(line)
        return "\n".join(clean)

    def load_json(self, filepath: str) -> dict[str, Any]:
        """Load and parse a JSON configuration file,
        removing comments and validating its structure."""
        if not filepath.lower().endswith('.json'):
            raise ConfigFileError(
                f"-Error: Config file should end with '.json': {filepath}")

        try:
            with open(filepath, "r") as file:
                text = file.read()
        except FileNotFoundError:
            raise ConfigFileError(
                f"-Error: Can't find the file provided: {filepath}")
        except PermissionError:
            raise ConfigFileError(
                "-Error: There is no permission to read the provided file")

        clean_text = self.remove_comments(text)
        try:
            configs: dict = json.loads(clean_text)
        except json.JSONDecodeError as e:
            raise ConfigFileError(f"-Error: invalid JSON in config ({e})")
        return configs

    def validate_levels(self, value: Any) -> list[Level] | None:
        """Validate the 'levels' configuration value,
        ensuring it is a list of Level objects."""
        if not isinstance(value, list) or not value:
            return None
        levels: list[Level] = []
        for item in value:
            if not isinstance(item, dict):
                return None
            w = item.get("width")
            h = item.get("height")
            if not isinstance(w, int) or not isinstance(h, int):
                return None
            if w < 5 or h < 5 or w > 30 or h > 30:
                return None
            levels.append(Level(width=w, height=h))
        return levels

    def load_config(self, filepath: str) -> None:
        """Load and validate the configuration from a JSON file,
        applying default values for missing or invalid entries."""
        data = self.load_json(filepath)
        for key, value in DEFAULT_CONFIG.items():
            if key not in data:
                print(f"-Can't find {key}, using default")
                data[key] = value

        valid: dict[str, Any] = data.copy()
        for key, value in data.items():
            if key not in DEFAULT_CONFIG:
                print(f"-Unknown configuration key '{key}', ignoring.")
                valid.pop(key)
                continue

            if key == "levels":
                levels = self.validate_levels(value)
                if levels is None:
                    print("-Warning : 'levels' are invalid, using default")
                    valid[key] = DEFAULT_CONFIG[key]
                    continue
                valid[key] = levels
                continue
            if key == "highscore_filename":
                if value.count(".") != 1 or not value.endswith(".json"):
                    print("-Warning : invalid highscore filename "
                          "(ex..'.json'), using default")
                    valid[key] = DEFAULT_CONFIG[key]
                    continue

            expected = type(DEFAULT_CONFIG[key])
            if type(value) is expected:
                if key in POSITIVE_FIELDS and expected is int and value <= 0:
                    print(f"-Warning: value for {key} "
                          "in invalid, using default")
                    valid[key] = DEFAULT_CONFIG[key]
                    continue
                valid[key] = value
            else:
                print(f"-Warning: invalid type for {key}, using default")
                valid[key] = DEFAULT_CONFIG[key]

        self.highscore_filename = valid["highscore_filename"]
        self.lives = valid["lives"]
        self.pacgum = valid["pacgum"]
        self.points_per_pacgum = valid["points_per_pacgum"]
        self.points_per_super_pacgum = valid["points_per_super_pacgum"]
        self.points_per_ghost = valid["points_per_ghost"]
        self.seed = valid["seed"]
        self.level_max_time = valid["level_max_time"]
        self.levels = valid["levels"]
