"""CALLBACK HANDLERS
Callback Handlers for the Callback Queries, produced when users press buttons from the inline keyboards on messages
"""

# # Installed # #
import aiogram

# # Project # #
from ..message_generators import *
from ...exceptions import *

__all__ = ("register_handlers",)


async def stop_refresh(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Refresh button on Stop messages. Must generate a new Stop message content and edit the original message.
    """
    try:
        stop_id = callback_data["stop_id"]
        get_all_buses = int(callback_data["get_all_buses"])
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id

        context = SourceContext(
            stop_id=stop_id,
            source_message=callback_query.message,
            get_all_buses=get_all_buses
        )
        # await start_typing(bot=callback_query.bot, chat_id=chat_id)

        text, markup = await generate_stop_message(context)

        await callback_query.bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    # TODO Add Except cases and replies to users

    except MessageNotModified:
        # MessageNotModified exceptions can trigger when user presses Update button many times too quickly,
        # resulting on the same message text with the same timestamp. Ignore these errors.
        pass

    finally:
        # stop_typing(chat_id)
        pass


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register the callback query (inline keyboard buttons) handlers for the given Bot Dispatcher.
    """
    # Stop Refresh button
    dispatcher.register_callback_query_handler(stop_refresh, StopUpdateCallbackData.filter())
