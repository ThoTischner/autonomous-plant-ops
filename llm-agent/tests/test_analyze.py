import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest



async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "llm-agent"



async def test_analyze_returns_analysis_response(client):
    mock_llm_response = {
        "message": {
            "content": json.dumps({
                "anomalies": [
                    {
                        "equipment_id": "R-201",
                        "sensor": "temperature",
                        "value": 215.0,
                        "normal_range": "150-200°C",
                        "severity": "high",
                    }
                ],
                "reasoning": "Reactor temperature is elevated above normal range",
                "actions": [
                    {
                        "equipment_id": "R-201",
                        "action": "increase_cooling",
                        "reason": "Temperature exceeds safe operating range",
                        "urgency": "high",
                        "parameters": {},
                    }
                ],
            })
        }
    }

    with patch("src.agent.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.chat = AsyncMock(return_value=mock_llm_response)
        mock_client_cls.return_value = mock_instance

        # Re-import to pick up the mock
        from src.routes.analyze import agent
        agent.client = mock_instance

        resp = await client.post("/agent/analyze", json={
            "sensors": [
                {
                    "equipment_id": "R-201",
                    "equipment_name": "Reactor R-201",
                    "temperature": 215.0,
                    "pressure": 8.5,
                    "vibration": 2.0,
                    "status": "warning",
                }
            ],
        })

    assert resp.status_code == 200
    body = resp.json()
    assert "anomalies" in body
    assert "reasoning" in body
    assert "actions" in body
    assert "timestamp" in body
    assert len(body["anomalies"]) == 1
    assert body["anomalies"][0]["equipment_id"] == "R-201"
    assert body["anomalies"][0]["severity"] == "high"
    assert len(body["actions"]) == 1
    assert body["actions"][0]["action"] == "increase_cooling"



async def test_analyze_handles_llm_failure(client):
    with patch("src.agent.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.chat = AsyncMock(side_effect=Exception("Ollama unreachable"))
        mock_client_cls.return_value = mock_instance

        from src.routes.analyze import agent
        agent.client = mock_instance

        resp = await client.post("/agent/analyze", json={
            "sensors": [
                {
                    "equipment_id": "P-101",
                    "equipment_name": "Pump P-101",
                    "temperature": 72.0,
                    "pressure": 3.0,
                    "vibration": 2.0,
                    "status": "normal",
                }
            ],
        })

    assert resp.status_code == 200
    body = resp.json()
    assert body["anomalies"] == []
    assert body["actions"] == []
    assert "Failed" in body["reasoning"] or "failed" in body["reasoning"].lower()



async def test_analyze_with_multiple_sensors(client):
    mock_llm_response = {
        "message": {
            "content": json.dumps({
                "anomalies": [],
                "reasoning": "All systems operating within normal parameters",
                "actions": [],
            })
        }
    }

    with patch("src.agent.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.chat = AsyncMock(return_value=mock_llm_response)
        mock_client_cls.return_value = mock_instance

        from src.routes.analyze import agent
        agent.client = mock_instance

        resp = await client.post("/agent/analyze", json={
            "sensors": [
                {
                    "equipment_id": "P-101",
                    "equipment_name": "Pump P-101",
                    "temperature": 72.0,
                    "pressure": 3.0,
                    "vibration": 2.0,
                    "flow_rate": 125.0,
                    "status": "normal",
                },
                {
                    "equipment_id": "R-201",
                    "equipment_name": "Reactor R-201",
                    "temperature": 175.0,
                    "pressure": 7.5,
                    "vibration": 1.5,
                    "status": "normal",
                },
                {
                    "equipment_id": "C-301",
                    "equipment_name": "Compressor C-301",
                    "temperature": 55.0,
                    "pressure": 9.0,
                    "vibration": 4.0,
                    "flow_rate": 250.0,
                    "status": "normal",
                },
            ],
        })

    assert resp.status_code == 200
    body = resp.json()
    assert body["anomalies"] == []
    assert body["actions"] == []



async def test_analyze_with_history_and_actions(client):
    mock_llm_response = {
        "message": {
            "content": json.dumps({
                "anomalies": [],
                "reasoning": "Situation improving after recent cooling increase",
                "actions": [
                    {
                        "equipment_id": "R-201",
                        "action": "no_action",
                        "reason": "Monitoring — situation stabilizing",
                        "urgency": "low",
                        "parameters": {},
                    }
                ],
            })
        }
    }

    with patch("src.agent.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.chat = AsyncMock(return_value=mock_llm_response)
        mock_client_cls.return_value = mock_instance

        from src.routes.analyze import agent
        agent.client = mock_instance

        resp = await client.post("/agent/analyze", json={
            "sensors": [
                {
                    "equipment_id": "R-201",
                    "equipment_name": "Reactor R-201",
                    "temperature": 190.0,
                    "pressure": 8.0,
                    "vibration": 2.0,
                    "status": "normal",
                }
            ],
            "history": [
                {"equipment_id": "R-201", "temperature": 205.0},
            ],
            "recent_actions": [
                {"action": "increase_cooling", "equipment_id": "R-201"},
            ],
        })

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["actions"]) == 1
    assert body["actions"][0]["action"] == "no_action"
