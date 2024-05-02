"""SENT MESSAGES PERSISTENCE
Persist certain messages sent by the bot to users.
"""

import asyncio

from aiogram.types.message import Message

from vigobusbot.models import SentMessageTypes, SentMessage
from vigobusbot.persistence import SentMessagesRepository


async def persist_sent_message(msg_type: str, message: Message):
    message_persist = SentMessage(
        message_type=msg_type,
        chat_id=message.chat.id,
        message_id=message.message_id,
        message_text=message.html_text,
        message_reply_markup_json=message.reply_markup.as_json() if message.reply_markup else None,
    )

    await SentMessagesRepository.get_repository().save_message(message_persist)


async def persist_sent_stop_message(message: Message):
    """When any Stop message is sent or edited, it must be passed to this method.
    The persistence will be performed in background.
    """
    # noinspection PyAsyncCall
    asyncio.create_task(persist_sent_message(msg_type=SentMessageTypes.STOP, message=message))
