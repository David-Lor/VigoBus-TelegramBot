"""CALLBACK HANDLERS
Callback Handlers for the Callback Queries, produced when users press buttons from the inline keyboards on messages
"""

# # Native # #
import asyncio

# # Installed # #
import aiogram

# # Package # #
from .request_handlers import stop_rename_request_handler

# # Project # #
from ..status_sender import *
from ..message_generators import *
from ...persistence_api import saved_stops
from ...static_handler import get_messages
from ...vigobus_api import *
from ...exceptions import *

__all__ = ("register_handlers",)


async def stop_refresh(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Refresh button on Stop messages. Must generate a new Stop message content and edit the original message.
    """
    try:
        data = CallbackDataExtractor.extract(callback_data)
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id

        context = SourceContext(
            user_id=chat_id,
            stop_id=data.stop_id,
            source_message=callback_query.message,
            get_all_buses=data.get_all_buses
        )

        # For now, not sending "typing" status, since after message is updated it can still show "typing"...
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


async def stop_get(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """A Stop button on a Saved Stops message. Must send a Stop Message like it would send as response to a Stop command
    """
    data = CallbackDataExtractor.extract(callback_data)
    chat_id = user_id = callback_query.message.chat.id

    try:
        context = SourceContext(
            user_id=user_id,
            stop_id=data.stop_id,
            source_message=callback_query.message
        )

        await start_typing(bot=callback_query.bot, chat_id=chat_id)
        text, markup = await generate_stop_message(context)

        await callback_query.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )

    finally:
        stop_typing(chat_id)
        await callback_query.bot.answer_callback_query(
            callback_query_id=callback_query.id
        )


async def stop_save(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Save button on Stop messages. Must save the Stop on Persistence API and update the keyboard markup,
    showing the Delete button instead.
    """
    # TODO We could unify save & delete functions in one (actions to perform after saving/deleting are the same)
    try:
        data = CallbackDataExtractor.extract(callback_data)
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id

        context = SourceContext(
            user_id=chat_id,
            stop_id=data.stop_id,
            source_message=callback_query.message,
            get_all_buses=data.get_all_buses
        )

        if not await saved_stops.is_stop_saved(user_id=chat_id, stop_id=data.stop_id):
            await saved_stops.save_stop(
                user_id=chat_id,
                stop_id=data.stop_id,
                stop_name=None
            )
            assert await saved_stops.is_stop_saved(user_id=chat_id, stop_id=data.stop_id)

        markup = generate_stop_message_buttons(context=context, is_stop_saved=True)
        await callback_query.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    finally:
        await callback_query.bot.answer_callback_query(
            callback_query_id=callback_query.id
        )


async def stop_delete(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Delete button on Stop messages. Must delete the Stop from Persistence API and update the keyboard markup,
    showing the Save button instead.
    """
    try:
        data = CallbackDataExtractor.extract(callback_data)
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id

        context = SourceContext(
            user_id=chat_id,
            stop_id=data.stop_id,
            source_message=callback_query.message,
            get_all_buses=data.get_all_buses
        )

        if await saved_stops.is_stop_saved(user_id=chat_id, stop_id=data.stop_id):
            await saved_stops.delete_stop(
                user_id=chat_id,
                stop_id=data.stop_id
            )
            assert not await saved_stops.is_stop_saved(user_id=chat_id, stop_id=data.stop_id)

        markup = generate_stop_message_buttons(context=context, is_stop_saved=False)
        await callback_query.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    finally:
        await callback_query.bot.answer_callback_query(
            callback_query_id=callback_query.id
        )


async def stop_rename(callback_query: aiogram.types.CallbackQuery, callback_data: dict):
    """Rename button on Stop messages. Must ask the user for the new Stop name on a new message using ForceReply,
    and register the request for identifying user reply later on the message handler.
    """
    answered_callback_query = False

    try:
        messages = get_messages()
        source_message = callback_query.message
        data = CallbackDataExtractor.extract(callback_data)
        chat_id = source_message.chat.id

        stop, saved_stop = await asyncio.gather(
            get_stop(data.stop_id),
            saved_stops.get_stop(user_id=chat_id, stop_id=data.stop_id)
        )

        # User pressed Rename button when the stop is already deleted
        if saved_stop is None:
            update_keyboard_context = SourceContext(
                stop_id=data.stop_id,
                user_id=chat_id,
                source_message=source_message
            )
            await asyncio.gather(
                # Let user know the stop is already deleted
                callback_query.bot.answer_callback_query(
                    callback_query_id=callback_query.id,
                    text=messages.stop_rename.currently_deleted,
                    show_alert=True
                ),
                # Also update source message
                callback_query.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=source_message.message_id,
                    reply_markup=generate_stop_message_buttons(
                        context=update_keyboard_context,
                        is_stop_saved=False
                    )
                )
            )
            answered_callback_query = True
            return

        text = messages.stop_rename.request.format(
            stop_id=data.stop_id,
            stop_name=stop.name
        )

        if saved_stop.stop_name:
            text += "\n" + messages.stop_rename.request_unname.format(
                current_stop_name=saved_stop.stop_name
            )

        force_reply_message = await callback_query.bot.send_message(
            chat_id=chat_id,
            reply_markup=RenameStopForceReply.create(),
            text=text
        )

        rename_request_context = stop_rename_request_handler.StopRenameRequestContext(
            stop_id=data.stop_id,
            user_id=callback_query.message.chat.id,
            get_all_buses=data.get_all_buses,
            source_message=source_message,
            force_reply_message_id=force_reply_message.message_id
        )
        stop_rename_request_handler.register_stop_rename_request(rename_request_context)

    finally:
        if not answered_callback_query:
            await callback_query.bot.answer_callback_query(
                callback_query_id=callback_query.id
            )


async def generic_callback_handler(callback_query: aiogram.types.CallbackQuery):
    """Any deprecated button is handled by the Generic Handler, informing the user of this situation.
    """
    messages = get_messages()

    await callback_query.bot.answer_callback_query(
        callback_query_id=callback_query.id,
        text=messages.generic.deprecated_inline_keyboard_button,
        show_alert=True
    )


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register the callback query (inline keyboard buttons) handlers for the given Bot Dispatcher.
    """
    # Stop Refresh button
    dispatcher.register_callback_query_handler(stop_refresh, StopUpdateCallbackData.filter())

    # Get Stop button (from Saved Stops message keyboard)
    dispatcher.register_callback_query_handler(stop_get, StopGetCallbackData.filter())

    # Stop Save button
    dispatcher.register_callback_query_handler(stop_save, StopSaveCallbackData.filter())

    # Stop Delete button
    dispatcher.register_callback_query_handler(stop_delete, StopDeleteCallbackData.filter())

    # Stop Rename button
    dispatcher.register_callback_query_handler(stop_rename, StopRenameCallbackData.filter())

    # Rest of buttons (generic handler for deprecated buttons)
    dispatcher.register_callback_query_handler(generic_callback_handler)
