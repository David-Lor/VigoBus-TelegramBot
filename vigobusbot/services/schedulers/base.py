import abc

import aiocron

from vigobusbot.utils import Singleton, SetupTeardown
from vigobusbot.logger import logger

__all__ = ["BaseScheduler"]


class BaseScheduler(abc.ABC, Singleton, SetupTeardown):
    _scheduler: aiocron.Cron = None
    _worker_locked: bool = None

    def __init__(self, cron_schedule: str, limit_concurrency: bool = False):
        if not cron_schedule:
            logger.info(f"Scheduled {self.get_class_name()} is disabled")
            return

        self.limit_concurrency = limit_concurrency
        self._worker_locked = False
        self._scheduler = aiocron.crontab(
            spec=cron_schedule,
            func=self._worker_wrapper,
        )

    async def setup(self):
        if not self._scheduler:
            return

        logger.debug(f"Starting scheduled {self.get_class_name()}...")
        self._scheduler.start()
        logger.bind(cron_expression=self._scheduler.spec).info(f"Scheduled {self.get_class_name()} running")

    async def teardown(self):
        if not self._scheduler:
            return

        logger.debug(f"Stopping scheduled {self.get_class_name()}...")
        self._scheduler.stop()
        logger.info(f"Scheduled {self.get_class_name()} stopped")

    async def _worker_wrapper(self):
        if self.limit_concurrency and self._worker_locked:
            logger.debug(f"Scheduled {self.get_class_name()} worker already running, not executing new iteration")
            return

        try:
            self._worker_locked = True
            logger.trace(f"Scheduled {self.get_class_name()} running iteration...")
            await self._worker()
            logger.trace(f"Scheduled {self.get_class_name()} iteration completed")
        except Exception as ex:
            logger.opt(exception=ex).error(f"Scheduled {self.get_class_name()} iteration failed")
        finally:
            self._worker_locked = False

    @abc.abstractmethod
    async def _worker(self):
        pass
