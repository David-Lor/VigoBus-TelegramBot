"""BUS GETTER
Get Buses using the API
"""

# # Native # #
import json

# # Package # #
from .requester import http_get
from .exceptions import manage_exceptions

# # Project # #
from ..entities import Bus, BusesResponse

__all__ = ("get_buses",)


async def get_buses(stop_id: int, get_all_buses=False) -> BusesResponse:
    with manage_exceptions():
        query_params = {
            "get_all_buses": int(get_all_buses)
        }
        result = await http_get(endpoint=f"/buses/{stop_id}", query_params=query_params)
        data = json.loads(result.text)

        buses = [Bus(**bus_data) for bus_data in data["buses"]]
        more_buses_available = data["more_buses_available"]

        return BusesResponse(
            buses=buses,
            more_buses_available=more_buses_available
        )
