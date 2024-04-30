import abc
from typing import Type, Optional, List, Union

import tenacity
import aiocouch.exception

from .base import BaseRepository
from vigobusbot.services import encryption
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.models import mapper, SavedUserStop, SavedUserStopPersist


class SavedUserStopsRepository(BaseRepository):
    @classmethod
    def get_repository(cls) -> Type["SavedUserStopsRepository"]:
        return SavedUserStopsCouchDBRepository

    @classmethod
    @abc.abstractmethod
    async def get_user_all_stops(cls, user_id: int) -> List[SavedUserStop]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def get_user_single_stop(cls, user_id: int, stop_id: int, return_existence: bool = False) -> Union[SavedUserStop, None, bool]:
        """Return a single SavedUserStop, or None if not found.
        If return_existence=True, return if the saved stop exists by the user as True/False."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def save_user_stop(cls, stop: SavedUserStop):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def delete_user_single_stop(cls, user_id: int, stop_id: int):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def delete_user_all_stops(cls, user_id: int):
        raise NotImplementedError


class SavedUserStopsCouchDBRepository(SavedUserStopsRepository):
    _conflict_retry = tenacity.retry_if_exception_type(aiocouch.exception.ConflictError)
    _retry_stop = tenacity.stop_after_attempt(5)

    @classmethod
    async def get_user_all_stops(cls, user_id: int) -> List[SavedUserStop]:
        query = {
            "user_id": encryption.encode_user_id(user_id)
        }

        results = list()
        async for doc in CouchDB.get_instance().db_user_stops.find(query):
            stop_read = SavedUserStopPersist(**doc.data)
            results.append(mapper.map(stop_read, SavedUserStop, user_id=user_id))

        return results

    @classmethod
    async def get_user_single_stop(cls, user_id: int, stop_id: int, return_existence: bool = False):
        doc = await cls._get_user_single_stop_document(user_id, stop_id)
        found = bool(doc) and doc.exists
        if return_existence:
            return found
        if not found:
            return None

        stop_read = SavedUserStopPersist(**doc.data)
        return mapper.map(stop_read, SavedUserStop, user_id=user_id)

    @classmethod
    async def save_user_stop(cls, stop: SavedUserStop):
        stop_persist: SavedUserStopPersist = mapper.map(stop, SavedUserStopPersist)
        doc_id = stop_persist.key
        doc = stop_persist.dict()

        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                await CouchDB.update_doc(
                    db=CouchDB.get_instance().db_user_stops,
                    doc_id=doc_id,
                    doc_data=doc
                )

    @classmethod
    async def delete_user_single_stop(cls, user_id: int, stop_id: int) -> bool:
        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                doc = await cls._get_user_single_stop_document(user_id, stop_id)
                if not doc:
                    return False

                await doc.delete(discard_changes=True)
                return True

    @classmethod
    async def delete_user_all_stops(cls, user_id: int):
        all_stops = await cls.get_user_all_stops(user_id)
        for stop in all_stops:
            doc = await cls._get_user_single_stop_document(user_id, stop.stop_id)
            if doc and doc.exists:
                await doc.delete(discard_changes=True)

    @classmethod
    async def _get_user_single_stop_document(cls, user_id: int, stop_id: int) -> Optional[aiocouch.Document]:
        query = {
            "user_id": encryption.encode_user_id(user_id),
            "stop_id": stop_id
        }

        async for doc in CouchDB.get_instance().db_user_stops.find(query, limit=1):
            return doc
