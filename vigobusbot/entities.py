"""ENTITIES
Custom and imported entities used all over the project
"""

# # Native # #
from typing import Optional, List, Dict

# # Installed # #
import pydantic

__all__ = ("Stop", "Bus", "Stops", "Buses", "StopsDict", "BusesResponse", "File", "Files")


class Stop(pydantic.BaseModel):
    stop_id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]


class Bus(pydantic.BaseModel):
    line: str
    route: str
    time: int


class File(pydantic.BaseModel):
    filename: str
    description: str


Stops = List[Stop]
Buses = List[Bus]
StopsDict = Dict[int, Stop]
Files = List[File]


class BusesResponse(pydantic.BaseModel):
    """Response given by the Bus API when querying for the buses of a Stop"""
    buses: Buses
    """List of Bus objects (if no buses available, is empty array)"""
    more_buses_available: bool = False
    """If True, more buses are available to fetch"""
