from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    equipment_id: str
    equipment_name: str
    temperature: float
    pressure: float
    vibration: float
    flow_rate: Optional[float] = None
    status: str


class AnalysisRequest(BaseModel):
    sensors: list[SensorData]
    history: Optional[list[dict]] = None
    recent_actions: Optional[list[dict]] = None


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ActionType(str, Enum):
    adjust_setpoint = "adjust_setpoint"
    reduce_speed = "reduce_speed"
    increase_cooling = "increase_cooling"
    shutdown_equipment = "shutdown_equipment"
    alert_operator = "alert_operator"
    no_action = "no_action"


class Anomaly(BaseModel):
    equipment_id: str
    sensor: str
    value: float
    normal_range: str
    severity: Severity


class RecommendedAction(BaseModel):
    equipment_id: str
    action: ActionType
    reason: str
    urgency: Severity
    parameters: dict = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    anomalies: list[Anomaly]
    reasoning: str
    actions: list[RecommendedAction]
    timestamp: datetime
