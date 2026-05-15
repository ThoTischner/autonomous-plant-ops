from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RangeModel(BaseModel):
    min: float
    max: float
    unit: str = ""


class EquipmentDef(BaseModel):
    equipment_id: str
    name: str
    etype: str = "generic"
    temperature: RangeModel
    pressure: RangeModel
    vibration: RangeModel
    flow_rate: Optional[RangeModel] = None


class EquipmentStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    SHUTDOWN = "shutdown"


class SensorReading(BaseModel):
    equipment_id: str
    equipment_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temperature: float
    pressure: float
    vibration: float
    flow_rate: Optional[float] = None
    status: EquipmentStatus = EquipmentStatus.NORMAL
    # Seconds since the equipment was shut down (None if running). Lets the
    # agent decide when a safe restart is appropriate.
    shutdown_seconds: Optional[float] = None
    # While shut down: what the status WOULD be on restart (latent), and
    # whether it is safe to restart now (latent values all uncritical).
    latent_status: Optional[EquipmentStatus] = None
    safe_to_restart: Optional[bool] = None


class ActionType(str, Enum):
    ADJUST_SETPOINT = "adjust_setpoint"
    REDUCE_SPEED = "reduce_speed"
    INCREASE_COOLING = "increase_cooling"
    SHUTDOWN_EQUIPMENT = "shutdown_equipment"
    RESTART_EQUIPMENT = "restart_equipment"
    ALERT_OPERATOR = "alert_operator"
    NO_ACTION = "no_action"


class ActionRequest(BaseModel):
    equipment_id: str
    action: ActionType
    parameters: dict = Field(default_factory=dict)
    reason: str = ""


class ActionResponse(BaseModel):
    success: bool
    equipment_id: str
    action: ActionType
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
