import abc
from typing import Type, AsyncGenerator

import tenacity
import aiocouch.exception

from .base import BaseRepository
from vigobusbot.models import mapper, SentMessagePersist, SentMessage
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.logger import logger


class SentMessagesRepository(BaseRepository):
    @classmethod
    def get_repository(cls) -> Type["SentMessagesRepository"]:
        return SentMessagesCouchDBRepository

    @classmethod
    @abc.abstractmethod
    async def save_message(cls, message: SentMessage):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def iter_messages(cls, msg_type: str, max_timestamp: int) -> AsyncGenerator[SentMessage, None]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def delete_message(cls, msg_key: str) -> bool:
        raise NotImplementedError


class SentMessagesCouchDBRepository(SentMessagesRepository):
    _conflict_retry = tenacity.retry_if_exception_type(aiocouch.exception.ConflictError)
    _retry_stop = tenacity.stop_after_attempt(5)

    @classmethod
    async def save_message(cls, message: SentMessage):
        message_persist = mapper.map(message, SentMessagePersist)
        doc_id = message_persist.message_key
        doc = message_persist.dict(exclude={"message_key"})

        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                await CouchDB.update_doc(
                    db=CouchDB.get_instance().db_sent_messages,
                    doc_id=doc_id,
                    doc_data=doc
                )
                logger.bind(message_key=message_persist.message_key).debug("Persisted SentMessage in CouchDB")

    @classmethod
    async def iter_messages(cls, msg_type: str, max_timestamp: int):
        query = {
            "message_type": msg_type,
            "published_on": {"$lte": max_timestamp}
        }

        async for doc in CouchDB.get_instance().db_sent_messages.find(query):
            message_read = SentMessagePersist(
                message_key=doc.id,
                **doc.data
            )
            yield mapper.map(message_read, SentMessage)

    @classmethod
    async def delete_message(cls, msg_key: str) -> bool:
        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                try:
                    doc = await CouchDB.get_instance().db_sent_messages.get(id=msg_key)
                    await doc.delete(discard_changes=True)
                    return True
                except aiocouch.exception.NotFoundError:
                    return False
