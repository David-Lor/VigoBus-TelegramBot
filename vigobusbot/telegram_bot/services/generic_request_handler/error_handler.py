"""SERVICES - GENERIC REQUEST HANDLER - ERROR HANDLER
Handle errors while processing user requests, notifying the user about the error
"""

import contextlib

from vigobusbot.logger import logger, get_request_id
from vigobusbot.static_handler import get_messages
from vigobusbot.exceptions import StopNotExist, UserRateLimit
from vigobusbot.telegram_bot.entities import RequestSource, Message, CallbackQuery

__all__ = ("handle_exceptions",)


async def notify_error(request_source: RequestSource, text: str, with_request_id: bool = False):
    """Notify the client about an error while processing its request.
    If `with_request_id` is True, add the `request_id` template on the `request_id_text` placeholder, only if
    `request_source` is a Message.
    """
    with logger.contextualize(user_error_message_text=text):  # TODO avoid contextualize (log on first record)
        logger.debug("Notifying user about an error...")

        # noinspection PyBroadException
        try:
            if isinstance(request_source, CallbackQuery):
                await request_source.bot.answer_callback_query(
                    callback_query_id=request_source.id,
                    text=text,
                    show_alert=True
                )
                logger.debug("Sent error to the user as callback query answer")

            elif isinstance(request_source, Message):
                if with_request_id and request_source:
                    request_id = get_request_id()
                    request_id_text = get_messages().generic.request_id.format(request_id=request_id)
                    text = text.format(request_id_text=request_id_text)

                await request_source.bot.send_message(
                    chat_id=request_source.chat.id,
                    text=text,
                    reply_to_message_id=request_source.message_id
                )
                logger.debug("Sent error to the user as message")

            else:
                logger.info(f"The user request is of type {request_source.__class__.__name__}; "
                            "no notification will be sent to the user")

        except Exception:
            logger.opt(exception=True).error("Error while notifying the user about an error processing the request")


@contextlib.asynccontextmanager
async def handle_exceptions(request_source: RequestSource):
    """ContextManager to handle exceptions while processing a request. Will notify the user about the error
    """
    # noinspection PyBroadException
    try:
        yield

    except StopNotExist:
        await notify_error(text=get_messages().stop.not_exists, request_source=request_source)

    except UserRateLimit:
        await notify_error(text=get_messages().generic.rate_limit_error, request_source=request_source)

    except Exception:
        logger.opt(exception=True).error("Unidentified error while processing a client request")
        await notify_error(
            text=get_messages().generic.generic_error,
            request_source=request_source,
            with_request_id=True
        )
