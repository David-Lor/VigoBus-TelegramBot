import abc
from typing import Type, List, Optional

import tenacity
import aiocouch.exception

from .base import BaseRepository
from vigobusbot.models import Stop, StopPersist, mapper
from vigobusbot.services.couchdb import CouchDB


class StopsRepository(BaseRepository):
    @classmethod
    def get_repository(cls) -> Type["StopsRepository"]:
        return StopsCouchDBRepository

    @classmethod
    @abc.abstractmethod
    async def get_stop_by_id(cls, stop_id: int) -> Optional[Stop]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def search_stops_by_name(cls, search_term: str) -> List[Stop]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def save_stop(cls, stop: Stop):
        raise NotImplementedError


class StopsCouchDBRepository(StopsRepository):
    _conflict_retry = tenacity.retry_if_exception_type(aiocouch.exception.ConflictError)
    _retry_stop = tenacity.stop_after_attempt(5)

    @classmethod
    async def get_stop_by_id(cls, stop_id: int) -> Optional[Stop]:
        query = {
            "_id": str(stop_id)
        }

        try:
            doc = await CouchDB.get_instance().db_stops.find(query, limit=1).__anext__()
        except (aiocouch.exception.NotFoundError, StopAsyncIteration):
            return None

        stop_read = StopPersist(
            id=doc.id,
            **doc.data
        )
        return mapper.map(stop_read, Stop)

    @classmethod
    async def search_stops_by_name(cls, search_term: str) -> List[Stop]:
        # TODO Sanitize search_term, only letters and numbers
        query = {
            "name": {
                "$regex": f"(?i).*{search_term}.*"
            }
        }

        results: List[Stop] = list()
        async for doc in CouchDB.get_instance().db_user_stops.find(query):
            stop_read = StopPersist(
                id=doc.id,
                **doc.data,
            )
            results.append(mapper.map(stop_read, Stop))

        return results

    @classmethod
    async def save_stop(cls, stop: Stop):
        stop_persist: StopPersist = mapper.map(stop, StopPersist)
        doc_id = str(stop_persist.id)
        doc = stop_persist.jsonable_dict(exclude={"id"})

        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                await CouchDB.update_doc(
                    db=CouchDB.get_instance().db_stops,
                    doc_id=doc_id,
                    doc_data=doc
                )
