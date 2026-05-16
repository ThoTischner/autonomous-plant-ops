from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from ..equipment import EQUIPMENT
from ..logsafe import clean
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
            if cfg.is_shutdown:
                # Idempotent: re-shutting-down an already-stopped unit must
                # NOT reset shutdown_at — doing so restarts the cool-down
                # clock and re-spikes the displayed temperature, trapping
                # recovery in a shutdown↔shutdown oscillation.
                elapsed = (
                    time.time() - cfg.shutdown_at
                    if cfg.shutdown_at is not None else 0.0
                )
                msg = (
                    f"{cfg.name} ist bereits seit {elapsed:.0f}s "
                    f"abgeschaltet — keine erneute Abschaltung nötig"
                )
            else:
                cfg.is_shutdown = True
                cfg.shutdown_at = time.time()
                msg = f"{cfg.name} shut down"

        case ActionType.RESTART_EQUIPMENT:
            # Throttled restart: back online but at reduced load with extra
            # cooling; the simulator ramps these back to nominal over time.
            cfg.reset()
            simulator.reset_drift(req.equipment_id)
            cfg.is_shutdown = False
            cfg.shutdown_at = None
            cfg.speed_factor = 0.5
            cfg.cooling_factor = 1.6
            msg = f"{cfg.name} wird gedrosselt wieder hochgefahren"

        case ActionType.INCREASE_COOLING:
            cfg.cooling_factor = min(cfg.cooling_factor + 0.2, 2.0)
            # Actively pull the temperature excursion back down.
            simulator.damp_drift(req.equipment_id, "temperature", 0.45)
            msg = f"{cfg.name} cooling increased (factor={cfg.cooling_factor:.1f})"

        case ActionType.REDUCE_SPEED:
            cfg.speed_factor = max(cfg.speed_factor - 0.15, 0.3)
            simulator.damp_drift(req.equipment_id, "vibration", 0.45)
            msg = f"{cfg.name} speed reduced (factor={cfg.speed_factor:.2f})"

        case ActionType.ADJUST_SETPOINT:
            simulator.reset_drift(req.equipment_id)
            cfg.reset()
            msg = f"{cfg.name} setpoints reset to normal"

        case ActionType.ALERT_OPERATOR:
            msg = f"Operator alerted for {cfg.name}: {req.reason}"

        case ActionType.NO_ACTION:
            msg = f"No action taken for {cfg.name}"

    logger.info("Action executed: %s on %s — %s",
                clean(req.action.value), clean(req.equipment_id), clean(msg))

    return ActionResponse(
        success=True,
        equipment_id=req.equipment_id,
        action=req.action,
        message=msg,
    )
