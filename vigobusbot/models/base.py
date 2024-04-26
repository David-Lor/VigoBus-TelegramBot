import pydantic
import classmapper

mapper = classmapper.ClassMapper()


class BaseModel(pydantic.BaseModel):
    pass
