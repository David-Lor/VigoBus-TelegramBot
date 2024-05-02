import asyncio

import aiogram.types

from .base import BaseScheduler
from vigobusbot.static_handler import get_messages
from vigobusbot.models import SentMessage, SentMessageTypes
from vigobusbot.persistence import SentMessagesRepository
from vigobusbot.telegram_bot import Bot
from vigobusbot.settings_handler import telegram_settings
from vigobusbot.logger import logger
from vigobusbot.utils import json, get_time

__all__ = ["StopMessagesDeprecationReminder"]


class StopMessagesDeprecationReminder(BaseScheduler):

    # noinspection PyAsyncCall
    async def _worker(self):
        max_timestamp = get_time() - telegram_settings.stop_messages_deprecation_reminder_after_seconds

        # noinspection PyTypeChecker
        async for message in SentMessagesRepository.get_repository().iter_messages(
            msg_type=SentMessageTypes.STOP,
            max_timestamp=max_timestamp
        ):  # type: SentMessage
            logger.bind(message_key=message.message_key).trace("Deprecated Stop message ready for notification")
            asyncio.create_task(self._process_message(message))
            asyncio.create_task(SentMessagesRepository.get_repository().delete_message(message.message_key))

    @classmethod
    async def _process_message(cls, message: SentMessage):
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
