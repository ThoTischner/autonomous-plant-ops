"""Control passthrough — the frontend only talks to dashboard-api, so we
proxy scenario/reset/prompt calls to sensor-simulator and llm-agent."""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

SENSOR_URL = os.environ.get("SENSOR_URL", "http://sensor-simulator:8001")
AGENT_URL = os.environ.get("AGENT_URL", "http://llm-agent:8002")

router = APIRouter(prefix="/control", tags=["control"])


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
