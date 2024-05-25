import json
import datetime

import pydantic
import classmapper

from vigobusbot.utils import get_datetime, jsonable_dict
from vigobusbot.settings_handler import system_settings

__all__ = ("BaseModel", "mapper", "Timestamp", "Metadata", "BaseMetadataedModel")

mapper = classmapper.ClassMapper()


class BaseModel(pydantic.BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complete_fields()

    def complete_fields(self):
        pass

    def jsonable_dict(self, **kwargs) -> dict:
        return jsonable_dict(self, **kwargs)


class Timestamp(BaseModel):
    iso: datetime.datetime = None
    unix: int = None
    """Unix timestamp, UTC, seconds"""

    def complete_fields(self):
        if not self.iso:
            self.iso = get_datetime()
        if not self.unix:
            self.unix = int(self.iso.timestamp())


class Metadata(BaseModel):
    version: int
    created_on: Timestamp = None
    created_by_node: str = None

    def complete_fields(self):
        if not self.created_by_node:
            self.created_by_node = system_settings.node_name
        if not self.created_on:
            self.created_on = Timestamp()


class BaseMetadataedModel(BaseModel):
    metadata: Metadata = None

    def complete_fields(self):
        if not self.metadata:
            self.metadata = Metadata(version=self.get_current_version())

    @classmethod
    def get_current_version(cls):
        return 0
