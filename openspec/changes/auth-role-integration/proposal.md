## Why

hr-manager-role 实现了主管 Tools/Service/Agent，但认证链路缺失 role 和 department_id，导致主管功能无法触达。`EmployeeContext` 只有 employee_id，`session_state` 未传 role，`router_team` 模块级单例永远用 employee 角色。且后续还有管理层、人才发展部等角色，需要可扩展的角色架构。

## What Changes

- `EmployeeContext` 增加 `roles: list[str]`、`department_id: int | None` 字段
- `get_employee_from_token` 解析 JWT 后查库判断角色列表（如 manager），动态填充 roles/department_id
- `chat.py` 将完整的 roles/department_id 写入 session_state，每次请求按 roles 动态创建包含对应 tools 的 Agent
- `hr_agent.py` 工厂函数改为接收 `roles: list[str]`，按 roles 累加 tools 和 prompt
- `router_agent.py` 改为工厂函数 `create_router_team(roles)`，每次请求动态创建

## Capabilities

### New Capabilities

（无新增 capability）

### Modified Capabilities
- `auth`: 身份上下文从单 role 改为 roles 列表，查库动态判断，支持多角色

## Impact

- `app/schemas/auth.py` — EmployeeContext 增加字段
- `app/core/auth.py` — 查库判断角色列表
- `app/core/deps.py` — 改为异步依赖
- `app/agents/hr_agent.py` — 工厂函数改为接收 roles 列表
- `app/agents/router_agent.py` — 改为工厂函数
- `app/api/v1/endpoints/chat.py` — session_state 补全，动态创建 team
- `app/tools/hr/manager_query.py` — _check_manager 改为检查 roles 列表
