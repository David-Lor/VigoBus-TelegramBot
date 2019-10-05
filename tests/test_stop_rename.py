"""TESTS - STOP RENAME
"""

# # Installed # #
import pytest

# # Package # #
from .utils import *


class TestStopRename(BasePersistenceBusAPITest):
    """
    """

    def teardown_method(self):
        self.persistence_api.clear()

    def _given_stop(self):
        stop, buses = given_stop_and_buses()
        self.bus_api.set_data(BusData(stop=stop, buses=buses))
        return stop

    @pytest.fixture
    def stop(self):
        return self._given_stop()

    @pytest.fixture
    def saved_stop(self):
        stop = self._given_stop()
        self.persistence_api.save_stop(stop_id=stop.stopid, user_id=self.user_id)
        return stop

    def test_saved_stop_should_have_rename_button(self, saved_stop):
        """Having a stop saved, the Stop message should have the Rename button
        """
        self.debug_test_name()

        received = self.client.send_message_await(text=str(saved_stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.rename)

    def test_not_saved_stop_should_not_have_rename_button(self, stop):
        """Having a stop not saved, the Stop message should not have the Rename button
        """
        self.debug_test_name()

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert not sum(1 for b in buttons if b.text == self.messages.stop.buttons.rename)

    def test_saved_stop_press_rename_button(self, saved_stop):
        """Having a stop saved, do the whole Rename procedure."""
        self.debug_test_name()

        received = self.client.send_message_await(text=str(saved_stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)
        rename_button = next(b for b in buttons if b.text == self.messages.stop.buttons.rename)

        received = self.press_inline_button(received, rename_button.text, num_expected=1)
        print("RX", type(received))
        raise AssertionError
