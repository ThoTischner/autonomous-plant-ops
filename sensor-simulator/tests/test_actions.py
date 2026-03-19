import pytest
from src.equipment import EQUIPMENT


@pytest.fixture(autouse=True)
def _reset_equipment():
    """Reset all equipment state before each test."""
    for cfg in EQUIPMENT.values():
        cfg.reset()
    yield
    for cfg in EQUIPMENT.values():
        cfg.reset()



async def test_shutdown_equipment(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "P-101",
        "action": "shutdown_equipment",
        "reason": "Emergency shutdown test",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["equipment_id"] == "P-101"
    assert body["action"] == "shutdown_equipment"
    assert "shut down" in body["message"].lower()



async def test_increase_cooling(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "R-201",
        "action": "increase_cooling",
        "reason": "Temperature rising",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["action"] == "increase_cooling"
    assert "cooling" in body["message"].lower()



async def test_reduce_speed(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "C-301",
        "action": "reduce_speed",
        "reason": "High vibration",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["action"] == "reduce_speed"
    assert "speed" in body["message"].lower()



async def test_adjust_setpoint(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "P-101",
        "action": "adjust_setpoint",
        "reason": "Resetting to normal",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["action"] == "adjust_setpoint"
    assert "reset" in body["message"].lower() or "setpoint" in body["message"].lower()



async def test_no_action(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "R-201",
        "action": "no_action",
        "reason": "All nominal",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["action"] == "no_action"



async def test_alert_operator(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "P-101",
        "action": "alert_operator",
        "reason": "Bearing wear detected",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["action"] == "alert_operator"
    assert "operator" in body["message"].lower()



async def test_unknown_equipment(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "UNKNOWN-999",
        "action": "shutdown_equipment",
        "reason": "Test",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "unknown" in body["message"].lower()



async def test_action_response_has_timestamp(client):
    resp = await client.post("/actions/execute", json={
        "equipment_id": "P-101",
        "action": "no_action",
        "reason": "",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "timestamp" in body
