"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Native # #
import datetime

# # Installed # #
import aiogram

# # Project # #
from ...vigobus_getters import *
from ...static_handler import *
from ...exceptions import *

__all__ = ("register_handlers",)


async def command_start(message: aiogram.types.Message):
    for text in get_messages().start:
        await message.reply(text, parse_mode="Markdown")


async def command_help(message: aiogram.types.Message):
    for text in get_messages().help:
        await message.reply(text, parse_mode="Markdown")


async def command_stop(message: aiogram.types.Message):
    """Stop command handler receives forwarded messages from the Global Message Handler
    after filtering the user intention.
    """
    try:
        stopid = int(message.text.replace("/stop", "").strip())
        stop = await get_stop(stopid)
        buses = await get_buses(stopid, get_all_buses=False)

    except ValueError:
        await message.reply(get_messages().stop.not_valid)

    except StopNotExist:
        await message.reply(get_messages().stop.not_exists)

    except GetterException:
        await message.reply(get_messages().stop.generic_error)

    else:
        if buses:
            buses_text_lines = list()
            for bus in buses:
                if bus.time == 0:
                    time_text = get_messages().stop.bus_time_now
                else:
                    time_text = get_messages().stop.bus_time_remaining.format(minutes=bus.time)
                buses_text_lines.append(get_messages().stop.bus_line.format(
                    line=bus.line,
                    route=bus.route,
                    time=time_text
                ))
            buses_text = "\n".join(buses_text_lines)
        else:
            buses_text = get_messages().stop.no_buses_found

        last_update_text = datetime.datetime.now().strftime(get_messages().stop.time_format)

        text = get_messages().stop.message.format(
            stop_id=stopid,
            stop_name=stop.name,
            buses=buses_text,
            last_update=last_update_text
        )

        await message.reply(text, parse_mode="Markdown")


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

    # /stop command
    dispatcher.register_message_handler(command_stop, commands=("stop", "parada"))

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)
