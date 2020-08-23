"""SEARCH STOPS INLINE
Generator of results for Search Stops inline queries.
Have the responsability of finding the Stops and generating the result articles.
"""

# # Native # #
import re
from datetime import datetime
from typing import List

# # Installed # #
import aiogram

# # Project # #
from vigobusbot.vigobus_api import search_stops_by_name, get_stop
from vigobusbot.static_handler import get_messages
from vigobusbot.exceptions import StopNotExist

__all__ = ("generate_search_stops_inline_responses",)


class InputTextMessageContent(aiogram.types.InputTextMessageContent):
    parse_mode = "HTML"


async def generate_search_stops_inline_responses(search_term: str) -> List[aiogram.types.InlineQueryResultArticle]:
    messages = get_messages()
    results = list()

    if search_term.isdigit():
        try:
            found_stops = [await get_stop(stop_id=int(search_term))]
        except StopNotExist:
            found_stops = []
    else:
        found_stops = await search_stops_by_name(search_term)

    if found_stops:
        common_reply_loading_button = aiogram.types.InlineKeyboardButton("Cargando...", callback_data="None")
        common_reply_markup = aiogram.types.InlineKeyboardMarkup()
        common_reply_markup.row(common_reply_loading_button)

        for found_stop in found_stops:
            loading_message_text = messages.stop.message.format(
                stop_id=found_stop.stop_id,
                stop_name=found_stop.name,
                buses=messages.search_stops.inline.searching,
                last_update=datetime.now().strftime(messages.stop.time_format)
            )
            results.append(aiogram.types.InlineQueryResultArticle(
                id=str(found_stop.stop_id),
                title=found_stop.name,
                description=f"#{found_stop.stop_id}",
                input_message_content=aiogram.types.InputTextMessageContent(loading_message_text, parse_mode="HTML"),
                reply_markup=common_reply_markup
            ))

    else:
        not_found_message = messages.search_stops.message_no_stops
        not_found_title = re.sub(re.compile('<.*?>'), '', not_found_message)  # Remove HTML tags
        results.append(aiogram.types.InlineQueryResultArticle(
            id="None",
            title=not_found_title,
            input_message_content=InputTextMessageContent(not_found_message, parse_mode="HTML")
        ))

    return results
