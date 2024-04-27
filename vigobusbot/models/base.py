import datetime

import pydantic
import classmapper

from vigobusbot.utils import get_datetime
from vigobusbot.settings_handler import system_settings

mapper = classmapper.ClassMapper()


class BaseModel(pydantic.BaseModel):
    pass


class Timestamp(BaseModel):
    iso: datetime.datetime = None
    unix: int = None
    """Unix timestamp, UTC, seconds"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize()

    def initialize(self):
        if not self.iso:
            self.iso = get_datetime()
        if not self.unix:
            self.unix = int(self.iso.timestamp())

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d["iso"] = self.iso.isoformat()
        return d


class Metadata(BaseModel):
    version: int
    created_on: Timestamp = None
    created_by_node: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize()

    def initialize(self):
        if not self.created_by_node:
            self.created_by_node = system_settings.node_name
        if not self.created_on:
            self.created_on = Timestamp()
