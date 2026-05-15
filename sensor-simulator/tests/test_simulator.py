import pytest
from src.simulator import Simulator
from src.equipment import EQUIPMENT


@pytest.fixture
def sim():
    """Create a fresh Simulator instance for each test."""
    return Simulator()


def test_generate_reading_returns_dict_like(sim):
    reading = sim.generate_reading("FL-401")
    assert reading.equipment_id == "FL-401"
    assert reading.equipment_name == "Gabelstapler FL-401"
    assert isinstance(reading.temperature, float)
    assert isinstance(reading.pressure, float)
    assert isinstance(reading.vibration, float)
    assert reading.flow_rate is not None  # FL-401 has flow_rate


def test_generate_reading_without_flow_rate(sim):
    reading = sim.generate_reading("AGV-601")
    assert reading.equipment_id == "AGV-601"
    assert reading.flow_rate is None  # AGV-601 has no flow_rate


def test_generate_reading_updates_latest(sim):
    assert "FL-401" not in sim.latest
    reading = sim.generate_reading("FL-401")
    assert sim.latest["FL-401"] == reading


def test_generate_reading_appends_to_history(sim):
    assert len(sim.history["FL-401"]) == 0
    sim.generate_reading("FL-401")
    assert len(sim.history["FL-401"]) == 1
    sim.generate_reading("FL-401")
    assert len(sim.history["FL-401"]) == 2


def test_add_drift_changes_values(sim):
    # Generate a baseline reading
    baseline = sim.generate_reading("FL-401")

    # Add large temperature drift
    for _ in range(10):
        sim.add_drift("FL-401", "temperature", 10.0)

    # Generate readings after drift — temperature should be noticeably higher
    readings_after = [sim.generate_reading("FL-401") for _ in range(5)]
    avg_temp_after = sum(r.temperature for r in readings_after) / len(readings_after)

    # The drift of 100 degrees should make it much higher than baseline
    assert avg_temp_after > baseline.temperature + 20


def test_reset_drift_restores(sim):
    # Add drift
    sim.add_drift("FL-401", "temperature", 100.0)
    sim.add_drift("FL-401", "pressure", 50.0)

    # Reset
    sim.reset_drift("FL-401")

    # After reset, drift dict should be zeroed
    drift = sim._drift["FL-401"]
    assert drift["temperature"] == 0
    assert drift["pressure"] == 0
    assert drift["vibration"] == 0
    assert drift["flow_rate"] == 0


def test_all_equipment_ids_have_history(sim):
    for eid in EQUIPMENT:
        assert eid in sim.history


def test_shutdown_equipment_reading(sim):
    cfg = EQUIPMENT["FL-401"]
    cfg.is_shutdown = True
    try:
        reading = sim.generate_reading("FL-401")
        assert reading.status == "shutdown"
        assert reading.pressure == 0.0
        assert reading.vibration == 0.0
    finally:
        cfg.is_shutdown = False


def test_generate_reading_normal_status(sim):
    # With default config, readings should typically be normal
    reading = sim.generate_reading("FL-401")
    assert reading.status in ("normal", "warning", "critical", "shutdown")


def test_add_drift_unknown_sensor_ignored(sim):
    # Should not raise
    sim.add_drift("FL-401", "nonexistent_sensor", 10.0)


def test_add_drift_unknown_equipment_ignored(sim):
    # Should not raise
    sim.add_drift("UNKNOWN-999", "temperature", 10.0)
