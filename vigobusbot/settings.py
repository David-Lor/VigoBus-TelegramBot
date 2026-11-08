import os
import platform

import yaml
import pydantic

from .utils import Singleton

SETTINGS_FILE = os.getenv("SETTINGS_FILE", "settings.yaml")


class BaseSetting(pydantic.BaseModel, Singleton):
    pass


class TelegramSettings(BaseSetting):
    token: pydantic.SecretStr
    admin_userid: int
    bot_api_url: str = "https://api.telegram.org"
    skip_prev_updates: bool = True
    polling_fast: bool = True
    polling_timeout: float = 30
    disable_dispatcher_logger: bool = False

    buses_shortmessage_limit: int = 5
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
    stop_updater_first_run: bool = False

    stop_messages_deprecation_reminder_cron: str = ""
    """Cron expression for running the Stop messages deprecation reminder loop.
    Empty to disable this feature."""
    stop_messages_deprecation_reminder_after_seconds: int = 300  # 300s = 5m
    """Time for a Stop message to be considered deprecated, thus update with a warning about it being deprecated."""
    stop_messages_include_arrival_hour_after_minutes: int = -1
    """Buses arriving after this amount of minutes will include the calculated hour of arrival.
    Negative values disable the feature."""

    stop_elastic_sync_cron: str = ""
    stop_elastic_sync_first_run: bool = False


class CouchDBSettings(BaseSetting):
    url: str = "http://localhost:5984"
    user: str
    password: pydantic.SecretStr
    create_databases: bool = True
    """If True, issue command to create the databases if not exist. This requires the user provided to be admin."""

    db_sent_messages: str = "vigobusbot_sent_messages"
    db_stops: str = "vigobusbot_stops"
    db_user_stops: str = "vigobusbot_userstops"


class ElasticSearchSettings(BaseSetting):
    url: pydantic.AnyHttpUrl|None = None
    user: str | None = None
    password: pydantic.SecretStr | None = None
    stops_search_limit: int = 20
    stops_index: str = "vigobus_stops"
    create_indexes: bool = True

    @property
    def enabled(self) -> bool:
        return bool(self.url)

    @property
    def basic_auth_tuple(self) -> tuple|None:
        if self.user and self.password:
            return self.user, self.password.get_secret_value()
        return None


class PersistenceSettings(BaseSetting):
    encryption_key: str = "GeneralEncryptionKey"
    """Fixed encryption key for encrypting sensitive values (cannot change once there is data stored)."""
    key_cache_size: int = 100


class SystemSettings(BaseSetting):
    static_path: str | None = None
    """Location of "static" directory (might be required when running from Docker)"""
    log_level: str = "INFO"
    """Log level for printing system log records"""
    request_logs_print_level: str = "WARNING"
    """Log level for printing individual request log records"""
    node_name: str = platform.node()
    """Hostname/node name, to be appended to the logs. If equals to 'hostname', use the current hostname."""
    test: bool = False
    """If True, run the test handlers"""


class Settings(BaseSetting):
    telegram: TelegramSettings
    couchdb: CouchDBSettings
    elasticsearch: ElasticSearchSettings = pydantic.Field(default_factory=ElasticSearchSettings)
    persistence: PersistenceSettings
    system: SystemSettings = pydantic.Field(default_factory=SystemSettings)


def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        data = yaml.safe_load(f)
    settings: Settings = Settings(**data).set_current_as_singleton()

    settings.system.set_current_as_singleton()
    settings.telegram.set_current_as_singleton()
    settings.couchdb.set_current_as_singleton()
    settings.elasticsearch.set_current_as_singleton()
    settings.persistence.set_current_as_singleton()
