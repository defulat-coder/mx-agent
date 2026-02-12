## ADDED Requirements

### Requirement: AgentOS 运行时
系统 SHALL 使用 agno AgentOS 作为运行时，提供内置 API、session 管理和 tracing。

#### Scenario: 应用启动
- **WHEN** 应用启动
- **THEN** AgentOS 注册所有 Agent 和 Team，启动 FastAPI 服务，自动建表

#### Scenario: 聊天请求
- **WHEN** 前端调用 `/teams/router-team/runs`
- **THEN** AgentOS 路由到 router_team，执行对话并返回 SSE 流式响应

#### Scenario: session 自动管理
- **WHEN** 请求携带 user_id 和 session_id
- **THEN** AgentOS 自动加载/保存对话历史

### Requirement: base_app 集成
系统 SHALL 通过 AgentOS base_app 参数保留自定义 middleware、exception handlers 和业务路由。

#### Scenario: 自定义路由可用
- **WHEN** 前端调用 base_app 中定义的路由
- **THEN** 路由正常响应，不受 AgentOS 影响
