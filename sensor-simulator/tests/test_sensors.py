import pytest
from src.simulator import simulator


@pytest.fixture(autouse=True)
def _seed_simulator():
    """Ensure the simulator has at least one reading per equipment."""
    for eid in ("P-101", "R-201", "C-301"):
        simulator.generate_reading(eid)
    yield



async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "sensor-simulator"



async def test_get_latest_returns_list(client):
    resp = await client.get("/sensors/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    equipment_ids = {r["equipment_id"] for r in data}
    assert "P-101" in equipment_ids
    assert "R-201" in equipment_ids
    assert "C-301" in equipment_ids



async def test_get_latest_reading_structure(client):
    resp = await client.get("/sensors/latest")
    assert resp.status_code == 200
    reading = resp.json()[0]
    required_fields = {
        "equipment_id",
        "equipment_name",
        "timestamp",
        "temperature",
        "pressure",
        "vibration",
        "status",
    }
    assert required_fields.issubset(reading.keys())
    assert isinstance(reading["temperature"], (int, float))
    assert isinstance(reading["pressure"], (int, float))
    assert isinstance(reading["vibration"], (int, float))



async def test_get_latest_specific_equipment(client):
    resp = await client.get("/sensors/latest/P-101")
    assert resp.status_code == 200
    data = resp.json()
    assert data["equipment_id"] == "P-101"
    assert data["equipment_name"] == "Pump P-101"



async def test_get_history(client):
    resp = await client.get("/sensors/history/P-101")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["equipment_id"] == "P-101"



async def test_get_history_unknown_equipment(client):
    resp = await client.get("/sensors/history/UNKNOWN")
    assert resp.status_code == 200
    assert resp.json() == []



async def test_get_history_limit(client):
    # Generate multiple readings
    for _ in range(5):
        simulator.generate_reading("R-201")
    resp = await client.get("/sensors/history/R-201", params={"limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 2
