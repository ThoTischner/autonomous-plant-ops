from datetime import datetime, timezone

from src.models import (
    ActionType,
    AnalysisRequest,
    AnalysisResponse,
    Anomaly,
    RecommendedAction,
    SensorData,
    Severity,
)


def _make_sensor_data(**overrides):
    defaults = {
        "equipment_id": "P-101",
        "equipment_name": "Pump P-101",
        "temperature": 72.5,
        "pressure": 3.1,
        "vibration": 2.3,
        "flow_rate": 120.0,
        "status": "normal",
    }
    defaults.update(overrides)
    return SensorData(**defaults)


def test_sensor_data_instantiation():
    sd = _make_sensor_data()
    assert sd.equipment_id == "P-101"
    assert sd.temperature == 72.5
    assert sd.flow_rate == 120.0


def test_sensor_data_without_flow_rate():
    sd = _make_sensor_data(flow_rate=None)
    assert sd.flow_rate is None


def test_analysis_request_instantiation():
    sensor = _make_sensor_data()
    req = AnalysisRequest(sensors=[sensor])
    assert len(req.sensors) == 1
    assert req.history is None
    assert req.recent_actions is None


def test_analysis_request_with_history():
    sensor = _make_sensor_data()
    req = AnalysisRequest(
        sensors=[sensor],
        history=[{"equipment_id": "P-101", "temperature": 70.0}],
        recent_actions=[{"action": "no_action"}],
    )
    assert len(req.history) == 1
    assert len(req.recent_actions) == 1


def test_anomaly_instantiation():
    anomaly = Anomaly(
        equipment_id="R-201",
        sensor="temperature",
        value=215.0,
        normal_range="150-200°C",
        severity=Severity.high,
    )
    assert anomaly.equipment_id == "R-201"
    assert anomaly.severity == Severity.high
    assert anomaly.value == 215.0


def test_recommended_action_instantiation():
    action = RecommendedAction(
        equipment_id="R-201",
        action=ActionType.increase_cooling,
        reason="Temperature exceeds safe range",
        urgency=Severity.high,
        parameters={"target_temp": 180},
    )
    assert action.action == ActionType.increase_cooling
    assert action.urgency == Severity.high
    assert action.parameters["target_temp"] == 180


def test_recommended_action_default_parameters():
    action = RecommendedAction(
        equipment_id="P-101",
        action=ActionType.no_action,
        reason="All normal",
        urgency=Severity.low,
    )
    assert action.parameters == {}


def test_analysis_response_instantiation():
    response = AnalysisResponse(
        anomalies=[
            Anomaly(
                equipment_id="R-201",
                sensor="temperature",
                value=220.0,
                normal_range="150-200°C",
                severity=Severity.critical,
            )
        ],
        reasoning="Reactor temperature is dangerously high",
        actions=[
            RecommendedAction(
                equipment_id="R-201",
                action=ActionType.shutdown_equipment,
                reason="Critical temperature",
                urgency=Severity.critical,
            )
        ],
        timestamp=datetime.now(timezone.utc),
    )
    assert len(response.anomalies) == 1
    assert len(response.actions) == 1
    assert "dangerously" in response.reasoning


def test_analysis_response_empty_lists():
    response = AnalysisResponse(
        anomalies=[],
        reasoning="All systems nominal",
        actions=[],
        timestamp=datetime.now(timezone.utc),
    )
    assert response.anomalies == []
    assert response.actions == []


def test_severity_enum_values():
    assert Severity.low == "low"
    assert Severity.medium == "medium"
    assert Severity.high == "high"
    assert Severity.critical == "critical"


def test_action_type_enum_values():
    assert ActionType.adjust_setpoint == "adjust_setpoint"
    assert ActionType.reduce_speed == "reduce_speed"
    assert ActionType.increase_cooling == "increase_cooling"
    assert ActionType.shutdown_equipment == "shutdown_equipment"
    assert ActionType.alert_operator == "alert_operator"
    assert ActionType.no_action == "no_action"
