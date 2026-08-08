from dataclasses import dataclass
from typing import Any
from .custom_errors import ConfigFileError
import json


@dataclass
class Level:
    width: int
    height: int


@dataclass
class Config:
    highscore_filename: str
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    levels: list[Level]

DEFAULT_CONFIG: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "seed": 42,
    "lives": 3,
    "level_max_time": 90,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "levels":    [
        Level(width=10, height=10),
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
    "points_per_pacgum",
    "points_per_super_pacgum",
    "points_per_ghost",
    "level_max_time",
}

def remove_comments(text: str) -> str:
    clean: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        clean.append(line)
    return "\n".join(clean)

def load_json(filepath: str) -> dict[str, Any]:
    if not filepath.lower().endswith('.json'):
        raise ConfigFileError(f"-Error: Config file should end with '.json': {filepath}")

    try:
        with open(filepath, "r") as file:
            text = file.read()
    except FileNotFoundError:
        raise ConfigFileError(f"-Error: Can't find the file provided: {filepath}")
    except PermissionError:
        raise ConfigFileError(f"-Error: The is no permission to read the provided file")
    
    clean_text = remove_comments(text)
    try:
        configs: dict = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ConfigFileError(f"-Error: invalid JSON in config ({e})")
    return configs


def validate_levels(value: Any) -> list[Level] | None:
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
        if w < 5 or h < 5 or w > 60 or h > 60:
            return None
        levels.append(Level(width=w, height=h))
    return levels


def load_config(filepath: str) -> Config:
    data = load_json(filepath)
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
            levels = validate_levels(value)
            if levels is None:
                print(f"-Warning : 'levels' are invalid, using default")
                valid[key] = DEFAULT_CONFIG[key]
                continue
            valid[key] = levels
            continue

        expected = type(DEFAULT_CONFIG[key])
        if type(value) is expected:
            if key in POSITIVE_FIELDS and expected is int and value <= 0:
                print(f"-Warning: value for {key} in invalid, using default")
                valid[key] = DEFAULT_CONFIG[key]
                continue
            valid[key] = value
        else:
            print(f"-Warning: invalid type for {key}, using default")
            valid[key] = DEFAULT_CONFIG[key]  

    return Config(
        highscore_filename=valid["highscore_filename"],
        lives=valid["lives"],
        points_per_pacgum=valid["points_per_pacgum"],
        points_per_super_pacgum=valid["points_per_super_pacgum"],
        points_per_ghost=valid["points_per_ghost"],
        seed=valid["seed"],
        level_max_time=valid["level_max_time"],
        levels=valid["levels"])
