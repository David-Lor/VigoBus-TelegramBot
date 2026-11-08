"""FEEDBACK REQUEST HANDLER
Handler and utils for working with Feedback requests, involving Force Reply handling
"""

import asyncio
import contextlib
from typing import Optional

import cachetools
import pydantic
import aiogram

from vigobusbot.static_handler import get_messages
from vigobusbot.settings import TelegramSettings, SettingsLoadedSignal
from vigobusbot.logger import logger
from vigobusbot.utils import SingletonHold

__all__ = (
    "FeedbackRequestContext", "register_feedback_request",
    "get_feedback_request_context", "handle_feedback_request_reply"
)

_feedback_requests: SingletonHold[cachetools.Cache[int, "FeedbackRequestContext"]] = SingletonHold()
"""Storage for Feedback requests, which must be replied by users in less than the force_reply_ttl
Key=force_reply_message_id
Value=FeedbackRequestContext
"""


@SettingsLoadedSignal.connect
def _on_settings_loaded(*_, **__):
    cache = cachetools.TTLCache(maxsize=float("inf"), ttl=TelegramSettings.get().force_reply_ttl)
    _feedback_requests.set_value(cache)
    logger.bind(cache_maxsize=cache.maxsize).debug("Initialized FeedbackRequestContext cache")


class FeedbackRequestContext(pydantic.BaseModel):
    user_id: int
    force_reply_message_id: int


def register_feedback_request(user_id: int, force_reply_message_id: int):
    if (cache := _feedback_requests.get_value()) is None:
        return

    context = FeedbackRequestContext(user_id=user_id, force_reply_message_id=force_reply_message_id)
    cache[context.force_reply_message_id] = context
    logger.bind(force_reply_message_id=force_reply_message_id).debug("Registered Feedback Request for message")


def get_feedback_request_context(
        force_reply_message_id: Optional[int] = None, user_id: Optional[int] = None, pop: bool = True
) -> Optional[FeedbackRequestContext]:
    if (cache := _feedback_requests.get_value()) is None:
        return None

    result: Optional[FeedbackRequestContext] = None

    if user_id and not force_reply_message_id:
        with contextlib.suppress(StopIteration):
            force_reply_message_id = next(
                force_reply_message_id
                for force_reply_message_id, context
                in cache.items()
                if context.user_id == user_id
            )

    if force_reply_message_id:
        with contextlib.suppress(KeyError):
            if pop:
                result = cache.pop(force_reply_message_id)
            else:
                result = cache[force_reply_message_id]

    logger.bind(
        force_reply_message_id=force_reply_message_id,
        with_user_id=bool(user_id),
        pop_result=pop
    ).debug(f"{'Found' if result else 'Not Found'} FeedbackRequestContext")
    return result


async def handle_feedback_request_reply(user_reply_message: aiogram.types.Message):
    """This handler is called from message handlers when a user replies to a Feedback ForceReply request.
    The user replies with the message that wants to send to the bot admin.
    """
    message_text = user_reply_message.text
    chat_id = user_id = user_reply_message.chat.id
    request_context = get_feedback_request_context(user_id=user_id, pop=True)
    messages = get_messages()
    logger.bind(user_id=user_id, message_text=message_text).info("Received Feedback message")

    await user_reply_message.bot.send_message(
        chat_id=TelegramSettings.get().admin_userid,
        text=messages.feedback.send_admin.format(user_id=chat_id, message_text=message_text)
    )

    # Confirmation message send to the user
    confirmation_coro = user_reply_message.bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=user_reply_message.message_id,
        text=messages.feedback.success
    )
    # Delete the original message with the ForceReply markup sent by the bot
    delete_original_message_coro = user_reply_message.bot.delete_message(
        chat_id=chat_id,
        message_id=request_context.force_reply_message_id
    )

    logger.debug("Sending confirmation to user and message to admin")
    await asyncio.gather(confirmation_coro, delete_original_message_coro)
