from __future__ import annotations

import asyncio
import logging
import math
import time
from collections import deque

import numpy as np

from .equipment import EQUIPMENT, EquipmentConfig, SensorRange
from .models import EquipmentStatus, SensorReading

logger = logging.getLogger(__name__)

MAX_HISTORY = 300  # ~5 min at 1 reading/s

# Per-tick exponential decay of accumulated drift. A stopped scenario (or a
# corrective action) therefore self-heals back toward normal instead of
# staying anomalous forever.
DRIFT_DECAY = 0.92
# Time constant (s) for a shut-down unit cooling toward ambient.
SHUTDOWN_TAU = 12.0
# How fast restart load/cooling factors glide back to nominal (per tick).
RAMP_RATE = 0.06


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


def _status_raw(
    temp: float, pres: float, vib: float, cfg: EquipmentConfig
) -> EquipmentStatus:
    """Threshold logic ignoring shutdown — also used for the latent status."""
    warnings = 0
    criticals = 0
    for rng, val in (
        (cfg.temperature, temp),
        (cfg.pressure, pres),
        (cfg.vibration, vib),
    ):
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


def _determine_status(reading: SensorReading, cfg: EquipmentConfig) -> EquipmentStatus:
    if cfg.is_shutdown:
        return EquipmentStatus.SHUTDOWN
    return _status_raw(reading.temperature, reading.pressure,
                       reading.vibration, cfg)


class Simulator:
    def __init__(self) -> None:
        self.history: dict[str, deque[SensorReading]] = {}
        self.latest: dict[str, SensorReading] = {}
        self._drift: dict[str, dict[str, float]] = {}
        # Last normal-operation temperature, used as the cool-down start
        # point while an equipment is shut down.
        self._last_temp: dict[str, float] = {}
        self._running = False
        for eid in EQUIPMENT:
            self.ensure(eid)

    def ensure(self, equipment_id: str) -> None:
        """Lazily init state for equipment added at runtime."""
        if equipment_id not in self.history:
            self.history[equipment_id] = deque(maxlen=MAX_HISTORY)
        if equipment_id not in self._drift:
            self._drift[equipment_id] = {
                "temperature": 0, "pressure": 0, "vibration": 0, "flow_rate": 0,
            }

    def forget(self, equipment_id: str) -> None:
        """Drop all state for deleted equipment."""
        self.history.pop(equipment_id, None)
        self.latest.pop(equipment_id, None)
        self._drift.pop(equipment_id, None)

    def _decay(self, equipment_id: str) -> None:
        d = self._drift[equipment_id]
        for k in d:
            d[k] *= DRIFT_DECAY
            if abs(d[k]) < 1e-2:
                d[k] = 0.0

    def _raw_values(self, cfg: EquipmentConfig, equipment_id: str):
        drift = self._drift[equipment_id]
        temp = _apply_factors(
            _sample(cfg.temperature, cfg) + drift["temperature"],
            cfg.temperature, cfg, is_temp=True,
        )
        pres = _apply_factors(
            _sample(cfg.pressure, cfg) + drift["pressure"], cfg.pressure, cfg,
        )
        vib = _apply_factors(
            _sample(cfg.vibration, cfg) + drift["vibration"], cfg.vibration, cfg,
        )
        flow = None
        if cfg.flow_rate:
            flow = _apply_factors(
                _sample(cfg.flow_rate, cfg) + drift["flow_rate"],
                cfg.flow_rate, cfg,
            )
        return temp, pres, vib, flow

    def generate_reading(self, equipment_id: str) -> SensorReading:
        cfg = EQUIPMENT[equipment_id]
        self.ensure(equipment_id)
        # Drift always decays — a stopped scenario / corrective action heals.
        self._decay(equipment_id)

        if cfg.is_shutdown:
            elapsed = (
                time.time() - cfg.shutdown_at
                if cfg.shutdown_at is not None else 0.0
            )
            ambient = round(cfg.temperature.min_val * 0.5, 2)
            start = self._last_temp.get(equipment_id, cfg.temperature.max_val)
            # Physically realistic: temperature decays toward ambient.
            disp_temp = round(
                ambient + (start - ambient) * math.exp(-elapsed / SHUTDOWN_TAU),
                2,
            )
            # Latent: what it WOULD read running now (drift keeps decaying).
            lt, lp, lv, _ = self._raw_values(cfg, equipment_id)
            latent = _status_raw(lt, lp, lv, cfg)
            reading = SensorReading(
                equipment_id=equipment_id,
                equipment_name=cfg.name,
                temperature=disp_temp,
                pressure=0.0,
                vibration=0.0,
                flow_rate=0.0 if cfg.flow_rate else None,
                status=EquipmentStatus.SHUTDOWN,
                shutdown_seconds=round(elapsed, 1),
                latent_status=latent,
                safe_to_restart=(
                    latent == EquipmentStatus.NORMAL
                    and disp_temp <= cfg.temperature.max_val
                ),
            )
            self.latest[equipment_id] = reading
            self.history[equipment_id].append(reading)
            return reading

        # Gradually glide a throttled restart back to nominal load.
        if cfg.speed_factor != 1.0:
            cfg.speed_factor += (1.0 - cfg.speed_factor) * RAMP_RATE
            if abs(cfg.speed_factor - 1.0) < 0.01:
                cfg.speed_factor = 1.0
        if cfg.cooling_factor != 1.0:
            cfg.cooling_factor += (1.0 - cfg.cooling_factor) * RAMP_RATE
            if abs(cfg.cooling_factor - 1.0) < 0.01:
                cfg.cooling_factor = 1.0

        ramping = cfg.speed_factor != 1.0 or cfg.cooling_factor != 1.0

        temp, pres, vib, flow = self._raw_values(cfg, equipment_id)
        reading = SensorReading(
            equipment_id=equipment_id,
            equipment_name=cfg.name,
            temperature=temp,
            pressure=pres,
            vibration=vib,
            flow_rate=flow,
            ramping_up=ramping or None,
        )
        reading.status = _determine_status(reading, cfg)

        self._last_temp[equipment_id] = temp
        self.latest[equipment_id] = reading
        self.history[equipment_id].append(reading)
        return reading

    def add_drift(self, equipment_id: str, sensor: str, amount: float) -> None:
        # A stopped machine cannot physically drift.
        cfg = EQUIPMENT.get(equipment_id)
        if cfg is not None and cfg.is_shutdown:
            return
        if equipment_id in self._drift and sensor in self._drift[equipment_id]:
            self._drift[equipment_id][sensor] += amount

    def damp_drift(self, equipment_id: str, sensor: str, factor: float) -> None:
        """Corrective actions actively pull a drift back toward zero."""
        if equipment_id in self._drift and sensor in self._drift[equipment_id]:
            self._drift[equipment_id][sensor] *= factor

    def reset_drift(self, equipment_id: str) -> None:
        self._drift[equipment_id] = {
            "temperature": 0, "pressure": 0, "vibration": 0, "flow_rate": 0,
        }

    async def run(self) -> None:
        self._running = True
        logger.info("Simulator started")
        while self._running:
            for eid in list(EQUIPMENT):
                self.generate_reading(eid)
            await asyncio.sleep(1.0)

    def stop(self) -> None:
        self._running = False


# Global singleton
simulator = Simulator()
