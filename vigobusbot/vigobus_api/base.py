import vigobus

from vigobusbot.utils import Singleton
from vigobusbot.settings_handler import telegram_settings

__all__ = ["VigoBusAPI"]


class VigoBusAPI(vigobus.Vigobus, Singleton):
    def __init__(self):
        super().__init__(
            getbuses_notallbuses_limit=telegram_settings.buses_shortmessage_limit
        )
