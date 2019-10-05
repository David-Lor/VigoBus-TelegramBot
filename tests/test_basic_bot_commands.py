"""TESTS - BASIC BOT COMMANDS
"""

# # Package # #
from .utils import *


class TestBasicBotCommands(BaseTest):
    """Request the bot for basic text commands without complex logic.
    """

    def __command_test(self, command, expected):
        """Given a command and the expected output message/s,
        send the command as the client and wait for the bot to reply.
        """
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
        self.debug_test_name()
        self.__command_test("start", self.messages.start)

    def test_command_help(self):
        """Test the /help command
        """
        self.debug_test_name()
        self.__command_test("help", self.messages.help)
        self.__command_test("ayuda", self.messages.help)

    def test_command_donate(self):
        """Test the /donate command
        """
        self.debug_test_name()
        self.__command_test("donate", self.messages.donate)

    def test_command_about(self):
        """Test the /about command
        """
        self.debug_test_name()
        self.__command_test("about", self.messages.about)
        self.__command_test("acercade", self.messages.about)
