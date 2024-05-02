import vigobus

from vigobusbot.utils import Singleton

__all__ = ["VigoBusAPI"]


class VigoBusAPI(vigobus.Vigobus, Singleton):
    # TODO Parameterize settings
    pass
