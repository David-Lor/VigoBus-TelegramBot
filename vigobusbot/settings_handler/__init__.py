"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

# # Native # #
from typing import Optional

# # Installed # #
from dotenv_settings_handler import BaseSettingsHandler
from dotenv import load_dotenv

__all__ = ("telegram_settings", "api_settings", "data_manager_settings")

load_dotenv()


class BaseBotSettings(BaseSettingsHandler):
    class Config:
        case_insensitive = True


class TelegramSettings(BaseBotSettings):
    token: str
    method = "polling"
    skip_prev_updates = True
    polling_fast = True
    polling_timeout: float = 30
    static_path: Optional[str]


class APISettings(BaseBotSettings):
    url = "http://localhost:5000"
    timeout: float = 30

    class Config:
        env_prefix = "API_"


class DataManagerSettings(BaseBotSettings):
    pass


telegram_settings = TelegramSettings()
api_settings = APISettings()
data_manager_settings = DataManagerSettings()
