## Why

当前马喜智能助手缺乏对 Agent 调用链的可观测性，无法追踪用户请求在 Router Team 和子 Agent 之间的流转路径，也无法分析 LLM 调用的延迟、Token 消耗和成本。集成 Langfuse 可以提供全链路追踪、性能分析和成本监控能力，帮助优化 Agent 性能和用户体验。

## What Changes

- 添加 `langfuse` SDK 依赖
- 在 `app/config.py` 中添加 Langfuse 相关配置项（从环境变量读取）
- 创建 `app/core/tracing.py` 模块，封装 OpenTelemetry 和 Langfuse 初始化逻辑
- 修改 `app/main.py`，在应用启动时初始化 tracing 系统
- 配置 OpenTelemetry OTLP exporter，将追踪数据发送到 Langfuse
- 启用 Agno OpenInference Instrumentor，自动捕获 Agent/Tool/LLM 调用

## Capabilities

### New Capabilities
- `langfuse-tracing`: Langfuse 观测集成，通过 OpenTelemetry 自动追踪所有 Agent 调用链、Tool 执行和 LLM 请求

### Modified Capabilities
（无，此变更为纯新增能力，不涉及现有 spec 的 REQUIREMENTS 变更）

## Impact

- **依赖变更**: 新增 `langfuse>=2.0` 依赖
- **配置变更**: `.env` 文件需添加 `LANGFUSE_SECRET_KEY`、`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_BASE_URL`
- **代码变更**: 
  - `app/config.py`: 新增 Langfuse 配置项
  - `app/core/tracing.py`: 新增 tracing 初始化模块
  - `app/main.py`: 启动时调用 tracing 初始化
- **运行时影响**: 应用启动时会建立与 Langfuse 的连接，失败时记录警告但不阻断启动
- **数据隐私**: 追踪数据包含用户查询内容，需确保 Langfuse 实例的访问控制
