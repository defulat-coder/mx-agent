## Context

hr-manager-role 已实现主管 Tools/Service/Agent 工厂函数，但认证链路只传 `employee_id`。后续还会有管理层、人才发展部等角色，需要可扩展的架构，不能为每个角色预建一套 Team。

## Goals / Non-Goals

**Goals:**
- 认证时查库判断角色列表（roles），动态填充到 EmployeeContext
- session_state 传递 roles 列表到 Agent/Tools
- 每次请求按 roles 动态创建包含对应 tools 的 Agent（折中方案）
- Tool 层保留权限校验作为防御纵深

**Non-Goals:**
- 不改变 JWT token 格式（roles 通过查库获得）
- 不引入角色缓存
- 不做 Agent 实例池化（后续优化点）

## Decisions

### 1. roles 列表替代单 role

session_state 使用 `roles: list[str]` 而非 `role: str`，天然支持多角色（如某人同时是部门主管 + 管理层）。

```python
session_state = {
    "employee_id": 9,
    "roles": ["employee", "manager"],
    "department_id": 2,
}
```

所有员工默认有 `"employee"` 角色。

### 2. 请求时查库判断角色

`get_employee_from_token` 解析 JWT 拿到 `employee_id` 后，查 `departments` 表判断是否为某部门 `manager_id`。后续新增角色只需扩展此查询逻辑。

### 3. 每次请求动态创建 Agent（折中方案）

不预建多套 Team，而是每次请求按 roles 动态创建：
- HR Agent 按 roles 累加 tools 和 prompt
- router_team 按 roles 动态组装

**理由**：
- 加新角色只需新增 tools + prompt 片段，不用改 router
- 多角色用户天然支持
- LLM 只看到有权的 tools，不浪费 token
- Tool 层仍保留校验（防御纵深）

**代价**：每次请求创建 Agent 实例。Agent 初始化是轻量的（只组装配置），不涉及网络/IO，可接受。

### 4. deps 改为异步

`get_current_employee` 需要查库，改为 `async def`。

### 5. 一人管多部门取第一个

如果一个员工是多个部门的 manager，取第一个匹配的 department_id。

## Risks / Trade-offs

- **每次请求创建 Agent 实例** → Agent 初始化只是 Python 对象组装，开销极小。如果后续成为瓶颈可引入实例池。
- **每次请求多一次 DB 查询** → departments 表很小，性能可控。
- **deps 从同步改异步** → 需检查 `CurrentEmployee` 的所有引用点。
