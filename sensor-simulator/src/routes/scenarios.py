from __future__ import annotations

import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from ..scenarios import SCENARIOS

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


class ScenarioRequest(BaseModel):
    scenario: str
    equipment_id: str | None = None


class ScenarioResponse(BaseModel):
    success: bool
    message: str
    available: list[str] | None = None


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

    asyncio.create_task(SCENARIOS[req.scenario](**kwargs))

    return ScenarioResponse(
        success=True,
        message=f"Scenario '{req.scenario}' triggered",
    )


@router.get("/list", response_model=list[str])
async def list_scenarios():
    return list(SCENARIOS.keys())
