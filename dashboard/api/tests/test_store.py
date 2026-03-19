import asyncio

import pytest

from src.models import Event, EventType
from src.store import EventStore


@pytest.fixture
def store():
    return EventStore(maxlen=10)



async def test_add_and_get_all(store):
    event = Event(event_type=EventType.SENSOR_READING, data={"temp": 72.0})
    await store.add(event)
    events = store.get_all()
    assert len(events) == 1
    assert events[0].event_type == EventType.SENSOR_READING
    assert events[0].data["temp"] == 72.0



async def test_get_all_respects_limit(store):
    for i in range(5):
        await store.add(Event(event_type=EventType.SENSOR_READING, data={"i": i}))
    events = store.get_all(limit=3)
    assert len(events) == 3
    # Should return the last 3
    assert events[0].data["i"] == 2
    assert events[-1].data["i"] == 4



async def test_get_by_type(store):
    await store.add(Event(event_type=EventType.SENSOR_READING, data={"a": 1}))
    await store.add(Event(event_type=EventType.ANOMALY_DETECTED, data={"b": 2}))
    await store.add(Event(event_type=EventType.SENSOR_READING, data={"c": 3}))

    anomalies = store.get_by_type(EventType.ANOMALY_DETECTED)
    assert len(anomalies) == 1
    assert anomalies[0].data["b"] == 2

    readings = store.get_by_type(EventType.SENSOR_READING)
    assert len(readings) == 2



async def test_get_by_type_with_limit(store):
    for i in range(5):
        await store.add(Event(event_type=EventType.SENSOR_READING, data={"i": i}))
    readings = store.get_by_type(EventType.SENSOR_READING, limit=2)
    assert len(readings) == 2
    assert readings[-1].data["i"] == 4



async def test_get_latest(store):
    for i in range(5):
        await store.add(Event(event_type=EventType.SENSOR_READING, data={"i": i}))
    latest = store.get_latest(n=3)
    assert len(latest) == 3
    assert latest[0].data["i"] == 2
    assert latest[-1].data["i"] == 4



async def test_maxlen_enforcement(store):
    # store has maxlen=10
    for i in range(15):
        await store.add(Event(event_type=EventType.SENSOR_READING, data={"i": i}))
    all_events = store.get_all(limit=100)
    assert len(all_events) == 10
    # Oldest should be dropped, so first remaining should be i=5
    assert all_events[0].data["i"] == 5
    assert all_events[-1].data["i"] == 14



async def test_subscribe_and_unsubscribe(store):
    queue = store.subscribe()
    assert queue in store._subscribers

    store.unsubscribe(queue)
    assert queue not in store._subscribers



async def test_subscriber_receives_events(store):
    queue = store.subscribe()
    event = Event(event_type=EventType.ACTION_EXECUTED, data={"action": "shutdown"})
    await store.add(event)

    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.event_type == EventType.ACTION_EXECUTED
    assert received.data["action"] == "shutdown"
    store.unsubscribe(queue)



async def test_empty_store(store):
    assert store.get_all() == []
    assert store.get_by_type(EventType.SENSOR_READING) == []
    assert store.get_latest() == []



async def test_event_has_auto_id(store):
    event = Event(event_type=EventType.SENSOR_READING, data={})
    await store.add(event)
    stored = store.get_all()[0]
    assert stored.id is not None
    assert len(stored.id) > 0



async def test_event_has_auto_timestamp(store):
    event = Event(event_type=EventType.SENSOR_READING, data={})
    await store.add(event)
    stored = store.get_all()[0]
    assert stored.timestamp is not None
