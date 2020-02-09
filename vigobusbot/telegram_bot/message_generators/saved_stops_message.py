"""SAVED STOPS MESSAGE
Generator of Saved Stops message body (text and keyboard markup).
Have the responsability of getting the Saved Stops list of the user from the Persistence API .
"""

# # Native # #
from typing import Tuple, Optional

# # Installed # #
import aiogram

# # Package # #
from .entities import *

# # Project # #
from ...persistence_api.saved_stops import get_user_saved_stops
from ...static_handler import *
from ...vigobus_api import *
from ...entities import *

__all__ = ("generate_saved_stops_message",)


async def generate_saved_stops_message(user_id: int) -> Tuple[str, Optional[aiogram.types.InlineKeyboardMarkup]]:
    """Generate the Text body and Markup buttons to send as a Saved Stops message, given the User ID
    """
    messages = get_messages()
    saved_stops = await get_user_saved_stops(user_id)
    text, markup = None, None

    if saved_stops:
        text = messages.saved_stops.message_has_stops.format(
            n_stops=len(saved_stops),
            plural="s" if len(saved_stops) > 1 else ""
        )
        markup = aiogram.types.InlineKeyboardMarkup()

        # Get the Real Stop info from the Bus API
        real_stops: StopsDict = await get_multiple_stops(*[stop.stop_id for stop in saved_stops], return_dict=True)

        # Add the Real Stop name to the Saved Stops
        for saved_stop in saved_stops:
            saved_stop.stop_original_name = real_stops[saved_stop.stop_id].name

        # Sort saved stops by custom name or real name
        saved_stops.sort(key=lambda stop: stop.stop_name or stop.stop_original_name)

        for saved_stop in saved_stops:
            if saved_stop.stop_name:
                stop_name_text = messages.saved_stops.buttons.stop_custom_name.format(
                    stop_custom_name=saved_stop.stop_name,
                    stop_original_name=saved_stop.stop_original_name
                )
            else:
                stop_name_text = saved_stop.stop_original_name

            button = aiogram.types.InlineKeyboardButton(
                text=messages.saved_stops.buttons.stop.format(
                    stop_id=saved_stop.stop_id,
                    stop_name=stop_name_text
                ),
                callback_data=StopGetCallbackData.new(
                    stop_id=saved_stop.stop_id
                )
            )
            markup.row(button)

    else:
        text = messages.saved_stops.message_no_stops

    return text, markup
