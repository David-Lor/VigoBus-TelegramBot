from .base import BaseScheduler
from vigobusbot.vigobus_api import VigoBusAPI
from vigobusbot.models import Stop
from vigobusbot.persistence import StopsRepository
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
        for stop in await VigoBusAPI.get_instance().get_all_stops():
            await self._process_stop(stop)

    @classmethod
    async def _process_stop(cls, stop: Stop):
        stop_read = await StopsRepository.get_repository().get_stop_by_id(stop.id)
        if not stop_read:
            logger.bind(stop_data=stop.dict()).info("New Stop found")
            await StopsRepository.get_repository().save_stop(stop)
