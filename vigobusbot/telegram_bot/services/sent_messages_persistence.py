"""SENT MESSAGES PERSISTENCE
Persist certain messages sent by the bot to users.
"""

import asyncio
import datetime
from typing import Dict

import pydantic
from aiogram.types.message import Message

from vigobusbot.persistence_api.saved_stops.services.encoder import encode_user_id
from vigobusbot.utils import get_datetime_now_utc


class PersistMessageTypes:
    STOP = "stop"


class MessagePersist(pydantic.BaseModel):
    message_type: str
    message: Message
    published_on: datetime.datetime

    # Fields generated from complete_fields() method:
    message_key: str = ""
    chat_id_encoded: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complete_fields()

    def complete_fields(self):
        user_id = self.message.chat.id
        message_id = self.message.message_id
        self.chat_id_encoded = encode_user_id(user_id)
        self.message_key = f"{self.message_type}_{self.chat_id_encoded}_{message_id}"

    def is_expired(self, now: datetime.datetime, ttl_seconds: int) -> bool:
        return (now - self.published_on).seconds >= ttl_seconds

    class Config:
        arbitrary_types_allowed = True


sent_messages_cache: Dict[str, MessagePersist] = dict()
"""`{ message_key : message }`"""
sent_messages_cache_lock = asyncio.Lock()


async def persist_sent_message(msg_type: str, message: Message):
    message_persist = MessagePersist(
        message_type=msg_type,
        message=message,
        published_on=get_datetime_now_utc(),
    )
    async with sent_messages_cache_lock:
        sent_messages_cache[message_persist.message_key] = message_persist


async def persist_sent_stop_message(message: Message):
    """When any Stop message is sent or edited, it must be passed to this method.
    """
    # noinspection PyAsyncCall
    asyncio.create_task(persist_sent_message(msg_type=PersistMessageTypes.STOP, message=message))
