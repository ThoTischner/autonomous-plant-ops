import json

import pytest

from src import equipment as eq
from src.simulator import simulator

DEFAULT_IDS = {"FL-401", "FL-402", "TR-501", "AGV-601"}

NEW = {
    "equipment_id": "T-900",
    "name": "Test Unit",
    "etype": "pump",
    "temperature": {"min": 10, "max": 20, "unit": "°C"},
    "pressure": {"min": 1, "max": 2, "unit": "bar"},
    "vibration": {"min": 0, "max": 1, "unit": "mm/s"},
    "flow_rate": None,
}


@pytest.fixture(autouse=True)
def _iso(tmp_path, monkeypatch):
    monkeypatch.setattr(eq, "EQUIPMENT_FILE", str(tmp_path / "eq.json"))
    eq.reset_to_defaults()
    for eid in list(simulator.history):
        if eid not in eq.EQUIPMENT:
            simulator.forget(eid)
    for eid in eq.EQUIPMENT:
        simulator.ensure(eid)
    yield
    eq.reset_to_defaults()


async def test_list_defaults(client):
    r = await client.get("/equipment")
    assert r.status_code == 200
    ids = {e["equipment_id"] for e in r.json()}
    assert ids == DEFAULT_IDS


async def test_add_then_simulated(client):
    r = await client.post("/equipment", json=NEW)
    assert r.status_code == 201
    assert "T-900" in eq.EQUIPMENT
    assert "T-900" in simulator._drift  # picked up by simulator
    reading = simulator.generate_reading("T-900")
    assert reading.equipment_id == "T-900"


async def test_duplicate_conflict(client):
    await client.post("/equipment", json=NEW)
    r = await client.post("/equipment", json=NEW)
    assert r.status_code == 409


async def test_update(client):
    body = {**NEW, "name": "Renamed"}
    await client.post("/equipment", json=NEW)
    r = await client.put("/equipment/T-900", json=body)
    assert r.status_code == 200
    assert eq.EQUIPMENT["T-900"].name == "Renamed"


async def test_delete_and_guard_last(client):
    await client.post("/equipment", json=NEW)
    r = await client.delete("/equipment/T-900")
    assert r.status_code == 200
    assert "T-900" not in eq.EQUIPMENT
    assert "T-900" not in simulator.history

    # Delete down to one, last delete must be blocked.
    ids = [e["equipment_id"] for e in (await client.get("/equipment")).json()]
    for eid in ids[:-1]:
        assert (await client.delete(f"/equipment/{eid}")).status_code == 200
    last = await client.delete(f"/equipment/{ids[-1]}")
    assert last.status_code == 400


async def test_persistence_roundtrip(client):
    await client.post("/equipment", json=NEW)
    data = json.loads(open(eq.EQUIPMENT_FILE, encoding="utf-8").read())
    assert any(e["equipment_id"] == "T-900" for e in data)
    eq.EQUIPMENT.clear()
    eq.load()  # reload from file
    assert "T-900" in eq.EQUIPMENT


async def test_reset_endpoint(client):
    await client.post("/equipment", json=NEW)
    r = await client.post("/equipment/reset")
    assert r.status_code == 200
    ids = {e["equipment_id"] for e in r.json()}
    assert ids == DEFAULT_IDS
    assert "T-900" not in simulator.history
