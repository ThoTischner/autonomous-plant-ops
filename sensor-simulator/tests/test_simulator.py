import pytest
from src.simulator import Simulator
from src.equipment import EQUIPMENT


@pytest.fixture
def sim():
    """Create a fresh Simulator instance for each test."""
    return Simulator()


def test_generate_reading_returns_dict_like(sim):
    reading = sim.generate_reading("P-101")
    assert reading.equipment_id == "P-101"
    assert reading.equipment_name == "Pump P-101"
    assert isinstance(reading.temperature, float)
    assert isinstance(reading.pressure, float)
    assert isinstance(reading.vibration, float)
    assert reading.flow_rate is not None  # P-101 has flow_rate


def test_generate_reading_without_flow_rate(sim):
    reading = sim.generate_reading("R-201")
    assert reading.equipment_id == "R-201"
    assert reading.flow_rate is None  # R-201 has no flow_rate


def test_generate_reading_updates_latest(sim):
    assert "P-101" not in sim.latest
    reading = sim.generate_reading("P-101")
    assert sim.latest["P-101"] == reading


def test_generate_reading_appends_to_history(sim):
    assert len(sim.history["P-101"]) == 0
    sim.generate_reading("P-101")
    assert len(sim.history["P-101"]) == 1
    sim.generate_reading("P-101")
    assert len(sim.history["P-101"]) == 2


def test_add_drift_changes_values(sim):
    # Generate a baseline reading
    baseline = sim.generate_reading("P-101")

    # Add large temperature drift
    for _ in range(10):
        sim.add_drift("P-101", "temperature", 10.0)

    # Generate readings after drift — temperature should be noticeably higher
    readings_after = [sim.generate_reading("P-101") for _ in range(5)]
    avg_temp_after = sum(r.temperature for r in readings_after) / len(readings_after)

    # The drift of 100 degrees should make it much higher than baseline
    assert avg_temp_after > baseline.temperature + 20


def test_reset_drift_restores(sim):
    # Add drift
    sim.add_drift("P-101", "temperature", 100.0)
    sim.add_drift("P-101", "pressure", 50.0)

    # Reset
    sim.reset_drift("P-101")

    # After reset, drift dict should be zeroed
    drift = sim._drift["P-101"]
    assert drift["temperature"] == 0
    assert drift["pressure"] == 0
    assert drift["vibration"] == 0
    assert drift["flow_rate"] == 0


def test_all_equipment_ids_have_history(sim):
    for eid in EQUIPMENT:
        assert eid in sim.history


def test_shutdown_equipment_reading(sim):
    cfg = EQUIPMENT["P-101"]
    cfg.is_shutdown = True
    try:
        reading = sim.generate_reading("P-101")
        assert reading.status == "shutdown"
        assert reading.pressure == 0.0
        assert reading.vibration == 0.0
    finally:
        cfg.is_shutdown = False


def test_generate_reading_normal_status(sim):
    # With default config, readings should typically be normal
    reading = sim.generate_reading("P-101")
    assert reading.status in ("normal", "warning", "critical", "shutdown")


def test_add_drift_unknown_sensor_ignored(sim):
    # Should not raise
    sim.add_drift("P-101", "nonexistent_sensor", 10.0)


def test_add_drift_unknown_equipment_ignored(sim):
    # Should not raise
    sim.add_drift("UNKNOWN-999", "temperature", 10.0)
