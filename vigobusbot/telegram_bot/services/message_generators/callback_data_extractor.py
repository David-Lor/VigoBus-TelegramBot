"""CALLBACK DATA EXTRACTOR
Extract data from a received Callback Data dict
"""

# # Installed # #
import pydantic

__all__ = ("CallbackDataExtractor",)


class CallbackDataExtractor(pydantic.BaseModel):
    stop_id: int
    get_all_buses: int = 0
    more_buses_available: int = 0

    @staticmethod
    def extract(callback_data: dict):
        return CallbackDataExtractor(**callback_data)
