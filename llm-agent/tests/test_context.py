from src.context import RollingContext


def test_add_reading():
    ctx = RollingContext()
    ctx.add_reading({"equipment_id": "P-101", "temperature": 72.0})
    summary = ctx.get_history_summary()
    assert len(summary) == 1
    assert summary[0]["equipment_id"] == "P-101"
    assert summary[0]["temperature"] == 72.0


def test_add_reading_includes_recorded_at():
    ctx = RollingContext()
    ctx.add_reading({"equipment_id": "P-101"})
    summary = ctx.get_history_summary()
    assert "recorded_at" in summary[0]


def test_add_action():
    ctx = RollingContext()
    ctx.add_action({"action": "increase_cooling", "equipment_id": "R-201"})
    actions = ctx.get_recent_actions()
    assert len(actions) == 1
    assert actions[0]["action"] == "increase_cooling"
    assert actions[0]["equipment_id"] == "R-201"


def test_add_action_includes_executed_at():
    ctx = RollingContext()
    ctx.add_action({"action": "no_action"})
    actions = ctx.get_recent_actions()
    assert "executed_at" in actions[0]


def test_get_history_summary_returns_max_10():
    ctx = RollingContext()
    for i in range(20):
        ctx.add_reading({"equipment_id": f"E-{i}", "temperature": float(i)})
    summary = ctx.get_history_summary()
    assert len(summary) == 10
    # Should return the last 10
    assert summary[0]["equipment_id"] == "E-10"
    assert summary[-1]["equipment_id"] == "E-19"


def test_get_recent_actions_returns_all():
    ctx = RollingContext()
    for i in range(5):
        ctx.add_action({"action": f"action_{i}"})
    actions = ctx.get_recent_actions()
    assert len(actions) == 5


def test_rolling_window_maxlen():
    ctx = RollingContext()
    # Internal deque maxlen is 60
    for i in range(70):
        ctx.add_reading({"index": i})
    # Only 60 should be stored internally
    summary = ctx.get_history_summary()
    assert len(summary) == 10  # get_history_summary returns last 10
    assert summary[-1]["index"] == 69


def test_actions_rolling_window():
    ctx = RollingContext()
    for i in range(70):
        ctx.add_action({"index": i})
    actions = ctx.get_recent_actions()
    # deque maxlen is 60, so oldest are dropped
    assert len(actions) == 60
    assert actions[0]["index"] == 10


def test_empty_context():
    ctx = RollingContext()
    assert ctx.get_history_summary() == []
    assert ctx.get_recent_actions() == []


def test_add_reading_preserves_original_data():
    ctx = RollingContext()
    original = {"equipment_id": "P-101", "temperature": 72.0, "pressure": 3.1}
    ctx.add_reading(original)
    summary = ctx.get_history_summary()
    assert summary[0]["equipment_id"] == "P-101"
    assert summary[0]["temperature"] == 72.0
    assert summary[0]["pressure"] == 3.1
