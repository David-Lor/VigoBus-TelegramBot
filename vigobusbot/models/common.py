"""MODELS - Common
Common variables, classes, attributes - for models (internal usage)
"""

# # Installed # #
import pydantic


class BaseModel(pydantic.BaseModel):
    def dict(self, *args, **kwargs):
        # TODO exclude None
        return super().dict(*args, **kwargs)
