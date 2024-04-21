"""SENT MESSAGES PERSISTENCE
Persist certain messages sent by the bot to users.
"""

import asyncio
from typing import Tuple, Optional

import pydantic
from aiogram.types.message import Message

from vigobusbot.services.couchdb import CouchDB
from vigobusbot.services.encryption import encode_user_id, encrypt_general_data, encrypt_user_data
from vigobusbot.utils import get_time


class PersistMessageTypes:
    STOP = "stop"


class MessagePersist(pydantic.BaseModel):
    message_type: str
    published_on: int  # unix timestamp, UTC, seconds precision
    message_id: int
    message_text_encrypted: str
    message_reply_markup_json_encrypted: Optional[str]
    chat_id_encoded: str
    chat_id_encrypted: str

    # Fields generated from complete_fields() method:
    message_key: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complete_fields()

    def complete_fields(self):
        if not self.message_key:
            self.message_key = f"{self.message_type}_{self.chat_id_encoded}_{self.message_id}"

    def is_expired(self, now: int, ttl_seconds: int) -> bool:
        return (now - self.published_on) >= ttl_seconds

    def to_document(self) -> Tuple[str, dict]:
        return self.message_key, self.dict(exclude={"message_key"})

    @classmethod
    def from_document(cls, doc_id: str, doc_data: dict) -> "MessagePersist":
        return cls(message_key=doc_id, **doc_data)

    class Config:
        arbitrary_types_allowed = True


async def persist_sent_message(msg_type: str, message: Message):
    user_id = message.chat.id
    message_persist = MessagePersist(
        message_type=msg_type,
        published_on=get_time(),
        message_id=message.message_id,
        message_text_encrypted=encrypt_user_data(user_id=user_id, data=message.html_text),
        message_reply_markup_json_encrypted=encrypt_user_data(user_id=user_id, data=message.reply_markup.as_json()) if message.reply_markup else None,
        chat_id_encoded=encode_user_id(user_id),
        chat_id_encrypted=encrypt_general_data(str(user_id))
    )

    doc_id, doc_data = message_persist.to_document()
    # noinspection PyAsyncCall
    await CouchDB.update_doc(
        db=CouchDB.get_instance().db_sent_messages,
        doc_id=doc_id,
        doc_data=doc_data
    )


async def persist_sent_stop_message(message: Message):
    """When any Stop message is sent or edited, it must be passed to this method.
    The persistence will be performed in background.
    """
    # noinspection PyAsyncCall
    asyncio.create_task(persist_sent_message(msg_type=PersistMessageTypes.STOP, message=message))
