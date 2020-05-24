"""INLINE HANDLERS
Callback Handlers for the Inline Queries, produced when users search stops from the inline mode
"""

# # Native # #
import asyncio

# # Installed # #
import aiogram

# # Project # #
from vigobusbot.telegram_bot.services.message_generators import generate_search_stops_inline_responses
from vigobusbot.telegram_bot.services.message_generators import generate_stop_message
from vigobusbot.telegram_bot.services.message_generators import SourceContext
from vigobusbot.telegram_bot.services import request_handler
from vigobusbot.settings_handler import telegram_settings as settings
from vigobusbot.logger import logger

__all__ = ("register_handlers",)


@request_handler("Inline stop search", rate_limit_weight=0.25)
async def stop_search(inline_query: aiogram.types.InlineQuery, *args, **kwargs):
    search_term = inline_query.query
    if len(search_term) < 3:
        logger.debug("Search term is too short")
        # TODO Notify user? (in which case this should be verified on the helper)
        return

    inline_results = await generate_search_stops_inline_responses(search_term)
    await inline_query.bot.answer_inline_query(
        inline_query_id=inline_query.id,
        results=inline_results,
        cache_time=settings.inline_cache_time
    )


@request_handler("Inline stop search - chosen result", rate_limit_weight=0)
async def stop_search_chosen_result(chosen_inline_query: aiogram.types.ChosenInlineResult, *args, **kwargs):
    stop_id = int(chosen_inline_query.result_id)

    context = SourceContext(
        stop_id=stop_id,
        from_inline=True
    )
    text, markup = await generate_stop_message(context)

    await chosen_inline_query.bot.edit_message_text(
        inline_message_id=chosen_inline_query.inline_message_id,
        text=text,
        reply_markup=markup
    )


def register_handlers(dispatcher: aiogram.Dispatcher):
    # Stop Search
    dispatcher.register_inline_handler(stop_search)

    # Chosen Result from Stop Search
    dispatcher.register_chosen_inline_handler(
        stop_search_chosen_result,
        lambda chosen_inline_query: chosen_inline_query.result_id.isdigit()
    )

    logger.debug("Registered Inline Handlers")
