"""FEEDBACK REQUEST HANDLER
Handler and utils for working with Feedback requests, involving Force Reply handling
"""

# # Native # #
import contextlib
from typing import Optional

# # Installed # #
import cachetools
import pydantic
import aiogram

# # Project # #
from vigobusbot.static_handler import get_messages
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger

__all__ = (
    "FeedbackRequestContext", "register_feedback_request",
    "get_feedback_request_context", "handle_feedback_request_reply"
)

_feedback_requests = cachetools.TTLCache(maxsize=float("inf"), ttl=settings.force_reply_ttl)
"""Storage for Feedback requests, which must be replied by users in less than the force_reply_ttl
Key=force_reply_message_id
Value=FeedbackRequestContext
"""


class FeedbackRequestContext(pydantic.BaseModel):
    user_id: int
    force_reply_message_id: int


def register_feedback_request(user_id: int, force_reply_message_id: int):
    context = FeedbackRequestContext(user_id=user_id, force_reply_message_id=force_reply_message_id)
    _feedback_requests[context.force_reply_message_id] = context
    logger.debug(f"Registered Feedback Request for message {force_reply_message_id}")


def get_feedback_request_context(
        force_reply_message_id: Optional[int] = None, user_id: Optional[int] = None, pop: bool = True
) -> Optional[FeedbackRequestContext]:
    result: Optional[FeedbackRequestContext] = None

    if user_id and not force_reply_message_id:
        with contextlib.suppress(StopIteration):
            force_reply_message_id = next(
                force_reply_message_id
                for force_reply_message_id, context
                in _feedback_requests.items()
                if context.user_id == user_id
            )

    if force_reply_message_id:
        with contextlib.suppress(KeyError):
            if pop:
                result = _feedback_requests.pop(force_reply_message_id)
            else:
                result = _feedback_requests[force_reply_message_id]

    logger.debug(
        f"{'Found' if result else 'Not Found'} FeedbackRequestContext" +
        f"{f'ForceReplyMessageID={force_reply_message_id} ' if force_reply_message_id else ''}" +
        f"{f' With-UserID' if user_id else ' No-UserID'}" +
        (" (Pop)" if pop else " (No-Pop)")
    )
    return result


async def handle_feedback_request_reply(user_reply_message: aiogram.types.Message):
    """This handler is called from message handlers when a user replies to a Feedback ForceReply request.
    The user replies with the message that wants to send to the bot admin.
    """
    message_text = user_reply_message.text
    chat_id = user_reply_message.chat.id
    messages = get_messages()

    logger.info(
        f"Received Feedback message from user {chat_id} with the text (length={len(message_text)}):\n{message_text}"
    )

    await user_reply_message.bot.send_message(
        chat_id=settings.admin_userid,
        text=messages.feedback.send_admin.format(user_id=chat_id, message_text=message_text)
    )
    await user_reply_message.bot.send_message(
        chat_id=chat_id,
        text=messages.feedback.success
    )
