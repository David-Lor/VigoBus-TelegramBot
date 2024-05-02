"""SETTINGS HANDLER
Load settings from dotenv file or environment variables
"""

import os
import platform
from typing import Optional

import pydantic

from .helpers import *

__all__ = ("telegram_settings", "persistence_settings", "couchdb_settings", "system_settings")


class BaseBotSettings(pydantic.BaseSettings):
    class Config:
        env_file = os.getenv("ENV_FILE", ".env")


class TelegramSettings(BaseBotSettings):
    token: str
    admin_userid: int
    bot_api: str = "https://api.telegram.org"
    skip_prev_updates = True
    polling_fast = True
    polling_timeout: float = 30

    webhook_url: Optional[pydantic.AnyHttpUrl] = None
    webhook_path: str = "/"
    webhook_secret: Optional[str] = None
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 3000
    webhook_delete_on_close: bool = False
    webhook_status_path: Optional[str] = None

    force_reply_ttl: int = 3600
    """Timeout for Force Reply requests until cleanup"""
    user_rate_limit_amount: int = 5
    """Maximum requests performed by users in "user_rate_limit_time" seconds"""
    user_rate_limit_time: float = 1
    """Timeout for User Rate counter to reset"""
    typing_safe_limit_time: float = 30
    """Timeout for a Typing chat action to end"""
    inline_cache_time: int = 300

    stop_updater_cron: str = ""

    stop_messages_deprecation_reminder_cron: str = ""
    """Cron expression for running the Stop messages deprecation reminder loop.
    Empty to disable this feature."""
    stop_messages_deprecation_reminder_after_seconds: int = 300  # 300s = 5m
    """Time for a Stop message to be considered deprecated, thus update with a warning about it being deprecated."""
    stop_messages_include_arrival_hour_after_minutes: int = -1
    """Buses arriving after this amount of minutes will include the calculated hour of arrival.
    Negative values disable the feature."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = load_secrets_file(path=self.token.strip(), path_startswith=True)

    @property
    def webhook_enabled(self):
        return bool(self.webhook_url)


class APISettings(BaseBotSettings):
    url = "http://localhost:5000"
    timeout: float = 30
    retries: int = 2

    class Config(BaseBotSettings.Config):
        env_prefix = "API_"


class PersistenceSettings(BaseBotSettings):
    encryption_key: str = "GeneralEncryptionKey"
    """Fixed encryption key for encrypting sensitive values (cannot change once there is data stored)."""
    key_cache_size: int = 100

    class Config(BaseBotSettings.Config):
        env_prefix = "PERSIST_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.encryption_key = load_secrets_file(path=self.encryption_key.strip(), path_startswith=True)


class CouchDBSettings(BaseBotSettings):
    url: pydantic.AnyHttpUrl = "http://localhost:5984"
    user: str
    password: pydantic.SecretStr
    create_databases: bool = True
    """If True, issue command to create the databases if not exist. This requires the user provided to be admin."""

    db_sent_messages: str = "vigobusbot_sent_messages"
    db_stops: str = "vigobusbot_stops"
    db_user_stops: str = "vigobusbot_userstops"

    class Config(BaseBotSettings.Config):
        env_prefix = "COUCHDB_"


class SystemSettings(BaseBotSettings):
    static_path: Optional[str]
    """Location of "static" directory (might be required when running from Docker)"""
    log_level: str = "INFO"
    """Log level for printing system log records"""
    request_logs_print_level: str = "WARNING"
    """Log level for printing individual request log records"""
    node_name: str = ""
    """Hostname/node name, to be appended to the logs. If equals to 'hostname', use the current hostname."""
    test: bool = False
    """If True, run the test handlers"""

    @pydantic.validator("node_name")
    def _node_name_set_as_hostname(cls, v):
        if v == "hostname":
            v = platform.node()
        return v


telegram_settings = TelegramSettings()
persistence_settings = PersistenceSettings()
couchdb_settings = CouchDBSettings()
system_settings = SystemSettings()
