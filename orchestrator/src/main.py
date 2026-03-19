"""
Autonomous Plant Ops — Orchestrator

Replaces n8n with a simple Python loop:
1. Fetch sensor data
2. Push sensor readings to dashboard
3. Call LLM agent for analysis
4. Execute recommended actions
5. Push analysis + actions to dashboard
6. Randomly trigger failure scenarios for demo

Runs every CYCLE_INTERVAL seconds.
"""

import asyncio
import logging
import os
import random
import time

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("orchestrator")

SENSOR_URL = os.environ.get("SENSOR_URL", "http://sensor-simulator:8001")
AGENT_URL = os.environ.get("AGENT_URL", "http://llm-agent:8002")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://dashboard-api:8003")
CYCLE_INTERVAL = int(os.environ.get("CYCLE_INTERVAL", "12"))
SCENARIO_CHANCE = float(os.environ.get("SCENARIO_CHANCE", "0.08"))

SCENARIOS = ["thermal_runaway", "bearing_degradation", "compressor_surge", "pressure_spike"]


async def wait_for_services(client: httpx.AsyncClient) -> None:
    """Wait until all services are healthy."""
    services = {
        "sensor-simulator": f"{SENSOR_URL}/health",
        "llm-agent": f"{AGENT_URL}/health",
        "dashboard-api": f"{DASHBOARD_URL}/health",
    }
    for name, url in services.items():
        for attempt in range(60):
            try:
                r = await client.get(url, timeout=5)
                if r.status_code == 200:
                    log.info("  %s ready", name)
                    break
            except Exception:
                pass
            await asyncio.sleep(2)
        else:
            log.warning("  %s not ready after 120s, continuing anyway", name)


async def push_event(client: httpx.AsyncClient, event_type: str, data: dict, **kwargs) -> None:
    """Push an event to the dashboard API."""
    payload = {"event_type": event_type, "data": data, **kwargs}
    try:
        await client.post(f"{DASHBOARD_URL}/events", json=payload, timeout=5)
    except Exception as e:
        log.warning("Failed to push %s event: %s", event_type, e)


async def maybe_trigger_scenario(client: httpx.AsyncClient) -> None:
    """Randomly trigger a failure scenario."""
    if random.random() < SCENARIO_CHANCE:
        scenario = random.choice(SCENARIOS)
        log.info("TRIGGERING SCENARIO: %s", scenario)
        try:
            r = await client.post(
                f"{SENSOR_URL}/scenarios/trigger",
                json={"scenario": scenario},
                timeout=10,
            )
            if r.status_code == 200:
                await push_event(client, "scenario_triggered", {
                    "scenario": scenario,
                    "message": f"Scenario '{scenario}' triggered",
                })
        except Exception as e:
            log.warning("Failed to trigger scenario: %s", e)


async def run_cycle(client: httpx.AsyncClient, cycle: int) -> None:
    """Run one monitoring cycle."""
    t0 = time.time()

    # 1. Fetch sensor data
    try:
        r = await client.get(f"{SENSOR_URL}/sensors/latest", timeout=10)
        sensors = r.json()
    except Exception as e:
        log.error("Failed to fetch sensors: %s", e)
        return

    # 2. Push sensor readings to dashboard
    for s in sensors:
        severity = None
        if s.get("status") == "critical":
            severity = "critical"
        elif s.get("status") == "warning":
            severity = "warning"
        await push_event(client, "sensor_reading", s,
                         equipment_id=s.get("equipment_id"), severity=severity)

    # 3. Call LLM agent
    try:
        r = await client.post(
            f"{AGENT_URL}/agent/analyze",
            json={"sensors": sensors},
            timeout=120,
        )
        analysis = r.json()
    except Exception as e:
        log.error("Agent call failed: %s", e)
        analysis = {
            "anomalies": [], "reasoning": f"Agent unavailable: {e}",
            "actions": [], "timestamp": None,
        }

    # 4. Push analysis to dashboard
    anomaly_severity = None
    if analysis.get("anomalies"):
        anomaly_severity = "critical" if any(
            a.get("severity") == "critical" for a in analysis["anomalies"]
        ) else "warning"
    await push_event(client, "agent_analysis", analysis, severity=anomaly_severity)

    # 5. Execute actions
    for action in analysis.get("actions", []):
        try:
            r = await client.post(
                f"{SENSOR_URL}/actions/execute",
                json={
                    "equipment_id": action.get("equipment_id", "unknown"),
                    "action": action.get("action", "no_action"),
                    "parameters": action.get("parameters", {}),
                    "reason": action.get("reason", ""),
                },
                timeout=10,
            )
            result = r.json()
            log.info("  ACTION: %s on %s -> %s",
                     action.get("action"), action.get("equipment_id"), result.get("message"))
            await push_event(client, "action_executed", result,
                             equipment_id=result.get("equipment_id"),
                             severity="critical" if action.get("action") == "shutdown_equipment" else "warning")
        except Exception as e:
            log.warning("  Failed to execute action: %s", e)

    dt = time.time() - t0
    n_anomalies = len(analysis.get("anomalies", []))
    n_actions = len(analysis.get("actions", []))
    log.info("Cycle %d done in %.1fs — %d anomalies, %d actions",
             cycle, dt, n_anomalies, n_actions)
    if analysis.get("reasoning"):
        log.info("  AI: %s", analysis["reasoning"][:120])


async def main() -> None:
    log.info("=" * 50)
    log.info("  Autonomous Plant Ops — Orchestrator")
    log.info("=" * 50)
    log.info("Cycle interval: %ds", CYCLE_INTERVAL)
    log.info("Scenario chance: %.0f%% per cycle", SCENARIO_CHANCE * 100)
    log.info("")

    async with httpx.AsyncClient() as client:
        log.info("Waiting for services...")
        await wait_for_services(client)
        log.info("All services ready. Starting monitoring loop.")
        log.info("")

        cycle = 0
        while True:
            cycle += 1
            await maybe_trigger_scenario(client)
            await run_cycle(client, cycle)
            await asyncio.sleep(CYCLE_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
