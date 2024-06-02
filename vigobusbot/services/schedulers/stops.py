import asyncio
from typing import Dict, Set

from .base import BaseScheduler
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.models import Stop
from vigobusbot.persistence import StopsRepository, StopsElasticSearchRepository
from vigobusbot.utils import async_gather_limited, jsonable_dict
from vigobusbot.logger import logger

__all__ = ["StopUpdaterService", "StopSyncToElasticService"]


class StopUpdaterService(BaseScheduler):

    async def _worker(self):
        prev_stops_etag, current_stops_etag = await asyncio.gather(
            StopsRepository.get_repository().get_stops_etag(),
            VigoBusAPI.get_instance().get_all_stops_etag(),
        )

        if prev_stops_etag == current_stops_etag:
            logger.bind(stops_etag=current_stops_etag).debug("Stops ETag not changed")
            return

        logger.bind(stops_etag_prev=prev_stops_etag, stops_etag_new=current_stops_etag).\
            debug("Stops ETag changed, requesting stops and updating...")

        current_stops, saved_stops, _ = await asyncio.gather(
            VigoBusAPI.get_instance().get_all_stops(),
            StopsRepository.get_repository().get_all_stops(),
            StopsRepository.get_repository().save_stops_etag(current_stops_etag)
        )
        current_stops = {stop.id: stop for stop in current_stops}
        current_stops_ids = set(current_stops.keys())
        saved_stops = {stop.id: stop for stop in saved_stops}
        saved_stops_ids = set(saved_stops.keys())

        same_stops_ids = current_stops_ids.intersection(saved_stops_ids)
        new_stops_ids = current_stops_ids.difference(saved_stops_ids)
        deleted_stops_ids = saved_stops_ids.difference(current_stops_ids)

        await async_gather_limited(
            # Existing stops
            *[self._process_existing_stop(
                saved_stop=saved_stops[stop_id],
                current_stop=current_stops[stop_id]
            ) for stop_id in same_stops_ids],

            # New stops
            *[self._process_new_stop(current_stops[stop_id])
              for stop_id in new_stops_ids],

            # Deleted stops
            *[self._process_deleted_stop(stop_id) for stop_id in deleted_stops_ids],

            limit=5,  # TODO add to settings
        )

    @classmethod
    async def _process_existing_stop(cls, saved_stop: Stop, current_stop: Stop):
        # noinspection PyBroadException
        try:
            saved_stop_dict = saved_stop.dict(exclude={"metadata"})
            current_stop_dict = current_stop.dict(exclude={"metadata"})

            if saved_stop_dict == current_stop_dict:
                logger.bind(stop_data=saved_stop_dict).trace("Stop not changed")
                return

            logger.bind(stop_old_data=saved_stop_dict, stop_new_data=current_stop_dict).info("Stop changed")
            await StopsRepository.get_repository().save_stop(current_stop)
        except Exception:
            logger.opt(exception=True).bind(stop_id=saved_stop.id).error("Failed processing existing stop")

    @classmethod
    async def _process_new_stop(cls, stop: Stop):
        # noinspection PyBroadException
        try:
            logger.bind(stop_data=stop.dict()).info("New Stop detected")
            await StopsRepository.get_repository().save_stop(stop)
        except Exception:
            logger.opt(exception=True).bind(stop_id=stop.id).error("Failed processing new stop")

    @classmethod
    async def _process_deleted_stop(cls, stop_id: int):
        with logger.contextualize(stop_id=stop_id):
            # noinspection PyBroadException
            try:
                logger.info("Stop not detected, considering no longer existing")
                await StopsRepository.get_repository().delete_stop(stop_id)
            except Exception:
                logger.opt(exception=True).error("Failed processing deleted stop")


class StopSyncToElasticService(BaseScheduler):
    _repo_stops: Dict[int, Stop]
    _elastic_stops: Dict[int, Stop]

    async def _worker(self):
        self._repo_stops = dict()
        self._elastic_stops = dict()

        try:
            await asyncio.gather(
                self._fetch_repo_stops(),
                self._fetch_elastic_stops(),
            )
            await asyncio.gather(
                self._sync_repository_to_elastic(),
                self._sync_elastic_to_repository(),
            )
        finally:
            self._repo_stops.clear()
            self._elastic_stops.clear()

    async def _fetch_repo_stops(self):
        """Read and store in local cache the currently saved stops from the main repository.
        """
        # noinspection PyTypeChecker
        async for repo_stop in StopsRepository.get_repository().iter_all_stops():  # type: Stop
            self._repo_stops[repo_stop.id] = repo_stop
        logger.trace(f"{len(self._repo_stops)} stops read from main repository")

    async def _fetch_elastic_stops(self):
        # noinspection PyTypeChecker
        async for elastic_stop in StopsElasticSearchRepository.get_repository().iter_all_stops():  # type: Stop
            self._elastic_stops[elastic_stop.id] = elastic_stop
        logger.trace(f"{len(self._elastic_stops)} stops read from ElasticSearch repository")

    async def _sync_repository_to_elastic(self):
        """Synchronize the Stops in the main repository, to Elastic,
        by adding new stops and updating existing stops.
        """
        save_stops_to_elastic: list[Stop] = list()
        for stop_id, repo_stop in self._repo_stops.items():
            elastic_stop = self._elastic_stops.get(stop_id)
            repo_stop_jsonable = jsonable_dict(repo_stop)
            if not elastic_stop:
                logger.bind(stop_data=repo_stop_jsonable).trace("New stop to persist in Elastic")
                save_stops_to_elastic.append(repo_stop)
            else:
                elastic_stop_jsonable = jsonable_dict(elastic_stop)
                if repo_stop_jsonable != elastic_stop_jsonable:
                    logger.bind(repo_stop_data=repo_stop_jsonable, elastic_stop_data=elastic_stop_jsonable).\
                        trace("Modified stop to update in Elastic")
                    save_stops_to_elastic.append(repo_stop)

        await async_gather_limited(
            *[self._save_stop_in_elastic(stop) for stop in save_stops_to_elastic],
            limit=5,  # TODO add to settings
        )

    async def _sync_elastic_to_repository(self):
        """Synchronize the Stops in Elastic, to the main repository,
        by removing from Elastic those stops that no longer exist in the repository.
        """
        delete_stops_ids = self._elastic_stops_ids.difference(self._repo_stops_ids)

        await async_gather_limited(
            *[self._delete_stop_id_from_elastic(stop_id) for stop_id in delete_stops_ids],
            limit=5,  # TODO add to settings
        )

    @property
    def _repo_stops_ids(self) -> Set[int]:
        return set(self._repo_stops.keys())

    @property
    def _elastic_stops_ids(self) -> Set[int]:
        return set(self._elastic_stops.keys())

    @classmethod
    async def _save_stop_in_elastic(cls, stop: Stop):
        with logger.contextualize(stop_id=stop.id, stop_name=stop.name):
            # noinspection PyBroadException
            try:
                logger.info("Saving stop in Elastic")
                await StopsElasticSearchRepository.save_stop(stop)
            except Exception:
                logger.opt(exception=True).error("Failed saving stop in Elastic")

    @classmethod
    async def _delete_stop_id_from_elastic(cls, stop_id: int):
        with logger.contextualize(stop_id=stop_id):
            # noinspection PyBroadException
            try:
                logger.info("Deleting stop from Elastic")
                await StopsElasticSearchRepository.delete_stop(stop_id)
            except Exception:
                logger.opt(exception=True).error("Failed deleting stop from Elastic")
