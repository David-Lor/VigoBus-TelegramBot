"""TESTS - UTILS - TELEGRAM BOT
Start and stop the Telegram bot for testing
"""

# # Native # #
import multiprocessing
from typing import Optional

# # Project # #
from vigobusbot.telegram_bot.bot import get_bot
from vigobusbot.runner import run

__all__ = ("start_bot", "stop_bot", "get_bot")

# noinspection PyTypeChecker
__bot_process: Optional[multiprocessing.Process] = None


def start_bot():
    global __bot_process
    if not __bot_process:
        __bot_process = multiprocessing.Process(
            target=run,
            daemon=True
        )
        __bot_process.start()


def stop_bot(join=False, timeout=5):
    global __bot_process
    if __bot_process and __bot_process.is_alive():
        get_bot().dispatcher.stop_polling()
        if join:
            __bot_process.join(timeout)
        __bot_process = None
