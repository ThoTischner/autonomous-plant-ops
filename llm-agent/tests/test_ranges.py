import httpx
import pytest

from src import ranges
from src.prompts import build_user_prompt

ITEMS = [
    {
        "equipment_id": "P-101", "etype": "pump",
        "temperature": {"min": 60, "max": 80, "unit": "°C"},
        "pressure": {"min": 2, "max": 4, "unit": "bar"},
        "vibration": {"min": 0, "max": 5, "unit": "mm/s"},
        "flow_rate": {"min": 100, "max": 150, "unit": "L/min"},
    }
]


def test_format_ranges():
    txt = ranges.format_ranges(ITEMS)
    assert "P-101 (pump)" in txt
    assert "temperature 60-80°C" in txt
    assert "flow 100-150L/min" in txt


def test_build_user_prompt_includes_ranges():
    p = build_user_prompt(
        [{"equipment_id": "P-101", "temperature": 70, "pressure": 3,
          "vibration": 1, "status": "normal"}],
        ranges_text="- P-101 (pump): temperature 60-80°C",
    )
    assert "NORMAL RANGES (current plant configuration):" in p
    assert "P-101 (pump): temperature 60-80°C" in p


async def test_get_ranges_text_fallback(monkeypatch):
    ranges._cache.update(t=0.0, text="")

    class _Boom:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, *a, **k):
            raise httpx.ConnectError("down")

    monkeypatch.setattr(httpx, "AsyncClient", _Boom)
    txt = await ranges.get_ranges_text()
    assert "FL-401" in txt and "AGV-601" in txt  # static fallback


@pytest.mark.parametrize("flow", [None, {"min": 1, "max": 2, "unit": "x"}])
def test_format_handles_optional_flow(flow):
    item = {**ITEMS[0], "flow_rate": flow}
    txt = ranges.format_ranges([item])
    assert ("flow 1-2x" in txt) == (flow is not None)
