"""SERVICES - GENERIC REQUEST HANDLER - REQUEST HANDLER
"""

# # Native # #
import uuid

# # Package # #
from .rate_limit_handler import handle_user_rate_limit
from .error_handler import handle_exceptions

# # Project # #
from vigobusbot.telegram_bot.entities import RequestSource
from vigobusbot.logger import logger, get_request_id, get_request_verb

__all__ = ("request_handler",)


def request_handler(verb: str):
    """Decorator that must be used by all the bot Request Handler async functions,
    for logging and error handling purposes.
    :param verb: Descriptor of the request being processed
    """
    def _real_decorator(request_handler_function):
        # noinspection PyUnusedLocal
        async def request_wrapper(*args, **kwargs):
            result = None
            request_source: RequestSource = args[0]
            request_id = get_request_id()

            # In most cases the request will not have a defined Request ID
            if not request_id:
                request_id = str(uuid.uuid4())
                user_id = request_source.from_user.id

                with logger.contextualize(request_id=request_id, verb=verb):
                    logger.info("Request started")

                    async with handle_exceptions(request_source=request_source):
                        handle_user_rate_limit(user_id=user_id)
                        result = await request_handler_function(*args, **kwargs)

                    with logger.contextualize(last_record=True):
                        logger.info("Request finished")

            # ...but sometimes the request handler is called from another request handler
            else:
                parent_verb = get_request_verb()
                with logger.contextualize(verb=verb, parent_verb=parent_verb):
                    logger.debug("Sub-Request started")

                    async with handle_exceptions(request_source=request_source):
                        result = await request_handler_function(*args, **kwargs)

                    logger.debug("Sub-Request finished")

            return result

        return request_wrapper

    return _real_decorator
