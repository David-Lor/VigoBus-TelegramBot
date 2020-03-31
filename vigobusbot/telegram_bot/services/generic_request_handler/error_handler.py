"""SERVICES - GENERIC REQUEST HANDLER - ERROR HANDLER

"""

# # Native # #
import contextlib
import traceback

# # Project # #
from vigobusbot.logger import logger
from vigobusbot.static_handler import get_messages
from vigobusbot.exceptions import StopNotExist, UserRateLimit
from vigobusbot.telegram_bot.entities import RequestSource, Message, CallbackQuery

__all__ = ("handle_exceptions",)


async def notify_error(request_source: RequestSource, text: str):
    """Notify the client about an error while processing its request
    """
    with contextlib.suppress(Exception):
        # TODO Log errors happening here
        if isinstance(request_source, CallbackQuery):
            r = await request_source.bot.answer_callback_query(
                callback_query_id=request_source.id,
                text=text,
                show_alert=True
            )
            logger.debug("Sent error to the user as callback query answer")

        elif isinstance(request_source, Message):
            await request_source.bot.send_message(
                chat_id=request_source.chat.id,
                text=text,
                reply_to_message_id=request_source.message_id
            )
            logger.debug("Sent error to the user as message")


@contextlib.asynccontextmanager
async def handle_exceptions(request_source: RequestSource):
    """ContextManager to handle exceptions while processing a request
    """
    # noinspection PyBroadException
    try:
        yield

    except StopNotExist:
        await notify_error(text=get_messages().stop.not_exists, request_source=request_source)

    except UserRateLimit:
        await notify_error(text=get_messages().generic.rate_limit_error, request_source=request_source)

    except Exception as exception:
        await notify_error(text=get_messages().generic.generic_error, request_source=request_source)

        traceback_msg = ""
        if exception.__traceback__:
            traceback_msg = f"\n{traceback.format_exc()}"

        logger.error(f"Unidentified error while processing a client request ({exception}){traceback_msg}")
