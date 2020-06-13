"""LOGS Repository
Repository for Log persistence
"""

# # Native # #
import asyncio
from typing import List

# # Installed # #
from pydantic import BaseModel, Field

# # Project # #
from vigobusbot.services.mongo import get_logs_collection
from vigobusbot.utils import *

__all__ = ("persist_records",)


class RequestLogRecords(BaseModel):
    """Schema for documents inserted in Mongo for request log records"""
    # TODO Move to another location if possible
    request_id: str
    records: List[dict]
    timestamp: int = Field(default_factory=get_time)

    def dict(self, **kwargs):
        d = super().dict(**kwargs)
        d["_id"] = d.pop("request_id")
        return d


async def persist_records(request_id: str, records: List[dict]):
    """Persist an array of records, identified by an unique request_id"""
    records_obj = RequestLogRecords(request_id=request_id, records=records)
    return await get_logs_collection(asyncio.get_event_loop()).insert_one(records_obj.dict())
