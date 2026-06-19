"""API 基础测试"""

from types import SimpleNamespace

import pytest
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def mock_router_chat(monkeypatch: pytest.MonkeyPatch):
    """避免 API 契约测试依赖真实 LLM。"""

    async def fake_arun(*args, **kwargs):
        return SimpleNamespace(content="测试回复", session_id=kwargs.get("session_id") or "test-session")

    monkeypatch.setattr("app.api.v1.endpoints.chat.router_team.arun", fake_arun)


async def test_health_ok(client: AsyncClient):
    """AgentOS health 路由返回运行状态。"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


async def test_chat_missing_body(client: AsyncClient, auth_headers: dict):
    """缺少 body 返回统一格式 422"""
    resp = await client.post("/v1/chat", headers=auth_headers)
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == 42201
    assert isinstance(body["detail"], list)


async def test_chat_empty_message(client: AsyncClient, auth_headers: dict):
    """空 message 字段也可请求（不做非空校验）"""
    resp = await client.post("/v1/chat", json={"message": ""}, headers=auth_headers)
    # 只要鉴权通过，应返回 200（Agent 会给出回复）
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data


async def test_request_id_in_response_header(client: AsyncClient):
    """响应 header 包含 X-Request-ID"""
    resp = await client.get("/health")
    assert "X-Request-ID" in resp.headers
    assert resp.headers["X-Request-ID"].startswith("req_")


async def test_request_id_passthrough(client: AsyncClient):
    """请求携带 X-Request-ID 时透传"""
    resp = await client.get("/health", headers={"X-Request-ID": "custom-id-123"})
    assert resp.headers["X-Request-ID"] == "custom-id-123"


async def test_chat_response_schema(client: AsyncClient, auth_headers: dict):
    """验证 ChatResponse schema 结构"""
    resp = await client.post(
        "/v1/chat",
        json={"message": "你好"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert "action" in data
