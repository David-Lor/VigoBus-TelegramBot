from typing import List, Dict

import aiocouch
from vigobus.models import Stop, Bus, BusesResponse, StopMetadata

from .base import BaseModel, BaseMetadataedModel, mapper
from .db import KeyValue, KV_DOC_KEY_PREFIX

__all__ = ("Stop", "StopPersist", "Bus", "Stops", "Buses", "StopsDict", "BusesResponse", "File", "Files", "StopsEtagKV")


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


class StopsEtagKV(KeyValue):
    value: str

    @classmethod
    def get_key(cls):
        return KV_DOC_KEY_PREFIX + "stops_etag"


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


@mapper.register(aiocouch.Document, Stop)
def _mapper_from_document(_from: aiocouch.Document) -> Stop:
    stop_persist = StopPersist(
        id=_from.id,
        **_from.data,
    )
    return mapper.map(stop_persist, Stop)


@mapper.register(aiocouch.Document, StopsEtagKV)
def _mapper_stopsetagkv_from_document(_from: aiocouch.Document) -> StopsEtagKV:
    return StopsEtagKV(**_from.data)
