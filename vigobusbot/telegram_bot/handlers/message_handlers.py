"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Installed # #
import aiogram

# # Project # #
from ..message_generators import *
from ...static_handler import *
from ...exceptions import *

__all__ = ("register_handlers",)


async def command_start(message: aiogram.types.Message):
    for text in get_messages().start:
        await message.bot.send_message(message.chat.id, text, parse_mode="Markdown")


async def command_help(message: aiogram.types.Message):
    for text in get_messages().help:
        await message.bot.send_message(message.chat.id, text, parse_mode="Markdown")


async def command_donate(message: aiogram.types.Message):
    for text in get_messages().donate:
        await message.bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)


async def command_about(message: aiogram.types.Message):
    for text in get_messages().about:
        await message.bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)


async def command_stop(message: aiogram.types.Message):
    """Stop command handler receives forwarded messages from the Global Message Handler
    after filtering the user intention.
    """
    try:
        stopid = int(message.text.replace("/stop", "").strip())

        context = SourceContext(
            stopid=stopid,
            source_message=message,
            get_all_buses=False
        )
        text, markup = await generate_stop_message(context)

        await message.reply(
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    except ValueError:
        await message.reply(get_messages().stop.not_valid)

    except StopNotExist:
        await message.reply(get_messages().stop.not_exists)

    except (GetterException, AssertionError):
        await message.reply(get_messages().stop.generic_error)


async def global_message_handler(message: aiogram.types.Message):
    """Last Message Handler handles any text message that does not match any of the other message handlers.
    The message text is filtered to guess what the user wants (most probably get a Stop).
    """
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

    # /stop command
    dispatcher.register_message_handler(command_stop, commands=("stop", "parada"))

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)
