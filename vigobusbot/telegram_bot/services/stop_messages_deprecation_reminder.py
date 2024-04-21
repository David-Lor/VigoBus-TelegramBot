"""STOP MESSAGES DEPRECATION REMINDER
For the Stop messages sent to users, modify them with a warning/reminder when the messages are outdated for a long time.
"""

import json
import asyncio

import aiocron
import aiogram

from .sent_messages_persistence import MessagePersist, PersistMessageTypes
from vigobusbot.services.encryption import decrypt_general_data, decrypt_user_data
from vigobusbot.static_handler import get_messages
from vigobusbot.telegram_bot.bot import Bot
from vigobusbot.services.couchdb import CouchDB
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
        self._scheduler.start()
        logger.info(f"Stop messages deprecation reminder running with cron expression: {self._scheduler.spec}")

    async def teardown(self):
        self._scheduler.stop()

    @classmethod
    async def _worker(cls):
        # noinspection PyBroadException
        try:
            max_timestamp = get_time() - telegram_settings.stop_messages_deprecation_reminder_after_seconds
            query = {
                "message_type": PersistMessageTypes.STOP,
                "published_on": {"$lte": max_timestamp}
            }
            logger.bind(couchdb_query=query).trace("Stop messages deprecation reminder: worker loop start")

            msg_count = 0
            async for doc in CouchDB.get_instance().db_sent_messages.find(query):
                msg_count += 1
                message = MessagePersist.from_document(doc_id=doc.id, doc_data=doc.data)
                # noinspection PyAsyncCall
                asyncio.create_task(cls._process_deprecated_stop_message(message))
                # noinspection PyAsyncCall
                asyncio.create_task(doc.delete(discard_changes=True))

            logger.bind(msg_count=msg_count).trace("Stop messages deprecation reminder: worker loop completed")

        except Exception:
            logger.opt(exception=True).error("Stop messages deprecation reminder: worker loop failed")

    @classmethod
    async def _process_deprecated_stop_message(cls, message: MessagePersist):
        with logger.contextualize(user_id_encoded=message.chat_id_encoded, message_id=message.message_id):
            logger.debug("Processing deprecated Stop message...")

            # noinspection PyBroadException
            try:
                user_id = int(decrypt_general_data(message.chat_id_encrypted))
                text = decrypt_user_data(user_id=user_id, encrypted_data=message.message_text_encrypted)
                text += "\n" + get_messages().stop.deprecated_warning

                reply_markup = None
                if message.message_reply_markup_json_encrypted:
                    reply_markup_json = decrypt_user_data(user_id=user_id, encrypted_data=message.message_reply_markup_json_encrypted)
                    reply_markup_dict = json.loads(reply_markup_json)
                    reply_markup = aiogram.types.InlineKeyboardMarkup(**reply_markup_dict)

                await Bot.get_instance().edit_message_text(
                    chat_id=user_id,
                    message_id=message.message_id,
                    text=text,
                    reply_markup=reply_markup,
                )
                logger.debug("Deprecated Stop message updated with warning")

            except aiogram.exceptions.MessageToEditNotFound:
                logger.debug("Deprecated Stop message deleted by the user")

            except Exception:
                logger.opt(exception=True).error("Failed updating deprecated Stop message")
