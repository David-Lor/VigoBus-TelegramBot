"""STOP MESSAGE
Generator of Stop message body (text and keyboard markup).
Have the responsability of finding the Stop, Buses and if the Stop is saved on user list.
"""

# # Native # #
import asyncio
from typing import Tuple

# # Installed # #
from aiogram.types import InlineKeyboardMarkup

# # Project # #
from vigobusbot.persistence_api import saved_stops
from vigobusbot.vigobus_api import get_stop, get_buses
from vigobusbot.entities import Stop, BusesResponse

# # Package # #
from .source_context import SourceContext
from .stop_message_text import generate_stop_message_text
from .stop_message_buttons import generate_stop_message_buttons

__all__ = ("generate_stop_message",)


async def generate_stop_message(context: SourceContext) -> Tuple[str, InlineKeyboardMarkup]:
    """Generate the Text body and Markup buttons to send as a Stop message, given a SourceContext
    """
    stop: Stop
    buses_response: BusesResponse
    stop, buses_response, user_saved_stop = await asyncio.gather(
        get_stop(context.stop_id),
        get_buses(stop_id=context.stop_id, get_all_buses=context.get_all_buses),
        saved_stops.get_stop(user_id=context.user_id, stop_id=context.stop_id)
    )

    text = generate_stop_message_text(stop=stop, buses_response=buses_response, user_saved_stop=user_saved_stop)
    context.more_buses_available = buses_response.more_buses_available
    buttons = generate_stop_message_buttons(context=context, is_stop_saved=bool(user_saved_stop))

    return text, buttons
