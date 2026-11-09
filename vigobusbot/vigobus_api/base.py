import vigobus

from vigobusbot.utils import Singleton
from vigobusbot.settings import TelegramSettings

__all__ = ["VigoBusAPI"]


class VigoBusAPI(vigobus.Vigobus, Singleton):
    def __init__(self):
        super().__init__(
            getbuses_notallbuses_limit=TelegramSettings.get().buses_shortmessage_limit
        )
