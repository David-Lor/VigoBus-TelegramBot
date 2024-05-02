from typing import List, Dict

from vigobus.models import Stop, Bus, BusesResponse, StopMetadata

from .base import BaseModel, BaseMetadataedModel, mapper

__all__ = ("Stop", "StopPersist", "Bus", "Stops", "Buses", "StopsDict", "BusesResponse", "File", "Files")


class File(BaseModel):
    filename: str
    description: str


Stops = List[Stop]
Buses = List[Bus]
StopsDict = Dict[int, Stop]
Files = List[File]


class StopPersist(BaseMetadataedModel, Stop):
    id: str
    stop_metadata: StopMetadata


@mapper.register(Stop, StopPersist)
def _mapper_to_persist(_from: Stop) -> StopPersist:
    return StopPersist(
        **_from.dict(exclude={"metadata"}),
        stop_metadata=_from.metadata,
    )


@mapper.register(StopPersist, Stop)
def _mapper_from_persist(_from: StopPersist) -> Stop:
    return Stop(
        **_from.dict(exclude={"metadata"}),
        metadata=_from.stop_metadata,
    )
