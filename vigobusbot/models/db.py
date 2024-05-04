import abc
from typing import Any

from .base import BaseMetadataedModel

__all__ = ["KeyValue", "KV_DOC_KEY_PREFIX"]

KV_DOC_KEY_PREFIX = "kv/"


class KeyValue(abc.ABC, BaseMetadataedModel):
    value: Any

    @classmethod
    @abc.abstractmethod
    def get_key(cls):
        return NotImplementedError
