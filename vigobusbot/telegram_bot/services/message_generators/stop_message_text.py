"""STOP MESSAGE TEXT
Helper to generate the Stop Message text body
"""

import datetime
from typing import Optional, List

from vigobusbot.models import SavedUserStop, Stop, BusesResponse, Bus
from vigobusbot.static_handler import get_messages
from vigobusbot.settings_handler import telegram_settings

__all__ = ("generate_stop_message_text",)


def generate_stop_message_text(
        stop: Stop,
        buses_response: BusesResponse,
        user_saved_stop: Optional[SavedUserStop]
) -> str:
    messages = get_messages()

    # Generate Stop Name text
    if user_saved_stop and user_saved_stop.stop_name:
        stop_name_text = messages.stop.stop_custom_name.format(
            stop_custom_name=user_saved_stop.stop_name,
            stop_original_name=stop.name
        )
    else:
        stop_name_text = stop.name

    buses_text = "\n".join(_generate_buses_text_lines(buses_response.buses))
    last_update_text = datetime.datetime.now().strftime(messages.stop.time_format)

    return messages.stop.message.format(
        stop_id=stop.stop_id,
        stop_name=stop_name_text,
        buses=buses_text,
        last_update=last_update_text
    )


def _generate_buses_text_lines(buses: List[Bus]) -> List[str]:
    if not buses:
        return [get_messages().stop.no_buses_found]

    return [_generate_bus_text_line(bus) for bus in buses]


def _generate_bus_text_line(bus: Bus) -> str:
    messages = get_messages()
    if bus.time == 0:
        time_text = messages.stop.bus_time_now
    else:
        if bus.time > telegram_settings.stop_messages_include_arrival_hour_after_minutes:
            arrival_time = bus.get_calculated_arrival_time().strftime(messages.stop.bus_arrival_time_format)
        else:
            arrival_time = ""

        time_text = messages.stop.bus_time_remaining.format(
            minutes=bus.time,
            arrival_time=arrival_time
        ).strip()

    return messages.stop.bus_line.format(
        line=bus.line,
        route=bus.route,
        time=time_text
    )
