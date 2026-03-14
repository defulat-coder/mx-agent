## ADDED Requirements

### Requirement: Langfuse 配置管理
系统 SHALL 从环境变量读取 Langfuse 连接配置，并在配置缺失或无效时提供清晰的错误提示。

#### Scenario: 配置加载成功
- **WHEN** 应用启动时 `.env` 文件中包含有效的 `LANGFUSE_SECRET_KEY`、`LANGFUSE_PUBLIC_KEY` 和 `LANGFUSE_BASE_URL`
- **THEN** 配置模块正确解析并暴露这些配置项

#### Scenario: 配置缺失时优雅处理
- **WHEN** 应用启动时 Langfuse 相关环境变量缺失
- **THEN** 应用继续启动，但记录警告日志提示追踪功能未启用

### Requirement: OpenTelemetry Tracing 初始化
系统 SHALL 在应用启动时初始化 OpenTelemetry tracing，配置 OTLP exporter 将追踪数据发送到 Langfuse。

#### Scenario: 成功初始化
- **WHEN** 应用启动且 Langfuse 配置有效
- **THEN** OpenTelemetry SDK 和 Agno OpenInference Instrumentor 正确初始化
- **AND** 追踪数据通过 OTLP 协议发送到配置的 Langfuse 端点

#### Scenario: 初始化失败时降级
- **WHEN** 应用启动但 Langfuse 服务不可用或配置无效
- **THEN** 应用继续启动，记录错误日志，tracing 功能静默禁用

### Requirement: Agent 调用链自动追踪
系统 SHALL 自动追踪 Router Team 和所有子 Agent 的调用链，包括调用关系、输入输出和延迟。

#### Scenario: 单 Agent 调用追踪
- **WHEN** 用户发送请求到 Router Team，Router 将请求路由到单个 Agent（如 HR Agent）
- **THEN** Langfuse 中生成完整的 trace，包含 Router Team 和 HR Agent 的调用层级
- **AND** 记录每个 Agent 的输入消息、输出响应和执行耗时

#### Scenario: 跨域多 Agent 调用追踪
- **WHEN** 用户请求涉及多个 Agent（如入职流程需要 HR + IT + Admin）
- **THEN** Langfuse 中生成单个 trace，包含所有参与的 Agent 调用
- **AND** 清晰展示 Agent 之间的调用顺序和依赖关系

### Requirement: Tool 调用追踪
系统 SHALL 自动追踪所有 Tool 的调用，包括 Tool 名称、输入参数、输出结果和执行延迟。

#### Scenario: Tool 调用成功
- **WHEN** Agent 调用某个 Tool（如查询员工信息）
- **THEN** Langfuse 中生成 Tool 调用的 span，包含 Tool 名称、输入参数、输出结果
- **AND** 记录 Tool 执行耗时

#### Scenario: Tool 调用失败
- **WHEN** Agent 调用 Tool 时发生异常
- **THEN** Langfuse 中记录失败的 Tool 调用，包含异常信息和堆栈

### Requirement: LLM 调用追踪
系统 SHALL 自动追踪所有 LLM 调用，包括模型名称、输入消息、输出内容、token 消耗和延迟。

#### Scenario: LLM 调用追踪
- **WHEN** Agent 调用 LLM 生成响应
- **THEN** Langfuse 中生成 LLM span，包含模型 ID、输入消息、输出内容
- **AND** 记录 prompt tokens、completion tokens、总 token 数
- **AND** 记录 LLM 调用耗时

### Requirement: 用户身份关联
系统 SHALL 将追踪数据与当前用户（employee_id）关联，支持用户级的追踪查询。

#### Scenario: 用户身份注入
- **WHEN** 已认证用户发送请求
- **THEN** 追踪数据中包含 `employee_id` 标签
- **AND** Langfuse 中可通过用户 ID 过滤和查询相关 traces
