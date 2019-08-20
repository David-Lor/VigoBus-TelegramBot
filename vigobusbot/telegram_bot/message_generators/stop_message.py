"""STOP MESSAGE
Generator of Stop message body (text and keyboard markup).
Have the responsability of finding the Stop, Buses and if the Stop is saved on user list.
"""

# # Native # #
import asyncio
from typing import Tuple

# # Installed # #
import aiogram

# # Project # #
from ...entities import *
from ...vigobus_api import *

# # Package # #
from .source_context import *
from .stop_message_text import *
from .stop_message_buttons import *

__all__ = ("generate_stop_message",)


async def generate_stop_message(context: SourceContext) -> Tuple[str, aiogram.types.InlineKeyboardMarkup]:
    """Generate the Text body and Markup buttons to send as a Stop message, given a SourceContext
    """
    results = await asyncio.gather(
        get_stop(context.stop_id),
        get_buses(context.stop_id),
        generate_stop_message_buttons(context)
    )  # TODO Set Timeout?

    stop = None
    buses = None
    buttons = None

    for result in results:
        if isinstance(result, Stop):
            stop = result
        elif isinstance(result, list):
            buses = result
        elif isinstance(result, aiogram.types.InlineKeyboardMarkup):
            buttons = result

    assert isinstance(stop, Stop)
    assert isinstance(buses, list)
    assert isinstance(buttons, aiogram.types.InlineKeyboardMarkup)

    text = generate_stop_message_text(stop, buses)

    return text, buttons
