"""PATH LOADER
Path Loader to get the 'static' path, getting it from the telegram_settings or finding in parent directories
"""

# # Native # #
import pathlib

# # Project # #
from vigobusbot.settings_handler import system_settings as settings
from vigobusbot.logger import logger

__all__ = ("get_static_path",)

STATIC_PATH_LEVEL_LIMIT = 5


def get_static_path() -> pathlib.Path:
    if settings.static_path is not None:
        static_path = pathlib.Path(settings.static_path)
        logger.debug(f"Static files path is {static_path}")
        return static_path

    current_path = pathlib.Path('.').absolute()
    static_path = None

    for _ in range(STATIC_PATH_LEVEL_LIMIT):
        try:
            _static_path = next(current_path.glob("static"))
            if _static_path.is_dir():
                static_path = _static_path
                break
        except StopIteration:
            current_path = current_path.parent

    if static_path is None:
        raise FileNotFoundError("Static path not found!")

    logger.debug(f"Found Static files path at {static_path}")
    return static_path
