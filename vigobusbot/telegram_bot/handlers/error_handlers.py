"""ERROR HANDLERS
Telegram Bot Error Handlers for global exceptions
"""

# # Native # #
import contextlib

# # Installed # #
import aiogram

# # Project # #
from ...static_handler import *
from ...exceptions import *

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


# noinspection PyUnusedLocal
async def global_error_handler(update: aiogram.types.Update, exception: Exception):
    """Handle all types of exceptions uncatched by source functions.
    """
    messages = get_messages()

    if isinstance(exception, StopNotExist):
        # StopNotExist errors are preferably catched on source functions, to avoid logging them on output
        await notify_error(update, messages.stop.not_exists)

    else:
        await notify_error(update, messages.generic.generic_error)


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the error handlers for the given Bot Dispatcher.
    """
    dispatcher.register_errors_handler(global_error_handler)
