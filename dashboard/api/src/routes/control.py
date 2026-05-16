"""Control passthrough — the frontend only talks to dashboard-api, so we
proxy scenario/reset/prompt calls to sensor-simulator and llm-agent."""
from __future__ import annotations

import os
import re
from typing import Any, Optional
from urllib.parse import quote

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

SENSOR_URL = os.environ.get("SENSOR_URL", "http://sensor-simulator:8001")
AGENT_URL = os.environ.get("AGENT_URL", "http://llm-agent:8002")

router = APIRouter(prefix="/control", tags=["control"])

# Equipment IDs are short alphanumerics (FL-401, TR-501, IT-1). Anything
# else is rejected before it can reach a proxied URL — this is the SSRF
# guard: a strict allowlist + percent-encoding so a crafted id can never
# alter the request path/host of the upstream call.
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _safe_id(eid: str) -> str:
    if not _ID_RE.fullmatch(eid):
        raise HTTPException(status_code=400, detail="Ungültige equipment_id")
    return quote(eid, safe="")


class ScenarioBody(BaseModel):
    scenario: str
    equipment_id: Optional[str] = None


class PromptBody(BaseModel):
    prompt: str


async def _proxy(method: str, url: str, json: Any | None = None) -> Any:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.request(method, url, json=json)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code,
                            detail=e.response.text) from e
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502,
                            detail=f"Upstream nicht erreichbar: {e}") from e


@router.get("/scenarios")
async def list_scenarios():
    return await _proxy("GET", f"{SENSOR_URL}/scenarios/list")


@router.post("/scenario")
async def trigger_scenario(body: ScenarioBody):
    return await _proxy("POST", f"{SENSOR_URL}/scenarios/trigger",
                        json=body.model_dump(exclude_none=True))


@router.post("/reset")
async def reset_plant():
    return await _proxy("POST", f"{SENSOR_URL}/scenarios/reset")


@router.get("/prompt")
async def get_prompt():
    return await _proxy("GET", f"{AGENT_URL}/agent/prompt")


@router.put("/prompt")
async def put_prompt(body: PromptBody):
    return await _proxy("PUT", f"{AGENT_URL}/agent/prompt",
                        json=body.model_dump())


@router.post("/prompt/reset")
async def reset_prompt():
    return await _proxy("POST", f"{AGENT_URL}/agent/prompt/reset")


# --- Equipment CRUD passthrough (-> sensor-simulator) ---

@router.get("/equipment")
async def list_equipment():
    return await _proxy("GET", f"{SENSOR_URL}/equipment")


@router.post("/equipment")
async def add_equipment(payload: dict):
    return await _proxy("POST", f"{SENSOR_URL}/equipment", json=payload)


@router.put("/equipment/{eid}")
async def update_equipment(eid: str, payload: dict):
    safe = _safe_id(eid)
    return await _proxy("PUT", f"{SENSOR_URL}/equipment/{safe}", json=payload)


@router.delete("/equipment/{eid}")
async def delete_equipment(eid: str):
    safe = _safe_id(eid)
    return await _proxy("DELETE", f"{SENSOR_URL}/equipment/{safe}")


@router.post("/equipment/reset")
async def reset_equipment():
    return await _proxy("POST", f"{SENSOR_URL}/equipment/reset")
