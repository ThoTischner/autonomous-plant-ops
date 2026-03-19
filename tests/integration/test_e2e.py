"""
End-to-end integration tests that run against live Docker services.

These tests expect the following services to be running on the Docker network:
  - sensor-simulator at http://sensor-simulator:8001
  - dashboard-api at http://dashboard-api:8003
"""

import httpx
import pytest

SENSOR_SIM_URL = "http://sensor-simulator:8001"
DASHBOARD_API_URL = "http://dashboard-api:8003"


@pytest.fixture(scope="module")
def sensor_client():
    with httpx.Client(base_url=SENSOR_SIM_URL, timeout=10.0) as client:
        yield client


@pytest.fixture(scope="module")
def dashboard_client():
    with httpx.Client(base_url=DASHBOARD_API_URL, timeout=10.0) as client:
        yield client


# --- Sensor Simulator Tests ---


def test_sensor_simulator_health(sensor_client):
    resp = sensor_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "sensor-simulator"


def test_sensor_simulator_returns_sensor_data(sensor_client):
    resp = sensor_client.get("/sensors/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Should have 3 equipment: P-101, R-201, C-301
    assert len(data) >= 3
    equipment_ids = {r["equipment_id"] for r in data}
    assert "P-101" in equipment_ids
    assert "R-201" in equipment_ids
    assert "C-301" in equipment_ids


def test_sensor_simulator_reading_has_expected_fields(sensor_client):
    resp = sensor_client.get("/sensors/latest")
    data = resp.json()
    for reading in data:
        assert "equipment_id" in reading
        assert "equipment_name" in reading
        assert "temperature" in reading
        assert "pressure" in reading
        assert "vibration" in reading
        assert "status" in reading
        assert "timestamp" in reading


def test_sensor_simulator_trigger_scenario(sensor_client):
    resp = sensor_client.post("/scenarios/trigger", json={
        "scenario": "thermal_runaway",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "thermal_runaway" in body["message"]


def test_sensor_simulator_list_scenarios(sensor_client):
    resp = sensor_client.get("/scenarios/list")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert "thermal_runaway" in scenarios
    assert "bearing_degradation" in scenarios


def test_sensor_simulator_execute_action(sensor_client):
    resp = sensor_client.post("/actions/execute", json={
        "equipment_id": "P-101",
        "action": "no_action",
        "reason": "Integration test",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["equipment_id"] == "P-101"


def test_sensor_simulator_history(sensor_client):
    resp = sensor_client.get("/sensors/history/P-101", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# --- Dashboard API Tests ---


def test_dashboard_api_health(dashboard_client):
    resp = dashboard_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"


def test_dashboard_api_post_and_get_event(dashboard_client):
    # Post an event
    post_resp = dashboard_client.post("/events", json={
        "event_type": "sensor_reading",
        "data": {"equipment_id": "P-101", "temperature": 72.5},
        "equipment_id": "P-101",
    })
    assert post_resp.status_code == 200
    assert post_resp.json()["status"] == "ok"

    # Retrieve events
    get_resp = dashboard_client.get("/events")
    assert get_resp.status_code == 200
    events = get_resp.json()
    assert len(events) >= 1

    # Find our posted event
    matching = [e for e in events if e.get("equipment_id") == "P-101"]
    assert len(matching) >= 1


def test_dashboard_api_event_type_filter(dashboard_client):
    # Post events of different types
    dashboard_client.post("/events", json={
        "event_type": "anomaly_detected",
        "data": {"sensor": "temperature", "value": 215.0},
        "equipment_id": "R-201",
        "severity": "high",
    })
    dashboard_client.post("/events", json={
        "event_type": "action_executed",
        "data": {"action": "increase_cooling"},
        "equipment_id": "R-201",
    })

    # Filter by anomaly_detected
    resp = dashboard_client.get("/events", params={"event_type": "anomaly_detected"})
    assert resp.status_code == 200
    events = resp.json()
    for event in events:
        assert event["event_type"] == "anomaly_detected"


def test_dashboard_api_post_scenario_event(dashboard_client):
    resp = dashboard_client.post("/events", json={
        "event_type": "scenario_triggered",
        "data": {"scenario": "compressor_surge", "equipment_id": "C-301"},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "event_id" in body
