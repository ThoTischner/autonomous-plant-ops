from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine

from .equipment import EQUIPMENT
from .simulator import simulator

logger = logging.getLogger(__name__)


async def _thermal_runaway(equipment_id: str = "R-201") -> None:
    """Reactor temperature ramps up dangerously over 30 seconds."""
    logger.info("Scenario: thermal_runaway on %s", equipment_id)
    for i in range(30):
        simulator.add_drift(equipment_id, "temperature", 3.0)
        simulator.add_drift(equipment_id, "pressure", 0.3)
        await asyncio.sleep(1)


async def _bearing_degradation(equipment_id: str = "P-101") -> None:
    """Pump vibration increases gradually — bearing wear."""
    logger.info("Scenario: bearing_degradation on %s", equipment_id)
    for i in range(40):
        simulator.add_drift(equipment_id, "vibration", 0.25)
        simulator.add_drift(equipment_id, "temperature", 0.5)
        await asyncio.sleep(1)


async def _compressor_surge(equipment_id: str = "C-301") -> None:
    """Compressor pressure oscillates, flow drops."""
    logger.info("Scenario: compressor_surge on %s", equipment_id)
    for i in range(25):
        sign = 1 if i % 2 == 0 else -1
        simulator.add_drift(equipment_id, "pressure", sign * 1.5)
        simulator.add_drift(equipment_id, "flow_rate", -5.0)
        simulator.add_drift(equipment_id, "vibration", 0.4)
        await asyncio.sleep(1)


async def _pressure_spike(equipment_id: str = "R-201") -> None:
    """Sudden pressure increase in reactor."""
    logger.info("Scenario: pressure_spike on %s", equipment_id)
    for i in range(15):
        simulator.add_drift(equipment_id, "pressure", 1.0)
        await asyncio.sleep(1)


SCENARIOS: dict[str, Callable[..., Coroutine]] = {
    "thermal_runaway": _thermal_runaway,
    "bearing_degradation": _bearing_degradation,
    "compressor_surge": _compressor_surge,
    "pressure_spike": _pressure_spike,
}
