# 评测模块重构设计 — 基于 Langfuse

**日期**: 2026-03-23  
**状态**: 待实施  
**作者**: AI 协作设计

---

## 1. 背景与目标

### 现状

当前评测体系由以下部分组成：

- `app/evals/runner.py`：解析 `tests/test_evaluation_*.md` 中的表格用例为 `EvalCase` 对象
- `app/evals/executor.py`：发起 HTTP 请求调用 Agent API，通过状态码 + 工具名文本匹配本地打分
- `scripts/run_evals.py`：CLI 入口，结果输出到控制台或 JSON 文件

痛点：
- 用例管理分散在 Markdown 文件，无版本可视化、无历史趋势
- 打分逻辑（文本模糊匹配工具名）不够可靠，无法评估回答质量
- 评测结果与 Langfuse tracing 完全脱离，无法与 trace 关联分析

### 目标

1. 将测试用例迁移至 Langfuse Dataset 统一管理
2. 实现双指标打分：规则打分（tool_match）+ LLM-as-a-judge（response_quality）
3. 打分结果通过 Langfuse Scores API 上报，与对应 trace 关联
4. 提供 CLI 脚本和 FastAPI 接口两种评测触发方式
5. 提供一次性迁移脚本将现有 Markdown 用例导入 Langfuse Dataset

---

## 2. 架构设计

### 整体数据流

```
Markdown 用例文件 (tests/)
       ↓ [migrate_evals.py — 一次性迁移]
Langfuse Dataset (dataset_name = "mx-agent-evals")
       ↓ [eval runner 读取 dataset items]
Agent HTTP API (调用 agno team/agent)
       ↓ [trace 自动上报 via OTel/AgnoInstrumentor]
Langfuse Trace (现有 tracing 链路，零改动)
       ↓ [双指标打分]
  ┌──────────────────────────────────────────┐
  │ Score 1: tool_match  (value=0/1, 规则)   │
  │ Score 2: response_quality (value=0-1, LLM)│
  └──────────────────────────────────────────┘
       ↓
Langfuse Scores + Dataset Item Run Link
```

### 模块划分

| 文件 | 职责 | 变更 |
|---|---|---|
| `app/evals/runner.py` | Markdown 解析（EvalCase） | 保留不变，迁移后备用 |
| `app/evals/executor.py` | HTTP 请求层（HttpEvalRequester） | 保留请求层，移除本地打分逻辑 |
| `app/evals/langfuse_eval.py` | Langfuse Dataset/Score 核心操作 | **新增** |
| `app/evals/judge.py` | LLM-as-a-judge 实现 | **新增** |
| `scripts/migrate_evals.py` | Markdown → Langfuse Dataset 一次性迁移 | **新增** |
| `scripts/run_evals.py` | CLI 入口 | **重构** |
| `app/api/v1/endpoints/evals.py` | FastAPI 触发评测接口 | **新增** |

---

## 3. 核心模块设计

### 3.1 Langfuse Dataset 数据结构

每条 Dataset Item 存储格式：

```python
# input
{
  "user_input": "帮我查下张三的薪资",
  "case_id": "EMP-01",
  "section": "HR",
  "subsection": "薪资查询"
}

# expected_output
{
  "expected_tool": "get_salary_records",
  "expected_behavior": "调用 HR 工具返回薪资记录"
}
```

Dataset 名称默认为 `mx-agent-evals`，可通过参数覆盖。

### 3.2 `app/evals/langfuse_eval.py`

核心数据类与函数：

```python
@dataclass
class EvalRunSummary:
    run_name: str
    total: int
    passed: int
    tool_match_rate: float
    avg_response_quality: float | None
    failed: list[FailedItem]  # {case_id, fail_reason, response_preview}

def get_or_create_dataset(name: str) -> Dataset

def upsert_dataset_item(dataset_name: str, case: EvalCase) -> DatasetItem
# upsert key: case_id 作为 external_id，Langfuse 以 external_id 去重，迁移脚本可安全重复执行

async def run_eval_experiment(
    dataset_name: str,
    run_name: str,                          # 默认追加时间戳后缀保证唯一性
    requester: HttpEvalRequester,
    judge_fn: Callable[[str, str, str], Awaitable[JudgeResult]],  # (user_input, expected_behavior, response_text)
    id_prefix: str = "",
    limit: int = 0,
) -> EvalRunSummary
```

`run_eval_experiment` 执行逻辑（async）：
1. 拉取 dataset items（按 id_prefix/limit 过滤）
2. 对每条 item 调用 `requester` 发起请求，返回 `HttpEvalResponse`
3. 从响应头 `X-Trace-Id` 或响应体 `trace_id` 字段提取 trace_id
4. 调用 `langfuse_client.create_dataset_run_item(run_name=..., dataset_item_id=..., trace_id=...)` 关联 trace
5. 计算 `tool_match`（规则）并上报 score
6. `await judge_fn(...)` 获取 `response_quality` 并上报 score
7. 汇总统计返回 `EvalRunSummary`

> **同步/异步统一**：`run_eval_experiment` 统一为 `async def`；CLI 脚本通过 `asyncio.run()` 顶层调用；FastAPI endpoint 使用 `async def` 直接 await。

### 3.3 `app/evals/judge.py`

LLM judge 实现：

```python
async def llm_judge(
    user_input: str,
    expected_behavior: str,
    response_text: str,
    model: str,
    api_key: str,
    base_url: str,
) -> JudgeResult  # { score: float, reason: str }
```

Prompt 结构：
```
你是一个企业 AI 助手评测员。请根据以下信息给实际回答打分。

用户问题: {user_input}
预期行为: {expected_behavior}
实际回答: {response_text}

评分标准（综合以下维度）：
- 是否直接回答了用户问题
- 回答是否符合预期行为描述
- 回答是否准确完整，无明显错误

请输出 JSON（只输出 JSON，不要其他内容）:
{"score": 0.85, "reason": "回答基本符合预期，但..."}

score 范围 0.0-1.0。
```

解析失败时返回 `JudgeResult(score=None, reason="parse_error: <原始输出>")`。

### 3.4 评测触发 — CLI

改造 `scripts/run_evals.py`，新增 `--dataset-name` 参数：

```bash
# 执行评测（使用 Langfuse Dataset）
uv run python scripts/run_evals.py \
  --mode execute \
  --dataset-name mx-agent-evals \
  --base-url http://localhost:8000 \
  --auth-token <token> \
  --limit 20

# 一次性迁移
uv run python scripts/migrate_evals.py \
  --tests-dir tests \
  --dataset-name mx-agent-evals
```

### 3.5 评测触发 — FastAPI

新增 endpoint，**复用现有 JWT 鉴权中间件**（需有效 Bearer Token）：

```
POST /v1/evals/runs
Content-Type: application/json
Authorization: Bearer <token>

{
  "dataset_name": "mx-agent-evals",   // 可选，默认 mx-agent-evals
  "id_prefix": "EMP,HR",              // 可选，空则全量
  "limit": 20,                        // 可选，0=不限制
  "run_name": "run-2026-03-23"        // 可选，实际写入时追加时间戳后缀确保唯一
}
```

**执行方式**：使用 FastAPI `BackgroundTasks` 后台执行，接口立即返回 `run_name`，避免大批量用例导致 HTTP 超时：

```
Response 202:
{
  "run_name": "run-2026-03-23-143012",   // 实际使用的唯一 run_name
  "status": "started",
  "message": "评测已在后台启动，请在 Langfuse UI 或通过 GET 接口查询进度"
}

GET /v1/evals/runs/{run_name}
Response 200:
{
  "run_name": "run-2026-03-23-143012",
  "status": "completed" | "running" | "failed",
  "total": 20,
  "passed": 17,
  "tool_match_rate": 0.85,
  "avg_response_quality": 0.78,
  "failed": [...]
}
```

> 后台任务结果暂存内存（`dict`），服务重启后丢失；如需持久化可后续扩展到数据库，当前阶段不实现。

---

## 4. 错误处理

| 场景 | 处理方式 |
|---|---|
| Langfuse 未配置 | 降级：跳过上报，仍输出本地统计 |
| Langfuse 连接失败 | 捕获异常，警告日志，继续执行 |
| Agent API 请求超时/失败 | 记录 error，保留现有 fail_reason 分类，不中断整批 |
| LLM judge 返回格式错误 | score=null，comment 记录原始输出，不阻塞 |
| Dataset 不存在 | 自动创建，无需手动预建 |
| trace_id 不可用 | 跳过 link，score 仍单独上报 |

---

## 5. trace_id 传递约定

Agent API 响应中需携带 `trace_id`，优先级：

1. 响应头 `X-Trace-Id`
2. 响应体 JSON 字段 `trace_id`
3. 均不可用则跳过 link

如果当前 API 响应未包含 trace_id，需在 Agent API 响应中补充该字段（作为实施任务之一）。

---

## 6. 迁移策略

1. 运行 `scripts/migrate_evals.py` 一次性将所有 Markdown 用例导入 Langfuse Dataset
2. 验证 Dataset item 数量与 Markdown 用例数一致
3. 将 `tests/test_evaluation_*.md` 移至 `tests/archived/`
4. 后续新增用例直接在 Langfuse Dataset 中管理

---

## 7. 对现有代码的影响

- `app/evals/runner.py`：零改动
- `app/evals/executor.py`：
  - 保留 `HttpEvalRequester`
  - **扩展返回值**：`__call__` 返回类型从 `tuple[int, dict]` 改为 `HttpEvalResponse`（新增响应头字段，用于提取 `X-Trace-Id`）
  - 移除 `score_case`、`execute_cases`（由新模块接管）
- `app/core/tracing.py`：零改动，`get_langfuse_client()` 被新模块复用
- 现有 tracing 链路：不受影响
- `app/api/v1/router.py`：新增 evals router 注册

---

## 8. 依赖

现有依赖已满足（`langfuse` 已在项目中），无需新增 package。

Langfuse SDK 版本要求：`langfuse >= 2.x`（项目已安装）。Dataset Item 的 `external_id` 去重和 `create_dataset_run_item` API 在 2.x 及以上版本可用。

---

## 9. 成功标准

- [ ] 现有 Markdown 用例全部成功迁移到 Langfuse Dataset
- [ ] 执行评测后，Langfuse UI 可查看每条 item 的 run 记录
- [ ] 每条 trace 有 `tool_match` 和 `response_quality` 两个 score
- [ ] CLI 和 FastAPI 两种触发方式均可用
- [ ] Langfuse 不可用时评测不报错，降级为本地输出
