from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    SENSOR_READING = "sensor_reading"
    ANOMALY_DETECTED = "anomaly_detected"
    ACTION_EXECUTED = "action_executed"
    AGENT_ANALYSIS = "agent_analysis"
    SCENARIO_TRIGGERED = "scenario_triggered"


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = Field(default_factory=dict)
    equipment_id: str | None = None
    severity: str | None = None
