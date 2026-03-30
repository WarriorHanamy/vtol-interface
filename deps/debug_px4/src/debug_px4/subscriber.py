from collections.abc import Callable
from typing import Any

import zenoh


class ZenohSubscriber:
    def __init__(self, config: dict[str, Any] | None = None):
        self._session: zenoh.Session | None = None
        self._subscribers: list[zenoh.Subscriber] = []
        self._config = config or {}

    def connect(self, mode: str = "peer", locator: str = "") -> None:
        conf = zenoh.Config()
        conf.insert_json5("mode", f'"{mode}"')
        if locator:
            conf.insert_json5("connect/endpoints", f'["{locator}"]')
        self._session = zenoh.open(conf)

    def subscribe(self, keyexpr: str, callback: Callable[[bytes], None]) -> zenoh.Subscriber:
        if self._session is None:
            raise RuntimeError("Session not connected")

        def _cb(sample: zenoh.Sample):
            callback(bytes(sample.payload))

        sub = self._session.declare_subscriber(keyexpr, _cb)
        self._subscribers.append(sub)
        return sub

    def close(self) -> None:
        for sub in self._subscribers:
            sub.undeclare()
        if self._session:
            self._session.close()
        self._subscribers.clear()
        self._session = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
