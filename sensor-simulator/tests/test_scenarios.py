import pytest



async def test_trigger_valid_scenario(client):
    resp = await client.post("/scenarios/trigger", json={
        "scenario": "thermal_runaway",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "thermal_runaway" in body["message"]



async def test_trigger_scenario_with_equipment_id(client):
    resp = await client.post("/scenarios/trigger", json={
        "scenario": "bearing_degradation",
        "equipment_id": "P-101",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True



async def test_trigger_invalid_scenario_returns_available(client):
    resp = await client.post("/scenarios/trigger", json={
        "scenario": "nonexistent_scenario",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "unknown" in body["message"].lower()
    assert body["available"] is not None
    assert "thermal_runaway" in body["available"]
    assert "bearing_degradation" in body["available"]
    assert "compressor_surge" in body["available"]
    assert "pressure_spike" in body["available"]



async def test_list_scenarios(client):
    resp = await client.get("/scenarios/list")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert isinstance(scenarios, list)
    assert len(scenarios) == 4
    assert "thermal_runaway" in scenarios
    assert "bearing_degradation" in scenarios
    assert "compressor_surge" in scenarios
    assert "pressure_spike" in scenarios



async def test_trigger_all_valid_scenarios(client):
    for scenario in ["thermal_runaway", "bearing_degradation", "compressor_surge", "pressure_spike"]:
        resp = await client.post("/scenarios/trigger", json={"scenario": scenario})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
