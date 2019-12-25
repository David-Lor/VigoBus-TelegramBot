"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Installed # #
import aiogram

# # Package # #
from .request_handlers import stop_rename_request_handler
from .rate_limit_handlers import handle_user_rate_limit
from . import test_message_handlers

# # Project # #
from ...settings_handler import system_settings
from ..status_sender import *
from ..message_generators import *
from ...static_handler import *
from ...exceptions import *
from ...logger import *

__all__ = ("register_handlers",)


def handle_rate_limit(message: aiogram.types.Message):
    handle_user_rate_limit(message.chat.id)


async def command_start(message: aiogram.types.Message):
    logger.debug("Requested command /start")
    handle_rate_limit(message)
    for text in get_messages().start:
        await message.bot.send_message(message.chat.id, text)


async def command_help(message: aiogram.types.Message):
    logger.debug("Requested command /help")
    handle_rate_limit(message)
    for text in get_messages().help:
        await message.bot.send_message(message.chat.id, text)


async def command_donate(message: aiogram.types.Message):
    logger.debug("Requested command /donate")
    handle_rate_limit(message)
    for text in get_messages().donate:
        await message.bot.send_message(message.chat.id, text)


async def command_about(message: aiogram.types.Message):
    logger.debug("Requested command /about")
    handle_rate_limit(message)
    for text in get_messages().about:
        await message.bot.send_message(message.chat.id, text)


async def command_stops(message: aiogram.types.Message):
    """Stops command handler must return all the Stops saved by the user
    """
    logger.debug("Requested command /stops")
    handle_rate_limit(message)
    chat_id = user_id = message.chat.id

    try:
        await start_typing(bot=message.bot, chat_id=chat_id)

        text, buttons = await generate_saved_stops_message(user_id)
        await message.bot.send_message(message.chat.id, text, reply_markup=buttons)

    finally:
        stop_typing(chat_id)


async def command_stop(message: aiogram.types.Message):
    """Stop command handler receives forwarded messages from the Global Message Handler
    after filtering the user intention.
    """
    logger.debug("Requested command /stop")
    handle_rate_limit(message)
    chat_id = message.chat.id

    try:
        stop_id = next(chunk for chunk in message.text.split() if chunk.isdigit())

        context = SourceContext(
            user_id=chat_id,
            stop_id=stop_id,
            source_message=message,
            get_all_buses=False
        )

        await start_typing(bot=message.bot, chat_id=chat_id)
        text, markup = await generate_stop_message(context)

        await message.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=markup
        )

    except (ValueError, StopIteration):
        await message.reply(get_messages().stop.not_valid)

    except StopNotExist:
        await message.reply(get_messages().stop.not_exists)

    finally:
        stop_typing(chat_id)


async def command_cancel(message: aiogram.types.Message):
    """Cancel command handler cancels a ForceReply operation, such as Stop Rename.
    The ForceReply message sent by the bot must be deleted, if possible.
    """
    logger.debug("Requested command /cancel (for ForceReply operation)")
    handle_rate_limit(message)
    user_id = chat_id = message.chat.id
    stop_rename_request_context = stop_rename_request_handler.get_stop_rename_request_context(user_id=user_id)

    if stop_rename_request_context:
        await message.bot.delete_message(
            chat_id=chat_id,
            message_id=stop_rename_request_context.force_reply_message_id
        )

    else:
        await message.bot.send_message(
            chat_id=chat_id,
            text=get_messages().stop_rename.deprecated_command,
            reply_to_message_id=message.message_id
        )


async def command_removename(message: aiogram.types.Message):
    """Remove Name command handler removes a custom name from a previously user saved Stop.
    A rename ForceReply message should be sent by the bot and the StopRenameRequestContext must exist.
    """
    logger.debug("Requested command /removename")
    handle_rate_limit(message)
    user_id = chat_id = message.chat.id

    if stop_rename_request_handler.get_stop_rename_request_context(user_id=user_id, pop=False):
        return await stop_rename_request_handler.stop_rename_request_reply_handler(message, remove_custom_name=True)

    else:
        await message.bot.send_message(
            chat_id=chat_id,
            text=get_messages().stop_rename.deprecated_command,
            reply_to_message_id=message.message_id
        )


async def global_message_handler(message: aiogram.types.Message):
    """Last Message Handler handles any text message that does not match any of the other message handlers.
    The message text is filtered to guess what the user wants (most probably get, search or rename a Stop).
    """
    # Reply to bot message = reply to Rename stop question
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        logger.debug("Received Reply to bot message")
        if stop_rename_request_handler.get_stop_rename_request_context(
                force_reply_message_id=message.reply_to_message.message_id, pop=False
        ):
            return await stop_rename_request_handler.stop_rename_request_reply_handler(message)
        else:
            # if ForceReply message not registered, user might had replied any message, or the request expired
            await message.bot.send_message(
                chat_id=message.chat.id,
                text=get_messages().stop_rename.expired_request,
                reply_to_message_id=message.message_id
            )

    # Get a Stop by Stop ID
    if message.text.strip().isdigit():
        logger.debug("Requested Stop without command (direct input)")
        return await command_stop(message)


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

    # /cancel command
    dispatcher.register_message_handler(command_cancel, commands=("cancel", "cancelar"))

    # /removename command
    dispatcher.register_message_handler(command_removename, commands=("removename", "quitarnombre"))

    # Test handlers
    if system_settings.test:
        test_message_handlers.register_handlers(dispatcher)

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)

    logger.debug("Registered Message Handlers")
