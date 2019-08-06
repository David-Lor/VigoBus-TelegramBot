"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Installed # #
import aiogram

# # Project # #
from ...vigobus_getters import get_stop, get_buses
from ...static_handler import get_messages
from ...exceptions import *

__all__ = ("register_handlers",)


async def command_start(message: aiogram.types.Message):
    await message.reply(get_messages().commands.start)


async def command_help(message: aiogram.types.Message):
    await message.reply(get_messages().commands.help)


async def command_stop(message: aiogram.types.Message):
    """Temporary handler to prove functionality.
    """
    try:
        stopid = int(message.text.replace("/stop", "").strip())
        stop = await get_stop(stopid)
        buses = await get_buses(stopid, get_all_buses=False)

    except ValueError:
        await message.reply("Invalid Stop ID!")

    except StopNotExist:
        await message.reply("The Stop does not exist!")

    except GetterException:
        await message.reply("Error happened, try again later")

    else:
        stop_text = f"Stop #{stop.stopid}: {stop.name}"

        if buses:
            buses_text = f"{len(buses)} buses found:\n"
            buses_text += "\n".join([f"```* {bus.line} - {bus.route}: {bus.time}m```" for bus in buses])
        else:
            buses_text = "**No buses found!**"

        text = f"*{stop_text}*\n{buses_text}"

        await message.reply(text, parse_mode="Markdown")


async def global_message_handler(message: aiogram.types.Message):
    """Last Message Handler that handles any text message that does not match any of the other message handlers.
    """
    await message.reply("Pong! " + message.text)


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the message handlers for the given Bot Dispatcher.
    """
    # /start command
    dispatcher.register_message_handler(command_start, commands=("start",))

    # /help command
    dispatcher.register_message_handler(command_help, commands=("help", "ayuda"))

    # /stop command
    dispatcher.register_message_handler(command_stop, commands=("stop", "parada"))

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)
