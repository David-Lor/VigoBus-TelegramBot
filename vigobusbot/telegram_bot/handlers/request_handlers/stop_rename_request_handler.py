"""STOP RENAME REQUEST HANDLER
Handler and utils for working with Stop Rename requests
"""

# # Installed # #
import aiogram
import pydantic
import cachetools

# # Project # #
from ....static_handler import get_messages
from ....vigobus_api import get_stop
from ....persistence_api import saved_stops

__all__ = (
    "StopRenameRequestContext",
    "register_stop_rename_request", "stop_rename_request_reply_handler", "is_stop_rename_request_registered"
)

_stop_rename_requests = cachetools.TTLCache(maxsize=2, ttl=3600)
"""Storage for Stop Rename requests, which must be replied by users in less than 1 hour (3600s).
Key=force_reply_message_id
Value=StopRenameRequestContext
"""


class StopRenameRequestContext(pydantic.BaseModel):
    stop_id: int
    user_id: int
    original_stop_message_id: int
    force_reply_message_id: int


def register_stop_rename_request(context: StopRenameRequestContext):
    _stop_rename_requests[context.force_reply_message_id] = context


def is_stop_rename_request_registered(force_reply_message_id: int) -> bool:
    return force_reply_message_id in _stop_rename_requests


async def stop_rename_request_reply_handler(user_reply_message: aiogram.types.Message):
    rename_context = _stop_rename_requests.pop(user_reply_message.reply_to_message.message_id)
    new_stop_name = user_reply_message.text
    chat_id = user_reply_message.chat.id
    messages = get_messages()
    # TODO restrictions and filters on user stop name input

    await saved_stops.save_stop(
        user_id=chat_id,
        stop_id=rename_context.stop_id,
        stop_name=new_stop_name
    )

    stop = await get_stop(rename_context.stop_id)
    await user_reply_message.bot.send_message(
        chat_id=chat_id,
        text=messages.stop_rename.renamed_successfully.format(
            stop_id=rename_context.stop_id,
            stop_name=stop.name,
            custom_stop_name=new_stop_name
        ),
        reply_to_message_id=user_reply_message.message_id
    )

    # TODO Edit original message with new Stop data
