"""SEARCH STOPS MESSAGE
Generator of Search Stops message body (text and keyboard markup).
Have the responsability of finding the Stops and if they are saved on user list.
"""

# # Native # #
from typing import Tuple

# # Installed # #
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# # Project # #
from vigobusbot.vigobus_api import search_stops_by_name
from vigobusbot.persistence_api.saved_stops import get_user_saved_stops
from vigobusbot.static_handler import get_messages

# # Package # #
from .entities import StopGetCallbackData

__all__ = ("generate_search_stops_message",)


async def generate_search_stops_message(search_term: str, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
    messages = get_messages()
    found_stops = await search_stops_by_name(search_term)

    # Add custom Stop Name for stops saved by the user
    if found_stops:
        user_saved_stops = await get_user_saved_stops(user_id)
        user_saved_stops_dict = {saved_stop.stop_id: saved_stop for saved_stop in user_saved_stops}

        for found_stop in found_stops:
            try:
                found_stop_user_saved = user_saved_stops_dict[found_stop.stop_id]
            except KeyError:
                continue

            if found_stop_user_saved.stop_name:
                found_stop.name = messages.search_stops.buttons.stop_custom_name.format(
                    stop_original_name=found_stop.name,
                    stop_custom_name=found_stop_user_saved.stop_name
                )

    # Generate text
    if found_stops:
        text = messages.search_stops.message_stops_found.format(
            n_stops=len(found_stops),
            plural="s" if len(found_stops) > 1 else ""
        )
    else:
        text = messages.search_stops.message_no_stops

    # Generate buttons
    markup = InlineKeyboardMarkup()
    for stop in found_stops:
        button = InlineKeyboardButton(
            text=messages.search_stops.buttons.stop.format(
                stop_name=stop.name,
                stop_id=stop.stop_id
            ),
            callback_data=StopGetCallbackData.new(stop_id=stop.stop_id)
        )
        markup.row(button)

    return text, markup
