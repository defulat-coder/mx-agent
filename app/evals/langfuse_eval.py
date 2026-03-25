"""Langfuse 评测核心 — Dataset 管理、实验执行、双指标打分上报"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime

from app.core.logging import logger
from app.core.tracing import get_langfuse_client
from app.evals.executor import HttpEvalRequester, HttpEvalResponse
from app.evals.judge import JudgeResult
from app.evals.runner import EvalCase

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
    avg_response_quality: float | None
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


def _collect_response_text(body: dict) -> str:
    """从响应体递归收集文本内容。"""
    values: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, str):
            values.append(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in {
                    "reply", "content", "message", "result", "response",
                    "output", "text", "member_responses", "messages", "choices", "delta",
                }:
                    walk(value)

    walk(body)
    return " ".join(values).strip()


def _collect_tool_names(body: dict) -> set[str]:
    """从响应体结构化字段收集完整工具名。

    只从明确的工具调用字段中提取名称，``"name"`` 仅在作为
    ``"function"`` / ``"tool_call"`` dict 的子键时才被采集，
    避免将用户名、模型名等无关值误判为工具名。
    """
    names: set[str] = set()

    def walk(node: object, *, inside_tool: bool = False) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item, inside_tool=inside_tool)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in {"tool", "tool_name"}:
                    if isinstance(value, str):
                        names.add(value.strip().lower())
                    else:
                        walk(value, inside_tool=True)
                elif key in {"function", "tool_call", "tool_calls"}:
                    walk(value, inside_tool=True)
                elif key == "name" and inside_tool:
                    if isinstance(value, str):
                        names.add(value.strip().lower())
                elif key in {"member_responses", "messages", "choices", "delta"}:
                    walk(value, inside_tool=False)

    walk(body)
    return names


def _compute_tool_match(case: EvalCase, resp: HttpEvalResponse) -> bool | None:
    """计算工具匹配分（精确匹配）。

    Args:
        case: 评测用例
        resp: HTTP 评测响应

    Returns:
        True/False 表示匹配/不匹配；None 表示用例无需检查工具
    """
    expected = case.expected_tool.strip() if case.expected_tool else ""
    if not expected or expected in {"—", "-"}:
        return None
    expected_lower = expected.lower()
    observed = _collect_tool_names(resp.body)
    return expected_lower in observed


def _make_run_name(base: str | None) -> str:
    """生成唯一 run_name，追加时间戳后缀。"""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if base:
        return f"{base}-{ts}"
    return f"eval-run-{ts}"


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
    actual_run_name = run_name if run_name else _make_run_name(None)
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
                if (it.input.get("original_case_id") or it.input.get("case_id", ""))
                .split("-", 1)[0].upper() in prefixes
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
    quality_scores: list[float] = []
    failed_items: list[FailedItem] = []
    completed = 0

    async def _eval_one(idx: int, item: object) -> None:
        nonlocal total, passed, completed
        inp = item.input or {}
        exp = item.expected_output or {}
        case = EvalCase(
            case_id=inp.get("case_id", ""),
            file_path="langfuse",
            section=inp.get("section", ""),
            subsection=inp.get("subsection", ""),
            user_input=inp.get("user_input", ""),
            expected_tool=exp.get("expected_tool", ""),
            expected_behavior=exp.get("expected_behavior", ""),
            raw={},
        )

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

            # 关联 trace 到当前 run
            if client and trace_id:
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            client.create_dataset_run_item,
                            run_name=actual_run_name,
                            dataset_item_id=item.id,
                            trace_id=trace_id,
                        ),
                        timeout=15,
                    )
                except Exception as e:
                    logger.debug(f"关联 trace 失败 case={case.case_id}: {e}")

            # 规则打分: tool_match
            tool_match = _compute_tool_match(case, resp)

            # HTTP 状态检查
            if resp.status_code != 200:
                fail_reason = f"http_{resp.status_code}"
            elif tool_match is False:
                fail_reason = "tool_mismatch"

            # 上报 tool_match score
            if client and trace_id and tool_match is not None:
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(
                            client.score,
                            trace_id=trace_id,
                            name="tool_match",
                            value=1.0 if tool_match else 0.0,
                            data_type="NUMERIC",
                        ),
                        timeout=15,
                    )
                except Exception as e:
                    logger.debug(f"上报 tool_match score 失败: {e}")

            # LLM judge: response_quality
            response_text = _collect_response_text(resp.body)
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
                                    client.score,
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

            # 综合判断是否通过
            case_ok = resp.status_code == 200 and tool_match is not False

            async with lock:
                total += 1
                completed += 1
                if tool_match is not None:
                    tool_matches.append(tool_match)
                if judge_score is not None:
                    quality_scores.append(judge_score)
                if case_ok:
                    passed += 1
                elif fail_reason:
                    failed_items.append(
                        FailedItem(
                            case_id=case.case_id,
                            fail_reason=fail_reason,
                            response_preview=response_text[:160],
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
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None

    msg = f"评测完成: {total} 条, 通过 {passed}, 工具匹配率 {tool_match_rate:.1%}"
    if avg_quality is not None:
        msg += f", 平均质量 {avg_quality:.2f}"
    logger.info(msg)

    return EvalRunSummary(
        run_name=actual_run_name,
        total=total,
        passed=passed,
        tool_match_rate=tool_match_rate,
        avg_response_quality=avg_quality,
        failed=failed_items,
    )
