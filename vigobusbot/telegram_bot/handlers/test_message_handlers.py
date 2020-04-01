"""MESSAGE HANDLERS
Telegram Bot Message Handlers for test purposes. Loaded from message_handlers.
"""

# # Installed # #
import aiogram

# # Project # #
from vigobusbot.telegram_bot.entities import Message
from vigobusbot.telegram_bot.services import request_handler, start_typing
from vigobusbot.logger import logger


@request_handler("Test Command /test_typing_forever")
async def command_typing_forever(message: Message, *args, **kwargs):
    """Test send Typing status and never stop it. Should auto-stop due to safe time limit.
    """
    await start_typing(bot=message.bot, chat_id=message.chat.id)


@request_handler("Test Command /test_fail")
async def command_fail(message: Message, *args, **kwargs):
    """Test raising an uncatched exception from the command handler. Should be catched by the global error handler.
    """
    raise Exception(f"Test command fail for message {message.message_id}")


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the test message handlers for the given Bot Dispatcher.
    To be called from message_handlers.register_handlers only if "test" env var is True.
    """
    dispatcher.register_message_handler(command_typing_forever, commands=("test_typing_forever", "testTypingForever"))
    dispatcher.register_message_handler(command_fail, commands=("test_fail", "testFail"))

    logger.debug("Registered Test Message Handlers")
