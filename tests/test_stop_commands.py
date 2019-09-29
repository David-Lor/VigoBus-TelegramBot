"""TESTS - STOP COMMANDS
"""

# # Native # #
import datetime

# # Package # #
from .utils import *


class TestStopCommands(BaseAPITest):
    """Request the bot for Stop commands, that should return buses arriving to a stop in real time
    """

    def test_stop_not_exists(self):
        """Should return a message warning that the Stop does not exist when the API Stop endpoint returns 404
        """
        stop_id = given_stop_id()

        received_text = self.send_message_await_text(message_text=str(stop_id))

        assert received_text == self.messages.stop.not_exists

    def test_stop_id_name(self):
        """Should return a message with the Stop info (ID, Name) on it
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = given_buses()

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert str(stop.stopid) in received_text
        assert stop.name in received_text

    def test_stop_buses(self):
        """Should return a message with all the Buses on it (having many buses as the initial bus limit).
        At least one of the buses is arriving now (time=0). The message should contain one bus line per bus available,
        formatted with the bus line, route and time.
        """
        stop = given_stop()
        buses = [given_bus() for _ in range(settings.buses_limit - 1)]
        buses.append(given_bus(time=0))
        self.api.stop = stop
        self.api.buses = buses

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        for bus in buses:
            if bus.time == 0:
                expected_time = self.messages.stop.bus_time_now
            else:
                expected_time = self.messages.stop.bus_time_remaining.format(minutes=bus.time)
            assert self.messages.stop.bus_line.format(
                line=bus.line,
                route=bus.route,
                time=expected_time
            ) in received_text

    def test_stop_no_buses(self):
        """Should return a message warning the user that no buses are available.
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = []

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert self.messages.stop.no_buses_found in received_text

    def test_stop_last_update(self):
        """Should return a message with the timestamp when the message was generated.
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = given_buses()

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        # TODO allow +/-1s diff
        assert datetime.datetime.now().strftime(self.messages.stop.time_format) in received_text

    def test_stop_generic_error_stop_endpoint(self):
        """Should return a generic error message when the API Stop endpoint returns 500
        """
        stop_id = given_stop_id()
        self.api.stop = Exception()
        self.api.buses = given_buses()
        self.api.stop_id_should_exist = stop_id

        received_text = self.send_message_await_text(message_text=str(stop_id))

        assert received_text == self.messages.generic.generic_error

    def test_stop_generic_error_buses_endpoint(self):
        """Should return a generic error message when the API Buses endpoint returns 500
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = Exception()

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert received_text == self.messages.generic.generic_error

    def test_stop_default_buttons(self):
        """Should return a message with a Update button, a Save Stop button
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = given_buses()

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = []
        for inline_keyboard in received.inline_keyboards:
            for row_of_buttons in inline_keyboard.rows:
                buttons.extend(row_of_buttons)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.save)
        assert any(b for b in buttons if b.text == self.messages.stop.buttons.refresh)

    def test_stop_more_buses_button(self):
        """Should return a message with the More Buses button if more buses than the initial bus limit are available
        """
        stop = given_stop()
        self.api.stop = stop
        self.api.buses = given_buses(limit=settings.buses_limit + 1)

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = []
        for inline_keyboard in received.inline_keyboards:
            for row_of_buttons in inline_keyboard.rows:
                buttons.extend(row_of_buttons)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.more_buses)
