"""TEST UTILS - SETTINGS
Load test-specific settings
"""

# # Installed # #
from dotenv_settings_handler import BaseSettingsHandler
from dotenv import load_dotenv

__all__ = ("settings",)


class SettingsTest(BaseSettingsHandler):
    bot_name: str
    telegram_session_filename: str = "vigobusbot_test"
    # Get API ID & Hash from: https://my.telegram.org/apps
    api_id: str
    api_hash: str
    max_wait_response: float = 15.0
    min_wait_consecutive: float = 2.0

    class Config:
        env_prefix = "TEST_"
        case_insensitive = True


load_dotenv()
settings = SettingsTest()
