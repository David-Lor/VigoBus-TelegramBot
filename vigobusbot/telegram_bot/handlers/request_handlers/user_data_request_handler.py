"""USER DATA REQUEST HANDLER
Handler and utils for working with User Data Extraction requests
"""

# # Native # #
import os
import json

# # Installed # #
import aiogram

# # Project # #
from ....persistence_api.saved_stops import get_user_saved_stops
from ....vigobus_api.stop_getter import fill_saved_stops_info
from ....static_handler import get_messages
from ....entities import *
from ....logger import *

__all__ = ("extract_user_data", "send_file")


class UserDataExtractors:
    """Methods to extract user data to a file.
    Return the filename (path) where the data is saved.
    """
    @staticmethod
    async def stops(user_id: int) -> str:
        messages = get_messages()
        saved_stops = await get_user_saved_stops(user_id)
        await fill_saved_stops_info(saved_stops)
        stops_dict = [stop.dict() for stop in saved_stops]

        filename = f"/tmp/{user_id}_{messages.extracted_data.stops.filename}"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(stops_dict, file, indent=2)

        return filename


async def send_file(bot: aiogram.Bot, chat_id: int, file: File, remove_file: bool = False):
    filename = file.filename
    with open(filename, "r") as file_open:
        result = await bot.send_document(
            chat_id=chat_id,
            document=file_open,
            caption=file.description,
            parse_mode="Markdown"
        )
        logger.debug(f"Sent file {filename} to {chat_id} - result: {result}")

    if remove_file:
        os.remove(filename)
        logger.debug(f"Removed internal file {filename}")

    return result


async def extract_user_data(user_id: int) -> Files:
    """Extract data for the given user, creating files that must be read afterwards for sending through Telegram.
    Returns File objects, which include the filename (path) and description of each file.
    """
    messages = get_messages()
    logger.debug(f"Extracting user data for user {user_id}")

    # When adding more extractors, use asyncio.gather
    stops_data = await UserDataExtractors.stops(user_id)

    return [
        File(filename=stops_data, description=messages.extracted_data.stops.description)
    ]
