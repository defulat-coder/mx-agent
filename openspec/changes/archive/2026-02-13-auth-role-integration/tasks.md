## 1. Schema

- [x] 1.1 更新 app/schemas/auth.py — EmployeeContext: role → roles: list[str]，保留 department_id

## 2. Auth 层

- [x] 2.1 更新 app/core/auth.py — get_employee_from_token 改为异步，查 departments 表判断角色列表
- [x] 2.2 更新 app/core/deps.py — get_current_employee 改为异步

## 3. Agent 层

- [x] 3.1 更新 app/agents/hr_agent.py — create_hr_agent(roles: list[str])，按 roles 累加 tools/prompt
- [x] 3.2 更新 app/agents/router_agent.py — 改为 create_router_team(roles) 工厂函数

## 4. Chat 接口

- [x] 4.1 更新 app/api/v1/endpoints/chat.py — session_state 写入 roles 列表，每次请求调用 create_router_team(roles)

## 5. Tool 权限

- [x] 5.1 更新 app/tools/hr/manager_query.py — _check_manager 改为检查 roles 列表
- [x] 5.2 更新 app/tools/hr/manager_action.py — _check_manager 通过 import 复用，无需额外改动
