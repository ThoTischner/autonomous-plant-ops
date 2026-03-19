import pytest

from src.routes.events import store


@pytest.fixture(autouse=True)
def _clear_store():
    """Clear the event store before each test."""
    store._events.clear()
    yield
    store._events.clear()



async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"



async def test_post_event(client):
    resp = await client.post("/events", json={
        "event_type": "sensor_reading",
        "data": {"equipment_id": "P-101", "temperature": 72.0},
        "equipment_id": "P-101",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "event_id" in body



async def test_get_events_empty(client):
    resp = await client.get("/events")
    assert resp.status_code == 200
    assert resp.json() == []



async def test_post_and_get_events(client):
    # Post an event
    await client.post("/events", json={
        "event_type": "anomaly_detected",
        "data": {"equipment_id": "R-201", "sensor": "temperature", "value": 215.0},
        "equipment_id": "R-201",
        "severity": "high",
    })

    # Retrieve it
    resp = await client.get("/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 1
    assert events[0]["event_type"] == "anomaly_detected"
    assert events[0]["equipment_id"] == "R-201"
    assert events[0]["severity"] == "high"
    assert events[0]["data"]["sensor"] == "temperature"



async def test_get_events_with_type_filter(client):
    # Post events of different types
    await client.post("/events", json={
        "event_type": "sensor_reading",
        "data": {"temperature": 72.0},
        "equipment_id": "P-101",
    })
    await client.post("/events", json={
        "event_type": "anomaly_detected",
        "data": {"sensor": "temperature"},
        "equipment_id": "R-201",
        "severity": "high",
    })
    await client.post("/events", json={
        "event_type": "action_executed",
        "data": {"action": "increase_cooling"},
        "equipment_id": "R-201",
    })

    # Filter by anomaly_detected
    resp = await client.get("/events", params={"event_type": "anomaly_detected"})
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 1
    assert events[0]["event_type"] == "anomaly_detected"



async def test_get_events_with_limit(client):
    for i in range(5):
        await client.post("/events", json={
            "event_type": "sensor_reading",
            "data": {"index": i},
        })

    resp = await client.get("/events", params={"limit": 2})
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 2



async def test_multiple_event_types(client):
    await client.post("/events", json={
        "event_type": "scenario_triggered",
        "data": {"scenario": "thermal_runaway"},
    })
    await client.post("/events", json={
        "event_type": "agent_analysis",
        "data": {"reasoning": "All normal"},
    })

    resp = await client.get("/events")
    events = resp.json()
    assert len(events) == 2

    types = {e["event_type"] for e in events}
    assert "scenario_triggered" in types
    assert "agent_analysis" in types



async def test_event_has_id_and_timestamp(client):
    await client.post("/events", json={
        "event_type": "sensor_reading",
        "data": {"test": True},
    })

    resp = await client.get("/events")
    event = resp.json()[0]
    assert "id" in event
    assert "timestamp" in event
    assert len(event["id"]) > 0
