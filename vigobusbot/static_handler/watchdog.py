"""WATCHDOG
File watchdog, watching the static path for changes on files.
"""

# # Native # #
import atexit

# # Installed # #
import watchdog.observers
import watchdog.events

# # Project # #
from ..logger import *

# # Package # #
from .loader import load_messages, static_path
from .files import MESSAGES_FILENAME

__all__ = ("watchdog_start",)


class WatchdogHandler(watchdog.events.FileModifiedEvent):
    @staticmethod
    def dispatch(event: watchdog.events.FileModifiedEvent):
        filename = event.src_path.split("/")[-1]
        logger.debug(f"Static file Watchdog found change on file {filename}")

        if filename == MESSAGES_FILENAME:
            load_messages()


def watchdog_start():
    observer = watchdog.observers.Observer()
    observer.schedule(
        event_handler=WatchdogHandler,
        path=str(static_path),
        recursive=False
    )

    observer.start()
    atexit.register(observer.stop)
    logger.debug("Started static file watchdog")
