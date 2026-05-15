import httpx
import pytest


class _Resp:
    def __init__(self, data):
        self._d = data
        self.status_code = 200
        self.text = ""

    def json(self):
        return self._d

    def raise_for_status(self):
        return None


class _Client:
    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def request(self, method, url, json=None):
        return _Resp({"ok": True, "method": method, "url": url, "sent": json})


@pytest.fixture(autouse=True)
def _fake_httpx(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", _Client)


async def test_list_scenarios_proxied(client):
    r = await client.get("/control/scenarios")
    assert r.status_code == 200
    assert r.json()["url"].endswith("/scenarios/list")


async def test_trigger_scenario_proxied(client):
    r = await client.post("/control/scenario", json={"scenario": "thermal_runaway"})
    assert r.status_code == 200
    body = r.json()
    assert body["method"] == "POST"
    assert body["url"].endswith("/scenarios/trigger")
    assert body["sent"] == {"scenario": "thermal_runaway"}


async def test_reset_proxied(client):
    r = await client.post("/control/reset")
    assert r.json()["url"].endswith("/scenarios/reset")


async def test_prompt_get_put_reset_proxied(client):
    assert (await client.get("/control/prompt")).json()["url"].endswith("/agent/prompt")
    r = await client.put("/control/prompt", json={"prompt": "x"})
    assert r.json()["sent"] == {"prompt": "x"}
    assert (await client.post("/control/prompt/reset")).json()["url"].endswith(
        "/agent/prompt/reset"
    )
