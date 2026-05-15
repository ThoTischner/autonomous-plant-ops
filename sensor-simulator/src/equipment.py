from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

EQUIPMENT_FILE = os.environ.get("EQUIPMENT_FILE", "/data/equipment.json")


@dataclass
class SensorRange:
    min_val: float
    max_val: float
    unit: str


@dataclass
class EquipmentConfig:
    equipment_id: str
    name: str
    temperature: SensorRange
    pressure: SensorRange
    vibration: SensorRange
    flow_rate: SensorRange | None = None
    etype: str = "generic"
    # Mutable runtime state (not persisted)
    speed_factor: float = field(default=1.0, repr=False)
    cooling_factor: float = field(default=1.0, repr=False)
    is_shutdown: bool = field(default=False, repr=False)
    shutdown_at: float | None = field(default=None, repr=False)

    def reset(self) -> None:
        self.speed_factor = 1.0
        self.cooling_factor = 1.0
        self.is_shutdown = False
        self.shutdown_at = None


# Live registry — mutated in place so `from .equipment import EQUIPMENT`
# stays valid everywhere.
EQUIPMENT: dict[str, EquipmentConfig] = {}


def _defaults() -> list[dict]:
    return [
        {
            "equipment_id": "P-101", "name": "Pump P-101", "etype": "pump",
            "temperature": {"min": 60, "max": 80, "unit": "°C"},
            "pressure": {"min": 2, "max": 4, "unit": "bar"},
            "vibration": {"min": 0, "max": 5, "unit": "mm/s"},
            "flow_rate": {"min": 100, "max": 150, "unit": "L/min"},
        },
        {
            "equipment_id": "R-201", "name": "Reactor R-201", "etype": "reactor",
            "temperature": {"min": 150, "max": 200, "unit": "°C"},
            "pressure": {"min": 5, "max": 10, "unit": "bar"},
            "vibration": {"min": 0, "max": 3, "unit": "mm/s"},
            "flow_rate": None,
        },
        {
            "equipment_id": "C-301", "name": "Compressor C-301", "etype": "compressor",
            "temperature": {"min": 40, "max": 70, "unit": "°C"},
            "pressure": {"min": 6, "max": 12, "unit": "bar"},
            "vibration": {"min": 0, "max": 8, "unit": "mm/s"},
            "flow_rate": {"min": 200, "max": 300, "unit": "m³/h"},
        },
        {
            "equipment_id": "FL-401", "name": "Gabelstapler FL-401",
            "etype": "forklift",
            "temperature": {"min": 40, "max": 90, "unit": "°C"},
            "pressure": {"min": 5, "max": 15, "unit": "bar"},
            "vibration": {"min": 0, "max": 6, "unit": "mm/s"},
            "flow_rate": {"min": 10, "max": 40, "unit": "L/min"},
        },
        {
            "equipment_id": "TR-501", "name": "LKW TR-501", "etype": "truck",
            "temperature": {"min": 70, "max": 105, "unit": "°C"},
            "pressure": {"min": 2, "max": 6, "unit": "bar"},
            "vibration": {"min": 0, "max": 4, "unit": "mm/s"},
            "flow_rate": {"min": 5, "max": 30, "unit": "L/h"},
        },
        {
            "equipment_id": "AGV-601", "name": "Transportroboter AGV-601",
            "etype": "agv",
            "temperature": {"min": 30, "max": 60, "unit": "°C"},
            "pressure": {"min": 0, "max": 2, "unit": "bar"},
            "vibration": {"min": 0, "max": 3, "unit": "mm/s"},
            "flow_rate": None,
        },
    ]


def _range_from(d: dict | None) -> SensorRange | None:
    if not d:
        return None
    return SensorRange(float(d["min"]), float(d["max"]), str(d.get("unit", "")))


def _range_to(r: SensorRange | None) -> dict | None:
    if r is None:
        return None
    return {"min": r.min_val, "max": r.max_val, "unit": r.unit}


def from_dict(d: dict) -> EquipmentConfig:
    return EquipmentConfig(
        equipment_id=str(d["equipment_id"]),
        name=str(d.get("name") or d["equipment_id"]),
        etype=str(d.get("etype", "generic")),
        temperature=_range_from(d["temperature"]),  # type: ignore[arg-type]
        pressure=_range_from(d["pressure"]),  # type: ignore[arg-type]
        vibration=_range_from(d["vibration"]),  # type: ignore[arg-type]
        flow_rate=_range_from(d.get("flow_rate")),
    )


def to_dict(cfg: EquipmentConfig) -> dict:
    """Definition only (no runtime state)."""
    return {
        "equipment_id": cfg.equipment_id,
        "name": cfg.name,
        "etype": cfg.etype,
        "temperature": _range_to(cfg.temperature),
        "pressure": _range_to(cfg.pressure),
        "vibration": _range_to(cfg.vibration),
        "flow_rate": _range_to(cfg.flow_rate),
    }


def _apply(defs: list[dict]) -> None:
    EQUIPMENT.clear()
    for d in defs:
        cfg = from_dict(d)
        EQUIPMENT[cfg.equipment_id] = cfg


def save() -> None:
    path = Path(EQUIPMENT_FILE)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps([to_dict(c) for c in EQUIPMENT.values()], indent=2),
            encoding="utf-8",
        )
    except OSError as e:  # pragma: no cover - depends on FS
        logger.warning("Could not persist equipment to %s: %s", EQUIPMENT_FILE, e)


def load() -> None:
    path = Path(EQUIPMENT_FILE)
    if path.is_file():
        try:
            _apply(json.loads(path.read_text(encoding="utf-8")))
            logger.info("Loaded %d equipment from %s", len(EQUIPMENT), EQUIPMENT_FILE)
            return
        except (OSError, ValueError, KeyError) as e:
            logger.warning("Invalid equipment file %s (%s) — using defaults",
                           EQUIPMENT_FILE, e)
    _apply(_defaults())
    save()


def reset_to_defaults() -> None:
    _apply(_defaults())
    save()


load()
