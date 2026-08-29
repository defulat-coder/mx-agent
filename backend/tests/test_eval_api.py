"""评测 API 的权限、输入安全与后台任务边界测试。"""

import time
from unittest.mock import Mock

import jwt
import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient

from app.api.v1.endpoints import evals
from app.config import settings


def _auth_headers(*roles: str) -> dict[str, str]:
    token = jwt.encode(
        {
            "employee_id": 9,
            "roles": list(roles),
            "exp": int(time.time()) + 3600,
        },
        settings.AUTH_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clear_eval_state():
    evals._run_results.clear()
    evals._active_runs.clear()
    yield
    evals._run_results.clear()
    evals._active_runs.clear()


async def test_eval_runs_require_admin_role(client: AsyncClient):
    employee_headers = _auth_headers("employee")

    start = await client.post("/v1/evals/runs", json={}, headers=employee_headers)
    status = await client.get("/v1/evals/runs/missing", headers=employee_headers)

    assert start.status_code == 403
    assert status.status_code == 403


async def test_admin_can_start_and_query_eval(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *_args, **_kwargs: None)
    headers = _auth_headers("admin")

    start = await client.post(
        "/v1/evals/runs",
        json={"run_name": "security-check", "limit": 10, "timeout": 15},
        headers=headers,
    )

    assert start.status_code == 202
    run_name = start.json()["run_name"]
    assert run_name.startswith("security-check-")

    status = await client.get(f"/v1/evals/runs/{run_name}", headers=headers)
    assert status.status_code == 200
    assert status.json()["status"] == "running"


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"base_url": "http://169.254.169.254"}, "base_url"),
        ({"base_url": "file://localhost/tmp"}, "base_url"),
        ({"base_url": "http://localhost:8000/other"}, "base_url"),
        ({"base_url": "http://user:pass@localhost:8000"}, "base_url"),
        ({"endpoint": "http://evil.example/teams/router-team/runs"}, "endpoint"),
        ({"endpoint": "/agents"}, "endpoint"),
        ({"limit": 1001}, "limit"),
        ({"timeout": 0.5}, "timeout"),
        ({"timeout": 121}, "timeout"),
        ({"run_name": "unsafe name"}, "run_name"),
        ({"run_name": "x" * 65}, "run_name"),
    ],
)
async def test_eval_request_rejects_unsafe_or_unbounded_input(
    client: AsyncClient,
    payload: dict,
    field: str,
):
    response = await client.post("/v1/evals/runs", json=payload, headers=_auth_headers("admin"))

    assert response.status_code == 422
    assert any(field in error["loc"] for error in response.json()["detail"])


async def test_eval_concurrency_limit_returns_429(client: AsyncClient):
    evals._active_runs.update({"run-1", "run-2"})

    response = await client.post("/v1/evals/runs", json={}, headers=_auth_headers("admin"))

    assert response.status_code == 429
    assert "并发数已达上限" in response.json()["message"]


def test_run_names_do_not_collide_within_same_second():
    first = evals._new_run_name("same")
    evals._run_results[first] = "started"
    second = evals._new_run_name("same")

    assert first != second


def test_all_result_states_use_bounded_storage(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(evals, "_MAX_RUN_RESULTS", 2)

    evals._store_run_result("started", "started")
    evals._store_run_result("failed", "failed: boom")
    evals._store_run_result("newest", "started")

    assert list(evals._run_results) == ["failed", "newest"]


async def test_background_failure_is_logged_stored_and_releases_slot(
    monkeypatch: pytest.MonkeyPatch,
):
    close_called = False

    class FakeRequester:
        def __init__(self, **_kwargs):
            pass

        async def close(self):
            nonlocal close_called
            close_called = True

    async def fail_run(**_kwargs):
        raise RuntimeError("boom")

    log_exception = Mock()
    monkeypatch.setattr(evals, "setup_tracing", lambda: None)
    monkeypatch.setattr(evals, "flush_traces", lambda: None)
    monkeypatch.setattr(evals, "HttpEvalRequester", FakeRequester)
    monkeypatch.setattr(evals, "run_eval_experiment", fail_run)
    monkeypatch.setattr(evals.logger, "exception", log_exception)
    evals._active_runs.add("broken-run")

    await evals._run_background("broken-run", evals.EvalRunRequest())

    assert evals._run_results["broken-run"] == "failed: boom"
    assert "broken-run" not in evals._active_runs
    assert close_called
    log_exception.assert_called_once()
