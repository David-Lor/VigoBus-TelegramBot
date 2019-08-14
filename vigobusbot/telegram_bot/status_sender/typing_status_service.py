"""WRITING STATUS SERVICE
Service to send Typing status to clients while their requests are being processed
"""

# # Native # #
import asyncio
from typing import Dict

# # Installed # #
import aiogram

__all__ = ("start_typing", "stop_typing")

typing_chats: Dict[int, asyncio.Event] = dict()  # { chat_id: event }


async def typing_service(bot: aiogram.Bot, chat_id: int, stop_event: asyncio.Event):
    while not stop_event.is_set():
        await bot.send_chat_action(
            chat_id=chat_id,
            action=aiogram.types.ChatActions.TYPING
        )
        await asyncio.sleep(4.5)


async def start_typing(bot: aiogram.Bot, chat_id: int):
    stop_event = asyncio.Event()
    asyncio.get_running_loop().create_task(typing_service(bot=bot, chat_id=chat_id, stop_event=stop_event))
    typing_chats[chat_id] = stop_event


def stop_typing(chat_id: int):
    try:
        typing_chats.pop(chat_id).set()
    except KeyError:
        pass
