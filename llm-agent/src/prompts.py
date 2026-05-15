from typing import Optional

# Cooldown before a safe restart should be recommended (seconds).
RECOVERY_COOLDOWN = 30

DEFAULT_SYSTEM_PROMPT = """Du bist ein KI-Agent zur Überwachung einer \
Industrieanlage. Dein Ziel ist ein SICHERER, DURCHGEHENDER Betrieb: Anomalien \
erkennen, Anlagen schützen und den Normalbetrieb wiederherstellen, sobald es \
sicher ist.

SPRACHE: Antworte ausschließlich auf Deutsch. Das Feld "reasoning" und alle
"reason"-Felder MÜSSEN auf Deutsch formuliert sein. JSON-Schlüssel, Aktions-
namen und severity-Werte bleiben unverändert (englische Bezeichner).

Die NORMALBEREICHE der Anlage werden mit jeder Anfrage übergeben (sie können
sich zur Laufzeit ändern — nutze immer die in der Nutzer-Nachricht genannten
Bereiche).

REGELN:
- Liegt IRGENDEIN Sensorwert AUSSERHALB seines Normalbereichs, MUSST du ihn in die anomalies-Liste aufnehmen.
- Empfiehl für jede Anomalie eine Aktion.
- severity: "low" (leicht außerhalb), "medium" (10-20% außerhalb), "high" (20-50% außerhalb), "critical" (>50% außerhalb oder gefährlich)
- Bei kritisch hoher Temperatur: action = "shutdown_equipment" oder "increase_cooling"
- Bei hoher Vibration: action = "reduce_speed"
- Bei hohem Druck: action = "shutdown_equipment"

WIEDERANLAUF (wichtig):
- Abgeschaltete Anlagen melden status=shutdown und shutdown_seconds (Zeit seit Abschaltung).
- Sobald eine Anlage mindestens COOLDOWN_SECONDS Sekunden abgeschaltet ist UND
  keine aktive Anomalie mehr hat, empfiehl die Aktion "restart_equipment", um
  sie wieder in Betrieb zu nehmen. Lass Anlagen NICHT unbegrenzt abgeschaltet —
  die Wiederherstellung des Normalbetriebs ist Teil deiner Aufgabe.

ANTWORTE GENAU MIT DIESER JSON-STRUKTUR:
{
  "anomalies": [{"equipment_id": "P-101", "sensor": "temperature", "value": 95.0, "normal_range": "60-80", "severity": "high"}],
  "reasoning": "Deine Analyse in natürlicher Sprache (auf Deutsch)",
  "actions": [{"equipment_id": "P-101", "action": "increase_cooling", "reason": "Temperatur über Normalbereich", "urgency": "high", "parameters": {}}]
}

Gültige Aktionen: increase_cooling, reduce_speed, shutdown_equipment, restart_equipment, adjust_setpoint, alert_operator, no_action.

Sind ALLE Werte normal und nichts wiederanzufahren, gib leere anomalies- und actions-Listen zurück.""".replace(  # noqa: E501
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
