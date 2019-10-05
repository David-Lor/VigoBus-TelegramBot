"""TESTS - UTILS - BASE TEST
Base classes for the tests
"""

# # Native # #
import contextlib
from typing import List, Union

# # Installed # #
from tgintegration import Response
from pyrogram.client.types import InlineKeyboardButton

# # Package # #
from .helpers import *
from .mocked_persistence_api import *
from .mocked_bus_api import *
from .telegram_bot import *
from .telegram_client import *

# # Project # #
from vigobusbot.static_handler import get_messages, load_static_files
from vigobusbot.settings_handler import telegram_settings as bot_telegram_settings
from vigobusbot.settings_handler import api_settings as bot_bus_api_settings
from vigobusbot.settings_handler import persistence_settings as bot_persistence_api_settings

__all__ = ("BaseTest", "BaseBusAPITest", "BasePersistenceBusAPITest")


class BaseTest:
    """Base class for all the tests.
    Initialize the Telegram Bot and Client.
    """
    user_id: int = None
    client: BotIntegrationClient = None
    messages = None

    @classmethod
    def setup_class(cls):
        load_static_files()
        cls.messages = get_messages()
        cls.client = start_client()
        cls.user_id = cls.client.get_me().id
        bot_telegram_settings.skip_prev_updates = True
        start_bot()

    @classmethod
    def teardown_class(cls):
        stop_client()
        stop_bot(join=True)

    @staticmethod
    def parse_message_buttons(response: Response) -> List[InlineKeyboardButton]:
        """Parse all the inline keyboard buttons from a Telegram Response (mixing from all the rows).
        """
        buttons = []
        with contextlib.suppress(IndexError):
            for row_of_buttons in response.inline_keyboards[0].rows:
                buttons.extend(row_of_buttons)
        return buttons

    @staticmethod
    def press_inline_button(response: Response, text: str, **kwargs):
        # noinspection PyTypeChecker
        return response.inline_keyboards[0].press_button_await(pattern=text, **kwargs)

    def send_message_await_text(self, message_text: str, num_expected=1, **kwargs) -> Union[str, List[str]]:
        """Send message through Telegram client to bot. Get the text (Markdown-parsed) from the received message/s.
        If num_expected > 1, a List of str is returned; if == 1, the single str.
        """
        received = self.client.send_message_await(
            text=message_text,
            num_expected=num_expected,
            **kwargs
        )

        received = [clear_markdown(msg.text.markdown) for msg in received]
        if len(received) == 1:
            received = received[0]

        return received

    def debug_test_name(self):
        with contextlib.suppress(StopIteration):
            self.client.send_message(chat_id=self.client.bot_under_test, text="/test " + get_test_function_name())


class BaseBusAPITest(BaseTest):
    """Base class for all the tests that require the Stop & Bus API to be running.
    Initialize the Telegram Bot, Client and the Fake Bus API.
    """
    bus_api: FakeBusAPI

    @classmethod
    def setup_class(cls):
        cls.bus_api = FakeBusAPI()
        cls.bus_api.start_server(wait=True)
        bot_bus_api_settings.url = f"http://localhost:{cls.bus_api.app_port}"
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        if cls.bus_api:
            cls.bus_api.stop_server(join=True)
        super().teardown_class()


class BasePersistenceBusAPITest(BaseBusAPITest):
    """Base class for all the tests that require the Stop & Bus API + Persistence API to be running.
    Initialize the Telegram Bot, Client and the Fake Bus API and the Fake Persistence API.
    """
    persistence_api: FakePersistenceAPI

    @classmethod
    def setup_class(cls):
        cls.persistence_api = FakePersistenceAPI()
        cls.persistence_api.start_server(wait=True)
        bot_persistence_api_settings.url = f"http://localhost:{cls.persistence_api.app_port}"
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        if cls.persistence_api:
            cls.persistence_api.stop_server(join=True)
        super().teardown_class()
