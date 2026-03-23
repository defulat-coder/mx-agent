# 评估模块独立说明

> **⚠ 已重构**：评测模块已迁移至 Langfuse Dataset。本文档描述旧架构供参考，新架构请参考
> `docs/superpowers/specs/2026-03-23-langfuse-evals-design.md`。
>
> **快速开始（新架构）：**
> 1. 迁移用例：`uv run python scripts/migrate_evals.py`
> 2. 执行评测：`uv run python scripts/run_evals.py --limit 20 --auth-token <token>`
> 3. 查看结果：登录 Langfuse UI → Datasets → mx-agent-evals
> 4. API 触发：`POST /v1/evals/runs`，查询进度：`GET /v1/evals/runs/{run_name}`
>
> 历史 Markdown 用例已归档至 `tests/archived/`。

## 1. 目标与范围

本项目评估模块用于将 `tests/test_evaluation_*.md` 中的用例结构化解析后，按需进行：

- 静态统计（用例数量、前缀分布）
- 在线执行（调用接口并打分）
- 结果归因（HTTP/工具匹配/请求异常）

适用场景：

- 回归验证 Router Team 的工具路由是否命中
- 按角色前缀（如 `EMP/ADM/CD/RT`）抽样执行
- 在 CI 或本地快速定位失败原因

---

## 2. 代码结构

- 解析与过滤：`app/evals/runner.py`
- 执行与打分：`app/evals/executor.py`
- 命令行入口：`scripts/run_evals.py`
- 核心测试：
  - `tests/test_eval_runner.py`
  - `tests/test_eval_executor.py`

---

## 3. 评估流程

### 3.1 用例解析

`runner.py` 会扫描指定目录下匹配 `pattern` 的 Markdown 文件，解析表格行并映射为 `EvalCase`：

- `case_id`
- `user_input`
- `expected_tool`
- `expected_behavior`
- `section/subsection`

解析要求：

- 表头必须包含 `ID`
- `ID` 必须包含 `-`（如 `EMP-01`）
- 支持 `用户输入/场景`、`期望工具/期望工具组合`、`预期行为/验证点` 的兼容字段读取

### 3.2 执行请求

`executor.py` 的 `HttpEvalRequester` 支持三种请求模式：

- `auto`：自动推断
- `form`：`data` 表单提交（`/teams/.../runs` 默认走此模式）
- `json`：`json` 请求体提交

`auto` 规则：当 endpoint 同时包含 `/teams/` 和 `/runs` 时，自动切换为 `form`。

### 3.3 打分逻辑

`score_case` 规则：

1. `status_code == 200`
2. 若存在 `expected_tool`，则需要工具命中：
   - 命中响应文本中的工具名
   - 或命中结构化 `tool/tool_calls/function/name` 等字段

满足以上条件才会 `ok=True`。

---

## 4. 失败原因分类

### 4.1 HTTP 失败分类

- `http_401_unauthorized`
- `http_403_forbidden`
- `http_404_not_found`
- `http_422_validation`
- `http_429_rate_limited`
- `http_5xx_upstream`
- 兜底：`http_status`

### 4.2 请求异常分类

- `request_timeout`
- `request_connection_error`
- 兜底：`request_error`

### 4.3 其他失败分类

- `tool_mismatch`：接口成功但工具未命中
- `unknown`：无法归入以上类型的异常场景

---

## 5. 命令行使用

### 5.1 仅统计

```bash
uv run python scripts/run_evals.py
uv run python scripts/run_evals.py --id-prefix EMP,ADM
uv run python scripts/run_evals.py --output-json data/evals/cases.json
```

### 5.2 执行评估

```bash
uv run python scripts/run_evals.py --mode execute --limit 20 --base-url http://localhost:8000
uv run python scripts/run_evals.py --mode execute --endpoint /v1/chat --request-mode json
uv run python scripts/run_evals.py --mode execute --show-failed 10 --output-json data/evals/results.json
```

关键参数说明：

- `--mode`: `summary | execute`
- `--id-prefix`: 逗号分隔前缀过滤
- `--limit`: 仅执行前 N 条
- `--request-mode`: `auto | form | json`
- `--show-failed`: 打印 Top N 失败样例（`0` 表示不打印）

---

## 6. 输出结果解读

执行模式会输出：

- 执行用例数、通过数、失败数
- 请求异常数、工具匹配失败数
- 状态码分布
- 失败原因分布
- 失败样例 Top N

JSON（`--output-json`）中每条执行结果字段：

- `id`
- `ok`
- `status_code`
- `tool_match`
- `error`
- `fail_reason`
- `response_preview`

---

## 7. 常见问题排查

1. 全量失败且状态码集中在 5xx  
   优先检查目标服务是否可达、上游依赖是否正常。

2. 请求超时或连接失败  
   检查 `--base-url`、服务监听地址与网络连通性。

3. 工具匹配频繁失败  
   检查 `expected_tool` 与实际工具名一致性，确认响应中是否有 `tool_calls/function/name` 结构。

4. 追踪组件导致调用异常（如本地调试）  
   可在本地临时禁用追踪后再执行评估，避免非业务链路干扰结果。

---

## 8. 推荐实践

- 先 `summary` 再 `execute`，减少无效请求
- 先按前缀小批量执行，再扩到全量
- 固定 `--request-mode` 与目标接口契约保持一致
- 将 `fail_reason` 分布纳入回归报告，持续观察稳定性趋势
