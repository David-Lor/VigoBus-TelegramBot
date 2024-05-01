"""BUS GETTER
Get Buses using the API
"""

from .requester import http_get
from .exceptions import manage_stop_exceptions
from vigobusbot.models import Bus, BusesResponse

__all__ = ("get_buses",)


async def get_buses(stop_id: int, get_all_buses=False) -> BusesResponse:
    with manage_stop_exceptions(stop_id):
        query_params = {
            "get_all_buses": int(get_all_buses)
        }
        result = await http_get(endpoint=f"/buses/{stop_id}", query_params=query_params)
        data = result.json()

        buses = [Bus(**bus_data) for bus_data in data["buses"]]
        more_buses_available = data["more_buses_available"]

        return BusesResponse(
            buses=buses,
            more_buses_available=more_buses_available
        )
