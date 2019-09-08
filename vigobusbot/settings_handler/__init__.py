"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

# # Native # #
from typing import Optional

# # Installed # #
from dotenv_settings_handler import BaseSettingsHandler
from dotenv import load_dotenv

__all__ = ("telegram_settings", "api_settings", "persistence_settings")

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
    stop_rename_request_ttl: int = 3600

    class Config:
        case_insensitive = True


class APISettings(BaseBotSettings):
    url = "http://localhost:5000"
    timeout: float = 30

    class Config:
        env_prefix = "API_"
        case_insensitive = True


class PersistenceSettings(BaseBotSettings):
    url = "http://localhost:5001"
    salt = "FixedSalt"
    timeout: float = 30
    cache_size: int = 100

    class Config:
        env_prefix = "PERSIST_"
        case_insensitive = True


telegram_settings = TelegramSettings()
api_settings = APISettings()
persistence_settings = PersistenceSettings()
