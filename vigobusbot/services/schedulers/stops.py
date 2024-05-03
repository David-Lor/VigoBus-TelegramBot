import asyncio

from .base import BaseScheduler
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.models import Stop
from vigobusbot.persistence import StopsRepository
from vigobusbot.utils import async_gather_limited
from vigobusbot.logger import logger

__all__ = ["StopUpdaterService"]


class StopUpdaterService(BaseScheduler):
    last_etag: str = ""

    async def _worker(self):
        stops_etag = await VigoBusAPI.get_instance().get_all_stops_etag()
        # TODO Persist ETag in repository
        if stops_etag == self.last_etag:
            logger.bind(stops_etag=stops_etag).debug("Stops ETag not changed")
            return

        logger.bind(stops_etag=stops_etag).debug("Stops ETag changed, requesting stops and updating...")
        self.last_etag = stops_etag

        current_stops, saved_stops = await asyncio.gather(
            VigoBusAPI.get_instance().get_all_stops(),
            StopsRepository.get_repository().get_all_stops(),
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

            limit=5
        )

    @classmethod
    async def _process_existing_stop(cls, saved_stop: Stop, current_stop: Stop):
        saved_stop_dict = saved_stop.dict(exclude={"metadata"})
        current_stop_dict = current_stop.dict(exclude={"metadata"})

        if saved_stop_dict == current_stop_dict:
            logger.bind(stop_data=saved_stop_dict).trace("Stop not changed")
            return

        logger.bind(stop_old_data=saved_stop_dict, stop_new_data=current_stop_dict).info("Stop changed")
        await StopsRepository.get_repository().save_stop(current_stop)

    @classmethod
    async def _process_new_stop(cls, stop: Stop):
        logger.bind(stop_data=stop.dict()).info("New Stop detected")
        await StopsRepository.get_repository().save_stop(stop)

    @classmethod
    async def _process_deleted_stop(cls, stop_id: int):
        logger.bind(stop_id=stop_id).info("Stop not detected, considering no longer existing")
        await StopsRepository.get_repository().delete_stop(stop_id)
