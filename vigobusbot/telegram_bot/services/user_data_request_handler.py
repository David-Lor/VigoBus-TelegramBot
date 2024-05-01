"""USER DATA REQUEST HANDLER
Handler and utils for working with User Data Extraction requests
"""

import os
import json

import aiogram

from vigobusbot.vigobus_api.stop_getter import fill_saved_stops_info
from vigobusbot.persistence_api.saved_stops import get_user_saved_stops
from vigobusbot.models import File, Files
from vigobusbot.static_handler import get_messages
from vigobusbot.logger import logger

__all__ = ("extract_user_data", "send_file")


class UserDataExtractors:
    """Methods to extract user data to a file.
    Return the filename (path) where the data is saved.
    """
    @staticmethod
    async def stops(user_id: int) -> str:
        logger.debug("Extracting Saved Stops data from user")
        messages = get_messages()
        saved_stops = await get_user_saved_stops(user_id)
        await fill_saved_stops_info(saved_stops)
        stops_dict = [dict(
            stop_id=stop.stop_id,
            stop_name=stop.stop_name,
        ) for stop in saved_stops]

        filename = f"/tmp/{user_id}_{messages.extracted_data.stops.filename}"
        with open(filename, "w") as file:
            json.dump(stops_dict, file, indent=2, ensure_ascii=False)

        return filename


async def send_file(bot: aiogram.Bot, chat_id: int, file: File, remove_file: bool = False):
    filename = file.filename
    with logger.contextualize(filename=filename):
        with open(filename, "r") as file_open:
            result = await bot.send_document(
                chat_id=chat_id,
                document=file_open,
                caption=file.description,
                parse_mode="HTML"
            )
            logger.debug(f"Sent file to user")

        if remove_file:
            os.remove(filename)
            logger.debug(f"Removed internal file")

    return result


async def extract_user_data(user_id: int) -> Files:
    """Extract data for the given user, creating files that must be read afterwards for sending through Telegram.
    Returns File objects, which include the filename (path) and description of each file.
    """
    messages = get_messages()
    logger.debug("Extracting user data")

    # When adding more extractors, use asyncio.gather
    stops_data = await UserDataExtractors.stops(user_id)

    return [
        File(filename=stops_data, description=messages.extracted_data.stops.description)
    ]
