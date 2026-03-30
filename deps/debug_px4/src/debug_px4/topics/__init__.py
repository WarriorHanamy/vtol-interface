from collections.abc import Callable
from typing import Any

from debug_px4.topics.acc_rates_control import AccRatesControlHandler

_topic_handlers: dict[str, Any] = {
    "neupilot/debug/acc_rates_control": AccRatesControlHandler(),
}


def get_topic_handler(keyexpr: str):
    return _topic_handlers.get(keyexpr)
