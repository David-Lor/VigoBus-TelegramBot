"""HANDLERS
Register all the available handlers (messages, callbacks) to the Bot Dispatcher instance.
"""

# # Installed # #
import aiogram

# # Package # #
from . import message_handlers, callback_handlers, inline_handlers

__all__ = ("register_handlers",)


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the available handlers to the Bot Dispatcher instance.
    This function is called after creating a new Bot instance and before running it (using Polling or Webhook).
    """
    message_handlers.register_handlers(dispatcher)
    callback_handlers.register_handlers(dispatcher)
    inline_handlers.register_handlers(dispatcher)
