import abc
import asyncio

import aiocron
import contexttimer

from vigobusbot.utils import Singleton, SetupTeardown
from vigobusbot.logger import logger

__all__ = ["BaseScheduler"]


class BaseScheduler(abc.ABC, Singleton, SetupTeardown):
    _scheduler: aiocron.Cron = None
    _worker_locked: bool = None

    def __init__(self, cron_schedule: str, first_run: bool = False, limit_concurrency: bool = False):
        if not cron_schedule:
            logger.info(f"Scheduled {self.get_class_name()} is disabled")
            return

        self.limit_concurrency = limit_concurrency
        self.first_run = first_run
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

        if self.first_run:
            await self.run_now_background()

    async def teardown(self):
        if not self._scheduler:
            return

        logger.debug(f"Stopping scheduled {self.get_class_name()}...")
        self._scheduler.stop()
        logger.info(f"Scheduled {self.get_class_name()} stopped")

    async def run_now(self):
        await self._worker_wrapper()

    async def run_now_background(self):
        await asyncio.create_task(self.run_now())

    async def _worker_wrapper(self):
        if self.limit_concurrency and self._worker_locked:
            logger.info(f"Scheduled {self.get_class_name()} worker already running, not executing new iteration")
            return

        try:
            with contexttimer.Timer() as timer:
                self._worker_locked = True
                logger.debug(f"Scheduled {self.get_class_name()} running iteration...")
                await self._worker()
                logger.bind(elapsed=timer.elapsed).debug(f"Scheduled {self.get_class_name()} iteration completed")
        except Exception as ex:
            logger.opt(exception=ex).error(f"Scheduled {self.get_class_name()} iteration failed")
        finally:
            self._worker_locked = False

    @abc.abstractmethod
    async def _worker(self):
        pass
