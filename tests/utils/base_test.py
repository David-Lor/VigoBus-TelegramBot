"""TESTS - UTILS - BASE TEST
Base classes for the tests
"""

# # Native # #
from typing import List, Union

# # Package # #
from .helpers import *
from .mocked_api import *
from .telegram_bot import *
from .telegram_client import *
from .settings import settings

# # Project # #
from vigobusbot.static_handler import get_messages, load_static_files
from vigobusbot.settings_handler import api_settings as bot_api_settings

__all__ = ("BaseTest", "BaseAPITest")


class BaseTest:
    """Base class for all the tests.
    Initialize the Telegram Bot and Client.
    """
    client: BotIntegrationClient = None
    messages = None

    @classmethod
    def setup_class(cls):
        load_static_files()
        cls.messages = get_messages()
        cls.client = start_client()
        start_bot()

    @classmethod
    def teardown_class(cls):
        stop_client()
        stop_bot(join=True)

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


class BaseAPITest(BaseTest):
    """Base class for all the tests that require the Stop/Bus API to be running.
    Initialize the Telegram Bot, Client and a Fake API.
    """
    api: FakeAPI

    @classmethod
    def setup_class(cls):
        cls.api = FakeAPI()
        cls.api.start_server()
        bot_api_settings.url = f"http://localhost:{settings.fake_api_port}"
        super().setup_class()

    def teardown_method(self):
        self.api.clear()
