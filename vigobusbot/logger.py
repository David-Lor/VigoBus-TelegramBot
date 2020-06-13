"""LOGGER
Loggers initialization and self-utils
"""

# # Native # #
import sys
import json
import logging
import contextlib
from typing import Optional

# # Installed # #
import cachetools
from loguru import logger
# noinspection PyProtectedMember
from loguru._logger import context as loguru_context

# # Project # #
from vigobusbot.repositories.logs import *
from vigobusbot.settings_handler import system_settings as settings

__all__ = ("logger", "get_request_id", "get_request_verb")

LoggerFormat = "<green>{time:YY-MM-DD HH:mm:ss}</green> | " \
               "<level>{level}</level> | " \
               "{function}: <level>{message}</level> | " \
               "{extra}"

_request_records = cachetools.TTLCache(maxsize=float("inf"), ttl=settings.request_logs_persist_record_timeout)
"""Local cache for the request records organized by request id: { request_id: record[] }"""


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


async def _request_record_handler(record: str):
    """Handler for any Request record received"""
    request_id = None

    # noinspection PyBroadException
    try:
        record = json.loads(record)["record"]
        request_id = record["extra"]["request_id"]

        with logger.contextualize(logs_request_id=request_id):
            try:
                _request_records[request_id].append(record)
            except KeyError:
                _request_records[request_id] = [record]

            # If this was last request record, pop from cache and persist if exceeds level
            if record["extra"].get("last_record"):
                records = _request_records.pop(request_id)
                logger.debug(f"Processing {len(records)} records for request")

                if any(
                        rec for rec in records
                        if rec["level"]["no"] >= logger.level(settings.request_logs_persist_level.upper()).no
                ):
                    logger.debug(f"Inserting {len(records)} request log records on Mongo")
                    result = await persist_records(request_id=request_id, records=records)
                    assert result.acknowledged

                else:
                    logger.debug("No records must be persisted from this request")

    except Exception:
        logger.opt(exception=True).bind(logs_request_id=request_id).error(
            "Could not insert request log records on Mongo"
        )


# Disable default aiogram & loguru loggers
logging.getLogger("aiogram").disabled = True
logger.remove()

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
# Request logger (persist)
if settings.request_logs_persist_enabled:
    logger.add(
        _request_record_handler,
        level="TRACE",
        filter=_set_request_filter(is_request_logger=True),
        enqueue=True,
        serialize=True  # record provided as JSON string to the handler
    )
