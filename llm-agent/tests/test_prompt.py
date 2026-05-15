from src.prompts import reset_system_prompt


async def test_get_prompt_default(client):
    reset_system_prompt()
    r = await client.get("/agent/prompt")
    assert r.status_code == 200
    d = r.json()
    assert d["is_default"] is True
    assert "restart_equipment" in d["prompt"]
    assert "RECOVERY" in d["prompt"]


async def test_put_and_reset_prompt(client):
    r = await client.put("/agent/prompt", json={"prompt": "Mein eigener Prompt"})
    assert r.status_code == 200
    d = r.json()
    assert d["prompt"] == "Mein eigener Prompt"
    assert d["is_default"] is False

    r = await client.post("/agent/prompt/reset")
    d = r.json()
    assert d["is_default"] is True
    assert "industrial plant monitoring" in d["prompt"]


async def test_empty_prompt_falls_back_to_default(client):
    r = await client.put("/agent/prompt", json={"prompt": "   "})
    assert r.json()["is_default"] is True
    reset_system_prompt()
