"""Fetch the current equipment definition from the sensor-simulator and
format it as a NORMAL RANGES block for the prompt. Short TTL cache with a
static fallback so the agent keeps working if the sim is briefly down."""
import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)

SENSOR_URL = os.environ.get("SENSOR_URL", "http://sensor-simulator:8001")
_TTL = 15.0
_cache: dict = {"t": 0.0, "text": ""}

_FALLBACK = (
    "- FL-401 (forklift): temperature 40-90°C, pressure 5-15 bar, "
    "vibration 0-6 mm/s, flow 10-40 L/min\n"
    "- FL-402 (forklift): temperature 40-90°C, pressure 5-15 bar, "
    "vibration 0-6 mm/s, flow 10-40 L/min\n"
    "- TR-501 (truck): temperature 70-105°C, pressure 2-6 bar, "
    "vibration 0-4 mm/s, flow 5-30 L/h\n"
    "- AGV-601 (agv): temperature 30-60°C, pressure 0-2 bar, "
    "vibration 0-3 mm/s"
)


def format_ranges(items: list[dict]) -> str:
    lines = []
    for e in items:
        t, p, v = e["temperature"], e["pressure"], e["vibration"]
        f = e.get("flow_rate")
        line = (
            f"- {e['equipment_id']} ({e.get('etype', 'generic')}): "
            f"temperature {t['min']}-{t['max']}{t.get('unit', '')}, "
            f"pressure {p['min']}-{p['max']}{p.get('unit', '')}, "
            f"vibration {v['min']}-{v['max']}{v.get('unit', '')}"
        )
        if f:
            line += f", flow {f['min']}-{f['max']}{f.get('unit', '')}"
        lines.append(line)
    return "\n".join(lines)


async def get_ranges_text() -> str:
    now = time.time()
    if _cache["text"] and now - _cache["t"] < _TTL:
        return _cache["text"]
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{SENSOR_URL}/equipment")
            r.raise_for_status()
            text = format_ranges(r.json())
        _cache.update(t=now, text=text)
        return text
    except Exception as e:  # noqa: BLE001 - degrade gracefully
        logger.warning("Equipment ranges fetch failed: %s", e)
        return _cache["text"] or _FALLBACK
