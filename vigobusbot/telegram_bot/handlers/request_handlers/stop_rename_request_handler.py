"""STOP RENAME REQUEST HANDLER
Handler and utils for working with Stop Rename requests
"""

# # Native # #
import re

# # Installed # #
import aiogram
import pydantic
import cachetools
import emoji

# # Project # #
from ....static_handler import get_messages
from ....vigobus_api import get_stop
from ....persistence_api import saved_stops

__all__ = (
    "StopRenameRequestContext",
    "register_stop_rename_request", "stop_rename_request_reply_handler", "is_stop_rename_request_registered"
)

_stop_rename_requests = cachetools.TTLCache(maxsize=float("inf"), ttl=3600)
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


def get_stop_rename_request_context(force_reply_message_id: int) -> StopRenameRequestContext:
    return _stop_rename_requests.pop(force_reply_message_id)


async def stop_rename_request_reply_handler(user_reply_message: aiogram.types.Message):
    rename_context = get_stop_rename_request_context(user_reply_message.reply_to_message.message_id)
    new_stop_name = user_reply_message.text
    remove_custom_name = False
    chat_id = user_reply_message.chat.id
    messages = get_messages()

    # Remove Stop custom name
    if new_stop_name.strip().lower() == messages.stop_rename.unname_command:
        new_stop_name = None
        remove_custom_name = True

    # Set Stop custom name (filter input)
    else:
        new_stop_name = emoji.demojize(new_stop_name)
        new_stop_name = re.sub(
            pattern=messages.stop_rename.regex_sub,
            repl='',
            string=new_stop_name
        )
        new_stop_name = emoji.emojize(new_stop_name)

    await saved_stops.save_stop(
        user_id=chat_id,
        stop_id=rename_context.stop_id,
        stop_name=new_stop_name
    )

    stop = await get_stop(rename_context.stop_id)

    if not remove_custom_name:
        text = messages.stop_rename.renamed_successfully.format(
            stop_id=stop.stopid,
            stop_name=stop.name,
            custom_stop_name=new_stop_name
        )
    else:
        text = messages.stop_rename.unnamed_successfully.format(
            stop_id=stop.stopid,
            stop_name=stop.name
        )

    await user_reply_message.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_to_message_id=user_reply_message.message_id
    )
    # Remove ForceReply message sent by bot to avoid client from getting asked for a reply when reopening the client
    await user_reply_message.bot.delete_message(
        chat_id=chat_id,
        message_id=rename_context.force_reply_message_id
    )

    # TODO Edit original message with new Stop data
