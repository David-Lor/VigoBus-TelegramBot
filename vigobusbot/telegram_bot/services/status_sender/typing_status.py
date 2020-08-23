"""TYPING STATUS SERVICE
Send "Typing..." status to clients while their requests are being processed
"""

# # Native # #
import asyncio
import contextlib
from time import time
from typing import Dict

# # Installed # #
import aiogram
from aiogram.types import ChatActions

# # Project # #
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger

__all__ = ("start_typing", "stop_typing")

_typing_chats: Dict[int, asyncio.Event] = dict()
"""key=chat_id ; value=asyncio.Event"""


async def _typing_service(bot: aiogram.Bot, chat_id: int, stop_event: asyncio.Event):
    """This coroutine runs as an async background task from start_typing, and can be stopped
    with the given asyncio.Event. It periodically sends the typing chat action to the given chat,
    unless the task runs for longer than a safe time limit
    """
    logger.debug(f"Started Typing chat action")
    started = time()

    while not stop_event.is_set():
        await bot.send_chat_action(
            chat_id=chat_id,
            action=ChatActions.TYPING
        )
        logger.debug("Sent Typing chat action")
        await asyncio.sleep(4.5)

        time_diff = time() - started
        if time_diff >= settings.typing_safe_limit_time:
            logger.bind(typing_action_time=time_diff).warning("Ended Typing chat action due to time exceed")
            stop_typing(chat_id=chat_id)
            return

    logger.debug("Ended Typing chat action cleanly")


async def start_typing(bot: aiogram.Bot, chat_id: int):
    stop_event = asyncio.Event()
    asyncio.get_running_loop().create_task(_typing_service(bot=bot, chat_id=chat_id, stop_event=stop_event))
    stop_typing(chat_id=chat_id)  # ensure multiple typing actions are not running at the same time
    _typing_chats[chat_id] = stop_event


def stop_typing(chat_id: int):
    with contextlib.suppress(KeyError):
        _typing_chats.pop(chat_id).set()
        logger.debug("Asked Typing chat action to end")
