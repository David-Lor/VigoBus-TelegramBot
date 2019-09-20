"""ENTITIES
Custom and imported entities used all over the project
"""

# # Installed # #
import pydantic
from pybusent import Stop, Bus, Buses

__all__ = ("Stop", "Bus", "Buses", "BusesResponse")


class BusesResponse(pydantic.BaseModel):
    """Response given by the Bus API when querying for the buses of a Stop"""
    buses: Buses
    """List of Bus objects (if no buses available, is empty array)"""
    more_buses_available: bool = False
    """If True, more buses are available to fetch"""
