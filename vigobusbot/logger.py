"""LOGGER
Logger instance
"""

# # Native # #
import sys
import uuid
import logging
import contextlib
from typing import Optional

# # Installed # #
from loguru import logger
# noinspection PyProtectedMember
from loguru._logger import context as loguru_context

# # Package # #
from .settings_handler import system_settings as settings

__all__ = ("logger", "contextualize_request", "get_context_id")

ContextId = "request_id"
"""Name of the Context ID variable part of the logger context extra"""

DefaultContextId = "No-Request"
"""Value of the Context ID when the log record lacks of context id (when is not a bot request)"""

LoggerFormat = "{time} | {level} | {name}: {message} | {extra[$ContextId$]}".replace("$ContextId$", ContextId)


@contextlib.asynccontextmanager
async def contextualize_request(context_id: Optional[str] = None):
    """Must wrap each user request handler, to create a Request ID used as the Context ID for the logger,
    to track the request through all the log records created by the call
    """
    # TODO When the handler function fails, the error handler cannot get the Context ID
    #      (might get fixed when using a custom error handler, instead of the one provided by aiogram)
    if not context_id:
        # TODO Generate shorter Context ID (even not random-based, but based on timestamp and/or counting the requests?)
        context_id = str(uuid.uuid4())

    with logger.contextualize(**{ContextId: context_id}):
        yield context_id


def get_context_id() -> Optional[str]:
    """Return the current Context ID, if defined, being used by the logger
    """
    with contextlib.suppress(Exception):
        context: dict = loguru_context.get()
        return context.get(ContextId)


def _patch_func(record):
    """If the log record does not have Context ID, set to a generic value.
    This happens when logging during system initialization (outside of bot requests).
    """
    # TODO dynamically remove contextId from log (use dynamic formatting, seting logger format as a function)
    if not record["extra"] or not record["extra"].get(ContextId):
        record["extra"][ContextId] = DefaultContextId


# Disable default aiogram logger
logging.getLogger("aiogram").disabled = True

# Set custom logger
logger.remove()
logger.add(sys.stderr, level=settings.log_level.upper(), format=LoggerFormat)
logger = logger.patch(_patch_func)
