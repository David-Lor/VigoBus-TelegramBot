"""TEST UTILS - TELEGRAM BOT
Start and stop the Telegram bot for testing
"""

# # Native # #
import multiprocessing

# # Project # #
from vigobusbot.telegram_bot.bot import get_bot
from vigobusbot.runner import run

__all__ = ("start_bot", "stop_bot", "get_bot")

# noinspection PyTypeChecker
__bot_process: multiprocessing.Process = None


def start_bot():
    global __bot_process
    if not __bot_process:
        __bot_process = multiprocessing.Process(
            target=run,
            daemon=True
        )
        __bot_process.start()


def stop_bot(join=False, timeout=5):
    if __bot_process:
        get_bot().dispatcher.stop_polling()
        if join:
            __bot_process.join(timeout)
