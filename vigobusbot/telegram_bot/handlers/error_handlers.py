"""ERROR HANDLERS
Telegram Bot Error Handlers for global exceptions
"""

# # Native # #
import traceback
import contextlib

# # Installed # #
import aiogram

# # Project # #
from ...static_handler import *
from ...exceptions import *
from ...logger import *

__all__ = ("register_handlers",)


async def notify_error(update: aiogram.types.Update, text: str):
    """Send the error message to the user, as a message reply or a callback answer, depending on the context.
    """
    with contextlib.suppress(Exception):
        if update.callback_query:
            await update.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text=text,
                show_alert=True
            )

        elif update.message:
            await update.bot.send_message(
                chat_id=update.message.chat.id,
                text=text,
                reply_to_message_id=update.message.message_id
            )


async def global_error_handler(update: aiogram.types.Update, exception: Exception) -> True:
    """Handle all types of exceptions uncatched by source functions.
    """
    try:
        messages = get_messages()

        if isinstance(exception, StopNotExist):
            await notify_error(update, messages.stop.not_exists)

        elif isinstance(exception, UserRateLimit):
            await notify_error(update, messages.generic.rate_limit_error)

        else:
            # Unidentified (Generic) errors
            traceback_msg = ""
            if exception.__traceback__:
                # TODO Format/get traceback str
                traceback_msg = f" - Traceback:\n{traceback.format_tb(exception.__traceback__)}"
            # TODO No request id context on this log record
            logger.error(f"Unidentified error while processing a client request ({exception}){traceback_msg}")
            await notify_error(update, messages.generic.generic_error)

    finally:
        return True


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the error handlers for the given Bot Dispatcher.
    """
    # TODO register for each type using "exception" kwarg
    dispatcher.register_errors_handler(global_error_handler)
