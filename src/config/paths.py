import os
import sys


def resource_path(relative_path: str) -> str:
    """Return the absolute path to a bundled resource.

    Works both when running from source and when running as a
    PyInstaller --onefile frozen executable.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        base_path = meipass
        return os.path.join(base_path, relative_path)
    return relative_path


def highscore_path(filename: str) -> str:
    """Return the absolute path to the highscore file.

    Works both when running from source and when running as a
    PyInstaller --onefile frozen executable.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, filename)
    return filename
