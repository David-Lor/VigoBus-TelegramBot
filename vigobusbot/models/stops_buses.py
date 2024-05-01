import datetime
from typing import Optional, List, Dict

from .base import BaseModel

__all__ = ("Stop", "Bus", "Stops", "Buses", "StopsDict", "BusesResponse", "File", "Files")


class Stop(BaseModel):
    stop_id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]


class Bus(BaseModel):
    line: str
    route: str
    time: int  # minutes

    def get_calculated_arrival_time(self) -> datetime.datetime:
        return datetime.datetime.now() + datetime.timedelta(minutes=self.time)


class File(BaseModel):
    filename: str
    description: str


Stops = List[Stop]
Buses = List[Bus]
StopsDict = Dict[int, Stop]
Files = List[File]


class BusesResponse(BaseModel):
    """Response given by the Bus API when querying for the buses of a Stop"""
    buses: Buses
    """List of Bus objects (if no buses available, is empty array)"""
    more_buses_available: bool = False
    """If True, more buses are available to fetch"""
