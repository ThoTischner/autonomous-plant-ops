from collections import deque
from datetime import datetime


class RollingContext:
    """Maintains a rolling window of sensor readings and executed actions."""

    def __init__(self) -> None:
        self._readings: deque[dict] = deque(maxlen=60)
        self._actions: deque[dict] = deque(maxlen=60)

    def add_reading(self, data: dict) -> None:
        entry = {**data, "recorded_at": datetime.utcnow().isoformat()}
        self._readings.append(entry)

    def add_action(self, action: dict) -> None:
        entry = {**action, "executed_at": datetime.utcnow().isoformat()}
        self._actions.append(entry)

    def get_history_summary(self) -> list[dict]:
        """Return the last 10 readings."""
        return list(self._readings)[-10:]

    def get_recent_actions(self) -> list[dict]:
        """Return all stored recent actions."""
        return list(self._actions)
