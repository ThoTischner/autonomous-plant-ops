from __future__ import annotations

from fastapi import APIRouter, Query

from ..models import SensorReading
from ..simulator import simulator

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/latest", response_model=list[SensorReading])
async def get_latest():
    """Return latest reading for every equipment."""
    return list(simulator.latest.values())


@router.get("/latest/{equipment_id}", response_model=SensorReading)
async def get_latest_equipment(equipment_id: str):
    """Return latest reading for a specific equipment."""
    if equipment_id not in simulator.latest:
        return {"error": f"Unknown equipment: {equipment_id}"}
    return simulator.latest[equipment_id]


@router.get("/history/{equipment_id}", response_model=list[SensorReading])
async def get_history(
    equipment_id: str,
    limit: int = Query(60, ge=1, le=300),
):
    """Return recent readings for a specific equipment."""
    if equipment_id not in simulator.history:
        return []
    history = list(simulator.history[equipment_id])
    return history[-limit:]
