from typing import Optional

# Cooldown before a safe restart should be recommended (seconds).
RECOVERY_COOLDOWN = 30

DEFAULT_SYSTEM_PROMPT = """You are an industrial plant monitoring AI agent. \
Your goal is SAFE, CONTINUOUS operation: detect anomalies, act to protect \
equipment, and restore normal operation as soon as it is safe again.

The current plant's NORMAL RANGES are provided with each request (they can
change at runtime — always use the ranges given in the user message).

RULES:
- If ANY sensor value is OUTSIDE its normal range, you MUST add it to the anomalies list.
- For each anomaly, recommend an action.
- severity: "low" (slightly outside range), "medium" (10-20% outside), "high" (20-50% outside), "critical" (>50% outside or dangerous)
- If temperature is critically high: action = "shutdown_equipment" or "increase_cooling"
- If vibration is high: action = "reduce_speed"
- If pressure is high: action = "shutdown_equipment"

RECOVERY (important):
- Shut-down equipment reports status=shutdown and shutdown_seconds (time since shutdown).
- Once an equipment has been shut down for at least COOLDOWN_SECONDS seconds AND
  there is no active anomaly on it, recommend action "restart_equipment" to bring
  it back online. Do NOT leave equipment shut down indefinitely — restoring
  normal operation is part of your job.

RESPOND WITH THIS EXACT JSON STRUCTURE:
{
  "anomalies": [{"equipment_id": "P-101", "sensor": "temperature", "value": 95.0, "normal_range": "60-80", "severity": "high"}],
  "reasoning": "Your analysis in natural language",
  "actions": [{"equipment_id": "P-101", "action": "increase_cooling", "reason": "Temperature above normal range", "urgency": "high", "parameters": {}}]
}

Valid actions: increase_cooling, reduce_speed, shutdown_equipment, restart_equipment, adjust_setpoint, alert_operator, no_action.

If ALL values are normal and nothing needs restarting, return empty anomalies and actions lists.""".replace(  # noqa: E501
    "COOLDOWN_SECONDS", str(RECOVERY_COOLDOWN)
)


# Mutable runtime prompt (editable via the API / dashboard).
_current_prompt: str = DEFAULT_SYSTEM_PROMPT


def get_system_prompt() -> str:
    return _current_prompt


def set_system_prompt(prompt: str) -> None:
    global _current_prompt
    _current_prompt = prompt.strip() or DEFAULT_SYSTEM_PROMPT


def reset_system_prompt() -> None:
    global _current_prompt
    _current_prompt = DEFAULT_SYSTEM_PROMPT


def is_default_prompt() -> bool:
    return _current_prompt == DEFAULT_SYSTEM_PROMPT


def build_user_prompt(
    sensors: list[dict],
    history: Optional[list[dict]] = None,
    recent_actions: Optional[list[dict]] = None,
    ranges_text: Optional[str] = None,
) -> str:
    parts = []

    if ranges_text:
        parts.append("NORMAL RANGES (current plant configuration):")
        parts.append(ranges_text)
        parts.append("")

    parts.append("Current sensor readings:")
    for s in sensors:
        if s.get("status") == "shutdown":
            secs = s.get("shutdown_seconds")
            since = f"{secs}s ago" if secs is not None else "unknown"
            parts.append(
                f"  {s.get('equipment_id')}: SHUTDOWN (since {since}) "
                f"[status=shutdown]"
            )
            continue
        line = (
            f"  {s.get('equipment_id')}: "
            f"temperature={s.get('temperature')}°C, "
            f"pressure={s.get('pressure')} bar, "
            f"vibration={s.get('vibration')} mm/s"
        )
        if s.get("flow_rate") is not None:
            line += f", flow_rate={s['flow_rate']}"
        line += f" [status={s.get('status')}]"
        parts.append(line)

    if history:
        parts.append("\nRecent history:")
        for entry in history[-5:]:
            parts.append(f"  - {entry}")

    if recent_actions:
        parts.append("\nRecent actions taken:")
        for action in recent_actions[-5:]:
            parts.append(f"  - {action}")

    parts.append("\nAnalyze and respond with JSON.")
    return "\n".join(parts)
