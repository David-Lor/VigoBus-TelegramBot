"""MESSAGE HANDLERS
Telegram Bot Message Handlers: functions that handle incoming messages, depending on their command or content.
"""

# # Installed # #
import aiogram

__all__ = ("register_handlers",)


async def command_start(message: aiogram.types.Message):
    await message.reply("Hi there!")


async def command_help(message: aiogram.types.Message):
    await message.reply("Help!")


async def global_message_handler(message: aiogram.types.Message):
    """Last Message Handler that handles any text message that does not match any of the other message handlers.
    """
    await message.reply("Pong! " + message.text)


def register_handlers(dispatcher: aiogram.Dispatcher):
    """Register all the message handlers for the given Bot Dispatcher.
    """
    # /start command
    dispatcher.register_message_handler(command_start, commands=("start",))

    # /help command
    dispatcher.register_message_handler(command_help, commands=("help", "ayuda"))

    # Rest of text messages
    dispatcher.register_message_handler(global_message_handler)
