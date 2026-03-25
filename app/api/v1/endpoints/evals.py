"""评测触发接口 — 通过 API 启动 Langfuse Dataset 评测实验"""
from __future__ import annotations

import functools
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.core.tracing import setup_tracing
from app.evals.executor import HttpEvalRequester
from app.evals.judge import llm_judge
from app.evals.langfuse_eval import EvalRunSummary, run_eval_experiment

router = APIRouter(prefix="/evals", tags=["evals"])

# 内存中存储后台任务结果（服务重启后丢失，当前阶段不持久化）
# 使用 OrderedDict 限制最大条目数，防止内存泄漏
_MAX_RUN_RESULTS = 100
_run_results: OrderedDict[str, EvalRunSummary | str] = OrderedDict()


_ALLOWED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


class EvalRunRequest(BaseModel):
    """评测实验请求参数。"""

    dataset_name: str = Field(default="mx-agent-evals", description="Langfuse Dataset 名称")
    id_prefix: str = Field(default="", description="按 case_id 前缀过滤，逗号分隔")
    limit: int = Field(default=0, ge=0, description="最多执行条数，0=不限制")
    run_name: str = Field(default="", description="实验名称前缀，为空则自动生成")
    base_url: str = Field(default="http://localhost:8000", description="Agent 接口地址")
    endpoint: str = Field(default="/teams/router-team/runs", description="接口路径")
    auth_token: str = Field(default="", description="Bearer Token")
    timeout: float = Field(default=30.0, description="接口超时秒数")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        parsed = urlparse(v)
        host = (parsed.hostname or "").lower()
        if host not in _ALLOWED_HOSTS:
            raise ValueError(f"base_url 仅允许本地地址 ({', '.join(_ALLOWED_HOSTS)})，收到: {host}")
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
    avg_response_quality: float | None = None
    failed: list[dict] | None = None


async def _run_background(run_name: str, req: EvalRunRequest) -> None:
    """后台执行评测实验。"""
    setup_tracing()
    requester = HttpEvalRequester(
        base_url=req.base_url,
        endpoint=req.endpoint,
        timeout=req.timeout,
        auth_token=req.auth_token,
        request_mode="auto",
    )
    judge_fn = functools.partial(
        llm_judge,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )
    try:
        summary = await run_eval_experiment(
            dataset_name=req.dataset_name,
            run_name=run_name,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix=req.id_prefix,
            limit=req.limit,
        )
        _run_results[run_name] = summary
        # 淘汰最旧条目
        while len(_run_results) > _MAX_RUN_RESULTS:
            _run_results.popitem(last=False)
    except Exception as e:
        _run_results[run_name] = f"failed: {e}"
    finally:
        if requester is not None:
            await requester.close()


@router.post("/runs", response_model=EvalRunStarted, status_code=202)
async def start_eval_run(req: EvalRunRequest, background_tasks: BackgroundTasks) -> EvalRunStarted:
    """启动评测实验（后台执行，立即返回）。

    Args:
        req: 评测请求参数
        background_tasks: FastAPI 后台任务

    Returns:
        EvalRunStarted，含实际 run_name
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_name = f"{req.run_name}-{ts}" if req.run_name else f"eval-run-{ts}"
    _run_results[run_name] = "started"
    background_tasks.add_task(_run_background, run_name, req)
    return EvalRunStarted(run_name=run_name)


@router.get("/runs/{run_name}", response_model=EvalRunStatus)
async def get_eval_run_status(run_name: str) -> EvalRunStatus:
    """查询评测实验状态与结果。

    Args:
        run_name: 由 POST /v1/evals/runs 返回的 run_name

    Returns:
        EvalRunStatus
    """
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
