from typing import Optional


def get_system_prompt() -> str:
    return """You are an industrial plant monitoring AI agent. Analyze sensor data and detect anomalies.

NORMAL RANGES:
- P-101 (Pump): temperature 60-80°C, pressure 2-4 bar, vibration 0-5 mm/s, flow 100-150 L/min
- R-201 (Reactor): temperature 150-200°C, pressure 5-10 bar, vibration 0-3 mm/s
- C-301 (Compressor): temperature 40-70°C, pressure 6-12 bar, vibration 0-8 mm/s, flow 200-300 m³/h

RULES:
- If ANY sensor value is OUTSIDE its normal range, you MUST add it to the anomalies list.
- For each anomaly, recommend an action.
- severity: "low" (slightly outside range), "medium" (10-20% outside), "high" (20-50% outside), "critical" (>50% outside or dangerous)
- If temperature is critically high: action = "shutdown_equipment" or "increase_cooling"
- If vibration is high: action = "reduce_speed"
- If pressure is high: action = "shutdown_equipment"

RESPOND WITH THIS EXACT JSON STRUCTURE:
{
  "anomalies": [{"equipment_id": "P-101", "sensor": "temperature", "value": 95.0, "normal_range": "60-80", "severity": "high"}],
  "reasoning": "Your analysis in natural language",
  "actions": [{"equipment_id": "P-101", "action": "increase_cooling", "reason": "Temperature above normal range", "urgency": "high", "parameters": {}}]
}

If ALL values are normal, return empty anomalies and actions lists."""


def build_user_prompt(
    sensors: list[dict],
    history: Optional[list[dict]] = None,
    recent_actions: Optional[list[dict]] = None,
) -> str:
    parts = []

    parts.append("Current sensor readings:")
    for s in sensors:
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
