"""RUNNER
Start Telegram bot using Polling/Webhook methods depending on the settings
"""

# # Project # #
from .settings_handler import telegram_settings as settings
from .static_handler import load_static_files
from . import telegram_bot as bot

__all__ = ("run",)


def run():
    load_static_files()

    if settings.method == "webhook":
        pass
    else:
        bot.start_polling()


if __name__ == '__main__':
    run()
