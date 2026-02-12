## Why

当前项目手工搭建 FastAPI + agno SDK，手写 chat 端点、session 管理、auth 逻辑。agno 提供 AgentOS 运行时，内置 50+ 生产 API（含 SSE 流式聊天）、JWT 认证、session 管理、tracing、Control Plane UI。迁移到 AgentOS 可大幅减少自维护代码，获得生产级基础设施。

## What Changes

- **BREAKING** 入口从自定义 FastAPI app 改为 AgentOS，现有 `/v1/chat` 端点由 AgentOS 内置 `/teams/{id}/runs` 替代
- HR Agent 从动态 tools 改为全量 tools 单实例，权限通过 Tool 层校验 session_state.roles
- router_team 改为静态实例注册到 AgentOS
- 认证从自定义 auth.py + deps.py 改为 AgentOS JWTMiddleware，roles 写入 JWT 通过 session_state_claims 自动注入
- 移除自定义 chat 端点和 chat schema（AgentOS 内置）
- 保留自定义 middleware（RequestID、Logging）、exception handlers、业务路由作为 base_app
- 保留业务 DB（SQLite）和 init_db 逻辑

## Capabilities

### New Capabilities
- `agentos-runtime`: AgentOS 运行时集成，提供内置 API、tracing、session 管理

### Modified Capabilities
- `auth`: 从自定义 JWT 解析+查库改为 AgentOS JWTMiddleware，roles 从 JWT claims 注入 session_state
- `router-agent`: 从工厂函数改为静态实例注册到 AgentOS
- `hr-agent-impl`: 从动态 tools 改为全量 tools，权限在 Tool 层强制校验

## Impact

- `main.py` — 重写为 AgentOS 入口
- `app/agents/hr_agent.py` — 全量 tools 单实例
- `app/agents/router_agent.py` — 静态实例，移除工厂函数
- `app/core/auth.py` — 移除（JWTMiddleware 替代）
- `app/core/deps.py` — 移除 get_current_employee（AgentOS 自动注入）
- `app/api/v1/endpoints/chat.py` — 移除（AgentOS 内置）
- `app/schemas/chat.py` — 移除 ChatRequest/ChatResponse（AgentOS 内置）
- `app/schemas/auth.py` — 简化，EmployeeContext 可能不再需要
- `scripts/generate_token.py` — 更新 JWT payload 包含 roles、department_id
- `pyproject.toml` — 确认 agno 版本支持 AgentOS
