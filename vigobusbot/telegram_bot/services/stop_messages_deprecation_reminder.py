"""STOP MESSAGES DEPRECATION REMINDER
For the Stop messages sent to users, modify them with a warning/reminder when the messages are outdated for a long time.
"""

import asyncio

import aiogram

from .sent_messages_persistence import sent_messages_cache, sent_messages_cache_lock, MessagePersist, PersistMessageTypes
from vigobusbot.static_handler import get_messages
from vigobusbot.settings_handler import telegram_settings
from vigobusbot.utils import get_datetime_now_utc
from vigobusbot.logger import logger


async def stop_messages_deprecation_reminder_worker(bot: aiogram.Bot):
    if telegram_settings.stop_messages_deprecation_reminder_after_seconds <= 0:
        logger.info("Stop messages deprecation reminder is disabled")
        return

    while True:
        await asyncio.sleep(telegram_settings.stop_messages_deprecation_reminder_loop_delay_seconds)

        now = get_datetime_now_utc()
        ttl = telegram_settings.stop_messages_deprecation_reminder_after_seconds

        async with sent_messages_cache_lock:
            cached_messages = list(sent_messages_cache.values())

        for msg in cached_messages:
            if msg.message_type == PersistMessageTypes.STOP and msg.is_expired(now=now, ttl_seconds=ttl):
                async with sent_messages_cache_lock:
                    # noinspection PyAsyncCall
                    asyncio.create_task(_process_deprecated_stop_message(bot, msg))
                    sent_messages_cache.pop(msg.message_key)


async def _process_deprecated_stop_message(bot: aiogram.Bot, message: MessagePersist):
    with logger.contextualize(user_id_encoded=message.chat_id_encoded, message_id=message.message.message_id):
        logger.debug("Processing deprecated Stop message...")
        text = message.message.html_text
        text += "\n" + get_messages().stop.deprecated_warning

        # noinspection PyBroadException
        try:
            await bot.edit_message_text(
                chat_id=message.message.chat.id,
                message_id=message.message.message_id,
                text=text,
                reply_markup=message.message.reply_markup,
            )
            logger.debug("Deprecated Stop message updated with warning")

        except aiogram.exceptions.MessageToEditNotFound:
            logger.debug("Deprecated Stop message deleted by the user")

        except Exception:
            logger.opt(exception=True).error("Failed updating deprecated Stop message")
