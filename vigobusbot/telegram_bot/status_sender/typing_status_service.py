"""WRITING STATUS SERVICE
Service to send Typing status to clients while their requests are being processed
"""

# # Native # #
import asyncio
import contextlib
from time import time
from typing import Dict

# # Installed # #
import aiogram

# # Project # #
from ...settings_handler import telegram_settings as settings
from ...logger import *

__all__ = ("start_typing", "stop_typing")

typing_chats: Dict[int, asyncio.Event] = dict()  # { chat_id: event }


async def typing_service(bot: aiogram.Bot, chat_id: int, stop_event: asyncio.Event):
    logger.debug(f"Started Typing chat action (chat={chat_id})")
    started = time()

    while not stop_event.is_set():
        await bot.send_chat_action(
            chat_id=chat_id,
            action=aiogram.types.ChatActions.TYPING
        )
        logger.debug(f"Sent Typing chat action (chat={chat_id})")
        await asyncio.sleep(4.5)

        time_diff = time() - started
        if time_diff >= settings.typing_safe_limit_time:
            logger.debug(f"Ended Typing chat action (chat={chat_id}) by time exceed (t={int(time_diff)}")
            stop_typing(chat_id)
            return

    logger.debug(f"Ended Typing chat action (chat={chat_id})")


async def start_typing(bot: aiogram.Bot, chat_id: int):
    stop_event = asyncio.Event()
    asyncio.get_running_loop().create_task(typing_service(bot=bot, chat_id=chat_id, stop_event=stop_event))
    typing_chats[chat_id] = stop_event


def stop_typing(chat_id: int):
    with contextlib.suppress(KeyError):
        typing_chats.pop(chat_id).set()
        logger.debug(f"Asked Typing chat action (chat={chat_id}) to Stop")
