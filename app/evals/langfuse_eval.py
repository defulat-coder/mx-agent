"""Langfuse 评测核心 — Dataset 管理、实验执行、双指标打分上报"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime

from app.core.logging import logger
from app.core.tracing import flush_traces, get_langfuse_client
from app.evals.executor import HttpEvalRequester, HttpEvalResponse, analyze_response, score_case
from app.evals.judge import JudgeResult
from app.evals.runner import (
    EvalAuthProfile,
    EvalCase,
    _parse_agent_expectation,
    _parse_forbidden_tools,
    _parse_tool_expectation,
)

# 默认并发数
DEFAULT_CONCURRENCY = 5


@dataclass(slots=True)
class FailedItem:
    case_id: str
    fail_reason: str
    response_preview: str


@dataclass
class EvalRunSummary:
    run_name: str
    total: int
    passed: int
    tool_match_rate: float
    route_match_rate: float | None = None
    avg_response_quality: float | None = None
    failed: list[FailedItem] = field(default_factory=list)


def _extract_trace_id(resp: HttpEvalResponse) -> str | None:
    """从响应头或响应体提取 trace_id。

    Args:
        resp: HTTP 评测响应

    Returns:
        trace_id 字符串，不存在则返回 None
    """
    lower_headers = {k.lower(): v for k, v in resp.headers.items()}
    if tid := lower_headers.get("x-trace-id"):
        return tid
    if isinstance(resp.body, dict):
        return resp.body.get("trace_id") or None
    return None


def _make_run_name(base: str | None) -> str:
    """生成唯一 run_name，追加时间戳后缀。"""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if base:
        return f"{base}-{ts}"
    return f"eval-run-{ts}"


def _get_item_field(item: object, field: str, default: object = None) -> object:
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def _coerce_mapping(value: object) -> dict:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        if isinstance(dumped, dict):
            return dumped
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def _extract_case_prefix(item: object) -> str:
    inp = _coerce_mapping(_get_item_field(item, "input", {}))
    case_id = inp.get("original_case_id") or inp.get("case_id") or ""
    return str(case_id).split("-", 1)[0].upper()


def _build_case_from_dataset_item(item: object) -> EvalCase:
    inp = _coerce_mapping(_get_item_field(item, "input", {}))
    exp = _coerce_mapping(_get_item_field(item, "expected_output", {}))
    metadata = _coerce_mapping(_get_item_field(item, "metadata", {}))
    auth_profile = _coerce_mapping(inp.get("auth_profile") or exp.get("auth_profile"))
    expected_tool = exp.get("expected_tool", "")
    expected_tools = list(exp.get("expected_tools", []))
    expected_tool_mode = exp.get("expected_tool_mode", "none")
    expected_tool_counts = dict(exp.get("expected_tool_counts", {}))
    if not expected_tools and expected_tool:
        expected_tools, expected_tool_mode, expected_tool_counts = _parse_tool_expectation(
            expected_tool
        )

    forbidden_tools = list(exp.get("forbidden_tools", []))
    if not forbidden_tools and exp.get("forbidden_tool"):
        forbidden_tools = _parse_forbidden_tools(exp.get("forbidden_tool", ""))

    expected_agents = list(exp.get("expected_agents", []))
    expected_agent_mode = exp.get("expected_agent_mode", "none")
    route_text = exp.get("expected_route", "")
    if not expected_agents and route_text:
        expected_agents, expected_agent_mode = _parse_agent_expectation(route_text, "预期路由")

    return EvalCase(
        case_id=inp.get("original_case_id") or inp.get("case_id") or metadata.get("case_id", ""),
        file_path=inp.get("source_file", "langfuse"),
        section=inp.get("section", ""),
        subsection=inp.get("subsection", ""),
        user_input=inp.get("user_input", ""),
        expected_tool=expected_tool,
        expected_behavior=exp.get("expected_behavior", ""),
        raw={},
        domain=inp.get("domain", ""),
        auth_profile=EvalAuthProfile(
            employee_id=auth_profile.get("employee_id", 1),
            roles=list(auth_profile.get("roles", [])),
            department_id=auth_profile.get("department_id"),
            label=auth_profile.get("label") or auth_profile.get("persona_label", ""),
        ),
        expected_tools=expected_tools,
        expected_tool_mode=expected_tool_mode,
        expected_tool_counts=expected_tool_counts,
        forbidden_tools=forbidden_tools,
        expected_agents=expected_agents,
        expected_agent_mode=expected_agent_mode,
    )


async def run_eval_experiment(
    dataset_name: str,
    run_name: str | None,
    requester: HttpEvalRequester,
    judge_fn: Callable[[str, str, str], Awaitable[JudgeResult]],
    id_prefix: str = "",
    limit: int = 0,
    concurrency: int = DEFAULT_CONCURRENCY,
    judge_concurrency: int | None = None,
) -> EvalRunSummary:
    """执行评测实验，上报双指标分数到 Langfuse。

    Args:
        dataset_name: Langfuse Dataset 名称
        run_name: 实验名称前缀，None 则自动生成（追加时间戳）
        requester: HTTP 请求执行器（async callable）
        judge_fn: LLM judge 函数，签名 (user_input, expected_behavior, response_text) -> JudgeResult
        id_prefix: 按 case_id 前缀过滤，逗号分隔，空则全量
        limit: 最多执行条数，0=不限制
        concurrency: 最大并发数
        judge_concurrency: LLM judge 最大并发数，None=跟随 concurrency

    Returns:
        EvalRunSummary 汇总结果
    """
    actual_run_name = _make_run_name(run_name)
    client = get_langfuse_client()
    judge_limit = max(1, min(concurrency, judge_concurrency or concurrency))

    # 降级：client=None（未配置）或 get_dataset 失败（连接异常）均跳过上报
    logger.info(f"正在从 Langfuse 获取 Dataset '{dataset_name}' ...")
    try:
        dataset = await asyncio.to_thread(client.get_dataset, dataset_name) if client else None
    except Exception as e:
        logger.warning(f"获取 Langfuse Dataset 失败: {e}，将跳过上报")
        dataset = None

    items = []
    if dataset:
        items = list(dataset.items)
        logger.info(f"Dataset 共 {len(items)} 条 items")
        if id_prefix:
            prefixes = {p.strip().upper() for p in id_prefix.split(",") if p.strip()}
            items = [
                it for it in items
                if _extract_case_prefix(it) in prefixes
            ]
            logger.info(f"按前缀 {id_prefix} 过滤后剩余 {len(items)} 条")
        if limit > 0:
            items = items[:limit]

    if not items:
        logger.warning(
            f"Dataset '{dataset_name}' 无可用 items"
            f"（已过滤 prefix={id_prefix!r} limit={limit}）"
        )
        return EvalRunSummary(
            run_name=actual_run_name,
            total=0,
            passed=0,
            tool_match_rate=0.0,
            route_match_rate=None,
            avg_response_quality=None,
        )

    logger.info(f"开始评测: {len(items)} 条用例，并发={concurrency}，run={actual_run_name}")

    # 并发控制
    semaphore = asyncio.Semaphore(concurrency)
    judge_semaphore = asyncio.Semaphore(judge_limit)
    lock = asyncio.Lock()

    # 共享结果
    total = 0
    passed = 0
    tool_matches: list[bool] = []
    route_matches: list[bool] = []
    quality_scores: list[float] = []
    failed_items: list[FailedItem] = []
    completed = 0

    async def _eval_one(idx: int, item: object) -> None:
        nonlocal total, passed, completed
        case = _build_case_from_dataset_item(item)

        async with semaphore:
            logger.info(f"[{idx + 1}/{len(items)}] 开始: {case.case_id} - {case.user_input[:40]}")
            trace_id: str | None = None
            fail_reason: str | None = None

            try:
                resp = await requester(case)
                trace_id = _extract_trace_id(resp)
            except Exception as exc:
                msg = str(exc).lower()
                fail_reason = "request_timeout" if "timeout" in msg else "request_error"
                async with lock:
                    total += 1
                    completed += 1
                    failed_items.append(
                        FailedItem(case_id=case.case_id, fail_reason=fail_reason, response_preview="")
                    )
                logger.warning(f"[{idx + 1}/{len(items)}] 失败: {case.case_id} - {fail_reason}")
                return

            if client and not trace_id:
                logger.warning(
                    f"[{idx + 1}/{len(items)}] trace_id 缺失: {case.case_id} — "
                    "Langfuse 评分上报将跳过（请确认 Agent 响应包含 X-Trace-Id 头或 trace_id 字段）"
                )

            # 关联 trace 到当前 run
            if client and trace_id:
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            client.api.dataset_run_items.create,
                            run_name=actual_run_name,
                            dataset_item_id=item.id,
                            trace_id=trace_id,
                        ),
                        timeout=15,
                    )
                except Exception as e:
                    logger.debug(f"关联 trace 失败 case={case.case_id}: {e}")

            rule_result = score_case(case, resp.status_code, resp.body)
            tool_match = rule_result.tool_match
            route_match = rule_result.route_match
            fail_reason = rule_result.fail_reason

            # 上报 tool_match score
            if client and trace_id and tool_match is not None:
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            client.create_score,
                            trace_id=trace_id,
                            name="tool_match",
                            value=1.0 if tool_match else 0.0,
                            data_type="NUMERIC",
                        ),
                        timeout=15,
                    )
                except Exception as e:
                    logger.debug(f"上报 tool_match score 失败: {e}")

            if client and trace_id and route_match is not None:
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            client.create_score,
                            trace_id=trace_id,
                            name="route_match",
                            value=1.0 if route_match else 0.0,
                            data_type="NUMERIC",
                        ),
                        timeout=15,
                    )
                except Exception as e:
                    logger.debug(f"上报 route_match score 失败: {e}")

            # LLM judge: response_quality
            response_text = analyze_response(resp.body).response_text
            judge_score: float | None = None
            try:
                async with judge_semaphore:
                    judge_result = await judge_fn(
                        case.user_input,
                        case.expected_behavior,
                        response_text,
                    )
                if judge_result.score is not None:
                    judge_score = judge_result.score
                    if client and trace_id:
                        try:
                            await asyncio.wait_for(
                                asyncio.to_thread(
                                    client.create_score,
                                    trace_id=trace_id,
                                    name="response_quality",
                                    value=judge_result.score,
                                    comment=judge_result.reason,
                                    data_type="NUMERIC",
                                ),
                                timeout=15,
                            )
                        except Exception as e:
                            logger.debug(f"上报 response_quality score 失败: {e}")
            except Exception as e:
                logger.debug(f"LLM judge 失败 case={case.case_id}: {e}")

            case_ok = rule_result.ok

            async with lock:
                total += 1
                completed += 1
                if tool_match is not None:
                    tool_matches.append(tool_match)
                if route_match is not None:
                    route_matches.append(route_match)
                if judge_score is not None:
                    quality_scores.append(judge_score)
                if case_ok:
                    passed += 1
                elif fail_reason:
                    failed_items.append(
                        FailedItem(
                            case_id=case.case_id,
                            fail_reason=fail_reason,
                            response_preview=rule_result.response_preview,
                        )
                    )
                current = completed

            status = "PASS" if case_ok else f"FAIL({fail_reason})"
            logger.info(f"[{current}/{len(items)}] 完成: {case.case_id} - {status}")

    # 并发执行所有用例
    tasks = [_eval_one(i, item) for i, item in enumerate(items)]
    await asyncio.gather(*tasks)

    tool_match_rate = (
        sum(1 for m in tool_matches if m) / len(tool_matches) if tool_matches else 0.0
    )
    route_match_rate = (
        sum(1 for m in route_matches if m) / len(route_matches) if route_matches else None
    )
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None

    # 刷新 Langfuse 缓冲区，确保所有 score / run-item 发送到服务端
    if client:
        try:
            await asyncio.to_thread(flush_traces)
            logger.info("Langfuse 缓冲区已刷新")
        except Exception as e:
            logger.warning(f"刷新 Langfuse 缓冲区失败: {e}")

    msg = f"评测完成: {total} 条, 通过 {passed}, 工具匹配率 {tool_match_rate:.1%}"
    if route_match_rate is not None:
        msg += f", 路由命中率 {route_match_rate:.1%}"
    if avg_quality is not None:
        msg += f", 平均质量 {avg_quality:.2f}"
    logger.info(msg)

    return EvalRunSummary(
        run_name=actual_run_name,
        total=total,
        passed=passed,
        tool_match_rate=tool_match_rate,
        route_match_rate=route_match_rate,
        avg_response_quality=avg_quality,
        failed=failed_items,
    )
