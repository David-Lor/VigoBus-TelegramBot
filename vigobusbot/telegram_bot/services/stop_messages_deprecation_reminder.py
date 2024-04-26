"""STOP MESSAGES DEPRECATION REMINDER
For the Stop messages sent to users, modify them with a warning/reminder when the messages are outdated for a long time.
"""

import json
import asyncio

import aiocron
import aiogram

from vigobusbot.models import SentMessageTypes, SentMessage
from vigobusbot.persistence.sent_messages import SentMessagesRepository
from vigobusbot.static_handler import get_messages
from vigobusbot.telegram_bot.bot import Bot
from vigobusbot.settings_handler import telegram_settings
from vigobusbot.logger import logger
from vigobusbot.utils import Singleton, SetupTeardown, get_time


class StopMessagesDeprecationReminder(Singleton, SetupTeardown):
    _scheduler: aiocron.Cron

    def __init__(self):
        self._scheduler = aiocron.crontab(
            spec=telegram_settings.stop_messages_deprecation_reminder_cron,
            func=self._worker,
        )

    async def setup(self):
        logger.debug("Starting Stop messages deprecation reminder...")
        self._scheduler.start()
        logger.bind(cron_expression=self._scheduler.spec).info(f"Stop messages deprecation reminder running")

    async def teardown(self):
        logger.debug("Stopping Stop messages deprecation reminder...")
        self._scheduler.stop()
        logger.info("Stop messages deprecation reminder stopped")

    @classmethod
    async def _worker(cls):
        # noinspection PyBroadException
        try:
            msg_count = 0
            max_timestamp = get_time() - telegram_settings.stop_messages_deprecation_reminder_after_seconds

            # noinspection PyTypeChecker
            async for message in SentMessagesRepository.get_repository().iter_messages(
                    msg_type=SentMessageTypes.STOP,
                    max_timestamp=max_timestamp
            ):  # type: SentMessage
                msg_count += 1

                # TODO Catch&Log exceptions of tasks (here or in repo)
                # noinspection PyAsyncCall
                asyncio.create_task(cls._process_deprecated_stop_message(message))
                # noinspection PyAsyncCall
                asyncio.create_task(SentMessagesRepository.get_repository().delete_message(message.message_key))

            logger.bind(msg_count=msg_count).trace("Stop messages deprecation reminder: worker loop completed")

        except Exception:
            logger.opt(exception=True).error("Stop messages deprecation reminder: worker loop failed")

    @classmethod
    async def _process_deprecated_stop_message(cls, message: SentMessage):
        # TODO Add chat_id_encoded to logger (but this field is only present in SentMessagePersist, make available in SentMessage? find best canonical way)
        logger.debug("Processing deprecated Stop message...")

        # noinspection PyBroadException
        try:
            text = message.message_text
            text += "\n" + get_messages().stop.deprecated_warning

            reply_markup = None
            if message.message_reply_markup_json:
                reply_markup_dict = json.loads(message.message_reply_markup_json)
                reply_markup = aiogram.types.InlineKeyboardMarkup(**reply_markup_dict)

            await Bot.get_instance().edit_message_text(
                chat_id=message.chat_id,
                message_id=message.message_id,
                text=text,
                reply_markup=reply_markup,
            )
            logger.debug("Deprecated Stop message updated with warning")

        except aiogram.exceptions.MessageToEditNotFound:
            logger.debug("Deprecated Stop message deleted by the user")

        except Exception:
            logger.opt(exception=True).error("Failed updating deprecated Stop message")
