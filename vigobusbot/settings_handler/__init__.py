"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

# # Native # #
from typing import Optional

# # Installed # #
from dotenv_settings_handler import BaseSettingsHandler
from dotenv import load_dotenv

# # Package # #
from .helpers import *

__all__ = ("telegram_settings", "api_settings", "persistence_settings", "system_settings")


class BaseBotSettings(BaseSettingsHandler):
    class Config:
        case_insensitive = True


class TelegramSettings(BaseBotSettings):
    token: str
    admin_userid: int
    method = "polling"
    skip_prev_updates = True
    polling_fast = True
    polling_timeout: float = 30
    force_reply_ttl: int = 3600
    user_rate_limit_amount: int = 5
    user_rate_limit_time: int = 1
    typing_safe_limit_time: float = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = load_secrets_file(path=self.token.strip(), path_startswith=True)


class APISettings(BaseBotSettings):
    url = "http://localhost:5000"
    timeout: float = 30
    retries: int = 2

    class Config(BaseBotSettings.Config):
        env_prefix = "API_"


class PersistenceSettings(BaseBotSettings):
    url = "http://localhost:5001"
    salt = "FixedSalt"
    timeout: float = 30
    retries: int = 2
    key_cache_size: int = 100

    class Config(BaseBotSettings.Config):
        env_prefix = "PERSIST_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.salt = load_secrets_file(path=self.salt.strip(), path_startswith=True)


class SystemSettings(BaseBotSettings):
    static_path: Optional[str]
    log_level: str = "INFO"
    test: bool = False


load_dotenv()

telegram_settings = TelegramSettings()
api_settings = APISettings()
persistence_settings = PersistenceSettings()
system_settings = SystemSettings()
