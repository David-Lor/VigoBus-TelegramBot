"""PATH LOADER
Path Loader to get the 'static' path, getting it from the settings or finding in parent directories
"""

# # Native # #
import pathlib

# # Project # #
from ..settings_handler import telegram_settings as settings

__all__ = ("get_static_path",)


# def get_static_path():
#     current_directory = os.getcwd()
#     static_directory = None
#
#     for _ in range(5):
#         if "static" in os.listdir(current_directory):
#             static_directory = os.path.join(current_directory, "static")
#             break
#         else:
#             current_directory = os.path.join(current_directory, "..")
#
#     if static_directory is None:
#         raise FileNotFoundError("Static path not found!")
#
#     return static_directory


def get_static_path() -> pathlib.Path:
    if settings.static_path is not None:
        return pathlib.Path(settings.static_path)

    current_path = pathlib.Path('.').absolute()
    static_path = None

    for _ in range(5):
        try:
            _static_path = next(current_path.glob("static"))
            if _static_path.is_dir():
                static_path = _static_path
                break
        except StopIteration:
            current_path = current_path.parent

    if static_path is None:
        raise FileNotFoundError("Static path not found!")

    return static_path
