import asyncio
from collections import deque

from .models import Event, EventType


class EventStore:
    def __init__(self, maxlen: int = 1000):
        self._events: deque[Event] = deque(maxlen=maxlen)
        self._subscribers: list[asyncio.Queue] = []

    async def add(self, event: Event) -> None:
        self._events.append(event)
        for queue in self._subscribers:
            await queue.put(event)

    def get_all(self, limit: int = 100) -> list[Event]:
        items = list(self._events)
        return items[-limit:]

    def get_by_type(self, event_type: EventType, limit: int = 50) -> list[Event]:
        filtered = [e for e in self._events if e.event_type == event_type]
        return filtered[-limit:]

    def get_latest(self, n: int = 10) -> list[Event]:
        items = list(self._events)
        return items[-n:]

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)
