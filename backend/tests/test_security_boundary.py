"""后端 HTTP 安全边界回归测试。"""

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/info",
        "/agents",
        "/agents/router-agent/runs",
        "/teams",
        "/teams/router-team/runs",
        "/workflows",
        "/sessions",
        "/sessions/example",
        "/memories",
        "/knowledge/content",
        "/traces",
        "/traces/example",
        "/metrics",
        "/metrics/sessions",
        "/config",
    ],
)
async def test_agentos_routes_reject_anonymous_requests(client: AsyncClient, path: str):
    response = await client.get(path)

    assert response.status_code == 401


@pytest.mark.parametrize("path", ["/health", "/docs", "/openapi.json"])
async def test_public_operational_routes_remain_available(client: AsyncClient, path: str):
    response = await client.get(path)

    assert response.status_code == 200


async def test_allowed_local_frontend_origin_can_preflight(client: AsyncClient):
    response = await client.options(
        "/v1/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


async def test_untrusted_origin_is_not_allowed(client: AsyncClient):
    response = await client.options(
        "/v1/chat",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers

    actual_response = await client.get(
        "/sessions",
        headers={"Origin": "https://evil.example"},
    )
    assert actual_response.status_code == 401
    assert "access-control-allow-origin" not in actual_response.headers


@pytest.mark.parametrize(
    "payload",
    [
        {"message": ""},
        {"message": "   "},
        {"message": "x" * 10_001},
        {"message": "hello", "session_id": ""},
        {"message": "hello", "session_id": "x" * 129},
    ],
)
async def test_chat_request_rejects_invalid_lengths(
    client: AsyncClient,
    auth_headers: dict[str, str],
    payload: dict[str, str],
):
    response = await client.post("/v1/chat", headers=auth_headers, json=payload)

    assert response.status_code == 422
