## 1. 依赖与配置

- [x] 1.1 添加 `langfuse` 依赖到 `pyproject.toml` 并运行 `uv sync`
- [x] 1.2 在 `app/config.py` 中添加 Langfuse 配置项（LANGFUSE_SECRET_KEY、LANGFUSE_PUBLIC_KEY、LANGFUSE_BASE_URL）

## 2. Tracing 核心模块

- [x] 2.1 创建 `app/core/tracing.py` 模块，实现 `setup_tracing()` 函数
- [x] 2.2 在 `setup_tracing()` 中初始化 OpenTelemetry OTLP exporter
- [x] 2.3 在 `setup_tracing()` 中启用 Agno OpenInference Instrumentor
- [x] 2.4 添加错误处理和优雅降级逻辑（配置缺失或服务不可用时记录警告）

## 3. 应用集成

- [x] 3.1 修改 `app/main.py`，在 `lifespan` 中调用 `setup_tracing()`
- [x] 3.2 确保 tracing 初始化在 AgentOS 启动之前完成
- [x] 3.3 验证启动日志中 tracing 状态信息正确输出

## 4. 用户身份关联

- [x] 4.1 在 tracing 中注入 `employee_id` 标签（从 JWT session_state 获取）
- [x] 4.2 验证每个 trace 都包含用户身份信息

## 5. 验证与测试

- [x] 5.1 启动应用，发送测试请求到 Router Team
- [x] 5.2 登录 Langfuse 控制台，确认 traces 正常接收
- [x] 5.3 验证 Agent 调用链层级正确显示
- [x] 5.4 验证 Tool 调用和 LLM 调用被正确追踪
- [x] 5.5 验证 token 消耗和延迟数据正确记录
- [x] 5.6 测试配置缺失场景，确认应用仍能启动
