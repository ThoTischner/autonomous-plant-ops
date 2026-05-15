from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .. import equipment as eq
from ..equipment import EQUIPMENT, from_dict, to_dict
from ..models import EquipmentDef
from ..simulator import simulator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/equipment", tags=["equipment"])


def _sync_simulator() -> None:
    for eid in list(simulator.history):
        if eid not in EQUIPMENT:
            simulator.forget(eid)
    for eid in EQUIPMENT:
        simulator.ensure(eid)


@router.get("")
async def list_equipment():
    return [to_dict(c) for c in EQUIPMENT.values()]


@router.post("", status_code=201)
async def add_equipment(body: EquipmentDef):
    if body.equipment_id in EQUIPMENT:
        raise HTTPException(409, f"Equipment '{body.equipment_id}' existiert bereits")
    EQUIPMENT[body.equipment_id] = from_dict(body.model_dump())
    simulator.ensure(body.equipment_id)
    eq.save()
    logger.info("Equipment added: %s", body.equipment_id)
    return to_dict(EQUIPMENT[body.equipment_id])


@router.put("/{eid}")
async def update_equipment(eid: str, body: EquipmentDef):
    old = EQUIPMENT.get(eid)
    if old is None:
        raise HTTPException(404, f"Unbekanntes Equipment: {eid}")
    cfg = from_dict(body.model_dump())
    # Preserve runtime state across a definition edit.
    cfg.speed_factor = old.speed_factor
    cfg.cooling_factor = old.cooling_factor
    cfg.is_shutdown = old.is_shutdown
    cfg.shutdown_at = old.shutdown_at
    EQUIPMENT.pop(eid, None)
    if eid != cfg.equipment_id:
        simulator.forget(eid)
    EQUIPMENT[cfg.equipment_id] = cfg
    simulator.ensure(cfg.equipment_id)
    eq.save()
    logger.info("Equipment updated: %s", eid)
    return to_dict(cfg)


@router.delete("/{eid}")
async def delete_equipment(eid: str):
    if eid not in EQUIPMENT:
        raise HTTPException(404, f"Unbekanntes Equipment: {eid}")
    if len(EQUIPMENT) <= 1:
        raise HTTPException(400, "Mindestens ein Equipment muss bestehen bleiben")
    EQUIPMENT.pop(eid, None)
    simulator.forget(eid)
    eq.save()
    logger.info("Equipment deleted: %s", eid)
    return {"success": True, "deleted": eid}


@router.post("/reset")
async def reset_equipment():
    eq.reset_to_defaults()
    _sync_simulator()
    return [to_dict(c) for c in EQUIPMENT.values()]
