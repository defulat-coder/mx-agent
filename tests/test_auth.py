"""鉴权相关测试"""

import time

import jwt
from httpx import AsyncClient

from app.config import settings
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
