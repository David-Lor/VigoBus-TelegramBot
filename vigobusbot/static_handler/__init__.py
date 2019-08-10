"""STATIC HANDLER
Load static files from the 'static' path, such as the Messages file.
A filesystem watchdog is started to reload content from files if they change during execution.
"""

# # Package # #
from .watchdog import watchdog_start
from .exceptions import *
from .loader import *
from .files import *

__all__ = ("load_static_files", "FileException", "get_messages")


def load_static_files():
    """Start the loading process for the static files. This will load the files and start a watchdog that
    will reload files content if they change.
    This function must run before starting the bot. If a file cannot be loaded, an exception is raised and the
    bot execution shall stop.
    :raises: Any file-related exception present on FileException
    """
    load_messages()
    watchdog_start()
