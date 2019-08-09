"""STOP MESSAGE BUTTONS
Helper to generate the Stop Message buttons markup
"""

# # Project # #
from ...static_handler import *
from ...entities import *

# # Package # #
from .source_context import *

__all__ = ("generate_stop_message_buttons",)


def generate_stop_message_buttons(context: SourceContext):
    messages = get_messages()

    return None
