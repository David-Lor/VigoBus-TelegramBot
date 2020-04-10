"""LOGGER
Logger instance
"""

# # Native # #
import sys
import logging
import contextlib
from typing import Optional

# # Installed # #
from loguru import logger
# noinspection PyProtectedMember
from loguru._logger import context as loguru_context

# # Project # #
from vigobusbot.settings_handler import system_settings as settings

__all__ = ("logger", "get_request_id", "get_request_verb")

LoggerFormat = "<green>{time:YY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "{function}: <level>{message}</level> | " \
               "{extra}"


def get_request_id() -> Optional[str]:
    """Return the current Request ID, if defined, being used by the logger
    """
    with contextlib.suppress(Exception):
        context: dict = loguru_context.get()
        return context.get("request_id")


def get_request_verb() -> Optional[str]:
    """Return the current Request Verb, if defined, being used by the logger
    """
    with contextlib.suppress(Exception):
        context: dict = loguru_context.get()
        return context.get("verb")


# Disable default aiogram logger
logging.getLogger("aiogram").disabled = True

# Set custom logger
logger.remove()
logger.add(sys.stderr, level=settings.log_level.upper(), format=LoggerFormat)
