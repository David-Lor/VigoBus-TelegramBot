"""LOGGER
Loggers initialization and self-utils
"""

import sys
import logging
import contextlib
from typing import Optional

from loguru import logger
# noinspection PyProtectedMember
from loguru._logger import context as loguru_context

from vigobusbot.settings_handler import system_settings as settings

__all__ = ("logger", "get_request_id", "get_request_verb")

LoggerFormat = "<green>{time:YY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "<level>{message}</level> | " \
               "{extra}"


def get_request_id() -> Optional[str]:
    """Return the current Request ID, if defined, being used by the logger"""
    with contextlib.suppress(Exception):
        context: dict = loguru_context.get()
        return context.get("request_id")


def get_request_verb() -> Optional[str]:
    """Return the current Request Verb, if defined, being used by the logger"""
    with contextlib.suppress(Exception):
        context: dict = loguru_context.get()
        return context.get("verb")


def _set_request_filter(is_request_logger: bool):
    """Set filter for virtual loggers, depending if the virtual logger is for request logs or system logs"""
    def record_filter(record: dict):
        record_is_request = record["extra"].get("request_id")
        return bool(record_is_request) == is_request_logger
    return record_filter


# Disable default aiogram & loguru loggers
logging.getLogger("aiogram").disabled = True
logger.remove()
if node_name := settings.node_name:
    logger = logger.bind(node=node_name)

# Create virtual loggers for system logs and request logs

# System logger
logger.add(
    sys.stderr,
    level=settings.log_level.upper(),
    filter=_set_request_filter(is_request_logger=False),
    format=LoggerFormat
)
# Request logger (print)
logger.add(
    sys.stderr,
    level=settings.request_logs_print_level.upper(),
    filter=_set_request_filter(is_request_logger=True),
    format=LoggerFormat
)
