"""TEST - BASIC BOT COMMANDS
"""

# # Package # #
from .utils import *

# # Project # #
from vigobusbot.static_handler import get_messages, load_static_files


class TestBasicBotCommands:
    """Request the bot for basic text commands without complex logic.
    """
    client: BotIntegrationClient = None
    messages = None

    @classmethod
    def setup_class(cls):
        load_static_files()
        start_bot()
        cls.messages = get_messages()
        cls.client = start_client()

    @classmethod
    def teardown_class(cls):
        stop_client()
        stop_bot()

    def __command_test(self, command, expected):
        if isinstance(expected, str):
            expected = [expected]
        n_expected = len(expected)

        response = self.client.send_command_await(command, num_expected=n_expected)

        for i, expected_text in enumerate(expected):
            received_text = clear_markdown(response.messages[i].text.markdown)
            assert received_text == expected_text

    def test_command_start(self):
        """Test the /start command
        """
        self.__command_test("start", self.messages.start)

    def test_command_help(self):
        """Test the /help command
        """
        self.__command_test("help", self.messages.help)
        self.__command_test("ayuda", self.messages.help)

    def test_command_donate(self):
        """Test the /donate command
        """
        self.__command_test("donate", self.messages.donate)

    def test_command_about(self):
        """Test the /about command
        """
        self.__command_test("about", self.messages.about)
        self.__command_test("acercade", self.messages.about)
