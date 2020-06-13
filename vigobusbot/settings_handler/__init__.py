"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

# # Native # #
from typing import Optional

# # Installed # #
import pydantic

# # Package # #
from .helpers import *

__all__ = ("telegram_settings", "api_settings", "persistence_settings", "mongo_settings", "system_settings")


class BaseBotSettings(pydantic.BaseSettings):
    class Config:
        env_file = ".env"


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
    inline_cache_time: int = 300

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


class MongoSettings(BaseBotSettings):
    uri: str = "mongodb://localhost:27017"
    database: str = "vigobusbot"
    collection_logs: str = "logs"

    class Config(BaseBotSettings.Config):
        env_prefix = "MONGO_"


class SystemSettings(BaseBotSettings):
    static_path: Optional[str]
    log_level: str = "INFO"
    request_logs_persist_enabled: bool = True
    request_logs_persist_level: str = "ERROR"
    request_logs_persist_record_timeout: float = 120
    request_logs_print_level: str = "WARNING"
    test: bool = False


telegram_settings = TelegramSettings()
api_settings = APISettings()
persistence_settings = PersistenceSettings()
mongo_settings = MongoSettings()
system_settings = SystemSettings()
