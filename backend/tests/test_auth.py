"""鉴权相关测试"""

import time
from types import SimpleNamespace

import jwt
import pytest
from httpx import AsyncClient

from app.config import settings
from app.tools.hr.utils import get_employee_id
from tests.conftest import make_token


async def test_no_token_returns_401(client: AsyncClient):
    resp = await client.post("/v1/chat", json={"message": "hello"})
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == 40101
    assert "token" in body["message"]
    assert "request_id" in body
    assert "timestamp" in body


async def test_invalid_token_returns_401(client: AsyncClient):
    resp = await client.post(
        "/v1/chat",
        json={"message": "hello"},
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == 40103


async def test_expired_token_returns_401(client: AsyncClient, expired_token: str):
    resp = await client.post(
        "/v1/chat",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == 40102
    assert "过期" in body["message"]


async def test_token_missing_employee_id(client: AsyncClient):
    token = jwt.encode(
        {"name": "test", "exp": int(time.time()) + 3600},
        settings.AUTH_SECRET,
        algorithm="HS256",
    )
    resp = await client.post(
        "/v1/chat",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert "employee_id" in resp.json()["message"]


def test_mock_identity_disabled_by_default():
    old_debug = settings.DEBUG
    old_allow_mock = settings.ALLOW_MOCK_IDENTITY
    try:
        settings.DEBUG = False
        settings.ALLOW_MOCK_IDENTITY = False
        run_context = SimpleNamespace(session_id="s1", session_state=None)
        with pytest.raises(ValueError, match="未检测到登录态"):
            get_employee_id(run_context)  # type: ignore[arg-type]
    finally:
        settings.DEBUG = old_debug
        settings.ALLOW_MOCK_IDENTITY = old_allow_mock


def test_mock_identity_enabled_can_inject():
    old_debug = settings.DEBUG
    old_allow_mock = settings.ALLOW_MOCK_IDENTITY
    try:
        settings.DEBUG = False
        settings.ALLOW_MOCK_IDENTITY = True
        run_context = SimpleNamespace(session_id="s2", session_state=None)
        employee_id = get_employee_id(run_context)  # type: ignore[arg-type]
        assert isinstance(employee_id, int)
        assert run_context.session_state["employee_id"] == employee_id
    finally:
        settings.DEBUG = old_debug
        settings.ALLOW_MOCK_IDENTITY = old_allow_mock
