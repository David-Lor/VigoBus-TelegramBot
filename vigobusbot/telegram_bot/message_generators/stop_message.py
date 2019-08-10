"""STOP MESSAGE
Generator of Stop message body. Have responsability to find the Stop and Buses
"""

# # Native # #
import asyncio
from typing import Tuple

# # Project # #
from ...entities import *
from ...vigobus_getters import *

# # Package # #
from .source_context import *
from .stop_message_text import *
from .stop_message_buttons import *

__all__ = ("generate_stop_message",)


async def generate_stop_message(context: SourceContext) -> Tuple[str, None]:
    """Generate the Text body and Markup buttons to send as a Stop message, given a SourceContext
    """
    results = await asyncio.gather(
        get_stop(context.stopid),
        get_buses(context.stopid)
    )  # TODO Set Timeout?

    stop = None
    buses = None
    for result in results:
        if isinstance(result, Stop):
            stop = result
        elif isinstance(result, list):
            buses = result

    assert isinstance(stop, Stop)
    assert isinstance(buses, list)

    text = generate_stop_message_text(stop, buses)
    buttons = generate_stop_message_buttons(context=context)

    return text, buttons
