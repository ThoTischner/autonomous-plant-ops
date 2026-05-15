from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ..equipment import EQUIPMENT
from ..scenarios import SCENARIOS
from ..simulator import simulator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

# Track running scenario tasks so a reset can cancel them — otherwise a
# still-running scenario keeps re-applying drift right after a reset.
_active_tasks: set[asyncio.Task] = set()


class ScenarioRequest(BaseModel):
    scenario: str
    equipment_id: str | None = None


class ScenarioResponse(BaseModel):
    success: bool
    message: str
    available: list[str] | None = None


class ResetResponse(BaseModel):
    success: bool
    message: str
    equipment: list[str]


@router.post("/trigger", response_model=ScenarioResponse)
async def trigger_scenario(req: ScenarioRequest):
    """Trigger a failure scenario."""
    if req.scenario not in SCENARIOS:
        return ScenarioResponse(
            success=False,
            message=f"Unknown scenario: {req.scenario}",
            available=list(SCENARIOS.keys()),
        )

    kwargs = {}
    if req.equipment_id:
        kwargs["equipment_id"] = req.equipment_id

    task = asyncio.create_task(SCENARIOS[req.scenario](**kwargs))
    _active_tasks.add(task)
    task.add_done_callback(_active_tasks.discard)

    return ScenarioResponse(
        success=True,
        message=f"Scenario '{req.scenario}' triggered",
    )


@router.post("/reset", response_model=ResetResponse)
async def reset_all():
    """Cancel running scenarios and restore every equipment to normal."""
    cancelled = 0
    for task in list(_active_tasks):
        task.cancel()
        cancelled += 1
    _active_tasks.clear()

    for eid, cfg in EQUIPMENT.items():
        simulator.reset_drift(eid)
        cfg.reset()

    logger.info("Reset: %d scenario(s) cancelled, %d equipment restored",
                cancelled, len(EQUIPMENT))
    return ResetResponse(
        success=True,
        message=f"{cancelled} Szenario(s) gestoppt, alle Anlagen auf Normalbetrieb zurückgesetzt",
        equipment=list(EQUIPMENT.keys()),
    )


@router.get("/list", response_model=list[str])
async def list_scenarios():
    return list(SCENARIOS.keys())
