from src.prompts import build_user_prompt, get_system_prompt


def test_get_system_prompt_not_empty():
    prompt = get_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100


def test_get_system_prompt_contains_equipment_info():
    prompt = get_system_prompt()
    assert "P-101" in prompt
    assert "R-201" in prompt
    assert "C-301" in prompt


def test_get_system_prompt_contains_json_structure():
    prompt = get_system_prompt()
    assert "anomalies" in prompt
    assert "reasoning" in prompt
    assert "actions" in prompt


def test_get_system_prompt_contains_action_types():
    prompt = get_system_prompt()
    assert "shutdown_equipment" in prompt
    assert "increase_cooling" in prompt
    assert "reduce_speed" in prompt
    assert "adjust_setpoint" in prompt


def test_build_user_prompt_formats_sensor_data():
    sensors = [
        {
            "equipment_id": "P-101",
            "equipment_name": "Pump P-101",
            "temperature": 75.0,
            "pressure": 3.2,
            "vibration": 2.1,
            "flow_rate": 130.0,
            "status": "normal",
        }
    ]
    prompt = build_user_prompt(sensors)
    assert "P-101" in prompt
    assert "75.0" in prompt
    assert "3.2" in prompt
    assert "2.1" in prompt
    assert "130.0" in prompt
    assert "normal" in prompt


def test_build_user_prompt_without_flow_rate():
    sensors = [
        {
            "equipment_id": "R-201",
            "equipment_name": "Reactor R-201",
            "temperature": 175.0,
            "pressure": 7.5,
            "vibration": 1.8,
            "flow_rate": None,
            "status": "normal",
        }
    ]
    prompt = build_user_prompt(sensors)
    assert "R-201" in prompt
    assert "175.0" in prompt


def test_build_user_prompt_with_history():
    sensors = [
        {
            "equipment_id": "P-101",
            "equipment_name": "Pump P-101",
            "temperature": 75.0,
            "pressure": 3.2,
            "vibration": 2.1,
            "status": "normal",
        }
    ]
    history = [{"equipment_id": "P-101", "temperature": 73.0}]
    prompt = build_user_prompt(sensors, history=history)
    assert "Historie" in prompt


def test_build_user_prompt_with_recent_actions():
    sensors = [
        {
            "equipment_id": "P-101",
            "equipment_name": "Pump P-101",
            "temperature": 75.0,
            "pressure": 3.2,
            "vibration": 2.1,
            "status": "normal",
        }
    ]
    actions = [{"action": "increase_cooling", "equipment_id": "P-101"}]
    prompt = build_user_prompt(sensors, recent_actions=actions)
    assert "Aktionen" in prompt


def test_build_user_prompt_multiple_sensors():
    sensors = [
        {
            "equipment_id": "P-101",
            "equipment_name": "Pump P-101",
            "temperature": 75.0,
            "pressure": 3.2,
            "vibration": 2.1,
            "status": "normal",
        },
        {
            "equipment_id": "R-201",
            "equipment_name": "Reactor R-201",
            "temperature": 180.0,
            "pressure": 8.0,
            "vibration": 1.5,
            "status": "warning",
        },
    ]
    prompt = build_user_prompt(sensors)
    assert "P-101" in prompt
    assert "R-201" in prompt
    assert "JSON" in prompt


def test_build_user_prompt_ends_with_instruction():
    sensors = [
        {
            "equipment_id": "P-101",
            "equipment_name": "Pump P-101",
            "temperature": 75.0,
            "pressure": 3.2,
            "vibration": 2.1,
            "status": "normal",
        }
    ]
    prompt = build_user_prompt(sensors)
    assert prompt.strip().endswith("JSON.")
