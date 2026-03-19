from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime

import numpy as np

from .equipment import EQUIPMENT, EquipmentConfig, SensorRange
from .models import EquipmentStatus, SensorReading

logger = logging.getLogger(__name__)

MAX_HISTORY = 300  # ~5 min at 1 reading/s


def _sample(rng: SensorRange, cfg: EquipmentConfig) -> float:
    mid = (rng.min_val + rng.max_val) / 2
    spread = (rng.max_val - rng.min_val) / 2
    noise = np.random.normal(0, spread * 0.08)
    value = mid + noise
    return round(float(value), 2)


def _apply_factors(value: float, rng: SensorRange, cfg: EquipmentConfig, is_temp: bool = False) -> float:
    if is_temp:
        value *= (2.0 - cfg.cooling_factor)
    value *= cfg.speed_factor
    return round(value, 2)


def _determine_status(reading: SensorReading, cfg: EquipmentConfig) -> EquipmentStatus:
    if cfg.is_shutdown:
        return EquipmentStatus.SHUTDOWN

    warnings = 0
    criticals = 0

    for sensor_name in ("temperature", "pressure", "vibration"):
        rng: SensorRange = getattr(cfg, sensor_name)
        val = getattr(reading, sensor_name)
        margin = (rng.max_val - rng.min_val) * 0.15

        if val > rng.max_val + margin or val < rng.min_val - margin:
            criticals += 1
        elif val > rng.max_val or val < rng.min_val:
            warnings += 1

    if criticals > 0:
        return EquipmentStatus.CRITICAL
    if warnings > 0:
        return EquipmentStatus.WARNING
    return EquipmentStatus.NORMAL


class Simulator:
    def __init__(self) -> None:
        self.history: dict[str, deque[SensorReading]] = {
            eid: deque(maxlen=MAX_HISTORY) for eid in EQUIPMENT
        }
        self.latest: dict[str, SensorReading] = {}
        self._drift: dict[str, dict[str, float]] = {
            eid: {"temperature": 0, "pressure": 0, "vibration": 0, "flow_rate": 0}
            for eid in EQUIPMENT
        }
        self._running = False

    def generate_reading(self, equipment_id: str) -> SensorReading:
        cfg = EQUIPMENT[equipment_id]

        if cfg.is_shutdown:
            reading = SensorReading(
                equipment_id=equipment_id,
                equipment_name=cfg.name,
                temperature=round(cfg.temperature.min_val * 0.5, 2),
                pressure=0.0,
                vibration=0.0,
                flow_rate=0.0 if cfg.flow_rate else None,
                status=EquipmentStatus.SHUTDOWN,
            )
            self.latest[equipment_id] = reading
            self.history[equipment_id].append(reading)
            return reading

        drift = self._drift[equipment_id]

        temp = _apply_factors(
            _sample(cfg.temperature, cfg) + drift["temperature"],
            cfg.temperature, cfg, is_temp=True,
        )
        pres = _apply_factors(
            _sample(cfg.pressure, cfg) + drift["pressure"],
            cfg.pressure, cfg,
        )
        vib = _apply_factors(
            _sample(cfg.vibration, cfg) + drift["vibration"],
            cfg.vibration, cfg,
        )
        flow = None
        if cfg.flow_rate:
            flow = _apply_factors(
                _sample(cfg.flow_rate, cfg) + drift["flow_rate"],
                cfg.flow_rate, cfg,
            )

        reading = SensorReading(
            equipment_id=equipment_id,
            equipment_name=cfg.name,
            temperature=temp,
            pressure=pres,
            vibration=vib,
            flow_rate=flow,
        )
        reading.status = _determine_status(reading, cfg)

        self.latest[equipment_id] = reading
        self.history[equipment_id].append(reading)
        return reading

    def add_drift(self, equipment_id: str, sensor: str, amount: float) -> None:
        if equipment_id in self._drift and sensor in self._drift[equipment_id]:
            self._drift[equipment_id][sensor] += amount

    def reset_drift(self, equipment_id: str) -> None:
        self._drift[equipment_id] = {
            "temperature": 0, "pressure": 0, "vibration": 0, "flow_rate": 0,
        }

    async def run(self) -> None:
        self._running = True
        logger.info("Simulator started")
        while self._running:
            for eid in EQUIPMENT:
                self.generate_reading(eid)
            await asyncio.sleep(1.0)

    def stop(self) -> None:
        self._running = False


# Global singleton
simulator = Simulator()
