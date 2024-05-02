"""BUS GETTER
Get Buses using the API
"""

from .base import VigoBusAPI
from vigobusbot.models import BusesResponse

__all__ = ("get_buses",)


async def get_buses(stop_id: int, get_all_buses=False) -> BusesResponse:
    return await VigoBusAPI.get_instance().get_buses(stop_id=stop_id, get_all_buses=get_all_buses)
