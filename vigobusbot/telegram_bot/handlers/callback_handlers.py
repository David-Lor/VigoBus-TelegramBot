"""CALLBACK HANDLERS
Callback Handlers for the Callback Queries, produced when users press buttons from the inline keyboards on messages
"""

# # Installed # #
import aiogram

# # Project # #
from ..message_generators import *
from ...persistence_api import saved_stops
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
            user_id=chat_id,
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


async def stop_save(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Save button on Stop messages. Must save the Stop on Persistence API and update the keyboard markup,
    showing the Delete button instead.
    """
    stop_id = callback_data["stop_id"]
    get_all_buses = int(callback_data["get_all_buses"])
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    context = SourceContext(
        user_id=chat_id,
        stop_id=stop_id,
        source_message=callback_query.message,
        get_all_buses=get_all_buses
    )

    await saved_stops.save_stop(
        user_id=chat_id,
        stop_id=stop_id,
        stop_name=None
    )

    markup = await generate_stop_message_buttons(context)
    await callback_query.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )


async def stop_delete(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Delete button on Stop messages. Must delete the Stop from Persistence API and update the keyboard markup,
    showing the Save button instead.
    """
    stop_id = callback_data["stop_id"]
    get_all_buses = int(callback_data["get_all_buses"])
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    context = SourceContext(
        user_id=chat_id,
        stop_id=stop_id,
        source_message=callback_query.message,
        get_all_buses=get_all_buses
    )

    await saved_stops.delete_stop(
        user_id=chat_id,
        stop_id=stop_id
    )

    markup = await generate_stop_message_buttons(context)
    await callback_query.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )


async def stop_get(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """A Stop button on a Saved Stops message. Must send a Stop Message like it would send as response to a Stop command
    """
    stop_id = callback_data["stop_id"]
    chat_id = user_id = callback_query.message.chat.id

    try:
        context = SourceContext(
            user_id=user_id,
            stop_id=stop_id,
            source_message=callback_query.message
        )

        text, markup = await generate_stop_message(context)
        # await start_typing(bot=callback_query.bot, chat_id=chat_id)

        await callback_query.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )

    finally:
        # stop_typing(chat_id)
        await callback_query.bot.answer_callback_query(
            callback_query_id=callback_query.id
        )


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register the callback query (inline keyboard buttons) handlers for the given Bot Dispatcher.
    """
    # Stop Refresh button
    dispatcher.register_callback_query_handler(stop_refresh, StopUpdateCallbackData.filter())

    # Stop Save button
    dispatcher.register_callback_query_handler(stop_save, StopSaveCallbackData.filter())

    # Stop Delete button
    dispatcher.register_callback_query_handler(stop_delete, StopDeleteCallbackData.filter())

    # Get Stop button (from Saved Stops message keyboard)
    dispatcher.register_callback_query_handler(stop_get, StopGetCallbackData.filter())
