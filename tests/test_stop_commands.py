"""TESTS - STOP COMMANDS
"""

# # Native # #
import datetime

# # Package # #
from .utils import *


class TestStopCommands(BaseBusAPITest):
    """Request the bot for Stop commands, that should return buses arriving to a stop in real time
    """

    def test_stop_not_exists(self):
        """Should return a message warning that the Stop does not exist when the API Stop endpoint returns 404
        """
        self.debug_test_name()

        stop_id = given_stop_id()

        received_text = self.send_message_await_text(message_text=str(stop_id))

        assert received_text == self.messages.stop.not_exists

    def test_stop_id_name(self):
        """Should return a message with the Stop info (ID, Name) on it
        """
        self.debug_test_name()

        stop = given_stop()
        self.bus_api.set_data(BusData(stop=stop, buses=given_buses()))

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert str(stop.stopid) in received_text
        assert stop.name in received_text

    def test_stop_buses(self):
        """Should return a message with all the Buses on it (having many buses as the initial bus limit).
        At least one of the buses is arriving now (time=0). The message should contain one bus line per bus available,
        formatted with the bus line, route and time.
        """
        self.debug_test_name()

        stop = given_stop()
        buses = [given_bus() for _ in range(settings.buses_limit - 1)]
        buses.append(given_bus(time=0))
        self.bus_api.set_data(BusData(stop=stop, buses=buses))

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
        self.debug_test_name()

        stop = given_stop()
        self.bus_api.set_data(BusData(stop=stop, buses=[]))

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert self.messages.stop.no_buses_found in received_text

    def test_stop_last_update(self):
        """Should return a message with the timestamp when the message was generated.
        """
        self.debug_test_name()

        stop = given_stop()
        self.bus_api.set_data(BusData(stop=stop, buses=given_buses()))

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        now = datetime.datetime.now()
        try:
            assert now.strftime(self.messages.stop.time_format) in received_text
        except AssertionError:
            assert (now - datetime.timedelta(seconds=1)).strftime(self.messages.stop.time_format) in received_text

    def test_stop_generic_error_stop_endpoint(self):
        """Should return a generic error message when the API Stop endpoint returns 500
        """
        self.debug_test_name()

        stop_id = given_stop_id()
        self.bus_api.set_data(BusData(stop=Exception(), buses=given_buses, stop_id_should_exist=stop_id))

        received_text = self.send_message_await_text(message_text=str(stop_id))

        assert received_text == self.messages.generic.generic_error

    def test_stop_generic_error_buses_endpoint(self):
        """Should return a generic error message when the API Buses endpoint returns 500
        """
        self.debug_test_name()

        stop = given_stop()
        self.bus_api.set_data(BusData(stop=stop, buses=Exception()))

        received_text = self.send_message_await_text(message_text=str(stop.stopid))

        assert received_text == self.messages.generic.generic_error

    def test_stop_default_buttons(self):
        """Should return a message with a Update button, a Save Stop button
        """
        self.debug_test_name()

        stop = given_stop()
        self.bus_api.set_data(BusData(stop=stop, buses=given_buses()))

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.save)
        assert any(b for b in buttons if b.text == self.messages.stop.buttons.refresh)

    def test_stop_more_buses_button(self):
        """Should return a message with the More Buses button if more buses than the initial bus limit are available
        """
        self.debug_test_name()

        stop = given_stop()
        buses = given_buses(limit=settings.buses_limit + 1)
        self.bus_api.set_data(BusData(stop=stop, buses=buses))

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.more_buses)
