from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter

from ..equipment import EQUIPMENT
from ..models import ActionRequest, ActionResponse, ActionType
from ..simulator import simulator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/execute", response_model=ActionResponse)
async def execute_action(req: ActionRequest):
    """Execute an action on a piece of equipment."""
    if req.equipment_id not in EQUIPMENT:
        return ActionResponse(
            success=False,
            equipment_id=req.equipment_id,
            action=req.action,
            message=f"Unknown equipment: {req.equipment_id}",
        )

    cfg = EQUIPMENT[req.equipment_id]
    msg = ""

    match req.action:
        case ActionType.SHUTDOWN_EQUIPMENT:
            cfg.is_shutdown = True
            msg = f"{cfg.name} shut down"

        case ActionType.INCREASE_COOLING:
            cfg.cooling_factor = min(cfg.cooling_factor + 0.2, 2.0)
            simulator.add_drift(req.equipment_id, "temperature", -5.0)
            msg = f"{cfg.name} cooling increased (factor={cfg.cooling_factor:.1f})"

        case ActionType.REDUCE_SPEED:
            cfg.speed_factor = max(cfg.speed_factor - 0.15, 0.3)
            simulator.add_drift(req.equipment_id, "vibration", -1.0)
            msg = f"{cfg.name} speed reduced (factor={cfg.speed_factor:.2f})"

        case ActionType.ADJUST_SETPOINT:
            simulator.reset_drift(req.equipment_id)
            cfg.reset()
            msg = f"{cfg.name} setpoints reset to normal"

        case ActionType.ALERT_OPERATOR:
            msg = f"Operator alerted for {cfg.name}: {req.reason}"

        case ActionType.NO_ACTION:
            msg = f"No action taken for {cfg.name}"

    logger.info("Action executed: %s on %s — %s", req.action.value, req.equipment_id, msg)

    return ActionResponse(
        success=True,
        equipment_id=req.equipment_id,
        action=req.action,
        message=msg,
    )
