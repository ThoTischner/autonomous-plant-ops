import json
import logging
import os
from datetime import datetime, timezone

from ollama import AsyncClient

from .context import RollingContext
from .models import (
    ActionType,
    AnalysisRequest,
    AnalysisResponse,
    Anomaly,
    RecommendedAction,
    Severity,
)
from .prompts import build_user_prompt, get_system_prompt
from .ranges import get_ranges_text

logger = logging.getLogger(__name__)

# Valid action types for normalization
VALID_ACTIONS = {
    "adjust_setpoint", "reduce_speed", "increase_cooling",
    "shutdown_equipment", "restart_equipment", "alert_operator", "no_action",
}
VALID_SEVERITIES = {"low", "medium", "high", "critical"}


def _normalize_anomaly(raw: dict) -> Anomaly:
    """Parse an anomaly dict from LLM output, mapping variant field names."""
    equipment_id = raw.get("equipment_id", "unknown")
    sensor = raw.get("sensor") or raw.get("parameter") or raw.get("metric") or "unknown"
    value = float(raw.get("value", 0))

    # normal_range can come in many formats
    nr = raw.get("normal_range") or raw.get("range") or ""
    if not nr:
        lo = raw.get("threshold_low") or raw.get("min") or raw.get("normal_min")
        hi = raw.get("threshold_high") or raw.get("max") or raw.get("normal_max")
        if lo is not None and hi is not None:
            nr = f"{lo}-{hi}"

    severity = str(raw.get("severity") or raw.get("state") or raw.get("level") or "medium").lower()
    if severity not in VALID_SEVERITIES:
        severity = "high" if severity in ("above", "high", "danger", "alert") else "medium"

    return Anomaly(
        equipment_id=equipment_id,
        sensor=sensor,
        value=value,
        normal_range=str(nr),
        severity=Severity(severity),
    )


def _normalize_action(raw: dict) -> RecommendedAction:
    """Parse an action dict from LLM output, mapping variant field names."""
    equipment_id = raw.get("equipment_id", "unknown")

    action = str(raw.get("action") or raw.get("type") or raw.get("name") or "alert_operator").lower()
    action = action.replace(" ", "_").replace("-", "_")
    if action not in VALID_ACTIONS:
        action = "alert_operator"

    reason = raw.get("reason") or raw.get("description") or raw.get("rationale") or ""
    urgency = str(raw.get("urgency") or raw.get("priority") or raw.get("severity") or "medium").lower()
    if urgency not in VALID_SEVERITIES:
        urgency = "medium"

    parameters = raw.get("parameters") or {}
    if not isinstance(parameters, dict):
        parameters = {}

    return RecommendedAction(
        equipment_id=equipment_id,
        action=ActionType(action),
        reason=reason,
        urgency=Severity(urgency),
        parameters=parameters,
    )


class AnalysisAgent:
    def __init__(
        self,
        ollama_host: str | None = None,
        model: str | None = None,
    ) -> None:
        self.ollama_host = ollama_host or os.environ.get(
            "OLLAMA_HOST", "http://ollama:11434"
        )
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
        self.context = RollingContext()
        self.client = AsyncClient(host=self.ollama_host)

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        sensors_dicts = [s.model_dump() for s in request.sensors]

        history = request.history or self.context.get_history_summary()
        recent_actions = request.recent_actions or self.context.get_recent_actions()

        ranges_text = await get_ranges_text()
        system_prompt = get_system_prompt()
        user_prompt = build_user_prompt(
            sensors_dicts, history, recent_actions, ranges_text=ranges_text
        )

        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format="json",
            )
            content = response["message"]["content"]
            parsed = json.loads(content)

            anomalies = []
            for a in parsed.get("anomalies", []):
                try:
                    anomalies.append(_normalize_anomaly(a))
                except Exception as e:
                    logger.warning("Skipping malformed anomaly %s: %s", a, e)

            actions = []
            for act in parsed.get("actions", []):
                try:
                    actions.append(_normalize_action(act))
                except Exception as e:
                    logger.warning("Skipping malformed action %s: %s", act, e)

            # Hard guard against the shutdown↔shutdown oscillation:
            # a unit already in SHUTDOWN is never an anomaly, and the only
            # action it may receive is restart_equipment (or no_action).
            # This holds even if the LLM ignores the system prompt.
            shutdown_ids = {
                s.get("equipment_id")
                for s in sensors_dicts
                if s.get("status") == "shutdown"
            }
            if shutdown_ids:
                anomalies = [
                    a for a in anomalies if a.equipment_id not in shutdown_ids
                ]
                filtered_actions = []
                for act in actions:
                    if act.equipment_id in shutdown_ids and act.action not in (
                        ActionType("restart_equipment"),
                        ActionType("no_action"),
                    ):
                        logger.info(
                            "Dropping %s on shut-down %s (only "
                            "restart_equipment/no_action allowed)",
                            act.action.value, act.equipment_id,
                        )
                        continue
                    filtered_actions.append(act)
                actions = filtered_actions

            analysis = AnalysisResponse(
                anomalies=anomalies,
                reasoning=parsed.get("reasoning", parsed.get("analysis", "")),
                actions=actions,
                timestamp=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error("LLM analysis failed: %s", e)
            analysis = AnalysisResponse(
                anomalies=[],
                reasoning=f"LLM analysis error: {e}",
                actions=[],
                timestamp=datetime.now(timezone.utc),
            )

        # Update rolling context
        for s in sensors_dicts:
            self.context.add_reading(s)
        for act in analysis.actions:
            self.context.add_action(act.model_dump())

        return analysis
