import abc
import asyncio
from typing import Type, List, AsyncGenerator, Optional

import tenacity
import aiocouch.exception

from .base import BaseRepository
from vigobusbot.models import Stop, StopPersist, StopsEtagKV, mapper
from vigobusbot.services.couchdb import CouchDB
from vigobusbot.services.elasticsearch import ElasticSearch
from vigobusbot.settings_handler import elastic_settings
from vigobusbot.utils import jsonable_dict

__all__ = ["StopsRepository", "StopsCouchDBRepository", "StopsElasticSearchRepository"]


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

    @classmethod
    @abc.abstractmethod
    async def iter_all_stops(cls) -> AsyncGenerator[Stop, None]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def delete_stop(cls, stop_id: int):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def save_stops_etag(cls, etag: str):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def get_stops_etag(cls) -> Optional[str]:
        raise NotImplementedError

    @classmethod
    async def get_all_stops(cls) -> List[Stop]:
        # noinspection PyTypeChecker
        return [s async for s in cls.iter_all_stops()]

    @classmethod
    async def stop_exists(cls, stop_id: int) -> bool:
        return bool(await cls.get_stop_by_id(stop_id))


class StopsCouchDBRepository(StopsRepository):
    _conflict_retry = tenacity.retry_if_exception_type(aiocouch.exception.ConflictError)
    _retry_stop = tenacity.stop_after_attempt(5)

    @classmethod
    async def _get_stop_by_id_doc(cls, stop_id: int) -> Optional[aiocouch.Document]:
        try:
            return await CouchDB.get_instance().db_stops.get(id=str(stop_id))
        except aiocouch.NotFoundError:
            return None

    @classmethod
    async def get_stop_by_id(cls, stop_id: int) -> Optional[Stop]:
        doc = await cls._get_stop_by_id_doc(stop_id)
        if doc and doc.exists:
            return mapper.map(doc, Stop)

    @classmethod
    async def search_stops_by_name(cls, search_term: str) -> List[Stop]:
        # TODO Decidir si obtener de Elastic solo IDs o Stops completas
        stops_ids = await StopsElasticSearchRepository.search_stops_by_name(search_term)
        return sorted(
            await asyncio.gather(*[
                cls.get_stop_by_id(stop_id)
                for stop_id in stops_ids
            ]),
            key=lambda stop: stop.name,
        )

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

    @classmethod
    async def iter_all_stops(cls) -> AsyncGenerator[Stop, None]:
        async for doc in CouchDB.get_instance().db_stops.find(selector={}):
            if doc.id.isdigit():
                yield mapper.map(doc, Stop)

    @classmethod
    async def delete_stop(cls, stop_id: int):
        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                # TODO Add a "deleted" field and set to True, instead of deleting the document
                doc = await cls._get_stop_by_id_doc(stop_id)
                await doc.delete(discard_changes=True)

    @classmethod
    async def save_stops_etag(cls, etag: str):
        kv = StopsEtagKV(value=etag)
        doc = kv.jsonable_dict()

        async for attempt in tenacity.AsyncRetrying(stop=cls._retry_stop, retry=cls._conflict_retry):
            with attempt:
                await CouchDB.update_doc(
                    db=CouchDB.get_instance().db_stops,
                    doc_id=kv.get_key(),
                    doc_data=doc,
                )

    @classmethod
    async def get_stops_etag(cls) -> Optional[str]:
        try:
            doc = await CouchDB.get_instance().db_stops.get(id=StopsEtagKV.get_key())
        except aiocouch.NotFoundError:
            return None

        kv: StopsEtagKV = mapper.map(doc, StopsEtagKV)
        return kv.value

    @classmethod
    async def stop_exists(cls, stop_id: int) -> bool:
        try:
            result = await CouchDB.get_instance().db_stops.get(id=str(stop_id))
            return result.exists
        except aiocouch.NotFoundError:
            return False


class StopsElasticSearchRepository(StopsRepository):
    """ElasticSarch is only used for storing Stop names.
    The rest of the information is acquired from the other repositories.
    """

    @classmethod
    def get_repository(cls) -> Type["StopsRepository"]:
        return StopsElasticSearchRepository

    @classmethod
    async def get_stop_by_id(cls, stop_id: int) -> Optional[Stop]:
        # ZincSearch seems to not be compatible with client.get() method, so we have to use client.search().
        result = await ElasticSearch.get_instance().client.search(
            index=elastic_settings.stops_index,
            query={
                "match": {
                    "_id": str(stop_id)
                }
            },
            size=1,
        )

        hits = result.body.get("hits", {}).get("hits", [])
        if hits:
            hit = hits[0]
            doc = hit["_source"]
            return mapper.map(doc, Stop)

    @classmethod
    async def search_stops_by_name(cls, search_term: str) -> list[int]:
        result = await ElasticSearch.get_instance().client.search(
            index=elastic_settings.stops_index,
            query={
                "match": {
                    "name": {
                        "query": search_term,
                        "fuziness": "AUTO"
                    }
                }
            },
            source_includes=["id"],
            size=elastic_settings.stops_search_limit,
        )

        hits = result.body.get("hits", {}).get("hits", [])
        stops_ids = list()
        for hit in hits:
            stop_dict = hit["_source"]
            stops_ids.append(stop_dict["id"])

        return stops_ids

    @classmethod
    async def save_stop(cls, stop: Stop):
        await ElasticSearch.get_instance().client.index(
            index=elastic_settings.stops_index,
            id=str(stop.id),
            document=jsonable_dict(stop)
        )

    @classmethod
    async def iter_all_stops(cls) -> AsyncGenerator[Stop, None]:
        # Scroll API seems to not be working in ZincSearch
        result = await ElasticSearch.get_instance().client.search(
            index=elastic_settings.stops_index,
            query={"match_all": {}},
            size=1000000,
        )
        hits = result.body.get("hits", {}).get("hits", [])
        for hit in hits:
            yield mapper.map(hit["_source"], Stop)

    @classmethod
    async def delete_stop(cls, stop_id: int):
        await ElasticSearch.get_instance().client.delete(
            index=elastic_settings.stops_index,
            id=str(stop_id),
        )

    @classmethod
    async def save_stops_etag(cls, etag: str):
        raise NotImplementedError

    @classmethod
    async def get_stops_etag(cls) -> Optional[str]:
        raise NotImplementedError
