"""评测触发接口 — 通过 API 启动 Langfuse Dataset 评测实验"""
from __future__ import annotations

import functools
import uuid
from collections import OrderedDict
from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.core.auth import decode_auth_claims
from app.core.exceptions import ForbiddenException
from app.core.tracing import flush_traces, setup_tracing
from app.evals.auth import make_auth_token_resolver
from app.evals.executor import HttpEvalRequester
from app.evals.judge import llm_judge
from app.evals.langfuse_eval import EvalRunSummary, run_eval_experiment

router = APIRouter(prefix="/evals", tags=["evals"])

# 内存中存储后台任务结果（服务重启后丢失，当前阶段不持久化）
# 使用 OrderedDict 限制最大条目数，防止内存泄漏
_MAX_RUN_RESULTS = 100
_MAX_CONCURRENT_RUNS = 2
_run_results: OrderedDict[str, EvalRunSummary | str] = OrderedDict()
_active_runs: set[str] = set()

_ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
_ALLOWED_ENDPOINTS = {"/teams/router-team/runs"}


class EvalRunRequest(BaseModel):
    """评测实验请求参数。"""

    dataset_name: str = Field(default="mx-agent-evals", min_length=1, max_length=128, description="Langfuse Dataset 名称")
    id_prefix: str = Field(default="", max_length=512, description="按 case_id 前缀过滤，逗号分隔")
    limit: int = Field(default=0, ge=0, le=1000, description="最多执行条数，0=不限制")
    run_name: str = Field(
        default="",
        max_length=64,
        pattern=r"^[A-Za-z0-9._-]*$",
        description="实验名称前缀，为空则自动生成",
    )
    base_url: str = Field(default="http://localhost:8000", description="Agent 接口地址")
    endpoint: str = Field(default="/teams/router-team/runs", description="接口路径")
    auth_mode: Literal["auto", "static"] = Field(
        default="auto",
        description="auto=按用例身份自动生成 token；static=使用传入 token",
    )
    auth_token: str = Field(default="", description="Bearer Token")
    timeout: float = Field(default=30.0, ge=1.0, le=120.0, description="接口超时秒数")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        parsed = urlparse(v)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("base_url 仅允许 http 或 https")
        if host not in _ALLOWED_HOSTS:
            raise ValueError(f"base_url 仅允许本地地址 ({', '.join(_ALLOWED_HOSTS)})，收到: {host}")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url 不允许包含认证信息、查询参数或 fragment")
        if parsed.path not in {"", "/"}:
            raise ValueError("base_url 不允许包含路径")
        return v.rstrip("/")

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        if v not in _ALLOWED_ENDPOINTS:
            raise ValueError("endpoint 仅允许站内 router team run 路径")
        return v


class EvalRunStarted(BaseModel):
    """评测实验启动响应。"""

    run_name: str = Field(description="实际使用的唯一 run_name（含时间戳后缀）")
    status: str = Field(default="started")
    message: str = Field(default="评测已在后台启动，请通过 GET /v1/evals/runs/{run_name} 查询进度")


class EvalRunStatus(BaseModel):
    """评测实验状态查询响应。"""

    run_name: str
    status: str = Field(description="running | completed | failed")
    total: int | None = None
    passed: int | None = None
    tool_match_rate: float | None = None
    route_match_rate: float | None = None
    avg_response_quality: float | None = None
    failed: list[dict] | None = None


def _require_admin(request: Request) -> None:
    claims = decode_auth_claims(request)
    roles = claims.get("roles", [])
    if not isinstance(roles, list) or "admin" not in roles:
        raise ForbiddenException(message="评测接口仅限管理员使用")


def _store_run_result(run_name: str, result: EvalRunSummary | str) -> None:
    _run_results[run_name] = result
    _run_results.move_to_end(run_name)
    while len(_run_results) > _MAX_RUN_RESULTS:
        _run_results.popitem(last=False)


def _new_run_name(prefix: str) -> str:
    base = prefix or "eval-run"
    while True:
        suffix = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        run_name = f"{base}-{suffix}"
        if run_name not in _run_results and run_name not in _active_runs:
            return run_name


async def _run_background(run_name: str, req: EvalRunRequest) -> None:
    """后台执行评测实验。"""
    requester: HttpEvalRequester | None = None
    try:
        setup_tracing()
        static_token = req.auth_token if req.auth_mode == "static" else ""
        requester = HttpEvalRequester(
            base_url=req.base_url,
            endpoint=req.endpoint,
            timeout=req.timeout,
            auth_token=static_token,
            request_mode="auto",
            auth_token_resolver=make_auth_token_resolver(settings.AUTH_SECRET, static_token),
        )
        judge_fn = functools.partial(
            llm_judge,
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        summary = await run_eval_experiment(
            dataset_name=req.dataset_name,
            run_name=run_name,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix=req.id_prefix,
            limit=req.limit,
        )
        _store_run_result(run_name, summary)
    except Exception as e:
        logger.exception("后台评测失败 | run_name={}", run_name)
        _store_run_result(run_name, f"failed: {e}")
    finally:
        _active_runs.discard(run_name)
        if requester is not None:
            try:
                await requester.close()
            except Exception:
                logger.exception("关闭评测 HTTP 客户端失败 | run_name={}", run_name)
        try:
            flush_traces()
        except Exception:
            logger.exception("刷新评测 trace 失败 | run_name={}", run_name)


@router.post("/runs", response_model=EvalRunStarted, status_code=202)
async def start_eval_run(req: EvalRunRequest, background_tasks: BackgroundTasks, request: Request) -> EvalRunStarted:
    """启动评测实验（后台执行，立即返回）。

    Args:
        req: 评测请求参数
        background_tasks: FastAPI 后台任务

    Returns:
        EvalRunStarted，含实际 run_name
    """
    _require_admin(request)
    if len(_active_runs) >= _MAX_CONCURRENT_RUNS:
        raise HTTPException(status_code=429, detail=f"评测任务并发数已达上限 {_MAX_CONCURRENT_RUNS}")
    run_name = _new_run_name(req.run_name)
    _active_runs.add(run_name)
    _store_run_result(run_name, "started")
    background_tasks.add_task(_run_background, run_name, req)
    return EvalRunStarted(run_name=run_name)


@router.get("/runs/{run_name}", response_model=EvalRunStatus)
async def get_eval_run_status(run_name: str, request: Request) -> EvalRunStatus:
    """查询评测实验状态与结果。

    Args:
        run_name: 由 POST /v1/evals/runs 返回的 run_name

    Returns:
        EvalRunStatus
    """
    _require_admin(request)
    result = _run_results.get(run_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"run_name '{run_name}' 不存在")
    if result == "started":
        return EvalRunStatus(run_name=run_name, status="running")
    if isinstance(result, str) and result.startswith("failed:"):
        return EvalRunStatus(run_name=run_name, status="failed")
    summary: EvalRunSummary = result  # type: ignore[assignment]
    return EvalRunStatus(
        run_name=run_name,
        status="completed",
        total=summary.total,
        passed=summary.passed,
        tool_match_rate=summary.tool_match_rate,
        route_match_rate=summary.route_match_rate,
        avg_response_quality=summary.avg_response_quality,
        failed=[
            {
                "case_id": f.case_id,
                "fail_reason": f.fail_reason,
                "response_preview": f.response_preview,
            }
            for f in summary.failed
        ],
    )
