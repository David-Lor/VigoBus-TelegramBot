"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

from typing import Optional

import pydantic
import aiogram.bot.api

from .helpers import *

__all__ = ("telegram_settings", "api_settings", "persistence_settings", "mongo_settings", "system_settings")


class BaseBotSettings(pydantic.BaseSettings):
    class Config:
        env_file = ".env"


class TelegramSettings(BaseBotSettings):
    token: str
    admin_userid: int
    bot_api: str = "https://api.telegram.org"
    method = "polling"
    skip_prev_updates = True
    polling_fast = True
    polling_timeout: float = 30
    force_reply_ttl: int = 3600
    """Timeout for Force Reply requests until cleanup"""
    user_rate_limit_amount: int = 5
    """Maximum requests performed by users in "user_rate_limit_time" seconds"""
    user_rate_limit_time: float = 1
    """Timeout for User Rate counter to reset"""
    typing_safe_limit_time: float = 30
    """Timeout for a Typing chat action to end"""
    inline_cache_time: int = 300
    stop_messages_deprecation_reminder_after_seconds: int = 0
    """Time for a Stop message to be considered deprecated, thus update with a warning about it being deprecated.
    If 0, disable this feature."""
    stop_messages_deprecation_reminder_loop_delay_seconds: int = 60
    """Delay for the loop that checks for deprecated Stop messages."""
    stop_messages_include_arrival_hour_after_minutes: int = -1
    """Buses arriving after this amount of minutes will include the calculated hour of arrival.
    Negative values to disable the feature."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = load_secrets_file(path=self.token.strip(), path_startswith=True)

    @property
    def bot_api_server(self):
        return aiogram.bot.api.TelegramAPIServer.from_base(self.bot_api)


class APISettings(BaseBotSettings):
    url = "http://localhost:5000"
    timeout: float = 30
    retries: int = 2

    class Config(BaseBotSettings.Config):
        env_prefix = "API_"


class PersistenceSettings(BaseBotSettings):
    url = "http://localhost:5001"
    salt = "FixedSalt"
    """Fixed salt value for hashing stored user data (saved stops) in local persistence
    (cannot change once there is data stored)"""
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
    """Collection for log records"""

    class Config(BaseBotSettings.Config):
        env_prefix = "MONGO_"


class SystemSettings(BaseBotSettings):
    static_path: Optional[str]
    """Location of "static" directory (might be required when running from Docker)"""
    log_level: str = "INFO"
    """Log level for printing system log records"""
    request_logs_persist_enabled: bool = True
    """If True, enable persisting request log records on Mongo"""
    request_logs_persist_level: str = "ERROR"
    """Minimum record level to persist all records for a request (at least one record with this level)"""
    request_logs_persist_record_timeout: float = 120
    """Timeout for request records in logger cache until cleanup"""
    request_logs_print_level: str = "WARNING"
    """Log level for printing individual request log records"""
    test: bool = False
    """If True, run the test handlers"""


telegram_settings = TelegramSettings()
api_settings = APISettings()
persistence_settings = PersistenceSettings()
mongo_settings = MongoSettings()
system_settings = SystemSettings()
