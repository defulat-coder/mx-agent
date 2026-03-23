# Langfuse 评测模块重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将评测模块从本地 Markdown + 自定义打分迁移到 Langfuse Dataset + 双指标打分（规则 tool_match + LLM-as-a-judge response_quality），并提供 CLI 和 FastAPI 两种触发方式。

**Architecture:** 新增 `app/evals/langfuse_eval.py`（Dataset/Score 核心）和 `app/evals/judge.py`（LLM judge），改造 `executor.py` 返回值类型，新增迁移脚本和 FastAPI endpoint，`runner.py` 零改动。

**Tech Stack:** Python 3.13, FastAPI, langfuse>=4.0.0, openai>=2.20.0（GLM 兼容），pytest, asyncio

---

## 文件变更清单

| 动作 | 文件 |
|---|---|
| 修改 | `app/evals/executor.py` — 扩展返回类型，保留请求层 |
| 新增 | `app/evals/judge.py` — LLM-as-a-judge |
| 新增 | `app/evals/langfuse_eval.py` — Dataset/Score 核心 |
| 新增 | `scripts/migrate_evals.py` — Markdown → Langfuse Dataset |
| 重构 | `scripts/run_evals.py` — CLI 改为调用 Langfuse 评测 |
| 新增 | `app/api/v1/endpoints/evals.py` — FastAPI endpoint |
| 修改 | `app/api/v1/router.py` — 注册 evals router |
| 新增 | `tests/test_eval_langfuse.py` — langfuse_eval 单元测试 |
| 新增 | `tests/test_eval_judge.py` — judge 单元测试 |
| 修改 | `tests/test_eval_executor.py` — 更新受影响的测试 |

---

## Task 1: 扩展 `HttpEvalRequester` 返回类型

`executor.py` 当前 `__call__` 返回 `tuple[int, dict]`，无法携带响应头（用于提取 `X-Trace-Id`）。需要引入 `HttpEvalResponse` 数据类，同时保留现有 `score_case`/`execute_cases` 以免破坏现有测试。

**Files:**
- Modify: `app/evals/executor.py`
- Modify: `tests/test_eval_executor.py`

- [ ] **Step 1: 在 `executor.py` 顶部添加 `HttpEvalResponse` 数据类**

在文件第 1 行 `from dataclasses import dataclass` 后，在 `EvalResult` 定义前插入：

```python
@dataclass(slots=True)
class HttpEvalResponse:
    status_code: int
    body: dict[str, Any]
    headers: dict[str, str]
```

- [ ] **Step 2: 修改 `HttpEvalRequester.__call__` 返回 `HttpEvalResponse`**

将 `__call__` 方法改为：

```python
def __call__(self, case: EvalCase) -> HttpEvalResponse:
    payload = {self.message_field: case.user_input}
    mode = self._resolved_mode()
    if mode == "form":
        payload["stream"] = "false"
        payload["monitor"] = "false"
        response = self._client.post(self.endpoint, data=payload)
    else:
        response = self._client.post(self.endpoint, json=payload)
    try:
        body = response.json()
    except Exception:
        body = {"message": response.text}
    return HttpEvalResponse(
        status_code=response.status_code,
        body=body,
        headers=dict(response.headers),
    )
```

- [ ] **Step 3: 更新 `execute_cases` 兼容新返回类型**

`execute_cases` 中 `requester(case)` 的解包改为：

```python
eval_response = requester(case)
results.append(score_case(case, eval_response.status_code, eval_response.body))
```

同时更新函数签名：

```python
def execute_cases(
    cases: Iterable[EvalCase],
    requester: Callable[[EvalCase], HttpEvalResponse],
) -> list[EvalResult]:
```

- [ ] **Step 4: 更新 `tests/test_eval_executor.py` 中受影响的测试**

`test_execute_cases_collects_errors` 和 `test_execute_cases_classifies_timeout_error` 中的 mock requester 仍然 raise 异常，逻辑不变。但两个测试里的类型注解需要更新为 `Callable[[EvalCase], HttpEvalResponse]`（如有显式注解），同时文件顶部需要导入 `HttpEvalResponse`：

```python
from app.evals.executor import HttpEvalRequester, HttpEvalResponse, execute_cases, score_case
```

另外，如果未来有返回正常值的 mock requester（非 raise），mock 函数需要改为返回 `HttpEvalResponse`，例如：

```python
def mock_requester(case: EvalCase) -> HttpEvalResponse:
    return HttpEvalResponse(status_code=200, body={"reply": "ok"}, headers={})
```

- [ ] **Step 5: 运行测试确认全部通过**

```bash
uv run pytest tests/test_eval_executor.py -v
```

预期：全部 PASS

- [ ] **Step 6: Commit**

```bash
git add app/evals/executor.py tests/test_eval_executor.py
git commit -m "refactor(evals): 扩展 HttpEvalRequester 返回 HttpEvalResponse 含响应头"
```

---

## Task 2: 实现 `app/evals/judge.py`

**Files:**
- Create: `app/evals/judge.py`
- Create: `tests/test_eval_judge.py`

- [ ] **Step 1: 写失败测试**

新建 `tests/test_eval_judge.py`：

```python
"""LLM judge 单元测试"""
import pytest
from unittest.mock import AsyncMock, patch
from app.evals.judge import JudgeResult, llm_judge


@pytest.mark.asyncio
async def test_llm_judge_returns_score_on_valid_json():
    mock_response = AsyncMock()
    mock_response.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": '{"score": 0.9, "reason": "回答准确"}'})()})()
    ]
    with patch("app.evals.judge.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await llm_judge(
            user_input="查薪资",
            expected_behavior="调用薪资工具",
            response_text="已调用 get_salary_info 返回数据",
            model="glm-4",
            api_key="test-key",
            base_url="https://example.com",
        )
    assert result.score == pytest.approx(0.9)
    assert result.reason == "回答准确"


@pytest.mark.asyncio
async def test_llm_judge_handles_parse_error():
    mock_response = AsyncMock()
    mock_response.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": "不是JSON格式的输出"})()})()
    ]
    with patch("app.evals.judge.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await llm_judge(
            user_input="查薪资",
            expected_behavior="调用薪资工具",
            response_text="回答",
            model="glm-4",
            api_key="test-key",
            base_url="https://example.com",
        )
    assert result.score is None
    assert result.reason.startswith("parse_error:")
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_eval_judge.py -v
```

预期：ImportError（模块不存在）

- [ ] **Step 3: 实现 `app/evals/judge.py`**

```python
"""LLM-as-a-judge — 使用 LLM 对 Agent 回答质量打分"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

_JUDGE_PROMPT = """\
你是一个企业 AI 助手评测员。请根据以下信息给实际回答打分。

用户问题: {user_input}
预期行为: {expected_behavior}
实际回答: {response_text}

评分标准（综合以下维度）：
- 是否直接回答了用户问题
- 回答是否符合预期行为描述
- 回答是否准确完整，无明显错误

请只输出 JSON，不要其他内容：
{{"score": 0.85, "reason": "简要说明"}}

score 范围 0.0-1.0。\
"""


@dataclass(slots=True)
class JudgeResult:
    score: float | None
    reason: str


async def llm_judge(
    user_input: str,
    expected_behavior: str,
    response_text: str,
    model: str,
    api_key: str,
    base_url: str,
) -> JudgeResult:
    """使用 LLM 对 Agent 回答质量打分。

    Args:
        user_input: 用户原始输入
        expected_behavior: 用例中定义的预期行为
        response_text: Agent 实际回答文本
        model: LLM 模型名称
        api_key: LLM API Key
        base_url: LLM API Base URL

    Returns:
        JudgeResult，score=None 表示解析失败
    """
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    prompt = _JUDGE_PROMPT.format(
        user_input=user_input,
        expected_behavior=expected_behavior,
        response_text=response_text[:2000],
    )
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=256,
        )
        raw = response.choices[0].message.content or ""
        # 提取 JSON（容忍 LLM 在 JSON 前后输出少量文字）
        match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
        if not match:
            return JudgeResult(score=None, reason=f"parse_error: {raw[:200]}")
        data = json.loads(match.group())
        score = float(data["score"])
        score = max(0.0, min(1.0, score))
        return JudgeResult(score=score, reason=str(data.get("reason", "")))
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return JudgeResult(score=None, reason=f"parse_error: {e}")
    except Exception as e:
        return JudgeResult(score=None, reason=f"judge_error: {e}")
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_eval_judge.py -v
```

预期：2 个 PASS

- [ ] **Step 5: 关于 `judge_fn` 与 `run_eval_experiment` 的接口说明**

`llm_judge` 有 6 个参数，而 `run_eval_experiment` 期望的 `judge_fn` 类型是 `Callable[[str, str, str], Awaitable[JudgeResult]]`（只接收 user_input, expected_behavior, response_text）。调用方需用 `functools.partial` 预先绑定后 3 个参数（Tasks 5 和 6 中已体现）：

```python
import functools
judge_fn = functools.partial(
    llm_judge,
    model=settings.LLM_MODEL,
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
)
# judge_fn 现在符合 Callable[[str, str, str], Awaitable[JudgeResult]]
```

- [ ] **Step 6: Commit**

```bash
git add app/evals/judge.py tests/test_eval_judge.py
git commit -m "feat(evals): 添加 LLM-as-a-judge 实现"
```

---

## Task 3: 实现 `app/evals/langfuse_eval.py`

**Files:**
- Create: `app/evals/langfuse_eval.py`
- Create: `tests/test_eval_langfuse.py`

- [ ] **Step 1: 写失败测试**

新建 `tests/test_eval_langfuse.py`：

```python
"""langfuse_eval 核心逻辑单元测试"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.evals.runner import EvalCase
from app.evals.langfuse_eval import (
    EvalRunSummary,
    FailedItem,
    _extract_trace_id,
    _compute_tool_match,
)
from app.evals.executor import HttpEvalResponse


def make_case(case_id: str = "EMP-01", expected_tool: str = "get_salary_info") -> EvalCase:
    return EvalCase(
        case_id=case_id,
        file_path="tests/demo.md",
        section="HR",
        subsection="薪资",
        user_input="查薪资",
        expected_tool=expected_tool,
        expected_behavior="调用薪资工具",
        raw={},
    )


def test_extract_trace_id_from_header():
    resp = HttpEvalResponse(
        status_code=200,
        body={},
        headers={"x-trace-id": "trace-abc"},
    )
    assert _extract_trace_id(resp) == "trace-abc"


def test_extract_trace_id_from_body():
    resp = HttpEvalResponse(
        status_code=200,
        body={"trace_id": "trace-xyz"},
        headers={},
    )
    assert _extract_trace_id(resp) == "trace-xyz"


def test_extract_trace_id_returns_none_when_missing():
    resp = HttpEvalResponse(status_code=200, body={}, headers={})
    assert _extract_trace_id(resp) is None


def test_compute_tool_match_hit():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"reply": "将调用 get_salary_info"},
        headers={},
    )
    assert _compute_tool_match(case, resp) is True


def test_compute_tool_match_miss():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(status_code=200, body={"reply": "普通回答"}, headers={})
    assert _compute_tool_match(case, resp) is False


def test_compute_tool_match_no_expected_tool():
    case = make_case(expected_tool="—")
    resp = HttpEvalResponse(status_code=200, body={"reply": "任何回答"}, headers={})
    assert _compute_tool_match(case, resp) is None
```

- [ ] **Step 2: 运行确认失败**

```bash
uv run pytest tests/test_eval_langfuse.py -v
```

预期：ImportError

- [ ] **Step 3: 实现 `app/evals/langfuse_eval.py`**

```python
"""Langfuse 评测核心 — Dataset 管理、实验执行、双指标打分上报"""
from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime

from app.core.logging import logger
from app.core.tracing import get_langfuse_client
from app.evals.executor import HttpEvalRequester, HttpEvalResponse
from app.evals.judge import JudgeResult
from app.evals.runner import EvalCase


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
    """从响应头或响应体提取 trace_id。"""
    # 响应头优先（大小写不敏感）
    lower_headers = {k.lower(): v for k, v in resp.headers.items()}
    if tid := lower_headers.get("x-trace-id"):
        return tid
    # 响应体 JSON 字段
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
                if key in {"reply", "content", "message", "result", "response", "output", "text",
                           "member_responses", "messages", "choices", "delta"}:
                    walk(value)

    walk(body)
    return " ".join(values).strip()


def _collect_tool_hints(body: dict) -> set[str]:
    """从响应体结构化字段收集工具名。"""
    hints: set[str] = set()

    def add_tokens(value: str) -> None:
        for token in re.findall(r"[a-zA-Z_]{3,}", value):
            hints.add(token.lower())

    def walk(node: object) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in {"tool", "tool_name", "name", "function", "tool_call", "tool_calls"}:
                    if isinstance(value, str):
                        add_tokens(value)
                    else:
                        walk(value)
                elif key in {"member_responses", "messages", "choices", "delta"}:
                    walk(value)

    walk(body)
    return hints


def _compute_tool_match(case: EvalCase, resp: HttpEvalResponse) -> bool | None:
    """计算工具匹配分（规则）。None 表示用例无需检查工具。"""
    expected = case.expected_tool.strip() if case.expected_tool else ""
    if not expected or expected in {"—", "-"}:
        return None
    candidates = [t.lower() for t in re.findall(r"[a-zA-Z_]{3,}", expected)]
    if not candidates:
        return None
    response_text = _collect_response_text(resp.body).lower()
    observed = _collect_tool_hints(resp.body)
    return any(c in response_text or c in observed for c in candidates)


def _make_run_name(base: str | None) -> str:
    """生成唯一 run_name（追加时间戳后缀）。"""
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
) -> EvalRunSummary:
    """执行评测实验，上报双指标分数到 Langfuse。

    Args:
        dataset_name: Langfuse Dataset 名称
        run_name: 实验名称前缀，None 则自动生成
        requester: HTTP 请求执行器
        judge_fn: LLM judge 函数
        id_prefix: 按 case_id 前缀过滤（逗号分隔）
        limit: 最多执行条数，0=不限制

    Returns:
        EvalRunSummary 汇总结果
    """
    actual_run_name = _make_run_name(run_name)
    client = get_langfuse_client()

    # 获取 dataset items
    # 降级条件：(1) client=None（Langfuse 未配置/初始化失败）
    # (2) client.get_dataset() 抛异常（运行时连接失败）
    # 两种情况均 dataset=None，继续执行但跳过所有上报
    try:
        dataset = client.get_dataset(dataset_name) if client else None
    except Exception as e:
        logger.warning(f"获取 Langfuse Dataset 失败: {e}，将跳过上报")
        dataset = None

    items = []
    if dataset:
        items = list(dataset.items)
        if id_prefix:
            prefixes = {p.strip().upper() for p in id_prefix.split(",") if p.strip()}
            items = [
                it for it in items
                if it.input.get("case_id", "").split("-", 1)[0].upper() in prefixes
            ]
        if limit > 0:
            items = items[:limit]

    if not items:
        logger.warning(f"Dataset '{dataset_name}' 无可用 items（已过滤 prefix={id_prefix!r} limit={limit}）")
        return EvalRunSummary(
            run_name=actual_run_name,
            total=0,
            passed=0,
            tool_match_rate=0.0,
            avg_response_quality=None,
        )

    total = 0
    passed = 0
    tool_matches: list[bool] = []
    quality_scores: list[float] = []
    failed_items: list[FailedItem] = []

    for item in items:
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
        total += 1
        trace_id: str | None = None
        fail_reason: str | None = None

        try:
            resp = requester(case)
            trace_id = _extract_trace_id(resp)
        except Exception as exc:
            msg = str(exc).lower()
            fail_reason = "request_timeout" if "timeout" in msg else "request_error"
            failed_items.append(FailedItem(case_id=case.case_id, fail_reason=fail_reason, response_preview=""))
            continue

        # 关联 trace
        if client and trace_id:
            try:
                client.create_dataset_run_item(
                    run_name=actual_run_name,
                    dataset_item_id=item.id,
                    trace_id=trace_id,
                )
            except Exception as e:
                logger.debug(f"关联 trace 失败 case={case.case_id}: {e}")

        # 规则打分: tool_match
        tool_match = _compute_tool_match(case, resp)
        if tool_match is not None:
            tool_matches.append(tool_match)

        # HTTP 状态检查
        if resp.status_code != 200:
            fail_reason = f"http_{resp.status_code}"
        elif tool_match is False:
            fail_reason = "tool_mismatch"

        # 上报 tool_match score
        if client and trace_id and tool_match is not None:
            try:
                client.score(
                    trace_id=trace_id,
                    name="tool_match",
                    value=1.0 if tool_match else 0.0,
                    data_type="NUMERIC",
                )
            except Exception as e:
                logger.debug(f"上报 tool_match score 失败: {e}")

        # LLM judge: response_quality
        response_text = _collect_response_text(resp.body)
        try:
            judge_result = await judge_fn(case.user_input, case.expected_behavior, response_text)
            if judge_result.score is not None:
                quality_scores.append(judge_result.score)
                if client and trace_id:
                    try:
                        client.score(
                            trace_id=trace_id,
                            name="response_quality",
                            value=judge_result.score,
                            comment=judge_result.reason,
                            data_type="NUMERIC",
                        )
                    except Exception as e:
                        logger.debug(f"上报 response_quality score 失败: {e}")
        except Exception as e:
            logger.debug(f"LLM judge 失败 case={case.case_id}: {e}")

        # 综合判断是否通过
        case_ok = resp.status_code == 200 and tool_match is not False
        if case_ok:
            passed += 1
        elif fail_reason:
            response_preview = response_text[:160]
            failed_items.append(FailedItem(
                case_id=case.case_id,
                fail_reason=fail_reason,
                response_preview=response_preview,
            ))

    tool_match_rate = sum(1 for m in tool_matches if m) / len(tool_matches) if tool_matches else 0.0
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None

    return EvalRunSummary(
        run_name=actual_run_name,
        total=total,
        passed=passed,
        tool_match_rate=tool_match_rate,
        avg_response_quality=avg_quality,
        failed=failed_items,
    )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_eval_langfuse.py -v
```

预期：6 个 PASS

- [ ] **Step 5: Commit**

```bash
git add app/evals/langfuse_eval.py tests/test_eval_langfuse.py
git commit -m "feat(evals): 添加 langfuse_eval 核心模块（Dataset/Score/实验执行）"
```

---

## Task 4: 迁移脚本 `scripts/migrate_evals.py`

**Files:**
- Create: `scripts/migrate_evals.py`

- [ ] **Step 1: 实现迁移脚本**

```python
"""Markdown 评测用例 → Langfuse Dataset 一次性迁移脚本"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.runner import collect_eval_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将 Markdown 评测用例迁移到 Langfuse Dataset")
    parser.add_argument("--tests-dir", default="tests", help="Markdown 用例目录")
    parser.add_argument("--pattern", default="test_evaluation_*.md", help="文件 glob")
    parser.add_argument("--dataset-name", default="mx-agent-evals", help="Langfuse Dataset 名称")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不实际写入")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    setup_tracing()
    client = get_langfuse_client()
    if client is None:
        print("错误: Langfuse 未初始化，请检查 LANGFUSE_* 环境变量", file=sys.stderr)
        sys.exit(1)

    cases = collect_eval_cases(args.tests_dir, args.pattern)
    print(f"共发现 {len(cases)} 条用例，目标 Dataset: {args.dataset_name}")

    if args.dry_run:
        for case in cases[:5]:
            print(f"  [dry-run] {case.case_id}: {case.user_input[:40]}")
        print("  ... (dry-run 模式，未写入)")
        return

    # 确保 dataset 存在
    try:
        client.create_dataset(name=args.dataset_name)
        print(f"Dataset '{args.dataset_name}' 已创建")
    except Exception:
        print(f"Dataset '{args.dataset_name}' 已存在，继续写入")

    success = 0
    errors = 0
    for case in cases:
        try:
            # external_id=case.case_id 是幂等 key，Langfuse 用此字段去重
            # 重复执行迁移脚本时不会创建重复 item
            client.create_dataset_item(
                dataset_name=args.dataset_name,
                input={
                    "user_input": case.user_input,
                    "case_id": case.case_id,
                    "section": case.section,
                    "subsection": case.subsection,
                },
                expected_output={
                    "expected_tool": case.expected_tool,
                    "expected_behavior": case.expected_behavior,
                },
                external_id=case.case_id,
            )
            success += 1
        except Exception as e:
            print(f"  写入失败 {case.case_id}: {e}", file=sys.stderr)
            errors += 1

    print(f"迁移完成: 成功 {success}，失败 {errors}")
    if errors == 0:
        print(f"所有用例已写入 Langfuse Dataset '{args.dataset_name}'")
        print("建议执行: mv tests/test_evaluation_*.md tests/archived/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证脚本 dry-run 可运行（无需真实 Langfuse 连接）**

```bash
uv run python scripts/migrate_evals.py --dry-run
```

预期：打印用例数量和前 5 条（如果 Langfuse 未配置则打印错误提示退出）

- [ ] **Step 3: Commit**

```bash
git add scripts/migrate_evals.py
git commit -m "feat(evals): 添加 Markdown → Langfuse Dataset 迁移脚本"
```

---

## Task 5: 重构 `scripts/run_evals.py`

**Files:**
- Modify: `scripts/run_evals.py`

- [ ] **Step 1: 重构 `run_evals.py` 改为调用 Langfuse 评测**

将 `scripts/run_evals.py` 完整替换为：

```python
"""评测执行脚本 — 从 Langfuse Dataset 读取用例，双指标打分并上报"""
import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.executor import HttpEvalRequester
from app.evals.judge import llm_judge
from app.evals.langfuse_eval import run_eval_experiment

import functools


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 Langfuse Dataset 执行评测并上报分数")
    parser.add_argument("--dataset-name", default="mx-agent-evals", help="Langfuse Dataset 名称")
    parser.add_argument("--run-name", default="", help="实验名称前缀，默认自动生成")
    parser.add_argument("--id-prefix", default="", help="按 case_id 前缀过滤，逗号分隔")
    parser.add_argument("--limit", type=int, default=0, help="最多执行条数，0=不限制")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Agent 接口地址")
    parser.add_argument("--endpoint", default="/teams/router-team/runs", help="接口路径")
    parser.add_argument("--request-mode", choices=["auto", "json", "form"], default="auto")
    parser.add_argument("--message-field", default="message")
    parser.add_argument("--auth-token", default="")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser


async def main_async(args: argparse.Namespace) -> None:
    setup_tracing()

    requester = HttpEvalRequester(
        base_url=args.base_url,
        endpoint=args.endpoint,
        timeout=args.timeout,
        auth_token=args.auth_token,
        message_field=args.message_field,
        request_mode=args.request_mode,
    )

    judge_fn = functools.partial(
        llm_judge,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    try:
        summary = await run_eval_experiment(
            dataset_name=args.dataset_name,
            run_name=args.run_name or None,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix=args.id_prefix,
            limit=args.limit,
        )
    finally:
        requester.close()

    print(f"run_name:        {summary.run_name}")
    print(f"总用例数:        {summary.total}")
    print(f"通过数:          {summary.passed}")
    print(f"工具匹配率:      {summary.tool_match_rate:.1%}")
    if summary.avg_response_quality is not None:
        print(f"平均回答质量:    {summary.avg_response_quality:.2f}")
    if summary.failed:
        print(f"失败用例 Top {min(5, len(summary.failed))}:")
        for item in summary.failed[:5]:
            print(f"  - {item.case_id} | {item.fail_reason} | {item.response_preview[:60]}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证脚本可解析参数（无需真实服务）**

```bash
uv run python scripts/run_evals.py --help
```

预期：打印帮助信息，无报错

- [ ] **Step 3: Commit**

```bash
git add scripts/run_evals.py
git commit -m "refactor(evals): 重构 run_evals.py 改为 Langfuse Dataset + 双指标打分"
```

---

## Task 6: 新增 FastAPI Evals Endpoint

**Files:**
- Create: `app/api/v1/endpoints/evals.py`
- Modify: `app/api/v1/router.py`

- [ ] **Step 1: 实现 `app/api/v1/endpoints/evals.py`**

```python
"""评测触发接口 — 通过 API 启动 Langfuse Dataset 评测实验"""
from __future__ import annotations

import asyncio
import functools
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.executor import HttpEvalRequester
from app.evals.judge import llm_judge
from app.evals.langfuse_eval import EvalRunSummary, run_eval_experiment

router = APIRouter(prefix="/evals", tags=["evals"])

# 内存中存储后台任务结果（服务重启后丢失）
_run_results: dict[str, EvalRunSummary | str] = {}


class EvalRunRequest(BaseModel):
    dataset_name: str = Field(default="mx-agent-evals", description="Langfuse Dataset 名称")
    id_prefix: str = Field(default="", description="按 case_id 前缀过滤，逗号分隔")
    limit: int = Field(default=0, ge=0, description="最多执行条数，0=不限制")
    run_name: str = Field(default="", description="实验名称前缀，为空则自动生成")
    base_url: str = Field(default="http://localhost:8000", description="Agent 接口地址")
    endpoint: str = Field(default="/teams/router-team/runs", description="接口路径")
    auth_token: str = Field(default="", description="Bearer Token")
    timeout: float = Field(default=30.0, description="接口超时秒数")


class EvalRunStarted(BaseModel):
    run_name: str = Field(description="实际使用的唯一 run_name（含时间戳后缀）")
    status: str = Field(default="started")
    message: str = Field(default="评测已在后台启动，请通过 GET /evals/runs/{run_name} 查询进度")


class EvalRunStatus(BaseModel):
    run_name: str
    status: str  # started | completed | failed
    total: int | None = None
    passed: int | None = None
    tool_match_rate: float | None = None
    avg_response_quality: float | None = None
    failed: list[dict] | None = None


async def _run_background(run_name: str, req: EvalRunRequest) -> None:
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
            run_name=req.run_name or None,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix=req.id_prefix,
            limit=req.limit,
        )
        _run_results[run_name] = summary
    except Exception as e:
        _run_results[run_name] = f"failed: {e}"
    finally:
        requester.close()


@router.post("/runs", response_model=EvalRunStarted, status_code=202)
async def start_eval_run(req: EvalRunRequest, background_tasks: BackgroundTasks) -> EvalRunStarted:
    """启动评测实验（后台执行）。

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
        run_name: 由 POST /evals/runs 返回的 run_name

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
            {"case_id": f.case_id, "fail_reason": f.fail_reason, "response_preview": f.response_preview}
            for f in summary.failed
        ],
    )
```

- [ ] **Step 2: 在 `app/api/v1/router.py` 注册 evals router**

```python
"""v1 路由聚合 — 注册并挂载各业务端点的 router。"""

from fastapi import APIRouter

from app.api.v1.endpoints.evals import router as evals_router

v1_router = APIRouter()
v1_router.include_router(evals_router)
```

- [ ] **Step 3: 运行服务并验证接口可访问**

```bash
uv run uvicorn app.main:app --reload --port 8000
# 另开终端
curl -s http://localhost:8000/v1/evals/runs -X POST \
  -H "Content-Type: application/json" \
  -d '{"limit": 0}' | python3 -m json.tool
```

预期：返回 202 + `{"run_name": "eval-run-...", "status": "started", ...}`

- [ ] **Step 4: Commit**

```bash
git add app/api/v1/endpoints/evals.py app/api/v1/router.py
git commit -m "feat(evals): 添加 FastAPI 评测触发接口 POST/GET /v1/evals/runs"
```

---

## Task 7: 更新文档并归档 Markdown 用例

**Files:**
- Modify: `docs/evals-guide.md`
- Archive: `tests/test_evaluation_*.md` → `tests/archived/`

- [ ] **Step 1: 创建 `tests/archived/` 目录并移动文件**

```bash
mkdir -p tests/archived
mv tests/test_evaluation_*.md tests/archived/
```

- [ ] **Step 2: 更新 `docs/evals-guide.md`**

在文件顶部追加说明，指向新工作流：

在 `## 1. 目标与范围` 前插入：

```markdown
> **⚠ 已重构**：评测模块已迁移至 Langfuse Dataset。本文档描述旧架构，新架构请参考
> `docs/superpowers/specs/2026-03-23-langfuse-evals-design.md`。
> 快速开始：
> 1. 迁移用例：`uv run python scripts/migrate_evals.py`
> 2. 执行评测：`uv run python scripts/run_evals.py --limit 20`
> 3. 查看结果：登录 Langfuse UI → Datasets → mx-agent-evals
```

- [ ] **Step 3: Commit**

```bash
git add tests/archived/ docs/evals-guide.md
git commit -m "chore(evals): 归档 Markdown 用例，更新评测文档指向新架构"
```

---

## 验收检查

运行所有测试，确认无回归：

```bash
uv run pytest tests/test_eval_runner.py tests/test_eval_executor.py tests/test_eval_judge.py tests/test_eval_langfuse.py -v
```

预期：全部 PASS，无 ERROR。
