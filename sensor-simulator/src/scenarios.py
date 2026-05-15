from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine

from .simulator import simulator

logger = logging.getLogger(__name__)


async def _thermal_runaway(equipment_id: str = "TR-501") -> None:
    """Truck engine overheating — temperature ramps up dangerously."""
    logger.info("Scenario: thermal_runaway on %s", equipment_id)
    for _ in range(25):
        simulator.add_drift(equipment_id, "temperature", 4.0)
        simulator.add_drift(equipment_id, "pressure", 0.2)
        await asyncio.sleep(1)


async def _bearing_degradation(equipment_id: str = "FL-401") -> None:
    """Forklift bearing wear — vibration increases gradually."""
    logger.info("Scenario: bearing_degradation on %s", equipment_id)
    for _ in range(30):
        simulator.add_drift(equipment_id, "vibration", 0.7)
        simulator.add_drift(equipment_id, "temperature", 0.6)
        await asyncio.sleep(1)


async def _compressor_surge(equipment_id: str = "AGV-601") -> None:
    """AGV drivetrain instability — pressure oscillates, vibration rises."""
    logger.info("Scenario: compressor_surge on %s", equipment_id)
    for i in range(20):
        sign = 1 if i % 2 == 0 else -1
        simulator.add_drift(equipment_id, "pressure", sign * 1.0)
        simulator.add_drift(equipment_id, "vibration", 0.4)
        await asyncio.sleep(1)


async def _pressure_spike(equipment_id: str = "FL-402") -> None:
    """Forklift hydraulic pressure spike."""
    logger.info("Scenario: pressure_spike on %s", equipment_id)
    for _ in range(15):
        simulator.add_drift(equipment_id, "pressure", 1.6)
        await asyncio.sleep(1)


SCENARIOS: dict[str, Callable[..., Coroutine]] = {
    "thermal_runaway": _thermal_runaway,
    "bearing_degradation": _bearing_degradation,
    "compressor_surge": _compressor_surge,
    "pressure_spike": _pressure_spike,
}
