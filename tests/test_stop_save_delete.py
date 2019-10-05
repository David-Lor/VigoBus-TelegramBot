"""TESTS - STOP SAVE/DELETE
"""

# # Installed # #
import pytest

# # Package # #
from .utils import *


class TestStopSaveDelete(BasePersistenceBusAPITest):
    """Request the bot for Stop commands, then Save or Delete the stop and verify
    """

    def teardown_method(self):
        self.persistence_api.clear()

    @pytest.fixture
    def stop(self):
        stop, buses = given_stop_and_buses()
        self.bus_api.set_data(BusData(stop=stop, buses=buses))
        return stop

    def test_not_saved_stop_should_have_save_button(self, stop):
        """Having a stop not saved, the Stop message should have the Save button
        """
        self.debug_test_name()

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.save)

    def test_saved_stop_should_have_delete_button(self, stop):
        """Having a stop saved, the Stop message should have the Delete button
        """
        self.debug_test_name()

        self.persistence_api.save_stop(stop_id=stop.stopid, user_id=self.user_id)

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)

        assert any(b for b in buttons if b.text == self.messages.stop.buttons.delete)

    def test_not_saved_stop_press_save_button(self, stop):
        """Having a stop not saved, when the Save button is pressed, the stop should get saved,
        and the Stop message Save button updated with the Delete button
        """
        self.debug_test_name()

        received = self.client.send_message_await(text=str(stop.stopid), num_expected=1)
        buttons = self.parse_message_buttons(received)
        save_button = next(b for b in buttons if b.text == self.messages.stop.buttons.save)

        received = self.press_inline_button(received, save_button.text)

        # The Stop should be saved
        assert self.persistence_api.get_stop(self.client.user_id, stop.stopid)

        # The message should be updated with the Delete button
        buttons = self.parse_message_buttons(received)
        assert any(b for b in buttons if b.text == self.messages.stop.buttons.delete)
