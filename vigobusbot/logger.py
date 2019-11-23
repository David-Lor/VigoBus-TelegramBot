"""LOGGER
Logger instance
"""

# # Native # #
import sys
import logging

# # Installed # #
from loguru import logger

# # Package # #
from .settings_handler import system_settings as settings

__all__ = ("logger",)

# Disable default aiogram logger
logging.getLogger("aiogram").disabled = True

logger.remove()
logger.add(sys.stderr, level=settings.log_level.upper())
