"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Installed # #
import aiogram

# # Package # #
from .request_handlers import stop_rename_request_handler

# # Project # #
from ..status_sender import *
from ..message_generators import *
from ...static_handler import *
from ...exceptions import *

__all__ = ("register_handlers",)


async def command_start(message: aiogram.types.Message):
    for text in get_messages().start:
        await message.bot.send_message(message.chat.id, text)


async def command_help(message: aiogram.types.Message):
    for text in get_messages().help:
        await message.bot.send_message(message.chat.id, text)


async def command_donate(message: aiogram.types.Message):
    for text in get_messages().donate:
        await message.bot.send_message(message.chat.id, text)


async def command_about(message: aiogram.types.Message):
    for text in get_messages().about:
        await message.bot.send_message(message.chat.id, text)


async def command_stops(message: aiogram.types.Message):
    """Stops command handler must return all the Stops saved by the user
    """
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
            reply_to_message_id=message.message_id,
            text=text,
            reply_markup=markup
        )

    except ValueError:
        await message.reply(get_messages().stop.not_valid)

    except StopNotExist:
        await message.reply(get_messages().stop.not_exists)

    except (GetterException, AssertionError):
        await message.reply(get_messages().stop.generic_error)

    finally:
        stop_typing(chat_id)


async def global_message_handler(message: aiogram.types.Message):
    """Last Message Handler handles any text message that does not match any of the other message handlers.
    The message text is filtered to guess what the user wants (most probably get, search or rename a Stop).
    """
    # Reply to bot message = reply to Rename stop question
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        if stop_rename_request_handler.is_stop_rename_request_registered(message.reply_to_message.message_id):
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

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)
