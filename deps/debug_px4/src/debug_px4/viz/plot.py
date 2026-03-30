from collections import deque
from typing import Any

import matplotlib.pyplot as plt


class RealTimePlot:
    def __init__(self, handler: Any, max_points: int = 500):
        self._handler = handler
        self._max_points = max_points
        self._timestamps: deque[float] = deque(maxlen=max_points)
        self._data: dict[str, deque[float]] = {}
        self._fig, self._ax = plt.subplots()
        self._lines: dict[str, Any] = {}

        for field in handler.get_plot_fields():
            self._data[field] = deque(maxlen=max_points)

    def on_data(self, raw: bytes) -> None:
        msg = self._handler.decode(raw)
        t = msg.timestamp / 1e6
        self._timestamps.append(t)

        for field in self._data:
            val = getattr(msg, field, None)
            if val is None and hasattr(msg, field.split("_")[0]):
                base = field.split("_")[0]
                val = getattr(msg, base, 0)
            self._data[field].append(val if val is not None else 0)

        self._update_plot()

    def _update_plot(self) -> None:
        if len(self._timestamps) < 2:
            return

        self._ax.clear()
        ts = list(self._timestamps)
        ts0 = ts[0]
        ts_rel = [t - ts0 for t in ts]

        for field, values in self._data.items():
            self._ax.plot(ts_rel, list(values), label=field)

        self._ax.set_xlabel("Time (s)")
        self._ax.legend(loc="upper right", fontsize="small")
        self._ax.grid(True, alpha=0.3)
        plt.draw()
        plt.pause(0.001)

    def show(self) -> None:
        plt.show()
