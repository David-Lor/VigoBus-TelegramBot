"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

import asyncio

import aiogram

from . import test_message_handlers
from vigobusbot.telegram_bot.services import request_handler
from vigobusbot.telegram_bot.services.status_sender import start_typing, stop_typing
from vigobusbot.telegram_bot.services.feedback_request_handler import get_feedback_request_context
from vigobusbot.telegram_bot.services.feedback_request_handler import register_feedback_request
from vigobusbot.telegram_bot.services.feedback_request_handler import handle_feedback_request_reply
from vigobusbot.telegram_bot.services.stop_rename_request_handler import get_stop_rename_request_context
from vigobusbot.telegram_bot.services.stop_rename_request_handler import handle_stop_rename_request_reply
from vigobusbot.telegram_bot.services.user_data_request_handler import extract_user_data, send_file
from vigobusbot.telegram_bot.entities import Message
from vigobusbot.telegram_bot.services.message_generators import SourceContext, FeedbackForceReply
from vigobusbot.telegram_bot.services.message_generators import generate_stop_message, generate_saved_stops_message
from vigobusbot.telegram_bot.services.message_generators import generate_search_stops_message
from vigobusbot.telegram_bot.services.sent_messages_persistence import persist_sent_stop_message
from vigobusbot.persistence_api.saved_stops import delete_all_stops
from vigobusbot.settings_handler import system_settings
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger

__all__ = ("register_handlers",)


@request_handler("Command /start")
async def command_start(message: Message, *args, **kwargs):
    for text in get_messages().start:
        await message.bot.send_message(message.chat.id, text)


@request_handler("Command /help")
async def command_help(message: Message, *args, **kwargs):
    for text in get_messages().help:
        await message.bot.send_message(message.chat.id, text)


@request_handler("Command /donate")
async def command_donate(message: Message, *args, **kwargs):
    for text in get_messages().donate:
        await message.bot.send_message(message.chat.id, text)


@request_handler("Command /about")
async def command_about(message: Message, *args, **kwargs):
    for text in get_messages().about:
        await message.bot.send_message(message.chat.id, text)


@request_handler("Command /extractdata")
async def command_extract_data(message: Message, *args, **kwargs):
    chat_id = user_id = message.chat.id

    try:
        await start_typing(bot=message.bot, chat_id=chat_id)

        files = await extract_user_data(user_id)
        await asyncio.gather(*[
            send_file(bot=message.bot, chat_id=chat_id, file=file, remove_file=True)
            for file in files
        ])

    finally:
        stop_typing(chat_id)


@request_handler("Command /deletedata")
async def command_delete_data(message: Message, *args, **kwargs):
    await message.bot.send_message(message.chat.id, get_messages().delete_data.ask_confirmation)


@request_handler("Command /deletedata_yes")
async def command_delete_data_confirmed(message: Message, *args, **kwargs):
    chat_id = user_id = message.chat.id

    try:
        await start_typing(bot=message.bot, chat_id=chat_id)
        await delete_all_stops(user_id)
        await message.bot.send_message(chat_id, get_messages().delete_data.success)

    finally:
        stop_typing(chat_id)


@request_handler("Command /stops")
async def command_stops(message: Message, *args, **kwargs):
    """Stops command handler must return all the Stops saved by the user
    """
    chat_id = user_id = message.chat.id

    try:
        await start_typing(bot=message.bot, chat_id=chat_id)

        text, buttons = await generate_saved_stops_message(user_id)
        await message.bot.send_message(chat_id, text, reply_markup=buttons)

    finally:
        stop_typing(chat_id)


@request_handler("Command /stop")
async def command_stop(message: Message, *args, **kwargs):
    """Stop command handler receives forwarded messages from the Global Message Handler
    after filtering the user intention.
    """
    chat_id = user_id = message.chat.id

    try:
        stop_id = next(chunk for chunk in message.text.split() if chunk.isdigit())

        # noinspection PyTypeChecker
        context = SourceContext(
            user_id=user_id,
            stop_id=stop_id,
            source_message=message,
            get_all_buses=False
        )

        await start_typing(bot=message.bot, chat_id=chat_id)
        text, markup = await generate_stop_message(context)

        msg = await message.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )
        await persist_sent_stop_message(msg)

    except (ValueError, StopIteration):
        await message.bot.send_message(
            chat_id=message.chat.id,
            reply_to_message_id=message.message_id,
            text=get_messages().stop.not_valid,
        )

    finally:
        stop_typing(chat_id)


@request_handler("Command /search")
async def command_search_stops(message: Message, *args, **kwargs):
    """Search Stop command handler receives forwarded messages from the Global Message Handler
    after filtering the user intention.
    """
    chat_id = user_id = message.chat.id
    messages = get_messages()

    search_term = " ".join([chunk for chunk in message.text.split() if not chunk.startswith("/")]).strip()
    if len(search_term) < 3:
        logger.debug("Search term is too short or not given")
        return await message.bot.send_message(
            chat_id=chat_id,
            text=messages.search_stops.search_term_too_short
        )

    await start_typing(bot=message.bot, chat_id=chat_id)

    try:
        text, markup = await generate_search_stops_message(search_term=search_term, user_id=user_id)

        await message.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )

    finally:
        stop_typing(chat_id)


@request_handler("Command /cancel")
async def command_cancel(message: Message, *args, **kwargs):
    """Cancel command handler cancels a ForceReply operation, such as Stop Rename.
    The ForceReply message sent by the bot must be deleted, if possible.
    """
    user_id = chat_id = message.chat.id
    stop_rename_request_context = get_stop_rename_request_context(user_id=user_id)
    feedback_request_context = get_feedback_request_context(user_id=user_id)

    if stop_rename_request_context:
        await message.bot.delete_message(
            chat_id=chat_id,
            message_id=stop_rename_request_context.force_reply_message_id
        )
    elif feedback_request_context:
        await message.bot.delete_message(
            chat_id=chat_id,
            message_id=feedback_request_context.force_reply_message_id
        )
    else:
        await message.bot.send_message(
            chat_id=chat_id,
            text=get_messages().stop_rename.deprecated_command,
            reply_to_message_id=message.message_id
        )


@request_handler("Command /removename")
async def command_removename(message: Message, *args, **kwargs):
    """Remove Name command handler removes a custom name from a previously user saved Stop.
    A rename ForceReply message should be sent by the bot and the StopRenameRequestContext must exist.
    """
    user_id = chat_id = message.chat.id

    if get_stop_rename_request_context(user_id=user_id, pop=False):
        return await handle_stop_rename_request_reply(message, remove_custom_name=True)

    else:
        await message.bot.send_message(
            chat_id=chat_id,
            text=get_messages().stop_rename.deprecated_command,
            reply_to_message_id=message.message_id
        )


@request_handler("Command /feedback")
async def command_feedback(message: Message, *args, **kwargs):
    chat_id = user_id = message.chat.id

    force_reply_message = await message.bot.send_message(
        chat_id=chat_id,
        reply_markup=FeedbackForceReply.create(),
        text=get_messages().feedback.request
    )
    register_feedback_request(user_id=user_id, force_reply_message_id=force_reply_message.message_id)


@request_handler("Non-Command Text message")
async def global_message_handler(message: Message, *args, **kwargs):
    """Last Message Handler handles any text message that does not match any of the other message handlers.
    The message text is filtered to guess what the user wants (most probably get, search or rename a Stop).
    """
    # Reply to bot message = reply to Force Reply
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        logger.debug("Received Reply to bot message")

        if get_stop_rename_request_context(
                force_reply_message_id=message.reply_to_message.message_id, pop=False
        ):
            return await handle_stop_rename_request_reply(message)

        elif get_feedback_request_context(force_reply_message_id=message.reply_to_message.message_id, pop=False):
            return await handle_feedback_request_reply(message)

        else:
            # if ForceReply message not registered, user might had replied any message, or the request expired
            await message.bot.send_message(
                chat_id=message.chat.id,
                text=get_messages().stop_rename.expired_request,
                reply_to_message_id=message.message_id
            )

    # Get a Stop by Stop ID
    message_text = message.text.strip()
    if message_text.isdigit():
        logger.debug("Requested Stop without command (direct input)")
        return await command_stop(message)

    # Search a Stop by Name
    return await command_search_stops(message)


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the message handlers for the given Bot Dispatcher.
    """
    # /start command
    dispatcher.register_message_handler(command_start, commands=("start",))

    # /help command
    dispatcher.register_message_handler(command_help, commands=("help", "ayuda"))

    # /donate command
    dispatcher.register_message_handler(command_donate, commands=("donate", "donar", "colaborar", "aportar"))

    # /about command
    dispatcher.register_message_handler(command_about, commands=("about", "acerca", "acercade"))

    # /stops command
    dispatcher.register_message_handler(command_stops, commands=("stops", "paradas"))

    # /stop command
    dispatcher.register_message_handler(command_stop, commands=("stop", "parada"))

    # /search command
    dispatcher.register_message_handler(command_search_stops, commands=("search", "buscar"))

    # /cancel command
    dispatcher.register_message_handler(command_cancel, commands=("cancel", "cancelar"))

    # /removename command
    dispatcher.register_message_handler(command_removename, commands=("removename", "quitarnombre"))

    # /extractdata command
    dispatcher.register_message_handler(command_extract_data, commands=("extractdata", "extraer_todo"))

    # /deletedata command
    dispatcher.register_message_handler(command_delete_data, commands=("deletedata", "borrar_todo"))

    # /deletedata_yes command
    dispatcher.register_message_handler(command_delete_data_confirmed, commands=("deletedata_yes", "borrar_todo_si"))

    # /feedback command
    dispatcher.register_message_handler(command_feedback, commands=("feedback", "comentarios"))

    # Test handlers
    if system_settings.test:
        test_message_handlers.register_handlers(dispatcher)

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)

    logger.debug("Registered Message Handlers")
