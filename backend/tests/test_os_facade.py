"""OS console facade contract tests."""

from httpx import AsyncClient


async def test_os_overview_contract(client: AsyncClient, auth_headers: dict[str, str]):
    resp = await client.get("/v1/os/overview", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["workspace"]["name"] == "MX AgentOS"
    assert body["workspace"]["status"] in {"active", "inactive"}
    assert {item["href"] for item in body["navigation"]} >= {
        "/",
        "/chat",
        "/sessions",
        "/traces",
        "/memory",
        "/knowledge",
        "/metrics",
        "/evaluation",
        "/approvals",
        "/scheduler",
    }


async def test_os_entities_contract(client: AsyncClient, auth_headers: dict[str, str]):
    resp = await client.get("/v1/os/entities", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["agents"]) >= 3
    assert len(body["teams"]) >= 2
    assert len(body["workflows"]) >= 2
    assert body["agents"][0]["actions"] == ["chat", "config"]


async def test_os_sessions_contract(client: AsyncClient, auth_headers: dict[str, str]):
    resp = await client.get("/v1/os/sessions", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Sessions"
    assert [column["key"] for column in body["columns"]] == ["name", "updated_at"]
    assert body["rows"]


async def test_os_metrics_contract(client: AsyncClient, auth_headers: dict[str, str]):
    resp = await client.get("/v1/os/metrics", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["period"] == "JUN 2026"
    assert {metric["label"] for metric in body["metrics"]} >= {
        "Total tokens",
        "Users",
        "Agent Runs",
    }
